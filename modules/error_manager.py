
class ErrorManager:
    def __init__(self):
        self.error_messages = {
            "EXCEL_LOAD": "Error al cargar el archivo Excel. Verifique la ruta o formato.",
            "EXCEL_COLUMN": "La columna '{column}' no existe en el archivo Excel.",
            "EXCEL_COLUMN_NULL": "La columna '{column}' del archivo seleccionado no contiene datos.",
            "EXCEL_TRUNCATE": "El archivo Excel contenía más de 20 símbolos. Se truncaron los primeros 20.",
            "VALIDATION_EXCESS_MANUAL": "Se superó el límite de 20 símbolos válidos. Por favor, elimine los símbolos en exceso para continuar: {exceso}.",
            #"VALIDATION_DUPLICATES": "Se eliminaron símbolos duplicados de la lista.",
            "VALIDATION_DUPLICATES": "Se eliminaron símbolos duplicados de la lista: {duplicates}.",
            "VALIDATION_SYMBOLS": "Algunos símbolos contienen caracteres inválidos: {invalidos}. Solo se permiten letras (A-Z).",
            "VALIDATION_TOO_MANY": "La lista contiene más de 20 símbolos. Se truncará a los primeros 20.",
            "VALIDATION_EMPTY": "No hay símbolos válidos después de las validaciones.",
            "UNKNOWN": "Ocurrió un error desconocido. Contacte al soporte técnico.",
            "EXPORT_EMPTY": "No hay resultados para exportar.",
            "EXPORT_PERMISSION": "No se puede escribir el archivo '{filename}'. Verifique que no esté abierto o que tenga permisos.",
            "EXPORT_UNKNOWN": "Ocurrió un error al exportar el archivo Excel: {error}",
            "NO_INTERNET": "No se detectó conexión a Internet. Verifique su conexión y vuelva a intentarlo."
        }


    def get_message(self, code: str, **kwargs) -> str:
        message = self.error_messages.get(code, self.error_messages["UNKNOWN"])
        return message.format(**kwargs) if kwargs else message
