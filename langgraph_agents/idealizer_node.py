from typing import Dict, Any, List
from .state import InnovationState
from utils import call_groq_api

class IdealizerNode:
    """
    Nó responsável por gerar ideias inovadoras com base nos insights e no contexto de negócio.
    """

    async def run(self, state: InnovationState) -> InnovationState:
        """
        Gera ideias inovadoras com base nos insights, tendências e no contexto de negócio.

        Args:
            state: Estado atual do grafo

        Returns:
            Estado atualizado com as ideias geradas
        """
        # Atualizar o estágio atual
        state.current_stage = "Gerando ideias"

        # Gerar ideias com base nos insights, tendências e no contexto de negócio
        ideas = await self._generate_ideas(
            state.insights,
            state.business_context,
            state.topic,
            state.trends
        )
        state.ideas = ideas

        return state

    async def _generate_ideas(self, insights: List[str], business_context: str, topic: str, trends: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Gera ideias inovadoras com base nos insights, tendências e no contexto de negócio.

        Args:
            insights: Lista de insights extraídos
            business_context: Contexto de negócio
            topic: Tópico de pesquisa
            trends: Tendências emergentes identificadas

        Returns:
            Lista de ideias geradas
        """
        # Formatar insights para o prompt
        insights_text = "\n\n".join(insights)

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
                    if len(description) > 150:
                        description = description[:150] + "..."
                    trends_context += f"\n   {description}\n"

        # Criar o prompt para geração de ideias
        prompt = f"""
        Com base nos insights, tendências emergentes e no contexto de negócio fornecido,
        gere 3-5 ideias inovadoras relacionadas ao tópico: {topic}

        Contexto de Negócio:
        {business_context}

        {trends_context}

        Insights:
        {insights_text}

        Para cada ideia:
        1. Forneça um título criativo, memorável e comercialmente atraente (como um nome de produto ou serviço)
           - O título deve ser curto (3-5 palavras) e impactante
           - Deve comunicar claramente o valor principal da ideia
           - Deve incluir um subtítulo explicativo
        2. Descreva a ideia em detalhes (problema que resolve, solução proposta, benefícios)
        3. Explique como a ideia se relaciona com as tendências emergentes e insights identificados
        4. Descreva o potencial impacto da ideia
        5. Sugira possíveis próximos passos para desenvolver a ideia
        6. Indique quais tendências emergentes específicas a ideia aproveita

        Formato de saída:
        # [Nome da Solução/Produto]: [Subtítulo explicativo]

        ## Descrição
        [Descrição detalhada da ideia]

        ## Relação com Tendências e Insights
        [Como a ideia se relaciona com as tendências emergentes e insights identificados]

        ## Impacto Potencial
        [Descrição do impacto potencial da ideia]

        ## Próximos Passos
        [Sugestões de próximos passos para desenvolver a ideia]

        ## Tendências Aproveitadas
        [Lista das tendências emergentes específicas que esta ideia aproveita]

        ---

        # [Nome da Solução/Produto]: [Subtítulo explicativo]

        ...e assim por diante.
        """

        # Chamar a API para gerar as ideias
        system_message = """Você é um especialista em inovação e geração de ideias criativas com base em pesquisas e insights.
        Você tem experiência em criar nomes de produtos e serviços memoráveis e comercialmente atraentes.
        Suas ideias sempre incluem títulos criativos que capturam a essência da solução proposta."""
        response = call_groq_api(prompt, system_message, 1500)

        # Processar a resposta para extrair as ideias
        ideas = []
        current_idea = None

        for line in response.split('\n'):
            line = line.strip()

            # Nova ideia começa com #
            if line.startswith('# '):
                if current_idea:
                    ideas.append(current_idea)
                current_idea = {'idea': line}
            # Linha de separação entre ideias
            elif line == '---':
                if current_idea:
                    ideas.append(current_idea)
                current_idea = None
            # Adicionar linha à ideia atual
            elif current_idea is not None:
                current_idea['idea'] += '\n' + line

        # Adicionar a última ideia se existir
        if current_idea:
            ideas.append(current_idea)

        return ideas
