from duckduckgo_search import DDGS
import json

class Tools:
    def __init__(self):
        self.ddgs = DDGS()

    def search_web(self, query, max_results=5):
        """Pesquisa na web usando DuckDuckGo."""
        print(f"\n[SISTEMA] Pesquisando por: {query}...")
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            if not results:
                return "Nenhum resultado encontrado."
            
            formatted_results = ""
            for i, r in enumerate(results):
                formatted_results += f"Resultado {i+1}:\nTítulo: {r['title']}\nLink: {r['href']}\nResumo: {r['body']}\n\n"
            return formatted_results
        except Exception as e:
            return f"Erro na pesquisa: {str(e)}"

    def read_url(self, url):
        """Lê o conteúdo de uma URL (Placeholder para implementação futura com requests/bs4)."""
        # Implementação básica poderia ser adicionada aqui se necessário
        return f"Capacidade de ler {url} ainda não implementada completamente, use o resumo da pesquisa."
