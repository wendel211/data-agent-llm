import { useEffect, useMemo, useState, useRef } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const SUGGESTIONS = [
  "Qual regiao teve o maior faturamento?",
  "Quem vendeu mais Mouse no Nordeste?",
  "Qual vendedor teve o maior volume?",
  "Qual produto teve a maior receita?",
];

const SIDEBAR_SECTIONS = [
  {
    title: "Base",
    items: ["vendas.csv"],
  },
  {
    title: "Stack",
    items: ["React", "FastAPI", "DuckDB"],
  },
];

const INITIAL_MESSAGE = {
  id: "welcome",
  role: "assistant",
  content: "Pronto para analisar sua base local. Como posso ajudar hoje?",
};

function AgentLogo() {
  return (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L4.5 20.29L5.21 21L12 18L18.79 21L19.5 20.29L12 2Z" fill="currentColor"/>
    </svg>
  );
}

function App() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("Pronto");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const visibleMessages = useMemo(
    () => messages.filter((message) => message.id !== "welcome" || messages.length > 1),
    [messages],
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) throw new Error("Offline");
        setStatus("Online");
      } catch {
        setStatus("Offline");
      }
    }
    void checkHealth();
  }, []);

  async function submitMessage(rawMessage) {
    const trimmedMessage = rawMessage.trim();
    if (!trimmedMessage || isLoading) return;

    const userMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: trimmedMessage,
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmedMessage }),
      });

      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Erro na consulta");

      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-assistant`,
          role: "assistant",
          content: payload.answer,
        },
      ]);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Erro desconhecido");
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    void submitMessage(input);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Data Agent Senior</h2>
        </div>
        
        <div className="sidebar-content">
          {SIDEBAR_SECTIONS.map((section) => (
            <div className="sidebar-card" key={section.title}>
              <h3>{section.title}</h3>
              <ul>
                {section.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <a href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer" className="sidebar-link">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Docs / API
          </a>
        </div>
      </aside>

      <main className="chat-shell">
        <header className="chat-header">
          <div className="header-content">
            <div className="header-title-group">
              <span className="header-title">Agente de Dados Senior</span>
              <span className="header-subtitle">Análise de Dados e Vendas (vendas.csv)</span>
            </div>
            <div className="badge">{status}</div>
          </div>
        </header>

        <div className="scroll-container">
          <div className="chat-content-limit">
            {visibleMessages.length === 0 ? (
              <div className="empty-state">
                <div className="empty-orb">
                  <AgentLogo />
                </div>
                <h1>Como posso ajudar você hoje?</h1>
                
                <div className="suggestion-grid">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      className="suggestion-card"
                      type="button"
                      onClick={() => void submitMessage(suggestion)}
                      disabled={isLoading}
                    >
                      <span>{suggestion}</span>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="message-list">
                {visibleMessages.map((message) => (
                  <article
                    key={message.id}
                    className={`message-bubble ${message.role === "user" ? "message-user" : "message-assistant"}`}
                  >
                    <div className="avatar">
                      {message.role === "user" ? "U" : <AgentLogo />}
                    </div>
                    <div className="message-content">
                      <p>{message.content}</p>
                    </div>
                  </article>
                ))}
                {isLoading && (
                  <article className="message-bubble message-assistant">
                    <div className="avatar"><AgentLogo /></div>
                    <div className="message-content">
                      <p>Analisando dados...</p>
                    </div>
                  </article>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        <footer className="composer-shell">
          <div className="composer-container">
            <form className="composer" onSubmit={handleSubmit}>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Pergunte sobre sua base de vendas..."
                rows={1}
                disabled={isLoading}
              />
              <button type="submit" disabled={isLoading || !input.trim()}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
              </button>
            </form>
            {error && <p className="feedback feedback-error">{error}</p>}
            {!error && <p className="feedback">Dados processados localmente via DuckDB.</p>}
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;
