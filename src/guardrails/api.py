import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .db import policy_schema, prepared_read_only_connection, semantic_catalog, snapshot_status
from .examples import EXAMPLES
from .proposals import create, execute
from .service import query
from .ui import CONSOLE_HTML

app = FastAPI(title="Text-to-SQL Guardrails", version="0.1.0")
EVALUATION_REPORT = Path(__file__).parents[2] / "evaluation" / "report.json"


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class QueryResponse(BaseModel):
    status: Literal["trusted", "refused", "failed_validation"]
    trace_id: str
    catalog_version: str
    generated_sql: str | None
    validation_checks: list[str]
    result_preview: list[dict]
    reason: str | None
    latency_ms: float
    cost_usd: float
    snapshot: dict


class ProposalRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)


class ApprovalRequest(BaseModel):
    approval_token: str = Field(min_length=16, max_length=200)


@app.post("/v1/query", response_model=QueryResponse)
def post_query(request: QueryRequest) -> dict:
    return query(request.question)


@app.post("/v2/query-proposals")
def post_query_proposal(request: ProposalRequest) -> dict:
    """Generate and validate a proposal. This endpoint never executes SQL."""
    return create(request.question)


@app.post("/v2/query-proposals/{proposal_id}/execute")
def execute_query_proposal(proposal_id: str, request: ApprovalRequest) -> dict:
    return execute(proposal_id, request.approval_token)


@app.get("/v2/semantic-catalog")
def get_semantic_catalog() -> dict:
    """Lineage-safe model context; intentionally excludes physical identifiers."""
    return {"catalog": semantic_catalog(), "identifier_fields": "excluded"}


@app.get("/v2/examples")
def get_examples() -> dict:
    """Human-readable prompts only; selecting one still requires V2 review."""
    return {
        "examples": EXAMPLES,
        "disclosure": "Examples create proposals; they never execute SQL.",
    }


@app.get("/v2/data-preview")
def get_data_preview(limit: int = Query(default=25, ge=1, le=100)) -> dict:
    """Return only curated, non-identifier columns from the active V2 contract."""
    schema = policy_schema()
    if set(schema) != {"fact_transactions"}:
        return {
            "state": "demo_fixture",
            "columns": [],
            "rows": [],
            "message": "An approved transaction snapshot is required for the curated data preview.",
        }
    columns = sorted(schema["fact_transactions"])
    rendered = ", ".join(columns)
    with prepared_read_only_connection(use_approved_snapshot=True) as connection:
        cursor = connection.execute(f"SELECT {rendered} FROM fact_transactions LIMIT {limit}")
        rows = [
            dict(zip([item[0] for item in cursor.description], row, strict=True))
            for row in cursor.fetchall()
        ]
    return {
        "state": "approved",
        "columns": columns,
        "rows": rows,
        "disclosure": "Curated synthetic transaction preview only; source account identifiers are excluded.",
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def analyst_console() -> str:
    return CONSOLE_HTML


@app.get("/v1/status")
def get_status() -> dict:
    return {
        "snapshot": snapshot_status(),
        "policy": "v1 deterministic catalog; v2 Foundry proposals require explicit human approval before read-only execution.",
    }


@app.get("/v1/evaluation")
def get_evaluation() -> dict:
    """Expose generated aggregate evidence, never raw analyst requests."""
    return json.loads(EVALUATION_REPORT.read_text(encoding="utf-8"))
