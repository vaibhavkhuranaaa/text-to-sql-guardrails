"""Measure a snapshot locally; the report is generated only from an actual run."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import duckdb


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("benchmarks/latest.json"))
    args = parser.parse_args()
    started = time.perf_counter()
    connection = duckdb.connect(str(args.snapshot), read_only=True)
    try:
        rows = connection.execute("SELECT COUNT(*) FROM fact_transactions").fetchone()[0]
        groups = connection.execute(
            "SELECT transaction_type, COUNT(*) FROM fact_transactions GROUP BY transaction_type ORDER BY transaction_type"
        ).fetchall()
    finally:
        connection.close()
    report = {
        "snapshot": str(args.snapshot),
        "fact_transaction_rows": rows,
        "transaction_type_groups": len(groups),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "disclosure": "Local measurement; not a production performance claim.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
