"""Short-lived, review-required proposal lifecycle; records only metadata events."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from .db import snapshot_status
from .foundry import FoundryUnavailable, generate
from .observability import event
from .service import execute_validated
from .validation import validate_sql

TTL_SECONDS = 300
DEFAULT_STORE_PATH = Path("/tmp/text-to-sql-guardrails-proposals.sqlite3")


@dataclass
class Proposal:
    proposal_id: str
    approval_hash: str
    sql: str
    assumptions: list[str]
    snapshot_checksum: str
    created_at: float
    validation: dict
    trace_id: str


def _store_path() -> Path:
    """Return the writable, owner-configurable store for pending approvals.

    The default is deliberately ephemeral at host/container restart. Deployments
    that need cross-replica approval must mount a private writable volume and set
    ``GUARDRAILS_PROPOSAL_STORE`` to a path on that volume.
    """
    return Path(os.getenv("GUARDRAILS_PROPOSAL_STORE", str(DEFAULT_STORE_PATH)))


def _connection() -> sqlite3.Connection:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS pending_proposals (
            proposal_id TEXT PRIMARY KEY,
            approval_hash TEXT NOT NULL,
            sql_text TEXT NOT NULL,
            assumptions_json TEXT NOT NULL,
            snapshot_checksum TEXT NOT NULL,
            created_at REAL NOT NULL,
            validation_json TEXT NOT NULL,
            trace_id TEXT NOT NULL
        )
        """
    )
    return connection


def _save(proposal: Proposal) -> None:
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO pending_proposals (
                proposal_id, approval_hash, sql_text, assumptions_json,
                snapshot_checksum, created_at, validation_json, trace_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                proposal.proposal_id,
                proposal.approval_hash,
                proposal.sql,
                json.dumps(proposal.assumptions),
                proposal.snapshot_checksum,
                proposal.created_at,
                json.dumps(proposal.validation),
                proposal.trace_id,
            ),
        )


def _get(connection: sqlite3.Connection, proposal_id: str) -> Proposal | None:
    row = connection.execute(
        "SELECT * FROM pending_proposals WHERE proposal_id = ?", (proposal_id,)
    ).fetchone()
    if row is None:
        return None
    return Proposal(
        proposal_id=row["proposal_id"],
        approval_hash=row["approval_hash"],
        sql=row["sql_text"],
        assumptions=json.loads(row["assumptions_json"]),
        snapshot_checksum=row["snapshot_checksum"],
        created_at=row["created_at"],
        validation=json.loads(row["validation_json"]),
        trace_id=row["trace_id"],
    )


def _snapshot_checksum() -> str:
    snapshot = snapshot_status()
    return str(snapshot.get("snapshot_sha256") or snapshot.get("sha256"))


def create(question: str) -> dict:
    trace_id = uuid.uuid4().hex
    try:
        generated = generate(question)
    except FoundryUnavailable as exc:
        event("proposal_refused", trace_id=trace_id, reason="provider_unavailable")
        return {"status": "refused", "trace_id": trace_id, "reason": str(exc)}
    result = validate_sql(generated.sql)
    if not result.valid:
        event("proposal_refused", trace_id=trace_id, reason="policy")
        return {
            "status": "refused",
            "trace_id": trace_id,
            "generated_sql": generated.sql,
            "reason": result.reason,
            "validation_checks": result.checks,
        }
    proposal_id, approval_token = uuid.uuid4().hex, secrets.token_urlsafe(24)
    review = {
        "policy_verdict": "allowed",
        "validation_checks": result.checks,
        "referenced_tables": result.referenced_tables or [],
        "referenced_columns": result.referenced_columns or [],
        "explain_summary": result.explain_summary,
        "estimated_result_shape": f"At most {100} preview rows.",
    }
    proposal = Proposal(
        proposal_id,
        hashlib.sha256(approval_token.encode()).hexdigest(),
        result.sql or "",
        generated.assumptions,
        _snapshot_checksum(),
        time.time(),
        review,
        trace_id,
    )
    _save(proposal)
    event("proposal_created", trace_id=trace_id, proposal_id=proposal_id, model=generated.model)
    return {
        "status": "proposed",
        "proposal_id": proposal_id,
        "approval_token": approval_token,
        "trace_id": trace_id,
        "generated_sql": proposal.sql,
        "assumptions": proposal.assumptions,
        **proposal.validation,
        "snapshot": snapshot_status(),
    }


def execute(proposal_id: str, approval_token: str) -> dict:
    # Serialize read/check/consume so two simultaneous approvals cannot execute
    # the same SQL twice. The proposal is consumed before execution by design.
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        proposal = _get(connection, proposal_id)
        if proposal is None:
            connection.execute("COMMIT")
            return {"status": "refused", "reason": "Unknown or already-consumed proposal."}
        if time.time() - proposal.created_at > TTL_SECONDS:
            connection.execute(
                "DELETE FROM pending_proposals WHERE proposal_id = ?", (proposal_id,)
            )
            connection.execute("COMMIT")
            event(
                "proposal_refused",
                trace_id=proposal.trace_id,
                proposal_id=proposal_id,
                reason="stale",
            )
            return {"status": "refused", "reason": "Proposal expired; request a new review."}
        token_hash = hashlib.sha256(approval_token.encode()).hexdigest()
        if not secrets.compare_digest(proposal.approval_hash, token_hash):
            connection.execute("COMMIT")
            event(
                "proposal_refused",
                trace_id=proposal.trace_id,
                proposal_id=proposal_id,
                reason="approval",
            )
            return {"status": "refused", "reason": "Explicit analyst approval token is required."}
        if proposal.snapshot_checksum != _snapshot_checksum():
            connection.execute("COMMIT")
            return {"status": "refused", "reason": "Snapshot changed; request a new proposal."}
        result = validate_sql(proposal.sql)
        if not result.valid:
            connection.execute("COMMIT")
            return {"status": "refused", "reason": result.reason}
        connection.execute("DELETE FROM pending_proposals WHERE proposal_id = ?", (proposal_id,))
        connection.execute("COMMIT")
    event("proposal_approved", trace_id=proposal.trace_id, proposal_id=proposal_id)
    return execute_validated(
        result.sql or "", trace_id=proposal.trace_id, assumptions=proposal.assumptions
    )
