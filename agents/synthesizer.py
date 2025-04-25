import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SynthesizerAgent:
    """
    Agent responsible for synthesizing information from multiple sources
    into a coherent format.
    """
    
    def __init__(self):
        """Initialize the SynthesizerAgent with API keys and configurations."""
        # Load API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Set OpenAI API key
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def synthesize(self, context_data, search_results):
        """
        Synthesize information from context data and search results.
        
        Args:
            context_data (dict): Contextual information about the business pain or topic
            search_results (list): List of articles and information from research
            
        Returns:
            dict: Synthesized information including patterns, insights, and connections
        """
        # If OpenAI API key is available, use it for synthesis
        if self.openai_api_key:
            return self._synthesize_with_openai(context_data, search_results)
        else:
            # Use rule-based approach as fallback
            return self._synthesize_with_rules(context_data, search_results)
    
    def _synthesize_with_openai(self, context_data, search_results):
        """
        Use OpenAI to synthesize information.
        """
        try:
            # Prepare context information
            sector = context_data.get('sector', 'Não especificado')
            
            # Prepare search results summary
            articles_summary = ""
            for i, article in enumerate(search_results[:5]):  # Limit to 5 articles to avoid token limits
                articles_summary += f"\nArtigo {i+1}: {article['title']}\n"
                articles_summary += f"Resumo: {article['summary']}\n"
                articles_summary += f"Fonte: {article['source']}\n"
            
            # Create prompt based on input type
            if 'pain_points' in context_data:
                # Business pain flow
                prompt = f"""
                Sintetize as informações abaixo sobre uma dor de negócio no setor de {sector} e os artigos relacionados.
                
                CONTEXTO DA DOR DE NEGÓCIO:
                Setor: {sector}
                Pontos de dor: {', '.join(context_data.get('pain_points', ['Não especificado']))}
                Contexto: {context_data.get('context', 'Não especificado')}
                Stakeholders: {', '.join(context_data.get('stakeholders', ['Não especificado']))}
                
                ARTIGOS RELACIONADOS:
                {articles_summary}
                
                Forneça uma síntese em formato JSON com os seguintes elementos:
                1. key_insights: Lista dos principais insights extraídos dos artigos
                2. patterns: Padrões identificados entre os artigos e a dor de negócio
                3. potential_solutions: Possíveis abordagens para solucionar a dor com base nos artigos
                4. innovation_opportunities: Oportunidades específicas de inovação
                5. market_trends: Tendências de mercado relevantes identificadas
                6. synthesis_summary: Um resumo geral conectando todos os pontos acima
                """
            else:
                # Topic exploration flow
                prompt = f"""
                Sintetize as informações abaixo sobre o tópico "{context_data.get('topic', 'Não especificado')}" no setor de {sector} e os artigos relacionados.
                
                CONTEXTO DO TÓPICO:
                Tópico: {context_data.get('topic', 'Não especificado')}
                Setor: {sector}
                Contexto: {context_data.get('context', 'Não especificado')}
                Aplicações específicas: {', '.join(context_data.get('sector_specific_applications', ['Não especificado']))}
                
                ARTIGOS RELACIONADOS:
                {articles_summary}
                
                Forneça uma síntese em formato JSON com os seguintes elementos:
                1. key_insights: Lista dos principais insights extraídos dos artigos
                2. patterns: Padrões identificados entre os artigos
                3. sector_applications: Aplicações específicas para o setor de {sector}
                4. innovation_opportunities: Oportunidades específicas de inovação
                5. market_trends: Tendências de mercado relevantes identificadas
                6. synthesis_summary: Um resumo geral conectando todos os pontos acima
                """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em síntese de informações e identificação de padrões para inovação."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
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
            
            result = json.loads(json_str)
            
            # Add original context data and search results
            result['context_data'] = context_data
            result['search_results'] = [
                {'title': article['title'], 'source': article['source']}
                for article in search_results
            ]
            
            return result
            
        except Exception as e:
            print(f"Error synthesizing with OpenAI: {e}")
            # Fall back to rule-based approach
            return self._synthesize_with_rules(context_data, search_results)
    
    def _synthesize_with_rules(self, context_data, search_results):
        """
        Synthesize information using rule-based approach (fallback).
        """
        # Extract sector
        sector = context_data.get('sector', 'Não especificado')
        
        # Extract key terms from search results
        all_terms = []
        for article in search_results:
            # Split summary into words
            words = article['summary'].lower().split()
            # Remove common words
            common_words = ['o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'e', 'que', 'para', 'com', 'em', 'por']
            terms = [word for word in words if word not in common_words and len(word) > 3]
            all_terms.extend(terms)
        
        # Count term frequency
        term_freq = {}
        for term in all_terms:
            if term in term_freq:
                term_freq[term] += 1
            else:
                term_freq[term] = 1
        
        # Get top terms
        top_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Create synthesis
        if 'pain_points' in context_data:
            # Business pain flow
            synthesis = {
                'key_insights': [f"Termo frequente: {term}" for term, _ in top_terms[:5]],
                'patterns': ["Padrão identificado com base na frequência de termos"],
                'potential_solutions': [
                    f"Solução baseada em {search_results[0]['title']}" if search_results else "Solução genérica",
                    f"Abordagem inspirada em {search_results[1]['title']}" if len(search_results) > 1 else "Abordagem alternativa"
                ],
                'innovation_opportunities': [
                    f"Oportunidade no setor de {sector} relacionada a {top_terms[0][0]}" if top_terms else "Oportunidade genérica"
                ],
                'market_trends': [
                    f"Tendência: {article['title']}" for article in search_results[:3]
                ],
                'synthesis_summary': f"Síntese de informações sobre dores no setor de {sector}, identificando padrões e possíveis soluções com base nos artigos pesquisados."
            }
        else:
            # Topic exploration flow
            topic = context_data.get('topic', 'Não especificado')
            synthesis = {
                'key_insights': [f"Termo frequente: {term}" for term, _ in top_terms[:5]],
                'patterns': ["Padrão identificado com base na frequência de termos"],
                'sector_applications': [
                    f"Aplicação de {topic} em {sector}",
                    f"Uso de {topic} para resolver problemas específicos de {sector}"
                ],
                'innovation_opportunities': [
                    f"Oportunidade no setor de {sector} relacionada a {top_terms[0][0]}" if top_terms else "Oportunidade genérica"
                ],
                'market_trends': [
                    f"Tendência: {article['title']}" for article in search_results[:3]
                ],
                'synthesis_summary': f"Síntese de informações sobre {topic} no setor de {sector}, identificando aplicações e oportunidades com base nos artigos pesquisados."
            }
        
        # Add original context data and search results
        synthesis['context_data'] = context_data
        synthesis['search_results'] = [
            {'title': article['title'], 'source': article['source']}
            for article in search_results
        ]
        
        return synthesis
