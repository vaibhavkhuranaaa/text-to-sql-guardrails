from __future__ import annotations

import time
import uuid
from threading import Timer

import duckdb
from opentelemetry import trace

from .catalog import CATALOG_VERSION, generate
from .db import prepared_read_only_connection, snapshot_status
from .observability import event
from .validation import validate, validate_sql

tracer = trace.get_tracer(__name__)
EXECUTION_TIMEOUT_SECONDS = 3


class QueryBudgetExceeded(RuntimeError):
    """Raised when DuckDB interrupts an over-budget query before returning rows."""


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
                    rows = _execute_with_budget(connection, result.sql or "")
            except QueryBudgetExceeded:
                event("execution", trace_id=trace_id, status="timed_out", cost_usd=0.0)
                return _verdict(
                    "refused",
                    trace_id,
                    sql,
                    result.checks,
                    [],
                    f"Query exceeded the {EXECUTION_TIMEOUT_SECONDS}-second execution limit.",
                    started,
                )
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


def execute_validated(
    sql: str, trace_id: str | None = None, assumptions: list[str] | None = None
) -> dict:
    """Execute a revalidated proposal only after the proposal lifecycle approves it."""
    started = time.perf_counter()
    trace_id = trace_id or uuid.uuid4().hex
    with prepared_read_only_connection(use_approved_snapshot=True) as connection:
        result = validate_sql(sql, connection)
        if not result.valid:
            return _verdict("refused", trace_id, sql, result.checks, [], result.reason, started)
        try:
            rows = _execute_with_budget(connection, result.sql or "")
        except QueryBudgetExceeded:
            return _verdict(
                "refused",
                trace_id,
                sql,
                result.checks,
                [],
                f"Query exceeded the {EXECUTION_TIMEOUT_SECONDS}-second execution limit.",
                started,
            )
        except Exception as exc:
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
    verdict["assumptions"] = assumptions or []
    return verdict


def _execute_with_budget(connection, sql: str) -> list[dict]:
    """Interrupt a query that exceeds the bounded local execution window.

    DuckDB has no statement-timeout setting in the supported runtime. Its
    connection interrupt is therefore armed before execution and cancelled only
    after all preview rows are materialized; no partial result is returned.
    """
    timer = Timer(EXECUTION_TIMEOUT_SECONDS, connection.interrupt)
    timer.daemon = True
    timer.start()
    try:
        cursor = connection.execute(sql)
        return [
            dict(zip([column[0] for column in cursor.description], row, strict=True))
            for row in cursor.fetchall()
        ]
    except duckdb.InterruptException as exc:
        raise QueryBudgetExceeded from exc
    finally:
        timer.cancel()


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
        "snapshot": snapshot_status(),
    }
