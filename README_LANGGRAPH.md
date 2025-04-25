# FourSight - Sistema Multiagentes de Inovação com LangGraph

Este repositório contém a implementação do Sistema Multiagentes de Inovação FourSight utilizando o framework LangGraph. O sistema gera ideias inovadoras baseadas em pesquisas recentes da web e artigos científicos relevantes.

## Características

- **Framework LangGraph**: Implementação moderna usando fluxo de trabalho estruturado
- **Modelo Llama 4**: Utiliza o modelo Llama 4 via API Groq para processamento de linguagem natural
- **Pesquisas Recentes**: Busca informações da web de 2024-2025
- **Artigos Científicos**: Integração com arXiv para buscar artigos relevantes
- **Análise de Tendências**: Identifica tendências emergentes a partir das fontes pesquisadas
- **RAG (Retrieval Augmented Generation)**: Processamento avançado de PDFs
- **Visualizações Interativas**: Gráficos e visualizações de insights e tendências

## Requisitos

```
pip install -r requirements_langgraph.txt
```

Principais dependências:
- streamlit
- matplotlib
- seaborn
- pandas
- langgraph
- langchain
- sentence-transformers
- rank-bm25

## Configuração

1. Crie um arquivo `.env` baseado no `.env.example` com suas chaves de API:
   ```
   GROQ_API_KEY=sua_chave_groq_aqui
   SERPER_API_KEY=sua_chave_serper_aqui
   ```

2. Instale as dependências:
   ```
   pip install -r requirements_langgraph.txt
   ```

## Uso

Execute o aplicativo Streamlit:

```
streamlit run innovation_system_langgraph.py
```

## Estrutura do Projeto

- `innovation_system_langgraph.py`: Aplicativo Streamlit principal
- `langgraph_agents/`: Implementação dos agentes usando LangGraph
  - `state.py`: Definição do estado compartilhado entre os agentes
  - `graph.py`: Definição do grafo de fluxo de trabalho
  - `researcher_node.py`: Agente de pesquisa (web e arXiv)
  - `processor_node.py`: Agente de processamento de PDFs
  - `trend_analyzer_node.py`: Agente de análise de tendências
  - `synthesizer_node.py`: Agente de síntese de informações
  - `idealizer_node.py`: Agente de geração de ideias
  - `evaluator_node.py`: Agente de avaliação de ideias
  - `orchestrator.py`: Coordenador do fluxo de trabalho
- `utils/`: Utilitários e funções auxiliares
  - `api_utils.py`: Funções para chamadas de API
  - `rag_bm25.py`: Implementação do sistema RAG
  - `pdf_report.py`: Geração de relatórios em PDF

## Fluxo de Trabalho

1. **Pesquisa**: Coleta de informações recentes da web e artigos científicos
2. **Processamento**: Análise de PDFs e extração de conhecimento com RAG
3. **Análise de Tendências**: Identificação de tendências emergentes
4. **Síntese**: Geração de insights a partir das tendências e dados coletados
5. **Ideação**: Criação de ideias inovadoras com nomes de produtos/serviços
6. **Avaliação**: Análise crítica das ideias geradas

## Visualizações

O sistema inclui visualizações interativas:
- Gráfico de radar para insights
- Mapa de conexões entre tendências e insights
- Gráficos de avaliação de ideias

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests ou abrir issues.

## Licença

Este projeto está licenciado sob os termos da licença MIT.
