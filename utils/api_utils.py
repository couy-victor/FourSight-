import os
import requests
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from datetime import datetime

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
    Search the web using Serper API.

    Args:
        query (str): Search query
        num_results (int): Number of results to return

    Returns:
        list: List of search result dictionaries
    """
    api_key = get_serper_api_key()

    if not api_key:
        print("Serper API key not found. Please set the SERPER_API_KEY environment variable.")
        return []

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    # Adicionar restrição de data para resultados recentes (2024-2025)
    # Usar uma restrição mais específica para garantir resultados de 2024-2025
    date_restricted_query = f"{query} after:2024-01-01 before:2025-12-31"

    payload = {
        'q': date_restricted_query,
        'num': num_results,
        'timeRange': 'last12m'  # Adicionar restrição de tempo para os últimos 12 meses
    }

    try:
        response = requests.post(
            'https://google.serper.dev/search',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            search_results = response.json()

            # Process and format results
            formatted_results = []

            if 'organic' in search_results:
                for result in search_results['organic']:
                    formatted_results.append({
                        'title': result.get('title', 'No Title'),
                        'url': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'source': result.get('source', 'Unknown')
                    })

            return formatted_results
        else:
            print(f"Error searching with Serper: {response.status_code}")
            return []

    except Exception as e:
        print(f"Error in search_web: {e}")
        return []

def call_ai_model(prompt, system_message="You are a helpful assistant.", max_tokens=1000, model_provider="groq"):
    """
    Generic function to call AI models from different providers.

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
    Call Groq API with Llama 4 model.

    Args:
        prompt (str): User prompt
        system_message (str): System message to set the context
        max_tokens (int): Maximum tokens in the response

    Returns:
        str: Groq API response text
    """
    api_key = get_groq_api_key()

    if not api_key:
        print("Groq API key not found. Using default key.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",  # Usando o modelo Llama 4 correto
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"Error calling Groq API: {response.status_code}")
            print(response.text)
            return f"Error calling Groq API: {response.status_code}"

    except Exception as e:
        print(f"Error in call_groq_api: {e}")
        return f"Error calling Groq API: {str(e)}"

def call_google_api(prompt, system_message="You are a helpful assistant.", max_tokens=1000):
    """
    Call Google Gemini API.

    Args:
        prompt (str): User prompt
        system_message (str): System message to set the context
        max_tokens (int): Maximum tokens in the response

    Returns:
        str: Google API response text
    """
    api_key = get_google_api_key()

    if not api_key:
        print("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
        return "Google API key not found. Unable to process request."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": system_message + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            response_json = response.json()
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                if "content" in response_json["candidates"][0] and "parts" in response_json["candidates"][0]["content"]:
                    parts = response_json["candidates"][0]["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"].strip()

            # If we couldn't parse the response properly
            return "Erro ao processar resposta da API do Google."
        else:
            print(f"Error calling Google API: {response.status_code}")
            print(response.text)
            return f"Error calling Google API: {response.status_code}"

    except Exception as e:
        print(f"Error in call_google_api: {e}")
        return f"Error calling Google API: {str(e)}"

def search_arxiv(query, max_results=10, sort_by="relevance", sort_order="descending", context=""):
    """
    Search arXiv for academic papers using the arXiv API.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        sort_by (str): Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate'
        sort_order (str): Sort order 'ascending' or 'descending'
        context (str): Additional context to improve search relevance

    Returns:
        list: List of paper dictionaries with title, authors, summary, etc.
    """
    # Traduzir a consulta para inglês se estiver em outro idioma
    # Dicionário de traduções comuns para termos de IA e saúde
    translations = {
        "inteligência artificial": "artificial intelligence",
        "aprendizado de máquina": "machine learning",
        "aprendizagem profunda": "deep learning",
        "redes neurais": "neural networks",
        "saúde": "health",
        "medicina": "medicine",
        "diagnóstico": "diagnosis",
        "tratamento": "treatment",
        "paciente": "patient",
        "hospital": "hospital",
        "clínica": "clinic",
        "médico": "medical",
        "doença": "disease",
        "câncer": "cancer",
        "diabetes": "diabetes",
        "radiologia": "radiology",
        "imagem médica": "medical imaging",
        "prontuário eletrônico": "electronic health record",
        "telemedicina": "telemedicine",
        "na saúde": "in healthcare"
    }

    # Verificar se a consulta está em português e traduzi-la
    query_lower = query.lower()
    english_query = query

    # Verificar se a consulta contém palavras em português
    for pt_term, en_term in translations.items():
        if pt_term in query_lower:
            english_query = query_lower.replace(pt_term, en_term)
            print(f"Traduzindo consulta para inglês: '{query}' -> '{english_query}'")
            break

    # Se a consulta original era "Inteligência Artificial na Saúde", usar uma tradução específica
    if query_lower == "inteligência artificial na saúde":
        english_query = "artificial intelligence in healthcare"
        print(f"Traduzindo consulta para inglês: '{query}' -> '{english_query}'")

    # Usar a consulta em inglês para o arXiv
    query = english_query
    base_url = "http://export.arxiv.org/api/query"

    # Ensure max_results is within limits (arXiv API has a limit of 2000 per request)
    if max_results > 100:
        max_results = 100  # We'll limit to 100 to avoid overloading the API

    # Get current year for date filtering
    current_year = datetime.now().year

    # Extract key terms from query and context for better search
    key_terms = []

    # Add the original query
    key_terms.append(query)

    # If context is provided, extract key terms
    if context:
        # Traduzir o contexto para inglês também
        english_context = context
        context_lower = context.lower()
        for pt_term, en_term in translations.items():
            if pt_term in context_lower:
                english_context = context_lower.replace(pt_term, en_term)
                print(f"Traduzindo contexto para inglês")

        # Simple extraction of potential key terms from English context
        context_words = english_context.lower().split()
        # Look for important terms (nouns, technical terms, etc.)
        important_indicators = ["ai", "machine", "learning", "neural", "data", "algorithm",
                               "model", "system", "technology", "analysis", "research",
                               "health", "medical", "clinical", "patient", "treatment",
                               "business", "market", "industry", "innovation", "strategy"]

        for word in context_words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 3 and (clean_word in important_indicators or clean_word.istitle()):
                key_terms.append(clean_word)

    # Create a more targeted query
    enhanced_query = f"({query})"

    # Add date constraint for recent papers (last 2 years)
    date_constraint = f" AND submittedDate:[{current_year-1} TO {current_year}]"
    enhanced_query += date_constraint

    # Adicionar restrição para artigos em inglês
    enhanced_query += " AND language:en"

    # Format query for arXiv API
    if any(prefix in enhanced_query for prefix in ['ti:', 'au:', 'abs:', 'cat:', 'all:']):
        # Query already has field prefixes, use it as is but replace spaces with +
        formatted_query = enhanced_query.replace(' ', '+')
    else:
        # Para consultas em inglês, usar uma abordagem mais ampla
        # Extrair palavras-chave da consulta
        query_words = query.split()

        # Se a consulta for "artificial intelligence in healthcare" ou similar
        if "artificial intelligence" in query.lower() and ("healthcare" in query.lower() or "health" in query.lower()):
            # Usar uma consulta mais específica para IA na saúde, priorizando o título
            formatted_query = f'(ti:"artificial intelligence" AND (ti:health OR ti:healthcare OR ti:medical OR ti:medicine OR ti:clinical)) OR (abs:"artificial intelligence" AND (abs:health OR abs:healthcare OR abs:medical OR abs:medicine OR abs:clinical) AND (abs:innovation OR abs:novel OR abs:new OR abs:recent OR abs:advance)){date_constraint}'
        elif len(query_words) > 3:
            # Para consultas longas, dividir em termos e buscar em título ou resumo
            main_terms = [word for word in query_words if len(word) > 3 and word.lower() not in ["and", "or", "the", "in", "on", "at", "for", "with", "by"]]
            term_conditions = []

            for term in main_terms:
                term_conditions.append(f'ti:"{term}" OR abs:"{term}"')

            if term_conditions:
                formatted_query = f'({" AND ".join(term_conditions)}){date_constraint}'
            else:
                # Fallback para a consulta original
                formatted_query = f'(ti:"{query}" OR abs:"{query}"){date_constraint}'
        else:
            # Para consultas simples, buscar no título ou resumo
            formatted_query = f'(ti:"{query}" OR abs:"{query}"){date_constraint}'

    # Print the formatted query for debugging
    print(f"Formatted arXiv query: {formatted_query}")

    # Set up parameters according to arXiv API documentation
    params = {
        'search_query': formatted_query,
        'start': 0,
        'max_results': max_results
    }

    # Add sort parameters if they're valid
    if sort_by in ['relevance', 'lastUpdatedDate', 'submittedDate']:
        params['sortBy'] = sort_by
    if sort_order in ['ascending', 'descending']:
        params['sortOrder'] = sort_order

    try:
        # Print the URL and parameters for debugging
        print(f"ArXiv API URL: {base_url}")
        print(f"ArXiv API Parameters: {params}")

        # Make the request
        response = requests.get(base_url, params=params)

        # Print response status for debugging
        print(f"ArXiv API Response Status: {response.status_code}")

        if response.status_code == 200:
            # Check if response has content
            if not response.text:
                print("ArXiv API returned empty response")
                return []

            # Print first 200 chars of response for debugging
            print(f"ArXiv API Response Preview: {response.text[:200]}...")

            # Parse XML response
            root = ET.fromstring(response.text)

            # Define namespaces according to arXiv API documentation
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }

            # Check for total results using OpenSearch namespace
            total_results_elem = root.find('.//opensearch:totalResults', namespaces)
            if total_results_elem is not None:
                total_results = int(total_results_elem.text)
                print(f"Total results available: {total_results}")
                if total_results == 0:
                    print("No results found in arXiv")
                    return []

            # Check for feed entries (skip the first entry if it's an error)
            entries = root.findall('.//atom:entry', namespaces)

            # Check if the first entry is an error
            if entries and entries[0].find('.//atom:title', namespaces) is not None:
                first_title = entries[0].find('.//atom:title', namespaces).text
                if first_title == "Error":
                    error_summary = entries[0].find('.//atom:summary', namespaces)
                    if error_summary is not None:
                        print(f"ArXiv API Error: {error_summary.text}")
                    return []

            if not entries:
                print("No entries found in ArXiv response")
                feed_title = root.find('.//atom:title', namespaces)
                if feed_title is not None:
                    print(f"ArXiv response title: {feed_title.text}")
                return []

            print(f"Found {len(entries)} entries in ArXiv response")

            # Extract papers
            papers = []

            for entry in entries:
                try:
                    # Check if this is an error entry
                    entry_title_elem = entry.find('.//atom:title', namespaces)
                    if entry_title_elem is not None and entry_title_elem.text == "Error":
                        continue

                    # Extract basic information
                    title = entry_title_elem.text.strip() if entry_title_elem is not None and entry_title_elem.text else "No Title"

                    # Get the arXiv ID from the id element
                    id_elem = entry.find('.//atom:id', namespaces)
                    arxiv_id = "Unknown"
                    if id_elem is not None and id_elem.text:
                        # Extract ID from URL format http://arxiv.org/abs/XXXX.XXXXX
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
                            # Format might be YYYY-MM-DDThh:mm:ssZ or YYYY-MM-DDThh:mm:ss-hh:mm
                            date_str = published_elem.text
                            if 'T' in date_str and ('+' in date_str or '-' in date_str or 'Z' in date_str):
                                if 'Z' in date_str:
                                    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                                else:
                                    # Handle timezone offset
                                    dt = datetime.fromisoformat(date_str)
                                published_date = dt.strftime('%Y-%m-%d')
                            else:
                                published_date = date_str.split('T')[0]
                        except Exception as date_error:
                            print(f"Error parsing date {published_elem.text}: {date_error}")
                            published_date = published_elem.text

                    # Get updated date
                    updated_elem = entry.find('.//atom:updated', namespaces)
                    updated_date = published_date
                    if updated_elem is not None and updated_elem.text:
                        try:
                            date_str = updated_elem.text
                            if 'T' in date_str and ('+' in date_str or '-' in date_str or 'Z' in date_str):
                                if 'Z' in date_str:
                                    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                                else:
                                    # Handle timezone offset
                                    dt = datetime.fromisoformat(date_str)
                                updated_date = dt.strftime('%Y-%m-%d')
                            else:
                                updated_date = date_str.split('T')[0]
                        except Exception:
                            updated_date = updated_elem.text

                    # Extract authors
                    authors = []
                    for author_elem in entry.findall('.//atom:author', namespaces):
                        name_elem = author_elem.find('.//atom:name', namespaces)
                        if name_elem is not None and name_elem.text:
                            author_name = name_elem.text.strip()

                            # Check for affiliation
                            affiliation_elem = author_elem.find('.//arxiv:affiliation', namespaces)
                            if affiliation_elem is not None and affiliation_elem.text:
                                author_name += f" ({affiliation_elem.text.strip()})"

                            authors.append(author_name)

                    if not authors:
                        authors = ["Unknown"]

                    # Extract links
                    links = entry.findall('.//atom:link', namespaces)
                    abstract_url = ""
                    pdf_url = ""
                    doi_url = ""

                    for link in links:
                        rel = link.get('rel', '')
                        href = link.get('href', '')
                        title = link.get('title', '')

                        if rel == 'alternate' and href:
                            abstract_url = href
                        elif title == 'pdf' and href:
                            pdf_url = href
                        elif title == 'doi' and href:
                            doi_url = href

                    # Use the most appropriate URL
                    url = pdf_url if pdf_url else abstract_url
                    if not url:
                        url = f"https://arxiv.org/abs/{arxiv_id}"

                    # Extract categories
                    categories = []
                    for category in entry.findall('.//atom:category', namespaces):
                        term = category.get('term')
                        if term:
                            categories.append(term)

                    # Get primary category
                    primary_category = ""
                    primary_elem = entry.find('.//arxiv:primary_category', namespaces)
                    if primary_elem is not None:
                        primary_term = primary_elem.get('term')
                        if primary_term:
                            primary_category = primary_term
                            # Make sure primary category is first in the list
                            if primary_term in categories:
                                categories.remove(primary_term)
                            categories.insert(0, primary_term)

                    if not categories:
                        categories = ["Uncategorized"]

                    # Get additional arXiv metadata
                    comment = ""
                    comment_elem = entry.find('.//arxiv:comment', namespaces)
                    if comment_elem is not None and comment_elem.text:
                        comment = comment_elem.text.strip()

                    journal_ref = ""
                    journal_elem = entry.find('.//arxiv:journal_ref', namespaces)
                    if journal_elem is not None and journal_elem.text:
                        journal_ref = journal_elem.text.strip()

                    doi = ""
                    doi_elem = entry.find('.//arxiv:doi', namespaces)
                    if doi_elem is not None and doi_elem.text:
                        doi = doi_elem.text.strip()

                    # Create paper dictionary with all available information
                    paper = {
                        'title': title,
                        'arxiv_id': arxiv_id,
                        'authors': authors,
                        'summary': summary,
                        'published_date': published_date,
                        'updated_date': updated_date,
                        'url': url,
                        'abstract_url': abstract_url,
                        'pdf_url': pdf_url,
                        'doi_url': doi_url,
                        'categories': categories,
                        'primary_category': primary_category,
                        'comment': comment,
                        'journal_ref': journal_ref,
                        'doi': doi,
                        'source': 'arXiv'
                    }

                    papers.append(paper)
                except Exception as entry_error:
                    print(f"Error processing entry: {entry_error}")
                    continue

            return papers
        else:
            print(f"Error searching arXiv: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            return []

    except ET.ParseError as xml_error:
        print(f"XML parsing error in ArXiv response: {xml_error}")
        print(f"Response content: {response.text[:500] if 'response' in locals() else 'No response'}")
        return []
    except Exception as e:
        print(f"Error in search_arxiv: {e}")
        return []
