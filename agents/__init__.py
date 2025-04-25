# Initialize agents package
from .researcher_agent import ResearcherAgent
from .synthesizer_agent import SynthesizerAgent
from .orchestrator import InnovationOrchestrator

# Importar o orquestrador LangGraph
try:
    from langgraph_agents import LangGraphOrchestrator
    has_langgraph = True
except ImportError:
    has_langgraph = False

# Importações dos agentes originais
try:
    from .researcher import ResearcherAgent as OriginalResearcherAgent
    from .contextual import ContextualAgent
    from .synthesizer import SynthesizerAgent as OriginalSynthesizerAgent
    from .idealizer import IdealizerAgent
    from .evaluator import EvaluatorAgent

    if has_langgraph:
        __all__ = [
            'ResearcherAgent',
            'SynthesizerAgent',
            'InnovationOrchestrator',
            'LangGraphOrchestrator',
            'OriginalResearcherAgent',
            'ContextualAgent',
            'OriginalSynthesizerAgent',
            'IdealizerAgent',
            'EvaluatorAgent'
        ]
    else:
        __all__ = [
            'ResearcherAgent',
            'SynthesizerAgent',
            'InnovationOrchestrator',
            'OriginalResearcherAgent',
            'ContextualAgent',
            'OriginalSynthesizerAgent',
            'IdealizerAgent',
            'EvaluatorAgent'
        ]
except ImportError:
    if has_langgraph:
        __all__ = [
            'ResearcherAgent',
            'SynthesizerAgent',
            'InnovationOrchestrator',
            'LangGraphOrchestrator'
        ]
    else:
        __all__ = [
            'ResearcherAgent',
            'SynthesizerAgent',
            'InnovationOrchestrator'
        ]
