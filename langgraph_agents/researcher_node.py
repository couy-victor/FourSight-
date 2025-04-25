from typing import Dict, Any, Annotated
from .state import InnovationState
from utils import search_web, search_arxiv

class ResearcherNode:
    """
    Nó responsável por pesquisar informações relevantes para o processo de inovação.
    Combina resultados de diferentes fontes: web, artigos científicos, etc.
    """

    async def run(self, state: InnovationState) -> InnovationState:
        """
        Executa a pesquisa de informações sobre o tópico.

        Args:
            state: Estado atual do grafo

        Returns:
            Estado atualizado com os resultados da pesquisa
        """
        print(f"Pesquisando sobre: {state.topic}")

        # Atualizar o estágio atual
        state.current_stage = "Pesquisando informações"

        # Pesquisar na web
        try:
            web_results = self._search_web(state.topic, state.max_web_results)
            state.web_results = web_results
        except Exception as e:
            print(f"Erro ao pesquisar na web: {e}")
            state.web_results = []

        # Pesquisar artigos científicos
        try:
            arxiv_results = self._search_arxiv(state.topic, state.max_arxiv_results, context=state.business_context)
            state.arxiv_results = arxiv_results
        except Exception as e:
            print(f"Erro ao pesquisar no arXiv: {e}")
            state.arxiv_results = []

        # Combinar resultados
        state.research_results = state.web_results + state.arxiv_results

        return state

    def _search_web(self, query: str, max_results: int = 5) -> list:
        """
        Pesquisa informações na web.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados

        Returns:
            Lista de resultados da web
        """
        print(f"Pesquisando na web: {query}")
        results = search_web(query, max_results)

        # Formatar resultados
        formatted_results = []
        for result in results:
            formatted_results.append({
                'title': result.get('title', 'Sem título'),
                'url': result.get('url', ''),
                'snippet': result.get('snippet', 'Sem descrição'),
                'source': 'Web',
                'type': 'web'
            })

        print(f"Encontrados {len(formatted_results)} resultados na web")
        return formatted_results

    def _search_arxiv(self, query: str, max_results: int = 5, context: str = "") -> list:
        """
        Pesquisa artigos no arXiv.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            context: Contexto adicional para melhorar a relevância da pesquisa

        Returns:
            Lista de resultados do arXiv
        """
        print(f"Pesquisando no arXiv: {query}")
        results = search_arxiv(query, max_results, context=context)

        # Formatar resultados
        formatted_results = []
        for paper in results:
            formatted_results.append({
                'title': paper.get('title', 'Sem título'),
                'url': paper.get('url', ''),
                'pdf_url': paper.get('pdf_url', ''),
                'authors': paper.get('authors', []),
                'summary': paper.get('summary', 'Sem resumo'),
                'published_date': paper.get('published_date', ''),
                'categories': paper.get('categories', []),
                'source': 'arXiv',
                'type': 'paper'
            })

        print(f"Encontrados {len(formatted_results)} artigos no arXiv")
        return formatted_results
