from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .service import query

app = FastAPI(title="Text-to-SQL Guardrails", version="0.1.0")


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


@app.post("/v1/query", response_model=QueryResponse)
def post_query(request: QueryRequest) -> dict:
    return query(request.question)
