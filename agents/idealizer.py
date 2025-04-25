import os
import openai
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IdealizerAgent:
    """
    Agent responsible for generating innovative ideas based on synthesized information.
    """
    
    def __init__(self):
        """Initialize the IdealizerAgent with API keys and configurations."""
        # Load API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Set OpenAI API key
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Load innovation techniques
        self.innovation_techniques = self._load_innovation_techniques()
    
    def generate_ideas(self, synthesis):
        """
        Generate innovative ideas based on synthesized information.
        
        Args:
            synthesis (dict): Synthesized information from the SynthesizerAgent
            
        Returns:
            list: List of idea dictionaries with title, description, benefits, etc.
        """
        # If OpenAI API key is available, use it for idea generation
        if self.openai_api_key:
            return self._generate_with_openai(synthesis)
        else:
            # Use rule-based approach as fallback
            return self._generate_with_rules(synthesis)
    
    def _generate_with_openai(self, synthesis):
        """
        Use OpenAI to generate innovative ideas.
        """
        try:
            # Extract relevant information from synthesis
            sector = synthesis.get('context_data', {}).get('sector', 'Não especificado')
            
            # Select a random innovation technique
            technique = random.choice(self.innovation_techniques)
            
            # Create prompt based on synthesis content
            if 'potential_solutions' in synthesis:
                # Business pain flow
                pain_points = synthesis.get('context_data', {}).get('pain_points', ['Não especificado'])
                
                prompt = f"""
                Gere 3-5 ideias inovadoras para resolver dores de negócio no setor de {sector}.
                
                CONTEXTO:
                Setor: {sector}
                Pontos de dor: {', '.join(pain_points)}
                Insights principais: {', '.join(synthesis.get('key_insights', ['Não especificado']))}
                Tendências de mercado: {', '.join(synthesis.get('market_trends', ['Não especificado']))}
                Oportunidades de inovação: {', '.join(synthesis.get('innovation_opportunities', ['Não especificado']))}
                
                TÉCNICA DE INOVAÇÃO A UTILIZAR:
                {technique['name']}: {technique['description']}
                
                Para cada ideia, forneça:
                1. title: Título da ideia (curto e impactante)
                2. description: Descrição detalhada da solução
                3. benefits: Principais benefícios
                4. technical_feasibility: Avaliação da viabilidade técnica (1-10)
                5. potential_impact: Avaliação do impacto potencial (1-10)
                6. risks: Principais riscos ou desafios
                7. implementation_steps: Passos iniciais para implementação
                
                Forneça as ideias em formato JSON como uma lista de objetos.
                """
            else:
                # Topic exploration flow
                topic = synthesis.get('context_data', {}).get('topic', 'Não especificado')
                
                prompt = f"""
                Gere 3-5 ideias inovadoras relacionadas ao tópico "{topic}" para o setor de {sector}.
                
                CONTEXTO:
                Tópico: {topic}
                Setor: {sector}
                Insights principais: {', '.join(synthesis.get('key_insights', ['Não especificado']))}
                Aplicações setoriais: {', '.join(synthesis.get('sector_applications', ['Não especificado']))}
                Tendências de mercado: {', '.join(synthesis.get('market_trends', ['Não especificado']))}
                Oportunidades de inovação: {', '.join(synthesis.get('innovation_opportunities', ['Não especificado']))}
                
                TÉCNICA DE INOVAÇÃO A UTILIZAR:
                {technique['name']}: {technique['description']}
                
                Para cada ideia, forneça:
                1. title: Título da ideia (curto e impactante)
                2. description: Descrição detalhada da solução
                3. benefits: Principais benefícios
                4. technical_feasibility: Avaliação da viabilidade técnica (1-10)
                5. potential_impact: Avaliação do impacto potencial (1-10)
                6. risks: Principais riscos ou desafios
                7. implementation_steps: Passos iniciais para implementação
                
                Forneça as ideias em formato JSON como uma lista de objetos.
                """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em inovação com experiência em gerar ideias disruptivas para diversos setores."},
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
            
            ideas = json.loads(json_str)
            
            # Add innovation technique used
            for idea in ideas:
                idea['innovation_technique'] = technique['name']
            
            return ideas
            
        except Exception as e:
            print(f"Error generating ideas with OpenAI: {e}")
            # Fall back to rule-based approach
            return self._generate_with_rules(synthesis)
    
    def _generate_with_rules(self, synthesis):
        """
        Generate ideas using rule-based approach (fallback).
        """
        # Extract relevant information
        sector = synthesis.get('context_data', {}).get('sector', 'Não especificado')
        
        # Select a random innovation technique
        technique = random.choice(self.innovation_techniques)
        
        # Generate ideas based on synthesis content
        ideas = []
        
        if 'potential_solutions' in synthesis:
            # Business pain flow
            pain_points = synthesis.get('context_data', {}).get('pain_points', ['Não especificado'])
            
            # Generate 3 ideas
            ideas = [
                {
                    'title': f"Plataforma de {synthesis.get('key_insights', ['inovação'])[0] if synthesis.get('key_insights') else 'inovação'} para {sector}",
                    'description': f"Uma plataforma que resolve {pain_points[0] if pain_points else 'problemas do setor'} utilizando tecnologias modernas e abordagens inovadoras.",
                    'benefits': "Redução de custos, aumento de eficiência, melhor experiência do usuário",
                    'technical_feasibility': random.randint(6, 9),
                    'potential_impact': random.randint(7, 10),
                    'risks': "Adoção pelo mercado, integração com sistemas legados, regulamentações",
                    'implementation_steps': "Prototipagem, validação com usuários, desenvolvimento MVP",
                    'innovation_technique': technique['name']
                },
                {
                    'title': f"Sistema de automação para {sector}",
                    'description': f"Um sistema que automatiza processos relacionados a {pain_points[0] if pain_points else 'operações do setor'}, reduzindo erros e aumentando a produtividade.",
                    'benefits': "Automação de tarefas repetitivas, redução de erros humanos, escalabilidade",
                    'technical_feasibility': random.randint(5, 8),
                    'potential_impact': random.randint(6, 9),
                    'risks': "Resistência à mudança, complexidade técnica, custo inicial",
                    'implementation_steps': "Mapeamento de processos, desenvolvimento de POC, implementação gradual",
                    'innovation_technique': technique['name']
                },
                {
                    'title': f"App móvel para {sector}",
                    'description': f"Um aplicativo móvel que permite aos usuários resolver {pain_points[0] if pain_points else 'problemas comuns'} de forma rápida e intuitiva.",
                    'benefits': "Mobilidade, facilidade de uso, disponibilidade 24/7",
                    'technical_feasibility': random.randint(7, 10),
                    'potential_impact': random.randint(6, 9),
                    'risks': "Concorrência, segurança de dados, experiência do usuário",
                    'implementation_steps': "Design de UX/UI, desenvolvimento ágil, testes com usuários",
                    'innovation_technique': technique['name']
                }
            ]
        else:
            # Topic exploration flow
            topic = synthesis.get('context_data', {}).get('topic', 'Não especificado')
            
            # Generate 3 ideas
            ideas = [
                {
                    'title': f"{topic} como serviço para {sector}",
                    'description': f"Uma plataforma que oferece {topic} como serviço para empresas do setor de {sector}, permitindo adoção rápida e sem grandes investimentos iniciais.",
                    'benefits': "Modelo de negócio baseado em assinatura, rápida implementação, escalabilidade",
                    'technical_feasibility': random.randint(6, 9),
                    'potential_impact': random.randint(7, 10),
                    'risks': "Segurança de dados, dependência de fornecedor, customização limitada",
                    'implementation_steps': "Desenvolvimento da plataforma, programa piloto, expansão gradual",
                    'innovation_technique': technique['name']
                },
                {
                    'title': f"Marketplace de {topic} para {sector}",
                    'description': f"Um marketplace que conecta provedores de soluções de {topic} com empresas do setor de {sector}, criando um ecossistema de inovação.",
                    'benefits': "Acesso a múltiplas soluções, competição saudável, inovação contínua",
                    'technical_feasibility': random.randint(5, 8),
                    'potential_impact': random.randint(6, 9),
                    'risks': "Atrair fornecedores de qualidade, garantir padrões, monetização",
                    'implementation_steps': "Desenvolvimento da plataforma, onboarding de parceiros, lançamento MVP",
                    'innovation_technique': technique['name']
                },
                {
                    'title': f"{topic} integrado com IA para {sector}",
                    'description': f"Uma solução que combina {topic} com inteligência artificial para criar novas possibilidades no setor de {sector}.",
                    'benefits': "Automação inteligente, insights preditivos, personalização",
                    'technical_feasibility': random.randint(4, 7),
                    'potential_impact': random.randint(8, 10),
                    'risks': "Complexidade técnica, qualidade dos dados, explicabilidade",
                    'implementation_steps': "Pesquisa e desenvolvimento, prototipagem, testes com dados reais",
                    'innovation_technique': technique['name']
                }
            ]
        
        return ideas
    
    def _load_innovation_techniques(self):
        """
        Load innovation techniques.
        """
        return [
            {
                'name': 'SCAMPER',
                'description': 'Técnica que sugere diferentes formas de modificar um produto ou serviço existente: Substituir, Combinar, Adaptar, Modificar, Propor outros usos, Eliminar, Rearranjar.'
            },
            {
                'name': 'Design Thinking',
                'description': 'Abordagem centrada no usuário que envolve empatia, definição do problema, ideação, prototipagem e testes.'
            },
            {
                'name': 'Blue Ocean Strategy',
                'description': 'Estratégia que busca criar novos mercados (oceanos azuis) em vez de competir em mercados existentes e saturados (oceanos vermelhos).'
            },
            {
                'name': 'Jobs to be Done',
                'description': 'Foco no "trabalho" que o cliente está tentando realizar, não nas características do produto ou serviço.'
            },
            {
                'name': 'Analogias e Metáforas',
                'description': 'Uso de analogias de outros setores ou da natureza para inspirar soluções inovadoras.'
            },
            {
                'name': 'Pensamento Lateral',
                'description': 'Abordagem de resolução de problemas que busca olhar para o problema de diferentes ângulos e perspectivas não convencionais.'
            },
            {
                'name': 'Brainstorming Reverso',
                'description': 'Técnica que começa identificando todas as maneiras de fazer algo falhar, para depois reverter essas ideias em soluções.'
            },
            {
                'name': 'Biomimética',
                'description': 'Inspiração em soluções encontradas na natureza para resolver problemas humanos.'
            }
        ]
