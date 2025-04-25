# FourSight - Sistema Multiagentes de Inovação

![FourSight Logo](https://via.placeholder.com/150x150?text=FourSight)

Um sistema avançado baseado em múltiplos agentes de IA especializados para gerar ideias inovadoras a partir de pesquisas científicas, tendências de mercado e contexto de negócio.

## 🌟 Destaques

- **Arquitetura Multiagente**: Agentes especializados trabalham em conjunto para pesquisar, processar e sintetizar informações
- **Processamento de PDFs com RAG**: Extrai e resume conteúdo de artigos científicos usando Retrieval Augmented Generation
- **Avaliação Multidimensional**: Avalia ideias com base em 5 critérios essenciais de inovação
- **Visualizações Interativas**: Gráficos e tabelas para análise detalhada das ideias geradas
- **Interface Intuitiva**: Experiência de usuário simplificada com Streamlit

## 📋 Requisitos

- Python 3.8+
- Chave de API da Groq (para processamento de linguagem natural com Llama 4)
- Chave de API do Serper (para busca na web)
- Opcionalmente: Chave de API do Google Gemini

## 🚀 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/couy-victor/FourSight-.git
   cd FourSight-
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves de API
   ```

## 💡 Uso

Execute o Sistema Completo de Inovação:

```bash
streamlit run innovation_system.py
```

Ou use o script de testes para escolher entre diferentes componentes:

```bash
python run_tests.py
```

### Funcionalidades do Sistema

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

## 🧠 Arquitetura do Sistema

O sistema utiliza uma arquitetura de agentes especializados:

1. **Agente Pesquisador**: Busca informações na web e artigos científicos
2. **Agente Sintetizador**: Analisa as informações e gera insights e ideias
3. **Orquestrador**: Coordena o fluxo de informações entre os agentes

## 📊 Sistema de Avaliação de Ideias

As ideias são avaliadas com base em cinco critérios principais:

1. **Originalidade**: Quão única e diferenciada é a ideia
2. **Viabilidade**: Quão viável é implementar a ideia
3. **Impacto potencial**: Qual o potencial de impacto da ideia
4. **Escalabilidade**: Quão escalável é a ideia
5. **Alinhamento com o contexto**: Quão bem a ideia se alinha ao contexto de negócio

## 📚 Processamento de PDFs com RAG

O sistema inclui um módulo de RAG (Retrieval Augmented Generation) para processar PDFs de artigos científicos:

1. **Extração de Texto**: O sistema baixa PDFs do arXiv e extrai o texto completo
2. **Resumo com IA**: O conteúdo é resumido usando modelos de linguagem avançados
3. **Integração com o Fluxo**: Os resumos são incorporados ao processo de geração de ideias

## 🔄 Fluxo de Trabalho

1. **Pesquisa**: Coleta de informações da web e artigos científicos
2. **Processamento**: Análise de PDFs e extração de conhecimento
3. **Síntese**: Geração de insights a partir dos dados coletados
4. **Ideação**: Criação de ideias inovadoras baseadas nos insights
5. **Avaliação**: Análise crítica das ideias geradas

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests ou abrir issues para melhorias e correções.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## 🙏 Agradecimentos

- Equipe de desenvolvimento do Streamlit
- Comunidade de IA e Processamento de Linguagem Natural
- Todos os contribuidores e testadores
