# Ejecución de la prueba:
# PYTHONPATH=. pytest -v -s -m performance
# o PYTHONPATH=. pytest -v -m performance (simplificado)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import pytest
from modules.symbols_manager import SymbolsManager
from modules.error_manager import ErrorManager
# Importar las clases necesarias para el flujo
from modules.indicators import MACDCalculator
from modules.classificator import MACDSignalClassifier
from modules.show_results import AnalysisResultsManager
from modules.yahoo_client import YahooFinanceClient


@pytest.mark.performance
def test_ntc_01_rendimiento():
    # Instancias necesarias
    error_manager = ErrorManager()
    symbols_manager = SymbolsManager(error_manager)
    yahoo_client = YahooFinanceClient(error_manager)
    macd_calculator = MACDCalculator()
    classifier = MACDSignalClassifier()
    results_manager = AnalysisResultsManager()

    # Lista de 20 símbolos válidos
    symbols_test = [
        "AAPL", "MSFT", "GOOG", "TSLA", "AMZN", "NFLX", "FB", "NVDA", "INTC", "AMD",
        "IBM", "ORCL", "SAP", "ADBE", "CSCO", "BABA", "V", "MA", "PYPL", "QCOM"
    ]

    # Validación de símbolos
    symbols_manager.validate_symbols_from_list(symbols_test, truncate=False)
    valid_symbols = symbols_manager.get_valid_symbols()

    # Medir tiempo total
    start_time = time.time()

    # 1️⃣ Llamada a la API
    success, msg = yahoo_client.fetch_data(valid_symbols)
    assert success, f"Error al obtener datos: {msg}"

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

    elapsed = time.time() - start_time
    print(f"\nTiempo total de ejecución: {elapsed:.2f} segundos")

    # Resultado esperado ≤ 120s
    assert elapsed <= 3, f"Tiempo de ejecución {elapsed:.2f}s supera 120s"
