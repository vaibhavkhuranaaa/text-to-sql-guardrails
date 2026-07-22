from __future__ import annotations

import time
import uuid

from opentelemetry import trace

from .catalog import CATALOG_VERSION, generate
from .db import prepared_read_only_connection
from .observability import event
from .validation import validate

tracer = trace.get_tracer(__name__)


def query(question: str, candidate_sql: str | None = None) -> dict:
    started = time.perf_counter()
    trace_id = uuid.uuid4().hex
    with prepared_read_only_connection() as connection:
        with tracer.start_as_current_span("text_to_sql.request") as span:
            span.set_attribute("trace_id", trace_id)
            span.set_attribute("cost_usd", 0.0)
            event("request", trace_id=trace_id, cost_usd=0.0)
            with tracer.start_as_current_span("text_to_sql.generation"):
                sql, refusal = (
                    (candidate_sql, None) if candidate_sql is not None else generate(question)
                )
            event("generation", trace_id=trace_id, generated=sql is not None)
            if refusal:
                event("refusal", trace_id=trace_id, reason="unsupported", cost_usd=0.0)
                return _verdict("refused", trace_id, None, [], [], refusal, started)
            with tracer.start_as_current_span("text_to_sql.validation"):
                result = validate(sql or "", connection)
            event("validation", trace_id=trace_id, valid=result.valid, checks=result.checks)
            if not result.valid:
                event("refusal", trace_id=trace_id, reason="validation", cost_usd=0.0)
                return _verdict("refused", trace_id, sql, result.checks, [], result.reason, started)
            try:
                with tracer.start_as_current_span("text_to_sql.execution"):
                    rows = [
                        dict(zip([d[0] for d in connection.description], row, strict=True))
                        for row in connection.execute(result.sql).fetchall()
                    ]
            except Exception as exc:  # defensive: validation should stop this path
                event("execution", trace_id=trace_id, status="failed", cost_usd=0.0)
                return _verdict(
                    "failed_validation",
                    trace_id,
                    sql,
                    result.checks,
                    [],
                    f"Execution failed safely: {exc}",
                    started,
                )
            verdict = _verdict("trusted", trace_id, result.sql, result.checks, rows, None, started)
            event(
                "execution",
                trace_id=trace_id,
                status="trusted",
                latency_ms=verdict["latency_ms"],
                cost_usd=0.0,
            )
            return verdict


def _verdict(
    status: str,
    trace_id: str,
    sql: str | None,
    checks: list[str],
    rows: list[dict],
    reason: str | None,
    started: float,
) -> dict:
    return {
        "status": status,
        "trace_id": trace_id,
        "catalog_version": CATALOG_VERSION,
        "generated_sql": sql,
        "validation_checks": checks,
        "result_preview": rows,
        "reason": reason,
        "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        "cost_usd": 0.0,
    }
