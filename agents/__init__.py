# Initialize agents package
from .researcher_agent import ResearcherAgent
from .synthesizer_agent import SynthesizerAgent
from .orchestrator import InnovationOrchestrator

# Importações dos agentes originais
try:
    from .researcher import ResearcherAgent as OriginalResearcherAgent
    from .contextual import ContextualAgent
    from .synthesizer import SynthesizerAgent as OriginalSynthesizerAgent
    from .idealizer import IdealizerAgent
    from .evaluator import EvaluatorAgent

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
    __all__ = [
        'ResearcherAgent',
        'SynthesizerAgent',
        'InnovationOrchestrator'
    ]
