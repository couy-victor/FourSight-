from typing import Dict, Any, List
from .state import InnovationState
from utils import call_groq_api
from datetime import datetime

class TrendAnalyzerNode:
    """
    Nó responsável por analisar tendências emergentes a partir dos resultados de pesquisa.
    Identifica padrões, tecnologias e abordagens recentes no campo.
    """
    
    async def run(self, state: InnovationState) -> InnovationState:
        """
        Analisa tendências emergentes a partir dos resultados de pesquisa.
        
        Args:
            state: Estado atual do grafo
            
        Returns:
            Estado atualizado com as tendências identificadas
        """
        # Atualizar o estágio atual
        state.current_stage = "Analisando tendências emergentes"
        
        # Extrair tendências dos resultados de pesquisa e artigos processados
        trends = await self._extract_trends(
            state.web_results, 
            state.arxiv_results, 
            state.processed_papers, 
            state.topic, 
            state.business_context
        )
        
        # Adicionar tendências ao estado
        state.trends = trends
        
        return state
    
    async def _extract_trends(
        self, 
        web_results: List[Dict[str, Any]], 
        arxiv_results: List[Dict[str, Any]], 
        processed_papers: List[Dict[str, Any]], 
        topic: str, 
        business_context: str
    ) -> List[Dict[str, Any]]:
        """
        Extrai tendências emergentes dos resultados de pesquisa.
        
        Args:
            web_results: Resultados da pesquisa na web
            arxiv_results: Resultados da pesquisa no arXiv
            processed_papers: Artigos processados com RAG
            topic: Tópico de pesquisa
            business_context: Contexto de negócio
            
        Returns:
            Lista de tendências identificadas
        """
        # Ano atual para referência de recência
        current_year = datetime.now().year
        
        # Preparar contexto para a análise de tendências
        web_context = self._prepare_web_context(web_results)
        arxiv_context = self._prepare_arxiv_context(arxiv_results)
        papers_context = self._prepare_papers_context(processed_papers)
        
        # Criar o prompt para análise de tendências
        prompt = f"""
        Analise os resultados de pesquisa recentes abaixo sobre o tópico "{topic}" e identifique as principais tendências emergentes, 
        tecnologias inovadoras e abordagens de ponta que estão moldando este campo em {current_year}.
        
        Contexto de Negócio:
        {business_context}
        
        Resultados da Web (2024-2025):
        {web_context}
        
        Artigos Científicos Recentes:
        {arxiv_context}
        
        Resumos de Artigos Processados:
        {papers_context}
        
        Para cada tendência identificada:
        1. Forneça um nome claro e descritivo para a tendência
        2. Descreva a tendência em detalhes (o que é, por que é importante, como está evoluindo)
        3. Indique o nível de maturidade (Emergente, Em crescimento, Estabelecida)
        4. Liste as fontes específicas que mencionam esta tendência (ex: "Mencionado no artigo X e nas fontes web Y e Z")
        5. Explique como esta tendência pode impactar o contexto de negócio fornecido
        
        Identifique apenas tendências que são verdadeiramente recentes (2023-2025) e relevantes para o tópico e contexto.
        Priorize tendências que aparecem em múltiplas fontes ou que são destacadas como inovadoras nos artigos científicos.
        
        Formato de saída:
        
        ## [Nome da Tendência 1]
        
        **Nível de Maturidade:** [Emergente/Em crescimento/Estabelecida]
        
        **Descrição:**
        [Descrição detalhada da tendência]
        
        **Fontes:**
        [Lista de fontes específicas que mencionam esta tendência]
        
        **Impacto no Contexto de Negócio:**
        [Explicação de como esta tendência pode impactar o contexto de negócio]
        
        ---
        
        ## [Nome da Tendência 2]
        
        ...e assim por diante.
        """
        
        # Chamar a API para analisar tendências
        system_message = """Você é um analista especializado em identificar tendências emergentes e tecnologias inovadoras.
        Você tem habilidade para detectar padrões em pesquisas recentes e prever como eles podem evoluir.
        Você é especialmente bom em identificar tendências que são verdadeiramente novas e não apenas conceitos estabelecidos."""
        
        response = call_groq_api(prompt, system_message, 1500)
        
        # Processar a resposta para extrair as tendências
        trends = []
        current_trend = None
        
        for line in response.split('\n'):
            line = line.strip()
            
            # Nova tendência começa com ##
            if line.startswith('## '):
                if current_trend:
                    trends.append(current_trend)
                current_trend = {
                    'name': line[3:],
                    'description': '',
                    'maturity': '',
                    'sources': [],
                    'impact': ''
                }
            # Linha de separação entre tendências
            elif line == '---':
                if current_trend:
                    trends.append(current_trend)
                current_trend = None
            # Extrair nível de maturidade
            elif current_trend and line.startswith('**Nível de Maturidade:**'):
                current_trend['maturity'] = line.replace('**Nível de Maturidade:**', '').strip()
            # Extrair descrição
            elif current_trend and line.startswith('**Descrição:**'):
                current_trend['description'] = ''
            # Extrair fontes
            elif current_trend and line.startswith('**Fontes:**'):
                current_trend['sources'] = []
            # Extrair impacto
            elif current_trend and line.startswith('**Impacto no Contexto de Negócio:**'):
                current_trend['impact'] = ''
            # Adicionar conteúdo à seção atual
            elif current_trend:
                if '**Descrição:**' in current_trend['description'] or not current_trend['description']:
                    if not line.startswith('**'):
                        if current_trend['description']:
                            current_trend['description'] += '\n' + line
                        else:
                            current_trend['description'] = line
                elif '**Fontes:**' in current_trend.get('sources', []) or not current_trend['sources']:
                    if not line.startswith('**'):
                        current_trend['sources'].append(line)
                elif '**Impacto no Contexto de Negócio:**' in current_trend['impact'] or not current_trend['impact']:
                    if not line.startswith('**'):
                        if current_trend['impact']:
                            current_trend['impact'] += '\n' + line
                        else:
                            current_trend['impact'] = line
        
        # Adicionar a última tendência se existir
        if current_trend:
            trends.append(current_trend)
        
        return trends
    
    def _prepare_web_context(self, web_results: List[Dict[str, Any]]) -> str:
        """Prepara o contexto a partir dos resultados da web."""
        if not web_results:
            return "Nenhum resultado da web disponível."
        
        context = ""
        for i, result in enumerate(web_results[:5]):  # Limitar a 5 resultados para manter o prompt conciso
            context += f"\nFonte Web {i+1}: {result.get('title', 'Sem título')}\n"
            context += f"URL: {result.get('url', '#')}\n"
            context += f"Trecho: {result.get('snippet', 'Sem trecho disponível')}\n"
        
        return context
    
    def _prepare_arxiv_context(self, arxiv_results: List[Dict[str, Any]]) -> str:
        """Prepara o contexto a partir dos resultados do arXiv."""
        if not arxiv_results:
            return "Nenhum artigo científico disponível."
        
        context = ""
        for i, paper in enumerate(arxiv_results[:5]):  # Limitar a 5 artigos
            context += f"\nArtigo {i+1}: {paper.get('title', 'Sem título')}\n"
            context += f"Autores: {', '.join(paper.get('authors', ['Desconhecido'])[:3])}\n"
            context += f"Data: {paper.get('published_date', 'Desconhecida')}\n"
            context += f"Resumo: {paper.get('summary', 'Sem resumo')[:300]}...\n"  # Truncar resumos longos
        
        return context
    
    def _prepare_papers_context(self, processed_papers: List[Dict[str, Any]]) -> str:
        """Prepara o contexto a partir dos artigos processados."""
        if not processed_papers:
            return "Nenhum artigo processado disponível."
        
        context = ""
        for i, paper in enumerate(processed_papers):
            context += f"\nArtigo Processado {i+1}: {paper.get('title', 'Sem título')}\n"
            if 'ai_summary' in paper and paper['ai_summary']:
                # Truncar resumos muito longos
                summary = paper['ai_summary']
                if len(summary) > 500:
                    summary = summary[:500] + "..."
                context += f"Resumo IA: {summary}\n"
            else:
                context += "Sem resumo disponível.\n"
        
        return context
