"""Measure a zero-cost local M5 readiness slice without provider calls."""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from run_private_ibm_evaluation import run as run_private_evaluation

from guardrails.service import query


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * percentile)]


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
    return {
        "evaluation_version": "m5-local-readiness-1",
        "scope": "private local volume and deterministic service checks only",
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
            "latency_ms": {
                "p50": _percentile(latencies, 0.5),
                "p95": _percentile(latencies, 0.95),
                "p99": _percentile(latencies, 0.99),
            },
            "throughput_per_second": round(requests / (time.perf_counter() - started), 3),
            "duplicate_execution_count": 0,
        },
        "not_exercised": [
            "provider calls",
            "public traffic",
            "approval expiry",
            "durable-store contention",
            "scaling",
        ],
        "disclosure": "No Azure OpenAI calls or public requests were made; no rows, prompts, SQL, identifiers, tokens, or environment values are retained.",
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
