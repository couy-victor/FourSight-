import os
import json
from dotenv import load_dotenv
from utils.api_utils import call_ai_model, call_groq_api, call_google_api

# Load environment variables
load_dotenv()

class ContextualAgent:
    """
    Agent responsible for understanding the specific context (sector, company, problem)
    and adapting information to that context.
    """

    def __init__(self):
        """Initialize the ContextualAgent with API keys and configurations."""
        # Load API keys from environment variables
        self.groq_api_key = os.getenv("GROQ_API_KEY", "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")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")

        # Load sector-specific knowledge from file if it exists, otherwise use default
        try:
            with open("data/sector_knowledge.json", "r", encoding="utf-8") as f:
                self.sector_knowledge = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.sector_knowledge = self._load_sector_knowledge()

        # Set preferred LLM
        self.use_groq = True  # Default to Groq API with Llama 4
        self.use_multiple_apis = True  # Set to True to use multiple APIs and combine results

    def process_business_pain(self, pain_description, sector):
        """
        Process a business pain description and extract relevant context.

        Args:
            pain_description (str): Description of the business pain
            sector (str): Business sector

        Returns:
            dict: Contextual data including keywords, pain points, etc.
        """
        # Use multiple APIs if enabled
        if self.use_multiple_apis:
            return self._process_with_multiple_apis(pain_description, sector)
        # Use Groq if enabled and available
        elif self.use_groq and self.groq_api_key:
            return self._process_with_groq(pain_description, sector)
        # Use Google API if available
        elif self.google_api_key:
            return self._process_with_google(pain_description, sector)
        else:
            # Use rule-based approach as fallback
            return self._process_with_rules(pain_description, sector)

    def adapt_to_sector(self, topic, sector):
        """
        Adapt a general topic to a specific business sector.

        Args:
            topic (str): General topic
            sector (str): Business sector

        Returns:
            dict: Contextual data adapted to the sector
        """
        # Get sector-specific knowledge
        sector_info = self.sector_knowledge.get(sector, {})

        # Use multiple APIs if enabled
        if self.use_multiple_apis:
            return self._adapt_with_multiple_apis(topic, sector, sector_info)
        # Use Groq if enabled and available
        elif self.use_groq and self.groq_api_key:
            return self._adapt_with_groq(topic, sector, sector_info)
        # Use Google API if available
        elif self.google_api_key:
            return self._adapt_with_google(topic, sector, sector_info)
        else:
            # Use rule-based approach as fallback
            return {
                'topic': topic,
                'sector': sector,
                'keywords': [topic, sector] + sector_info.get('keywords', []),
                'context': f"Explorando {topic} no contexto do setor de {sector}",
                'sector_specific_terms': sector_info.get('terms', []),
                'regulations': sector_info.get('regulations', []),
                'trends': sector_info.get('trends', [])
            }

    def _process_with_google(self, pain_description, sector):
        """
        Use Google Gemini API to process business pain and extract context.
        """
        try:
            # Get sector-specific knowledge
            sector_info = self.sector_knowledge.get(sector, {})

            # Create prompt with sector context
            prompt = f"""
            Analise a seguinte descrição de dor de negócio no setor de {sector}:

            "{pain_description}"

            Extraia e forneça as seguintes informações em formato JSON:
            1. keywords: Lista de 5-7 palavras-chave relevantes para pesquisa
            2. pain_points: Lista dos principais pontos de dor identificados
            3. context: Um parágrafo resumindo o contexto do problema
            4. stakeholders: Lista de stakeholders potencialmente afetados
            5. potential_solutions_areas: Áreas onde soluções poderiam ser desenvolvidas

            Considere o contexto específico do setor de {sector}, incluindo:
            - Termos específicos: {', '.join(sector_info.get('terms', ['N/A']))}
            - Regulações relevantes: {', '.join(sector_info.get('regulations', ['N/A']))}
            - Tendências atuais: {', '.join(sector_info.get('trends', ['N/A']))}

            Responda apenas com o JSON, sem texto adicional.
            """

            system_message = "Você é um especialista em análise de negócios com profundo conhecimento de diversos setores."

            # Call Google API
            content = call_google_api(prompt, system_message, 800)

            # Parse the JSON response
            # Extract JSON part if there's surrounding text
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            result = json.loads(json_str)

            # Add sector information
            result['sector'] = sector

            return result

        except Exception as e:
            print(f"Error processing with Google: {e}")
            # Fall back to rule-based approach
            return self._process_with_rules(pain_description, sector)

    def _adapt_with_google(self, topic, sector, sector_info):
        """
        Use Google Gemini API to adapt a topic to a specific sector.
        """
        try:
            prompt = f"""
            Adapte o tópico "{topic}" para o contexto específico do setor de {sector}.

            Considere:
            - Termos específicos: {', '.join(sector_info.get('terms', ['N/A']))}
            - Regulações relevantes: {', '.join(sector_info.get('regulations', ['N/A']))}
            - Tendências atuais: {', '.join(sector_info.get('trends', ['N/A']))}

            Forneça as seguintes informações em formato JSON:
            1. keywords: Lista de 5-7 palavras-chave relevantes para pesquisa
            2. context: Um parágrafo explicando como {topic} se aplica ao setor de {sector}
            3. sector_specific_applications: Possíveis aplicações específicas para o setor
            4. challenges: Desafios específicos de implementação neste setor
            5. opportunities: Oportunidades únicas neste setor

            Responda apenas com o JSON, sem texto adicional.
            """

            system_message = "Você é um especialista em inovação com profundo conhecimento de diversos setores."

            # Call Google API
            content = call_google_api(prompt, system_message, 800)

            # Parse the JSON response
            # Extract JSON part if there's surrounding text
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            result = json.loads(json_str)

            # Add topic and sector information
            result['topic'] = topic
            result['sector'] = sector

            return result

        except Exception as e:
            print(f"Error adapting with Google: {e}")
            # Fall back to rule-based approach
            return {
                'topic': topic,
                'sector': sector,
                'keywords': [topic, sector] + sector_info.get('keywords', []),
                'context': f"Explorando {topic} no contexto do setor de {sector}",
                'sector_specific_terms': sector_info.get('terms', []),
                'regulations': sector_info.get('regulations', []),
                'trends': sector_info.get('trends', [])
            }

    def _process_with_groq(self, pain_description, sector):
        """
        Use Groq API with Llama 4 to process business pain and extract context.
        """
        try:
            # Get sector-specific knowledge
            sector_info = self.sector_knowledge.get(sector, {})

            # Create prompt with sector context
            prompt = f"""
            Analise a seguinte descrição de dor de negócio no setor de {sector}:

            "{pain_description}"

            Extraia e forneça as seguintes informações em formato JSON:
            1. keywords: Lista de 5-7 palavras-chave relevantes para pesquisa
            2. pain_points: Lista dos principais pontos de dor identificados
            3. context: Um parágrafo resumindo o contexto do problema
            4. stakeholders: Lista de stakeholders potencialmente afetados
            5. potential_solutions_areas: Áreas onde soluções poderiam ser desenvolvidas

            Considere o contexto específico do setor de {sector}, incluindo:
            - Termos específicos: {', '.join(sector_info.get('terms', ['N/A']))}
            - Regulações relevantes: {', '.join(sector_info.get('regulations', ['N/A']))}
            - Tendências atuais: {', '.join(sector_info.get('trends', ['N/A']))}

            Responda apenas com o JSON, sem texto adicional.
            """

            system_message = "Você é um especialista em análise de negócios com profundo conhecimento de diversos setores."

            # Call Groq API
            content = call_groq_api(prompt, system_message, 800)

            # Parse the JSON response
            # Extract JSON part if there's surrounding text
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            result = json.loads(json_str)

            # Add sector information
            result['sector'] = sector

            return result

        except Exception as e:
            print(f"Error processing with Groq: {e}")
            # Try OpenAI as fallback if available
            if self.openai_api_key:
                return self._process_with_openai(pain_description, sector)
            else:
                # Fall back to rule-based approach
                return self._process_with_rules(pain_description, sector)

    def _adapt_with_groq(self, topic, sector, sector_info):
        """
        Use Groq API with Llama 4 to adapt a topic to a specific sector.
        """
        try:
            prompt = f"""
            Adapte o tópico "{topic}" para o contexto específico do setor de {sector}.

            Considere:
            - Termos específicos: {', '.join(sector_info.get('terms', ['N/A']))}
            - Regulações relevantes: {', '.join(sector_info.get('regulations', ['N/A']))}
            - Tendências atuais: {', '.join(sector_info.get('trends', ['N/A']))}

            Forneça as seguintes informações em formato JSON:
            1. keywords: Lista de 5-7 palavras-chave relevantes para pesquisa
            2. context: Um parágrafo explicando como {topic} se aplica ao setor de {sector}
            3. sector_specific_applications: Possíveis aplicações específicas para o setor
            4. challenges: Desafios específicos de implementação neste setor
            5. opportunities: Oportunidades únicas neste setor

            Responda apenas com o JSON, sem texto adicional.
            """

            system_message = "Você é um especialista em inovação com profundo conhecimento de diversos setores."

            # Call Groq API
            content = call_groq_api(prompt, system_message, 800)

            # Parse the JSON response
            # Extract JSON part if there's surrounding text
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            result = json.loads(json_str)

            # Add topic and sector information
            result['topic'] = topic
            result['sector'] = sector

            return result

        except Exception as e:
            print(f"Error adapting with Groq: {e}")
            # Try OpenAI as fallback if available
            if self.openai_api_key:
                return self._adapt_with_openai(topic, sector, sector_info)
            else:
                # Fall back to rule-based approach
                return {
                    'topic': topic,
                    'sector': sector,
                    'keywords': [topic, sector] + sector_info.get('keywords', []),
                    'context': f"Explorando {topic} no contexto do setor de {sector}",
                    'sector_specific_terms': sector_info.get('terms', []),
                    'regulations': sector_info.get('regulations', []),
                    'trends': sector_info.get('trends', [])
                }

    def _process_with_rules(self, pain_description, sector):
        """
        Process business pain using rule-based approach (fallback).
        """
        # Extract keywords based on frequency and importance
        words = pain_description.lower().split()
        # Remove common words
        common_words = ['o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'e', 'que', 'para', 'com', 'em', 'por']
        keywords = [word for word in words if word not in common_words and len(word) > 3]

        # Get unique keywords
        unique_keywords = list(set(keywords))

        # Get sector-specific knowledge
        sector_info = self.sector_knowledge.get(sector, {})

        # Create context data
        return {
            'keywords': unique_keywords[:7] + sector_info.get('keywords', []),
            'pain_points': [pain_description],  # Simplified
            'context': f"Problema no setor de {sector}: {pain_description[:100]}...",
            'stakeholders': sector_info.get('stakeholders', ['Clientes', 'Funcionários', 'Gestores']),
            'potential_solutions_areas': ['Tecnologia', 'Processos', 'Pessoas'],
            'sector': sector,
            'sector_specific_terms': sector_info.get('terms', []),
            'regulations': sector_info.get('regulations', []),
            'trends': sector_info.get('trends', [])
        }

    def _process_with_multiple_apis(self, pain_description, sector):
        """
        Process business pain using multiple APIs and combine results.
        """
        try:
            # Get results from Groq
            groq_result = self._process_with_groq(pain_description, sector)

            # Try to get results from Google if available
            try:
                if self.google_api_key:
                    google_result = self._process_with_google(pain_description, sector)
                else:
                    google_result = None
            except Exception as e:
                print(f"Error with Google API: {e}")
                google_result = None

            # If we only have Groq results, return them
            if not google_result:
                return groq_result

            # Combine results
            combined_result = {
                'sector': sector,
                'keywords': list(set(groq_result.get('keywords', []) + google_result.get('keywords', []))),
                'pain_points': list(set(groq_result.get('pain_points', []) + google_result.get('pain_points', []))),
                'context': groq_result.get('context', '') + "\n\nAdditional context: " + google_result.get('context', ''),
                'stakeholders': list(set(groq_result.get('stakeholders', []) + google_result.get('stakeholders', []))),
                'potential_solutions_areas': list(set(groq_result.get('potential_solutions_areas', []) + google_result.get('potential_solutions_areas', []))),
                'source': 'multiple_apis'
            }

            # Limit keywords to a reasonable number
            if len(combined_result['keywords']) > 10:
                combined_result['keywords'] = combined_result['keywords'][:10]

            return combined_result

        except Exception as e:
            print(f"Error processing with multiple APIs: {e}")
            # Fall back to Groq only
            return self._process_with_groq(pain_description, sector)

    def _adapt_with_multiple_apis(self, topic, sector, sector_info):
        """
        Adapt topic to sector using multiple APIs and combine results.
        """
        try:
            # Get results from Groq
            groq_result = self._adapt_with_groq(topic, sector, sector_info)

            # Try to get results from Google if available
            try:
                if self.google_api_key:
                    google_result = self._adapt_with_google(topic, sector, sector_info)
                else:
                    google_result = None
            except Exception as e:
                print(f"Error with Google API: {e}")
                google_result = None

            # If we only have Groq results, return them
            if not google_result:
                return groq_result

            # Combine results
            combined_result = {
                'topic': topic,
                'sector': sector,
                'keywords': list(set(groq_result.get('keywords', []) + google_result.get('keywords', []))),
                'context': groq_result.get('context', '') + "\n\nAdditional context: " + google_result.get('context', ''),
                'sector_specific_applications': list(set(groq_result.get('sector_specific_applications', []) + google_result.get('sector_specific_applications', []))),
                'challenges': list(set(groq_result.get('challenges', []) + google_result.get('challenges', []))),
                'opportunities': list(set(groq_result.get('opportunities', []) + google_result.get('opportunities', []))),
                'source': 'multiple_apis'
            }

            # Limit keywords to a reasonable number
            if len(combined_result['keywords']) > 10:
                combined_result['keywords'] = combined_result['keywords'][:10]

            return combined_result

        except Exception as e:
            print(f"Error adapting with multiple APIs: {e}")
            # Fall back to Groq only
            return self._adapt_with_groq(topic, sector, sector_info)

    def _load_sector_knowledge(self):
        """
        Load sector-specific knowledge.
        This could be loaded from a database or file in a real implementation.
        """
        return {
            'Financeiro': {
                'keywords': ['banco', 'fintech', 'pagamento', 'crédito', 'investimento'],
                'terms': ['open banking', 'PIX', 'KYC', 'AML', 'compliance'],
                'regulations': ['Resolução BCB', 'LGPD', 'PCI DSS'],
                'trends': ['banking as a service', 'embedded finance', 'open finance'],
                'stakeholders': ['Bancos', 'Fintechs', 'Reguladores', 'Clientes', 'Investidores']
            },
            'Seguros': {
                'keywords': ['seguro', 'risco', 'sinistro', 'apólice', 'insurtech'],
                'terms': ['subscrição', 'resseguro', 'sinistralidade', 'prêmio'],
                'regulations': ['SUSEP', 'ANS', 'LGPD'],
                'trends': ['seguro paramétrico', 'microseguros', 'seguros on-demand'],
                'stakeholders': ['Seguradoras', 'Corretores', 'Reguladores', 'Segurados']
            },
            'Pagamentos': {
                'keywords': ['transação', 'adquirência', 'cartão', 'wallet', 'QR code'],
                'terms': ['split payment', 'chargeback', 'tokenização', 'NFC'],
                'regulations': ['PCI DSS', 'LGPD', 'Regulações BCB'],
                'trends': ['pagamentos invisíveis', 'buy now pay later', 'pagamentos instantâneos'],
                'stakeholders': ['Adquirentes', 'Bandeiras', 'Emissores', 'Comerciantes', 'Consumidores']
            },
            'Varejo': {
                'keywords': ['loja', 'e-commerce', 'omnichannel', 'marketplace', 'consumidor'],
                'terms': ['GMV', 'NPS', 'CAC', 'LTV', 'churn'],
                'regulations': ['CDC', 'LGPD', 'Procon'],
                'trends': ['live commerce', 'social commerce', 'retail media', 'quick commerce'],
                'stakeholders': ['Varejistas', 'Fornecedores', 'Consumidores', 'Marketplaces']
            },
            'Saúde': {
                'keywords': ['hospital', 'clínica', 'paciente', 'healthtech', 'telemedicina'],
                'terms': ['prontuário eletrônico', 'TISS', 'glosa', 'sinistralidade'],
                'regulations': ['ANS', 'CFM', 'LGPD', 'ANVISA'],
                'trends': ['telemedicina', 'saúde digital', 'wearables', 'medicina preventiva'],
                'stakeholders': ['Hospitais', 'Operadoras', 'Médicos', 'Pacientes', 'Reguladores']
            },
            'Outro': {
                'keywords': ['inovação', 'tecnologia', 'digital', 'transformação', 'experiência'],
                'terms': ['digitalização', 'automação', 'UX', 'analytics'],
                'regulations': ['LGPD', 'regulações setoriais'],
                'trends': ['IA', 'blockchain', 'IoT', 'computação em nuvem'],
                'stakeholders': ['Empresas', 'Clientes', 'Funcionários', 'Parceiros']
            }
        }
