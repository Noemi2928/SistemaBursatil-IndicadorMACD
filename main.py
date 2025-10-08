import os

from flask import Flask, render_template, request, jsonify, send_file
from modules.error_manager import ErrorManager
from modules.excel_handler import ExcelHandler
from modules.symbols_manager import SymbolsManager
from modules.yahoo_client import YahooFinanceClient
from modules.indicators import MACDCalculator
from modules.classificator import MACDSignalClassifier
from modules.show_results import AnalysisResultsManager
import json

# Indicar a Flask dónde están las plantillas
app = Flask(__name__, template_folder="src")

# Instancias de gestores (iniciales)
error_manager = ErrorManager()
excel_handler = ExcelHandler(error_manager)
symbols_manager = SymbolsManager(error_manager)
yahoo_client = YahooFinanceClient(error_manager)
macd_calculator = MACDCalculator()
classifier = MACDSignalClassifier()
results_manager = AnalysisResultsManager()

# ------------------------------
# Ruta de la página inicial (index)
# ------------------------------
@app.route("/", methods=["GET"])
def index():
    global error_manager, excel_handler, symbols_manager

    # Reasignar solo los gestores que guardan datos temporales
    error_manager = ErrorManager()
    excel_handler = ExcelHandler(error_manager)
    symbols_manager = SymbolsManager(error_manager)
    
    # Mostrar el formulario
    return render_template("index.html")

# ------------------------------
# Ruta que procesa la carga de símbolos
# ------------------------------
@app.route("/result", methods=["POST"])
def result():
    messages = []
    final_symbols = []

    # Obtener symbols y mensajes iniciales
    symbols, initial_msgs = get_symbols()
    messages.extend(initial_msgs)

    # --- INICIO: fallback para símbolos cargados desde Excel ---
    if not symbols:
        excel_symbols_str = request.form.get("excel_symbols", "")
        symbols = [s.strip() for s in excel_symbols_str.split(",") if s.strip()]
    # --- FIN ---


    if symbols:
        symbols_manager.validate_symbols_from_list(symbols, truncate=True)
        messages.extend(symbols_manager.get_messages())
        final_symbols = symbols_manager.get_valid_symbols()

    # Determinar si se puede continuar
    can_continue = bool(final_symbols)
    status_symbols = {}
    macd_data = {}
    macd_status = {}


    if can_continue and request.form.get("confirm_continue") == "1":
        success, msg = yahoo_client.fetch_data(final_symbols)
        if not success:
            messages.append(msg)
            can_continue = False
        else:
            # 1️⃣ Calcular MACD
            macd_calculator.calculate_macd(yahoo_client.get_data(), yahoo_client.get_status())
            macd_data = macd_calculator.get_macd_data()
            macd_status = macd_calculator.get_symbols_status()

            # 2️⃣ Clasificar señales
            classifier = MACDSignalClassifier()  # nueva instancia
            classifier.classify_all(macd_data, macd_status)
            classified_signals = classifier.get_signals()

            # 3️⃣ Combinar resultados con estados
            results_manager = AnalysisResultsManager()  # nueva instancia
            results_manager.build_results(macd_status, classified_signals)
            results = results_manager.get_all_results()

            # 4️⃣ Renderizar tabla final
            return render_template("macd_results.html", results=results, messages=messages)


    return render_template(
        "result.html",
        messages=messages,
        symbols=final_symbols,
        can_continue=can_continue
    )


def get_symbols():
        # Obtiene la lista de símbolos a procesar, ya sea manual o Excel
        manual_input = request.form.get("manual_symbols", "").strip()
        excel_file = request.files.get("excel_file")
        column_name = request.form.get("column_name", "").strip()

        if manual_input and (not excel_file or excel_file.filename == ''):
            # Lista manual
            symbols = [s.strip().upper() for s in manual_input.split(",") if s.strip()]
            return symbols, []

        elif excel_file and excel_file.filename != '' and column_name:
            # Archivo Excel
            symbols, msg_excel = excel_handler.load_symbols(excel_file, column_name)
            msgs = [msg_excel] if msg_excel else []
            return symbols, msgs

        else:
            return [], ["Debe ingresar manualmente los símbolos o subir un archivo Excel válido."]

@app.route("/filter_results", methods=["POST"])
def filter_results():
    # Recuperamos todos los resultados enviados desde la plantilla
    all_results_json = request.form.get("all_results")
    all_results = json.loads(all_results_json)

    # Convertimos las claves de cada diccionario para compatibilidad con AnalysisResultsManager
    for symbol, data in all_results.items():
        all_results[symbol] = {"estado": data["estado"], "señal": data["señal"]}

    # Recuperamos la opción de filtrado
    selected_filter = request.form.get("signal_filter", "TODO")

    # Filtrar si no es TODO
    if selected_filter != "TODO":
        filtered_results = {
            symbol: data
            for symbol, data in all_results.items()
            if data["señal"] == selected_filter
        }
    else:
        filtered_results = all_results

    return render_template(
        "macd_results.html",
        results=filtered_results,
        messages=[],
        selected_filter=selected_filter
    )

@app.route("/export_excel", methods=["POST"])
def export_excel():
    results_json = request.form.get("results_json")
    if not results_json:
        return "No hay resultados para exportar.", 400

    try:
        results_dict = json.loads(results_json)
    except json.JSONDecodeError:
        return "Error al procesar los resultados.", 400

    # Usar ExcelHandler para exportar
    excel_handler = ExcelHandler(error_manager)
    success, msg = excel_handler.export_results(results_dict, filename="resultados.xlsx")

    if not success:
        return msg, 500

    # Enviar el archivo al usuario
    return send_file("resultados.xlsx", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)