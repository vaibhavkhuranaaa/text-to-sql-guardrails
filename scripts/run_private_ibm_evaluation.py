"""Run private semantic checks without retaining IBM rows or SQL in evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=Path("data/approved/ibm-aml-v8.duckdb"))
    parser.add_argument("--out", type=Path, default=Path("benchmarks/ibm-aml-v8-evaluation.json"))
    args = parser.parse_args()
    connection = duckdb.connect(str(args.snapshot), read_only=True)
    try:
        checks = {
            "row_count": (
                "SELECT COUNT(*) FROM benchmark_transactions",
                "SELECT SUM(1) FROM benchmark_transactions",
            ),
            "currency_groups": (
                "SELECT COUNT(DISTINCT payment_currency) FROM benchmark_transactions",
                "SELECT COUNT(*) FROM (SELECT payment_currency FROM benchmark_transactions GROUP BY 1)",
            ),
            "laundering_count": (
                "SELECT COUNT(*) FROM benchmark_transactions WHERE is_laundering",
                "SELECT SUM(CASE WHEN is_laundering THEN 1 ELSE 0 END) FROM benchmark_transactions",
            ),
        }
        passed = sum(
            connection.execute(left).fetchone() == connection.execute(right).fetchone()
            for left, right in checks.values()
        )
    finally:
        connection.close()
    report = {
        "evaluation_version": "ibm-aml-private-semantic-1",
        "benchmark_digest": hashlib.sha256(args.snapshot.read_bytes()).hexdigest(),
        "case_count": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "disclosure": "Private aggregate semantic evaluation only; no rows, labels, prompts, SQL, or identifiers retained.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
