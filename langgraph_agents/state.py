from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class InnovationState(BaseModel):
    """
    Classe que representa o estado do grafo de inovação.
    Contém todos os dados compartilhados entre os nós do grafo.
    """
    # Entradas do usuário
    topic: str = Field(default="", description="Tópico de pesquisa")
    business_context: str = Field(default="", description="Contexto de negócio")

    # Configurações
    max_web_results: int = Field(default=3, description="Número máximo de resultados da web")
    max_arxiv_results: int = Field(default=3, description="Número máximo de artigos do arXiv")
    max_papers_to_process: int = Field(default=2, description="Número máximo de PDFs a processar")

    # Resultados da pesquisa
    research_results: List[Dict[str, Any]] = Field(default_factory=list, description="Resultados da pesquisa (web e arXiv)")
    web_results: List[Dict[str, Any]] = Field(default_factory=list, description="Resultados da pesquisa na web")
    arxiv_results: List[Dict[str, Any]] = Field(default_factory=list, description="Resultados da pesquisa no arXiv")

    # Artigos processados
    processed_papers: List[Dict[str, Any]] = Field(default_factory=list, description="Artigos processados com RAG")

    # Relatórios e sínteses
    research_report: str = Field(default="", description="Relatório de pesquisa")
    trends: List[Dict[str, Any]] = Field(default_factory=list, description="Tendências emergentes identificadas")
    insights: List[str] = Field(default_factory=list, description="Insights extraídos")

    # Ideias e avaliações
    ideas: List[Dict[str, Any]] = Field(default_factory=list, description="Ideias geradas")
    evaluated_ideas: List[Dict[str, Any]] = Field(default_factory=list, description="Ideias avaliadas")

    # Relatório final
    final_report: str = Field(default="", description="Relatório final de inovação")

    # Estado de execução
    current_stage: str = Field(default="", description="Estágio atual do processo")
    error: Optional[str] = Field(default=None, description="Erro ocorrido durante o processo")

    def get_results(self) -> Dict[str, Any]:
        """
        Retorna os resultados do processo de inovação em um formato compatível
        com o orquestrador original.

        Returns:
            Dicionário com os resultados
        """
        synthesis_results = {
            "trends": self.trends,
            "insights": self.insights,
            "ideas": self.ideas,
            "evaluated_ideas": self.evaluated_ideas
        }

        return {
            'topic': self.topic,
            'business_context': self.business_context,
            'research_results': self.research_results,
            'processed_papers': self.processed_papers,
            'research_report': self.research_report,
            'synthesis_results': synthesis_results,
            'final_report': self.final_report
        }
