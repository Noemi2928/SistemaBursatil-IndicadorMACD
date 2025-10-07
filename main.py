import os

from flask import Flask, render_template, request
from modules.error_manager import ErrorManager
from modules.excel_handler import ExcelHandler
from modules.symbols_manager import SymbolsManager
from modules.yahoo_client import YahooFinanceClient
from modules.indicators import MACDCalculator

# Indicar a Flask dónde están las plantillas
app = Flask(__name__, template_folder="src")

# Instancias de gestores (iniciales)
error_manager = ErrorManager()
excel_handler = ExcelHandler(error_manager)
symbols_manager = SymbolsManager(error_manager)
yahoo_client = YahooFinanceClient(error_manager)
macd_calculator = MACDCalculator()

# ------------------------------
# Ruta de la página inicial (index)
# ------------------------------
@app.route("/", methods=["GET"])
def index():
    global error_manager, excel_handler, symbols_manager, yahoo_client, macd_calculator

    # Reasignar instancias para limpiar mensajes y listas previas
    error_manager = ErrorManager()
    excel_handler = ExcelHandler(error_manager)
    symbols_manager = SymbolsManager(error_manager)
    yahoo_client = YahooFinanceClient(error_manager)
    macd_calculator = MACDCalculator()

    # Solo mostramos el formulario
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
            # Calcular MACD
            macd_calculator.calculate_macd(yahoo_client.get_data(), yahoo_client.get_status())
            macd_data = macd_calculator.get_macd_data()
            macd_status = macd_calculator.get_symbols_status()
            return render_template("macd_results.html", macd_data=macd_data, macd_status=macd_status)

    return render_template(
        "result.html",
        messages=messages,
        symbols=final_symbols,
        macd_data=macd_data,
        macd_status=macd_status,
        can_continue=can_continue#,
        #status_symbols=status_symbols
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

if __name__ == "__main__":
    app.run(debug=True)