from typing import Dict, Any, Annotated, List
from .state import InnovationState
from utils import mcp

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

        try:
            # Usar o MCP para obter contexto de múltiplas fontes
            results = mcp.get_context(
                query=state.topic,
                max_results=max(state.max_web_results, state.max_arxiv_results),
                context=state.business_context
            )

            # Atualizar o estado com os resultados
            state.web_results = results['web']
            state.arxiv_results = results['arxiv']

            # Adicionar resultados do Reddit e Product Hunt ao estado
            state.reddit_results = results['reddit']
            state.producthunt_results = results['producthunt']

            # Combinar todos os resultados
            state.research_results = results['all']

            print(f"Resultados encontrados: Web={len(state.web_results)}, arXiv={len(state.arxiv_results)}, "
                  f"Reddit={len(state.reddit_results)}, Product Hunt={len(state.producthunt_results)}")

        except Exception as e:
            print(f"Erro ao pesquisar informações: {e}")
            # Inicializar listas vazias em caso de erro
            state.web_results = []
            state.arxiv_results = []
            state.reddit_results = []
            state.producthunt_results = []
            state.research_results = []

        return state

    # Métodos de pesquisa individuais removidos, pois agora usamos o MCP centralizado
