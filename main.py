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

# Instancias de gestores
error_manager = ErrorManager()
excel_handler = ExcelHandler(error_manager)
symbols_manager = SymbolsManager(error_manager)
yahoo_client = YahooFinanceClient(error_manager)
macd_calculator = MACDCalculator()
classifier = MACDSignalClassifier()
results_manager = AnalysisResultsManager()

# ------------------------------
# Función unificada para extraer y validar símbolos
# ------------------------------
def extract_and_validate_symbols(form, files):
    manual_input = form.get("manual_symbols", "").strip()
    excel_file = files.get("excel_file")
    column_name = form.get("column_name", "").strip()
    messages = []
    symbols = []
    truncate = False

    # Solo puede haber manual o Excel, nunca ambos
    if manual_input and (not excel_file or excel_file.filename == ''):
        symbols = [s.strip().upper() for s in manual_input.split(",") if s.strip()]
        truncate = False
    elif excel_file and excel_file.filename != '' and column_name:
        symbols, msg_excel = excel_handler.load_symbols(excel_file, column_name)
        truncate = True
        if msg_excel:
            messages.append(msg_excel)
    else:
        messages.append("Debe ingresar manualmente los símbolos o subir un archivo Excel válido.")

    # Validación final con SymbolsManager
    if symbols:
        symbols_manager.validate_symbols_from_list(symbols, truncate=truncate)
        messages.extend(symbols_manager.get_messages())
        symbols = symbols_manager.get_valid_symbols()

    return symbols, messages

# ------------------------------
# Ruta de la página inicial
# ------------------------------
@app.route("/", methods=["GET"])
def index():
    global error_manager, excel_handler, symbols_manager
    # Reasignar gestores que guardan datos temporales
    error_manager = ErrorManager()
    excel_handler = ExcelHandler(error_manager)
    symbols_manager = SymbolsManager(error_manager)
    return render_template("index.html")

# ------------------------------
# Validar símbolos (para el modal)
# ------------------------------
@app.route("/validate_symbols", methods=["POST"])
def validate_symbols():
    symbols, messages = extract_and_validate_symbols(request.form, request.files)
    return jsonify({
        "messages": messages,
        "symbols": symbols
    })

# ------------------------------
# Procesar descarga y cálculo de MACD
# ------------------------------
@app.route("/result", methods=["POST"])
def result():
    # Leer los símbolos que vienen del modal (form oculto)
    final_symbols_json = request.form.get("final_symbols_json")
    if not final_symbols_json:
        return "No se recibieron símbolos para procesar.", 400

    final_symbols = json.loads(final_symbols_json)
    messages = []

    if not final_symbols:
        messages.append("No hay símbolos válidos para procesar.")
        return render_template("macd_results.html", results={}, messages=messages)

    # 1️⃣ Llamada a la API
    success, msg = yahoo_client.fetch_data(final_symbols)
    if not success:
        messages.append(msg)
        return render_template("macd_results.html", results={}, messages=messages)

    # 2️⃣ Calcular MACD
    macd_calculator.calculate_macd(yahoo_client.get_data(), yahoo_client.get_status())
    macd_data = macd_calculator.get_macd_data()
    macd_status = macd_calculator.get_symbols_status()

    # 3️⃣ Clasificar señales
    classifier.classify_all(macd_data, macd_status)
    classified_signals = classifier.get_signals()

    # 4️⃣ Combinar resultados
    results_manager.build_results(macd_status, classified_signals)
    results = results_manager.get_all_results()

    # 5️⃣ Renderizar resultados finales
    return render_template("macd_results.html", results=results, messages=messages)

# ------------------------------
# Filtrado y exportación
# ------------------------------
@app.route("/filter_results", methods=["POST"])
def filter_results():
    all_results_json = request.form.get("all_results")
    all_results = json.loads(all_results_json)
    selected_filter = request.form.get("signal_filter", "TODO")

    if selected_filter != "TODO":
        filtered_results = {
            symbol: data
            for symbol, data in all_results.items()
            if data["señal"] == selected_filter
        }
    else:
        filtered_results = all_results

    return render_template("macd_results.html", results=filtered_results, messages=[])

@app.route("/export_excel", methods=["POST"])
def export_excel():
    results_json = request.form.get("results_json")
    if not results_json:
        return "No hay resultados para exportar.", 400

    try:
        results_dict = json.loads(results_json)
    except json.JSONDecodeError:
        return "Error al procesar los resultados.", 400

    excel_handler = ExcelHandler(error_manager)
    success, file_name_or_msg = excel_handler.export_results(results_dict, filename=None)
    if not success:
        return file_name_or_msg, 500

    return send_file(file_name_or_msg, as_attachment=True)

# ------------------------------
# Ruta para test con datos artificiales
# ------------------------------
@app.route("/test_results", methods=["GET"])
def test_results():
    messages = ["Estos son resultados de prueba para ver la tabla, filtros y exportación."]
    results = {
        "AAPL": {"estado": "OK", "señal": "COMPRA"},
        "GOOG": {"estado": "OK", "señal": "VENTA"},
        "MSFT": {"estado": "DATOS_INSUFICIENTES", "señal": "NULO"},
        "TSLA": {"estado": "OK", "señal": "COMPRA"},
        "NFLX": {"estado": "OK", "señal": "NULO"},
        "AMZN": {"estado": "DATOS_INSUFICIENTES", "señal": "NULO"},
    }
    return render_template("macd_results.html", results=results, messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
