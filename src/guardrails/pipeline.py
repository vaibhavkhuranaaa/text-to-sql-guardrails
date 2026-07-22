"""Owner-triggered public-data release pipeline; never runs during console startup."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from .db import APPROVED_SCHEMA

ROOT = Path(__file__).parents[2]
MANIFEST_PATH = ROOT / "data" / "source_manifest.json"


class DataQualityError(ValueError):
    """Input is not eligible for an approved snapshot."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = {"dataset", "doi", "version", "license", "landing_page", "files"}
    missing = required - set(manifest)
    if missing:
        raise DataQualityError(f"Source manifest is incomplete: {sorted(missing)}.")
    return manifest


def fetch_source(manifest_path: Path, destination: Path) -> list[Path]:
    """Fetch a pinned version and reject anything without a declared source checksum."""
    manifest = load_manifest(manifest_path)
    missing_checksums = [item["name"] for item in manifest["files"] if not item.get("sha256")]
    if missing_checksums:
        raise DataQualityError(
            f"Checksum missing for {missing_checksums}; refusing unpinned download."
        )
    with urllib.request.urlopen(manifest["metadata_api"], timeout=30) as response:
        metadata = json.load(response)
    files = metadata.get("files", metadata.get("data", []))
    destination.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for expected in manifest["files"]:
        remote = next((item for item in files if item.get("name") == expected["name"]), None)
        link = remote and (remote.get("download_url") or remote.get("url"))
        if not link:
            raise DataQualityError(
                f"Pinned source file unavailable in source metadata: {expected['name']}."
            )
        target = destination / expected["name"]
        with urllib.request.urlopen(link, timeout=120) as response, target.open("wb") as output:
            shutil.copyfileobj(response, output)
        if sha256(target) != expected["sha256"]:
            target.unlink(missing_ok=True)
            raise DataQualityError(f"Checksum mismatch for {expected['name']}.")
        downloaded.append(target)
    return downloaded


def profile_sources(sources: list[Path]) -> dict:
    """Create row-free, reproducible schema/quality evidence for reviewed CSVs.

    This deliberately records header-level classifications and aggregate counters only;
    source records and identifier values never enter the profile artifact.
    """
    if not sources:
        raise DataQualityError("At least one source CSV is required for profiling.")
    reports = []
    for source in sources:
        if not source.is_file():
            raise DataQualityError(f"Source file is missing: {source}.")
        with source.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise DataQualityError(f"Source has no header row: {source.name}.")
            fields = {name: {"null_count": 0} for name in reader.fieldnames}
            row_count = 0
            for row in reader:
                row_count += 1
                for name in reader.fieldnames:
                    if not (row.get(name) or "").strip():
                        fields[name]["null_count"] += 1
        reports.append(
            {
                "file": source.name,
                "sha256": sha256(source),
                "row_count": row_count,
                "fields": [
                    {
                        "name": name,
                        "classification": _classification(name),
                        **metrics,
                    }
                    for name, metrics in fields.items()
                ],
            }
        )
    return {
        "profile_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "disclosure": "Aggregate schema and quality profile only; no source rows or identifier values are included.",
        "sources": reports,
    }


def write_profile(sources: list[Path], output: Path) -> dict:
    profile = profile_sources(sources)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    return profile


def _classification(name: str) -> str:
    normalised = "".join(char for char in name.lower() if char.isalnum())
    if normalised in {"initiator", "recipient"} or any(
        token in normalised for token in ("id", "phone", "name", "address", "email")
    ):
        return "excluded_identifier"
    return "candidate_analytic"


SOURCE_COLUMNS = (
    "step",
    "transactionType",
    "amount",
    "initiator",
    "oldBalInitiator",
    "newBalInitiator",
    "recipient",
    "oldBalRecipient",
    "newBalRecipient",
    "isFraud",
)


def build_snapshot(source: Path, snapshot: Path, manifest_path: Path = MANIFEST_PATH) -> dict:
    """Publish an identifier-free, observed-schema snapshot without source-row retention."""
    manifest = load_manifest(manifest_path)
    if not source.is_file():
        raise DataQualityError(f"Source file is missing: {source}.")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=snapshot.parent, prefix="snapshot-") as directory:
        temporary = Path(directory) / snapshot.name
        connection = duckdb.connect(str(temporary))
        try:
            with source.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if tuple(reader.fieldnames or ()) != SOURCE_COLUMNS:
                    raise DataQualityError(
                        "Schema drift: source headers do not match the reviewed V2 contract."
                    )
            source_sql = str(source.resolve()).replace("'", "''")
            connection.execute(
                "CREATE TEMP TABLE staged_transactions AS "
                "SELECT TRY_CAST(step AS BIGINT) AS simulation_step, "
                "TRIM(transactionType) AS transaction_type, "
                "TRY_CAST(amount AS DECIMAL(20, 2)) AS amount, "
                "TRY_CAST(oldBalInitiator AS DECIMAL(20, 2)) AS old_initiator_balance, "
                "TRY_CAST(newBalInitiator AS DECIMAL(20, 2)) AS new_initiator_balance, "
                "TRY_CAST(oldBalRecipient AS DECIMAL(20, 2)) AS old_recipient_balance, "
                "TRY_CAST(newBalRecipient AS DECIMAL(20, 2)) AS new_recipient_balance, "
                "CASE WHEN TRY_CAST(isFraud AS BIGINT) = 0 THEN FALSE "
                "WHEN TRY_CAST(isFraud AS BIGINT) = 1 THEN TRUE END AS is_fraud "
                f"FROM read_csv_auto('{source_sql}', header = true)"
            )
            row_count = connection.execute("SELECT COUNT(*) FROM staged_transactions").fetchone()[0]
            if not row_count:
                raise DataQualityError("Quality failure: source contains no usable records.")
            invalid_rows = connection.execute(
                "SELECT COUNT(*) FROM staged_transactions WHERE simulation_step IS NULL "
                "OR simulation_step < 0 OR transaction_type IS NULL OR transaction_type = '' "
                "OR amount IS NULL OR amount < 0 OR is_fraud IS NULL"
            ).fetchone()[0]
            if invalid_rows:
                raise DataQualityError("Curated type and quality checks failed.")
            connection.execute(
                "CREATE TABLE fact_transactions AS SELECT * FROM staged_transactions"
            )
            for table, expected in APPROVED_SCHEMA.items():
                actual = {
                    row[1] for row in connection.execute(f"PRAGMA table_info('{table}')").fetchall()
                }
                if actual != expected:
                    raise DataQualityError(f"Schema verification failed for {table}.")
        finally:
            connection.close()
        os.replace(temporary, snapshot)
    metadata = {
        "snapshot_sha256": sha256(snapshot),
        "source": manifest["dataset"],
        "source_doi": manifest["doi"],
        "source_version": manifest["version"],
        "source_sha256": sha256(source),
        "refreshed_at_utc": datetime.now(UTC).isoformat(),
        "curated_schema": {table: sorted(columns) for table, columns in APPROVED_SCHEMA.items()},
        "excluded_source_columns": ["initiator", "recipient"],
        "quality": {
            "status": "passed",
            "transactions": row_count,
            "required_fields": ["simulation_step", "transaction_type", "amount", "is_fraud"],
            "nullable_fields": [
                "old_initiator_balance",
                "new_initiator_balance",
                "old_recipient_balance",
                "new_recipient_balance",
            ],
        },
    }
    snapshot.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata
