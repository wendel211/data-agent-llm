"""Streamlit chat interface for the autonomous data agent."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WELCOME_MESSAGE = (
    "Olá! Eu sou seu agente de dados. O banco de dados já está conectado. "
    "O que você gostaria de saber sobre nossas vendas?"
)


st.set_page_config(
    page_title="Data Agent Sênior",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Seu Analista de Dados Autônomo")
st.markdown("Faça perguntas sobre seus dados em linguagem natural.")


@st.cache_resource(show_spinner=False)
def load_agent():
    """Load the LangChain agent once per Streamlit process."""
    from src.agent.executor import get_agent

    return get_agent()


def ensure_chat_history() -> None:
    """Initialize the chat history for the current browser session."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
            }
        ]


def render_chat_history() -> None:
    """Render all messages already stored in session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def append_message(role: str, content: str) -> None:
    """Persist and render a chat message in the active session."""
    st.session_state.messages.append({"role": role, "content": content})


try:
    agent = load_agent()
except ModuleNotFoundError as exc:
    if exc.name not in {"src.agent", "src.agent.executor"}:
        raise

    st.error(
        "Não encontrei o módulo `src.agent.executor`. "
        "Confirme se a camada de orquestração do agente já foi criada e se ela expõe `get_agent()`."
    )
    st.caption(f"Detalhe técnico: {exc}")
    st.stop()


ensure_chat_history()
render_chat_history()

user_question = st.chat_input("Ex: Qual vendedor teve o maior faturamento?")

if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)
    append_message("user", user_question)

    with st.chat_message("assistant"):
        with st.spinner("Analisando o banco de dados..."):
            try:
                raw_response = agent.invoke({"input": user_question})
                response_text = raw_response["output"]
            except Exception as exc:  # noqa: BLE001 - Streamlit should show user-friendly failures.
                response_text = f"Desculpe, encontrei um erro ao processar os dados: {exc}"
                st.error(response_text)
            else:
                st.markdown(response_text)

    append_message("assistant", response_text)
