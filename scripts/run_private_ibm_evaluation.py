"""Run private aggregate checks without retaining IBM rows, prompts, or SQL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from guardrails.db import prepared_read_only_connection


def _benchmark_digest(metadata: Path) -> str:
    report = json.loads(metadata.read_text(encoding="utf-8"))
    digest = report.get("benchmark_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("Private benchmark metadata is missing its curated-content digest.")
    return digest


def _private_checks(connection: duckdb.DuckDBPyConnection) -> dict[str, bool]:
    checks = {
        "aggregation": (
            "SELECT COUNT(*) FROM benchmark_transactions",
            "SELECT SUM(1) FROM benchmark_transactions",
        ),
        "currency_groups": (
            "SELECT COUNT(DISTINCT payment_currency) FROM benchmark_transactions",
            "SELECT COUNT(*) FROM (SELECT payment_currency FROM benchmark_transactions GROUP BY 1)",
        ),
        "time_windows": (
            "SELECT COUNT(DISTINCT DATE_TRUNC('month', transaction_timestamp)) FROM benchmark_transactions",
            "SELECT COUNT(*) FROM (SELECT DATE_TRUNC('month', transaction_timestamp) FROM benchmark_transactions GROUP BY 1)",
        ),
        "nulls": (
            "SELECT COUNT(*) FILTER (WHERE payment_currency IS NULL) FROM benchmark_transactions",
            "SELECT SUM(CASE WHEN payment_currency IS NULL THEN 1 ELSE 0 END) FROM benchmark_transactions",
        ),
        "aggregate_join": (
            "SELECT COUNT(*) FROM (SELECT payment_currency, COUNT(*) AS n FROM benchmark_transactions GROUP BY 1) left_groups JOIN (SELECT payment_currency, COUNT(*) AS n FROM benchmark_transactions GROUP BY 1) right_groups USING (payment_currency) WHERE left_groups.n = right_groups.n",
            "SELECT COUNT(DISTINCT payment_currency) FROM benchmark_transactions",
        ),
        "label_aggregate": (
            "SELECT COUNT(*) FROM benchmark_transactions WHERE is_laundering",
            "SELECT SUM(CASE WHEN is_laundering THEN 1 ELSE 0 END) FROM benchmark_transactions",
        ),
    }
    return {
        name: connection.execute(left).fetchone() == connection.execute(right).fetchone()
        for name, (left, right) in checks.items()
    }


def _resource_limits_apply() -> bool:
    with prepared_read_only_connection() as connection:
        settings = dict(
            connection.execute(
                "SELECT name, value FROM duckdb_settings() "
                "WHERE name IN ('memory_limit', 'max_temp_directory_size')"
            ).fetchall()
        )
    return (
        settings["memory_limit"] != "0 bytes" and settings["max_temp_directory_size"] == "0 bytes"
    )


def run(snapshot: Path, metadata: Path) -> dict:
    connection = duckdb.connect(str(snapshot), read_only=True)
    try:
        checks = _private_checks(connection)
    finally:
        connection.close()
    checks["resource_limits"] = _resource_limits_apply()
    passed = sum(checks.values())
    return {
        "evaluation_version": "ibm-aml-private-semantic-2",
        "benchmark_digest": _benchmark_digest(metadata),
        "case_count": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "threshold": "All aggregate and resource-boundary checks must pass.",
        "limitations": "Private local evidence only; it does not measure model behavior, service load, or production performance.",
        "disclosure": "Private aggregate evaluation only; no rows, labels, prompts, SQL, identifiers, tokens, or environment values are retained.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=Path("data/approved/ibm-aml-v8.duckdb"))
    parser.add_argument("--metadata", type=Path, default=Path("benchmarks/ibm-aml-v8.json"))
    parser.add_argument("--out", type=Path, default=Path("benchmarks/ibm-aml-v8-evaluation.json"))
    args = parser.parse_args()
    report = run(args.snapshot, args.metadata)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
