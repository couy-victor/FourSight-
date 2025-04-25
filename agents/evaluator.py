import os
import openai
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EvaluatorAgent:
    """
    Agent responsible for evaluating and prioritizing generated ideas.
    """
    
    def __init__(self):
        """Initialize the EvaluatorAgent with API keys and configurations."""
        # Load API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Set OpenAI API key
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Load evaluation criteria
        self.evaluation_criteria = self._load_evaluation_criteria()
    
    def evaluate_ideas(self, ideas, context_data, impact_level=None):
        """
        Evaluate and prioritize generated ideas.
        
        Args:
            ideas (list): List of idea dictionaries from the IdealizerAgent
            context_data (dict): Contextual information about the business pain or topic
            impact_level (int, optional): User-defined impact level (1-10)
            
        Returns:
            list: List of evaluated and prioritized idea dictionaries
        """
        # If OpenAI API key is available, use it for evaluation
        if self.openai_api_key:
            return self._evaluate_with_openai(ideas, context_data, impact_level)
        else:
            # Use rule-based approach as fallback
            return self._evaluate_with_rules(ideas, context_data, impact_level)
    
    def _evaluate_with_openai(self, ideas, context_data, impact_level):
        """
        Use OpenAI to evaluate ideas.
        """
        try:
            # Extract relevant information
            sector = context_data.get('sector', 'Não especificado')
            
            # Create prompt based on context type
            if 'pain_points' in context_data:
                # Business pain flow
                pain_points = context_data.get('pain_points', ['Não especificado'])
                
                prompt = f"""
                Avalie as seguintes ideias para resolver dores de negócio no setor de {sector}.
                
                CONTEXTO:
                Setor: {sector}
                Pontos de dor: {', '.join(pain_points)}
                Nível de impacto desejado (1-10): {impact_level if impact_level else 'Não especificado'}
                
                IDEIAS A AVALIAR:
                """
                
                # Add each idea to the prompt
                for i, idea in enumerate(ideas):
                    prompt += f"""
                    Ideia {i+1}: {idea['title']}
                    Descrição: {idea['description']}
                    Benefícios: {idea['benefits']}
                    Viabilidade técnica: {idea['technical_feasibility']}/10
                    Impacto potencial: {idea['potential_impact']}/10
                    Riscos: {idea['risks']}
                    """
                
                prompt += """
                Para cada ideia, avalie:
                1. alignment_score: Alinhamento com as dores de negócio (1-10)
                2. innovation_score: Nível de inovação (1-10)
                3. feasibility_score: Viabilidade de implementação (1-10)
                4. market_potential: Potencial de mercado (1-10)
                5. overall_score: Pontuação geral (1-10)
                6. strengths: Principais pontos fortes
                7. weaknesses: Principais pontos fracos
                8. recommendations: Recomendações para melhorar a ideia
                
                Forneça a avaliação em formato JSON como uma lista de objetos, mantendo as propriedades originais de cada ideia e adicionando as avaliações.
                """
            else:
                # Topic exploration flow
                topic = context_data.get('topic', 'Não especificado')
                
                prompt = f"""
                Avalie as seguintes ideias relacionadas ao tópico "{topic}" para o setor de {sector}.
                
                CONTEXTO:
                Tópico: {topic}
                Setor: {sector}
                
                IDEIAS A AVALIAR:
                """
                
                # Add each idea to the prompt
                for i, idea in enumerate(ideas):
                    prompt += f"""
                    Ideia {i+1}: {idea['title']}
                    Descrição: {idea['description']}
                    Benefícios: {idea['benefits']}
                    Viabilidade técnica: {idea['technical_feasibility']}/10
                    Impacto potencial: {idea['potential_impact']}/10
                    Riscos: {idea['risks']}
                    """
                
                prompt += """
                Para cada ideia, avalie:
                1. relevance_score: Relevância para o tópico e setor (1-10)
                2. innovation_score: Nível de inovação (1-10)
                3. feasibility_score: Viabilidade de implementação (1-10)
                4. market_potential: Potencial de mercado (1-10)
                5. overall_score: Pontuação geral (1-10)
                6. strengths: Principais pontos fortes
                7. weaknesses: Principais pontos fracos
                8. recommendations: Recomendações para melhorar a ideia
                
                Forneça a avaliação em formato JSON como uma lista de objetos, mantendo as propriedades originais de cada ideia e adicionando as avaliações.
                """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em avaliação de ideias de inovação com vasta experiência em diversos setores."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            # Parse the JSON response
            import json
            content = response.choices[0].message.content.strip()
            
            # Extract JSON part if there's surrounding text
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content
            
            evaluated_ideas = json.loads(json_str)
            
            # Sort ideas by overall score
            evaluated_ideas.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
            
            # Add score property for consistency
            for idea in evaluated_ideas:
                idea['score'] = idea.get('overall_score', 0)
            
            return evaluated_ideas
            
        except Exception as e:
            print(f"Error evaluating ideas with OpenAI: {e}")
            # Fall back to rule-based approach
            return self._evaluate_with_rules(ideas, context_data, impact_level)
    
    def _evaluate_with_rules(self, ideas, context_data, impact_level):
        """
        Evaluate ideas using rule-based approach (fallback).
        """
        evaluated_ideas = []
        
        for idea in ideas:
            # Copy original idea
            evaluated_idea = idea.copy()
            
            # Calculate scores based on existing properties
            technical_feasibility = idea.get('technical_feasibility', random.randint(5, 9))
            potential_impact = idea.get('potential_impact', random.randint(6, 10))
            
            # Adjust impact based on user preference if available
            if impact_level:
                impact_weight = impact_level / 5  # Convert 1-10 scale to a multiplier
                potential_impact = min(10, int(potential_impact * impact_weight))
            
            # Calculate overall score
            innovation_score = random.randint(6, 9)
            market_potential = random.randint(5, 9)
            
            overall_score = (technical_feasibility + potential_impact + innovation_score + market_potential) / 4
            overall_score = round(overall_score, 1)
            
            # Add evaluation properties
            evaluated_idea['innovation_score'] = innovation_score
            evaluated_idea['market_potential'] = market_potential
            evaluated_idea['overall_score'] = overall_score
            evaluated_idea['score'] = overall_score  # For consistency
            
            # Add strengths, weaknesses and recommendations
            evaluated_idea['strengths'] = self._generate_strengths(idea)
            evaluated_idea['weaknesses'] = self._generate_weaknesses(idea)
            evaluated_idea['recommendations'] = self._generate_recommendations(idea)
            
            evaluated_ideas.append(evaluated_idea)
        
        # Sort ideas by overall score
        evaluated_ideas.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        return evaluated_ideas
    
    def _generate_strengths(self, idea):
        """Generate strengths based on idea properties."""
        strengths = []
        
        if idea.get('technical_feasibility', 0) >= 7:
            strengths.append("Alta viabilidade técnica")
        
        if idea.get('potential_impact', 0) >= 8:
            strengths.append("Alto impacto potencial")
        
        # Add a random strength from predefined list
        random_strengths = [
            "Abordagem inovadora",
            "Potencial de escalabilidade",
            "Diferencial competitivo claro",
            "Modelo de negócio sustentável",
            "Alinhamento com tendências de mercado"
        ]
        strengths.append(random.choice(random_strengths))
        
        return strengths
    
    def _generate_weaknesses(self, idea):
        """Generate weaknesses based on idea properties."""
        weaknesses = []
        
        if idea.get('technical_feasibility', 10) <= 6:
            weaknesses.append("Desafios técnicos significativos")
        
        if idea.get('potential_impact', 10) <= 5:
            weaknesses.append("Impacto potencial limitado")
        
        # Add a random weakness from predefined list
        random_weaknesses = [
            "Possível resistência do mercado",
            "Necessidade de investimento inicial alto",
            "Dependência de adoção por parceiros",
            "Complexidade de implementação",
            "Desafios regulatórios potenciais"
        ]
        weaknesses.append(random.choice(random_weaknesses))
        
        return weaknesses
    
    def _generate_recommendations(self, idea):
        """Generate recommendations based on idea properties."""
        recommendations = []
        
        if idea.get('technical_feasibility', 10) <= 6:
            recommendations.append("Realizar prova de conceito técnica")
        
        if idea.get('potential_impact', 10) <= 7:
            recommendations.append("Explorar formas de aumentar o impacto no negócio")
        
        # Add a random recommendation from predefined list
        random_recommendations = [
            "Validar com potenciais usuários antes de avançar",
            "Desenvolver MVP para teste de mercado",
            "Considerar parcerias estratégicas para implementação",
            "Refinar o modelo de negócio",
            "Realizar análise detalhada de concorrentes"
        ]
        recommendations.append(random.choice(random_recommendations))
        
        return recommendations
    
    def _load_evaluation_criteria(self):
        """
        Load evaluation criteria.
        """
        return {
            'innovation': {
                'name': 'Nível de Inovação',
                'description': 'Avalia o quão inovadora é a ideia em relação ao estado atual do mercado',
                'weight': 0.25
            },
            'feasibility': {
                'name': 'Viabilidade',
                'description': 'Avalia a viabilidade técnica e operacional de implementação',
                'weight': 0.25
            },
            'impact': {
                'name': 'Impacto Potencial',
                'description': 'Avalia o potencial impacto no negócio e no mercado',
                'weight': 0.3
            },
            'alignment': {
                'name': 'Alinhamento Estratégico',
                'description': 'Avalia o alinhamento com o contexto do problema ou tópico',
                'weight': 0.2
            }
        }
