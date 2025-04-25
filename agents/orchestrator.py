from typing import Dict, Any
from .researcher_agent import ResearcherAgent
from .synthesizer_agent import SynthesizerAgent

class InnovationOrchestrator:
    """
    Orquestrador principal do sistema de inovação.
    Coordena os diferentes agentes e o fluxo de informações entre eles.
    """
    
    def __init__(self):
        """Inicializa o orquestrador."""
        self.researcher = ResearcherAgent()
        self.synthesizer = SynthesizerAgent()
        self.results = {}
    
    def run_innovation_process(self, topic: str, business_context: str, max_research_results: int = 5, max_papers_to_process: int = 2) -> Dict[str, Any]:
        """
        Executa o processo completo de inovação.
        
        Args:
            topic: Tópico a ser pesquisado
            business_context: Contexto de negócio para a inovação
            max_research_results: Número máximo de resultados de pesquisa por fonte
            max_papers_to_process: Número máximo de artigos a processar
            
        Returns:
            Dicionário com os resultados do processo de inovação
        """
        print(f"Iniciando processo de inovação para o tópico: {topic}")
        print(f"Contexto de negócio: {business_context}")
        
        # Etapa 1: Pesquisa
        print("\n=== ETAPA 1: PESQUISA ===")
        research_results = self.researcher.research(topic, max_research_results)
        
        # Etapa 2: Processamento de artigos
        print("\n=== ETAPA 2: PROCESSAMENTO DE ARTIGOS ===")
        processed_papers = self.researcher.process_papers(max_papers_to_process)
        
        # Etapa 3: Geração de relatório de pesquisa
        print("\n=== ETAPA 3: GERAÇÃO DE RELATÓRIO DE PESQUISA ===")
        research_report = self.researcher.generate_research_report(topic, processed_papers)
        
        # Etapa 4: Síntese e geração de ideias
        print("\n=== ETAPA 4: SÍNTESE E GERAÇÃO DE IDEIAS ===")
        self.synthesizer.set_research_data(research_results)
        self.synthesizer.set_business_context(business_context)
        synthesis_results = self.synthesizer.synthesize(research_report)
        
        # Etapa 5: Geração de relatório final
        print("\n=== ETAPA 5: GERAÇÃO DE RELATÓRIO FINAL ===")
        final_report = self.synthesizer.generate_final_report()
        
        # Armazenar resultados
        self.results = {
            'topic': topic,
            'business_context': business_context,
            'research_results': research_results,
            'processed_papers': processed_papers,
            'research_report': research_report,
            'synthesis_results': synthesis_results,
            'final_report': final_report
        }
        
        print("\n=== PROCESSO DE INOVAÇÃO CONCLUÍDO ===")
        return self.results
    
    def get_results(self) -> Dict[str, Any]:
        """
        Retorna os resultados do processo de inovação.
        
        Returns:
            Dicionário com os resultados
        """
        return self.results
