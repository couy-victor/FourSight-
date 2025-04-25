import os
import tempfile
import requests
import re
from typing import List, Dict, Any, Optional

class SimplePDFProcessor:
    """
    Classe simplificada para processar PDFs e extrair texto.
    Não depende de bibliotecas externas complexas.
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
        Extrai texto de um arquivo PDF usando PyPDF.

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            Texto extraído do PDF
        """
        try:
            # Usar PyPDF para extrair texto
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            text = ""

            # Extrair texto de cada página
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Página {i+1} ---\n"
                    text += page_text + "\n"

            # Se não conseguiu extrair texto com PyPDF, tentar método alternativo
            if not text or len(text) < 100:
                print("Pouco texto extraído com PyPDF, tentando método alternativo...")

                # Tentar usar pdftotext se disponível
                try:
                    import subprocess
                    output_text_file = os.path.join(self.temp_dir, "output.txt")

                    subprocess.run(["pdftotext", "-layout", pdf_path, output_text_file], check=True)
                    with open(output_text_file, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                except (subprocess.SubprocessError, FileNotFoundError):
                    print("pdftotext não disponível, usando método de fallback...")

                    # Método de último recurso: extrair texto usando regex
                    with open(pdf_path, 'rb') as f:
                        content = f.read().decode('latin-1', errors='ignore')

                        # Extrair texto usando expressões regulares mais sofisticadas
                        # Procurar por blocos de texto com pelo menos 20 caracteres
                        text_blocks = re.findall(r'([\w\s\.,;:!\?-]{20,})', content)
                        text = '\n'.join(text_blocks)

            # Limpar o texto
            # Remover caracteres não imprimíveis
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
            # Remover múltiplos espaços em branco
            text = re.sub(r'\s+', ' ', text)
            # Remover múltiplas quebras de linha
            text = re.sub(r'\n\s*\n', '\n\n', text)

            # Verificar se o texto extraído parece ser conteúdo real ou apenas metadados/código
            if len(text) < 500 or "stream" in text.lower() and "endstream" in text.lower() and "obj" in text.lower():
                print("O texto extraído parece ser apenas metadados ou código PDF, não conteúdo real")
                return "Não foi possível extrair conteúdo textual significativo deste PDF. O arquivo pode estar protegido, ser uma imagem digitalizada ou conter apenas gráficos."

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


def extract_text_from_pdf_url(url: str) -> str:
    """
    Função auxiliar para extrair texto de um PDF a partir de uma URL.

    Args:
        url: URL do PDF

    Returns:
        Texto extraído do PDF
    """
    processor = SimplePDFProcessor()
    try:
        pdf_path = processor.download_pdf(url)
        if pdf_path:
            text = processor.extract_text_from_pdf(pdf_path)
            return text
        return "Não foi possível baixar o PDF."
    finally:
        processor.cleanup()


def summarize_pdf(pdf_url: str, api_function) -> str:
    """
    Função para resumir o conteúdo de um PDF usando um modelo de IA.

    Args:
        pdf_url: URL do PDF
        api_function: Função para chamar a API de IA (call_groq_api ou call_google_api)

    Returns:
        Resumo do PDF
    """
    # Extrair texto do PDF
    text = extract_text_from_pdf_url(pdf_url)

    # Limitar o tamanho do texto para evitar exceder limites de tokens
    if len(text) > 10000:
        text = text[:10000] + "..."

    # Criar prompt para resumir
    prompt = f"""
    Resuma o seguinte texto extraído de um artigo científico. Identifique:
    1. O objetivo principal do artigo
    2. A metodologia utilizada
    3. Os principais resultados
    4. As conclusões mais importantes

    Texto:
    {text}

    Resumo:
    """

    # Chamar a API para resumir
    system_message = "Você é um assistente especializado em resumir artigos científicos de forma clara e concisa."
    summary = api_function(prompt, system_message, 800)

    return summary
