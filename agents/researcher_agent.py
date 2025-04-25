import os
import json
from typing import List, Dict, Any
from utils import search_web, search_arxiv, extract_text_from_pdf_url, summarize_pdf, call_groq_api

class ResearcherAgent:
    """
    Agente responsável por pesquisar informações relevantes para o processo de inovação.
    Combina resultados de diferentes fontes: web, artigos científicos, etc.
    """
    
    def __init__(self, use_arxiv=True, use_web=True):
        """
        Inicializa o agente de pesquisa.
        
        Args:
            use_arxiv: Se True, pesquisa artigos no arXiv
            use_web: Se True, pesquisa informações na web
        """
        self.use_arxiv = use_arxiv
        self.use_web = use_web
        self.research_results = []
    
    def research(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Pesquisa informações sobre um tópico.
        
        Args:
            topic: Tópico a ser pesquisado
            max_results: Número máximo de resultados por fonte
            
        Returns:
            Lista de resultados da pesquisa
        """
        print(f"Pesquisando sobre: {topic}")
        self.research_results = []
        
        # Pesquisar na web
        if self.use_web:
            web_results = self._search_web(topic, max_results)
            self.research_results.extend(web_results)
        
        # Pesquisar artigos científicos
        if self.use_arxiv:
            arxiv_results = self._search_arxiv(topic, max_results)
            self.research_results.extend(arxiv_results)
        
        return self.research_results
    
    def _search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Pesquisa informações na web.
        
        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            
        Returns:
            Lista de resultados da web
        """
        try:
            print(f"Pesquisando na web: {query}")
            results = search_web(query, max_results)
            
            # Formatar resultados
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', 'Sem título'),
                    'url': result.get('url', ''),
                    'snippet': result.get('snippet', 'Sem descrição'),
                    'source': 'Web',
                    'type': 'web'
                })
            
            print(f"Encontrados {len(formatted_results)} resultados na web")
            return formatted_results
        
        except Exception as e:
            print(f"Erro ao pesquisar na web: {e}")
            return []
    
    def _search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Pesquisa artigos no arXiv.
        
        Args:
            query: Consulta de pesquisa
            max_results: Número máximo de resultados
            
        Returns:
            Lista de resultados do arXiv
        """
        try:
            print(f"Pesquisando no arXiv: {query}")
            results = search_arxiv(query, max_results)
            
            # Formatar resultados
            formatted_results = []
            for paper in results:
                formatted_results.append({
                    'title': paper.get('title', 'Sem título'),
                    'url': paper.get('url', ''),
                    'pdf_url': paper.get('pdf_url', ''),
                    'authors': paper.get('authors', []),
                    'summary': paper.get('summary', 'Sem resumo'),
                    'published_date': paper.get('published_date', ''),
                    'categories': paper.get('categories', []),
                    'source': 'arXiv',
                    'type': 'paper'
                })
            
            print(f"Encontrados {len(formatted_results)} artigos no arXiv")
            return formatted_results
        
        except Exception as e:
            print(f"Erro ao pesquisar no arXiv: {e}")
            return []
    
    def process_papers(self, max_papers: int = 2) -> List[Dict[str, Any]]:
        """
        Processa os artigos encontrados, extraindo e resumindo o conteúdo dos PDFs.
        
        Args:
            max_papers: Número máximo de artigos a processar
            
        Returns:
            Lista de artigos processados
        """
        papers = [r for r in self.research_results if r.get('type') == 'paper']
        processed_papers = []
        
        print(f"Processando {min(max_papers, len(papers))} artigos de {len(papers)} encontrados")
        
        for i, paper in enumerate(papers[:max_papers]):
            try:
                if 'pdf_url' in paper and paper['pdf_url']:
                    print(f"Processando artigo {i+1}: {paper['title']}")
                    
                    # Resumir o PDF
                    summary = summarize_pdf(paper['pdf_url'], call_groq_api)
                    
                    # Adicionar o resumo ao artigo
                    processed_paper = paper.copy()
                    processed_paper['ai_summary'] = summary
                    processed_papers.append(processed_paper)
                    
                    print(f"Artigo {i+1} processado com sucesso")
                else:
                    print(f"Artigo {i+1} não tem URL de PDF")
            except Exception as e:
                print(f"Erro ao processar artigo {i+1}: {e}")
        
        return processed_papers
    
    def generate_research_report(self, topic: str, processed_results: List[Dict[str, Any]]) -> str:
        """
        Gera um relatório de pesquisa com base nos resultados processados.
        
        Args:
            topic: Tópico da pesquisa
            processed_results: Resultados processados
            
        Returns:
            Relatório de pesquisa em formato de texto
        """
        # Construir o prompt para o relatório
        web_results = [r for r in self.research_results if r.get('type') == 'web']
        papers = [r for r in processed_results if r.get('type') == 'paper']
        
        # Construir contexto com informações da web
        web_context = ""
        for i, result in enumerate(web_results[:3]):
            web_context += f"\nFonte {i+1}: {result['title']}\n"
            web_context += f"URL: {result['url']}\n"
            web_context += f"Trecho: {result['snippet']}\n"
        
        # Construir contexto com informações dos artigos
        papers_context = ""
        for i, paper in enumerate(papers):
            papers_context += f"\nArtigo {i+1}: {paper['title']}\n"
            papers_context += f"Autores: {', '.join(paper['authors'][:3])}\n"
            papers_context += f"Data: {paper['published_date']}\n"
            papers_context += f"Resumo IA: {paper.get('ai_summary', 'Não disponível')}\n"
        
        # Criar o prompt para o relatório
        prompt = f"""
        Crie um relatório de pesquisa abrangente sobre o tópico: {topic}
        
        Informações da Web:
        {web_context}
        
        Artigos Científicos:
        {papers_context}
        
        Com base nas informações acima, crie um relatório estruturado que:
        1. Introduza o tópico e sua relevância
        2. Resuma as principais descobertas da web
        3. Sintetize as contribuições dos artigos científicos
        4. Identifique tendências, padrões ou insights importantes
        5. Conclua com direções futuras ou oportunidades de inovação
        
        Relatório:
        """
        
        # Chamar a API para gerar o relatório
        system_message = "Você é um assistente especializado em criar relatórios de pesquisa abrangentes e bem estruturados."
        report = call_groq_api(prompt, system_message, 1500)
        
        return report
    
    def save_results(self, filename: str = "research_results.json"):
        """
        Salva os resultados da pesquisa em um arquivo JSON.
        
        Args:
            filename: Nome do arquivo para salvar os resultados
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.research_results, f, ensure_ascii=False, indent=2)
            print(f"Resultados salvos em {filename}")
        except Exception as e:
            print(f"Erro ao salvar resultados: {e}")
    
    def load_results(self, filename: str = "research_results.json") -> bool:
        """
        Carrega resultados de pesquisa de um arquivo JSON.
        
        Args:
            filename: Nome do arquivo para carregar os resultados
            
        Returns:
            True se os resultados foram carregados com sucesso, False caso contrário
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.research_results = json.load(f)
                print(f"Resultados carregados de {filename}")
                return True
            else:
                print(f"Arquivo {filename} não encontrado")
                return False
        except Exception as e:
            print(f"Erro ao carregar resultados: {e}")
            return False
