from typing import Dict, Any
from .state import InnovationState
from .graph import create_innovation_graph
import asyncio

# Importações antecipadas para evitar referências circulares
from .researcher_node import ResearcherNode
from .processor_node import ProcessorNode
from .synthesizer_node import SynthesizerNode
from .idealizer_node import IdealizerNode
from .evaluator_node import EvaluatorNode

class LangGraphOrchestrator:
    """
    Orquestrador baseado em LangGraph para o sistema de inovação.
    Mantém a mesma interface pública do orquestrador original para compatibilidade.
    """

    def __init__(self):
        """Inicializa o orquestrador."""
        self.graph = create_innovation_graph()
        self.state = InnovationState()
        self.results = {}

        # Criar propriedades para compatibilidade com o orquestrador original
        self._researcher = None
        self._synthesizer = None

    @property
    def researcher(self):
        """
        Propriedade para compatibilidade com o orquestrador original.
        Permite chamadas como orchestrator.researcher.research()
        """
        if self._researcher is None:
            self._researcher = ResearcherCompatibilityWrapper(self)
        return self._researcher

    @property
    def synthesizer(self):
        """
        Propriedade para compatibilidade com o orquestrador original.
        Permite chamadas como orchestrator.synthesizer.synthesize()
        """
        if self._synthesizer is None:
            self._synthesizer = SynthesizerCompatibilityWrapper(self)
        return self._synthesizer

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

        # Configurar o estado inicial
        self.state = InnovationState(
            topic=topic,
            business_context=business_context,
            max_web_results=max_research_results,
            max_arxiv_results=max_research_results,
            max_papers_to_process=max_papers_to_process
        )

        # Executar o grafo
        try:
            # Executar o grafo de forma assíncrona
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            final_state = event_loop.run_until_complete(self._run_graph())

            # Armazenar os resultados
            self.results = final_state.get_results()

            print("\n=== PROCESSO DE INOVAÇÃO CONCLUÍDO ===")
            return self.results

        except Exception as e:
            print(f"Erro durante o processo de inovação: {e}")
            import traceback
            traceback.print_exc()

            # Retornar resultados parciais se disponíveis
            self.results = self.state.get_results()
            return self.results

    async def _run_graph(self):
        """
        Executa o grafo de forma assíncrona.

        Returns:
            Estado final após a execução do grafo
        """
        # Executar o grafo com o estado inicial
        try:
            result = await self.graph.ainvoke(self.state)
            return result
        except Exception as e:
            print(f"Erro ao executar o grafo: {e}")
            import traceback
            traceback.print_exc()
            return self.state

    def get_results(self) -> Dict[str, Any]:
        """
        Retorna os resultados do processo de inovação.

        Returns:
            Dicionário com os resultados
        """
        return self.results


class ResearcherCompatibilityWrapper:
    """
    Wrapper para manter compatibilidade com a interface do ResearcherAgent original.
    """

    def __init__(self, orchestrator):
        """
        Inicializa o wrapper.

        Args:
            orchestrator: Instância do orquestrador LangGraph
        """
        self.orchestrator = orchestrator

    def research(self, topic: str, max_results: int = 5, business_context: str = "") -> list:
        """
        Método de compatibilidade para pesquisa.

        Args:
            topic: Tópico a ser pesquisado
            max_results: Número máximo de resultados
            business_context: Contexto de negócio

        Returns:
            Resultados da pesquisa
        """
        # Atualizar o estado com os parâmetros
        self.orchestrator.state.topic = topic
        self.orchestrator.state.max_web_results = max_results
        self.orchestrator.state.max_arxiv_results = max_results
        self.orchestrator.state.business_context = business_context

        # Executar apenas o nó de pesquisa
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        researcher = ResearcherNode()

        # Executar o nó de pesquisa de forma assíncrona
        updated_state = event_loop.run_until_complete(researcher.run(self.orchestrator.state))
        self.orchestrator.state = updated_state

        return self.orchestrator.state.research_results

    def process_papers(self, max_papers: int = 2) -> list:
        """
        Método de compatibilidade para processamento de artigos.

        Args:
            max_papers: Número máximo de artigos a processar

        Returns:
            Artigos processados
        """
        # Atualizar o estado com os parâmetros
        self.orchestrator.state.max_papers_to_process = max_papers

        # Executar apenas o nó de processamento
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        processor = ProcessorNode()

        # Executar o nó de processamento de forma assíncrona
        updated_state = event_loop.run_until_complete(processor.run(self.orchestrator.state))
        self.orchestrator.state = updated_state

        return self.orchestrator.state.processed_papers

    def generate_research_report(self, topic: str, processed_papers: list) -> str:
        """
        Método de compatibilidade para geração de relatório de pesquisa.

        Args:
            topic: Tópico da pesquisa
            processed_papers: Artigos processados

        Returns:
            Relatório de pesquisa
        """
        # Atualizar o estado com os parâmetros
        self.orchestrator.state.topic = topic
        self.orchestrator.state.processed_papers = processed_papers

        # Executar apenas o nó de geração de relatório
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        processor = ProcessorNode()

        # Executar o nó de geração de relatório de forma assíncrona
        updated_state = event_loop.run_until_complete(processor.generate_research_report(self.orchestrator.state))
        self.orchestrator.state = updated_state

        return self.orchestrator.state.research_report


