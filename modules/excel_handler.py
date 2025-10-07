# -----------------------------
# Módulo de Excel
# -----------------------------
import pandas as pd
from modules.error_manager import ErrorManager

class ExcelHandler:
    def __init__(self, error_manager: ErrorManager):
        self.error_manager = error_manager

    def load_symbols(self, excel_file, column_name: str, truncate: bool = True) -> tuple[list[str], str | None]:
        message = None
        try:
            df = pd.read_excel(excel_file)
        except FileNotFoundError:
            message = self.error_manager.get_message("EXCEL_LOAD")
            return [], message
        except Exception:
            message = self.error_manager.get_message("EXCEL_LOAD")
            return [], message

        if column_name not in df.columns:
            message = self.error_manager.get_message("EXCEL_COLUMN", column=column_name)
            return [], message

        # Limpiamos valores vacíos, espacios y convertimos a mayúsculas
        symbols = [str(s).strip().upper() for s in df[column_name].dropna()]

        # Truncado si hay más de 20 símbolos
        if truncate and len(symbols) > 20:
            symbols = symbols[:20]
            message = self.error_manager.get_message("EXCEL_TRUNCATE")

        return symbols, message