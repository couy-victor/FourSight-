import os
import requests
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from datetime import datetime
import logging
import time
from typing import List, Dict, Any, Optional, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API_UTILS")

# Load environment variables
load_dotenv()

def get_serper_api_key():
    """Get Serper API key from environment variables."""
    return os.getenv("SERPER_API_KEY")

def get_groq_api_key():
    """Get Groq API key from environment variables."""
    return os.getenv("GROQ_API_KEY", "")

def get_google_api_key():
    """Get Google API key from environment variables."""
    return os.getenv("GOOGLE_API_KEY", "")

def search_web(query, num_results=10):
    """
    Search the web using Serper API with improved error handling and retries.

    Args:
        query (str): Search query
        num_results (int): Number of results to return

    Returns:
        list: List of search result dictionaries
    """
    api_key = get_serper_api_key()

    if not api_key:
        logger.warning("Serper API key not found. Please set the SERPER_API_KEY environment variable.")
        return []

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    # Adicionar restrição de data para resultados recentes (2024-2025)
    date_restricted_query = f"{query} after:2024-01-01 before:2025-12-31"

    payload = {
        'q': date_restricted_query,
        'num': num_results,
        'timeRange': 'last12m'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=payload,
                timeout=15  # Increased timeout
            )

            if response.status_code == 200:
                search_results = response.json()
                formatted_results = []

                if 'organic' in search_results:
                    for result in search_results['organic']:
                        formatted_results.append({
                            'title': result.get('title', 'No Title'),
                            'url': result.get('link', ''),
                            'snippet': result.get('snippet', ''),
                            'source': result.get('source', 'Unknown')
                        })

                logger.info(f"Serper search returned {len(formatted_results)} results")
                return formatted_results
            
            elif response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Error searching with Serper: {response.status_code} - {response.text}")
                return []

        except requests.exceptions.Timeout:
            logger.warning(f"Serper API timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
        except Exception as e:
            logger.error(f"Error in search_web: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue

    logger.error("All Serper API attempts failed")
    return []

def call_ai_model(prompt, system_message="You are a helpful assistant.", max_tokens=1000, model_provider="groq"):
    """
    Generic function to call AI models from different providers with improved error handling.

    Args:
        prompt (str): User prompt
        system_message (str): System message to set the context
        max_tokens (int): Maximum tokens in the response
        model_provider (str): Provider to use ("groq" or "google")

    Returns:
        str: AI model response text
    """
    if model_provider == "groq":
        return call_groq_api(prompt, system_message, max_tokens)
    elif model_provider == "google":
        return call_google_api(prompt, system_message, max_tokens)
    else:
        return f"Unsupported model provider: {model_provider}"

def call_groq_api(prompt, system_message="You are a helpful assistant.", max_tokens=1000):
    """
    Call Groq API with Llama 4 model with improved error handling and retries.

    Args:
        prompt (str): User prompt
        system_message (str): System message to set the context
        max_tokens (int): Maximum tokens in the response

    Returns:
        str: Groq API response text
    """
    api_key = get_groq_api_key()

    if not api_key:
        logger.warning("Groq API key not found. Using default response.")
        return "Groq API key não encontrada. Por favor, configure a variável GROQ_API_KEY."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Verificar tamanho do prompt
    total_input = len(prompt) + len(system_message)
    if total_input > 30000:  # Limitar para evitar erros de token
        logger.warning(f"Prompt muito longo ({total_input} chars), truncando...")
        prompt = prompt[:25000] + "..."

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": min(max_tokens, 4000),  # Limitar tokens
        "temperature": 0.7,
        "top_p": 0.9
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30  # Increased timeout
            )

            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"Groq API successful. Response length: {len(content)} chars")
                    return content
                else:
                    logger.error("Groq API response missing choices")
                    return "Erro: Resposta da API Groq inválida"
            
            elif response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Groq API rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                continue
            
            elif response.status_code == 400:
                logger.error(f"Groq API bad request: {response.text}")
                return "Erro: Requisição inválida para a API Groq"
            
            else:
                logger.error(f"Error calling Groq API: {response.status_code} - {response.text}")
                return f"Erro na API Groq: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.warning(f"Groq API timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
        except Exception as e:
            logger.error(f"Error in call_groq_api: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

    return "Erro: Todas as tentativas de chamada da API Groq falharam"

def call_google_api(prompt, system_message="You are a helpful assistant.", max_tokens=1000):
    """
    Call Google Gemini API with improved error handling.

    Args:
        prompt (str): User prompt
        system_message (str): System message to set the context
        max_tokens (int): Maximum tokens in the response

    Returns:
        str: Google API response text
    """
    api_key = get_google_api_key()

    if not api_key:
        logger.warning("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
        return "Google API key não encontrada. Por favor, configure a variável GOOGLE_API_KEY."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    # Combinar system message e prompt
    combined_prompt = f"{system_message}\n\n{prompt}"
    
    # Verificar tamanho do prompt
    if len(combined_prompt) > 30000:
        logger.warning(f"Prompt muito longo para Google API ({len(combined_prompt)} chars), truncando...")
        combined_prompt = combined_prompt[:25000] + "..."

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": combined_prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": min(max_tokens, 2048),
            "temperature": 0.7,
            "topP": 0.9
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                response_json = response.json()
                
                if "candidates" in response_json and len(response_json["candidates"]) > 0:
                    candidate = response_json["candidates"][0]
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            content = parts[0]["text"].strip()
                            logger.info(f"Google API successful. Response length: {len(content)} chars")
                            return content

                    # Check for safety filtering
                    if "finishReason" in candidate and candidate["finishReason"] == "SAFETY":
                        logger.warning("Google API response was filtered for safety")
                        return "Conteúdo filtrado por questões de segurança. Tente reformular sua pergunta."

                logger.error("Google API response structure unexpected")
                return "Erro: Resposta da API Google inválida"
            
            elif response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt
                logger.warning(f"Google API rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                continue
            
            else:
                logger.error(f"Error calling Google API: {response.status_code} - {response.text}")
                return f"Erro na API Google: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.warning(f"Google API timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
        except Exception as e:
            logger.error(f"Error in call_google_api: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

    return "Erro: Todas as tentativas de chamada da API Google falharam"

def translate_to_english_smart(text: str, context: str = "") -> str:
    """
    Traduz texto do português para inglês de forma inteligente.
    
    Args:
        text: Texto para traduzir
        context: Contexto adicional
        
    Returns:
        Texto traduzido para inglês
    """
    # Se o texto já parece estar em inglês, retorna como está
    english_indicators = ['the', 'and', 'of', 'to', 'in', 'for', 'on', 'with', 'at', 'by']
    text_words = text.lower().split()
    english_count = sum(1 for word in english_indicators if word in text_words)
    
    if english_count >= 3 or len(text_words) <= 2:
        logger.info(f"Texto já parece estar em inglês: {text}")
        return text

    # Dicionário expandido de traduções
    translations = {
        # Frases completas comuns
        "inteligência artificial na saúde": "artificial intelligence in healthcare",
        "inteligência artificial saúde": "artificial intelligence healthcare",
        "blockchain na saúde": "blockchain in healthcare",
        "blockchain saúde": "blockchain healthcare",
        "machine learning saúde": "machine learning healthcare",
        "deep learning saúde": "deep learning healthcare",
        
        # Termos compostos
        "inteligência artificial": "artificial intelligence",
        "inteligencia artificial": "artificial intelligence",
        "aprendizado de máquina": "machine learning",
        "aprendizagem profunda": "deep learning",
        "redes neurais": "neural networks",
        "processamento de linguagem natural": "natural language processing",
        "visão computacional": "computer vision",
        "ciência de dados": "data science",
        "big data": "big data",
        "internet das coisas": "internet of things",
        "computação em nuvem": "cloud computing",
        "realidade virtual": "virtual reality",
        "realidade aumentada": "augmented reality",
        "automação robótica": "robotic automation",
        "carro autônomo": "autonomous vehicle",
        "casa inteligente": "smart home",
        "cidade inteligente": "smart city",
        
        # Saúde e medicina
        "cuidados de saúde": "healthcare",
        "telemedicina": "telemedicine",
        "saúde digital": "digital health",
        "prontuário eletrônico": "electronic health record",
        "diagnóstico por imagem": "medical imaging",
        "medicina personalizada": "personalized medicine",
        "medicina de precisão": "precision medicine",
        "biotecnologia": "biotechnology",
        "farmácia": "pharmacy",
        "hospitalar": "hospital",
        "clínico": "clinical",
        "terapêutico": "therapeutic",
        "preventivo": "preventive",
        "diagnóstico": "diagnosis",
        "tratamento": "treatment",
        "paciente": "patient",
        "médico": "medical",
        "enfermagem": "nursing",
        "cirurgia": "surgery",
        "radiologia": "radiology",
        "cardiologia": "cardiology",
        "oncologia": "oncology",
        "neurologia": "neurology",
        "psiquiatria": "psychiatry",
        "dermatologia": "dermatology",
        "pediatria": "pediatrics",
        "ginecologia": "gynecology",
        "urologia": "urology",
        "oftalmologia": "ophthalmology",
        "otorrinolaringologia": "otolaryngology",
        
        # Blockchain e cripto
        "moeda digital": "digital currency",
        "criptomoeda": "cryptocurrency",
        "bitcoin": "bitcoin",
        "ethereum": "ethereum",
        "contrato inteligente": "smart contract",
        "carteira digital": "digital wallet",
        "mineração": "mining",
        "descentralizado": "decentralized",
        "distribuído": "distributed",
        "consensus": "consensus",
        "prova de trabalho": "proof of work",
        "prova de participação": "proof of stake",
        
        # Negócios e finanças
        "fintech": "fintech",
        "insurtech": "insurtech",
        "regtech": "regtech",
        "proptech": "proptech",
        "edtech": "edtech",
        "healthtech": "healthtech",
        "legaltech": "legaltech",
        "agtech": "agtech",
        "foodtech": "foodtech",
        "retailtech": "retailtech",
        "banco digital": "digital bank",
        "pagamento digital": "digital payment",
        "cartão de crédito": "credit card",
        "empréstimo": "loan",
        "investimento": "investment",
        "startup": "startup",
        "unicórnio": "unicorn",
        "venture capital": "venture capital",
        "private equity": "private equity",
        "ipo": "ipo",
        "merger": "merger",
        "aquisição": "acquisition",
        
        # Palavras individuais
        "saúde": "health",
        "saude": "health",
        "tecnologia": "technology",
        "inovação": "innovation",
        "inovacao": "innovation",
        "empresa": "company",
        "negócio": "business",
        "negocio": "business",
        "mercado": "market",
        "produto": "product",
        "serviço": "service",
        "servico": "service",
        "cliente": "customer",
        "usuário": "user",
        "usuario": "user",
        "plataforma": "platform",
        "aplicativo": "application",
        "aplicação": "application",
        "aplicacao": "application",
        "sistema": "system",
        "solução": "solution",
        "solucao": "solution",
        "ferramenta": "tool",
        "desenvolvimento": "development",
        "pesquisa": "research",
        "análise": "analysis",
        "analise": "analysis",
        "dados": "data",
        "informação": "information",
        "informacao": "information",
        "segurança": "security",
        "seguranca": "security",
        "privacidade": "privacy",
        "eficiência": "efficiency",
        "eficiencia": "efficiency",
        "produtividade": "productivity",
        "automação": "automation",
        "automacao": "automation",
        "otimização": "optimization",
        "otimizacao": "optimization",
        "personalização": "personalization",
        "personalizacao": "personalization",
        "integração": "integration",
        "integracao": "integration",
        "colaboração": "collaboration",
        "colaboracao": "collaboration",
        "comunicação": "communication",
        "comunicacao": "communication",
        "educação": "education",
        "educacao": "education",
        "entretenimento": "entertainment",
        "esporte": "sports",
        "música": "music",
        "musica": "music",
        "vídeo": "video",
        "video": "video",
        "foto": "photo",
        "imagem": "image",
        "design": "design",
        "marketing": "marketing",
        "vendas": "sales",
        "compras": "shopping",
        "comércio": "commerce",
        "comercio": "commerce",
        "logística": "logistics",
        "logistica": "logistics",
        "transporte": "transportation",
        "energia": "energy",
        "sustentabilidade": "sustainability",
        "meio ambiente": "environment",
        "clima": "climate",
        "agricultura": "agriculture",
        "alimentação": "food",
        "alimentacao": "food",
        "turismo": "tourism",
        "viagem": "travel",
        "hotel": "hotel",
        "restaurante": "restaurant",
        "varejo": "retail",
        "moda": "fashion",
        "beleza": "beauty",
        "fitness": "fitness",
        "exercício": "exercise",
        "exercicio": "exercise",
        "nutrição": "nutrition",
        "nutricao": "nutrition",
        "bem-estar": "wellness",
        "qualidade de vida": "quality of life",
        
        # Preposições e artigos
        "na": "in",
        "no": "in",
        "da": "of",
        "do": "of",
        "de": "of",
        "para": "for",
        "com": "with",
        "em": "in",
        "ao": "to",
        "aos": "to",
        "as": "the",
        "os": "the",
        "um": "a",
        "uma": "a",
        "e": "and",
        "ou": "or",
        "que": "that",
        "como": "how",
        "quando": "when",
        "onde": "where",
        "por que": "why",
        "porque": "because",
        "se": "if",
        "mas": "but",
        "então": "then",
        "entao": "then",
        "também": "also",
        "tambem": "also",
        "muito": "very",
        "mais": "more",
        "menos": "less",
        "melhor": "better",
        "pior": "worse",
        "maior": "bigger",
        "menor": "smaller",
        "novo": "new",
        "antigo": "old",
        "primeiro": "first",
        "último": "last",
        "ultimo": "last"
    }

    # Aplicar traduções
    translated_text = text.lower()
    
    # Primeiro, aplicar traduções de frases completas (mais específicas)
    for pt_phrase, en_phrase in translations.items():
        if " " in pt_phrase and pt_phrase in translated_text:
            translated_text = translated_text.replace(pt_phrase, en_phrase)
            logger.info(f"Traduzido frase: '{pt_phrase}' -> '{en_phrase}'")

    # Depois, aplicar traduções de palavras individuais
    words = translated_text.split()
    translated_words = []
    
    for word in words:
        # Remover pontuação para verificação
        clean_word = ''.join(c for c in word if c.isalnum())
        if clean_word in translations:
            # Manter pontuação original
            punctuation = ''.join(c for c in word if not c.isalnum())
            translated_words.append(translations[clean_word] + punctuation)
        else:
            translated_words.append(word)
    
    final_translation = ' '.join(translated_words)
    
    # Capitalizar primeira letra
    if final_translation:
        final_translation = final_translation[0].upper() + final_translation[1:]
    
    if final_translation != text:
        logger.info(f"Tradução completa: '{text}' -> '{final_translation}'")
    
    return final_translation

def search_arxiv(query, max_results=10, sort_by="relevance", sort_order="descending", context=""):
    """
    Search arXiv for academic papers using the arXiv API with improved translation and error handling.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        sort_by (str): Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate'
        sort_order (str): Sort order 'ascending' or 'descending'
        context (str): Additional context to improve search relevance

    Returns:
        list: List of paper dictionaries with title, authors, summary, etc.
    """
    # Traduzir a consulta para inglês usando nossa função melhorada
    english_query = translate_to_english_smart(query, context)
    logger.info(f"ArXiv search - Original: '{query}' -> Translated: '{english_query}'")

    base_url = "http://export.arxiv.org/api/query"

    # Limitar resultados
    if max_results > 100:
        max_results = 100

    # Obter ano atual para filtragem por data
    current_year = datetime.now().year

    # Construir consulta melhorada
    # Adicionar restrição de data para artigos recentes (últimos 3 anos)
    date_constraint = f" AND submittedDate:[{current_year-3} TO {current_year}]"

    # Estratégias de consulta baseadas no conteúdo
    query_lower = english_query.lower()
    
    if ("artificial intelligence" in query_lower or "ai " in query_lower.split()) and any(term in query_lower for term in ["health", "healthcare", "medical", "medicine", "clinical"]):
        # Consulta específica para IA na saúde
        formatted_query = f'((ti:"artificial intelligence" AND (ti:health OR ti:healthcare OR ti:medical OR ti:medicine OR ti:clinical)) OR (abs:"artificial intelligence" AND (abs:health OR abs:healthcare OR abs:medical OR abs:medicine OR abs:clinical) AND (abs:novel OR abs:new OR abs:recent OR abs:advance))){date_constraint}'
        logger.info("Usando consulta específica para IA na saúde")
    
    elif "blockchain" in query_lower and any(term in query_lower for term in ["health", "healthcare", "medical"]):
        # Consulta específica para blockchain na saúde
        formatted_query = f'((ti:blockchain AND (ti:health OR ti:healthcare OR ti:medical)) OR (abs:blockchain AND (abs:health OR abs:healthcare OR abs:medical) AND (abs:novel OR abs:new OR abs:recent)))){date_constraint}'
        logger.info("Usando consulta específica para blockchain na saúde")
    
    else:
        # Consulta genérica melhorada
        main_terms = [term for term in english_query.split() if len(term) > 3][:3]  # Pegar até 3 termos principais
        
        if main_terms:
            title_query = " AND ".join([f'ti:"{term}"' for term in main_terms])
            abstract_query = " AND ".join([f'abs:"{term}"' for term in main_terms])
            formatted_query = f'(({title_query}) OR ({abstract_query})){date_constraint}'
        else:
            # Fallback para consulta simples
            formatted_query = f'(ti:"{english_query}" OR abs:"{english_query}"){date_constraint}'
        
        logger.info("Usando consulta genérica")

    logger.info(f"ArXiv formatted query: {formatted_query}")

    # Parâmetros da consulta
    params = {
        'search_query': formatted_query,
        'start': 0,
        'max_results': max_results
    }

    if sort_by in ['relevance', 'lastUpdatedDate', 'submittedDate']:
        params['sortBy'] = sort_by
    if sort_order in ['ascending', 'descending']:
        params['sortOrder'] = sort_order

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=20)
            
            if response.status_code == 200:
                if not response.text:
                    logger.warning("ArXiv API returned empty response")
                    return []

                # Parse XML response
                root = ET.fromstring(response.text)

                # Namespaces
                namespaces = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
                    'arxiv': 'http://arxiv.org/schemas/atom'
                }

                # Check total results
                total_results_elem = root.find('.//opensearch:totalResults', namespaces)
                if total_results_elem is not None:
                    total_results = int(total_results_elem.text)
                    logger.info(f"ArXiv total results available: {total_results}")
                    if total_results == 0:
                        logger.info("No results found in arXiv")
                        return []

                # Get entries
                entries = root.findall('.//atom:entry', namespaces)

                # Check for error in first entry
                if entries and entries[0].find('.//atom:title', namespaces) is not None:
                    first_title = entries[0].find('.//atom:title', namespaces).text
                    if first_title == "Error":
                        error_summary = entries[0].find('.//atom:summary', namespaces)
                        if error_summary is not None:
                            logger.error(f"ArXiv API Error: {error_summary.text}")
                        return []

                if not entries:
                    logger.warning("No entries found in ArXiv response")
                    return []

                logger.info(f"Found {len(entries)} entries in ArXiv response")

                # Process papers
                papers = []
                for entry in entries:
                    try:
                        paper = process_arxiv_entry(entry, namespaces)
                        if paper:
                            papers.append(paper)
                    except Exception as entry_error:
                        logger.error(f"Error processing ArXiv entry: {entry_error}")
                        continue

                logger.info(f"Successfully processed {len(papers)} ArXiv papers")
                return papers
            
            else:
                logger.error(f"ArXiv API error: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return []

        except requests.exceptions.Timeout:
            logger.warning(f"ArXiv API timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
        except ET.ParseError as xml_error:
            logger.error(f"XML parsing error in ArXiv response: {xml_error}")
            return []
        except Exception as e:
            logger.error(f"Error in search_arxiv: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

    logger.error("All ArXiv API attempts failed")
    return []

def process_arxiv_entry(entry, namespaces):
    """
    Process a single ArXiv entry from XML.
    
    Args:
        entry: XML entry element
        namespaces: XML namespaces dict
        
    Returns:
        dict: Processed paper information
    """
    try:
        # Extract basic information
        title_elem = entry.find('.//atom:title', namespaces)
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No Title"

        # Get arXiv ID
        id_elem = entry.find('.//atom:id', namespaces)
        arxiv_id = "Unknown"
        if id_elem is not None and id_elem.text:
            id_parts = id_elem.text.split('/')
            if len(id_parts) > 0:
                arxiv_id = id_parts[-1]

        # Get summary
        summary_elem = entry.find('.//atom:summary', namespaces)
        summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else "No Summary"

        # Get published date
        published_elem = entry.find('.//atom:published', namespaces)
        published_date = "Unknown"
        if published_elem is not None and published_elem.text:
            try:
                date_str = published_elem.text
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    published_date = dt.strftime('%Y-%m-%d')
                else:
                    published_date = date_str.split('T')[0]
            except Exception:
                published_date = published_elem.text

        # Extract authors
        authors = []
        for author_elem in entry.findall('.//atom:author', namespaces):
            name_elem = author_elem.find('.//atom:name', namespaces)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text.strip())

        if not authors:
            authors = ["Unknown"]

        # Extract links
        links = entry.findall('.//atom:link', namespaces)
        abstract_url = ""
        pdf_url = ""

        for link in links:
            rel = link.get('rel', '')
            href = link.get('href', '')
            title_attr = link.get('title', '')

            if rel == 'alternate' and href:
                abstract_url = href
            elif title_attr == 'pdf' and href:
                pdf_url = href

        # Use appropriate URL
        url = pdf_url if pdf_url else abstract_url
        if not url:
            url = f"https://arxiv.org/abs/{arxiv_id}"

        # Extract categories
        categories = []
        for category in entry.findall('.//atom:category', namespaces):
            term = category.get('term')
            if term:
                categories.append(term)

        if not categories:
            categories = ["Uncategorized"]

        # Create paper object
        paper = {
            'title': title,
            'arxiv_id': arxiv_id,
            'authors': authors,
            'summary': summary,
            'published_date': published_date,
            'url': url,
            'abstract_url': abstract_url,
            'pdf_url': pdf_url,
            'categories': categories,
            'source': 'arXiv'
        }

        return paper

    except Exception as e:
        logger.error(f"Error processing arXiv entry: {e}")
        return None