class SynthesizerCompatibilityWrapper:
    """
    Wrapper para manter compatibilidade com a interface do SynthesizerAgent original.
    """

    def __init__(self, orchestrator):
        """
        Inicializa o wrapper.

        Args:
            orchestrator: Instância do orquestrador LangGraph
        """
        self.orchestrator = orchestrator

    def set_research_data(self, research_results: list):
        """
        Método de compatibilidade para definir dados de pesquisa.

        Args:
            research_results: Resultados da pesquisa
        """
        self.orchestrator.state.research_results = research_results

    def set_business_context(self, business_context: str):
        """
        Método de compatibilidade para definir o contexto de negócio.

        Args:
            business_context: Contexto de negócio
        """
        self.orchestrator.state.business_context = business_context

    def synthesize(self, research_report: str) -> Dict[str, Any]:
        """
        Método de compatibilidade para síntese.

        Args:
            research_report: Relatório de pesquisa

        Returns:
            Resultados da síntese
        """
        # Atualizar o estado com os parâmetros
        self.orchestrator.state.research_report = research_report

        # Executar os nós de análise de tendências, síntese, ideação e avaliação em sequência
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        # Executar o nó de análise de tendências
        from .trend_analyzer_node import TrendAnalyzerNode
        trend_analyzer = TrendAnalyzerNode()
        updated_state = event_loop.run_until_complete(trend_analyzer.run(self.orchestrator.state))
        self.orchestrator.state = updated_state

        # Executar o nó de síntese
        synthesizer = SynthesizerNode()
        updated_state = event_loop.run_until_complete(synthesizer.run(self.orchestrator.state))
        self.orchestrator.state = updated_state

        # Executar o nó de ideação
        idealizer = IdealizerNode()
        updated_state = event_loop.run_until_complete(idealizer.run(self.orchestrator.state))
        self.orchestrator.state = updated_state

        # Executar o nó de avaliação
        evaluator = EvaluatorNode()
        updated_state = event_loop.run_until_complete(evaluator.run(self.orchestrator.state))
        self.orchestrator.state = updated_state

        # Retornar os resultados da síntese
        return {
            "trends": self.orchestrator.state.trends,
            "insights": self.orchestrator.state.insights,
            "ideas": self.orchestrator.state.ideas,
            "evaluated_ideas": self.orchestrator.state.evaluated_ideas
        }

    def generate_final_report(self) -> str:
        """
        Método de compatibilidade para geração de relatório final.

        Returns:
            Relatório final
        """
        # Executar apenas o nó de geração de relatório final
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        evaluator = EvaluatorNode()

        # Executar o nó de geração de relatório final de forma assíncrona
        updated_state = event_loop.run_until_complete(evaluator.generate_final_report(self.orchestrator.state))
        self.orchestrator.state = updated_state

        return self.orchestrator.state.final_report
