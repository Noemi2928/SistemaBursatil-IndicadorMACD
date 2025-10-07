# -----------------------------
# Módulo de gestión de símbolos
# -----------------------------
import re
from modules.error_manager import ErrorManager

class SymbolsManager:
    def __init__(self, error_manager: ErrorManager):
        self.error_manager = error_manager
        self.valid_symbols = []  # Lista final validada
        self.report = {}         # Reporte de eliminados
        self.messages = []

    def validate_symbols_from_list(self, symbols: list[str], truncate: bool = False):
        self.messages = []
        self.report = {}
        self.valid_symbols = []
        
        eliminated = {
            "duplicados": [],
            "invalidos": [],
            "exceso": []
        }

        # eliminar duplicados manteniendo orden
        seen = set()
        unique_symbols = []
        for s in symbols:
            if s not in seen:
                seen.add(s)
                unique_symbols.append(s)
            else:
                eliminated["duplicados"].append(s)
        if eliminated["duplicados"]:
            self.messages.append(self.error_manager.get_message("VALIDATION_DUPLICATES"))

        # filtrar solo letras
        only_letters = [s for s in unique_symbols if re.fullmatch(r'[A-Za-z]+', s)]
        invalid = set(unique_symbols) - set(only_letters)
        if invalid:
            eliminated["invalidos"] = list(invalid)
            self.messages.append(self.error_manager.get_message("VALIDATION_SYMBOLS"))

        # truncado si corresponde
        if len(only_letters) > 20:
          eliminated["exceso"] = only_letters[20:]
          if truncate:
              only_letters = only_letters[:20]
              self.messages.append(self.error_manager.get_message("VALIDATION_TOO_MANY"))

        if not only_letters:
            self.messages.append(self.error_manager.get_message("VALIDATION_EMPTY"))

        # actualizar atributos internos
        self.valid_symbols = only_letters
        self.report = eliminated


    def get_valid_symbols(self) -> list[str]:
        return self.valid_symbols

    def get_validation_report(self) -> dict:
        return self.report

    def get_messages(self) -> list[str]:
        return self.messages
