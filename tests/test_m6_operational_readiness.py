import importlib.util
import sys
from pathlib import Path


def test_m6_operational_readiness_is_status_only_and_discloses_m0_a_limit():
    path = Path(__file__).parents[1] / "scripts" / "verify_m6_operational_readiness.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("verify_m6_operational_readiness", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.run() == {
        "status_endpoint": "passed",
        "evaluation_endpoint": "passed",
        "telemetry_scope": "process_local_aggregate_only",
        "durable_restore_drill": "not_applicable_under_m0_a",
    }
