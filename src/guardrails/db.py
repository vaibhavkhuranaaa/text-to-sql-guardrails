from __future__ import annotations

import hashlib
import json
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import duckdb

FIXTURE_PATH = Path(__file__).parents[2] / "data" / "fixtures" / "payments.json"
SCHEMA = {
    "fact_payments": {
        "payment_id",
        "customer_id",
        "payment_date",
        "amount_usd",
        "status",
        "channel",
    },
    "dim_customer": {"customer_id", "country", "segment"},
}


def fixture_sha256() -> str:
    return hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()


def connect(database: str = ":memory:") -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database, read_only=False)


@contextmanager
def prepared_read_only_connection() -> Iterator[duckdb.DuckDBPyConnection]:
    """Load deterministically, then execute only through DuckDB's read-only mode."""
    with tempfile.TemporaryDirectory(prefix="text-to-sql-guardrails-") as directory:
        database = Path(directory) / "payments.duckdb"
        loader = connect(str(database))
        load_fixture(loader)
        loader.close()
        reader = duckdb.connect(str(database), read_only=True)
        try:
            yield reader
        finally:
            reader.close()


def load_fixture(connection: duckdb.DuckDBPyConnection) -> dict[str, int | str]:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    connection.execute(
        "CREATE TABLE IF NOT EXISTS dim_customer (customer_id VARCHAR PRIMARY KEY, country VARCHAR NOT NULL, segment VARCHAR NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS fact_payments (payment_id VARCHAR PRIMARY KEY, customer_id VARCHAR NOT NULL, payment_date DATE NOT NULL, amount_usd DECIMAL(12, 2) NOT NULL, status VARCHAR NOT NULL, channel VARCHAR NOT NULL)"
    )
    connection.execute("DELETE FROM fact_payments")
    connection.execute("DELETE FROM dim_customer")
    connection.executemany(
        "INSERT INTO dim_customer VALUES (?, ?, ?)",
        [(r["customer_id"], r["country"], r["segment"]) for r in data["customers"]],
    )
    connection.executemany(
        "INSERT INTO fact_payments VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                r["payment_id"],
                r["customer_id"],
                r["payment_date"],
                r["amount_usd"],
                r["status"],
                r["channel"],
            )
            for r in data["payments"]
        ],
    )
    return {
        "customers": len(data["customers"]),
        "payments": len(data["payments"]),
        "sha256": fixture_sha256(),
    }


def schema_snapshot(connection: duckdb.DuckDBPyConnection) -> dict[str, list[str]]:
    return {
        table: [r[1] for r in connection.execute(f"PRAGMA table_info('{table}')").fetchall()]
        for table in SCHEMA
    }
