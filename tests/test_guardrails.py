import io
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from guardrails.api import app
from guardrails.catalog import SUPPORTED_QUESTIONS
from guardrails.db import connect, load_fixture, prepared_read_only_connection, semantic_catalog
from guardrails.pipeline import (
    DataQualityError,
    build_snapshot,
    fetch_source,
    profile_sources,
)
from guardrails.service import query
from guardrails.validation import validate, validate_sql


def _v2_count_sql() -> tuple[str, str, str]:
    if "fact_transactions" in semantic_catalog():
        return (
            "SELECT transaction_type, COUNT(*) AS transaction_count FROM fact_transactions "
            "GROUP BY transaction_type",
            "fact_transactions",
            "fact_transactions.transaction_type",
        )
    return (
        "SELECT channel, COUNT(*) AS payment_count FROM fact_payments GROUP BY channel",
        "fact_payments",
        "fact_payments.channel",
    )


def test_supported_question_is_trusted():
    verdict = query(SUPPORTED_QUESTIONS[0].question)
    assert verdict["status"] == "trusted"
    assert verdict["result_preview"] == [{"total_completed_amount_usd": 41.25}]
    assert verdict["cost_usd"] == 0.0


def test_typed_api_contract_returns_a_verdict():
    response = TestClient(app).post("/v1/query", json={"question": SUPPORTED_QUESTIONS[0].question})
    assert response.status_code == 200
    assert response.json()["status"] == "trusted"


def test_console_and_snapshot_status_are_visible_without_source_rows():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    status = client.get("/v1/status").json()
    assert status["snapshot"]["state"] in {"demo_fixture", "approved"}
    assert client.get("/v1/evaluation").json()["case_count"] >= 1


def test_educational_examples_and_curated_preview_are_available():
    client = TestClient(app)
    examples = client.get("/v2/examples").json()
    assert [item["level"] for item in examples["examples"]] == [
        "Beginner",
        "Intermediate",
        "Advanced",
    ]
    preview = client.get("/v2/data-preview?limit=1").json()
    assert len(preview["rows"]) <= 1
    assert {"initiator", "recipient"}.isdisjoint(preview["columns"])


def test_unsupported_question_is_refused():
    assert query("Delete all payments")["status"] == "refused"


def test_unsafe_and_malformed_sql_are_rejected_before_execution():
    assert query("demo", "DELETE FROM fact_payments")["status"] == "refused"
    assert query("demo", "SELECT * FROM no_such_table")["status"] == "refused"
    assert query("demo", "SELECT unknown_column FROM fact_payments")["status"] == "refused"
    assert query("demo", "SELECT FROM")["status"] == "refused"


def test_only_select_reaches_duckdb():
    connection = connect()
    load_fixture(connection)
    before = connection.execute("SELECT COUNT(*) FROM fact_payments").fetchone()[0]
    assert not validate("DROP TABLE fact_payments", connection).valid
    after = connection.execute("SELECT COUNT(*) FROM fact_payments").fetchone()[0]
    assert before == after == 4


def test_execution_connection_is_read_only():
    with prepared_read_only_connection() as connection:
        with pytest.raises(Exception):
            connection.execute("DELETE FROM fact_payments")


def test_execution_connection_applies_resource_limits():
    with prepared_read_only_connection() as connection:
        settings = dict(
            connection.execute(
                "SELECT name, value FROM duckdb_settings() "
                "WHERE name IN ('memory_limit', 'threads', 'max_temp_directory_size')"
            ).fetchall()
        )
    assert settings["memory_limit"] != "0 bytes"
    assert settings["max_temp_directory_size"] == "0 bytes"
    assert settings["threads"] == "2"


def test_loader_is_idempotent():
    connection = connect()
    first = load_fixture(connection)
    second = load_fixture(connection)
    assert first == second
    assert connection.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0] == 3
    assert connection.execute("SELECT COUNT(*) FROM fact_payments").fetchone()[0] == 4


def test_empty_result_is_trusted():
    verdict = query(
        "demo", "SELECT payment_date, amount_usd FROM fact_payments WHERE status = 'reversed'"
    )
    assert verdict["status"] == "trusted"
    assert verdict["result_preview"] == []


def test_snapshot_rejects_source_schema_drift(tmp_path):
    source = tmp_path / "drift.csv"
    source.write_text("identifier,value\nA,10\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"dataset":"test","doi":"test","version":1,"license":"test","landing_page":"test","files":[]}',
        encoding="utf-8",
    )
    with pytest.raises(DataQualityError, match="Schema drift"):
        build_snapshot(source, tmp_path / "snapshot.duckdb", manifest)


