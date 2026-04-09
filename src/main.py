"""Modern Streamlit interface for the autonomous data agent."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WELCOME_MESSAGE = (
    "Ola. Eu sou seu agente de dados. O banco local ja esta conectado e pronto "
    "para analisar regioes, vendedores, produtos, volume e faturamento."
)

SAMPLE_QUESTIONS = (
    "Quero saber a regiao que menos vende",
    "Qual vendedor teve o maior volume total?",
    "Quem vendeu mais Mouse no Nordeste?",
    "Qual produto teve maior faturamento?",
)


st.set_page_config(
    page_title="Data Agent Senior",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def render_global_styles() -> None:
    """Inject the custom visual system for the Streamlit page."""
    st.markdown(
        """
        <style>
        :root {
            --bg-primary: #07111f;
            --bg-secondary: rgba(9, 19, 35, 0.76);
            --bg-soft: rgba(12, 27, 49, 0.58);
            --line: rgba(126, 164, 214, 0.24);
            --line-strong: rgba(132, 198, 255, 0.42);
            --text-primary: #f4f7fb;
            --text-secondary: #97aac4;
            --text-soft: #6d819b;
            --accent: #7fc7ff;
            --accent-strong: #42a5ff;
            --accent-soft: rgba(127, 199, 255, 0.16);
            --shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
        }

        html, body, [class*="css"] {
            font-family: "Segoe UI", "Helvetica Neue", sans-serif;
        }

        .stApp {
            color: var(--text-primary);
            background:
                radial-gradient(circle at top left, rgba(66, 165, 255, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(127, 199, 255, 0.14), transparent 24%),
                linear-gradient(180deg, #040a14 0%, #07111f 48%, #091526 100%);
        }

        [data-testid="stAppViewContainer"] > .main {
            background: transparent;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stToolbar"] {
            visibility: hidden;
            height: 0;
            position: fixed;
        }

        .shell {
            position: relative;
            overflow: hidden;
            padding: 2rem;
            border: 1px solid var(--line);
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(18, 37, 68, 0.92), rgba(6, 15, 28, 0.92)),
                linear-gradient(180deg, rgba(255, 255, 255, 0.05), transparent);
            box-shadow: var(--shadow);
        }

        .shell::after {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(120deg, rgba(127, 199, 255, 0.12), transparent 30%, transparent 70%, rgba(127, 199, 255, 0.08));
            pointer-events: none;
        }

        .eyebrow {
            display: inline-block;
            margin-bottom: 1rem;
            padding: 0.45rem 0.8rem;
            border: 1px solid var(--line-strong);
            border-radius: 999px;
            background: rgba(127, 199, 255, 0.08);
            color: var(--accent);
            font-size: 0.78rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1.65fr 1fr;
            gap: 1.25rem;
            align-items: start;
        }

        .hero-title {
            margin: 0;
            font-size: clamp(2.5rem, 5vw, 4.4rem);
            line-height: 0.94;
            letter-spacing: -0.04em;
        }

        .hero-copy {
            max-width: 46rem;
            margin-top: 1rem;
            color: var(--text-secondary);
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .panel {
            height: 100%;
            padding: 1.35rem;
            border: 1px solid var(--line);
            border-radius: 22px;
            background: var(--bg-soft);
            backdrop-filter: blur(10px);
        }

        .panel-label {
            margin-bottom: 0.8rem;
            color: var(--text-soft);
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .signal-value {
            margin: 0;
            font-size: 1.85rem;
            line-height: 1;
            letter-spacing: -0.04em;
        }

        .signal-copy {
            margin-top: 0.75rem;
            color: var(--text-secondary);
            line-height: 1.65;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1.25rem;
        }

        .metric-card {
            padding: 1.1rem 1rem;
            border: 1px solid var(--line);
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.03);
        }

        .metric-name {
            color: var(--text-soft);
            font-size: 0.74rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .metric-value {
            margin-top: 0.55rem;
            font-size: 1.35rem;
            font-weight: 600;
            letter-spacing: -0.03em;
        }

        .metric-copy {
            margin-top: 0.45rem;
            color: var(--text-secondary);
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .section-title {
            margin-top: 2rem;
            margin-bottom: 0.35rem;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        .section-copy {
            margin-bottom: 1rem;
            color: var(--text-secondary);
            line-height: 1.65;
        }

        .guide-list {
            margin: 0;
            padding-left: 1rem;
            color: var(--text-secondary);
            line-height: 1.8;
        }

        .surface {
            margin-top: 1.35rem;
            padding: 1.15rem;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(5, 11, 22, 0.52);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .action-strip {
            margin-top: 1rem;
            margin-bottom: 0.25rem;
        }

        .action-caption {
            color: var(--text-soft);
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        div[data-testid="stButton"] > button {
            min-height: 3.2rem;
            border-radius: 18px;
            border: 1px solid var(--line);
            background:
                linear-gradient(180deg, rgba(17, 31, 56, 0.95), rgba(8, 17, 31, 0.95));
            color: var(--text-primary);
            font-weight: 600;
            letter-spacing: -0.01em;
            transition: all 160ms ease;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.18);
        }

        div[data-testid="stButton"] > button:hover {
            border-color: var(--line-strong);
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.26);
        }

        div[data-testid="stChatMessage"] {
            padding: 0.35rem 0;
            background: transparent;
        }

        div[data-testid="stChatMessage"] > div {
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(8, 18, 35, 0.72);
            backdrop-filter: blur(8px);
            padding: 0.95rem 1.1rem;
        }

        div[data-testid="stChatInput"] {
            padding-top: 0.75rem;
        }

        div[data-testid="stChatInput"] textarea {
            border-radius: 18px;
            background: rgba(7, 16, 30, 0.92);
            color: var(--text-primary);
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: var(--text-soft);
        }

        div[data-testid="stAlert"] {
            border-radius: 18px;
            border: 1px solid var(--line);
        }

        @media (max-width: 980px) {
            .hero-grid,
            .metric-grid {
                grid-template-columns: 1fr;
            }

            .shell {
                padding: 1.35rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def load_agent():
    """Load the LangChain agent once per Streamlit process."""
    from src.agent.executor import get_agent

    return get_agent()


def ensure_chat_history() -> None:
    """Initialize the chat history for the current browser session."""
    if "messages" not in st.session_state:
        reset_chat_history()


def append_message(role: str, content: str) -> None:
    """Persist a chat message in the active session."""
    st.session_state.messages.append({"role": role, "content": content})


def reset_chat_history() -> None:
    """Reset the chat to its initial assistant message."""
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]


def render_hero() -> None:
    """Render the futuristic top section of the application."""
    st.markdown(
        """
        <section class="shell">
            <div class="eyebrow">Data Agent Platform</div>
            <div class="hero-grid">
                <div>
                    <h1 class="hero-title">Analise vendas com linguagem natural e resposta executiva.</h1>
                    <p class="hero-copy">
                        Uma interface mais limpa para conversar com o seu banco local em DuckDB,
                        transformar perguntas em SQL e acelerar exploracao de dados sem sair do fluxo.
                    </p>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-name">Camada analitica</div>
                            <div class="metric-value">DuckDB local</div>
                            <div class="metric-copy">Consulta rapida em arquivos CSV sem depender de infra externa.</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-name">Orquestracao</div>
                            <div class="metric-value">LangChain + Groq</div>
                            <div class="metric-copy">Perguntas em linguagem natural convertidas em analise acionavel.</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-name">Experiencia</div>
                            <div class="metric-value">Sessao persistente</div>
                            <div class="metric-copy">Historico de conversa mantido por sessao para investigacoes iterativas.</div>
                        </div>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-label">Control Tower</div>
                    <p class="signal-value">Base pronta para operar</p>
                    <p class="signal-copy">
                        O agente esta preparado para responder sobre regiao, vendedor, produto,
                        volume e faturamento com foco em leitura executiva.
                    </p>
                    <div class="section-title">Escopo conectado</div>
                    <p class="section-copy">CSV local em <code>data/sample/vendas.csv</code> com colunas de pedido, data, regiao, vendedor, produto, quantidade e valor unitario.</p>
                    <div class="section-title">Como obter respostas melhores</div>
                    <ul class="guide-list">
                        <li>Peça comparacoes por regiao, produto ou vendedor.</li>
                        <li>Use termos como faturamento, volume, media e ranking.</li>
                        <li>Mencione filtros como periodo, produto ou territorio quando quiser analises mais precisas.</li>
                    </ul>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_action_bar() -> None:
    """Render top-level operational controls."""
    st.markdown('<div class="action-strip"><div class="action-caption">Workspace controls</div></div>', unsafe_allow_html=True)
    action_columns = st.columns((1, 1, 1.2, 1.2))
    with action_columns[0]:
        st.caption("Dados conectados")
        st.write("`data/sample/vendas.csv`")
    with action_columns[1]:
        st.caption("Regra de negocio")
        st.write("Faturamento = `quantidade * valor_unitario`")
    with action_columns[2]:
        if st.button("Limpar conversa", use_container_width=True):
            reset_chat_history()
            st.rerun()
    with action_columns[3]:
        if st.button("Recarregar agente", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()


def render_quick_prompts() -> str | None:
    """Render prompt shortcuts and return the selected question, if any."""
    st.markdown('<div class="section-title">Prompts iniciais</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Escolha uma pergunta pronta para acelerar a exploracao ou escreva sua propria analise no campo de chat.</div>',
        unsafe_allow_html=True,
    )
    selected_question = None
    columns = st.columns(4)
    for index, question in enumerate(SAMPLE_QUESTIONS):
        if columns[index].button(question, key=f"prompt_{index}", use_container_width=True):
            selected_question = question

    return selected_question


def render_chat_history() -> None:
    """Render all messages already stored in session state."""
    st.markdown('<div class="section-title">Fluxo analitico</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Converse com o agente como se estivesse falando com um analista senior de dados. As respostas aparecem abaixo em ordem cronologica.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="surface">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown("</div>", unsafe_allow_html=True)


def show_configuration_error(message: str) -> None:
    """Show setup errors with a clear recovery path."""
    st.error(message)
    with st.expander("Como corrigir"):
        st.markdown(
            """
            1. Crie o arquivo `.env` na raiz do projeto.
            2. Preencha `GROQ_API_KEY` com sua chave da Groq.
            3. Reinicie a aplicacao com `streamlit run src/main.py`.
            """
        )


render_global_styles()
render_hero()
render_action_bar()

try:
    agent = load_agent()
except ModuleNotFoundError as exc:
    if exc.name not in {"src.agent", "src.agent.executor"}:
        raise

    show_configuration_error(
        "Nao encontrei o modulo `src.agent.executor`. "
        "Confirme se a camada de orquestracao do agente ja foi criada e se ela expoe `get_agent()`."
    )
    st.caption(f"Detalhe tecnico: {exc}")
    st.stop()
except RuntimeError as exc:
    show_configuration_error(str(exc))
    st.stop()


ensure_chat_history()
selected_question = render_quick_prompts()
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
                    "Nao consegui concluir essa analise agora. "
                    "Tente reformular a pergunta ou recarregar o agente pelos controles da pagina.\n\n"
                    f"Detalhe tecnico: {exc}"
                )
                st.error(response_text)
            else:
                st.markdown(response_text)
                st.caption(f"Respondido em {time.perf_counter() - started_at:.1f}s")

    append_message("assistant", response_text)
