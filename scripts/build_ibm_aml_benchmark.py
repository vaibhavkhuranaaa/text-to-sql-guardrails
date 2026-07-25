"""Build an identifier-free private IBM AML benchmark from pinned local artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import duckdb

ROOT = Path(__file__).parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "ibm_aml_manifest.json"
SOURCE_COLUMNS = (
    "Timestamp",
    "From Bank",
    "Account",
    "To Bank",
    "Account",
    "Amount Received",
    "Receiving Currency",
    "Amount Paid",
    "Payment Currency",
    "Payment Format",
    "Is Laundering",
)
CURATED_COLUMNS = (
    "transaction_timestamp",
    "amount_received",
    "receiving_currency",
    "amount_paid",
    "payment_currency",
    "payment_format",
    "is_laundering",
)


class BenchmarkBoundaryError(ValueError):
    """The private source or derivative does not satisfy the M3 boundary."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = {"provider", "provider_ref", "version", "license", "files"}
    if required - set(manifest):
        raise BenchmarkBoundaryError("IBM benchmark manifest is incomplete.")
    if manifest["version"] != 8:
        raise BenchmarkBoundaryError("Only the owner-approved IBM dataset version 8 is permitted.")
    if manifest["license"] != "Community Data License Agreement - Sharing - Version 1.0":
        raise BenchmarkBoundaryError("IBM benchmark license does not match the approved record.")
    return manifest


def verify_artifacts(raw_dir: Path, manifest_path: Path = DEFAULT_MANIFEST) -> dict:
    """Verify names, byte counts, and SHA-256 values without inspecting source rows."""
    manifest = _load_manifest(manifest_path)
    verified = []
    for expected in manifest["files"]:
        path = raw_dir / expected["name"]
        if not path.is_file():
            raise BenchmarkBoundaryError(f"Missing approved IBM artifact: {expected['name']}.")
        if path.stat().st_size != expected["bytes"]:
            raise BenchmarkBoundaryError(f"Byte-count mismatch for {expected['name']}.")
        digest = sha256(path)
        if digest != expected["sha256"]:
            raise BenchmarkBoundaryError(f"Checksum mismatch for {expected['name']}.")
        verified.append({"name": expected["name"], "bytes": expected["bytes"], "sha256": digest})
    return {"provider": manifest["provider"], "version": manifest["version"], "files": verified}


def _source_sql(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def _content_sha256(connection: duckdb.DuckDBPyConnection) -> str:
    """Hash the curated rows in source order; DuckDB file bytes are not reproducible."""
    digest = hashlib.sha256()
    cursor = connection.execute(
        "SELECT transaction_timestamp, amount_received, receiving_currency, amount_paid, "
        "payment_currency, payment_format, is_laundering FROM benchmark_transactions"
    )
    while rows := cursor.fetchmany(10_000):
        for row in rows:
            digest.update(json.dumps(row, default=str, separators=(",", ":")).encode())
            digest.update(b"\n")
    return digest.hexdigest()


def build_benchmark(
    raw_dir: Path,
    output: Path,
    evidence: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> dict:
    """Create a private DuckDB derivative with no account or bank identifiers."""
    verification = verify_artifacts(raw_dir, manifest_path)
    source = raw_dir / "HI-Small_Trans.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix="ibm-aml-") as temporary_dir:
        temporary = Path(temporary_dir) / output.name
        connection = duckdb.connect(str(temporary))
        try:
            with source.open(encoding="utf-8-sig", newline="") as handle:
                header = tuple(next(csv.reader(handle)))
            if header != SOURCE_COLUMNS:
                raise BenchmarkBoundaryError(
                    "IBM transaction schema differs from the approved version-8 contract."
                )
            connection.execute(
                "CREATE TABLE benchmark_transactions AS "
                "SELECT "
                "TRY_CAST(Timestamp AS TIMESTAMP) AS transaction_timestamp, "
                'TRY_CAST("Amount Received" AS DECIMAL(20, 2)) AS amount_received, '
                'TRIM("Receiving Currency") AS receiving_currency, '
                'TRY_CAST("Amount Paid" AS DECIMAL(20, 2)) AS amount_paid, '
                'TRIM("Payment Currency") AS payment_currency, '
                'TRIM("Payment Format") AS payment_format, '
                'CASE WHEN TRY_CAST("Is Laundering" AS BIGINT) = 0 THEN FALSE '
                'WHEN TRY_CAST("Is Laundering" AS BIGINT) = 1 THEN TRUE END AS is_laundering '
                f"FROM read_csv_auto('{_source_sql(source)}', header = true)"
            )
            actual_columns = tuple(
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info('benchmark_transactions')"
                ).fetchall()
            )
            if actual_columns != CURATED_COLUMNS:
                raise BenchmarkBoundaryError("Private derivative contains an unapproved field.")
            row_count, invalid_rows, laundering_count = connection.execute(
                "SELECT COUNT(*), "
                "COUNT(*) FILTER (WHERE transaction_timestamp IS NULL OR amount_received IS NULL "
                "OR amount_received < 0 OR amount_paid IS NULL OR amount_paid < 0 "
                "OR receiving_currency IS NULL OR receiving_currency = '' "
                "OR payment_currency IS NULL OR payment_currency = '' "
                "OR payment_format IS NULL OR payment_format = '' OR is_laundering IS NULL), "
                "COUNT(*) FILTER (WHERE is_laundering) "
                "FROM benchmark_transactions"
            ).fetchone()
            if not row_count or invalid_rows:
                raise BenchmarkBoundaryError("Private derivative failed aggregate quality checks.")
            content_sha256 = _content_sha256(connection)
        finally:
            connection.close()
        os.replace(temporary, output)
    report = {
        "schema_version": 1,
        "transform_version": "ibm-aml-v8-curated-1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": verification,
        "benchmark_sha256": content_sha256,
        "duckdb_file_sha256": sha256(output),
        "row_count": row_count,
        "curated_columns": list(CURATED_COLUMNS),
        "aggregate_outcomes": {
            "quality_status": "passed",
            "invalid_rows": invalid_rows,
            "laundering_rows": laundering_count,
        },
        "retention": "Delete raw and derived local artifacts after 30 days; retain only row-free provenance and aggregate evidence.",
        "disclosure": "Private synthetic benchmark evidence only; no source rows, account values, bank identifiers, pattern details, or raw labels are retained here.",
    }
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/ibm-aml-v8"))
    parser.add_argument("--output", type=Path, default=Path("data/approved/ibm-aml-v8.duckdb"))
    parser.add_argument("--evidence", type=Path, default=Path("benchmarks/ibm-aml-v8.json"))
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    print(
        json.dumps(
            build_benchmark(args.raw_dir, args.output, args.evidence, args.manifest), indent=2
        )
    )


if __name__ == "__main__":
    main()
