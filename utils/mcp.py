"""
Model Context Protocol (MCP) para integração de múltiplas fontes de dados.
Este módulo centraliza a conexão com diferentes APIs e fontes de dados,
fornecendo um protocolo unificado para obtenção de contexto para os modelos.
"""

import os
import re
import requests
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MCP")

# Carregar variáveis de ambiente
load_dotenv()

class ModelContextProtocol:
    """
    Implementação do Model Context Protocol (MCP) para integração de múltiplas fontes de dados.
    Centraliza a conexão com diferentes APIs e fornece um protocolo unificado para obtenção de contexto.
    """

    def __init__(self):
        """Inicializa o protocolo MCP."""
        # Carregar chaves de API
        self.serper_api_key = os.getenv("SERPER_API_KEY", "")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        self.reddit_user_agent = os.getenv("REDDIT_USER_AGENT", "FourSight Innovation System v1.0")
        self.producthunt_api_key = os.getenv("PRODUCTHUNT_API_KEY", "")

        # Verificar disponibilidade das APIs
        self.reddit_available = bool(self.reddit_client_id and self.reddit_client_secret)
        self.producthunt_available = bool(self.producthunt_api_key)
        self.serper_available = bool(self.serper_api_key)

        # Tokens e clientes de API (inicializados quando necessário)
        self.reddit_token = None
        self.reddit_client = None  # Cliente PRAW para o Reddit
        self.producthunt_token = None

    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Pesquisa na web usando a API Serper.

        Args:
            query: Consulta de pesquisa
            num_results: Número máximo de resultados

        Returns:
            Lista de resultados da web
        """
        if not self.serper_available:
            logger.warning("Serper API key não encontrada. Retornando lista vazia.")
            return []

        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }

        # Adicionar restrição de data para resultados recentes (2024-2025)
        date_restricted_query = f"{query} after:2024-01-01 before:2025-12-31"

        payload = {
            'q': date_restricted_query,
            'num': num_results,
            'timeRange': 'last12m'  # Restrição de tempo para os últimos 12 meses
        }

        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                search_results = response.json()

                # Processar e formatar resultados
                formatted_results = []

                if 'organic' in search_results:
                    for result in search_results['organic']:
                        formatted_results.append({
                            'title': result.get('title', 'Sem título'),
                            'url': result.get('link', ''),
                            'snippet': result.get('snippet', ''),
                            'source': 'Web',
                            'type': 'web'
                        })

                return formatted_results
            else:
                logger.error(f"Erro na pesquisa Serper: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Erro em search_web: {e}")
            return []

    def _translate_to_english(self, text: str) -> str:
        """
        Traduz texto do português para o inglês usando o modelo Llama 4.
        Se a API falhar, usa um método alternativo de tradução.

        Args:
            text: Texto em português para traduzir

        Returns:
            Texto traduzido para inglês
        """
        try:
            # Verificar se o texto já está em inglês
            english_words = ['the', 'and', 'of', 'to', 'in', 'for', 'on', 'with', 'at', 'by', 'from']
            text_lower = text.lower()

            # Se o texto contém várias palavras comuns em inglês, provavelmente já está em inglês
            english_word_count = sum(1 for word in english_words if f" {word} " in f" {text_lower} ")
            if english_word_count >= 3 or any(word == text_lower for word in english_words):
                return text

            # Verificar se temos acesso à API Groq
            groq_api_key = os.getenv("GROQ_API_KEY", "")
            if not groq_api_key:
                logger.warning("Chave da API Groq não encontrada. Usando método alternativo de tradução.")
                return self._translate_to_english_alternative(text)

            # Configurar a API Groq
            groq_api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
            groq_model = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }

            # Criar o prompt para tradução
            prompt = f"""Traduza o seguinte texto do português para o inglês.
            Mantenha todos os termos técnicos e nomes próprios.
            Retorne apenas o texto traduzido, sem explicações ou comentários adicionais.

            Texto: {text}

            Tradução:"""

            # Fazer a requisição para a API
            response = requests.post(
                f"{groq_api_base}/chat/completions",
                headers=headers,
                json={
                    "model": groq_model,
                    "messages": [
                        {"role": "system", "content": "Você é um tradutor profissional de português para inglês."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=10  # Adicionar timeout para evitar esperas longas
            )

            if response.status_code == 200:
                result = response.json()
                translated_text = result["choices"][0]["message"]["content"].strip()
                logger.info(f"Texto traduzido com sucesso: '{text}' -> '{translated_text}'")
                return translated_text
            else:
                logger.error(f"Erro na tradução: {response.status_code}")
                logger.error(f"Resposta: {response.text}")
                # Usar método alternativo de tradução
                return self._translate_to_english_alternative(text)

        except Exception as e:
            logger.error(f"Erro ao traduzir texto: {e}")
            # Usar método alternativo de tradução
            return self._translate_to_english_alternative(text)

    def _translate_to_english_alternative(self, text: str) -> str:
        """
        Método alternativo de tradução quando a API Groq falha.
        Usa um dicionário de traduções comuns e regras simples.

        Args:
            text: Texto em português para traduzir

        Returns:
            Texto traduzido para inglês
        """
        logger.info(f"Usando método alternativo de tradução para: '{text}'")

        # Dicionário de traduções comuns
        translations = {
            # Palavras comuns
            "inteligência artificial": "artificial intelligence",
            "inteligencia artificial": "artificial intelligence",
            "saúde": "health",
            "saude": "health",
            "blockchain": "blockchain",
            "na": "in",
            "no": "in",
            "da": "of",
            "do": "of",
            "de": "of",
            "e": "and",
            "ou": "or",
            "para": "for",
            "com": "with",
            "em": "in",
            "ao": "to",
            "aos": "to",
            "as": "the",
            "os": "the",
            "um": "a",
            "uma": "a",

            # Termos específicos de IA e saúde
            "diagnóstico": "diagnosis",
            "diagnostico": "diagnosis",
            "tratamento": "treatment",
            "paciente": "patient",
            "pacientes": "patients",
            "médico": "medical",
            "medico": "medical",
            "hospital": "hospital",
            "clínica": "clinic",
            "clinica": "clinic",
            "doença": "disease",
            "doenca": "disease",
            "terapia": "therapy",

            # Termos específicos de blockchain
            "criptomoeda": "cryptocurrency",
            "token": "token",
            "contrato inteligente": "smart contract",
            "descentralizado": "decentralized",
            "descentralizada": "decentralized",
            "ledger": "ledger",

            # Termos de negócios
            "empresa": "company",
            "negócio": "business",
            "negocio": "business",
            "mercado": "market",
            "inovação": "innovation",
            "inovacao": "innovation",
            "tecnologia": "technology",
            "solução": "solution",
            "solucao": "solution",
            "produto": "product",
            "serviço": "service",
            "servico": "service",
            "cliente": "client",
            "usuário": "user",
            "usuario": "user",
            "dados": "data",
            "análise": "analysis",
            "analise": "analysis",
            "integrada": "integrated",
            "integrado": "integrated",
            "sistema": "system",
            "aplicação": "application",
            "aplicacao": "application",
            "desenvolvimento": "development",
            "implementação": "implementation",
            "implementacao": "implementation",
            "pesquisa": "research",
            "estudo": "study",
            "método": "method",
            "metodo": "method",
            "processo": "process",
            "resultado": "result",
            "avaliação": "evaluation",
            "avaliacao": "evaluation",
            "teste": "test",
            "modelo": "model",
            "algoritmo": "algorithm",
            "ferramenta": "tool",
            "plataforma": "platform"
        }

        # Traduzir o texto
        translated_text = text

        # Substituir palavras e frases
        for pt, en in translations.items():
            # Substituir com preservação de maiúsculas/minúsculas
            pattern = re.compile(re.escape(pt), re.IGNORECASE)
            translated_text = pattern.sub(en, translated_text)

        logger.info(f"Tradução alternativa: '{text}' -> '{translated_text}'")
        return translated_text

    def search_arxiv(self, query: str, max_results: int = 5, context: str = "") -> List[Dict[str, Any]]:
        """
        Pesquisa artigos no arXiv usando a API do arXiv.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            context: Contexto adicional para melhorar a relevância da pesquisa

        Returns:
            Lista de resultados do arXiv
        """
        # Traduzir a consulta para inglês (arXiv funciona melhor com consultas em inglês)
        english_query = self._translate_to_english(query)

        # Traduzir o contexto se fornecido
        english_context = self._translate_to_english(context) if context else ""

        logger.info(f"Consulta traduzida: '{query}' -> '{english_query}'")
        if context:
            logger.info(f"Contexto traduzido: '{context}' -> '{english_context}'")

        # Usar o contexto traduzido para o restante do processamento
        context = english_context

        base_url = "http://export.arxiv.org/api/query"

        # Limitar o número de resultados
        if max_results > 100:
            max_results = 100  # Limite para evitar sobrecarga da API

        # Obter o ano atual para filtragem por data
        current_year = datetime.now().year

        # Extrair termos-chave da consulta e contexto para melhorar a pesquisa
        key_terms = [english_query]

        # Adicionar termos do contexto de negócio
        if context:
            # Extrair termos mais relevantes do contexto
            # Remover palavras comuns e manter apenas termos significativos
            common_words = {"a", "an", "the", "in", "on", "at", "by", "for", "with", "and", "or", "to", "of", "is", "are", "that", "this", "has", "have", "be", "been", "was", "were"}

            # Dividir o contexto em frases para melhor análise
            sentences = context.split('.')
            important_terms = []

            for sentence in sentences:
                words = sentence.strip().lower().split()
                # Filtrar palavras comuns e palavras curtas
                filtered_words = [word for word in words if word not in common_words and len(word) > 3]
                important_terms.extend(filtered_words)

            # Adicionar termos importantes do contexto
            key_terms.extend(important_terms)

            # Log dos termos-chave extraídos
            logger.info(f"Termos-chave extraídos do contexto: {important_terms[:10]}...")

        # Construir consulta aprimorada incorporando termos-chave do contexto
        # Adicionar restrição de data para artigos recentes (últimos 3 anos)
        date_constraint = f" AND submittedDate:[{current_year-3} TO {current_year}]"

        # Log da consulta traduzida para depuração
        logger.info(f"Consulta original: '{query}'")
        logger.info(f"Consulta traduzida: '{english_query}'")

        # Formatar consulta para a API do arXiv
        if any(prefix in english_query for prefix in ['ti:', 'au:', 'abs:', 'cat:', 'all:']):
            # Consulta já tem prefixos de campo, usar como está
            formatted_query = english_query.replace(' ', '+')
        else:
            # Para consultas em inglês, usar uma abordagem mais contextual
            query_words = english_query.split()

            # Identificar tópicos específicos para consultas especializadas
            query_lower = english_query.lower()

            # Consulta para IA na saúde
            if ("artificial intelligence" in query_lower or "ai" in query_lower.split()) and any(term in query_lower for term in ["health", "healthcare", "medical", "medicine", "clinical", "hospital", "patient"]):
                # Consulta específica para IA na saúde com termos do contexto
                context_terms = []
                if context:
                    # Extrair termos relevantes do contexto relacionados à saúde
                    health_related_terms = ["diagnos", "treatment", "patient", "clinic", "hospital", "doctor", "medical", "health", "disease", "therapy"]
                    for term in key_terms:
                        if any(health_term in term.lower() for health_term in health_related_terms) or len(term) > 5:
                            if term.lower() not in ["artificial", "intelligence", "health", "healthcare"]:
                                context_terms.append(term.lower())

                # Limitar a 3 termos de contexto mais relevantes
                context_terms = context_terms[:3]

                # Construir consulta com termos do contexto
                if context_terms:
                    context_query = " OR ".join([f'abs:"{term}"' for term in context_terms])
                    formatted_query = f'((ti:"artificial intelligence" AND (ti:health OR ti:healthcare OR ti:medical)) OR (abs:"artificial intelligence" AND (abs:health OR abs:healthcare OR abs:medical))) AND ({context_query}){date_constraint}'
                    logger.info(f"Usando consulta específica para IA na saúde com termos do contexto: {context_terms}")
                else:
                    formatted_query = f'(ti:"artificial intelligence" AND (ti:health OR ti:healthcare OR ti:medical)) OR (abs:"artificial intelligence" AND (abs:health OR abs:healthcare OR abs:medical)){date_constraint}'
                    logger.info("Usando consulta específica para IA na saúde")

                print(f"Usando consulta específica para IA na saúde: {formatted_query}")

            # Consulta para IA e blockchain
            elif ("artificial intelligence" in query_lower or "ai" in query_lower.split()) and "blockchain" in query_lower:
                # Consulta específica para IA e blockchain com termos do contexto
                context_terms = []
                if context:
                    # Extrair termos relevantes do contexto relacionados à blockchain
                    blockchain_related_terms = ["crypto", "token", "decentral", "ledger", "smart contract", "web3", "ethereum", "bitcoin"]
                    for term in key_terms:
                        if any(blockchain_term in term.lower() for blockchain_term in blockchain_related_terms) or len(term) > 5:
                            if term.lower() not in ["artificial", "intelligence", "blockchain"]:
                                context_terms.append(term.lower())

                # Limitar a 3 termos de contexto mais relevantes
                context_terms = context_terms[:3]

                # Construir consulta com termos do contexto
                if context_terms:
                    context_query = " OR ".join([f'abs:"{term}"' for term in context_terms])
                    formatted_query = f'((ti:"artificial intelligence" AND ti:blockchain) OR (abs:"artificial intelligence" AND abs:blockchain)) AND ({context_query}){date_constraint}'
                    logger.info(f"Usando consulta específica para IA e blockchain com termos do contexto: {context_terms}")
                else:
                    formatted_query = f'(ti:"artificial intelligence" AND ti:blockchain) OR (abs:"artificial intelligence" AND abs:blockchain){date_constraint}'
                    logger.info("Usando consulta específica para IA e blockchain")

                print(f"Usando consulta específica para IA e blockchain: {formatted_query}")

            # Consulta para IA em geral
            elif "artificial intelligence" in query_lower or "ai" in query_lower.split():
                # Extrair termos de contexto relevantes
                context_terms = [term.lower() for term in key_terms if term.lower() not in ["artificial", "intelligence", "ai"] and len(term) > 4][:3]

                # Construir consulta com termos do contexto
                if context_terms:
                    context_query = " OR ".join([f'abs:"{term}"' for term in context_terms])
                    formatted_query = f'(ti:"artificial intelligence" OR abs:"artificial intelligence") AND ({context_query}){date_constraint}'
                    logger.info(f"Usando consulta para IA com termos do contexto: {context_terms}")
                else:
                    formatted_query = f'(ti:"artificial intelligence" OR abs:"artificial intelligence"){date_constraint}'
                    logger.info("Usando consulta para IA geral")

                print(f"Usando consulta para IA: {formatted_query}")

            # Para outras consultas
            else:
                # Extrair termos principais da consulta
                main_query_terms = [term for term in query_words if len(term) > 3][:2]

                # Extrair termos de contexto relevantes (diferentes dos termos da consulta)
                context_terms = [term.lower() for term in key_terms if term.lower() not in [t.lower() for t in main_query_terms] and len(term) > 4][:3]

                # Construir consulta
                query_part = " AND ".join([f'(ti:"{term}" OR abs:"{term}")' for term in main_query_terms])

                if context_terms:
                    context_part = " OR ".join([f'abs:"{term}"' for term in context_terms])
                    formatted_query = f'({query_part}) AND ({context_part}){date_constraint}'
                    logger.info(f"Usando consulta personalizada com termos do contexto: {context_terms}")
                else:
                    formatted_query = f'({query_part}){date_constraint}'
                    logger.info("Usando consulta personalizada sem termos de contexto")

                print(f"Usando consulta personalizada: {formatted_query}")

        logger.info(f"Consulta arXiv formatada: {formatted_query}")

        # Configurar parâmetros de acordo com a documentação da API do arXiv
        params = {
            'search_query': formatted_query,
            'start': 0,
            'max_results': max_results
        }

        # Adicionar parâmetros de ordenação se válidos
        params['sortBy'] = 'relevance'
        params['sortOrder'] = 'descending'

        try:
            # Fazer a requisição
            response = requests.get(base_url, params=params)

            logger.info(f"Status da resposta da API arXiv: {response.status_code}")

            if response.status_code == 200:
                # Verificar se a resposta tem conteúdo
                if not response.text:
                    logger.warning("API arXiv retornou resposta vazia")
                    return []

                # Analisar resposta XML
                root = ET.fromstring(response.text)

                # Definir namespaces de acordo com a documentação da API do arXiv
                namespaces = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
                    'arxiv': 'http://arxiv.org/schemas/atom'
                }

                # Verificar resultados totais usando o namespace OpenSearch
                total_results_elem = root.find('.//opensearch:totalResults', namespaces)
                if total_results_elem is not None:
                    total_results = int(total_results_elem.text)
                    logger.info(f"Total de resultados disponíveis: {total_results}")
                    if total_results == 0:
                        logger.info("Nenhum resultado encontrado no arXiv")
                        return []

                # Verificar entradas de feed (pular a primeira entrada se for um erro)
                entries = root.findall('.//atom:entry', namespaces)

                # Verificar se a primeira entrada é um erro
                if entries and entries[0].find('.//atom:title', namespaces) is not None:
                    first_title = entries[0].find('.//atom:title', namespaces).text
                    if first_title == "Error":
                        error_summary = entries[0].find('.//atom:summary', namespaces)
                        if error_summary is not None:
                            logger.error(f"Erro da API arXiv: {error_summary.text}")
                        return []

                if not entries:
                    logger.warning("Nenhuma entrada encontrada na resposta do arXiv")
                    return []

                logger.info(f"Encontradas {len(entries)} entradas na resposta do arXiv")

                # Extrair artigos
                papers = []
                for entry in entries:
                    try:
                        # Extrair informações básicas
                        title = entry.find('.//atom:title', namespaces).text.strip()
                        summary = entry.find('.//atom:summary', namespaces).text.strip()

                        # Extrair autores
                        authors = []
                        author_elements = entry.findall('.//atom:author/atom:name', namespaces)
                        for author_elem in author_elements:
                            authors.append(author_elem.text)

                        # Extrair link para o artigo
                        links = entry.findall('.//atom:link', namespaces)
                        url = ""
                        pdf_url = ""
                        for link in links:
                            link_type = link.get('type', '')
                            if link_type == 'text/html':
                                url = link.get('href', '')
                            elif link_type == 'application/pdf':
                                pdf_url = link.get('href', '')

                        # Extrair data de publicação
                        published = entry.find('.//atom:published', namespaces).text
                        published_date = published.split('T')[0]  # Formato YYYY-MM-DD

                        # Extrair categorias
                        categories = []
                        category_elements = entry.findall('.//arxiv:primary_category', namespaces)
                        for cat_elem in category_elements:
                            categories.append(cat_elem.get('term', ''))

                        # Criar objeto de artigo
                        paper = {
                            'title': title,
                            'url': url,
                            'pdf_url': pdf_url,
                            'authors': authors,
                            'summary': summary,
                            'published_date': published_date,
                            'categories': categories,
                            'source': 'arXiv',
                            'type': 'paper'
                        }

                        papers.append(paper)
                    except Exception as entry_error:
                        logger.error(f"Erro ao processar entrada: {entry_error}")
                        continue

                return papers
            else:
                logger.error(f"Erro ao pesquisar no arXiv: {response.status_code}")
                logger.error(f"Conteúdo da resposta: {response.text[:500]}")
                return []

        except ET.ParseError as xml_error:
            logger.error(f"Erro de análise XML na resposta do arXiv: {xml_error}")
            return []
        except Exception as e:
            logger.error(f"Erro em search_arxiv: {e}")
            return []

    def _filter_health_ai_content(self, search_text: str, title: str = "", query: str = "") -> tuple:
        """
        Filtra conteúdo relacionado a IA na saúde de forma mais rigorosa.

        Args:
            search_text: Texto completo para pesquisa
            title: Título do conteúdo (opcional)
            query: Consulta original (opcional)

        Returns:
            Tupla (relevante, pontuação) indicando se o conteúdo é relevante e sua pontuação
        """
        # Verificar se a consulta está relacionada a IA na saúde
        query_parts = query.lower().split() if query else []
        is_health_ai_query = (("artificial intelligence" in query.lower() or "ai" in query_parts) and
                             any(term in query.lower() for term in ["health", "healthcare", "medical"])) if query else True

        if not is_health_ai_query:
            return (True, 1)  # Se não for consulta de IA na saúde, considerar relevante

        # Termos de IA mais específicos
        ai_terms = ["artificial intelligence", "ai ", "machine learning", "ml ", "deep learning",
                   "neural network", "generative ai", "llm", "large language model"]

        # Termos de saúde mais específicos
        health_terms = ["health", "healthcare", "medical", "medicine", "clinical", "hospital",
                       "patient", "diagnosis", "treatment", "doctor", "physician", "genetic",
                       "genetics", "disease", "therapy", "diagnostic"]

        # Verificar se ambos os temas estão presentes
        has_ai_term = any(ai_term in search_text.lower() for ai_term in ai_terms)
        has_health_term = any(health_term in search_text.lower() for health_term in health_terms)

        # Se não tiver ambos os temas, não é relevante
        if not (has_ai_term and has_health_term):
            return (False, 0)

        # Verificar se os termos estão próximos um do outro no texto
        sentences = search_text.lower().split('.')
        has_both_in_same_sentence = False

        for sentence in sentences:
            has_ai_in_sentence = any(ai_term in sentence for ai_term in ai_terms)
            has_health_in_sentence = any(health_term in sentence for health_term in health_terms)

            if has_ai_in_sentence and has_health_in_sentence:
                has_both_in_same_sentence = True
                break

        # Calcular pontuação de relevância
        relevance_score = 2 if has_both_in_same_sentence else 1

        # Palavras-chave específicas para IA na saúde
        health_ai_keywords = ai_terms + health_terms

        # Pontuação adicional por cada palavra-chave específica
        for keyword in health_ai_keywords:
            if keyword in search_text.lower():
                relevance_score += 1

        # Verificar se o título contém termos relevantes
        if title:
            title_lower = title.lower()
            has_ai_in_title = any(ai_term in title_lower for ai_term in ai_terms)
            has_health_in_title = any(health_term in title_lower for health_term in health_terms)

            # Dar pontuação extra se os termos estiverem no título
            if has_ai_in_title:
                relevance_score += 2
            if has_health_in_title:
                relevance_score += 2
            if has_ai_in_title and has_health_in_title:
                relevance_score += 3  # Bônus extra por ter ambos no título

        # Considerar relevante se tiver pontuação mínima
        is_relevant = relevance_score >= 4

        return (is_relevant, relevance_score)

    def _get_reddit_token(self) -> bool:
        """
        Implementação alternativa que não depende de autenticação.
        Usaremos uma abordagem baseada em web scraping para o Reddit.

        Returns:
            True sempre, já que não precisamos de autenticação
        """
        logger.info("Usando abordagem alternativa para o Reddit (sem autenticação)")
        return True

    def search_reddit(self, query: str, max_results: int = 5, time_filter: str = "year") -> List[Dict[str, Any]]:
        """
        Pesquisa no Reddit usando a API oficial (PRAW).

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            time_filter: Filtro de tempo ('hour', 'day', 'week', 'month', 'year', 'all')

        Returns:
            Lista de resultados do Reddit
        """
        try:
            # Traduzir a consulta para inglês para melhores resultados
            english_query = self._translate_to_english(query)
            logger.info(f"Pesquisando no Reddit: {english_query}")

            # Verificar se temos as credenciais do Reddit no .env
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            user_agent = os.getenv("REDDIT_USER_AGENT", "FourSight Innovation System/1.0")

            # Se não temos credenciais, tentar uma abordagem alternativa
            if not client_id or not client_secret:
                logger.warning("Credenciais do Reddit não encontradas. Tentando abordagem alternativa.")

                # Usar uma abordagem alternativa com o pushshift.io API
                # Esta API não requer autenticação e fornece acesso a dados históricos do Reddit
                pushshift_url = f"https://api.pushshift.io/reddit/search/submission?q={english_query.replace(' ', '+')}&sort=desc&sort_type=created_utc&size={max_results}"

                headers = {
                    'User-Agent': 'FourSight Innovation System/1.0'
                }

                response = requests.get(pushshift_url, headers=headers, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    if 'data' in data and len(data['data']) > 0:
                        formatted_results = []

                        for post in data['data']:
                            # Converter timestamp para data legível
                            created_date = datetime.fromtimestamp(post.get('created_utc', 0)).strftime('%Y-%m-%d')

                            # Extrair texto do post
                            snippet = post.get('selftext', '')
                            if not snippet and 'title' in post:
                                snippet = post.get('title', '')

                            # Truncar snippet se for muito longo
                            if len(snippet) > 500:
                                snippet = snippet[:497] + "..."

                            # Adicionar ao resultado
                            formatted_results.append({
                                'title': post.get('title', 'Sem título'),
                                'url': f"https://www.reddit.com{post.get('permalink', '')}",
                                'original_url': f"https://www.reddit.com{post.get('permalink', '')}",
                                'snippet': snippet,
                                'created_date': created_date,
                                'subreddit': post.get('subreddit', ''),
                                'score': post.get('score', 0),
                                'num_comments': post.get('num_comments', 0),
                                'source': 'Reddit',
                                'type': 'social'
                            })

                        logger.info(f"Encontrados {len(formatted_results)} resultados do Reddit via Pushshift API")
                        return formatted_results
                    else:
                        logger.warning("Nenhum resultado encontrado no Reddit via Pushshift API")
                        return []
                else:
                    logger.error(f"Erro ao acessar a Pushshift API: {response.status_code}")
                    return []

            # Se temos credenciais, usar a API oficial do Reddit (PRAW)
            import praw

            # Verificar se temos username e password
            username = os.getenv("REDDIT_USERNAME")
            password = os.getenv("REDDIT_PASSWORD")

            # Se temos todas as credenciais, usar autenticação completa
            if username and password:
                logger.info("Usando autenticação completa do Reddit")
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                    username=username,
                    password=password
                )
            else:
                # Usar autenticação somente com client_id e client_secret (read-only)
                logger.info("Usando autenticação read-only do Reddit")
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )

            # Verificar se a autenticação foi bem-sucedida
            try:
                # Testar a autenticação
                reddit.auth.scopes()
                logger.info("Autenticação do Reddit bem-sucedida")
            except Exception as e:
                logger.error(f"Erro na autenticação do Reddit: {e}")
                # Tentar abordagem alternativa
                return self._search_reddit_alternative(english_query, max_results)

            # Realizar a pesquisa
            try:
                search_results = reddit.subreddit("all").search(
                    query=english_query,
                    sort="relevance",
                    time_filter=time_filter,
                    limit=max_results
                )
            except Exception as e:
                logger.error(f"Erro na pesquisa do Reddit: {e}")
                # Tentar abordagem alternativa
                return self._search_reddit_alternative(english_query, max_results)

            formatted_results = []

            for post in search_results:
                # Converter timestamp para data legível
                created_date = datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')

                # Extrair texto do post
                snippet = post.selftext
                if not snippet:
                    snippet = post.title

                # Truncar snippet se for muito longo
                if len(snippet) > 500:
                    snippet = snippet[:497] + "..."

                # Adicionar ao resultado
                formatted_results.append({
                    'title': post.title,
                    'url': f"https://www.reddit.com{post.permalink}",
                    'original_url': f"https://www.reddit.com{post.permalink}",
                    'snippet': snippet,
                    'created_date': created_date,
                    'subreddit': post.subreddit.display_name,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'source': 'Reddit',
                    'type': 'social'
                })

            logger.info(f"Encontrados {len(formatted_results)} resultados do Reddit via API oficial")
            return formatted_results

        except Exception as e:
            logger.error(f"Erro em search_reddit: {e}")
            # Tentar abordagem alternativa
            return self._search_reddit_alternative(query, max_results)

    def _search_reddit_alternative(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Método alternativo para pesquisar no Reddit quando a API oficial falha.
        Usa a API do Algolia que o Reddit usa para sua própria funcionalidade de pesquisa.

        Args:
            query: Consulta de pesquisa (já traduzida para inglês)
            max_results: Número máximo de resultados

        Returns:
            Lista de resultados do Reddit
        """
        logger.info(f"Usando método alternativo (Algolia) para pesquisar no Reddit: {query}")

        try:
            # Usar a API do Algolia que o Reddit usa para sua própria funcionalidade de pesquisa
            # Esta API não requer autenticação e é mais confiável
            algolia_url = "https://www.reddit.com/search.json"

            # Parâmetros de pesquisa
            params = {
                'q': query,
                'sort': 'relevance',
                't': 'year',  # Últimos 12 meses
                'limit': max_results * 3  # Solicitar mais resultados para filtrar depois
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            response = requests.get(algolia_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                try:
                    data = response.json()

                    if 'data' in data and 'children' in data['data']:
                        posts = data['data']['children']
                        formatted_results = []

                        for post_data in posts:
                            if 'data' not in post_data:
                                continue

                            post = post_data['data']

                            # Texto para pesquisa (título e texto do post)
                            title = post.get('title', '')
                            selftext = post.get('selftext', '')
                            search_text = title + ' ' + selftext

                            # Usar a função de filtragem melhorada
                            is_relevant, relevance_score = self._filter_health_ai_content(
                                search_text=search_text,
                                title=title,
                                query=query
                            )

                            # Se não for relevante, pular
                            if not is_relevant:
                                continue

                            # Extrair texto do post
                            snippet = selftext
                            if not snippet:
                                snippet = title

                            # Truncar snippet se for muito longo
                            if len(snippet) > 500:
                                snippet = snippet[:497] + "..."

                            # Converter timestamp para data legível
                            created_utc = post.get('created_utc', 0)
                            created_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')

                            # Adicionar ao resultado
                            formatted_results.append({
                                'title': title,
                                'url': f"https://www.reddit.com{post.get('permalink', '')}",
                                'original_url': f"https://www.reddit.com{post.get('permalink', '')}",
                                'snippet': snippet,
                                'created_date': created_date,
                                'subreddit': post.get('subreddit', ''),
                                'score': post.get('score', 0),
                                'num_comments': post.get('num_comments', 0),
                                'relevance_score': relevance_score,
                                'source': 'Reddit',
                                'type': 'social'
                            })

                        # Ordenar por relevância (mais relevantes primeiro)
                        formatted_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

                        # Limitar ao número máximo de resultados
                        formatted_results = formatted_results[:max_results]

                        logger.info(f"Encontrados {len(formatted_results)} resultados do Reddit via API Algolia")
                        return formatted_results
                    else:
                        logger.warning("Formato de resposta inesperado da API do Reddit")
                        return []
                except json.JSONDecodeError:
                    logger.error("Erro ao decodificar resposta JSON do Reddit")
                    return []
            else:
                logger.error(f"Erro ao acessar a API alternativa do Reddit: {response.status_code}")

                # Se ainda falhar, tentar uma terceira abordagem usando a API JSON do Reddit
                return self._search_reddit_third_approach(query, max_results)

        except Exception as e:
            logger.error(f"Erro no método alternativo do Reddit: {e}")
            # Tentar uma terceira abordagem
            return self._search_reddit_third_approach(query, max_results)

    def _search_reddit_third_approach(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Terceira abordagem para pesquisar no Reddit quando as outras falham.
        Usa a API JSON direta do Reddit.

        Args:
            query: Consulta de pesquisa (já traduzida para inglês)
            max_results: Número máximo de resultados

        Returns:
            Lista de resultados do Reddit
        """
        logger.info(f"Usando terceira abordagem para pesquisar no Reddit: {query}")

        try:
            # Usar a API JSON direta do Reddit
            # Formatar a consulta para URL
            formatted_query = query.replace(' ', '+')

            # Construir URL de pesquisa do Reddit
            reddit_url = f"https://www.reddit.com/search/.json?q={formatted_query}&sort=relevance&t=year&limit={max_results*2}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.5'
            }

            response = requests.get(reddit_url, headers=headers, timeout=15)

            if response.status_code == 200:
                try:
                    data = response.json()

                    if 'data' in data and 'children' in data['data']:
                        posts = data['data']['children']
                        formatted_results = []

                        for post_data in posts:
                            if 'data' not in post_data:
                                continue

                            post = post_data['data']

                            # Texto para pesquisa (título e texto do post)
                            title = post.get('title', '')
                            selftext = post.get('selftext', '')
                            search_text = title + ' ' + selftext

                            # Usar a função de filtragem melhorada
                            is_relevant, relevance_score = self._filter_health_ai_content(
                                search_text=search_text,
                                title=title,
                                query=query
                            )

                            # Se não for relevante, pular
                            if not is_relevant:
                                continue

                            # Extrair texto do post
                            snippet = post.get('selftext', '')
                            if not snippet:
                                snippet = post.get('title', '')

                            # Truncar snippet se for muito longo
                            if len(snippet) > 500:
                                snippet = snippet[:497] + "..."

                            # Converter timestamp para data legível
                            created_utc = post.get('created_utc', 0)
                            created_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')

                            # Adicionar ao resultado
                            formatted_results.append({
                                'title': post.get('title', 'Sem título'),
                                'url': f"https://www.reddit.com{post.get('permalink', '')}",
                                'original_url': f"https://www.reddit.com{post.get('permalink', '')}",
                                'snippet': snippet,
                                'created_date': created_date,
                                'subreddit': post.get('subreddit', ''),
                                'score': post.get('score', 0),
                                'num_comments': post.get('num_comments', 0),
                                'relevance_score': relevance_score,
                                'source': 'Reddit',
                                'type': 'social'
                            })

                        # Ordenar por relevância (mais relevantes primeiro)
                        formatted_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

                        # Limitar ao número máximo de resultados
                        formatted_results = formatted_results[:max_results]

                        logger.info(f"Encontrados {len(formatted_results)} resultados do Reddit via terceira abordagem")
                        return formatted_results
                    else:
                        logger.warning("Formato de resposta inesperado da API do Reddit (terceira abordagem)")
                        return []
                except json.JSONDecodeError:
                    logger.error("Erro ao decodificar resposta JSON do Reddit (terceira abordagem)")
                    return []
            else:
                logger.error(f"Erro ao acessar a API do Reddit (terceira abordagem): {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Erro na terceira abordagem do Reddit: {e}")
            return []

    def _get_producthunt_token(self) -> bool:
        """
        Obtém token de autenticação para a API do Product Hunt.

        Returns:
            True se a autenticação foi bem-sucedida, False caso contrário
        """
        # Recarregar a chave da API do arquivo .env
        load_dotenv(override=True)
        self.producthunt_api_key = os.getenv("PRODUCTHUNT_API_KEY", "")
        self.producthunt_available = bool(self.producthunt_api_key)

        if not self.producthunt_available:
            logger.warning("Chave de API do Product Hunt não configurada")
            return False

        # Devido às proteções Cloudflare, vamos usar uma abordagem alternativa
        # Simplesmente armazenar o token e tentar usá-lo diretamente
        logger.info("Usando token do Product Hunt diretamente")
        self.producthunt_token = self.producthunt_api_key
        logger.info(f"Token do Product Hunt carregado: {self.producthunt_api_key}")
        return True

    def search_producthunt(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Pesquisa no Product Hunt usando a API GraphQL do Product Hunt.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados

        Returns:
            Lista de resultados do Product Hunt
        """
        if not self.producthunt_available:
            logger.warning("API do Product Hunt não disponível. Retornando lista vazia.")
            return []

        # Obter token se necessário
        if not self.producthunt_token and not self._get_producthunt_token():
            return []

        # Traduzir a consulta para inglês para melhor correspondência
        english_query = self._translate_to_english(query)

        logger.info(f"Pesquisando no Product Hunt: {english_query}")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.producthunt_token}',
            'User-Agent': 'FourSight Innovation System/1.0'
        }

        # Verificar se o token está correto
        print(f"Token do Product Hunt: {self.producthunt_token}")

        # Consulta GraphQL com mais campos
        # A API do Product Hunt não aceita o parâmetro 'search' diretamente
        # Vamos buscar os posts mais recentes e filtrar no lado do cliente

        graphql_query = f'''
        {{
          posts(first: 20, order: NEWEST) {{
            edges {{
              node {{
                id
                name
                tagline
                description
                url
                votesCount
                commentsCount
                createdAt
                website
                topics(first: 3) {{
                  edges {{
                    node {{
                      name
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        '''

        # Log da consulta para depuração
        logger.info(f"Consulta GraphQL do Product Hunt para: '{english_query}'")
        print(f"Headers enviados para Product Hunt: {headers}")
        print(f"Token usado: {self.producthunt_token[:10]}...")

        try:
            response = requests.post(
                'https://api.producthunt.com/v2/api/graphql',
                headers=headers,
                json={'query': graphql_query}
            )

            if response.status_code == 200:
                data = response.json()

                # Log para depuração
                logger.info(f"Resposta inicial do Product Hunt: {str(data)[:200]}...")

                # Processar e formatar resultados
                formatted_results = []

                if 'data' in data and 'posts' in data['data'] and 'edges' in data['data']['posts']:
                    edges = data['data']['posts']['edges']
                    logger.info(f"Encontrados {len(edges)} resultados iniciais do Product Hunt")

                    # Preparar palavras-chave para filtragem
                    # Usar tanto a consulta original quanto a traduzida para garantir melhor correspondência
                    keywords_original = query.lower().split()
                    keywords_english = english_query.lower().split()

                    # Combinar palavras-chave de ambas as consultas
                    all_keywords = keywords_original + keywords_english

                    # Remover palavras comuns
                    common_words = {"in", "the", "and", "or", "of", "for", "with", "on", "at", "by", "to", "a", "an", "integrated", "integration", "na", "no", "da", "do", "de", "e", "ou", "que", "para", "com", "em", "ao", "aos", "as", "os", "um", "uma"}
                    search_keywords = [word for word in all_keywords if word not in common_words and len(word) > 3]

                    # Remover duplicatas
                    search_keywords = list(set(search_keywords))

                    logger.info(f"Filtrando resultados do Product Hunt com palavras-chave: {search_keywords}")

                    # Processar todos os resultados
                    all_results = []

                    for edge in data['data']['posts']['edges']:
                        node = edge['node']

                        # Extrair tópicos
                        topics = []
                        if 'topics' in node and 'edges' in node['topics']:
                            for topic_edge in node['topics']['edges']:
                                topics.append(topic_edge['node']['name'])

                        # Converter data de criação para formato legível
                        created_at = node.get('createdAt', '')
                        if created_at:
                            created_date = created_at.split('T')[0]  # Formato YYYY-MM-DD
                        else:
                            created_date = ''

                        # Criar o resultado
                        result = {
                            'title': node.get('name', 'Sem nome'),
                            'url': node.get('url', ''),
                            'website': node.get('website', ''),
                            'snippet': node.get('tagline', '') + '\n\n' + (node.get('description', '') or '')[:200] + '...',
                            'created_date': created_date,
                            'votes': node.get('votesCount', 0),
                            'comments': node.get('commentsCount', 0),
                            'topics': topics,
                            'source': 'Product Hunt',
                            'type': 'product'
                        }

                        # Adicionar à lista de todos os resultados
                        all_results.append(result)

                    # Filtrar resultados relevantes
                    for result in all_results:
                        # Texto para pesquisa (título, tagline, descrição e tópicos)
                        search_text = (
                            result['title'].lower() + ' ' +
                            result['snippet'].lower() + ' ' +
                            ' '.join(result['topics']).lower()
                        )

                        # Usar a função de filtragem melhorada
                        is_relevant, relevance_score = self._filter_health_ai_content(
                            search_text=search_text,
                            title=result['title'],
                            query=english_query
                        )

                        # Se não for uma consulta de IA na saúde ou não for relevante para IA na saúde,
                        # usar a abordagem padrão para outras consultas
                        if not is_relevant and relevance_score == 0:
                            # Para outras consultas, usar abordagem padrão
                            relevance_score = 0
                            for keyword in search_keywords:
                                if keyword in search_text:
                                    relevance_score += 1

                        # Exigir pontuação mínima de relevância
                        # Se encontrou pelo menos uma palavra-chave ou não temos palavras-chave para filtrar
                        if relevance_score > 0 or not search_keywords:
                            # Adicionar pontuação de relevância
                            result['relevance_score'] = relevance_score
                            formatted_results.append(result)

                    # Ordenar por relevância (mais relevantes primeiro)
                    formatted_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

                    # Limitar ao número máximo de resultados
                    formatted_results = formatted_results[:max_results]

                    logger.info(f"Filtrados {len(formatted_results)} resultados relevantes do Product Hunt")

                # Se não encontrou resultados com a consulta específica, tentar uma consulta mais genérica
                if not formatted_results:
                    logger.info("Nenhum resultado encontrado com a consulta específica. Tentando consulta mais genérica.")

                    # Tentar com consultas mais simples relacionadas ao tópico
                    # Extrair palavras-chave da consulta original
                    keywords = english_query.lower().split()

                    # Remover palavras comuns
                    common_words = {"in", "the", "and", "or", "of", "for", "with", "on", "at", "by", "to", "a", "an", "integrated", "integration"}
                    main_keywords = [word for word in keywords if word not in common_words and len(word) > 3]

                    # Criar consultas simples baseadas nas palavras-chave
                    simple_queries = []

                    # Adicionar palavras-chave individuais
                    for keyword in main_keywords:
                        simple_queries.append(keyword)

                    # Adicionar combinações de palavras-chave se houver mais de uma
                    if len(main_keywords) > 1:
                        for i in range(len(main_keywords)):
                            for j in range(i+1, len(main_keywords)):
                                simple_queries.append(f"{main_keywords[i]} {main_keywords[j]}")

                    # Adicionar consultas genéricas relacionadas a tecnologia
                    simple_queries.extend(["technology", "innovation", "tech", "startup", "product", "app", "software", "platform"])

                    for simple_query in simple_queries:
                        logger.info(f"Tentando consulta simples: '{simple_query}'")

                        # Não precisamos fazer uma nova consulta, pois a API não aceita o parâmetro 'search'
                        # Vamos apenas ajustar as palavras-chave para filtragem
                        logger.info(f"Ajustando filtragem para palavra-chave: '{simple_query}'")

                        # Usar apenas esta palavra-chave para filtragem
                        search_keywords = [simple_query]

                        # Filtrar os resultados originais com esta palavra-chave
                        filtered_results = []

                        for result in all_results:
                            # Texto para pesquisa (título, tagline, descrição e tópicos)
                            search_text = (
                                result['title'].lower() + ' ' +
                                result['snippet'].lower() + ' ' +
                                ' '.join(result['topics']).lower()
                            )

                            # Verificar se a palavra-chave está presente
                            if simple_query in search_text:
                                # Adicionar pontuação de relevância
                                result['relevance_score'] = 1
                                filtered_results.append(result)

                        # Se encontrou resultados com esta palavra-chave
                        if filtered_results:
                            # Limitar ao número máximo de resultados
                            filtered_results = filtered_results[:max_results]
                            logger.info(f"Encontrados {len(filtered_results)} resultados para '{simple_query}'")
                            formatted_results = filtered_results
                            break

                        # Não precisamos fazer uma nova consulta à API, pois já temos todos os resultados
                        # e estamos apenas filtrando-os com diferentes palavras-chave

                    # Se ainda não encontrou resultados, retornar lista vazia
                    if not formatted_results:
                        logger.info("Nenhum resultado encontrado no Product Hunt para nenhuma das consultas tentadas")
                        # Retornar lista vazia em vez de usar dados simulados

                return formatted_results
            else:
                logger.error(f"Erro na pesquisa do Product Hunt: {response.status_code}")
                logger.error(f"Resposta: {response.text[:500]}")

                # Se a API falhar, retornar lista vazia
                return []

        except Exception as e:
            logger.error(f"Erro em search_producthunt: {e}")
            return []



    def get_context(self, query: str, max_results: int = 5, context: str = "") -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtém contexto de múltiplas fontes para uma consulta.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados por fonte
            context: Contexto adicional para melhorar a relevância da pesquisa

        Returns:
            Dicionário com resultados de diferentes fontes
        """
        # Resultados de cada fonte
        try:
            web_results = self.search_web(query, max_results)
        except Exception as e:
            logger.error(f"Erro ao buscar resultados da web: {e}")
            web_results = []

        try:
            arxiv_results = self.search_arxiv(query, max_results, context)
        except Exception as e:
            logger.error(f"Erro ao buscar resultados do arXiv: {e}")
            arxiv_results = []

        try:
            reddit_results = self.search_reddit(query, max_results)
        except Exception as e:
            logger.error(f"Erro ao buscar resultados do Reddit: {e}")
            reddit_results = []

        try:
            producthunt_results = self.search_producthunt(query, max_results)
        except Exception as e:
            logger.error(f"Erro ao buscar resultados do Product Hunt: {e}")
            producthunt_results = []

        # Combinar resultados
        all_results = web_results + arxiv_results + reddit_results + producthunt_results

        # Organizar por fonte
        return {
            'all': all_results,
            'web': web_results,
            'arxiv': arxiv_results,
            'reddit': reddit_results,
            'producthunt': producthunt_results
        }

# Instância global para uso em todo o projeto
mcp = ModelContextProtocol()
