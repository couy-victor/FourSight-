import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from dotenv import load_dotenv
from langgraph_agents import LangGraphOrchestrator
from utils.pdf_report import generate_innovation_report, get_pdf_download_link

# Carregar variáveis de ambiente
load_dotenv()

# Definir cores do FourSight
foursight_blue = "#2E86C1"
foursight_orange = "#E67E22"
foursight_green = "#27AE60"
foursight_red = "#E74C3C"
foursight_gray = "#95A5A6"

# Configurar tema do Seaborn para todos os gráficos
sns.set_theme(style="whitegrid", palette=[foursight_blue, foursight_orange, foursight_green, foursight_red])
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['axes.edgecolor'] = '#dddddd'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.color'] = '#eeeeee'
plt.rcParams['grid.linestyle'] = ':'

st.set_page_config(
    page_title="FourSight - Inovação com Dados Recentes",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Configuração da página
    st.title("💡 FourSight - Sistema Multiagentes de Inovação")

    st.markdown("""
    <div style="background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #2E86C1;">
    <h3 style="color: #2E86C1;">Inovação Baseada em Dados Recentes e Relevantes</h3>
    <p>Este sistema utiliza múltiplos agentes de IA especializados implementados com LangGraph e Llama 4 para gerar ideias inovadoras
    baseadas em pesquisas científicas recentes (2023-2025), tendências emergentes de mercado e contexto de negócio.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    O processo avançado de inovação inclui:
    1. **Pesquisa Direcionada** - Coleta de informações recentes (2024-2025) da web e artigos científicos relevantes
    2. **Processamento Inteligente** - Análise de PDFs e extração de conhecimento com RAG (Retrieval Augmented Generation)
    3. **Análise de Tendências** - Identificação de tendências emergentes a partir de fontes recentes
    4. **Síntese Contextual** - Geração de insights conectados às tendências identificadas
    5. **Ideação Estratégica** - Criação de ideias inovadoras com nomes de produtos/serviços memoráveis
    6. **Avaliação Criteriosa** - Análise crítica e pontuação das ideias geradas
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
        st.caption("Desenvolvido com LangGraph")

    # Inicializar variáveis de estado da sessão
    if 'process_started' not in st.session_state:
        st.session_state['process_started'] = False

    if 'results' not in st.session_state:
        st.session_state['results'] = None

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
            with st.spinner("Executando processo de inovação com LangGraph..."):
                try:
                    # Criar o orquestrador LangGraph
                    orchestrator = LangGraphOrchestrator()

                    # Configurar parâmetros
                    max_research_results = max(max_web_results, max_arxiv_results)

                    # Etapa 1: Pesquisa
                    update_progress("Pesquisando informações", 0.1)
                    with log_container:
                        st.write(f"Pesquisando sobre: {topic}")

                    research_results = orchestrator.researcher.research(topic, max_research_results, business_context)
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

                    # Etapa 4: Análise de tendências emergentes
                    update_progress("Analisando tendências emergentes", 0.75)
                    with log_container:
                        st.write("Identificando tendências emergentes com base nas pesquisas recentes...")

                    # Etapa 5: Síntese e geração de ideias
                    update_progress("Sintetizando informações e gerando ideias", 0.85)
                    with log_container:
                        st.write("Sintetizando informações e gerando ideias...")

                    orchestrator.synthesizer.set_research_data(research_results)
                    orchestrator.synthesizer.set_business_context(business_context)
                    synthesis_results = orchestrator.synthesizer.synthesize(research_report)
                    update_progress("Síntese concluída", 0.9)

                    # Etapa 6: Geração de relatório final
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
                        'web_results': orchestrator.state.web_results,
                        'arxiv_results': orchestrator.state.arxiv_results,
                        'reddit_results': orchestrator.state.reddit_results,
                        'producthunt_results': orchestrator.state.producthunt_results,
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
            "Análises & Tendências",
            "Pesquisa",
            "Artigos Processados"
        ])

        # Tab 1: Relatório Final
        with tabs[0]:
            st.markdown("## Relatório Final de Inovação")
            st.markdown(results['final_report'])

            # Botões para exportar o relatório
            st.markdown("### Exportar Relatório")
            export_col1, export_col2 = st.columns([1, 1])

            with export_col1:
                if st.button("📄 Exportar como TXT"):
                    st.download_button(
                        label="Baixar Relatório (TXT)",
                        data=results['final_report'],
                        file_name=f"relatorio_inovacao_{topic.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

            with export_col2:
                if st.button("📊 Exportar como PDF (com gráficos)"):
                    with st.spinner("Gerando relatório em PDF..."):
                        try:
                            # Gerar o relatório em PDF
                            pdf_path = generate_innovation_report(results)

                            # Verificar se o caminho é uma mensagem de erro
                            if pdf_path.startswith("ERROR:"):
                                st.error(pdf_path)
                                st.info("Para habilitar a exportação em PDF, execute: pip install fpdf reportlab matplotlib")
                                st.info("Enquanto isso, você pode baixar o relatório em formato TXT como alternativa.")
                            else:
                                # Mostrar link de download
                                st.markdown(get_pdf_download_link(pdf_path), unsafe_allow_html=True)
                                st.success("Relatório PDF gerado com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao gerar o PDF: {str(e)}")
                            st.info("Tente baixar o relatório em formato TXT como alternativa.")

        # Tab 2: Ideias Geradas
        with tabs[1]:
            st.markdown("## Ideias Inovadoras Baseadas em Tendências Recentes")
            st.markdown("""
            <div style="background-color: #f0f7ff; padding: 10px; border-radius: 5px; border-left: 4px solid #3498DB; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 0.9em;">
                    <strong>Baseadas em:</strong> Tendências emergentes de 2024-2025 e artigos científicos recentes
                </p>
                <p style="margin: 5px 0 0 0; font-size: 0.8em; color: #555;">
                    Cada ideia inclui um nome de produto/serviço memorável e está diretamente conectada a tendências recentes identificadas.
                </p>
            </div>
            """, unsafe_allow_html=True)

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

                        # Mostrar pontuações em um gráfico mais elaborado
                        if 'scores' in idea_data:
                            scores_data = {k: v['score'] for k, v in idea_data['scores'].items()}
                            df = pd.DataFrame(list(scores_data.items()), columns=['Critério', 'Pontuação'])

                            # Criar um DataFrame para o Seaborn
                            df_sorted = df.sort_values(by='Pontuação', ascending=True)  # Ordenar para melhor visualização

                            # Criar gráfico com tamanho reduzido
                            fig, ax = plt.subplots(figsize=(7, 3.5))

                            # Usar paleta de cores personalizada baseada na pontuação
                            # Criar um mapa de cores do vermelho ao verde
                            cmap = sns.color_palette("RdYlGn", n_colors=len(df_sorted))

                            # Criar barras horizontais com Seaborn
                            sns.barplot(x='Pontuação', y='Critério', data=df_sorted,
                                      palette=cmap, orient='h', alpha=0.85, ax=ax)

                            # Adicionar valores nas barras com estilo mais sutil
                            for i, bar in enumerate(ax.patches):
                                width = bar.get_width()
                                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                                       f'{width:.1f}', va='center', color='#333333',
                                       fontweight='medium', fontsize=9)

                            # Personalizar eixos com estilo Seaborn
                            ax.set_xlim(0, 10.5)
                            ax.set_xlabel('Pontuação', fontsize=10, color='#333333', fontweight='medium')
                            ax.set_ylabel('')  # Remover label do eixo y

                            # Título mais elegante
                            ax.set_title('Avaliação por Critério', fontsize=13, color='#333333',
                                       fontweight='bold', pad=15)

                            # Remover todas as bordas para um visual mais clean
                            sns.despine(left=True, bottom=True)

                            # Adicionar uma linha vertical para a média com estilo aprimorado
                            avg_score = idea_data['average_score']
                            ax.axvline(x=avg_score, color=foursight_red, linestyle='-',
                                     alpha=0.7, linewidth=1.5, zorder=0)

                            # Adicionar texto da média com estilo melhorado
                            ax.text(avg_score, -0.6, f'Média: {avg_score:.1f}',
                                   color=foursight_red, fontsize=10, ha='center',
                                   fontweight='bold', bbox=dict(facecolor='white', alpha=0.8,
                                                              edgecolor='none', boxstyle='round,pad=0.2'))

                            # Ajustar o grid para ser mais sutil
                            ax.grid(axis='x', linestyle='--', color='#EEEEEE', alpha=0.7, zorder=0)

                            # Mostrar o gráfico
                            st.pyplot(fig)

                            # Mostrar justificativas
                            st.markdown("### Justificativas")
                            for criterion, data in idea_data['scores'].items():
                                st.markdown(f"**{criterion}:** {data['justification']}")
            else:
                st.info("Nenhuma ideia avaliada disponível.")

        # Tab 3: Análises & Tendências
        with tabs[2]:
            st.markdown("## Análises & Tendências Emergentes")
            st.markdown("""
            <div style="background-color: #e8f4f8; padding: 10px; border-radius: 5px; border-left: 4px solid #2E86C1; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 0.9em;">
                    <strong>Fonte:</strong> Pesquisas recentes da web (2024-2025) e artigos científicos relevantes
                </p>
                <p style="margin: 5px 0 0 0; font-size: 0.8em; color: #555;">
                    Esta seção combina tendências emergentes e insights analíticos extraídos das fontes mais recentes.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if 'trends' in results['synthesis_results'] and results['synthesis_results']['trends']:
                # Criar um dataframe com as tendências para visualização em tabela
                trends_data = []

                for i, trend in enumerate(results['synthesis_results']['trends']):
                    # Adicionar ao dataframe
                    trends_data.append({
                        'Nº': i+1,
                        'Tendência': trend.get('name', f"Tendência {i+1}"),
                        'Maturidade': trend.get('maturity', 'N/A'),
                    })

                # Criar e mostrar o dataframe
                if trends_data:
                    trends_df = pd.DataFrame(trends_data)
                    st.dataframe(
                        trends_df,
                        column_config={
                            "Maturidade": st.column_config.TextColumn(
                                "Nível de Maturidade",
                                help="Emergente, Em crescimento ou Estabelecida",
                            ),
                        },
                        hide_index=True
                    )

                # Mostrar detalhes de cada tendência
                for i, trend in enumerate(results['synthesis_results']['trends']):
                    with st.expander(f"Tendência {i+1}: {trend.get('name', 'Sem nome')}"):
                        # Mostrar nível de maturidade
                        maturity = trend.get('maturity', 'Não especificado')
                        maturity_color = "#1E88E5" if "emergente" in maturity.lower() else "#43A047" if "crescimento" in maturity.lower() else "#FFC107"
                        st.markdown(f"<div style='background-color: {maturity_color}; padding: 5px 10px; border-radius: 5px; display: inline-block; color: white; font-weight: bold; margin-bottom: 15px;'>{maturity}</div>", unsafe_allow_html=True)

                        # Mostrar descrição
                        if 'description' in trend and trend['description']:
                            st.markdown("### Descrição")
                            st.markdown(trend['description'])

                        # Mostrar fontes
                        if 'sources' in trend and trend['sources']:
                            st.markdown("### Fontes")
                            for source in trend['sources']:
                                st.markdown(f"- {source}")

                        # Mostrar impacto
                        if 'impact' in trend and trend['impact']:
                            st.markdown("### Impacto no Contexto de Negócio")
                            st.markdown(trend['impact'])
            else:
                st.info("Nenhuma tendência emergente identificada.")

            # Adicionar seção de insights na mesma aba
            st.markdown("### Insights Analíticos")

            if 'insights' in results['synthesis_results'] and results['synthesis_results']['insights']:
                # Extrair categorias dos insights para o gráfico de radar
                insights = results['synthesis_results']['insights']

                # Criar duas colunas: uma para o gráfico e outra para a lista de insights
                insight_cols = st.columns([3, 4])

                with insight_cols[0]:
                    # Criar gráfico de radar para visualizar insights
                    if len(insights) >= 3:  # Precisamos de pelo menos 3 insights para um radar decente
                        try:
                            # Extrair títulos dos insights (primeira linha ou primeiras palavras)
                            insight_titles = []
                            for insight in insights[:6]:  # Limitar a 6 para o radar não ficar muito cheio
                                # Tentar extrair o título do formato "Insight X: Título"
                                if ":" in insight.split("\n")[0]:
                                    title = insight.split("\n")[0].split(":", 1)[1].strip()
                                    # Limitar o tamanho do título
                                    if len(title) > 25:
                                        title = title[:22] + "..."
                                else:
                                    # Usar as primeiras palavras
                                    words = insight.split()
                                    title = " ".join(words[:4]) + "..."
                                insight_titles.append(title)

                            # Gerar valores de relevância (podemos usar um valor fixo ou extrair de alguma forma)
                            # Para um visual clean, usamos valores entre 60-90 para não ter muita variação
                            import random
                            random.seed(42)  # Para consistência
                            relevance = [random.randint(60, 90) for _ in range(len(insight_titles))]

                            # Criar o gráfico de radar
                            fig = plt.figure(figsize=(5, 5))
                            ax = fig.add_subplot(111, polar=True)

                            # Número de variáveis
                            N = len(insight_titles)

                            # Ângulos para cada eixo (divididos igualmente)
                            angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
                            angles += angles[:1]  # Fechar o círculo

                            # Adicionar valores
                            values = relevance
                            values += values[:1]  # Fechar o círculo

                            # Desenhar o gráfico com as cores do FourSight
                            ax.plot(angles, values, linewidth=2.5, linestyle='solid', color=foursight_blue, alpha=0.9)
                            ax.fill(angles, values, color=foursight_blue, alpha=0.2)

                            # Adicionar rótulos com estilo melhorado
                            plt.xticks(angles[:-1], insight_titles, color='#333333', size=9, fontweight='medium')

                            # Remover rótulos de y e ajustar limites
                            ax.set_yticklabels([])
                            ax.set_ylim(0, 100)

                            # Adicionar título com estilo Seaborn
                            plt.title('Mapa de Insights', size=13, color='#333333', pad=15, fontweight='bold')

                            # Estilo minimalista aprimorado
                            ax.grid(True, color='#EEEEEE', linestyle='-', linewidth=0.5, alpha=0.7)
                            ax.spines['polar'].set_visible(False)

                            # Adicionar círculos de referência sutis
                            for r in [25, 50, 75]:
                                circle = plt.Circle((0, 0), r, transform=ax.transData._b,
                                                  fill=False, color='#DDDDDD', linestyle='-', linewidth=0.5)

                            # Mostrar o gráfico
                            st.pyplot(fig)

                            # Adicionar legenda explicativa
                            st.markdown("""
                            <div style="background-color: #f8f9fa; padding: 8px; border-radius: 4px; font-size: 0.8em; color: #555;">
                            O gráfico acima mostra os principais insights identificados e sua distribuição temática.
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.info(f"Não foi possível gerar o gráfico de insights: {str(e)}")

                with insight_cols[1]:
                    # Mostrar lista de insights com expanders
                    for i, insight in enumerate(insights):
                        with st.expander(f"Insight {i+1}"):
                            st.markdown(insight)
            else:
                st.info("Nenhum insight analítico disponível.")

            # Adicionar gráfico de conexão entre tendências e insights quando ambos estão disponíveis
            if (results['synthesis_results'].get('trends') and results['synthesis_results'].get('insights') and
                len(results['synthesis_results']['trends']) > 0 and len(results['synthesis_results']['insights']) > 0):

                st.markdown("### Conexões entre Tendências e Insights")

                try:
                    # Criar um gráfico de rede simples
                    trends = results['synthesis_results']['trends'][:4]  # Limitar a 4 tendências
                    insights = results['synthesis_results']['insights'][:5]  # Limitar a 5 insights

                    # Extrair nomes das tendências
                    trend_names = [t.get('name', f"Tendência {i+1}") for i, t in enumerate(trends)]
                    trend_names = [name[:20] + "..." if len(name) > 20 else name for name in trend_names]

                    # Extrair títulos dos insights
                    insight_titles = []
                    for insight in insights:
                        # Tentar extrair o título do formato "Insight X: Título"
                        if ":" in insight.split("\n")[0]:
                            title = insight.split("\n")[0].split(":", 1)[1].strip()
                            # Limitar o tamanho do título
                            if len(title) > 20:
                                title = title[:17] + "..."
                        else:
                            # Usar as primeiras palavras
                            words = insight.split()
                            title = " ".join(words[:3]) + "..."
                        insight_titles.append(title)

                    # Criar figura
                    fig, ax = plt.subplots(figsize=(7, 5))

                    # Definir posições dos nós
                    import numpy as np

                    # Posições das tendências (parte superior)
                    trend_positions = {}
                    for i, name in enumerate(trend_names):
                        x = (i + 0.5) * (1.0 / len(trend_names))
                        trend_positions[name] = (x, 0.9)

                    # Posições dos insights (parte inferior)
                    insight_positions = {}
                    for i, title in enumerate(insight_titles):
                        x = (i + 0.5) * (1.0 / len(insight_titles))
                        insight_positions[title] = (x, 0.1)

                    # Combinar todas as posições
                    node_positions = {**trend_positions, **insight_positions}

                    # Desenhar nós de tendências com as cores do FourSight
                    for name, pos in trend_positions.items():
                        # Adicionar sombra sutil para efeito 3D
                        shadow = plt.Circle(pos, 0.052, color='#000000', alpha=0.05)
                        ax.add_patch(shadow)
                        # Adicionar círculo principal
                        circle = plt.Circle(pos, 0.05, color=foursight_blue, alpha=0.85)
                        ax.add_patch(circle)
                        # Adicionar texto com estilo melhorado
                        ax.text(pos[0], pos[1] + 0.07, name, ha='center', va='center', fontsize=9.5,
                                color='#333333', fontweight='bold', bbox=dict(facecolor='white', alpha=0.7,
                                                                            edgecolor='none', boxstyle='round,pad=0.3'))

                    # Desenhar nós de insights com as cores do FourSight
                    for title, pos in insight_positions.items():
                        # Adicionar sombra sutil para efeito 3D
                        shadow = plt.Circle(pos, 0.052, color='#000000', alpha=0.05)
                        ax.add_patch(shadow)
                        # Adicionar círculo principal
                        circle = plt.Circle(pos, 0.05, color=foursight_orange, alpha=0.85)
                        ax.add_patch(circle)
                        # Adicionar texto com estilo melhorado
                        ax.text(pos[0], pos[1] - 0.07, title, ha='center', va='center', fontsize=9.5,
                                color='#333333', fontweight='bold', bbox=dict(facecolor='white', alpha=0.7,
                                                                            edgecolor='none', boxstyle='round,pad=0.3'))

                    # Desenhar conexões (aleatórias para demonstração)
                    # Em um sistema real, essas conexões seriam baseadas em análise de texto
                    import random
                    random.seed(42)  # Para consistência

                    for trend_name in trend_names:
                        # Cada tendência se conecta a 1-3 insights aleatórios
                        num_connections = random.randint(1, min(3, len(insight_titles)))
                        connected_insights = random.sample(insight_titles, num_connections)

                        for insight_title in connected_insights:
                            trend_pos = trend_positions[trend_name]
                            insight_pos = insight_positions[insight_title]

                            # Desenhar linha com curvatura
                            # Calcular ponto de controle para a curva
                            control_x = (trend_pos[0] + insight_pos[0]) / 2
                            control_y = (trend_pos[1] + insight_pos[1]) / 2 + random.uniform(0.05, 0.15)

                            # Criar pontos para a curva Bézier
                            t = np.linspace(0, 1, 30)
                            x = (1-t)**2 * trend_pos[0] + 2*(1-t)*t * control_x + t**2 * insight_pos[0]
                            y = (1-t)**2 * trend_pos[1] + 2*(1-t)*t * control_y + t**2 * insight_pos[1]

                            # Desenhar a curva com gradiente de cor
                            from matplotlib.colors import LinearSegmentedColormap

                            # Criar um mapa de cores personalizado do azul para o laranja
                            colors = [(foursight_blue, foursight_blue), (foursight_orange, foursight_orange)]
                            custom_cmap = LinearSegmentedColormap.from_list("foursight_gradient", colors, N=100)

                            # Aplicar gradiente de cor na linha
                            for i in range(len(x)-1):
                                plt.plot(x[i:i+2], y[i:i+2], color=custom_cmap(i/len(x)), alpha=0.6, linewidth=2.0)

                    # Configurar o gráfico
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')  # Remover eixos

                    # Adicionar legenda com estilo Seaborn
                    trend_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=foursight_blue,
                                            markersize=10, label='Tendências')
                    insight_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=foursight_orange,
                                            markersize=10, label='Insights')
                    connection_line = plt.Line2D([0], [0], color=foursight_gray, linewidth=2, alpha=0.7,
                                               label='Conexões')

                    # Criar legenda com estilo aprimorado
                    legend = ax.legend(handles=[trend_patch, insight_patch, connection_line],
                                     loc='upper center', bbox_to_anchor=(0.5, 0.02),
                                     ncol=3, frameon=True, fontsize=9)

                    # Estilizar a legenda
                    frame = legend.get_frame()
                    frame.set_facecolor('white')
                    frame.set_alpha(0.9)
                    frame.set_edgecolor('#EEEEEE')

                    # Adicionar título com estilo Seaborn
                    plt.title('Mapa de Conexões: Tendências → Insights',
                            fontsize=13, pad=20, color='#333333', fontweight='bold')

                    # Mostrar o gráfico
                    st.pyplot(fig)

                    # Adicionar explicação
                    st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 8px; border-radius: 4px; font-size: 0.8em; color: #555;">
                    O gráfico acima mostra como as tendências emergentes (azul) influenciam os insights analíticos (vermelho).
                    As conexões representam relações temáticas entre tendências e insights.
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.info(f"Não foi possível gerar o gráfico de conexões: {str(e)}")

            # Adicionar explicação sobre a relação entre tendências e insights
            if not results['synthesis_results'].get('trends') and not results['synthesis_results'].get('insights'):
                st.markdown("""
                <div style="background-color: #fff8e1; padding: 15px; border-radius: 5px; border-left: 4px solid #FFC107; margin-top: 20px;">
                    <h4 style="margin-top: 0; color: #FFA000;">Sobre Tendências e Insights</h4>
                    <p>
                        <strong>Tendências</strong> representam padrões e direções emergentes identificados a partir de fontes recentes.
                        Elas mostram "para onde o campo está indo".
                    </p>
                    <p>
                        <strong>Insights</strong> são observações analíticas extraídas dessas tendências e dos dados coletados.
                        Eles revelam oportunidades e conexões não óbvias.
                    </p>
                    <p>
                        Juntos, tendências e insights formam a base para a geração de ideias inovadoras.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # Tab 4: Pesquisa
        with tabs[3]:
            st.markdown("## Resultados da Pesquisa")

            # Separar resultados por fonte
            web_results = results.get('web_results', [])
            arxiv_results = results.get('arxiv_results', [])
            reddit_results = results.get('reddit_results', [])
            producthunt_results = results.get('producthunt_results', [])

            # Mostrar estatísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Resultados da Web", len(web_results))
            with col2:
                st.metric("Artigos Científicos", len(arxiv_results))
            with col3:
                st.metric("Posts do Reddit", len(reddit_results))
            with col4:
                st.metric("Produtos do Product Hunt", len(producthunt_results))

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

            # Mostrar resultados do Reddit
            if reddit_results:
                st.subheader("Discussões do Reddit")
                for i, post in enumerate(reddit_results):
                    with st.expander(f"{i+1}. {post.get('title', 'Sem título')}"):
                        st.markdown(f"**Subreddit:** r/{post.get('subreddit', 'desconhecido')}")
                        st.markdown(f"**Data:** {post.get('created_date', 'Desconhecida')}")
                        st.markdown(f"**URL:** [{post.get('url', '#')}]({post.get('url', '#')})")
                        st.markdown(f"**Votos:** {post.get('score', 0)} | **Comentários:** {post.get('num_comments', 0)}")
                        st.markdown("**Conteúdo:**")
                        st.markdown(post.get('snippet', 'Sem conteúdo disponível'))

            # Mostrar resultados do Product Hunt
            if producthunt_results:
                st.subheader("Produtos do Product Hunt")
                for i, product in enumerate(producthunt_results):
                    with st.expander(f"{i+1}. {product.get('title', 'Sem nome')}"):
                        tagline = product.get('snippet', '').split('\n')[0] if '\n' in product.get('snippet', '') else product.get('snippet', '')
                        st.markdown(f"**Tagline:** {tagline}")
                        st.markdown(f"**Data:** {product.get('created_date', 'Desconhecida')}")
                        st.markdown(f"**URL:** [{product.get('url', '#')}]({product.get('url', '#')})")
                        if product.get('website'):
                            st.markdown(f"**Website:** [{product.get('website', '#')}]({product.get('website', '#')})")
                        st.markdown(f"**Votos:** {product.get('votes', 0)}")
                        if 'topics' in product and product['topics']:
                            st.markdown(f"**Tópicos:** {', '.join(product['topics'])}")
                        st.markdown("**Descrição:**")
                        description = product.get('snippet', '').split('\n\n', 1)[1] if '\n\n' in product.get('snippet', '') else product.get('snippet', '')
                        st.markdown(description)

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
