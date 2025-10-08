class AnalysisResultsManager:
    def __init__(self):
        self.results = {}  # { "AAPL": {"estado": "OK", "señal": "compra"} }

    def build_results(self, symbols_status: dict, classified_signals: dict):
        self.results.clear()
        for symbol, estado in symbols_status.items():
            señal = classified_signals.get(symbol, "NULO").upper()
            self.results[symbol] = {
                "estado": estado,
                "señal": señal
            }

    def get_all_results(self):
        """Retorna todos los resultados del análisis."""
        return self.results

    def filter_by_signal(self, tipo_senal: str):
        """
        Filtra los resultados según el tipo de señal especificado.
        Valores válidos: "compra", "venta", "nulo"
        """
        tipo_senal = tipo_senal.upper()
        return {
            symbol: data
            for symbol, data in self.results.items()
            if data["señal"].upper() == tipo_senal
        }

    def __str__(self):
        """Representación amigable para depuración o impresión por consola."""
        lines = []
        for symbol, data in self.results.items():
            lines.append(f"{symbol}: Estado={data['estado']}, Señal={data['señal']}")
        return "\n".join(lines)