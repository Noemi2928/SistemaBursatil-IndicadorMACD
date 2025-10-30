import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
from modules.indicators import MACDCalculator
from modules.classificator import MACDSignalClassifier  # ajusta el import a tu estructura real

def test_macd_classificacion_correcta():
    df_compra = pd.DataFrame({"MACD":[1,2], "Signal":[1,1.5], "Histogram":[0,0.5]})
    """ Ejemplo de cómo se ve
    df_compra = pd.DataFrame({
        "MACD": [1, 2],        # macd_prev=1, macd_t=2
        "Signal": [1, 1.5],    # signal_prev=1, signal_t=1.5
        "Histogram": [0, 0.5]  # hist_t=0.5
    })"""

    df_venta  = pd.DataFrame({"MACD":[2,0.9], "Signal":[1.5,1], "Histogram":[0,-0.5]})
    df_nulo   = pd.DataFrame({"MACD":[1,1], "Signal":[1,1], "Histogram":[0,0]})

    classifier = MACDSignalClassifier()
    classifier.classify_signal_for_symbol("SYM1", df_compra, "OK")
    classifier.classify_signal_for_symbol("SYM2", df_venta, "OK")
    classifier.classify_signal_for_symbol("SYM3", df_nulo, "OK")

    signals = classifier.get_signals()
    #print(signals)
    # {'COMPRA':'COMPRA', 'VENTA':'VENTA', 'NEUTRO':'NULO'}
    print("\nEsperado = 'SYM1':'COMPRA', 'SYM2':'VENTA', 'SYM3':'NULO'")
    print("Señales clasificadas:", signals)

    assert signals["SYM1"] == "COMPRA", f"Esperado COMPRA, obtenido {signals['COMPRA']}"
    assert signals["SYM2"] == "VENTA", f"Esperado VENTA, obtenido {signals['VENTA']}"
    assert signals["SYM3"] == "NULO", f"Esperado NULO, obtenido {signals['NEUTRO']}"