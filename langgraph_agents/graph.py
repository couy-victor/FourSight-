from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import InnovationState
from .researcher_node import ResearcherNode
from .processor_node import ProcessorNode
from .trend_analyzer_node import TrendAnalyzerNode
from .synthesizer_node import SynthesizerNode
from .idealizer_node import IdealizerNode
from .evaluator_node import EvaluatorNode

def create_innovation_graph():
    """
    Cria o grafo de inovação com todos os nós e arestas.

    Returns:
        Grafo de inovação configurado
    """
    # Criar os nós
    researcher = ResearcherNode()
    processor = ProcessorNode()
    trend_analyzer = TrendAnalyzerNode()
    synthesizer = SynthesizerNode()
    idealizer = IdealizerNode()
    evaluator = EvaluatorNode()

    # Criar o grafo
    builder = StateGraph(InnovationState)

    # Adicionar os nós ao grafo
    builder.add_node("researcher", researcher.run)
    builder.add_node("processor", processor.run)
    builder.add_node("report_generator", processor.generate_research_report)
    builder.add_node("trend_analyzer", trend_analyzer.run)
    builder.add_node("synthesizer", synthesizer.run)
    builder.add_node("idealizer", idealizer.run)
    builder.add_node("evaluator", evaluator.run)
    builder.add_node("report_finalizer", evaluator.generate_final_report)

    # Definir as arestas (fluxo de trabalho)
    builder.add_edge("researcher", "processor")
    builder.add_edge("processor", "report_generator")
    builder.add_edge("report_generator", "trend_analyzer")
    builder.add_edge("trend_analyzer", "synthesizer")
    builder.add_edge("synthesizer", "idealizer")
    builder.add_edge("idealizer", "evaluator")
    builder.add_edge("evaluator", "report_finalizer")
    builder.add_edge("report_finalizer", END)

    # Definir o nó inicial
    builder.set_entry_point("researcher")

    # Compilar o grafo
    return builder.compile()
