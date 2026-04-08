"""Streamlit chat interface for the autonomous data agent."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WELCOME_MESSAGE = (
    "Olá! Eu sou seu agente de dados. O banco de dados já está conectado. "
    "Você pode me perguntar sobre regiões, vendedores, produtos, volume e faturamento."
)

SAMPLE_QUESTIONS = (
    "Quero saber a região que menos vende",
    "Qual vendedor teve o maior volume total?",
    "Quem vendeu mais Mouse no Nordeste?",
    "Qual produto teve maior faturamento?",
)


st.set_page_config(
    page_title="Data Agent Sênior",
    page_icon="🤖",
    layout="centered",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 880px;
    }
    div[data-testid="stSidebar"] {
        border-right: 1px solid rgba(148, 163, 184, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.caption("DATA AGENT")
st.title("Seu Analista de Dados Autônomo")
st.write("Faça perguntas em linguagem natural e receba análises com base nos CSVs conectados ao DuckDB.")


@st.cache_resource(show_spinner=False)
def load_agent():
    """Load the LangChain agent once per Streamlit process."""
    from src.agent.executor import get_agent

    return get_agent()


def ensure_chat_history() -> None:
    """Initialize the chat history for the current browser session."""
    if "messages" not in st.session_state:
        reset_chat_history()


def render_chat_history() -> None:
    """Render all messages already stored in session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def append_message(role: str, content: str) -> None:
    """Persist and render a chat message in the active session."""
    st.session_state.messages.append({"role": role, "content": content})


def reset_chat_history() -> None:
    """Reset the chat to its initial assistant message."""
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]


def render_sidebar() -> None:
    """Render operational controls and usage guidance."""
    with st.sidebar:
        st.header("Operação")
        st.info("Interface online")
        st.caption("Use perguntas objetivas. Para valores de venda, o agente calcula quantidade vezes valor unitário.")

        if st.button("Limpar conversa", use_container_width=True):
            reset_chat_history()
            st.rerun()

        if st.button("Recarregar agente", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

        st.divider()
        st.subheader("Dados conectados")
        st.write("`data/sample/vendas.csv`")
        st.caption("Colunas principais: região, vendedor, produto, quantidade e valor unitário.")


def render_quick_prompts() -> str | None:
    """Render prompt shortcuts and return the selected question, if any."""
    st.caption("Comece por uma pergunta sugerida ou escreva a sua no chat.")
    columns = st.columns(2)

    for index, question in enumerate(SAMPLE_QUESTIONS):
        if columns[index % 2].button(question, key=f"prompt_{index}", use_container_width=True):
            return question

    return None


def show_configuration_error(message: str) -> None:
    """Show setup errors with a clear recovery path."""
    st.error(message)
    with st.expander("Como corrigir"):
        st.markdown(
            """
            1. Crie o arquivo `.env` na raiz do projeto.
            2. Preencha `GROQ_API_KEY` com sua chave da Groq.
            3. Reinicie a aplicação com `streamlit run src/main.py`.
            """
        )


render_sidebar()

try:
    agent = load_agent()
except ModuleNotFoundError as exc:
    if exc.name not in {"src.agent", "src.agent.executor"}:
        raise

    show_configuration_error(
        "Não encontrei o módulo `src.agent.executor`. "
        "Confirme se a camada de orquestração do agente já foi criada e se ela expõe `get_agent()`."
    )
    st.caption(f"Detalhe técnico: {exc}")
    st.stop()
except RuntimeError as exc:
    show_configuration_error(str(exc))
    st.stop()


ensure_chat_history()
selected_question = render_quick_prompts()
st.divider()
render_chat_history()

user_question = st.chat_input("Ex: Qual vendedor teve o maior faturamento?")
submitted_question = user_question or selected_question

if submitted_question:
    with st.chat_message("user"):
        st.markdown(submitted_question)
    append_message("user", submitted_question)

    with st.chat_message("assistant"):
        with st.spinner("Analisando o banco de dados..."):
            started_at = time.perf_counter()
            try:
                raw_response = agent.invoke({"input": submitted_question})
                response_text = raw_response["output"]
            except Exception as exc:  # noqa: BLE001 - Streamlit should show user-friendly failures.
                response_text = (
                    "Não consegui concluir essa análise agora. "
                    "Tente reformular a pergunta ou recarregar o agente pela barra lateral.\n\n"
                    f"Detalhe técnico: {exc}"
                )
                st.error(response_text)
            else:
                st.markdown(response_text)
                st.caption(f"Respondido em {time.perf_counter() - started_at:.1f}s")

    append_message("assistant", response_text)
