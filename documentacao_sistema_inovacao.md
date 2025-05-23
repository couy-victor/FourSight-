# Documentação do Sistema Multiagentes de Inovação com LangGraph

## 1. Visão Geral do Sistema

O FourSight é um sistema multiagentes de inovação avançado que utiliza a arquitetura LangGraph e o modelo Llama 4 para gerar ideias inovadoras baseadas em pesquisas científicas recentes, tendências emergentes de mercado e contexto de negócio. O sistema foi projetado para processar informações de múltiplas fontes, analisar tendências atuais (2023-2025) e gerar insights e ideias inovadoras relevantes para o contexto de negócio fornecido.

### 1.1 Arquitetura do Sistema

O sistema utiliza uma arquitetura de grafo baseada em LangGraph, onde cada nó representa um agente especializado com uma função específica no processo de inovação. Os agentes trabalham em sequência, passando informações entre si através de um estado compartilhado, permitindo um fluxo de trabalho coeso e eficiente.

### 1.2 Componentes Principais

O sistema é composto pelos seguintes componentes principais:

1. **Interface do Usuário (Streamlit)**: Interface web interativa para interação com o sistema
2. **Orquestrador LangGraph**: Coordena o fluxo de trabalho entre os agentes
3. **Agentes Especializados**: Conjunto de agentes com funções específicas
4. **Sistema RAG (Retrieval Augmented Generation)**: Melhora a qualidade das respostas com base em documentos externos
5. **APIs Externas**: Integração com serviços como Groq (Llama 4), arXiv, SERPER, Reddit e Product Hunt

## 2. Fluxo de Trabalho do Sistema

O processo de inovação segue um fluxo de trabalho estruturado:

### 2.1 Entrada de Dados

O usuário fornece:
- **Tópico de Pesquisa**: Área de interesse para geração de ideias
- **Contexto de Negócio**: Descrição do problema ou oportunidade de negócio
- **Configurações**: Número de resultados de pesquisa, artigos a processar, etc.

### 2.2 Processo de Inovação

1. **Pesquisa Direcionada** (ResearcherNode)
   - Pesquisa na web usando a API SERPER (resultados de 2024-2025)
   - Pesquisa de artigos científicos no arXiv (em inglês)
   - Pesquisa de discussões no Reddit sobre o tópico
   - Pesquisa de produtos inovadores no Product Hunt
   - Coleta e organização dos resultados via MCP (Model Context Protocol)

2. **Processamento de Artigos** (ProcessorNode)
   - Download e extração de texto de PDFs
   - Implementação de RAG (Retrieval Augmented Generation)
   - Geração de resumos inteligentes dos artigos

3. **Análise de Tendências** (TrendAnalyzerNode)
   - Identificação de tendências emergentes a partir das fontes pesquisadas
   - Classificação por nível de maturidade (Emergente, Em crescimento, Estabelecida)
   - Análise de impacto no contexto de negócio

4. **Síntese Contextual** (SynthesizerNode)
   - Geração de insights baseados nas tendências e no contexto
   - Conexão entre tendências e oportunidades de negócio
   - Criação de visualizações para facilitar a compreensão

5. **Ideação Estratégica** (IdealizerNode)
   - Geração de ideias inovadoras com nomes de produtos/serviços memoráveis
   - Alinhamento com as tendências identificadas
   - Consideração do contexto de negócio

6. **Avaliação Criteriosa** (EvaluatorNode)
   - Análise crítica das ideias geradas
   - Pontuação baseada em múltiplos critérios
   - Justificativas detalhadas para cada pontuação

7. **Geração de Relatório Final**
   - Compilação dos resultados em um relatório estruturado
   - Visualizações e gráficos para facilitar a compreensão
   - Opção de exportação para PDF

## 3. Análise de Tendências em Detalhes

A análise de tendências é um componente central do sistema, realizada pelo TrendAnalyzerNode. Este processo transforma dados brutos de pesquisa em insights acionáveis sobre tendências emergentes.

### 3.1 Coleta de Dados para Análise

O sistema coleta dados de cinco fontes principais:
- **Resultados da Web**: Informações recentes (2024-2025) de sites, blogs e notícias
- **Artigos Científicos**: Publicações acadêmicas do arXiv relacionadas ao tópico
- **Discussões do Reddit**: Conversas e opiniões de usuários sobre o tópico
- **Produtos do Product Hunt**: Produtos e serviços inovadores recentemente lançados
- **Artigos Processados**: Conteúdo extraído e processado de PDFs com RAG

### 3.2 Processo de Análise de Tendências

1. **Preparação do Contexto**
   ```python
   web_context = self._prepare_web_context(web_results)
   arxiv_context = self._prepare_arxiv_context(arxiv_results)
   reddit_context = self._prepare_reddit_context(reddit_results)
   producthunt_context = self._prepare_producthunt_context(producthunt_results)
   papers_context = self._prepare_papers_context(processed_papers)
   ```

