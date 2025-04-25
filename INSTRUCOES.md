# Instruções para Execução do Sistema Multiagentes para Inovação

Este documento contém instruções detalhadas para configurar e executar o Sistema Multiagentes para Inovação.

## Configuração Inicial

1. **Instale as dependências**:
   ```
   pip install -r requirements.txt
   ```

2. **Configure as variáveis de ambiente**:
   - Copie o arquivo `.env.example` para `.env`
   - Adicione suas chaves de API (a chave da Groq já está incluída)
   - Opcionalmente, ajuste as preferências de API

## Execução

### Método 1: Executar o Sistema Completo de Inovação

Para iniciar o sistema completo de inovação diretamente:

```
streamlit run innovation_system.py
```

### Método 2: Usar o script de testes

Para escolher entre diferentes componentes para testar:

```
python run_tests.py
```

Este script oferece um menu para:
1. Testar a API do arXiv - busca artigos científicos
2. Testar a API da Groq (Llama 4) - modelo de linguagem principal
3. Testar a API do Google (Gemini) - modelo de linguagem alternativo
4. Testar a API do Serper - busca na web
5. Testar RAG com PDFs do arXiv - processamento avançado de artigos científicos
6. Testar fluxo de inovação com RAG - teste do fluxo de agentes
7. Executar Sistema Completo de Inovação - interface completa do sistema

## Uso do Sistema Completo de Inovação

1. **Configure o processo de inovação**:
   - **Tópico de Pesquisa** - Defina o tema central para a pesquisa (ex: "Inteligência Artificial na Saúde")
   - **Contexto de Negócio** - Descreva o contexto empresarial, objetivos e restrições
   - **Configurações Avançadas** - Ajuste parâmetros como número de resultados e artigos a processar

2. **Inicie o processo**:
   - Clique no botão "Iniciar Processo de Inovação"
   - Acompanhe o progresso através da barra de progresso e logs de execução
   - O sistema executará automaticamente todas as etapas do processo

3. **Explore os resultados em diferentes abas**:
   - **Relatório Final** - Documento completo com contexto, insights e recomendações
   - **Ideias Geradas** - Lista de ideias inovadoras com pontuações e avaliações detalhadas
   - **Insights** - Observações importantes extraídas da pesquisa
   - **Pesquisa** - Resultados brutos da web e artigos científicos
   - **Artigos Processados** - Resumos gerados por IA dos PDFs analisados

4. **Analise as ideias em detalhes**:
   - Visualize gráficos de pontuação para cada critério de avaliação
   - Leia justificativas detalhadas para cada pontuação
   - Compare diferentes ideias através da tabela de resumo

5. **Exporte os resultados**:
   - Baixe o relatório final para compartilhar com stakeholders

## Notas Importantes

- A API do arXiv é gratuita e não requer chave
- A chave da Groq API já está incluída para facilitar os testes
- Para a API do Google Gemini, você precisará obter sua própria chave
- O sistema combina resultados de múltiplas APIs quando disponíveis
- Para uso em produção, recomenda-se obter suas próprias chaves de API

## Solução de Problemas

Se encontrar problemas com as APIs:
1. Verifique sua conexão com a internet
2. Execute os testes específicos de API usando `python run_tests.py`
3. Verifique se as chaves de API estão configuradas corretamente no arquivo `.env`
