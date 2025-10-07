import pandas as pd

class MACDCalculator:
    def __init__(self):
        # Almacena los resultados MACD por símbolo
        self.macd_data = {}       # { "AAPL": DataFrame con MACD, Signal, Histogram }
        # Estado de cada símbolo tras el cálculo
        self.symbols_status = {}  # { "AAPL": "OK" / "DATOS_INSUFICIENTES" / "Error" }

    def calculate_macd(self, price_data: dict, symbols_status: dict):
        self.macd_data = {}
        self.symbols_status = {} 
        #Valores para el MACD
        fast = 12
        slow = 26
        signal = 9

        for symbol, status in symbols_status.items():
            # Solo procesar símbolos con estado OK
            if status != "OK":
                self.symbols_status[symbol] = status
                continue

            df = price_data.get(symbol)

            # Verificar que los datos sean suficientes
            if df is None or df["Close"].dropna().shape[0] < slow + signal:
                self.symbols_status[symbol] = "DATOS_INSUFICIENTES"
                continue

            try:
                # Cálculo del MACD
                ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
                ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
                macd_line = ema_fast - ema_slow

                # Línea de señal
                signal_line = macd_line.ewm(span=signal, adjust=False).mean()

                # Histograma
                histogram = macd_line - signal_line

                # Guardar resultados en un DataFrame
                result_df = pd.DataFrame({
                    "MACD": macd_line,
                    "Signal": signal_line,
                    "Histogram": histogram
                }, index=df.index)

                self.macd_data[symbol] = result_df
                self.symbols_status[symbol] = "OK"

            except Exception as e:
                # En caso de error inesperado
                self.symbols_status[symbol] = f"Error: {str(e)}"

    def get_macd_data(self):
        """ Devuelve los DataFrames con MACD por símbolo """
        return self.macd_data

    def get_symbols_status(self):
        """ Devuelve el estado de cada símbolo tras cálculo """
        return self.symbols_status