2. **Geração do Prompt de Análise**
   - Criação de um prompt detalhado que inclui:
     - Tópico de pesquisa
     - Contexto de negócio
     - Dados da web, arXiv, Reddit, Product Hunt e artigos processados
     - Instruções para identificação de tendências

3. **Processamento com IA (Llama 4 via Groq)**
   - Utilização do modelo Llama 4 para analisar os dados
   - Sistema de mensagem especializado para análise de tendências

4. **Estruturação dos Resultados**
   - Para cada tendência identificada:
     - Nome da tendência
     - Nível de maturidade
     - Descrição detalhada
     - Fontes específicas
     - Impacto no contexto de negócio

### 3.3 Visualização de Tendências

O sistema gera visualizações interativas para facilitar a compreensão das tendências:

1. **Tabela de Tendências**
   - Lista organizada com nome e nível de maturidade
   - Código de cores para diferentes níveis de maturidade

2. **Detalhes Expandidos**
   - Descrição completa de cada tendência
   - Fontes que mencionam a tendência
   - Análise de impacto no contexto de negócio

3. **Gráfico de Conexões**
   - Mapa visual mostrando relações entre tendências e insights
   - Utiliza a biblioteca Seaborn para visualizações de alta qualidade
   - Cores personalizadas (azul FourSight para tendências, laranja para insights)

## 4. Implementação do RAG (Retrieval Augmented Generation)

O sistema implementa RAG para melhorar a qualidade das análises e insights gerados a partir de artigos científicos.

### 4.1 Processamento de PDFs

1. **Download e Extração de Texto**
   - Download de PDFs a partir de URLs
   - Extração de texto usando PyPDF
   - Métodos alternativos de extração para casos problemáticos

2. **Chunking e Indexação**
   - Divisão do texto em chunks gerenciáveis
   - Criação de índices para busca eficiente

### 4.2 Sistema RAG BM25

O sistema utiliza uma implementação híbrida de RAG que combina:

1. **Busca Semântica (Embeddings)**
   - Utiliza SentenceTransformer para gerar embeddings
   - Calcula similaridade de cosseno entre a consulta e os chunks

2. **Busca Léxica (BM25)**
   - Implementa o algoritmo BM25Okapi para ranking de relevância
   - Considera frequência de termos e raridade

3. **Abordagem Híbrida**
   - Combina resultados de ambas as abordagens
   - Parâmetro alpha para balancear embeddings vs BM25
   - Normalização de scores para comparação justa

### 4.3 Geração de Resumos com Contexto

```python
def summarize_with_context(self, query: str, api_function) -> str:
    # Obter resultados relevantes
    results = self.query(query)

    # Construir contexto com os resultados
    context = ""
    for result in results:
        context += f"\n\n[Trecho {result['rank']} (score={result['score']:.2f})]\n{result['text']}"

    # Criar prompt para resumo
    prompt = f"""
    Com base nos seguintes trechos de um artigo científico, {query}

    {context}

    Forneça um resumo detalhado que capture as informações mais importantes.
    """

    # Chamar a API para gerar o resumo
    system_message = "Você é um especialista em resumir artigos científicos de forma precisa e informativa."
    summary = api_function(prompt, system_message, 800)

    return summary
```

## 5. Geração de Visualizações

O sistema utiliza bibliotecas como Matplotlib e Seaborn para criar visualizações de alta qualidade que facilitam a compreensão dos resultados.

### 5.1 Configuração Visual

```python
# Configurar tema do Seaborn para todos os gráficos
sns.set_theme(style="whitegrid", palette=[foursight_blue, foursight_orange, foursight_green, foursight_red])
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['axes.edgecolor'] = '#dddddd'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.color'] = '#eeeeee'
plt.rcParams['grid.linestyle'] = ':'
```

### 5.2 Tipos de Visualizações

1. **Gráficos de Barras para Avaliação de Ideias**
   - Visualização das pontuações por critério
   - Código de cores baseado na pontuação
   - Estilo limpo e profissional

2. **Gráficos de Radar para Insights**
   - Representação visual das categorias de insights
   - Estilo minimalista com cores da marca

3. **Mapas de Conexão**
   - Visualização das relações entre tendências e insights
   - Linhas curvas com gradiente de cor
   - Legenda explicativa

## 6. Fluxo de Dados entre Agentes

O sistema utiliza um estado compartilhado (InnovationState) para passar dados entre os agentes, garantindo um fluxo coeso de informações. O Model Context Protocol (MCP) centraliza a conexão com diferentes APIs e fontes de dados.

### 6.1 Estrutura do Estado

