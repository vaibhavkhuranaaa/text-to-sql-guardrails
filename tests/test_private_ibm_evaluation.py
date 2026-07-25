import importlib.util
import json
from pathlib import Path

import duckdb


def _load_evaluator():
    path = Path(__file__).parents[1] / "scripts" / "run_private_ibm_evaluation.py"
    spec = importlib.util.spec_from_file_location("run_private_ibm_evaluation", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_private_evaluation_is_aggregate_only(tmp_path):
    snapshot = tmp_path / "benchmark.duckdb"
    with duckdb.connect(str(snapshot)) as connection:
        connection.execute(
            "CREATE TABLE benchmark_transactions AS "
            "SELECT TIMESTAMP '2022-01-01' AS transaction_timestamp, 1 AS amount_received, "
            "'USD' AS receiving_currency, 1 AS amount_paid, 'USD' AS payment_currency, "
            "'ACH' AS payment_format, FALSE AS is_laundering"
        )
    metadata = tmp_path / "benchmark.json"
    metadata.write_text(json.dumps({"benchmark_sha256": "a" * 64}), encoding="utf-8")

    report = _load_evaluator().run(snapshot, metadata)

    assert report["case_count"] == 7
    assert report["passed"] == 7
    assert report["failed"] == 0
    assert "SELECT" not in json.dumps(report)
