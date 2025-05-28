"""
Model Context Protocol (MCP) para integração de múltiplas fontes de dados.
Este módulo centraliza a conexão com diferentes APIs e fontes de dados,
fornecendo um protocolo unificado para obtenção de contexto para os modelos.

Versão melhorada com:
- Melhor busca no Product Hunt usando múltiplas estratégias
- Filtragem mais inteligente e contextual
- Tratamento de erros melhorado
- Fallbacks mais robustos
- Logs detalhados para debugging
"""

import os
import re
import requests
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import time
import random

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MCP")

# Carregar variáveis de ambiente
load_dotenv()

class ModelContextProtocol:
    """
    Implementação melhorada do Model Context Protocol (MCP) para integração de múltiplas fontes de dados.
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

        # Tokens e clientes de API
        self.reddit_token = None
        self.producthunt_token = None

        # Cache para evitar muitas chamadas de API
        self._cache = {}
        self._cache_timeout = 300  # 5 minutos

        logger.info(f"MCP inicializado - Serper: {self.serper_available}, Reddit: {self.reddit_available}, ProductHunt: {self.producthunt_available}")

    def _get_cache_key(self, source: str, query: str, **kwargs) -> str:
        """Gera uma chave de cache para consultas."""
        key_parts = [source, query.lower()]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return "|".join(key_parts)

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Obtém um resultado do cache se ainda válido."""
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if time.time() - timestamp < self._cache_timeout:
                logger.info(f"Resultado obtido do cache: {cache_key[:50]}...")
                return data
        return None

    def _set_cache(self, cache_key: str, data: Any):
        """Armazena um resultado no cache."""
        self._cache[cache_key] = (time.time(), data)

    def _extract_keywords_smart(self, text: str, context: str = "") -> List[str]:
        """
        Extrai palavras-chave de forma inteligente de um texto.

        Args:
            text: Texto principal
            context: Contexto adicional

        Returns:
            Lista de palavras-chave relevantes
        """
        # Dicionário de sinônimos e termos relacionados
        synonym_map = {
            "artificial intelligence": ["ai", "machine learning", "deep learning", "neural network", "ml"],
            "blockchain": ["crypto", "cryptocurrency", "web3", "defi", "smart contract"],
            "health": ["healthcare", "medical", "medicine", "clinical", "wellness", "fitness"],
            "finance": ["financial", "fintech", "banking", "payment", "trading"],
            "education": ["learning", "teaching", "training", "academic", "school"],
            "ecommerce": ["shopping", "retail", "marketplace", "store"],
            "productivity": ["workflow", "automation", "efficiency", "organization"],
            "communication": ["messaging", "chat", "collaboration", "social"],
            "data": ["analytics", "visualization", "dashboard", "reporting"],
            "security": ["cybersecurity", "privacy", "encryption", "authentication"]
        }

        # Extrair palavras-chave do texto principal
        words = re.findall(r'\b\w{3,}\b', text.lower())

        # Adicionar palavras do contexto
        if context:
            context_words = re.findall(r'\b\w{3,}\b', context.lower())
            words.extend(context_words)

        # Remover palavras comuns
        stop_words = {
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "its", "may", "new", "now", "old", "see", "two", "who", "boy", "did", "she", "use", "her", "way", "many", "then", "them", "these", "would", "like", "into", "time", "very", "when", "come", "could", "said", "each", "which", "their", "called", "long", "water", "been", "find", "more", "made", "part", "than", "were", "first", "down", "work", "right", "used", "your", "only", "think", "also", "after", "back", "other", "good", "just", "where", "most", "know", "take", "years", "same", "much", "before", "great", "through", "well", "another", "little", "should", "around", "such", "here", "even", "place", "still", "help", "small", "might", "again", "too", "any", "last", "set", "every", "turn", "why", "asked", "went", "men", "read", "need", "land", "different", "home", "move", "try", "kind", "hand", "picture", "being", "point", "world", "high", "head", "food", "far", "between", "own", "under", "story", "seen", "left", "don't", "few", "while", "along", "might", "close", "night", "real", "life", "never", "open", "door", "until", "without", "once", "white", "upon", "whole", "show", "heard", "house", "several", "during", "always", "example", "both", "important", "large", "often", "together", "asked", "house", "world", "going", "want", "school", "important", "until", "form", "food", "keep", "children", "feet", "land", "side", "without", "boy", "once", "animal", "life", "enough", "took", "sometimes", "four", "head", "above", "kind", "began", "almost", "live", "page", "got", "earth", "need", "far", "hand", "high", "year", "mother", "light", "country", "father", "let", "night", "picture", "being", "study", "second", "book", "carry", "took", "science", "eat", "room", "friend", "began", "idea", "fish", "mountain", "north", "once", "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood", "main", "enough", "plain", "girl", "usual", "young", "ready", "above", "ever", "red", "list", "though", "feel", "talk", "bird", "soon", "body", "dog", "family", "direct", "leave", "song", "measure", "door", "product", "black", "short", "numeral", "class", "wind", "question", "happen", "complete", "ship", "area", "half", "rock", "order", "fire", "south", "problem", "piece", "told", "knew", "pass", "since", "top", "whole", "king", "space", "heard", "best", "hour", "better", "during", "hundred", "five", "remember", "step", "early", "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing", "listen", "six", "table", "travel", "less", "morning", "ten", "simple", "several", "vowel", "toward", "war", "lay", "against", "pattern", "slow", "center", "love", "person", "money", "serve", "appear", "road", "map", "rain", "rule", "govern", "pull", "cold", "notice", "voice", "unit", "power", "town", "fine", "certain", "fly", "fall", "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure", "star", "box", "noun", "field", "rest", "correct", "able", "pound", "done", "beauty", "drive", "stood", "contain", "front", "teach", "week", "final", "gave", "green", "oh", "quick", "develop", "ocean", "warm", "free", "minute", "strong", "special", "mind", "behind", "clear", "tail", "produce", "fact", "street", "inch", "multiply", "nothing", "course", "stay", "wheel", "full", "force", "blue", "object", "decide", "surface", "deep", "moon", "island", "foot", "system", "busy", "test", "record", "boat", "common", "gold", "possible", "plane", "stead", "dry", "wonder", "laugh", "thousands", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss", "brought", "heat", "snow", "tire", "yes", "distant", "fill", "east", "paint", "language", "among", "grand", "ball", "yet", "wave", "drop", "heart", "am", "present", "heavy", "dance", "engine", "position", "arm", "wide", "sail", "material", "size", "vary", "settle", "speak", "weight", "general", "ice", "matter", "circle", "pair", "include", "divide", "syllable", "felt", "perhaps", "pick", "sudden", "count", "square", "reason", "length", "represent", "art", "subject", "region", "energy", "hunt", "probable", "bed", "brother", "egg", "ride", "cell", "believe", "fraction", "forest", "sit", "race", "window", "store", "summer", "train", "sleep", "prove", "lone", "leg", "exercise", "wall", "catch", "mount", "wish", "sky", "board", "joy", "winter", "sat", "written", "wild", "instrument", "kept", "glass", "grass", "cow", "job", "edge", "sign", "visit", "past", "soft", "fun", "bright", "gas", "weather", "month", "million", "bear", "finish", "happy", "hope", "flower", "clothe", "strange", "gone", "jump", "baby", "eight", "village", "meet", "root", "buy", "raise", "solve", "metal", "whether", "push", "seven", "paragraph", "third", "shall", "held", "hair", "describe", "cook", "floor", "either", "result", "burn", "hill", "safe", "cat", "century", "consider", "type", "law", "bit", "coast", "copy", "phrase", "silent", "tall", "sand", "soil", "roll", "temperature", "finger", "industry", "value", "fight", "lie", "beat", "excite", "natural", "view", "sense", "ear", "else", "quite", "broke", "case", "middle", "kill", "son", "lake", "moment", "scale", "loud", "spring", "observe", "child", "straight", "consonant", "nation", "dictionary", "milk", "speed", "method", "organ", "pay", "age", "section", "dress", "cloud", "surprise", "quiet", "stone", "tiny", "climb", "bad", "oil", "blood", "touch", "grew", "cent", "mix", "team", "wire", "cost", "lost", "brown", "wear", "garden", "equal", "sent", "choose", "fell", "fit", "flow", "fair", "bank", "collect", "save", "control", "decimal", "gentle", "woman", "captain", "practice", "separate", "difficult", "doctor", "please", "protect", "noon", "whose", "locate", "ring", "character", "insect", "caught", "period", "indicate", "radio", "spoke", "atom", "human", "history", "effect", "electric", "expect", "crop", "modern", "element", "hit", "student", "corner", "party", "supply", "bone", "rail", "imagine", "provide", "agree", "thus", "capital", "won't", "chair", "danger", "fruit", "rich", "thick", "soldier", "process", "operate", "guess", "necessary", "sharp", "wing", "create", "neighbor", "wash", "bat", "rather", "crowd", "corn", "compare", "poem", "string", "bell", "depend", "meat", "rub", "tube", "famous", "dollar", "stream", "fear", "sight", "thin", "triangle", "planet", "hurry", "chief", "colony", "clock", "mine", "tie", "enter", "major", "fresh", "search", "send", "yellow", "gun", "allow", "print", "dead", "spot", "desert", "suit", "current", "lift", "rose", "continue", "block", "chart", "hat", "sell", "success", "company", "subtract", "event", "particular", "deal", "swim", "term", "opposite", "wife", "shoe", "shoulder", "spread", "arrange", "camp", "invent", "cotton", "born", "determine", "quart", "nine", "truck", "noise", "level", "chance", "gather", "shop", "stretch", "throw", "shine", "property", "column", "molecule", "select", "wrong", "gray", "repeat", "require", "broad", "prepare", "salt", "nose", "plural", "anger", "claim", "continent", "oxygen", "sugar", "death", "pretty", "skill", "women", "season", "solution", "magnet", "silver", "thank", "branch", "match", "suffix", "especially", "fig", "afraid", "huge", "sister", "steel", "discuss", "forward", "similar", "guide", "experience", "score", "apple", "bought", "led", "pitch", "coat", "mass", "card", "band", "rope", "slip", "win", "dream", "evening", "condition", "feed", "tool", "total", "basic", "smell", "valley", "nor", "double", "seat", "arrive", "master", "track", "parent", "shore", "division", "sheet", "substance", "favor", "connect", "post", "spend", "chord", "fat", "glad", "original", "share", "station", "dad", "bread", "charge", "proper", "bar", "offer", "segment", "slave", "duck", "instant", "market", "degree", "populate", "chick", "dear", "enemy", "reply", "drink", "occur", "support", "speech", "nature", "range", "steam", "motion", "path", "liquid", "log", "meant", "quotient", "teeth", "shell", "neck"
        }

        # Filtrar palavras significativas
        keywords = []
        for word in words:
            if word not in stop_words and len(word) > 2:
                keywords.append(word)

        # Adicionar sinônimos
        expanded_keywords = set(keywords)
        for keyword in keywords:
            for main_term, synonyms in synonym_map.items():
                if keyword in main_term or keyword in synonyms:
                    expanded_keywords.update(synonyms)
                    expanded_keywords.add(main_term)

        # Remover duplicatas e limitar
        final_keywords = list(expanded_keywords)[:15]  # Limitar para evitar consultas muito complexas

        logger.info(f"Palavras-chave extraídas: {final_keywords[:10]}...")
        return final_keywords

    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Pesquisa na web usando a API Serper."""
        cache_key = self._get_cache_key("web", query, num_results=num_results)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

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
            'timeRange': 'last12m'
        }

        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                search_results = response.json()
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

                self._set_cache(cache_key, formatted_results)
                return formatted_results
            else:
                logger.error(f"Erro na pesquisa Serper: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Erro em search_web: {e}")
            return []

    def search_producthunt(self, query: str, max_results: int = 5, context: str = "") -> List[Dict[str, Any]]:
        """
        Pesquisa melhorada no Product Hunt com múltiplas estratégias.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            context: Contexto adicional para melhorar a relevância

        Returns:
            Lista de resultados do Product Hunt
        """
        cache_key = self._get_cache_key("producthunt", query, max_results=max_results, context=context[:100])
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        if not self.producthunt_available:
            logger.warning("API do Product Hunt não disponível. Retornando lista vazia.")
            return []

        # Extrair palavras-chave de forma inteligente
        keywords = self._extract_keywords_smart(query, context)
        logger.info(f"Pesquisando no Product Hunt com palavras-chave: {keywords[:5]}...")

        # Tentar múltiplas estratégias de busca
        strategies = [
            self._search_producthunt_by_topics,
            self._search_producthunt_recent_with_filter,
            self._search_producthunt_popular_with_filter
        ]

        all_results = []

        for strategy in strategies:
            try:
                strategy_results = strategy(keywords, max_results, context)
                if strategy_results:
                    all_results.extend(strategy_results)
                    logger.info(f"Estratégia {strategy.__name__} retornou {len(strategy_results)} resultados")
                else:
                    logger.info(f"Estratégia {strategy.__name__} não retornou resultados")
            except Exception as e:
                logger.error(f"Erro na estratégia {strategy.__name__}: {e}")
                continue

        # Remover duplicatas baseado na URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result.get('url') and result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)

        # Ordenar por relevância e limitar resultados
        final_results = self._rank_producthunt_results(unique_results, keywords)[:max_results]

        self._set_cache(cache_key, final_results)
        logger.info(f"Product Hunt retornou {len(final_results)} resultados finais")
        return final_results

    def _search_producthunt_by_topics(self, keywords: List[str], max_results: int, context: str) -> List[Dict[str, Any]]:
        """Busca no Product Hunt usando tópicos/tags."""
        if not self.producthunt_token:
            self._get_producthunt_token()

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.producthunt_token}',
            'User-Agent': 'FourSight Innovation System/1.0'
        }

        # Consulta GraphQL para buscar por tópicos
        topics_to_search = []

        # Mapear palavras-chave para tópicos conhecidos do Product Hunt
        topic_mapping = {
            'ai': 'artificial-intelligence',
            'artificial intelligence': 'artificial-intelligence',
            'machine learning': 'artificial-intelligence',
            'blockchain': 'blockchain',
            'crypto': 'cryptocurrency',
            'health': 'health-fitness',
            'healthcare': 'health-fitness',
            'medical': 'health-fitness',
            'finance': 'finance',
            'fintech': 'finance',
            'productivity': 'productivity',
            'education': 'education',
            'ecommerce': 'e-commerce',
            'social': 'social-media',
            'design': 'design-tools',
            'developer': 'developer-tools',
            'marketing': 'marketing',
            'analytics': 'analytics'
        }

        for keyword in keywords:
            keyword_lower = keyword.lower()
            for key, topic in topic_mapping.items():
                if key in keyword_lower:
                    topics_to_search.append(topic)

        if not topics_to_search:
            # Se não encontrou tópicos específicos, usar tópicos genéricos
            topics_to_search = ['artificial-intelligence', 'productivity', 'tech']

        # Remover duplicatas
        topics_to_search = list(set(topics_to_search))[:3]  # Limitar a 3 tópicos

        results = []
        for topic in topics_to_search:
            graphql_query = f'''
            {{
              topic(slug: "{topic}") {{
                posts(first: 10, order: NEWEST) {{
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
                      topics(first: 5) {{
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
            }}
            '''

            try:
                response = requests.post(
                    'https://api.producthunt.com/v2/api/graphql',
                    headers=headers,
                    json={'query': graphql_query},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data'] and 'topic' in data['data'] and data['data']['topic']:
                        posts = data['data']['topic']['posts']['edges']
                        for edge in posts:
                            result = self._format_producthunt_result(edge['node'])
                            if result:
                                results.append(result)

                # Pequena pausa entre requisições
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Erro ao buscar tópico {topic}: {e}")
                continue

        return results

    def _search_producthunt_recent_with_filter(self, keywords: List[str], max_results: int, context: str) -> List[Dict[str, Any]]:
        """Busca posts recentes e filtra por relevância."""
        if not self.producthunt_token:
            self._get_producthunt_token()

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.producthunt_token}',
            'User-Agent': 'FourSight Innovation System/1.0'
        }

        # Buscar posts mais recentes
        graphql_query = '''
        {
          posts(first: 30, order: NEWEST) {
            edges {
              node {
                id
                name
                tagline
                description
                url
                votesCount
                commentsCount
                createdAt
                website
                topics(first: 5) {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        '''

        try:
            response = requests.post(
                'https://api.producthunt.com/v2/api/graphql',
                headers=headers,
                json={'query': graphql_query},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'posts' in data['data']:
                    posts = data['data']['posts']['edges']
                    results = []

                    for edge in posts:
                        result = self._format_producthunt_result(edge['node'])
                        if result and self._is_producthunt_result_relevant(result, keywords):
                            results.append(result)

                    return results

        except Exception as e:
            logger.error(f"Erro na busca recente do Product Hunt: {e}")

        return []

    def _search_producthunt_popular_with_filter(self, keywords: List[str], max_results: int, context: str) -> List[Dict[str, Any]]:
        """Busca posts populares e filtra por relevância."""
        if not self.producthunt_token:
            self._get_producthunt_token()

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.producthunt_token}',
            'User-Agent': 'FourSight Innovation System/1.0'
        }

        # Buscar posts populares
        graphql_query = '''
        {
          posts(first: 30, order: VOTES) {
            edges {
              node {
                id
                name
                tagline
                description
                url
                votesCount
                commentsCount
                createdAt
                website
                topics(first: 5) {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        '''

        try:
            response = requests.post(
                'https://api.producthunt.com/v2/api/graphql',
                headers=headers,
                json={'query': graphql_query},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'posts' in data['data']:
                    posts = data['data']['posts']['edges']
                    results = []

                    for edge in posts:
                        result = self._format_producthunt_result(edge['node'])
                        if result and self._is_producthunt_result_relevant(result, keywords):
                            results.append(result)

                    return results

        except Exception as e:
            logger.error(f"Erro na busca popular do Product Hunt: {e}")

        return []

    def _format_producthunt_result(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Formata um resultado do Product Hunt."""
        try:
            # Extrair tópicos
            topics = []
            if 'topics' in node and 'edges' in node['topics']:
                for topic_edge in node['topics']['edges']:
                    topics.append(topic_edge['node']['name'])

            # Converter data
            created_at = node.get('createdAt', '')
            created_date = created_at.split('T')[0] if created_at else ''

            # Construir snippet
            tagline = node.get('tagline', '')
            description = node.get('description', '')
            snippet = tagline
            if description and description != tagline:
                snippet += f"\n\n{description[:200]}..."

            return {
                'title': node.get('name', 'Sem nome'),
                'url': node.get('url', ''),
                'website': node.get('website', ''),
                'snippet': snippet,
                'created_date': created_date,
                'votes': node.get('votesCount', 0),
                'comments': node.get('commentsCount', 0),
                'topics': topics,
                'source': 'Product Hunt',
                'type': 'product'
            }
        except Exception as e:
            logger.error(f"Erro ao formatar resultado do Product Hunt: {e}")
            return None

    def _translate_to_english(self, text: str) -> str:
        """
        Traduz texto do português para o inglês de forma simples e confiável.

        Args:
            text: Texto para traduzir

        Returns:
            Texto traduzido para inglês
        """
        # Verificar se o texto já parece estar em inglês
        english_indicators = ['the', 'and', 'of', 'to', 'in', 'for', 'on', 'with', 'at', 'by', 'from']
        text_lower = text.lower()

        # Se o texto contém várias palavras comuns em inglês, provavelmente já está em inglês
        english_word_count = sum(1 for word in english_indicators if f" {word} " in f" {text_lower} ")
        if english_word_count >= 2 or len(text.split()) <= 1:
            return text

        # Mapeamento direto de frases comuns (do mais específico para o mais geral)
        direct_translations = {
            "inteligência artificial na educação": "artificial intelligence in education",
            "inteligencia artificial na educacao": "artificial intelligence in education",
            "inteligência artificial na saúde": "artificial intelligence in healthcare",
            "inteligencia artificial na saude": "artificial intelligence in healthcare",
            "inteligência artificial": "artificial intelligence",
            "inteligencia artificial": "artificial intelligence",
            "aprendizado de máquina": "machine learning",
            "aprendizado de maquina": "machine learning",
            "aprendizagem profunda": "deep learning",
            "blockchain na saúde": "blockchain in healthcare",
            "blockchain na saude": "blockchain in healthcare",
            "saúde digital": "digital health",
            "saude digital": "digital health",
            "educação": "education",
            "educacao": "education",
            "saúde": "health",
            "saude": "health",
            "tecnologia educacional": "educational technology",
            "edtech": "edtech",
            "personalização": "personalization",
            "personalizacao": "personalization",
            "aprendizagem adaptativa": "adaptive learning",
            "tutoria automatizada": "automated tutoring",
            "análise de dados educacionais": "educational data analysis",
            "analise de dados educacionais": "educational data analysis"
        }

        # Tentar tradução direta primeiro
        for pt_phrase, en_phrase in direct_translations.items():
            if pt_phrase in text_lower:
                # Substituir preservando maiúsculas/minúsculas
                pattern = re.compile(re.escape(pt_phrase), re.IGNORECASE)
                text = pattern.sub(en_phrase, text)
                logger.info(f"Tradução direta aplicada: '{pt_phrase}' -> '{en_phrase}'")

        # Tradução simplificada para consultas comuns
        common_queries = {
            "inteligência artificial": "artificial intelligence",
            "inteligencia artificial": "artificial intelligence",
            "ia na educação": "ai in education",
            "ia na educacao": "ai in education",
            "ia na saúde": "ai in healthcare",
            "ia na saude": "ai in healthcare",
            "blockchain": "blockchain",
            "machine learning": "machine learning",
            "deep learning": "deep learning",
            "educação online": "online education",
            "educacao online": "online education",
            "ensino a distância": "distance learning",
            "ensino a distancia": "distance learning"
        }

        for pt_query, en_query in common_queries.items():
            if pt_query in text_lower:
                pattern = re.compile(re.escape(pt_query), re.IGNORECASE)
                text = pattern.sub(en_query, text)

        # Tradução palavra por palavra apenas para palavras-chave importantes
        word_translations = {
            "educação": "education",
            "educacao": "education",
            "saúde": "health",
            "saude": "health",
            "tecnologia": "technology",
            "inovação": "innovation",
            "inovacao": "innovation",
            "personalizada": "personalized",
            "personalizado": "personalized",
            "aprendizagem": "learning",
            "ensino": "teaching",
            "aluno": "student",
            "alunos": "students",
            "professor": "teacher",
            "professores": "teachers",
            "escola": "school",
            "universidade": "university",
            "curso": "course",
            "avaliação": "assessment",
            "avaliacao": "assessment",
            "desempenho": "performance",
            "conteúdo": "content",
            "conteudo": "content",
            "digital": "digital",
            "online": "online",
            "virtual": "virtual",
            "remoto": "remote",
            "remota": "remote",
            "plataforma": "platform",
            "sistema": "system",
            "ferramenta": "tool",
            "aplicativo": "app",
            "aplicação": "application",
            "aplicacao": "application",
            "dados": "data",
            "análise": "analysis",
            "analise": "analysis",
            "pesquisa": "research",
            "estudo": "study",
            "método": "method",
            "metodo": "method"
        }

        # Aplicar traduções de palavras individuais
        words = text.split()
        translated_words = []

        for word in words:
            word_lower = word.lower()
            translated = False

            # Verificar se a palavra está no dicionário de traduções
            for pt_word, en_word in word_translations.items():
                if word_lower == pt_word or word_lower == pt_word + 's':
                    # Preservar maiúsculas/minúsculas
                    if word[0].isupper():
                        translated_words.append(en_word.capitalize())
                    else:
                        translated_words.append(en_word)
                    translated = True
                    break

            # Se não encontrou tradução, manter a palavra original
            if not translated:
                translated_words.append(word)

        translated_text = ' '.join(translated_words)

        # Verificar se a tradução realmente mudou algo
        if translated_text == text:
            # Se não mudou nada, tentar uma abordagem mais simples para consultas comuns
            if "inteligência artificial" in text_lower or "inteligencia artificial" in text_lower:
                if "educação" in text_lower or "educacao" in text_lower:
                    translated_text = "artificial intelligence in education"
                elif "saúde" in text_lower or "saude" in text_lower:
                    translated_text = "artificial intelligence in healthcare"
                else:
                    translated_text = "artificial intelligence"
            elif "blockchain" in text_lower:
                if "saúde" in text_lower or "saude" in text_lower:
                    translated_text = "blockchain in healthcare"
                else:
                    translated_text = "blockchain technology"

        logger.info(f"Texto traduzido: '{text}' -> '{translated_text}'")
        return translated_text

    def _is_producthunt_result_relevant(self, result: Dict[str, Any], keywords: List[str]) -> bool:
        """Verifica se um resultado do Product Hunt é relevante."""
        # Texto para análise
        search_text = (
            result.get('title', '').lower() + ' ' +
            result.get('snippet', '').lower() + ' ' +
            ' '.join(result.get('topics', [])).lower()
        )

        # Contar correspondências de palavras-chave
        matches = 0
        for keyword in keywords:
            if keyword.lower() in search_text:
                matches += 1

        # Considerar relevante se tiver pelo menos uma correspondência
        # ou se tiver tópicos relevantes
        if matches > 0:
            return True

        # Verificar tópicos especiais
        topics = [t.lower() for t in result.get('topics', [])]
        relevant_topics = ['artificial intelligence', 'ai', 'machine learning', 'blockchain', 'health', 'productivity']

        for topic in topics:
            if any(rel_topic in topic for rel_topic in relevant_topics):
                return True

        return False

    def _rank_producthunt_results(self, results: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """Classifica resultados do Product Hunt por relevância."""
        for result in results:
            score = 0

            # Texto para análise
            search_text = (
                result.get('title', '').lower() + ' ' +
                result.get('snippet', '').lower() + ' ' +
                ' '.join(result.get('topics', [])).lower()
            )

            # Pontuação por palavra-chave encontrada
            for keyword in keywords:
                if keyword.lower() in search_text:
                    score += 1
                    # Bônus se estiver no título
                    if keyword.lower() in result.get('title', '').lower():
                        score += 2

            # Bônus por popularidade (normalizado)
            votes = result.get('votes', 0)
            if votes > 0:
                score += min(votes / 100, 5)  # Máximo de 5 pontos extras

            # Bônus por data recente
            created_date = result.get('created_date', '')
            if created_date:
                try:
                    date_obj = datetime.strptime(created_date, '%Y-%m-%d')
                    days_old = (datetime.now() - date_obj).days
                    if days_old < 30:  # Posts dos últimos 30 dias
                        score += 3
                    elif days_old < 90:  # Posts dos últimos 90 dias
                        score += 1
                except:
                    pass

            result['relevance_score'] = score

        # Ordenar por pontuação de relevância
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)

    def _get_producthunt_token(self) -> bool:
        """Obtém token de autenticação para a API do Product Hunt."""
        load_dotenv(override=True)
        self.producthunt_api_key = os.getenv("PRODUCTHUNT_API_KEY", "")
        self.producthunt_available = bool(self.producthunt_api_key)

        if not self.producthunt_available:
            logger.warning("Chave de API do Product Hunt não configurada")
            return False

        self.producthunt_token = self.producthunt_api_key
        logger.info("Token do Product Hunt configurado")
        return True

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
        cache_key = self._get_cache_key("arxiv", query, max_results=max_results, context=context[:100])
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        # Traduzir a consulta para inglês (arXiv funciona melhor com consultas em inglês)
        english_query = self._translate_to_english(query)

        # Traduzir o contexto se fornecido
        english_context = self._translate_to_english(context) if context else ""

        logger.info(f"Consulta traduzida para arXiv: '{query}' -> '{english_query}'")

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

        # Construir consulta aprimorada incorporando termos-chave do contexto
        # Adicionar restrição de data para artigos recentes (últimos 3 anos)
        date_constraint = f" AND submittedDate:[{current_year-3} TO {current_year}]"

        # Formatar consulta para a API do arXiv
        query_lower = english_query.lower()

        # Mapeamento de consultas específicas para melhorar a relevância
        if ("artificial intelligence" in query_lower or "ai" in query_lower.split()) and any(term in query_lower for term in ["education", "learning", "teaching", "student", "school"]):
            # Consulta específica para IA na educação
            formatted_query = f'(ti:"artificial intelligence" OR ti:"machine learning") AND (ti:education OR ti:learning OR ti:teaching OR ti:educational OR abs:education OR abs:learning OR abs:teaching OR abs:educational){date_constraint}'
            logger.info("Usando consulta específica para IA na educação")

        elif ("artificial intelligence" in query_lower or "ai" in query_lower.split()) and any(term in query_lower for term in ["health", "healthcare", "medical", "medicine", "clinical"]):
            # Consulta específica para IA na saúde
            formatted_query = f'(ti:"artificial intelligence" OR ti:"machine learning") AND (ti:health OR ti:healthcare OR ti:medical OR abs:health OR abs:healthcare OR abs:medical){date_constraint}'
            logger.info("Usando consulta específica para IA na saúde")

        elif ("blockchain" in query_lower) and any(term in query_lower for term in ["health", "healthcare", "medical"]):
            # Consulta específica para blockchain na saúde
            formatted_query = f'ti:blockchain AND (ti:health OR ti:healthcare OR ti:medical OR abs:health OR abs:healthcare OR abs:medical){date_constraint}'
            logger.info("Usando consulta específica para blockchain na saúde")

        elif "artificial intelligence" in query_lower or "ai" in query_lower.split():
            # Consulta genérica para IA
            formatted_query = f'(ti:"artificial intelligence" OR ti:"machine learning" OR ti:ai){date_constraint}'
            logger.info("Usando consulta genérica para IA")

        elif "education" in query_lower or "learning" in query_lower:
            # Consulta genérica para educação
            formatted_query = f'(ti:education OR ti:learning OR ti:"educational technology"){date_constraint}'
            logger.info("Usando consulta genérica para educação")

        else:
            # Para outras consultas, usar termos principais
            # Extrair termos principais da consulta (até 3 termos)
            main_query_terms = []
            for term in english_query.split():
                if len(term) > 3 and term.lower() not in ["with", "from", "that", "this", "these", "those", "have", "been"]:
                    main_query_terms.append(term)
                if len(main_query_terms) >= 3:
                    break

            # Construir consulta
            if main_query_terms:
                # Usar OR entre os termos para aumentar a chance de resultados
                query_part = " OR ".join([f'ti:"{term}" OR abs:"{term}"' for term in main_query_terms])
                formatted_query = f'({query_part}){date_constraint}'
            else:
                # Fallback para consulta simples
                formatted_query = f'(ti:"{english_query}" OR abs:"{english_query}"){date_constraint}'

            logger.info("Usando consulta genérica")

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
            response = requests.get(base_url, params=params, timeout=15)

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

                # Armazenar em cache e retornar
                self._set_cache(cache_key, papers)
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

    def search_reddit(self, query: str, max_results: int = 5, time_filter: str = "year") -> List[Dict[str, Any]]:
        """
        Pesquisa no Reddit usando múltiplas abordagens para garantir resultados.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            time_filter: Filtro de tempo ('hour', 'day', 'week', 'month', 'year', 'all')

        Returns:
            Lista de resultados do Reddit
        """
        cache_key = self._get_cache_key("reddit", query, max_results=max_results, time_filter=time_filter)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        try:
            # Traduzir a consulta para inglês para melhores resultados
            english_query = self._translate_to_english(query)
            logger.info(f"Pesquisando no Reddit: {english_query}")

            # Tentar múltiplas abordagens para garantir resultados
            all_results = []

            # Abordagem 1: Pesquisa direta com subreddits específicos
            direct_results = self._search_reddit_direct(english_query, max_results, time_filter)
            if direct_results:
                all_results.extend(direct_results)
                logger.info(f"Abordagem direta encontrou {len(direct_results)} resultados")

            # Abordagem 2: Pesquisa por tópicos populares relacionados
            if len(all_results) < max_results:
                topic_results = self._search_reddit_by_topics(english_query, max_results - len(all_results), time_filter)
                if topic_results:
                    all_results.extend(topic_results)
                    logger.info(f"Abordagem por tópicos encontrou {len(topic_results)} resultados")

            # Abordagem 3: Fallback para pesquisa geral se ainda não tiver resultados suficientes
            if len(all_results) < max_results:
                fallback_results = self._search_reddit_fallback(english_query, max_results - len(all_results), time_filter)
                if fallback_results:
                    all_results.extend(fallback_results)
                    logger.info(f"Abordagem fallback encontrou {len(fallback_results)} resultados")

            # Remover duplicatas baseado na URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                if result.get('url') and result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)

            # Limitar ao número máximo de resultados
            final_results = unique_results[:max_results]

            logger.info(f"Encontrados {len(final_results)} resultados do Reddit no total")

            # Armazenar em cache e retornar
            self._set_cache(cache_key, final_results)
            return final_results

        except Exception as e:
            logger.error(f"Erro em search_reddit: {e}")
            return []

    def _search_reddit_direct(self, query: str, max_results: int, time_filter: str) -> List[Dict[str, Any]]:
        """Pesquisa direta no Reddit com subreddits específicos."""
        try:
            # Refinar a consulta para melhorar os resultados
            refined_query = query

            # Adicionar subreddits relevantes para consultas específicas
            subreddit_param = ""

            query_lower = query.lower()
            if "artificial intelligence" in query_lower or "ai" in query_lower.split():
                if "education" in query_lower or "learning" in query_lower:
                    # IA na educação
                    subreddit_param = "subreddit:artificial+subreddit:MachineLearning+subreddit:education+subreddit:edtech+subreddit:OnlineCourses"
                    refined_query = "AI education learning"
                elif "health" in query_lower or "healthcare" in query_lower or "medical" in query_lower:
                    # IA na saúde
                    subreddit_param = "subreddit:artificial+subreddit:MachineLearning+subreddit:HealthTech+subreddit:medicine+subreddit:healthcare"
                    refined_query = "AI healthcare medical"
                else:
                    # IA geral
                    subreddit_param = "subreddit:artificial+subreddit:MachineLearning+subreddit:AINews+subreddit:singularity"
                    refined_query = "artificial intelligence"
            elif "blockchain" in query_lower or "crypto" in query_lower:
                # Blockchain
                subreddit_param = "subreddit:CryptoTechnology+subreddit:blockchain+subreddit:CryptoCurrency"
                refined_query = "blockchain technology"
            elif "education" in query_lower or "learning" in query_lower or "teaching" in query_lower:
                # Educação
                subreddit_param = "subreddit:education+subreddit:edtech+subreddit:OnlineCourses+subreddit:teaching"
                refined_query = "education technology"

            # Construir a consulta final
            final_query = refined_query
            if subreddit_param:
                final_query = f"{subreddit_param} {refined_query}"

            logger.info(f"Consulta refinada para Reddit (direta): {final_query}")

            # Usar a API do Reddit para pesquisa
            reddit_url = "https://www.reddit.com/search.json"

            # Parâmetros de pesquisa
            params = {
                'q': final_query,
                'sort': 'relevance',
                't': time_filter,
                'limit': max_results * 3,  # Solicitar mais resultados para filtrar depois
                'include_over_18': 'off'   # Excluir conteúdo adulto
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }

            response = requests.get(reddit_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()

                if 'data' in data and 'children' in data['data']:
                    posts = data['data']['children']
                    return self._format_reddit_results(posts, max_results, query)

            return []

        except Exception as e:
            logger.error(f"Erro na pesquisa direta do Reddit: {e}")
            return []

    def _search_reddit_by_topics(self, query: str, max_results: int, time_filter: str) -> List[Dict[str, Any]]:
        """Pesquisa no Reddit por tópicos populares relacionados."""
        try:
            # Extrair palavras-chave da consulta
            keywords = [word for word in query.lower().split() if len(word) > 3]

            # Mapear para subreddits populares relacionados a tópicos comuns
            topic_subreddits = {
                "ai": ["artificial", "MachineLearning", "AINews", "singularity", "deeplearning"],
                "intelligence": ["artificial", "MachineLearning", "AINews", "singularity", "deeplearning"],
                "artificial": ["artificial", "MachineLearning", "AINews", "singularity", "deeplearning"],
                "machine": ["MachineLearning", "artificial", "deeplearning", "datascience"],
                "learning": ["MachineLearning", "learnprogramming", "education", "OnlineCourses"],
                "education": ["education", "edtech", "OnlineCourses", "teaching", "learnprogramming"],
                "health": ["HealthTech", "medicine", "healthcare", "Health", "medical"],
                "healthcare": ["healthcare", "medicine", "HealthTech", "medical"],
                "medical": ["medicine", "healthcare", "medical", "HealthTech"],
                "blockchain": ["CryptoTechnology", "blockchain", "CryptoCurrency", "Bitcoin"],
                "crypto": ["CryptoCurrency", "CryptoTechnology", "Bitcoin", "blockchain"],
                "technology": ["technology", "tech", "Futurology", "gadgets"],
                "innovation": ["Futurology", "technology", "tech", "startups"],
                "business": ["business", "startups", "Entrepreneur", "smallbusiness"],
                "programming": ["programming", "learnprogramming", "webdev", "coding"],
                "data": ["datascience", "MachineLearning", "bigdata", "analytics"]
            }

            # Coletar subreddits relevantes
            relevant_subreddits = set()
            for keyword in keywords:
                if keyword in topic_subreddits:
                    relevant_subreddits.update(topic_subreddits[keyword])

            # Se não encontrou subreddits específicos, usar alguns genéricos
            if not relevant_subreddits:
                relevant_subreddits = {"technology", "Futurology", "science", "tech"}

            # Limitar a 5 subreddits para não sobrecarregar a consulta
            subreddits_to_search = list(relevant_subreddits)[:5]

            # Construir a consulta
            subreddit_param = "+".join([f"subreddit:{sr}" for sr in subreddits_to_search])

            # Usar termos mais genéricos para aumentar a chance de resultados
            generic_terms = "technology innovation future trends"

            final_query = f"{subreddit_param} {generic_terms}"

            logger.info(f"Consulta por tópicos para Reddit: {final_query}")

            # Fazer a requisição
            reddit_url = "https://www.reddit.com/search.json"

            params = {
                'q': final_query,
                'sort': 'relevance',
                't': time_filter,
                'limit': max_results * 2,
                'include_over_18': 'off'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }

            response = requests.get(reddit_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()

                if 'data' in data and 'children' in data['data']:
                    posts = data['data']['children']
                    return self._format_reddit_results(posts, max_results, query)

            return []

        except Exception as e:
            logger.error(f"Erro na pesquisa por tópicos do Reddit: {e}")
            return []

    def _search_reddit_fallback(self, query: str, max_results: int, time_filter: str = "year") -> List[Dict[str, Any]]:
        """
        Pesquisa fallback no Reddit para garantir resultados.

        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            time_filter: Filtro de tempo (ignorado, sempre usa 'year' para maximizar resultados)
        """
        try:
            # Simplificar a consulta para termos mais genéricos
            query_terms = query.lower().split()
            simplified_query = ""

            # Usar apenas os termos mais relevantes
            important_terms = ["ai", "artificial", "intelligence", "machine", "learning",
                              "blockchain", "health", "healthcare", "education", "technology"]

            for term in important_terms:
                if term in query_terms:
                    simplified_query += term + " "

            # Se não encontrou termos importantes, usar a consulta original
            if not simplified_query:
                simplified_query = query

            # Adicionar termos genéricos para aumentar a chance de resultados
            final_query = f"{simplified_query} reddit:technology"

            logger.info(f"Consulta fallback para Reddit: {final_query}")

            # Fazer a requisição
            reddit_url = "https://www.reddit.com/search.json"

            # Ignorar o time_filter passado e sempre usar 'year' para maximizar resultados
            params = {
                'q': final_query,
                'sort': 'top',  # Usar 'top' para encontrar posts populares
                't': 'year',    # Sempre usar 'year' para o fallback para ter mais resultados
                'limit': max_results * 2,
                'include_over_18': 'off'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }

            response = requests.get(reddit_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                try:
                    data = response.json()

                    if 'data' in data and 'children' in data['data']:
                        posts = data['data']['children']
                        return self._format_reddit_results(posts, max_results, query)
                except Exception as json_error:
                    logger.error(f"Erro ao processar JSON do Reddit: {json_error}")

            # Última tentativa: usar a API de pesquisa do Reddit sem filtros
            final_query = "technology OR innovation OR future"

            params = {
                'q': final_query,
                'sort': 'relevance',
                't': 'year',
                'limit': max_results * 2,
                'include_over_18': 'off'
            }

            response = requests.get(reddit_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                try:
                    data = response.json()

                    if 'data' in data and 'children' in data['data']:
                        posts = data['data']['children']
                        return self._format_reddit_results(posts, max_results, "technology innovation future")
                except Exception as json_error:
                    logger.error(f"Erro ao processar JSON do Reddit (última tentativa): {json_error}")

            return []

        except Exception as e:
            logger.error(f"Erro na pesquisa fallback do Reddit: {e}")
            return []

    def _format_reddit_results(self, posts: List[Dict[str, Any]], max_results: int, original_query: str = None) -> List[Dict[str, Any]]:
        """
        Formata e filtra os resultados do Reddit em um formato padronizado.

        Args:
            posts: Lista de posts do Reddit
            max_results: Número máximo de resultados
            original_query: Consulta original para filtrar por relevância

        Returns:
            Lista de resultados formatados e filtrados
        """
        formatted_results = []

        # Usar a consulta original para filtrar resultados por relevância
        query_terms = set()
        if original_query:
            # Extrair termos significativos da consulta
            query_terms = {term.lower() for term in original_query.split() if len(term) > 3}

        for post_data in posts:
            if 'data' not in post_data:
                continue

            post = post_data['data']

            # Extrair texto do post
            title = post.get('title', '')
            selftext = post.get('selftext', '')
            snippet = selftext if selftext else title

            # Truncar snippet se for muito longo
            if len(snippet) > 500:
                snippet = snippet[:497] + "..."

            # Converter timestamp para data legível
            created_utc = post.get('created_utc', 0)
            created_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')

            # Calcular pontuação de relevância
            relevance_score = self._calculate_reddit_relevance(title, snippet, post.get('subreddit', ''), query_terms)

            # Adicionar ao resultado
            formatted_results.append({
                'title': title,
                'url': f"https://www.reddit.com{post.get('permalink', '')}",
                'snippet': snippet,
                'created_date': created_date,
                'subreddit': post.get('subreddit', ''),
                'score': post.get('score', 0),
                'num_comments': post.get('num_comments', 0),
                'relevance': relevance_score,
                'source': 'Reddit',
                'type': 'social'
            })

        # Ordenar por relevância e depois por pontuação
        sorted_results = sorted(formatted_results, key=lambda x: (x['relevance'], x['score']), reverse=True)

        # Filtrar resultados com baixa relevância
        filtered_results = [r for r in sorted_results if r['relevance'] > 0.3]

        # Se não houver resultados suficientes após a filtragem, usar os melhores disponíveis
        if len(filtered_results) < max_results // 2:
            filtered_results = sorted_results

        # Limitar ao número máximo de resultados
        return filtered_results[:max_results]

    def _calculate_reddit_relevance(self, title: str, content: str, subreddit: str, query_terms: set) -> float:
        """
        Calcula a pontuação de relevância de um post do Reddit.

        Args:
            title: Título do post
            content: Conteúdo do post
            subreddit: Subreddit do post
            query_terms: Termos da consulta original

        Returns:
            Pontuação de relevância entre 0 e 1
        """
        # Se não há termos de consulta, não podemos calcular relevância específica
        if not query_terms:
            return 0.5  # Valor neutro

        # Converter para minúsculas para comparação
        title_lower = title.lower()
        content_lower = content.lower()
        subreddit_lower = subreddit.lower()

        # Pontuação base
        score = 0.0

        # Dicionário de subreddits relevantes por tópico
        relevant_subreddits = {
            "ai": ["artificial", "machinelearning", "ainews", "singularity", "deeplearning", "datascience"],
            "intelligence": ["artificial", "machinelearning", "ainews", "singularity", "deeplearning"],
            "education": ["education", "edtech", "onlinecourses", "teaching", "learnprogramming"],
            "health": ["healthtech", "medicine", "healthcare", "health", "medical"],
            "blockchain": ["cryptotechnology", "blockchain", "cryptocurrency", "bitcoin"],
            "technology": ["technology", "tech", "futurology", "gadgets"]
        }

        # Verificar se o subreddit é relevante para algum dos termos da consulta
        for term in query_terms:
            if term in relevant_subreddits:
                if subreddit_lower in relevant_subreddits[term]:
                    score += 0.3
                    break

        # Verificar correspondência no título (mais importante)
        title_matches = sum(1 for term in query_terms if term in title_lower)
        if title_matches > 0:
            score += 0.4 * (title_matches / len(query_terms))

        # Verificar correspondência no conteúdo
        content_matches = sum(1 for term in query_terms if term in content_lower)
        if content_matches > 0:
            score += 0.2 * (content_matches / len(query_terms))

        # Verificar frases exatas (correspondência mais forte)
        for i in range(len(query_terms) - 1):
            phrase = " ".join(list(query_terms)[i:i+2])
            if len(phrase) > 5:  # Apenas frases significativas
                if phrase in title_lower:
                    score += 0.2
                if phrase in content_lower:
                    score += 0.1

        # Penalizar posts muito genéricos ou com pouco conteúdo
        if len(content) < 50 and title_matches == 0:
            score -= 0.2

        # Verificar palavras-chave específicas que indicam conteúdo de qualidade
        quality_indicators = ["research", "study", "analysis", "report", "survey", "data", "statistics",
                             "expert", "professional", "official", "review", "comparison", "guide"]

        quality_matches = sum(1 for indicator in quality_indicators if indicator in title_lower or indicator in content_lower)
        if quality_matches > 0:
            score += 0.1 * min(quality_matches, 3) / 3  # Limitar a 0.1

        # Limitar a pontuação entre 0 e 1
        return max(0.0, min(1.0, score))

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
        logger.info(f"Obtendo contexto para: '{query}' com contexto: '{context[:100]}...'")

        # Resultados de cada fonte com tratamento de erro individual
        results = {}

        # Web
        try:
            web_results = self.search_web(query, max_results)
            results['web'] = web_results
            logger.info(f"Web: {len(web_results)} resultados")
        except Exception as e:
            logger.error(f"Erro ao buscar resultados da web: {e}")
            results['web'] = []

        # arXiv
        try:
            arxiv_results = self.search_arxiv(query, max_results, context)
            results['arxiv'] = arxiv_results
            logger.info(f"arXiv: {len(arxiv_results)} resultados")
        except Exception as e:
            logger.error(f"Erro ao buscar resultados do arXiv: {e}")
            results['arxiv'] = []

        # Reddit
        try:
            reddit_results = self.search_reddit(query, max_results)
            results['reddit'] = reddit_results
            logger.info(f"Reddit: {len(reddit_results)} resultados")
        except Exception as e:
            logger.error(f"Erro ao buscar resultados do Reddit: {e}")
            results['reddit'] = []

        # Product Hunt - com contexto melhorado
        try:
            producthunt_results = self.search_producthunt(query, max_results, context)
            results['producthunt'] = producthunt_results
            logger.info(f"Product Hunt: {len(producthunt_results)} resultados")
        except Exception as e:
            logger.error(f"Erro ao buscar resultados do Product Hunt: {e}")
            results['producthunt'] = []

        # Combinar resultados
        all_results = []
        for source_results in results.values():
            all_results.extend(source_results)

        results['all'] = all_results

        total_results = len(all_results)
        logger.info(f"Total de resultados obtidos: {total_results}")

        return results

# Instância global para uso em todo o projeto
mcp = ModelContextProtocol()