```python
class InnovationState(BaseModel):
    # Entradas do usuário
    topic: str
    business_context: str

    # Configurações
    max_web_results: int
    max_arxiv_results: int
    max_papers_to_process: int

    # Resultados da pesquisa
    research_results: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    arxiv_results: List[Dict[str, Any]]
    reddit_results: List[Dict[str, Any]]
    producthunt_results: List[Dict[str, Any]]

    # Artigos processados
    processed_papers: List[Dict[str, Any]]

    # Relatórios e sínteses
    research_report: str
    trends: List[Dict[str, Any]]
    insights: List[str]

    # Ideias e avaliações
    ideas: List[Dict[str, Any]]
    evaluated_ideas: List[Dict[str, Any]]

    # Relatório final
    final_report: str

    # Estado de execução
    current_stage: str
    error: Optional[str]
```

### 6.2 Grafo de Execução

```python
def create_innovation_graph():
    # Criar os nós
    researcher = ResearcherNode()
    processor = ProcessorNode()
    trend_analyzer = TrendAnalyzerNode()
    synthesizer = SynthesizerNode()
    idealizer = IdealizerNode()
    evaluator = EvaluatorNode()

    # Criar o grafo
    builder = StateGraph(InnovationState)

    # Adicionar os nós ao grafo
    builder.add_node("researcher", researcher.run)
    builder.add_node("processor", processor.run)
    builder.add_node("report_generator", processor.generate_research_report)
    builder.add_node("trend_analyzer", trend_analyzer.run)
    builder.add_node("synthesizer", synthesizer.run)
    builder.add_node("idealizer", idealizer.run)
    builder.add_node("evaluator", evaluator.run)
    builder.add_node("report_finalizer", evaluator.generate_final_report)

    # Definir as arestas (fluxo de trabalho)
    builder.add_edge("researcher", "processor")
    builder.add_edge("processor", "report_generator")
    builder.add_edge("report_generator", "trend_analyzer")
    builder.add_edge("trend_analyzer", "synthesizer")
    builder.add_edge("synthesizer", "idealizer")
    builder.add_edge("idealizer", "evaluator")
    builder.add_edge("evaluator", "report_finalizer")
    builder.add_edge("report_finalizer", END)

    # Definir o nó inicial
    builder.set_entry_point("researcher")

    # Compilar o grafo
    return builder.compile()
```

## 7. Interface do Usuário

A interface do usuário é implementada com Streamlit, oferecendo uma experiência interativa e amigável.

### 7.1 Componentes da Interface

1. **Formulário de Entrada**
   - Campo para tópico de pesquisa
   - Área de texto para contexto de negócio
   - Configurações avançadas (opcional)

2. **Indicador de Progresso**
   - Barra de progresso animada
   - Mensagens de status em tempo real

3. **Abas de Resultados**
   - **Relatório**: Visão geral do processo e resultados
   - **Ideias**: Lista de ideias geradas com avaliações
   - **Análises & Tendências**: Tendências identificadas e insights
   - **Dados Brutos**: Resultados de pesquisa e artigos processados

### 7.2 Visualizações Interativas

- Tabelas interativas com formatação condicional
- Gráficos responsivos com estilo personalizado
- Expanders para mostrar/ocultar detalhes

## 8. Considerações Técnicas

### 8.1 APIs Utilizadas

1. **Groq API com Llama 4**
   - Modelo: 'meta-llama/llama-4-scout-17b-16e-instruct'
   - Utilizado para geração de texto de alta qualidade

2. **arXiv API**
   - Endpoint: http://export.arxiv.org/api/
   - Utilizado para pesquisa de artigos científicos

3. **SERPER API**
   - Utilizado para pesquisa na web com resultados recentes

4. **Reddit API**
   - Endpoint: https://www.reddit.com/dev/api/
   - Utilizado para obter discussões e opiniões de usuários

5. **Product Hunt API**
   - Endpoint: https://api.producthunt.com/v2/docs
   - Utilizado para descobrir produtos e serviços inovadores recentes

### 8.2 Bibliotecas Principais

- **LangGraph**: Framework para criação de agentes conectados em grafo
- **Streamlit**: Interface web interativa
- **PyPDF**: Processamento de documentos PDF
- **FAISS/BM25**: Sistemas de recuperação de informação
- **Matplotlib/Seaborn**: Visualização de dados

### 8.3 Tratamento de Erros

O sistema implementa tratamento de erros em vários níveis:
- Fallbacks para métodos alternativos quando o principal falha
- Captura e registro de exceções
- Retorno de resultados parciais em caso de falha

## 9. Conclusão

O Sistema Multiagentes de Inovação com LangGraph representa uma abordagem avançada para geração de ideias inovadoras baseadas em dados recentes e relevantes. Através da combinação de múltiplos agentes especializados, RAG e visualizações interativas, o sistema oferece uma solução completa para o processo de inovação, desde a pesquisa inicial até a avaliação final das ideias geradas.

A arquitetura modular baseada em LangGraph permite fácil extensão e personalização, enquanto a interface Streamlit proporciona uma experiência de usuário intuitiva e informativa. O sistema demonstra como a IA pode ser aplicada de forma eficaz para impulsionar a inovação em diversos contextos de negócio.
