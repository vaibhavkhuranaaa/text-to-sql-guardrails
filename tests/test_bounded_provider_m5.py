import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


def test_bounded_provider_report_retains_aggregate_values_only(monkeypatch):
    path = Path(__file__).parents[1] / "scripts" / "run_bounded_provider_m5.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("run_bounded_provider_m5", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    from guardrails.foundry import GeneratedProposal

    monkeypatch.setattr(
        module,
        "generate",
        lambda _prompt: GeneratedProposal(
            sql="SELECT channel, COUNT(*) AS payment_count FROM fact_payments GROUP BY channel",
            assumptions=[],
            model="recorded-contract-test",
            input_tokens=10,
            output_tokens=20,
        ),
    )
    monkeypatch.setattr(module, "validate_sql", lambda _sql: SimpleNamespace(valid=True))

    report = module.run()

    assert report["evaluation_version"] == "m5-bounded-provider-1"
    assert report["attempted"] == 4
    assert report["valid"] == 4
    assert report["refused"] == 0
    assert report["input_tokens"] == 40
    assert report["output_tokens"] == 80
    assert "tokens by request" in report["disclosure"]
