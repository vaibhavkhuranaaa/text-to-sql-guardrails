import pytest
from fastapi.testclient import TestClient

from guardrails.api import app
from guardrails.catalog import SUPPORTED_QUESTIONS
from guardrails.db import connect, load_fixture, prepared_read_only_connection
from guardrails.service import query
from guardrails.validation import validate


def test_supported_question_is_trusted():
    verdict = query(SUPPORTED_QUESTIONS[0].question)
    assert verdict["status"] == "trusted"
    assert verdict["result_preview"] == [{"total_completed_amount_usd": 41.25}]
    assert verdict["cost_usd"] == 0.0


def test_typed_api_contract_returns_a_verdict():
    response = TestClient(app).post("/v1/query", json={"question": SUPPORTED_QUESTIONS[0].question})
    assert response.status_code == 200
    assert response.json()["status"] == "trusted"


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


def test_loader_is_idempotent():
    connection = connect()
    first = load_fixture(connection)
    second = load_fixture(connection)
    assert first == second
    assert connection.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0] == 3
    assert connection.execute("SELECT COUNT(*) FROM fact_payments").fetchone()[0] == 4


def test_empty_result_is_trusted():
    verdict = query("demo", "SELECT * FROM fact_payments WHERE status = 'reversed'")
    assert verdict["status"] == "trusted"
    assert verdict["result_preview"] == []
