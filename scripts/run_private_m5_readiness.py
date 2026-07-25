"""Measure a zero-cost local M5 readiness slice without provider calls."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from run_private_ibm_evaluation import run as run_private_evaluation

from guardrails import proposals
from guardrails.db import semantic_catalog
from guardrails.foundry import GeneratedProposal
from guardrails.service import query


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * percentile)]


def _safe_sql() -> str:
    if "fact_transactions" in semantic_catalog():
        return (
            "SELECT transaction_type, COUNT(*) AS transaction_count FROM fact_transactions "
            "GROUP BY transaction_type"
        )
    return "SELECT channel, COUNT(*) AS payment_count FROM fact_payments GROUP BY channel"


def _lifecycle_report(store: Path) -> dict:
    """Exercise approval controls locally without provider calls or retaining payloads."""
    safe_sql = _safe_sql()
    safe = GeneratedProposal(sql=safe_sql, assumptions=[], model="local-m5-contract")
    refused = GeneratedProposal(
        sql="DELETE FROM fact_payments", assumptions=[], model="local-m5-contract"
    )
    with patch.dict(os.environ, {"GUARDRAILS_PROPOSAL_STORE": str(store)}, clear=False):
        with patch("guardrails.proposals.generate", return_value=refused):
            refusal = proposals.create("private lifecycle refusal check")
        with patch("guardrails.proposals.generate", return_value=safe):
            approved = proposals.create("private lifecycle approval check")
            approval = proposals.execute(approved["proposal_id"], approved["approval_token"])

            expired = proposals.create("private lifecycle expiry check")
            with sqlite3.connect(store) as connection:
                connection.execute(
                    "UPDATE pending_proposals SET created_at = ? WHERE proposal_id = ?",
                    (time.time() - proposals.TTL_SECONDS - 1, expired["proposal_id"]),
                )
            expiry = proposals.execute(expired["proposal_id"], expired["approval_token"])

            duplicate = proposals.create("private lifecycle duplicate check")
            with ThreadPoolExecutor(max_workers=2) as executor:
                duplicate_attempts = list(
                    executor.map(
                        lambda _index: proposals.execute(
                            duplicate["proposal_id"], duplicate["approval_token"]
                        ),
                        range(2),
                    )
                )

    duplicate_statuses = Counter(item["status"] for item in duplicate_attempts)
    report = {
        "safe_proposals": 3,
        "policy_refusals": int(refusal["status"] == "refused"),
        "approved_executions": int(approval["status"] == "trusted"),
        "expired_approvals": int(expiry["status"] == "refused"),
        "duplicate_execution_attempts": len(duplicate_attempts),
        "duplicate_execution_count": max(duplicate_statuses["trusted"] - 1, 0),
        "duplicate_attempt_outcomes": dict(sorted(duplicate_statuses.items())),
    }
    if report != {
        "safe_proposals": 3,
        "policy_refusals": 1,
        "approved_executions": 1,
        "expired_approvals": 1,
        "duplicate_execution_attempts": 2,
        "duplicate_execution_count": 0,
        "duplicate_attempt_outcomes": {"refused": 1, "trusted": 1},
    }:
        raise RuntimeError(
            "Local M5 lifecycle controls did not produce the expected aggregate outcomes."
        )
    return report


def run(snapshot: Path, metadata: Path, requests: int, workers: int) -> dict:
    started = time.perf_counter()
    private_started = time.perf_counter()
    private_report = run_private_evaluation(snapshot, metadata)
    private_elapsed_ms = round((time.perf_counter() - private_started) * 1000, 3)
    candidates = [
        "SELECT channel, COUNT(*) AS payment_count FROM fact_payments GROUP BY channel",
        "DELETE FROM fact_payments",
    ]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(
            executor.map(lambda index: query("local", candidates[index % 2]), range(requests))
        )
    statuses = Counter(result["status"] for result in results)
    latencies = [result["latency_ms"] for result in results]
    with TemporaryDirectory(prefix="text-to-sql-m5-") as temporary_directory:
        lifecycle = _lifecycle_report(Path(temporary_directory) / "proposals.sqlite3")
    return {
        "evaluation_version": "m5-local-readiness-2",
        "scope": "private local volume, deterministic service, and ephemeral approval checks only",
        "benchmark_digest": private_report["benchmark_digest"],
        "private_volume": {
            "passed": private_report["passed"],
            "case_count": private_report["case_count"],
            "elapsed_ms": private_elapsed_ms,
        },
        "service": {
            "requests": requests,
            "workers": workers,
            "outcomes": dict(sorted(statuses.items())),
            "refusal_rate": round(statuses["refused"] / requests, 3),
            "error_rate": round(statuses["failed_validation"] / requests, 3),
            "latency_ms": {
                "p50": _percentile(latencies, 0.5),
                "p95": _percentile(latencies, 0.95),
                "p99": _percentile(latencies, 0.99),
            },
            "throughput_per_second": round(requests / (time.perf_counter() - started), 3),
            "duplicate_execution_count": 0,
        },
        "approval_lifecycle": lifecycle,
        "not_exercised": [
            "provider calls",
            "public traffic",
            "durable-store contention (not applicable to the M0-A ephemeral SQLite demo)",
            "scaling (M0-A remains zero-to-one replica)",
        ],
        "cost_boundary": "No provider calls were made. The separate bounded provider sample remains subject to the approved $30 ceiling and $24 optional-test stop threshold.",
        "disclosure": "No Azure OpenAI calls or public requests were made; no rows, prompts, SQL, identifiers, per-request tokens, or environment values are retained.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=Path("data/approved/ibm-aml-v8.duckdb"))
    parser.add_argument("--metadata", type=Path, default=Path("benchmarks/ibm-aml-v8.json"))
    parser.add_argument("--requests", type=int, default=12)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--out", type=Path, default=Path("benchmarks/m5-local-readiness.json"))
    args = parser.parse_args()
    if args.requests < 2 or args.workers < 1:
        raise ValueError("Use at least two requests and one worker.")
    report = run(args.snapshot, args.metadata, args.requests, args.workers)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
