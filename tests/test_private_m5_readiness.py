import importlib.util
import sys
from pathlib import Path


def test_percentile_uses_observed_values():
    path = Path(__file__).parents[1] / "scripts" / "run_private_m5_readiness.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("run_private_m5_readiness", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module._percentile([1.0, 2.0, 3.0], 0.95) == 3.0


def test_lifecycle_report_exercises_ephemeral_approval_controls(tmp_path):
    path = Path(__file__).parents[1] / "scripts" / "run_private_m5_readiness.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("run_private_m5_readiness", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module._lifecycle_report(tmp_path / "proposals.sqlite3") == {
        "safe_proposals": 3,
        "policy_refusals": 1,
        "approved_executions": 1,
        "expired_approvals": 1,
        "duplicate_execution_attempts": 2,
        "duplicate_execution_count": 0,
        "duplicate_attempt_outcomes": {"refused": 1, "trusted": 1},
    }
