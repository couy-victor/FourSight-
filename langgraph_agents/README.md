# Sistema Multiagentes de Inovação com LangGraph

Este diretório contém a implementação do Sistema Multiagentes de Inovação utilizando o framework LangGraph.

## Estrutura

A implementação segue o padrão de fluxo de trabalho do LangGraph, com os seguintes componentes:

- **Estado**: Representado pela classe `InnovationState`, que mantém todos os dados compartilhados entre os nós do grafo.
- **Nós**: Cada agente do sistema original foi convertido em um nó do grafo LangGraph.
- **Grafo**: Define o fluxo de trabalho entre os nós, com as transições e condições.
- **Orquestrador**: Coordena a execução do grafo e mantém compatibilidade com a interface do orquestrador original.

## Arquivos

- `state.py`: Define a classe `InnovationState` que representa o estado do grafo.
- `researcher_node.py`: Implementa o nó de pesquisa.
- `processor_node.py`: Implementa o nó de processamento de PDFs.
- `synthesizer_node.py`: Implementa o nó de síntese.
- `idealizer_node.py`: Implementa o nó de ideação.
- `evaluator_node.py`: Implementa o nó de avaliação.
- `graph.py`: Define o grafo e o fluxo de trabalho.
- `orchestrator.py`: Implementa o orquestrador baseado em LangGraph.

## Fluxo de Trabalho

O fluxo de trabalho do sistema é o seguinte:

1. **Pesquisa** (`researcher_node`): Coleta informações da web e artigos científicos.
2. **Processamento** (`processor_node`): Processa os PDFs dos artigos encontrados.
3. **Relatório de Pesquisa** (`processor_node`): Gera um relatório com base nos resultados da pesquisa.
4. **Síntese** (`synthesizer_node`): Extrai insights do relatório de pesquisa.
5. **Ideação** (`idealizer_node`): Gera ideias inovadoras com base nos insights.
6. **Avaliação** (`evaluator_node`): Avalia as ideias geradas.
7. **Relatório Final** (`evaluator_node`): Gera um relatório final com as ideias avaliadas.

## Uso

### Uso Direto

```python
from langgraph_agents import LangGraphOrchestrator

# Criar o orquestrador
orchestrator = LangGraphOrchestrator()

# Executar o processo de inovação
results = orchestrator.run_innovation_process(
    topic="Inteligência Artificial na Saúde",
    business_context="Uma empresa de tecnologia em saúde busca desenvolver soluções inovadoras...",
    max_research_results=3,
    max_papers_to_process=2
)

# Acessar os resultados
print(results['final_report'])
```

### Uso com Interface Streamlit

Execute o arquivo `example_langgraph.py` para usar o sistema com a interface Streamlit:

```
streamlit run example_langgraph.py
```

## Compatibilidade

O orquestrador LangGraph mantém compatibilidade com a interface do orquestrador original, permitindo chamadas como:

```python
orchestrator = LangGraphOrchestrator()

# Usar a interface do ResearcherAgent
research_results = orchestrator.researcher.research(topic="IA na Saúde", max_results=3)

# Usar a interface do SynthesizerAgent
orchestrator.synthesizer.set_business_context("Contexto de negócio...")
synthesis_results = orchestrator.synthesizer.synthesize(research_report)
```

## Testes

Para testar a implementação, execute o arquivo `test_langgraph.py`:

```
python test_langgraph.py
```
