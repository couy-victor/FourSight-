import os
import tempfile
import requests
from typing import List, Dict, Any, Optional
import io

# Importações condicionais para lidar com possíveis dependências ausentes
try:
    # Tentar importar do langchain-community (versão mais recente)
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import HuggingFaceEmbeddings
        langchain_available = True
    except ImportError:
        # Fallback para importações antigas do langchain
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.vectorstores import FAISS
        from langchain.embeddings import HuggingFaceEmbeddings
        langchain_available = True
except ImportError:
    langchain_available = False

try:
    import pypdf
    pypdf_available = True
except ImportError:
    pypdf_available = False

class PDFProcessor:
    """
    Classe para processar PDFs e extrair texto.
    """

    def __init__(self):
        """Inicializa o processador de PDF."""
        self.temp_dir = tempfile.mkdtemp()
        print(f"Diretório temporário criado: {self.temp_dir}")

    def download_pdf(self, url: str) -> Optional[str]:
        """
        Baixa um PDF de uma URL e salva em um arquivo temporário.

        Args:
            url: URL do PDF para baixar

        Returns:
            Caminho para o arquivo temporário ou None se falhar
        """
        try:
            print(f"Baixando PDF de {url}")
            response = requests.get(url, stream=True)

            if response.status_code != 200:
                print(f"Erro ao baixar PDF: {response.status_code}")
                return None

            # Criar um nome de arquivo temporário
            temp_file = os.path.join(self.temp_dir, f"temp_{os.urandom(4).hex()}.pdf")

            # Salvar o conteúdo no arquivo
            with open(temp_file, 'wb') as f:
                f.write(response.content)

            print(f"PDF salvo em {temp_file}")
            return temp_file

        except Exception as e:
            print(f"Erro ao baixar PDF: {e}")
            return None

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto de um arquivo PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            Texto extraído do PDF
        """
        if not pypdf_available:
            return "Biblioteca PyPDF não está disponível. Instale com 'pip install pypdf'."

        try:
            print(f"Extraindo texto de {pdf_path}")
            text = ""

            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"

            print(f"Extraído {len(text)} caracteres")
            return text

        except Exception as e:
            print(f"Erro ao extrair texto do PDF: {e}")
            return f"Erro ao extrair texto: {str(e)}"

    def cleanup(self):
        """Remove arquivos temporários."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            print(f"Diretório temporário removido: {self.temp_dir}")
        except Exception as e:
            print(f"Erro ao remover diretório temporário: {e}")


class RAGProcessor:
    """
    Classe para implementar Retrieval Augmented Generation (RAG) com PDFs.
    """

    def __init__(self, use_local_embeddings=True):
        """
        Inicializa o processador RAG.

        Args:
            use_local_embeddings: Se True, usa embeddings locais (HuggingFace),
                                 caso contrário, tenta usar embeddings remotos
        """
        if not langchain_available:
            raise ImportError("Bibliotecas LangChain não estão disponíveis. Instale com 'pip install langchain langchain-community'")

        self.pdf_processor = PDFProcessor()
        self.use_local_embeddings = use_local_embeddings

        # Inicializar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        # Inicializar embeddings
        if use_local_embeddings:
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="all-MiniLM-L6-v2"
                )
                print("Usando embeddings locais (HuggingFace)")
            except Exception as e:
                print(f"Erro ao carregar embeddings locais: {e}")
                raise
        else:
            # Implementar embeddings remotos se necessário
            raise NotImplementedError("Embeddings remotos ainda não implementados")

    def process_pdf_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Processa um PDF a partir de uma URL e cria um índice de busca.

        Args:
            url: URL do PDF para processar

        Returns:
            Dicionário com informações do processamento ou None se falhar
        """
        try:
            # Baixar o PDF
            pdf_path = self.pdf_processor.download_pdf(url)
            if not pdf_path:
                return None

            # Extrair texto
            text = self.pdf_processor.extract_text_from_pdf(pdf_path)
            if not text or text.startswith("Erro"):
                return None

            # Dividir o texto em chunks
            chunks = self.text_splitter.split_text(text)
            print(f"Texto dividido em {len(chunks)} chunks")

            # Criar índice de busca
            vectorstore = FAISS.from_texts(chunks, self.embeddings)

            return {
                "pdf_path": pdf_path,
                "text_length": len(text),
                "chunks": len(chunks),
                "vectorstore": vectorstore
            }

        except Exception as e:
            print(f"Erro ao processar PDF: {e}")
            return None

    def query(self, vectorstore, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Consulta o índice de busca com uma pergunta.

        Args:
            vectorstore: Índice de busca FAISS
            query: Pergunta para consultar
            k: Número de resultados a retornar

        Returns:
            Lista de documentos relevantes com seus scores
        """
        try:
            results_with_scores = vectorstore.similarity_search_with_score(query, k=k)

            formatted_results = []
            for doc, score in results_with_scores:
                formatted_results.append({
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                })

            return formatted_results

        except Exception as e:
            print(f"Erro ao consultar índice: {e}")
            return []

    def cleanup(self):
        """Limpa recursos temporários."""
        self.pdf_processor.cleanup()


def extract_text_from_pdf_url(url: str) -> str:
    """
    Função auxiliar para extrair texto de um PDF a partir de uma URL.

    Args:
        url: URL do PDF

    Returns:
        Texto extraído do PDF
    """
    processor = PDFProcessor()
    try:
        pdf_path = processor.download_pdf(url)
        if pdf_path:
            text = processor.extract_text_from_pdf(pdf_path)
            return text
        return "Não foi possível baixar o PDF."
    finally:
        processor.cleanup()


def query_pdf_with_rag(pdf_url: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Função auxiliar para consultar um PDF usando RAG.

    Args:
        pdf_url: URL do PDF
        query: Pergunta para consultar
        k: Número de resultados a retornar

    Returns:
        Lista de trechos relevantes com seus scores
    """
    rag_processor = RAGProcessor()
    try:
        result = rag_processor.process_pdf_url(pdf_url)
        if result and "vectorstore" in result:
            return rag_processor.query(result["vectorstore"], query, k)
        return []
    finally:
        rag_processor.cleanup()
