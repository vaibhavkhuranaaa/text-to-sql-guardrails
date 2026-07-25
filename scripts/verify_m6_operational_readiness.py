"""Verify the local, status-only portion of the M6 operational contract."""

from __future__ import annotations

from fastapi.testclient import TestClient

from guardrails.api import app


def run() -> dict:
    client = TestClient(app)
    status = client.get("/v1/status")
    evaluation = client.get("/v1/evaluation")
    if status.status_code != 200 or evaluation.status_code != 200:
        raise RuntimeError("Status-only operational endpoints must be available.")
    payload = status.json()
    if {"anonymous_demo_controls", "proposal_telemetry"} - payload.keys():
        raise RuntimeError("Status endpoint is missing required aggregate controls.")
    if payload["proposal_telemetry"]["scope"].startswith("single process") is False:
        raise RuntimeError("Telemetry scope must disclose its process-local limitation.")
    return {
        "status_endpoint": "passed",
        "evaluation_endpoint": "passed",
        "telemetry_scope": "process_local_aggregate_only",
        "durable_restore_drill": "not_applicable_under_m0_a",
    }


if __name__ == "__main__":
    print(run())
