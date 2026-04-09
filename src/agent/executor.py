"""LangChain SQL agent backed by Groq and DuckDB."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import duckdb
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import BaseTool, tool
from langchain_groq import ChatGroq


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DB_DIR = PROJECT_ROOT / ".runtime"
CSV_PATTERNS = (
    "data/*.csv",
    "data/raw/*.csv",
    "data/processed/*.csv",
    "data/sample/*.csv",
)

SYSTEM_PREFIX = """
Você é um analista de dados sênior trabalhando com dados de vendas em DuckDB.
Responda sempre em português do Brasil, com clareza executiva e sem inventar dados.
Use SQL apenas para consultar os dados disponíveis. Se a pergunta não puder ser
respondida com as tabelas existentes, explique objetivamente a limitação.

Regras de negócio:
- Na tabela vendas, não existe coluna valor_venda ou faturamento.
- Para perguntas sobre faturamento, receita, vendas em valor, ou "região que mais/menos vendeu",
  calcule o valor como SUM(quantidade * valor_unitario).
- Para perguntas sobre volume, itens, unidades ou quantidade vendida, use SUM(quantidade).
- Antes de consultar, use describe_table quando houver dúvida sobre os nomes das colunas.
"""


class DataAgentConfigurationError(RuntimeError):
    """Raised when the local agent cannot be initialized safely."""


class DataAgent:
    """Adapter that keeps the Streamlit contract independent from LangChain internals."""

    def __init__(self, graph: Any) -> None:
        self._graph = graph

    def invoke(self, payload: dict[str, str]) -> dict[str, str]:
        """Invoke the LangChain agent with the contract expected by the UI."""
        user_input = payload.get("input", "").strip()
        if not user_input:
            return {"output": "Envie uma pergunta sobre os dados para eu analisar."}

        response = self._graph.invoke({"messages": [{"role": "user", "content": user_input}]})
        message = response["messages"][-1]
        return {"output": str(message.content)}


def get_agent():
    """Create a LangChain SQL agent ready to answer natural language questions."""
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise DataAgentConfigurationError(
            "Configure a variável GROQ_API_KEY no arquivo .env antes de iniciar o agente."
        )

    csv_files = discover_csv_files(PROJECT_ROOT)
    if not csv_files:
        raise DataAgentConfigurationError(
            "Nenhum arquivo CSV foi encontrado em data/, data/raw/, data/processed/ ou data/sample/."
        )

    table_names = build_table_names(csv_files)
    db_path = get_runtime_duckdb_path()
    build_duckdb_database(csv_files, table_names, db_path)
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        api_key=api_key,
        temperature=0,
    )
    graph = create_agent(
        model=llm,
        tools=create_query_tools(db_path, set(table_names.values())),
        system_prompt=build_system_prompt(table_names),
        debug=os.getenv("LANGCHAIN_VERBOSE", "").lower() == "true",
    )

    return DataAgent(graph)


def discover_csv_files(project_root: Path) -> list[Path]:
    """Return all known local CSV files, without leaking virtualenv artifacts."""
    files: list[Path] = []
    for pattern in CSV_PATTERNS:
        files.extend(project_root.glob(pattern))

    return sorted({file.resolve() for file in files if file.is_file()})


def get_runtime_duckdb_path() -> Path:
    """Create a process-specific DuckDB path to avoid file lock conflicts."""
    RUNTIME_DB_DIR.mkdir(parents=True, exist_ok=True)
    return RUNTIME_DB_DIR / f"data_agent_{os.getpid()}.duckdb"


def build_duckdb_database(csv_files: list[Path], table_names: dict[Path, str], db_path: Path) -> None:
    """Create DuckDB tables from the discovered CSV files."""
    with duckdb.connect(str(db_path)) as connection:
        for csv_file in csv_files:
            table_name = table_names[csv_file]
            drop_relation(connection, table_name)
            connection.execute(
                f'CREATE TABLE "{table_name}" AS '
                f"SELECT * FROM read_csv_auto('{escape_duckdb_path(csv_file)}', header = true)"
            )


def drop_relation(connection: duckdb.DuckDBPyConnection, table_name: str) -> None:
    """Drop an existing DuckDB table or view with the given name."""
    for relation_type in ("TABLE", "VIEW"):
        try:
            connection.execute(f'DROP {relation_type} IF EXISTS "{table_name}"')
        except duckdb.CatalogException:
            continue


def create_query_tools(db_path: Path, table_names: set[str]) -> list[BaseTool]:
    """Build read-only DuckDB tools for the LangChain agent."""

    @tool
    def list_tables() -> str:
        """List the available DuckDB tables for analysis."""
        return ", ".join(sorted(table_names))

    @tool
    def describe_table(table_name: str) -> str:
        """Return the schema of a DuckDB table."""
        table = normalize_table_name(table_name, table_names)
        with duckdb.connect(str(db_path), read_only=True) as connection:
            rows = connection.execute(f'DESCRIBE "{table}"').fetchall()

        return "\n".join(f"{column}: {kind}" for column, kind, *_ in rows)

    @tool
    def query_data(sql: str) -> str:
        """Execute a read-only SQL query against DuckDB and return a compact result."""
        try:
            validate_read_only_sql(sql)
            with duckdb.connect(str(db_path), read_only=True) as connection:
                result = connection.execute(sql).fetchdf()
        except Exception as exc:  # noqa: BLE001 - tool errors should be observable by the agent.
            return (
                "Erro ao executar a consulta SQL. Revise o esquema com describe_table e tente novamente. "
                f"Detalhe: {exc}"
            )

        if result.empty:
            return "A consulta não retornou linhas."

        return result.head(50).to_string(index=False)

    return [list_tables, describe_table, query_data]


def build_system_prompt(table_names: dict[Path, str]) -> str:
    """Build an agent prompt with the known tables and their source files."""
    table_context = "\n".join(
        f"- {table}: {path.relative_to(PROJECT_ROOT).as_posix()}"
        for path, table in table_names.items()
    )
    return f"{SYSTEM_PREFIX}\n\nTabelas disponíveis:\n{table_context}"


def build_table_names(csv_files: list[Path]) -> dict[Path, str]:
    """Create deterministic SQL table names from CSV file names."""
    seen: dict[str, int] = {}
    table_names: dict[Path, str] = {}

    for csv_file in csv_files:
        base_name = sanitize_identifier(csv_file.stem)
        occurrence = seen.get(base_name, 0)
        seen[base_name] = occurrence + 1
        table_names[csv_file] = base_name if occurrence == 0 else f"{base_name}_{occurrence + 1}"

    return table_names


def sanitize_identifier(value: str) -> str:
    """Convert arbitrary file names to DuckDB-friendly identifiers."""
    identifier = re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower()
    return identifier or "dataset"


def normalize_table_name(table_name: str, allowed_tables: set[str]) -> str:
    """Validate a table name before interpolating it into SQL."""
    normalized = sanitize_identifier(table_name)
    if normalized not in allowed_tables:
        raise ValueError(f"Tabela desconhecida: {table_name}. Tabelas disponíveis: {sorted(allowed_tables)}")

    return normalized


def validate_read_only_sql(sql: str) -> None:
    """Allow only single-statement SELECT/WITH queries."""
    normalized = sql.strip().lower()
    if not normalized.startswith(("select", "with")):
        raise ValueError("A ferramenta aceita apenas consultas SELECT ou WITH.")

    if ";" in normalized.rstrip(";"):
        raise ValueError("A ferramenta aceita apenas uma consulta SQL por vez.")

    blocked_keywords = ("insert", "update", "delete", "drop", "alter", "create", "copy", "attach", "detach")
    if any(re.search(rf"\b{keyword}\b", normalized) for keyword in blocked_keywords):
        raise ValueError("A ferramenta está em modo somente leitura e bloqueou essa consulta.")


def escape_duckdb_path(path: Path) -> str:
    """Escape a filesystem path for DuckDB SQL string literals."""
    return path.as_posix().replace("'", "''")
