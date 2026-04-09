"""FastAPI backend for the React-based data agent frontend."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agent.executor import DataAgentConfigurationError, get_agent


PROJECT_ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="Data Agent API",
    version="0.1.0",
    description="HTTP API for querying local sales data through the LLM agent.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Payload accepted by the chat endpoint."""

    message: str = Field(..., min_length=1, description="Natural language question for the data agent.")


class ChatResponse(BaseModel):
    """Response returned by the chat endpoint."""

    answer: str


class HealthResponse(BaseModel):
    """Lightweight service status payload."""

    status: str
    datasets_path: str


@lru_cache(maxsize=1)
def load_agent():
    """Initialize the LangChain agent once per process."""
    return get_agent()


@app.get("/api/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    """Expose a lightweight health endpoint for local frontend checks."""
    return HealthResponse(status="ok", datasets_path=str(PROJECT_ROOT / "data"))


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Handle a user question and return the agent answer."""
    try:
        agent = load_agent()
        response = agent.invoke({"input": payload.message})
    except DataAgentConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - API must wrap unexpected agent failures.
        raise HTTPException(
            status_code=500,
            detail=(
                "Nao consegui concluir essa analise agora. "
                f"Detalhe tecnico: {exc}"
            ),
        ) from exc

    return ChatResponse(answer=response["output"])
