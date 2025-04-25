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
        Extrai texto de um arquivo PDF usando ferramentas básicas.
        Esta é uma implementação simplificada que usa comandos do sistema.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído do PDF
        """
        try:
            # Tentar usar pdftotext se disponível (parte do pacote poppler)
            import subprocess
            output_text_file = os.path.join(self.temp_dir, "output.txt")
            
            try:
                # Tentar com pdftotext (Linux/Mac)
                subprocess.run(["pdftotext", pdf_path, output_text_file], check=True)
                with open(output_text_file, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                return text
            except (subprocess.SubprocessError, FileNotFoundError):
                # Tentar com outro método
                pass
            
            # Método alternativo: usar strings básicas para extrair texto
            # Isso é muito limitado, mas funciona como fallback
            with open(pdf_path, 'rb') as f:
                content = f.read().decode('latin-1', errors='ignore')
                
                # Extrair texto usando expressões regulares simples
                # Isso é muito básico e não funcionará bem para PDFs complexos
                text_blocks = re.findall(r'([\w\s\.,;:!\?-]{20,})', content)
                text = '\n'.join(text_blocks)
                
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
