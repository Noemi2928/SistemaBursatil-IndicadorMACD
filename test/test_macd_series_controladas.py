import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
from modules.indicators import MACDCalculator
from modules.classificator import MACDSignalClassifier

def test_macd_series_controladas():
    n = 50  # cantidad de datos suficiente para EMAs

    # ----- Serie COMPRA: plana + subida brusca al final -----
    base = np.ones(n-2)*10
    last_two = [10.0, 15.0]  # fuerza el cruce en el último punto
    close_compra = np.concatenate([base, last_two])
    df_compra = pd.DataFrame({"Close": close_compra})

    # ----- Serie VENTA: plana + bajada brusca al final -----
    base = np.ones(n-2)*15
    last_two = [15.0, 10.0]  # fuerza cruce descendente
    close_venta = np.concatenate([base, last_two])
    df_venta = pd.DataFrame({"Close": close_venta})

    # ----- Serie NEUTRO: completamente plana -----
    df_neutro = pd.DataFrame({"Close": np.ones(n)*12})

    price_data = {
        "COMPRA": df_compra,
        "VENTA": df_venta,
        "NEUTRO": df_neutro
    }

    symbols_status = {s: "OK" for s in price_data.keys()}

    # ----- 1️⃣ Cálculo MACD -----
    calc = MACDCalculator()
    calc.calculate_macd(price_data, symbols_status)

    macd_data = calc.get_macd_data()
    symbols_status = calc.get_symbols_status()

    # ----- 2️⃣ Clasificación de señales -----
    classifier = MACDSignalClassifier()
    classifier.classify_all(macd_data, symbols_status)
    signals = classifier.get_signals()

    print("Señales clasificadas:", signals)

    # ----- 3️⃣ Validación según lógica -----
    assert signals["COMPRA"] == "COMPRA", f"Esperado COMPRA, obtenido {signals['COMPRA']}"
    assert signals["VENTA"] == "VENTA", f"Esperado VENTA, obtenido {signals['VENTA']}"
    assert signals["NEUTRO"] == "NULO", f"Esperado NULO, obtenido {signals['NEUTRO']}"
