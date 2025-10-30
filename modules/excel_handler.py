# -----------------------------
# Módulo de Excel
# -----------------------------
import pandas as pd
from modules.error_manager import ErrorManager
from datetime import datetime

class ExcelHandler:
    def __init__(self, error_manager: ErrorManager):
        self.error_manager = error_manager

    def load_symbols(self, excel_file, column_name: str, truncate: bool = True) -> tuple[list[str], str | None]:
        message = None
        try:
            #df = pd.read_excel(excel_file)
            df = pd.read_excel(excel_file, engine="openpyxl")

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

        if not symbols:
            message = self.error_manager.get_message("EXCEL_COLUMN_NULL", column=column_name)
            return [], message

        return symbols, message

    def export_results(self, results: dict, filename: str | None = None) -> tuple[bool, str | None]:
        """
        Exporta los resultados a un archivo Excel usando ErrorManager para los mensajes.
        results: { "AAPL": {"estado": "OK", "señal": "COMPRA"}, ... }
        filename: nombre del archivo de salida
        Retorna: (True, None) si tuvo éxito, (False, mensaje de error) si falló.
        """
        if not results:
            message = self.error_manager.get_message("EXPORT_EMPTY")
            return False, message

        try:
            # Convertir el diccionario en DataFrame
            df = pd.DataFrame.from_dict(results, orient="index")
            df.index.name = "Símbolo"

            # Generar nombre de archivo dinámico si no se pasó
            if not filename:
                fecha_str = datetime.now().strftime("%Y%m%d")
                filename = f"resultados_macd_{fecha_str}.xlsx"

            # Guardar en Excel
            df.to_excel(filename)
            return True, filename

        except PermissionError:
            message = self.error_manager.get_message("EXPORT_PERMISSION", filename=filename)
            return False, message

        except Exception as e:
            message = self.error_manager.get_message("EXPORT_UNKNOWN", error=str(e))
            return False, message
