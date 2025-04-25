# Sistema Multiagentes para Inovação

Um sistema baseado em múltiplos agentes de IA especializados para gerar ideias inovadoras a partir de dores de negócio, artigos e tendências de mercado.

## Visão Geral

Este sistema utiliza uma arquitetura de agentes especializados para processar diferentes tipos de entrada (dores de negócio ou tópicos de interesse) e gerar ideias inovadoras contextualizadas para setores específicos.

### Agentes Especializados

1. **Agente Pesquisador**: Busca artigos e informações relevantes
2. **Agente Contextual**: Entende o contexto específico do setor e problema
3. **Agente Sintetizador**: Combina informações de múltiplas fontes
4. **Agente Idealizador**: Gera ideias inovadoras baseadas na síntese
5. **Agente Avaliador**: Avalia e prioriza as ideias geradas

## Instalação

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente:
   - Copie o arquivo `.env.example` para `.env`
   - Adicione suas chaves de API (OpenAI, Serper)

## Uso

Execute o Sistema Completo de Inovação:

```
streamlit run innovation_system.py
```

Ou use o script de testes para escolher entre diferentes componentes:

```
python run_tests.py
```

### Funcionalidades do Sistema Completo

O sistema oferece uma interface intuitiva que permite:

- **Configurar o processo de inovação**:
  - Definir tópicos de pesquisa específicos
  - Descrever o contexto de negócio detalhadamente
  - Ajustar parâmetros avançados como número de resultados

- **Visualizar resultados em múltiplas perspectivas**:
  - Relatório final completo com recomendações
  - Lista de ideias inovadoras com avaliações detalhadas
  - Insights extraídos da pesquisa
  - Resultados brutos da pesquisa na web e artigos científicos
  - Resumos de PDFs processados com RAG

- **Analisar ideias em profundidade**:
  - Gráficos de pontuação para cada critério de avaliação
  - Justificativas detalhadas para cada pontuação
  - Comparação de ideias através de tabelas interativas

- **Exportar resultados**:
  - Baixar relatórios para compartilhar com stakeholders

## Fluxos de Trabalho

### Fluxo Baseado em Dores de Negócio

1. Usuário descreve uma dor ou desafio específico
2. Agente Contextual categoriza e estrutura o problema
3. Agente Pesquisador busca soluções ou abordagens relacionadas
4. Agente Sintetizador conecta o problema com possíveis soluções
5. Agente Idealizador propõe produtos ou abordagens
6. Agente Avaliador prioriza com base na relevância para a dor original

### Fluxo Baseado em Tópicos de Interesse

1. Usuário fornece um tópico de interesse (ex: "blockchain", "open banking")
2. Agente Pesquisador busca artigos relevantes
3. Agente Contextual adapta para o setor específico
4. Agente Sintetizador identifica conceitos-chave
5. Agente Idealizador gera produtos ou soluções potenciais
6. Agente Avaliador filtra as melhores ideias

## Requisitos

- Python 3.8+
- Streamlit
- Groq API (para processamento de linguagem natural com Llama 4)
- Google Gemini API (alternativa para processamento de linguagem natural)
- Serper API (para busca na web)
- arXiv API (para busca de artigos acadêmicos)

## APIs Utilizadas

### Groq API
Utilizamos a Groq API com o modelo Llama 4 8B Fast para processamento de linguagem natural. A Groq oferece alta performance e baixa latência para modelos de grande escala.

### Google Gemini API
A API do Google Gemini é utilizada como alternativa para processamento de linguagem natural. O sistema pode combinar resultados de múltiplos modelos para gerar ideias mais diversas e abrangentes.

### arXiv API
A API do arXiv é utilizada para buscar artigos acadêmicos relevantes para os tópicos de interesse ou dores de negócio. Isso permite que o sistema tenha acesso a pesquisas científicas atualizadas.

### Serper API
A Serper API é utilizada para buscar informações na web, permitindo que o sistema tenha acesso a notícias, blogs e outros conteúdos relevantes.

## Abordagem Multi-Modelo

O sistema utiliza uma abordagem multi-modelo, combinando resultados de diferentes APIs de IA para gerar ideias mais diversas e abrangentes. Isso permite:

1. **Maior diversidade de ideias**: Diferentes modelos têm diferentes vieses e forças
2. **Maior robustez**: Se uma API falhar, o sistema pode continuar funcionando com as outras
3. **Melhor qualidade**: A combinação de múltiplos modelos pode gerar resultados melhores do que qualquer modelo individual

## Processamento de PDFs com RAG

O sistema inclui um módulo de RAG (Retrieval Augmented Generation) para processar PDFs de artigos científicos:

1. **Extração de Texto**: O sistema baixa PDFs do arXiv e extrai o texto completo
2. **Indexação Vetorial**: O texto é dividido em chunks e transformado em embeddings usando modelos locais
3. **Recuperação Semântica**: Quando uma pergunta é feita, o sistema recupera os trechos mais relevantes
4. **Geração Contextualizada**: Os trechos recuperados são usados como contexto para gerar respostas precisas

Esta funcionalidade permite que o sistema responda perguntas específicas sobre artigos científicos, fornecendo insights mais profundos para o processo de inovação.

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests ou abrir issues para melhorias e correções.
