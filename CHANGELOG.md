# Changelog - Integração MCP e Novas Fontes de Dados

## Adições Principais

### 1. Model Context Protocol (MCP)
- Implementado o MCP para centralizar a conexão com diferentes APIs e fontes de dados
- Criado o arquivo `utils/mcp.py` com a classe `ModelContextProtocol`
- Migrado a conexão com arXiv para o MCP

### 2. Novas Fontes de Dados
- Adicionada integração com a API do Reddit para obter discussões e opiniões de usuários
- Adicionada integração com a API do Product Hunt para descobrir produtos e serviços inovadores recentes
- Atualizado o estado do sistema para armazenar os novos tipos de resultados

### 3. Análise de Tendências Aprimorada
- Atualizado o `TrendAnalyzerNode` para processar dados do Reddit e Product Hunt
- Adicionados métodos para preparar o contexto das novas fontes de dados
- Melhorado o prompt de análise para incluir as novas fontes

### 4. Interface do Usuário
- Atualizada a interface Streamlit para mostrar resultados do Reddit e Product Hunt
- Adicionadas métricas para as novas fontes de dados
- Implementados expanders para visualizar detalhes dos novos resultados

### 5. Documentação
- Atualizada a documentação para refletir as novas fontes de dados e o MCP
- Adicionadas instruções para configuração das novas APIs
- Atualizado o arquivo `.env.example` com as novas variáveis de ambiente

## Configuração Necessária

Para utilizar as novas funcionalidades, é necessário configurar as seguintes variáveis de ambiente:

```
# Reddit API
REDDIT_CLIENT_ID=seu_client_id_reddit_aqui
REDDIT_CLIENT_SECRET=seu_client_secret_reddit_aqui
REDDIT_USER_AGENT=FourSight Innovation System v1.0
REDDIT_USERNAME=seu_username_reddit_aqui
REDDIT_PASSWORD=sua_senha_reddit_aqui

# Product Hunt API
PRODUCTHUNT_API_KEY=sua_chave_producthunt_aqui
```

## Dependências Adicionadas
- `requests-oauthlib>=1.3.0` - Para autenticação OAuth com a API do Reddit
