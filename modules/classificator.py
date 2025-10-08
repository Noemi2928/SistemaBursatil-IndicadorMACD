class MACDSignalClassifier:
    def __init__(self):
        # Almacena la señal clasificada por símbolo
        self.signals = {}  # {"AAPL": "COMPRA", "GOOG": "NULO", ...}

    def classify_signal_for_symbol(self, symbol: str, macd_df, status: str):
        """
        Clasifica la señal del símbolo en COMPRA, VENTA o NULO
        según el cruce MACD/Signal.
        Si el estado no es 'OK', la señal se marca como NULO.
        """
        if status != "OK":
            self.signals[symbol] = "NULO"
            return

        # Verificar que el DataFrame tenga las columnas necesarias
        required_cols = {"MACD", "Signal"}
        if not required_cols.issubset(macd_df.columns):
            self.signals[symbol] = "NULO"
            return

        # Verificar que haya al menos dos filas
        if len(macd_df) < 2:
            self.signals[symbol] = "NULO"
            return

        # Últimos dos valores (t y t-1)
        macd_t = macd_df["MACD"].iloc[-1]
        macd_prev = macd_df["MACD"].iloc[-2]
        signal_t = macd_df["Signal"].iloc[-1]
        signal_prev = macd_df["Signal"].iloc[-2]

        # Histograma de la última vela
        hist_t = macd_df["Histogram"].iloc[-1]

        #print(f"Símbolo: {symbol}, MACD_t: {macd_t}, Signal_t: {signal_t}, MACD_prev: {macd_prev}, Signal_prev: {signal_prev}, Hist: {hist_t}")

        # Reglas de clasificación usando histograma para confirmar
        if macd_t > signal_t and macd_prev <= signal_prev and hist_t > 0:
            self.signals[symbol] = "COMPRA"
        elif macd_t < signal_t and macd_prev >= signal_prev and hist_t < 0:
            self.signals[symbol] = "VENTA"
        else:
            self.signals[symbol] = "NULO"



    def classify_all(self, macd_data: dict, symbols_status: dict):
        """
        Recorre todos los símbolos y aplica la clasificación.
        macd_data: { "AAPL": DataFrame con columnas MACD, Signal, Histogram }
        symbols_status: { "AAPL": "OK", "GOOG": "DATOS_INSUFICIENTES", ... }
        """
        self.signals = {}
        for symbol, df in macd_data.items():
            status = symbols_status.get(symbol, "NULO")
            self.classify_signal_for_symbol(symbol, df, status)

    def get_signals(self):
        """Devuelve las señales clasificadas."""
        return self.signals
