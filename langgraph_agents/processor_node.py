from typing import Dict, Any, List
from .state import InnovationState
from utils import extract_text_from_pdf_url, summarize_pdf, call_groq_api, RagBM25

class ProcessorNode:
    """
    Nó responsável por processar os artigos encontrados, extraindo e resumindo o conteúdo dos PDFs.
    Usa RAG BM25 se disponível para melhorar a qualidade dos resumos.
    """

    def __init__(self):
        """Inicializa o nó de processamento."""
        self.use_rag_bm25 = True

        # Inicializar o sistema RAG BM25
        try:
            self.rag_bm25 = RagBM25()
            print("Sistema RAG BM25 inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar RAG BM25: {e}")
            self.use_rag_bm25 = False

    async def run(self, state: InnovationState) -> InnovationState:
        """
        Processa os artigos encontrados, extraindo e resumindo o conteúdo dos PDFs.

        Args:
            state: Estado atual do grafo

        Returns:
            Estado atualizado com os artigos processados
        """
        # Atualizar o estágio atual
        state.current_stage = "Processando artigos científicos"

        papers = [r for r in state.research_results if r.get('type') == 'paper']
        processed_papers = []

        print(f"Processando {min(state.max_papers_to_process, len(papers))} artigos de {len(papers)} encontrados")

        for i, paper in enumerate(papers[:state.max_papers_to_process]):
            try:
                if 'pdf_url' in paper and paper['pdf_url']:
                    print(f"Processando artigo {i+1}: {paper['title']}")

                    # Usar RAG BM25 se disponível
                    if self.use_rag_bm25:
                        try:
                            # Processar o PDF com RAG BM25
                            success = self.rag_bm25.download_and_process_pdf(paper['pdf_url'])

                            if success:
                                # Gerar resumo com base no título e contexto
                                query = f"Resumir este artigo científico: {paper['title']}"
                                summary = self.rag_bm25.summarize_with_context(query, call_groq_api)
                                print(f"Artigo {i+1} processado com RAG BM25")
                            else:
                                # Fallback para o método tradicional
                                summary = summarize_pdf(paper['pdf_url'], call_groq_api)
                                print(f"Artigo {i+1} processado com método tradicional (fallback)")
                        except Exception as rag_error:
                            print(f"Erro no processamento RAG BM25: {rag_error}")
                            # Fallback para o método tradicional
                            summary = summarize_pdf(paper['pdf_url'], call_groq_api)
                    else:
                        # Método tradicional
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

        state.processed_papers = processed_papers

        return state

    async def generate_research_report(self, state: InnovationState) -> InnovationState:
        """
        Gera um relatório de pesquisa com base nos resultados processados.

        Args:
            state: Estado atual do grafo

        Returns:
            Estado atualizado com o relatório de pesquisa
        """
        # Atualizar o estágio atual
        state.current_stage = "Gerando relatório de pesquisa"

        # Construir o prompt para o relatório
        web_results = [r for r in state.research_results if r.get('type') == 'web']
        papers = state.processed_papers

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
        Crie um relatório de pesquisa abrangente sobre o tópico: {state.topic}

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

        state.research_report = report

        return state
