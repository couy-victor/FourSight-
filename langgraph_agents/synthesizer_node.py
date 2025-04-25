from typing import Dict, Any, List
from .state import InnovationState
from utils import call_groq_api

class SynthesizerNode:
    """
    Nó responsável por sintetizar informações e gerar insights a partir dos dados coletados.
    """

    async def run(self, state: InnovationState) -> InnovationState:
        """
        Sintetiza informações e gera insights a partir dos dados coletados e tendências identificadas.

        Args:
            state: Estado atual do grafo

        Returns:
            Estado atualizado com os insights gerados
        """
        # Atualizar o estágio atual
        state.current_stage = "Sintetizando informações"

        # Extrair insights do relatório de pesquisa e tendências identificadas
        insights = await self._extract_insights(
            state.research_report,
            state.business_context,
            state.trends
        )
        state.insights = insights

        return state

    async def _extract_insights(self, research_report: str, business_context: str, trends: List[Dict[str, Any]] = None) -> List[str]:
        """
        Extrai insights do relatório de pesquisa e tendências identificadas.

        Args:
            research_report: Relatório de pesquisa
            business_context: Contexto de negócio
            trends: Tendências emergentes identificadas

        Returns:
            Lista de insights extraídos
        """
        # Preparar o contexto de tendências
        trends_context = ""
        if trends:
            trends_context = "Tendências Emergentes Identificadas:\n"
            for i, trend in enumerate(trends):
                trends_context += f"\n{i+1}. {trend.get('name', 'Tendência sem nome')}"
                if 'maturity' in trend:
                    trends_context += f" ({trend['maturity']})"
                if 'description' in trend and trend['description']:
                    # Truncar descrições muito longas
                    description = trend['description']
                    if len(description) > 200:
                        description = description[:200] + "..."
                    trends_context += f"\n   {description}\n"

        # Criar o prompt para extração de insights
        prompt = f"""
        Com base no relatório de pesquisa, nas tendências emergentes identificadas e no contexto de negócio fornecido,
        identifique e extraia 5-7 insights principais que poderiam levar a oportunidades de inovação.

        Contexto de Negócio:
        {business_context}

        {trends_context}

        Relatório de Pesquisa:
        {research_report}

        Para cada insight:
        1. Seja específico e concreto
        2. Relacione o insight com as tendências emergentes identificadas e o contexto de negócio
        3. Explique por que este insight é relevante para inovação
        4. Sugira possíveis direções para explorar este insight
        5. Indique quais tendências emergentes estão relacionadas a este insight

        Formato de saída:
        - Insight 1: [Título do Insight]
          [Descrição detalhada do insight e sua relevância]
          [Conexão com tendências emergentes específicas]

        - Insight 2: [Título do Insight]
          [Descrição detalhada do insight e sua relevância]
          [Conexão com tendências emergentes específicas]

        E assim por diante...
        """

        # Chamar a API para gerar os insights
        system_message = "Você é um especialista em análise de tendências e identificação de oportunidades de inovação."
        response = call_groq_api(prompt, system_message, 1200)

        # Processar a resposta para extrair os insights
        insights = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('- Insight ') or line.startswith('Insight '):
                insights.append(line)
            elif insights and line:
                insights[-1] += '\n' + line

        return insights
