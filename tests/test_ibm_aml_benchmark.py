import hashlib
import importlib.util
import json
from pathlib import Path

import duckdb


def _load_builder():
    path = Path(__file__).parents[1] / "scripts" / "build_ibm_aml_benchmark.py"
    spec = importlib.util.spec_from_file_location("build_ibm_aml_benchmark", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_ibm_builder_excludes_account_and_bank_fields_and_is_repeatable(tmp_path):
    builder = _load_builder()
    raw = tmp_path / "raw"
    raw.mkdir()
    transactions = raw / "HI-Small_Trans.csv"
    transactions.write_text(
        "Timestamp,From Bank,Account,To Bank,Account,Amount Received,Receiving Currency,"
        "Amount Paid,Payment Currency,Payment Format,Is Laundering\n"
        "2022-09-01 00:00:00,bank-a,account-a,bank-b,account-b,10.00,USD,10.00,USD,ACH,0\n",
        encoding="utf-8",
    )
    patterns = raw / "HI-Small_Patterns.txt"
    patterns.write_text("private pattern detail\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "provider": "Kaggle",
                "provider_ref": "test/ibm-aml",
                "version": 8,
                "license": "Community Data License Agreement - Sharing - Version 1.0",
                "files": [
                    {
                        "name": transactions.name,
                        "bytes": transactions.stat().st_size,
                        "sha256": _sha256(transactions),
                    },
                    {
                        "name": patterns.name,
                        "bytes": patterns.stat().st_size,
                        "sha256": _sha256(patterns),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    first = tmp_path / "first.duckdb"
    second = tmp_path / "second.duckdb"
    first_report = builder.build_benchmark(raw, first, tmp_path / "first.json", manifest)
    second_report = builder.build_benchmark(raw, second, tmp_path / "second.json", manifest)

    assert first_report["row_count"] == 1
    assert first_report["benchmark_sha256"] == second_report["benchmark_sha256"]
    with duckdb.connect(str(first), read_only=True) as connection:
        columns = [
            row[1]
            for row in connection.execute("PRAGMA table_info('benchmark_transactions')").fetchall()
        ]
    assert columns == list(builder.CURATED_COLUMNS)
    assert not {"From Bank", "To Bank", "Account", "Account_1"} & set(columns)
