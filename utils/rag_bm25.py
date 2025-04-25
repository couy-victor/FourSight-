"""
Implementação de RAG com BM25 para o sistema de inovação.
Combina busca semântica (embeddings) com busca léxica (BM25) para melhorar a relevância dos resultados.
"""

import os
import re
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple

# NumPy será importado condicionalmente mais tarde para evitar erros

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("RAG_BM25")

try:
    try:
        from rank_bm25 import BM25Okapi
        from sentence_transformers import SentenceTransformer
        from pypdf import PdfReader
        import numpy as np
        BM25_AVAILABLE = True
    except ValueError as ve:
        # Capturar especificamente o erro de incompatibilidade do NumPy
        if "numpy.dtype size changed" in str(ve):
            logger.warning("Detectada incompatibilidade de versão do NumPy. Desativando RAG BM25.")
            BM25_AVAILABLE = False
        else:
            raise
except ImportError:
    logger.warning("Bibliotecas para RAG BM25 não encontradas. Usando fallback simples.")
    BM25_AVAILABLE = False

# Configurações padrão
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_ALPHA = 0.5  # Peso para balancear embeddings vs BM25
DEFAULT_TOP_K = 5
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

class DocumentProcessor:
    """
    Classe para processar documentos PDF e dividir em chunks.
    """

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """
        Extrai texto de um arquivo PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            Texto extraído do PDF
        """
        logger.info(f"Extraindo texto de: {pdf_path}")

        if not BM25_AVAILABLE:
            logger.warning("PyPDF não disponível. Usando extração de texto simplificada.")
            with open(pdf_path, 'rb') as f:
                content = f.read().decode('latin-1', errors='ignore')
                return content

        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"

        logger.info(f"Extração concluída: {len(text)} caracteres")
        return text

    @staticmethod
    def chunk_text(text: str,
                   chunk_size: int = DEFAULT_CHUNK_SIZE,
                   overlap: int = DEFAULT_CHUNK_OVERLAP
                   ) -> List[Dict[str, Any]]:
        """
        Divide o texto em chunks com sobreposição.

        Args:
            text: Texto a ser dividido
            chunk_size: Tamanho aproximado de cada chunk
            overlap: Sobreposição entre chunks consecutivos

        Returns:
            Lista de dicionários com id e texto de cada chunk
        """
        logger.info(f"Dividindo em chunks de ~{chunk_size} caracteres (overlap {overlap})")

        # Dividir por sentenças para manter coerência
        sentences = re.split(r'(?<=[.!?])\s+', text.replace("\n", " "))
        chunks, curr, idx = [], "", 0

        for sent in sentences:
            if len(curr) + len(sent) < chunk_size:
                curr += sent + " "
            else:
                chunks.append({"id": idx, "text": curr.strip()})
                idx += 1
                # Manter sobreposição para contexto
                curr = (curr[-overlap:] if overlap < len(curr) else curr) + sent + " "

        # Adicionar o último chunk se não estiver vazio
        if curr.strip():
            chunks.append({"id": idx, "text": curr.strip()})

        logger.info(f"Gerados {len(chunks)} chunks")
        return chunks

