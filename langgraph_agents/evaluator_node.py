from typing import Dict, Any, List
from .state import InnovationState
from utils import call_groq_api

class EvaluatorNode:
    """
    Nó responsável por avaliar as ideias geradas com base em critérios específicos.
    """

    async def run(self, state: InnovationState) -> InnovationState:
        """
        Avalia as ideias geradas com base em critérios específicos.

        Args:
            state: Estado atual do grafo

        Returns:
            Estado atualizado com as ideias avaliadas
        """
        # Atualizar o estágio atual
        state.current_stage = "Avaliando ideias"

        # Avaliar cada ideia
        evaluated_ideas = []
        for idea in state.ideas:
            evaluated_idea = await self._evaluate_idea(idea, state.business_context, state.topic)
            evaluated_ideas.append(evaluated_idea)

        state.evaluated_ideas = evaluated_ideas

        return state

    async def _evaluate_idea(self, idea: Dict[str, Any], business_context: str, topic: str) -> Dict[str, Any]:
        """
        Avalia uma ideia com base em critérios específicos.

        Args:
            idea: Ideia a ser avaliada
            business_context: Contexto de negócio
            topic: Tópico de pesquisa

        Returns:
            Ideia avaliada com pontuações e justificativas
        """
        # Critérios de avaliação
        criteria = [
            "Inovação",
            "Viabilidade",
            "Impacto",
            "Alinhamento Estratégico",
            "Escalabilidade"
        ]

        # Criar o prompt para avaliação
        prompt = f"""
        Avalie a seguinte ideia relacionada ao tópico "{topic}" com base no contexto de negócio fornecido.

        Contexto de Negócio:
        {business_context}

        Ideia:
        {idea['idea']}

        Avalie a ideia nos seguintes critérios (escala de 0 a 10):

        1. Inovação: Quão original e diferenciada é a ideia em relação às soluções existentes?
        2. Viabilidade: Quão viável é implementar esta ideia considerando recursos, tecnologia e tempo?
        3. Impacto: Qual o potencial de impacto da ideia no problema ou oportunidade identificada?
        4. Alinhamento Estratégico: Quão bem a ideia se alinha ao contexto de negócio fornecido?
        5. Escalabilidade: Qual o potencial de crescimento e expansão da ideia?

        Para cada critério:
        1. Atribua uma pontuação de 0 a 10
        2. Forneça uma justificativa detalhada para a pontuação

        Ao final, forneça uma avaliação geral da ideia, destacando pontos fortes, limitações e sugestões de melhoria.

        Formato de saída:

        ## Pontuações

        - Inovação: [pontuação]/10
          [justificativa]

        - Viabilidade: [pontuação]/10
          [justificativa]

        - Impacto: [pontuação]/10
          [justificativa]

        - Alinhamento Estratégico: [pontuação]/10
          [justificativa]

        - Escalabilidade: [pontuação]/10
          [justificativa]

        ## Avaliação Geral

        [Avaliação geral da ideia, destacando pontos fortes, limitações e sugestões de melhoria]
        """

        # Chamar a API para avaliar a ideia
        system_message = "Você é um especialista em avaliação de ideias de inovação com experiência em análise de negócios e empreendedorismo."
        response = call_groq_api(prompt, system_message, 1200)

        # Processar a resposta para extrair as pontuações e justificativas
        scores = {}
        evaluation = ""
        current_section = None

        for line in response.split('\n'):
            line = line.strip()

            if line.startswith('## Pontuações'):
                current_section = 'scores'
            elif line.startswith('## Avaliação Geral'):
                current_section = 'evaluation'
                evaluation = ""
            elif current_section == 'scores' and line.startswith('- '):
                # Extrair o critério e a pontuação
                parts = line.split(':')
                if len(parts) >= 2:
                    criterion = parts[0].replace('- ', '').strip()
                    score_text = parts[1].strip().split('/')[0].strip()
                    try:
                        score = float(score_text)
                        scores[criterion] = {'score': score, 'justification': ''}
                    except ValueError:
                        pass
            elif current_section == 'scores' and scores and line and not line.startswith('-'):
                # Adicionar justificativa ao último critério
                last_criterion = list(scores.keys())[-1]
                if scores[last_criterion]['justification']:
                    scores[last_criterion]['justification'] += ' ' + line
                else:
                    scores[last_criterion]['justification'] = line
            elif current_section == 'evaluation':
                evaluation += line + '\n'

        # Calcular a pontuação média
        if scores:
            average_score = sum(item['score'] for item in scores.values()) / len(scores)
        else:
            average_score = 0

        # Criar a ideia avaliada
        evaluated_idea = idea.copy()
        evaluated_idea['scores'] = scores
        evaluated_idea['evaluation'] = evaluation.strip()
        evaluated_idea['average_score'] = average_score

        return evaluated_idea

    async def generate_final_report(self, state: InnovationState) -> InnovationState:
        """
        Gera o relatório final com base nas ideias avaliadas e nos insights.

        Args:
            state: Estado atual do grafo

        Returns:
            Estado atualizado com o relatório final
        """
        # Atualizar o estágio atual
        state.current_stage = "Gerando relatório final"

        # Formatar ideias avaliadas para o prompt
        ideas_text = ""
        for i, idea in enumerate(state.evaluated_ideas):
            ideas_text += f"\n\nIdeia {i+1} (Pontuação: {idea['average_score']:.1f}/10):\n"
            ideas_text += idea['idea']
            ideas_text += f"\n\nAvaliação:\n{idea['evaluation']}"

        # Formatar insights para o prompt
        insights_text = "\n\n".join(state.insights)

        # Criar o prompt para o relatório final
        prompt = f"""
        Crie um relatório final de inovação para o tópico: {state.topic}

        Contexto de Negócio:
        {state.business_context}

        Insights Identificados:
        {insights_text}

        Ideias Avaliadas:
        {ideas_text}

        Com base nas informações acima, crie um relatório final estruturado que:
        1. Introduza o tópico e o contexto de negócio
        2. Resuma os principais insights identificados
        3. Apresente as ideias geradas, destacando suas pontuações e pontos fortes
        4. Recomende as ideias mais promissoras para desenvolvimento futuro
        5. Sugira próximos passos para o processo de inovação

        O relatório deve ser abrangente, bem estruturado e orientado para ação.

        Relatório Final:
        """

        # Chamar a API para gerar o relatório final
        system_message = "Você é um consultor de inovação especializado em criar relatórios executivos que sintetizam pesquisas e ideias em recomendações acionáveis."
        report = call_groq_api(prompt, system_message, 2000)

        state.final_report = report

        return state
