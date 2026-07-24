from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import duckdb

ASSET_ROOT = Path(os.getenv("GUARDRAILS_ASSET_ROOT", str(Path(__file__).parents[2])))
FIXTURE_PATH = ASSET_ROOT / "data" / "fixtures" / "payments.json"
APPROVED_SNAPSHOT_PATH = Path(__file__).parents[2] / "data" / "approved" / "payments.duckdb"
SNAPSHOT_METADATA_PATH = APPROVED_SNAPSHOT_PATH.with_suffix(".metadata.json")
DEMO_SCHEMA = {
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
APPROVED_SCHEMA = {
    "fact_transactions": {
        "simulation_step",
        "transaction_type",
        "amount",
        "old_initiator_balance",
        "new_initiator_balance",
        "old_recipient_balance",
        "new_recipient_balance",
        "is_fraud",
    }
}
# The committed fixture retains private join mechanics for the v1 walkthrough.
# Approved snapshots contain no source account identifiers at all.
IDENTIFIER_COLUMNS = {"payment_id", "customer_id", "initiator", "recipient"}
QUERY_MEMORY_LIMIT = os.getenv("GUARDRAILS_QUERY_MEMORY_LIMIT", "512MB")
QUERY_THREADS = int(os.getenv("GUARDRAILS_QUERY_THREADS", "2"))
SCHEMA = DEMO_SCHEMA


def policy_schema() -> dict[str, set[str]]:
    """Return the only schema eligible for SQL proposals and execution."""
    return APPROVED_SCHEMA if APPROVED_SNAPSHOT_PATH.exists() else DEMO_SCHEMA


def semantic_catalog() -> dict[str, list[str]]:
    """Catalog safe for prompt context, UI lineage, and proposal metadata."""
    return {
        table: sorted(columns - IDENTIFIER_COLUMNS) for table, columns in policy_schema().items()
    }


def fixture_sha256() -> str:
    return hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()


def connect(database: str = ":memory:") -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database, read_only=False)


@contextmanager
def prepared_read_only_connection(
    *, use_approved_snapshot: bool = False
) -> Iterator[duckdb.DuckDBPyConnection]:
    """Open either the stable v1 fixture or the separately approved v2 snapshot."""
    if use_approved_snapshot and APPROVED_SNAPSHOT_PATH.exists():
        reader = duckdb.connect(str(APPROVED_SNAPSHOT_PATH), read_only=True)
        try:
            _apply_query_resource_limits(reader)
            yield reader
        finally:
            reader.close()
        return
    with tempfile.TemporaryDirectory(prefix="text-to-sql-guardrails-") as directory:
        database = Path(directory) / "payments.duckdb"
        loader = connect(str(database))
        load_fixture(loader)
        loader.close()
        reader = duckdb.connect(str(database), read_only=True)
        try:
            _apply_query_resource_limits(reader)
            yield reader
        finally:
            reader.close()


def _apply_query_resource_limits(connection: duckdb.DuckDBPyConnection) -> None:
    """Bound resources available to an analyst's read-only query.

    Values are deployment-owned environment configuration. Temp spill is disabled
    so a query cannot fill a host volume after exhausting its memory allowance.
    """
    connection.execute(f"SET memory_limit = '{QUERY_MEMORY_LIMIT}'")
    connection.execute(f"SET threads = {QUERY_THREADS}")
    connection.execute("SET max_temp_directory_size = '0B'")
    connection.execute("SET enable_progress_bar = false")


def snapshot_status() -> dict:
    """Return provenance without opening or exposing source records."""
    if SNAPSHOT_METADATA_PATH.exists() and APPROVED_SNAPSHOT_PATH.exists():
        metadata = json.loads(SNAPSHOT_METADATA_PATH.read_text(encoding="utf-8"))
        return {"state": "approved", "path": str(APPROVED_SNAPSHOT_PATH), **metadata}
    return {
        "state": "demo_fixture",
        "path": None,
        "source": "hand-authored synthetic demo fixture",
        "sha256": fixture_sha256(),
        "message": "No approved local snapshot is present. The console is using its committed demo fixture.",
    }


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
        for table in policy_schema()
    }