class RagBM25:
    """
    Implementação de RAG com BM25 para melhorar a relevância dos resultados.
    Combina busca semântica (embeddings) com busca léxica (BM25).
    """

    def __init__(self,
                 embedding_model: str = DEFAULT_EMBEDDING_MODEL,
                 alpha: float = DEFAULT_ALPHA,
                 top_k: int = DEFAULT_TOP_K):
        """
        Inicializa o sistema RAG BM25.

        Args:
            embedding_model: Nome do modelo de embeddings
            alpha: Peso para balancear embeddings vs BM25 (0-1)
            top_k: Número de resultados a retornar
        """
        self.alpha = alpha
        self.top_k = top_k
        self.processor = DocumentProcessor()
        self.chunks = []
        self.chunk_texts = []
        self.embeddings = []

        # Inicializar componentes se disponíveis
        if BM25_AVAILABLE:
            try:
                self.embedder = SentenceTransformer(embedding_model)
                logger.info(f"Modelo de embeddings {embedding_model} carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo de embeddings: {e}")
                self.embedder = None
        else:
            self.embedder = None

    def process_pdf(self, pdf_path: str) -> bool:
        """
        Processa um arquivo PDF e prepara para consulta.

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            True se o processamento foi bem-sucedido, False caso contrário
        """
        try:
            # Extrair texto do PDF
            text = self.processor.extract_text(pdf_path)

            # Dividir em chunks
            self.chunks = self.processor.chunk_text(text)
            self.chunk_texts = [c["text"] for c in self.chunks]

            # Construir índice BM25 se disponível
            if BM25_AVAILABLE:
                tokenized = [doc.split() for doc in self.chunk_texts]
                self.bm25 = BM25Okapi(tokenized)
                logger.info("Índice BM25 construído com sucesso")

                # Gerar embeddings
                if self.embedder:
                    self.embeddings = self.embedder.encode(self.chunk_texts)
                    logger.info(f"Gerados {len(self.embeddings)} embeddings")

            return True

        except Exception as e:
            logger.error(f"Erro ao processar PDF: {e}")
            return False

    def _simple_keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Realiza uma busca simples por palavras-chave.
        Usado como fallback quando BM25 ou NumPy não estão disponíveis.

        Args:
            query: Pergunta do usuário

        Returns:
            Lista de resultados relevantes com texto e pontuação
        """
        keywords = query.lower().split()
        scores = []

        for i, text in enumerate(self.chunk_texts):
            text_lower = text.lower()
            score = sum(1 for kw in keywords if kw in text_lower) / len(keywords) if keywords else 0
            scores.append((i, score))

        # Ordenar por pontuação
        scores.sort(key=lambda x: x[1], reverse=True)

        # Retornar top_k resultados
        results = []
        for i, (idx, score) in enumerate(scores[:self.top_k]):
            if score > 0:
                results.append({
                    "id": idx,
                    "text": self.chunk_texts[idx],
                    "score": score,
                    "rank": i + 1
                })

        return results

    def query(self, query: str) -> List[Dict[str, Any]]:
        """
        Consulta o sistema RAG com uma pergunta.

        Args:
            query: Pergunta do usuário

        Returns:
            Lista de resultados relevantes com texto e pontuação
        """
        if not self.chunk_texts:
            logger.warning("Nenhum documento processado. Retornando lista vazia.")
            return []

        # Fallback simples se BM25 não estiver disponível
        if not BM25_AVAILABLE:
            return self._simple_keyword_search(query)

        # Implementação completa com BM25 e embeddings
        try:
            # Importar NumPy localmente para evitar problemas de compatibilidade
            try:
                import numpy as np
            except (ImportError, ValueError):
                logger.error("Erro ao importar NumPy. Usando fallback simples.")
                return self._simple_keyword_search(query)

            # 1. Busca por embeddings
            query_embedding = self.embedder.encode(query)

            # Calcular similaridade de cosseno
            similarities = []
            for i, emb in enumerate(self.embeddings):
                sim = np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb))
                similarities.append((i, sim))

            # 2. Busca BM25
            token_q = query.split()
            bm25_scores = self.bm25.get_scores(token_q)

            # Normalizar BM25 para [0,1]
            min_b, max_b = min(bm25_scores), max(bm25_scores) or 1.0
            norm_bm25 = [(s - min_b)/(max_b - min_b) if max_b > min_b else 0.5 for s in bm25_scores]

            # 3. Combinar candidatos (união de embedding + BM25)
            # Pegar top candidatos de cada método
            top_emb = sorted(similarities, key=lambda x: x[1], reverse=True)[:self.top_k*3]
            top_emb_ids = [i for i, _ in top_emb]

            top_bm25_ids = sorted(range(len(norm_bm25)),
                                 key=lambda i: norm_bm25[i],
                                 reverse=True)[:self.top_k*3]

            # União dos candidatos
            candidates = set(top_emb_ids).union(set(top_bm25_ids))

            # 4. Calcular score híbrido e ordenar
            hybrid = []
            for idx in candidates:
                # Encontrar score de embedding
                emb_score = 0.0
                for i, score in top_emb:
                    if i == idx:
                        emb_score = score
                        break

                # Score BM25 normalizado
                bm25_score = norm_bm25[idx]

                # Score híbrido ponderado
                score = self.alpha * emb_score + (1 - self.alpha) * bm25_score
                hybrid.append((idx, score))

            # Ordenar por pontuação
            hybrid.sort(key=lambda x: x[1], reverse=True)

            # 5. Selecionar top_k
            results = []
            for i, (idx, score) in enumerate(hybrid[:self.top_k]):
                results.append({
                    "id": idx,
                    "text": self.chunk_texts[idx],
                    "score": score,
                    "rank": i + 1
                })

            return results

        except Exception as e:
            logger.error(f"Erro na consulta: {e}")
            return []

    def download_and_process_pdf(self, pdf_url: str) -> bool:
        """
        Baixa um PDF de uma URL e o processa.

        Args:
            pdf_url: URL do PDF

        Returns:
            True se o processamento foi bem-sucedido, False caso contrário
        """
        try:
            # Importar requests localmente para evitar problemas de dependência
            try:
                import requests
            except ImportError:
                logger.error("Biblioteca 'requests' não encontrada. Não é possível baixar o PDF.")
                return False

            # Baixar o PDF
            logger.info(f"Baixando PDF de {pdf_url}")
            response = requests.get(pdf_url, stream=True)

            if response.status_code != 200:
                logger.error(f"Erro ao baixar PDF: {response.status_code}")
                return False

            # Salvar em arquivo temporário
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            # Processar o PDF
            result = self.process_pdf(tmp_path)

            # Remover arquivo temporário
            os.unlink(tmp_path)

            return result

        except Exception as e:
            logger.error(f"Erro ao baixar e processar PDF: {e}")
            return False

    def summarize_with_context(self, query: str, api_function) -> str:
        """
        Gera um resumo com base nos resultados da consulta.

        Args:
            query: Pergunta do usuário
            api_function: Função para chamar a API de IA

        Returns:
            Resumo gerado com base nos resultados
        """
        # Obter resultados relevantes
        results = self.query(query)

        if not results:
            return "Não foi possível encontrar informações relevantes para responder à pergunta."

        # Construir contexto com os resultados
        context = ""
        for result in results:
            context += f"\n\n[Trecho {result['rank']} (score={result['score']:.2f})]\n{result['text']}"

        # Criar prompt para resumo
        prompt = f"""
        Com base nos seguintes trechos de um artigo científico, crie um resumo abrangente e informativo:

        Pergunta: {query}

        Trechos relevantes:
        {context}

        Instruções:
        1. Crie um resumo estruturado e detalhado do artigo científico
        2. Identifique o tema principal, metodologia, resultados e conclusões
        3. Destaque as contribuições mais importantes e inovadoras
        4. Explique como este artigo se relaciona com o campo mais amplo
        5. Inclua terminologia técnica relevante para demonstrar precisão
        6. Mantenha um tom acadêmico e profissional

        Se os trechos parecerem desconexos ou insuficientes, tente extrair o máximo de informações possível
        e indique claramente quais aspectos não puderam ser determinados a partir dos trechos fornecidos.

        Formato sugerido:
        - Título e Autores (se disponíveis)
        - Objetivo do Estudo
        - Metodologia
        - Resultados Principais
        - Conclusões e Implicações
        - Relevância para o Campo
        """

        # Chamar a API para gerar o resumo
        system_message = "Você é um especialista em análise de artigos científicos, capaz de extrair informações valiosas mesmo de trechos fragmentados e criar resumos acadêmicos precisos e informativos."
        summary = api_function(prompt, system_message, 800)

        return summary
