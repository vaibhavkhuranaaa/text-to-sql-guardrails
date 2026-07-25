import json
from pathlib import Path


def test_m5_aggregate_readiness_evidence_is_redacted_and_complete():
    path = Path(__file__).parents[1] / "evidence" / "m5" / "aggregate-readiness.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))

    assert evidence["schemaVersion"] == 1
    assert evidence["classification"].startswith("private local bounded validation")
    assert evidence["provider_sample"]["attempted"] == 4
    assert evidence["provider_sample"]["completion_token_cap"] == 2048
    assert evidence["local_readiness"]["private_volume"] == {"case_count": 7, "passed": 7}
    assert evidence["local_readiness"]["service"]["duplicate_execution_count"] == 0
    assert evidence["local_readiness"]["service"]["refusal_rate"] == 0.5
    assert evidence["local_readiness"]["service"]["error_rate"] == 0.0
    assert evidence["local_readiness"]["approval_lifecycle"] == {
        "safe_proposals": 3,
        "policy_refusals": 1,
        "approved_executions": 1,
        "expired_approvals": 1,
        "concurrent_approval_attempts": 2,
        "duplicate_execution_count": 0,
    }
    assert evidence["container_boundary"]["passed"] is True
    assert "not applicable" in evidence["not_exercised"][1]

    prohibited_keys = {"question", "sql", "result_rows", "identifier", "environment"}
    assert prohibited_keys.isdisjoint(evidence)
