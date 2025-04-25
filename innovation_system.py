import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from agents import InnovationOrchestrator

st.set_page_config(
    page_title="Sistema Multiagentes de Inovação",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Configuração da página
    st.title("💡 Sistema Multiagentes de Inovação")
    
    st.markdown("""
    Este sistema utiliza múltiplos agentes de IA especializados para gerar ideias inovadoras 
    baseadas em pesquisas científicas, tendências de mercado e contexto de negócio.
    
    O processo inclui:
    1. **Pesquisa** - Coleta de informações da web e artigos científicos
    2. **Processamento** - Análise de PDFs e extração de conhecimento
    3. **Síntese** - Geração de insights a partir dos dados coletados
    4. **Ideação** - Criação de ideias inovadoras baseadas nos insights
    5. **Avaliação** - Análise crítica das ideias geradas
    """)
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("Configurações")
        
        # Seção de entrada de dados
        st.subheader("Entrada de Dados")
        
        topic = st.text_input(
            "Tópico de Pesquisa:",
            value="Inteligência Artificial na Saúde",
            help="Digite o tópico principal para a pesquisa de inovação"
        )
        
        business_context = st.text_area(
            "Contexto de Negócio:",
            value="Uma empresa de tecnologia em saúde busca desenvolver soluções inovadoras utilizando inteligência artificial para melhorar diagnósticos médicos e tratamentos personalizados. A empresa tem acesso a dados médicos anonimizados e busca criar produtos que possam ser adotados por hospitais e clínicas.",
            help="Descreva o contexto de negócio, incluindo objetivos, recursos disponíveis e restrições"
        )
        
        # Configurações avançadas
        st.subheader("Configurações Avançadas")
        
        with st.expander("Opções de Pesquisa"):
            max_web_results = st.slider(
                "Resultados da Web:",
                min_value=2,
                max_value=10,
                value=3,
                help="Número máximo de resultados a buscar na web"
            )
            
            max_arxiv_results = st.slider(
                "Artigos do arXiv:",
                min_value=2,
                max_value=10,
                value=3,
                help="Número máximo de artigos a buscar no arXiv"
            )
            
            max_papers_to_process = st.slider(
                "PDFs a Processar:",
                min_value=1,
                max_value=5,
                value=2,
                help="Número máximo de PDFs a processar com RAG"
            )
        
        # Botão para iniciar o processo
        start_button = st.button("Iniciar Processo de Inovação", type="primary")
        
        # Informações adicionais
        st.markdown("---")
        st.caption("Desenvolvido por milanesa e caramujo usando tecnologia de IA multiagente")
    
    # Conteúdo principal
    if 'process_started' not in st.session_state:
        st.session_state.process_started = False
    
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    # Iniciar o processo quando o botão for clicado
    if start_button:
        st.session_state.process_started = True
        
        # Mostrar progresso
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Função para atualizar o progresso
            def update_progress(stage, progress):
                status_text.text(f"Etapa: {stage}")
                progress_bar.progress(progress)
            
            # Container para logs
            log_container = st.expander("Logs de Execução", expanded=True)
            
            # Executar o processo
            with st.spinner("Executando processo de inovação..."):
                try:
                    # Criar o orquestrador
                    orchestrator = InnovationOrchestrator()
                    
                    # Configurar parâmetros
                    max_research_results = max(max_web_results, max_arxiv_results)
                    
                    # Etapa 1: Pesquisa
                    update_progress("Pesquisando informações", 0.1)
                    with log_container:
                        st.write(f"Pesquisando sobre: {topic}")
                    
                    research_results = orchestrator.researcher.research(topic, max_research_results)
                    update_progress("Pesquisa concluída", 0.3)
                    
                    # Etapa 2: Processamento de artigos
                    update_progress("Processando artigos científicos", 0.4)
                    with log_container:
                        st.write("Processando artigos...")
                    
                    processed_papers = orchestrator.researcher.process_papers(max_papers_to_process)
                    update_progress("Processamento de artigos concluído", 0.5)
                    
                    # Etapa 3: Geração de relatório de pesquisa
                    update_progress("Gerando relatório de pesquisa", 0.6)
                    with log_container:
                        st.write("Gerando relatório de pesquisa...")
                    
                    research_report = orchestrator.researcher.generate_research_report(topic, processed_papers)
                    update_progress("Relatório de pesquisa concluído", 0.7)
                    
                    # Etapa 4: Síntese e geração de ideias
                    update_progress("Sintetizando informações e gerando ideias", 0.8)
                    with log_container:
                        st.write("Sintetizando informações e gerando ideias...")
                    
                    orchestrator.synthesizer.set_research_data(research_results)
                    orchestrator.synthesizer.set_business_context(business_context)
                    synthesis_results = orchestrator.synthesizer.synthesize(research_report)
                    update_progress("Síntese concluída", 0.9)
                    
                    # Etapa 5: Geração de relatório final
                    update_progress("Gerando relatório final", 0.95)
                    with log_container:
                        st.write("Gerando relatório final...")
                    
                    final_report = orchestrator.synthesizer.generate_final_report()
                    update_progress("Processo concluído", 1.0)
                    
                    # Armazenar resultados na sessão
                    st.session_state.results = {
                        'topic': topic,
                        'business_context': business_context,
                        'research_results': research_results,
                        'processed_papers': processed_papers,
                        'research_report': research_report,
                        'synthesis_results': synthesis_results,
                        'final_report': final_report
                    }
                    
                    # Mostrar mensagem de sucesso
                    st.success("Processo de inovação concluído com sucesso!")
                    
                except Exception as e:
                    st.error(f"Erro durante o processo: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # Mostrar resultados se o processo foi concluído
    if st.session_state.process_started and st.session_state.results:
        results = st.session_state.results
        
        # Criar tabs para os diferentes resultados
        tabs = st.tabs([
            "Relatório Final", 
            "Ideias Geradas", 
            "Insights", 
            "Pesquisa", 
            "Artigos Processados"
        ])
        
        # Tab 1: Relatório Final
        with tabs[0]:
            st.markdown("## Relatório Final de Inovação")
            st.markdown(results['final_report'])
            
            # Botão para exportar o relatório
            export_col1, export_col2 = st.columns([1, 5])
            with export_col1:
                if st.button("📄 Exportar Relatório"):
                    st.download_button(
                        label="Baixar Relatório (TXT)",
                        data=results['final_report'],
                        file_name=f"relatorio_inovacao_{topic.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
        
        # Tab 2: Ideias Geradas
        with tabs[1]:
            st.markdown("## Ideias Geradas")
            
            if 'evaluated_ideas' in results['synthesis_results']:
                # Criar um dataframe com as ideias para visualização em tabela
                ideas_data = []
                
                for i, idea_data in enumerate(results['synthesis_results']['evaluated_ideas']):
                    # Extrair o título da ideia (primeira linha)
                    idea_lines = idea_data['idea'].split('\n')
                    idea_title = idea_lines[0] if idea_lines else f"Ideia {i+1}"
                    
                    # Adicionar ao dataframe
                    ideas_data.append({
                        'Nº': i+1,
                        'Título': idea_title,
                        'Pontuação': idea_data['average_score'],
                    })
                
                # Criar e mostrar o dataframe
                if ideas_data:
                    ideas_df = pd.DataFrame(ideas_data)
                    st.dataframe(
                        ideas_df,
                        column_config={
                            "Pontuação": st.column_config.ProgressColumn(
                                "Pontuação",
                                format="%.1f",
                                min_value=0,
                                max_value=10,
                            ),
                        },
                        hide_index=True
                    )
                
                # Mostrar detalhes de cada ideia
                for i, idea_data in enumerate(results['synthesis_results']['evaluated_ideas']):
                    with st.expander(f"Ideia {i+1} (Pontuação: {idea_data['average_score']:.1f}/10)"):
                        st.markdown(idea_data['idea'])
                        
                        st.markdown("### Avaliação")
                        st.markdown(idea_data['evaluation'])
                        
                        # Mostrar pontuações em um gráfico
                        if 'scores' in idea_data:
                            scores_data = {k: v['score'] for k, v in idea_data['scores'].items()}
                            df = pd.DataFrame(list(scores_data.items()), columns=['Critério', 'Pontuação'])
                            
                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.barh(df['Critério'], df['Pontuação'], color='skyblue')
                            ax.set_xlim(0, 10)
                            ax.set_xlabel('Pontuação')
                            ax.set_title('Avaliação da Ideia')
                            
                            st.pyplot(fig)
                            
                            # Mostrar justificativas
                            st.markdown("### Justificativas")
                            for criterion, data in idea_data['scores'].items():
                                st.markdown(f"**{criterion}:** {data['justification']}")
            else:
                st.info("Nenhuma ideia avaliada disponível.")
        
        # Tab 3: Insights
        with tabs[2]:
            st.markdown("## Insights Extraídos")
            
            if 'insights' in results['synthesis_results'] and results['synthesis_results']['insights']:
                for i, insight in enumerate(results['synthesis_results']['insights']):
                    with st.expander(f"Insight {i+1}"):
                        st.markdown(insight)
            else:
                st.info("Nenhum insight disponível.")
        
        # Tab 4: Pesquisa
        with tabs[3]:
            st.markdown("## Resultados da Pesquisa")
            
            # Separar resultados por fonte
            web_results = [r for r in results['research_results'] if r.get('source') == 'Web']
            arxiv_results = [r for r in results['research_results'] if r.get('source') == 'arXiv']
            
            # Mostrar estatísticas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Resultados da Web", len(web_results))
            with col2:
                st.metric("Artigos Científicos", len(arxiv_results))
            
            # Mostrar resultados da web
            if web_results:
                st.subheader("Resultados da Web")
                for i, result in enumerate(web_results):
                    with st.expander(f"{i+1}. {result.get('title', 'Sem título')}"):
                        st.markdown(f"**URL:** [{result.get('url', '#')}]({result.get('url', '#')})")
                        st.markdown(f"**Fonte:** {result.get('source', 'Desconhecida')}")
                        st.markdown("**Trecho:**")
                        st.markdown(result.get('snippet', 'Sem trecho disponível'))
            
            # Mostrar resultados do arXiv
            if arxiv_results:
                st.subheader("Artigos do arXiv")
                for i, paper in enumerate(arxiv_results):
                    with st.expander(f"{i+1}. {paper.get('title', 'Sem título')}"):
                        st.markdown(f"**Autores:** {', '.join(paper.get('authors', ['Desconhecido']))}")
                        st.markdown(f"**Data:** {paper.get('published_date', 'Desconhecida')}")
                        st.markdown(f"**URL:** [{paper.get('url', '#')}]({paper.get('url', '#')})")
                        if 'pdf_url' in paper and paper['pdf_url']:
                            st.markdown(f"**PDF:** [{paper.get('pdf_url', '#')}]({paper.get('pdf_url', '#')})")
                        st.markdown("**Resumo:**")
                        st.markdown(paper.get('summary', 'Sem resumo disponível'))
        
        # Tab 5: Artigos Processados
        with tabs[4]:
            st.markdown("## Artigos Processados com RAG")
            
            if results['processed_papers']:
                for i, paper in enumerate(results['processed_papers']):
                    with st.expander(f"{i+1}. {paper['title']}"):
                        st.markdown(f"**Autores:** {', '.join(paper['authors'])}")
                        st.markdown(f"**Data:** {paper['published_date']}")
                        st.markdown(f"**URL:** [{paper['url']}]({paper['url']})")
                        
                        if 'pdf_url' in paper and paper['pdf_url']:
                            st.markdown(f"**PDF:** [{paper['pdf_url']}]({paper['pdf_url']})")
                        
                        if 'ai_summary' in paper:
                            st.markdown("### Resumo Gerado por IA")
                            st.markdown(paper['ai_summary'])
            else:
                st.info("Nenhum artigo foi processado.")

if __name__ == "__main__":
    main()
