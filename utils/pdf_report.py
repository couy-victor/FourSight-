import os
import io
import base64
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional
from matplotlib.figure import Figure

# Verificar se as bibliotecas necessárias estão disponíveis
PDF_AVAILABLE = False
try:
    # Tentar importar as bibliotecas necessárias
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        from fpdf import FPDF
        from matplotlib.figure import Figure
        PDF_AVAILABLE = True
    except ValueError as ve:
        # Capturar especificamente o erro de incompatibilidade do NumPy
        if "numpy.dtype size changed" in str(ve):
            print("Aviso: Detectada incompatibilidade de versão do NumPy. Desativando funcionalidades de PDF avançadas.")
            PDF_AVAILABLE = False
        else:
            raise
except ImportError:
    print("Aviso: Bibliotecas para geração de PDF não encontradas. Usando funcionalidades básicas.")

# Criar classes e funções dummy para quando as bibliotecas não estão disponíveis
if not PDF_AVAILABLE:
    class FPDF:
        def __init__(self, *args, **kwargs):
            pass


class InnovationReport(FPDF):
    """
    Classe para gerar relatórios de inovação em PDF.
    Baseada na biblioteca FPDF.
    """

    def __init__(self, title="Relatório de Inovação", orientation="P", unit="mm", format="A4"):
        """
        Inicializa o relatório.

        Args:
            title: Título do relatório
            orientation: Orientação da página ('P' para retrato, 'L' para paisagem)
            unit: Unidade de medida
            format: Formato da página
        """
        super().__init__(orientation=orientation, unit=unit, format=format)
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        """Define o cabeçalho do relatório."""
        # Título
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, self.title, 0, 1, 'C')
        # Data
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'R')
        # Linha
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        """Define o rodapé do relatório."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        """
        Adiciona um título de capítulo.

        Args:
            title: Título do capítulo
        """
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def section_title(self, title):
        """
        Adiciona um título de seção.

        Args:
            title: Título da seção
        """
        self.set_font('Arial', 'B', 11)
        self.cell(0, 6, title, 0, 1, 'L')
        self.ln(2)

    def body_text(self, text):
        """
        Adiciona texto ao corpo do relatório.

        Args:
            text: Texto a ser adicionado
        """
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def add_image(self, img_path, w=0, h=0, caption=""):
        """
        Adiciona uma imagem ao relatório.

        Args:
            img_path: Caminho para a imagem
            w: Largura (0 para automático)
            h: Altura (0 para automático)
            caption: Legenda da imagem
        """
        self.image(img_path, x=None, y=None, w=w, h=h)
        if caption:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 5, caption, 0, 1, 'C')
        self.ln(5)

    def add_figure(self, fig: Figure, w=180, h=90, caption=""):
        """
        Adiciona uma figura do matplotlib ao relatório.

        Args:
            fig: Figura do matplotlib
            w: Largura
            h: Altura
            caption: Legenda da figura
        """
        # Salvar a figura em um arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            fig.savefig(tmp.name, format='png', bbox_inches='tight')
            tmp_name = tmp.name

        # Adicionar a imagem ao PDF
        self.add_image(tmp_name, w, h, caption)

        # Remover o arquivo temporário
        os.unlink(tmp_name)

    def add_table(self, data, headers=None, col_widths=None):
        """
        Adiciona uma tabela ao relatório.

        Args:
            data: Lista de listas com os dados da tabela
            headers: Lista com os cabeçalhos da tabela
            col_widths: Lista com as larguras das colunas
        """
        # Configurações da tabela
        line_height = 6
        if col_widths is None:
            col_widths = [40] * len(data[0])  # Largura padrão para todas as colunas

        # Cabeçalhos
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(200, 220, 255)
        if headers:
            for i, header in enumerate(headers):
                self.cell(col_widths[i], line_height, header, 1, 0, 'C', 1)
            self.ln(line_height)

        # Dados
        self.set_font('Arial', '', 9)
        self.set_fill_color(255, 255, 255)
        fill = False
        for row in data:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], line_height, str(cell), 1, 0, 'L', fill)
            self.ln(line_height)
            fill = not fill  # Alternar cores das linhas
        self.ln(5)


def generate_innovation_report(results: Dict[str, Any]) -> str:
    """
    Gera um relatório de inovação em PDF.

    Args:
        results: Dicionário com os resultados do processo de inovação

    Returns:
        Caminho para o arquivo PDF gerado ou mensagem de erro se as bibliotecas não estiverem disponíveis
    """
    # Verificar se as bibliotecas necessárias estão disponíveis
    if not PDF_AVAILABLE:
        return "ERROR: As bibliotecas necessárias para gerar PDFs não estão instaladas. Execute 'pip install fpdf reportlab matplotlib'."
    # Extrair dados
    topic = results.get('topic', 'Inovação')
    business_context = results.get('business_context', '')
    final_report = results.get('final_report', '')
    synthesis_results = results.get('synthesis_results', {})

    # Criar relatório
    pdf = InnovationReport(title=f"Relatório de Inovação: {topic}")

    # Introdução
    pdf.chapter_title("Introdução")
    pdf.body_text(f"Este relatório apresenta os resultados do processo de inovação sobre o tema '{topic}'.")
    pdf.body_text("Contexto de Negócio:")
    pdf.body_text(business_context)

    # Insights
    if 'insights' in synthesis_results and synthesis_results['insights']:
        pdf.chapter_title("Principais Insights")
        for i, insight in enumerate(synthesis_results['insights']):
            pdf.section_title(f"Insight {i+1}")
            pdf.body_text(insight)

    # Ideias Geradas
    if 'evaluated_ideas' in synthesis_results and synthesis_results['evaluated_ideas']:
        pdf.chapter_title("Ideias Inovadoras")

        # Tabela resumo das ideias
        pdf.section_title("Resumo das Ideias")
        headers = ["Nº", "Ideia", "Pontuação"]
        data = []

        for i, idea_data in enumerate(synthesis_results['evaluated_ideas']):
            # Extrair o título da ideia (primeira linha)
            idea_lines = idea_data['idea'].split('\n')
            idea_title = idea_lines[0] if idea_lines else f"Ideia {i+1}"

            # Adicionar à tabela
            data.append([
                i+1,
                idea_title,
                f"{idea_data['average_score']:.1f}/10"
            ])

        # Definir larguras das colunas
        col_widths = [15, 140, 35]
        pdf.add_table(data, headers, col_widths)

        # Detalhes de cada ideia
        for i, idea_data in enumerate(synthesis_results['evaluated_ideas']):
            pdf.add_page()
            pdf.section_title(f"Ideia {i+1}: {idea_data['average_score']:.1f}/10")

            # Descrição da ideia
            pdf.body_text(idea_data['idea'])

            # Avaliação
            pdf.section_title("Avaliação")
            pdf.body_text(idea_data['evaluation'])

            # Gráfico de pontuações
            if 'scores' in idea_data:
                scores_data = {k: v['score'] for k, v in idea_data['scores'].items()}
                df = pd.DataFrame(list(scores_data.items()), columns=['Critério', 'Pontuação'])

                # Usar um estilo clean preto e branco
                # Definir tons de cinza para as barras
                colors = []
                for score in df['Pontuação']:
                    # Usar diferentes tons de cinza baseados na pontuação
                    if score >= 8.5:
                        colors.append('#333333')  # Cinza escuro para pontuações excelentes
                    elif score >= 7:
                        colors.append('#555555')  # Cinza médio para pontuações boas
                    elif score >= 5.5:
                        colors.append('#777777')  # Cinza claro para pontuações médias
                    else:
                        colors.append('#999999')  # Cinza muito claro para pontuações baixas

                # Criar gráfico de barras com tamanho reduzido
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.grid(True, axis='x', linestyle='--', alpha=0.7)
                bars = ax.barh(df['Critério'], df['Pontuação'], color=colors, height=0.6,
                              edgecolor='gray', linewidth=0.5)

                # Adicionar valores nas barras
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                           f'{width:.1f}', va='center', fontweight='bold')

                # Personalizar eixos
                ax.set_xlim(0, 10.5)
                ax.set_xlabel('Pontuação', fontweight='bold')
                ax.set_title('Avaliação por Critério', fontweight='bold', fontsize=14)

                # Remover bordas desnecessárias
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # Adicionar uma linha vertical para a média
                avg_score = idea_data['average_score']
                ax.axvline(x=avg_score, color='red', linestyle='--', alpha=0.7)
                ax.text(avg_score, -0.5, f'Média: {avg_score:.1f}',
                       color='red', fontweight='bold', ha='center')

                # Adicionar áreas de classificação
                ax.axvspan(0, 5, alpha=0.1, color='red')
                ax.axvspan(5, 7, alpha=0.1, color='yellow')
                ax.axvspan(7, 9, alpha=0.1, color='lightgreen')
                ax.axvspan(9, 10.5, alpha=0.1, color='green')

                # Adicionar ao PDF
                pdf.add_figure(fig, w=180, h=90, caption="Pontuações por critério")
                plt.close(fig)

                # Criar gráfico de radar
                categories = list(scores_data.keys())
                values = list(scores_data.values())

                # Adicionar o primeiro valor novamente para fechar o polígono
                categories = categories + [categories[0]]
                values = values + [values[0]]

                # Criar ângulos para o gráfico de radar
                N = len(categories) - 1
                angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
                angles += [angles[0]]

                # Criar figura com tamanho reduzido
                fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

                # Usar estilo clean preto e branco para o radar também
                ax.plot(angles, values, linewidth=2, linestyle='solid', color='#333333')
                ax.fill(angles, values, color='#333333', alpha=0.2)

                # Adicionar rótulos
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories[:-1], fontweight='bold')

                # Configurar limites do eixo y
                ax.set_ylim(0, 10)

                # Adicionar círculos de referência
                ax.set_yticks([2, 4, 6, 8, 10])
                ax.set_yticklabels(['2', '4', '6', '8', '10'])
                ax.grid(True)

                # Adicionar título
                plt.title('Perfil de Avaliação da Ideia', fontweight='bold', fontsize=14, y=1.1)

                # Adicionar ao PDF
                pdf.add_figure(fig, w=150, h=150, caption="Visualização em radar dos critérios")
                plt.close(fig)

                # Justificativas
                pdf.section_title("Justificativas das Pontuações")
                for criterion, data in idea_data['scores'].items():
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(0, 5, f"{criterion}:", 0, 1)
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 5, data['justification'])
                    pdf.ln(2)

    # Relatório Final
    if final_report:
        pdf.add_page()
        pdf.chapter_title("Relatório Final")
        pdf.body_text(final_report)

    # Criar diretório para PDFs temporários se não existir
    temp_dir = os.path.join(os.getcwd(), "temp_pdfs")
    os.makedirs(temp_dir, exist_ok=True)

    # Salvar o PDF
    output_path = os.path.join(temp_dir, f"relatorio_inovacao_{topic.replace(' ', '_')}.pdf")
    pdf.output(output_path)

    return output_path


def get_pdf_download_link(pdf_path: str) -> str:
    """
    Cria um link de download para um arquivo PDF.

    Args:
        pdf_path: Caminho para o arquivo PDF ou mensagem de erro

    Returns:
        HTML com o link de download ou mensagem de erro
    """
    # Verificar se o caminho é uma mensagem de erro
    if pdf_path.startswith("ERROR:"):
        return f'<p style="color: red;">{pdf_path}</p>'

    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        b64 = base64.b64encode(pdf_bytes).decode()
        filename = os.path.basename(pdf_path)

        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Clique aqui para baixar o relatório em PDF</a>'
    except Exception as e:
        return f'<p style="color: red;">Erro ao gerar link de download: {str(e)}</p>'
