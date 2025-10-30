import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
import io
import time
import random
import string
from modules.excel_handler import ExcelHandler
from modules.symbols_manager import SymbolsManager
from modules.error_manager import ErrorManager

@pytest.mark.performance
def test_ntc_02_excel_stress():
    error_manager = ErrorManager()
    excel_handler = ExcelHandler(error_manager)
    symbols_manager = SymbolsManager(error_manager)

    valid_symbols = [''.join(random.choices(string.ascii_uppercase, k=4)) for _ in range(35)]
    invalid_symbols = ['SYM' + str(i) for i in range(10)]
    duplicates = random.sample(valid_symbols, 5)  # 5 duplicados aleatorios
    symbols = valid_symbols + invalid_symbols + duplicates
    random.shuffle(symbols)  # Mezclar todo

    # Crear Excel en memoria
    df = pd.DataFrame({"Símbolo": symbols})
    excel_bytes = io.BytesIO()
    df.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)

    # Medir tiempo de ejecución
    start_time = time.time()

    # Cargar símbolos desde Excel (truncate=True en ExcelHandler)
    loaded_symbols, msg_excel = excel_handler.load_symbols(excel_bytes, "Símbolo", truncate=True)

    # Validar con SymbolsManager (truncate=True también)
    symbols_manager.validate_symbols_from_list(loaded_symbols, truncate=True)
    valid_symbols = symbols_manager.get_valid_symbols()
    messages = symbols_manager.get_messages()

    elapsed = time.time() - start_time
    print(f"Tiempo total de ejecución: {elapsed:.2f} segundos")

    # Combinar mensajes de ExcelHandler y SymbolsManager
    all_messages = []
    if msg_excel:
        all_messages.append(msg_excel)
    all_messages.extend(messages)

    # ✅ Verificaciones
    # Solo se deben tomar los primeros 20 símbolos válidos
    assert len(valid_symbols) <= 20
    for sym in valid_symbols:
        assert sym.isalpha(), f"Símbolo inválido incluido: {sym}"

    # Mensajes deben indicar truncado (puede venir de ExcelHandler o SymbolsManager)
    trunc_msg_found = any("trunc" in m.lower() for m in all_messages)
    assert trunc_msg_found, "No se detectó mensaje de truncado cuando había exceso de símbolos válidos"

    # El tiempo de ejecución debe ser menor a 120 segundos
    assert elapsed <= 10, f"Procesamiento demasiado lento: {elapsed:.2f}s"