def test_snapshot_rejects_invalid_fraud_label(tmp_path):
    source = tmp_path / "invalid.csv"
    source.write_text(
        "step,transactionType,amount,initiator,oldBalInitiator,newBalInitiator,recipient,oldBalRecipient,newBalRecipient,isFraud\n"
        "1,PAYMENT,10,A,10,0,B,0,10,maybe\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"dataset":"test","doi":"test","version":1,"license":"test","landing_page":"test","files":[]}',
        encoding="utf-8",
    )
    with pytest.raises(DataQualityError, match="quality checks"):
        build_snapshot(source, tmp_path / "snapshot.duckdb", manifest)


def test_fetch_refuses_manifest_without_checksum_before_network(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"dataset":"test","doi":"test","version":1,"license":"test","landing_page":"test","metadata_api":"https://example.invalid","files":[{"name":"source.csv","sha256":null}]}',
        encoding="utf-8",
    )
    with pytest.raises(DataQualityError, match="Checksum missing"):
        fetch_source(manifest, tmp_path / "raw")


def test_snapshot_build_is_repeatable_and_writes_quality_metadata(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text(
        "step,transactionType,amount,initiator,oldBalInitiator,newBalInitiator,recipient,oldBalRecipient,newBalRecipient,isFraud\n"
        "1,PAYMENT,10,A,10,0,B,0,10,0\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"dataset":"test","doi":"test","version":1,"license":"test","landing_page":"test","files":[]}',
        encoding="utf-8",
    )
    snapshot = tmp_path / "approved.duckdb"
    first = build_snapshot(source, snapshot, manifest)
    second = build_snapshot(source, snapshot, manifest)
    assert first["quality"]["status"] == "passed"
    assert first["excluded_source_columns"] == ["initiator", "recipient"]
    assert first["quality"]["nullable_fields"] == [
        "old_initiator_balance",
        "new_initiator_balance",
        "old_recipient_balance",
        "new_recipient_balance",
    ]
    assert second["source_sha256"] == first["source_sha256"]
    assert snapshot.exists()


def test_snapshot_allows_null_balance_fields_but_requires_analytic_fields(tmp_path):
    source = tmp_path / "null-balances.csv"
    source.write_text(
        "step,transactionType,amount,initiator,oldBalInitiator,newBalInitiator,recipient,oldBalRecipient,newBalRecipient,isFraud\n"
        "1,PAYMENT,10,A,,,B,,,0\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"dataset":"test","doi":"test","version":1,"license":"test","landing_page":"test","files":[]}',
        encoding="utf-8",
    )
    snapshot = tmp_path / "approved.duckdb"
    build_snapshot(source, snapshot, manifest)
    connection = connect(str(snapshot))
    try:
        assert connection.execute(
            "SELECT old_initiator_balance IS NULL, new_recipient_balance IS NULL "
            "FROM fact_transactions"
        ).fetchone() == (True, True)
    finally:
        connection.close()


def test_profile_excludes_identifier_values_and_reports_aggregate_quality(tmp_path):
    source = tmp_path / "reviewed.csv"
    source.write_text("initiator,recipient,amount\nabc,def,10\nghi,jkl,\n", encoding="utf-8")
    profile = profile_sources([source])
    assert profile["sources"][0]["row_count"] == 2
    fields = {field["name"]: field for field in profile["sources"][0]["fields"]}
    assert fields["initiator"]["classification"] == "excluded_identifier"
    assert fields["recipient"]["classification"] == "excluded_identifier"
    assert fields["amount"]["null_count"] == 1
    assert "abc" not in str(profile)


def test_advanced_read_only_cte_window_and_set_operation_are_allowed():
    connection = connect()
    load_fixture(connection)
    result = validate(
        "WITH daily AS (SELECT payment_date, SUM(amount_usd) AS total FROM fact_payments "
        "GROUP BY payment_date) SELECT payment_date, total, AVG(total) OVER (ORDER BY payment_date) "
        "AS rolling_total FROM daily UNION ALL SELECT payment_date, total, total FROM daily",
        connection,
    )
    assert result.valid, result.reason
    assert result.referenced_tables == ["fact_payments"]


def test_ranking_requires_explicit_order_and_accepts_rank_with_order():
    connection = connect()
    load_fixture(connection)
    missing_order = validate("SELECT RANK() OVER () AS payment_rank FROM fact_payments", connection)
    assert not missing_order.valid
    ranked = validate(
        "SELECT channel, RANK() OVER (ORDER BY amount_usd DESC) AS payment_rank FROM fact_payments",
        connection,
    )
    assert ranked.valid, ranked.reason
    assert "ranking_order_explicit" in ranked.checks


def test_identifier_and_file_access_are_refused():
    assert not validate_sql("SELECT payment_id FROM fact_payments").valid
    assert not validate_sql("SELECT * FROM fact_payments").valid
    assert not validate_sql("SELECT * FROM read_csv_auto('outside.csv')").valid


def test_v2_never_executes_when_foundry_is_unconfigured(monkeypatch):
    monkeypatch.delenv("AZURE_FOUNDRY_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_FOUNDRY_DEPLOYMENT", raising=False)
    monkeypatch.delenv("AZURE_FOUNDRY_API_KEY", raising=False)
    response = TestClient(app).post(
        "/v2/query-proposals", json={"question": "Show payment counts."}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "refused"
    catalog = TestClient(app).get("/v2/semantic-catalog").json()["catalog"]
    assert {"initiator", "recipient"}.isdisjoint(
        {field for fields in catalog.values() for field in fields}
    )


def test_foundry_uses_entra_bearer_token_not_api_key(monkeypatch):
    from guardrails import foundry

    class Response:
        def __enter__(self):
            return io.BytesIO(
                json.dumps(
                    {
                        "choices": [
                            {
                                "message": {
                                    "content": '{"sql":"SELECT channel FROM fact_payments","assumptions":[]}'
                                }
                            }
                        ]
                    }
                ).encode()
            )

        def __exit__(self, *_args):
            return False

    captured = {}
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_FOUNDRY_DEPLOYMENT", "guarded-model")
    monkeypatch.setattr(foundry, "_access_token", lambda: "test-entraid-token")
    monkeypatch.setattr(
        foundry.urllib.request,
        "urlopen",
        lambda request, timeout: captured.update(request=request, timeout=timeout) or Response(),
    )
    proposal = foundry.generate("Show channels.")
    assert proposal.model == "guarded-model"
    assert captured["request"].full_url.endswith("/openai/v1/chat/completions")
    assert json.loads(captured["request"].data)["model"] == "guarded-model"
    assert captured["request"].get_header("Authorization") == "Bearer test-entraid-token"
    assert captured["request"].get_header("Api-key") is None


def test_v2_requires_approval_and_revalidates(monkeypatch, tmp_path):
    from guardrails.foundry import GeneratedProposal

    sql, table, referenced_column = _v2_count_sql()
    monkeypatch.setenv("GUARDRAILS_PROPOSAL_STORE", str(tmp_path / "proposals.sqlite3"))

    monkeypatch.setattr(
        "guardrails.proposals.generate",
        lambda _question: GeneratedProposal(
            sql=sql,
            assumptions=["Payment channel is present in the approved snapshot."],
            model="recorded-contract-test",
        ),
    )
    client = TestClient(app)
    proposal = client.post(
        "/v2/query-proposals", json={"question": "Show payment counts by channel."}
    ).json()
    assert proposal["status"] == "proposed"
    assert proposal["policy_verdict"] == "allowed"
    assert proposal["referenced_tables"] == [table]
    assert proposal["referenced_columns"] == [referenced_column]
    refused = client.post(
        f"/v2/query-proposals/{proposal['proposal_id']}/execute",
        json={"approval_token": "wrong-token-value-that-is-long-enough"},
    ).json()
    assert refused["status"] == "refused"
    executed = client.post(
        f"/v2/query-proposals/{proposal['proposal_id']}/execute",
        json={"approval_token": proposal["approval_token"]},
    ).json()
    assert executed["status"] == "trusted"
    assert executed["assumptions"]
    consumed = client.post(
        f"/v2/query-proposals/{proposal['proposal_id']}/execute",
        json={"approval_token": proposal["approval_token"]},
    ).json()
    assert consumed == {"status": "refused", "reason": "Unknown or already-consumed proposal."}


def test_v2_stale_proposal_is_refused_before_execution(monkeypatch, tmp_path):
    from guardrails.foundry import GeneratedProposal
    from guardrails.proposals import create, execute

    sql, _table, _column = _v2_count_sql()
    monkeypatch.setenv("GUARDRAILS_PROPOSAL_STORE", str(tmp_path / "proposals.sqlite3"))
    monkeypatch.setattr(
        "guardrails.proposals.generate",
        lambda _question: GeneratedProposal(
            sql=sql, assumptions=[], model="recorded-contract-test"
        ),
    )
    clock = iter([1000.0, 1301.0])
    monkeypatch.setattr("guardrails.proposals.time", SimpleNamespace(time=lambda: next(clock)))
    proposal = create("Show channels.")
    response = execute(proposal["proposal_id"], proposal["approval_token"])
    assert response == {"status": "refused", "reason": "Proposal expired; request a new review."}


def test_proposal_lifecycle_does_not_log_raw_question(monkeypatch, caplog):
    from guardrails.foundry import FoundryUnavailable

    secret_question = "Do not log this exact analyst question"
    monkeypatch.setattr(
        "guardrails.proposals.generate",
        lambda _question: (_ for _ in ()).throw(FoundryUnavailable("unavailable")),
    )
    with caplog.at_level("INFO", logger="guardrails"):
        response = TestClient(app).post("/v2/query-proposals", json={"question": secret_question})
    assert response.json()["status"] == "refused"
    assert secret_question not in caplog.text
