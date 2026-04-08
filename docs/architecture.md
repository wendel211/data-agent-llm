# Arquitetura do Data Agent

Este projeto segue uma arquitetura em camadas para transformar perguntas em
linguagem natural em consultas analíticas sobre dados locais.

## Fluxo de uma pergunta

1. O usuário envia uma pergunta pela interface Streamlit.
2. O Streamlit preserva o histórico em `st.session_state` e chama o agente
   carregado em cache com `st.cache_resource`.
3. A camada de orquestração em `src.agent.executor` monta o contexto de execução
   do LangChain com prompt de sistema, esquema das tabelas e pergunta do usuário.
4. O modelo hospedado via Groq decide se precisa executar uma ação e gera a
   consulta SQL apropriada.
5. O toolkit executa a consulta no DuckDB contra os dados locais.
6. O resultado bruto volta para o modelo, que sintetiza a resposta em linguagem
   natural.
7. A resposta final retorna para o Streamlit e é anexada ao histórico do chat.

## Responsabilidades por camada

- `src/main.py`: interface web, estado de sessão, cache do agente e tratamento de
  erros de apresentação.
- `src.agent.executor`: criação do agente LangChain, modelo, prompt de sistema,
  toolkit SQL e contrato público `get_agent()`.
- DuckDB: execução analítica local em memória, evitando a necessidade de um banco
  relacional externo para o ciclo inicial do produto.
- Groq + Llama: raciocínio, geração de SQL e síntese da resposta final para o
  usuário.

## Decisões de arquitetura

- O agente é carregado uma única vez por processo Streamlit para evitar recriar
  conexões, modelo e metadados a cada mensagem.
- O histórico do chat vive no `st.session_state`, que é o local correto para
  estado por sessão no Streamlit.
- A UI depende apenas do contrato `get_agent()`. Isso preserva baixo acoplamento:
  trocar Groq por outro provedor deve ficar restrito à camada de orquestração.
- O uso de DuckDB mantém a infraestrutura simples para OLAP local, sem Docker ou
  serviços externos no caminho crítico de desenvolvimento.
