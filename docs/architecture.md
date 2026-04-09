# Arquitetura do Data Agent

Este projeto agora usa uma arquitetura separada entre frontend e backend para
entregar uma experiencia de chat mais proxima de um produto real.

## Fluxo de uma pergunta

1. O usuario envia uma pergunta pela interface React em `frontend/`.
2. O frontend chama `POST /api/chat` no backend FastAPI.
3. `src/main.py` recebe a requisicao HTTP, carrega o agente em cache e repassa a
   pergunta para a camada de orquestracao.
4. `src.agent.executor` monta o contexto do LangChain com prompt, ferramentas e
   esquema das tabelas locais.
5. O modelo hospedado via Groq decide como consultar os dados.
6. O toolkit executa a consulta no DuckDB.
7. A resposta final volta pela API e e renderizada no chat React.

## Responsabilidades por camada

- `frontend/`: interface de chat em React + Vite.
- `src/main.py`: backend FastAPI, CORS, endpoints HTTP e cache do agente.
- `src.agent.executor`: criacao do agente LangChain, modelo, prompt de sistema,
  toolkit SQL e contrato publico `get_agent()`.
- DuckDB: execucao analitica local sobre os CSVs.
- Groq + Llama: raciocinio, geracao de SQL e sintese da resposta final.

## Decisoes de arquitetura

- O agente e carregado uma unica vez por processo via `lru_cache` no backend.
- A UI foi separada do Python para permitir controle fino de layout, estados e
  identidade visual.
- O backend preserva o contrato simples de pergunta e resposta, o que facilita
  trocar o frontend futuramente sem reescrever a logica analitica.
- O uso de DuckDB mantem a infraestrutura leve, sem dependencia de um banco
  externo para o ciclo inicial do produto.
