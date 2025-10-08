import yfinance as yf
import pandas as pd
import socket
from datetime import datetime, timedelta
from modules.error_manager import ErrorManager

class YahooFinanceClient:
    def __init__(self, error_manager: ErrorManager):
        self.raw_data = {}        # { "AAPL": DataFrame, ... }
        self.symbols_status = {}  # { "AAPL": "OK", "MSFT": "Error", ... }
        self.error_manager = error_manager

    def _check_internet(self, host="8.8.8.8", port=53, timeout=3) -> bool:
        """Verifica conexión a Internet intentando abrir un socket."""
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False

    def fetch_data(self, symbols: list[str], min_days: int = 60, interval: str = "1d") -> tuple[bool, str | None]:
        
        if not self._check_internet():
            message = self.error_manager.get_message("NO_INTERNET")
            return False, message

        self.raw_data = {}
        self.symbols_status = {}
        start_date = datetime.today() - timedelta(days=min_days)
        start_str = start_date.strftime("%Y-%m-%d")

        try:
            data = yf.download(
                tickers=symbols,
                start=start_str,
                end=datetime.today().strftime("%Y-%m-%d"),
                interval=interval,
                progress=False,
                group_by="ticker",
                auto_adjust=False,
                threads=True
            )
        except Exception as e:
            if "Too Many Requests" in str(e):
                message = self.error_manager.get_message("API_LIMIT")
            else:
                message = self.error_manager.get_message("API_ERROR", str(e))
            return False, message

        for symbol in symbols:
            try:
                # Detectar si las columnas tienen MultiIndex (varios tickers) o no (único ticker)
                if isinstance(data.columns, pd.MultiIndex):
                    df = data[symbol]
                else:
                    df = data  # único ticker → DataFrame plano

                # Validar que tenga columna Close y no esté vacía
                if "Close" not in df.columns or df["Close"].dropna().empty:
                    self.symbols_status[symbol] = "Error"
                    continue

                # Nos aseguramos de que tenga las columnas necesarias (OHLCV)
                required_cols = {"Open", "High", "Low", "Close", "Volume"}
                if not required_cols.issubset(set(df.columns)):
                    self.symbols_status[symbol] = "Error"
                    continue

                # FILTRO: eliminar filas con Close vacío (día actual si no cerró)
                df = df[df["Close"].notna()]

                # Excluir el día actual (si aparece en los datos)
                today = pd.Timestamp.now().normalize()
                df = df[df.index < today]


                # Si todo va bien, guardamos los datos y estado OK
                self.raw_data[symbol] = df
                self.symbols_status[symbol] = "OK"

            except Exception:
                self.symbols_status[symbol] = "Error"
                
        return True, None

    def get_data(self)-> dict:
        """ Devuelve los datos descargados (OHLCV por símbolo). """
        return self.raw_data

    def get_status(self)-> dict:
        """ Devuelve el estado de cada símbolo (OK o Error). """
        return self.symbols_status