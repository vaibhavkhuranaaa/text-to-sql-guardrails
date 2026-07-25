"""Privacy-preserving structured observability for the local prototype."""

import hashlib
import json
import logging
import os
import threading
import time
from collections import Counter

logger = logging.getLogger("guardrails")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def lifecycle_sample_rate() -> float:
    """Return the bounded rate for status-only lifecycle log samples."""
    try:
        return min(1.0, max(0.0, float(os.getenv("GUARDRAILS_TELEMETRY_SAMPLE_RATE", "0.1"))))
    except ValueError:
        return 0.1


class ProposalTelemetry:
    """Process-local, aggregate-only evidence for the anonymous proposal path."""

    _LATENCY_BUCKETS = (100, 500, 1_000, 5_000)

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._model_calls_attempted = 0
        self._model_calls_succeeded = 0
        self._model_calls_failed = 0
        self._reported_input_tokens = 0
        self._reported_output_tokens = 0
        self._usage_reported_calls = 0
        self._proposal_outcomes: Counter[str] = Counter()
        self._model_latency_buckets: Counter[str] = Counter()
        self._proposal_latency_buckets: Counter[str] = Counter()

    @classmethod
    def _bucket(cls, latency_ms: float) -> str:
        for upper_bound in cls._LATENCY_BUCKETS:
            if latency_ms <= upper_bound:
                return f"lte_{upper_bound}_ms"
        return "gt_5000_ms"

    def model_call_started(self) -> float:
        with self._lock:
            self._model_calls_attempted += 1
        return time.perf_counter()

    def model_call_finished(
        self,
        started: float,
        *,
        succeeded: bool,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        latency_ms = (time.perf_counter() - started) * 1_000
        with self._lock:
            if succeeded:
                self._model_calls_succeeded += 1
                if input_tokens is not None or output_tokens is not None:
                    self._usage_reported_calls += 1
                    self._reported_input_tokens += input_tokens or 0
                    self._reported_output_tokens += output_tokens or 0
            else:
                self._model_calls_failed += 1
            self._model_latency_buckets[self._bucket(latency_ms)] += 1

    def proposal_finished(self, outcome: str, started: float) -> None:
        latency_ms = (time.perf_counter() - started) * 1_000
        with self._lock:
            self._proposal_outcomes[outcome] += 1
            self._proposal_latency_buckets[self._bucket(latency_ms)] += 1

    def status(self) -> dict[str, object]:
        with self._lock:
            return {
                "scope": "single process; aggregate-only; reset on restart or scale-to-zero",
                "model_calls": {
                    "attempted_since_start": self._model_calls_attempted,
                    "succeeded_since_start": self._model_calls_succeeded,
                    "failed_since_start": self._model_calls_failed,
                    "usage_reported_calls_since_start": self._usage_reported_calls,
                    "reported_input_tokens_since_start": self._reported_input_tokens,
                    "reported_output_tokens_since_start": self._reported_output_tokens,
                    "latency_buckets_ms": dict(self._model_latency_buckets),
                },
                "proposal_outcomes_since_start": dict(self._proposal_outcomes),
                "proposal_latency_buckets_ms": dict(self._proposal_latency_buckets),
                "lifecycle_log_sample_rate": lifecycle_sample_rate(),
                "retention": "No raw questions, SQL, result rows, client identifiers, tokens, or trace IDs are retained in this aggregate. Lifecycle logs are status-only samples and have no configured exporter.",
            }


proposal_telemetry = ProposalTelemetry()


def event(name: str, **fields: object) -> None:
    """Emit a deterministic, status-only lifecycle sample without identifiers."""
    sample_key = str(fields.get("trace_id", name)).encode()
    sample = int.from_bytes(hashlib.sha256(sample_key).digest()[:8], "big") / 2**64
    if sample >= lifecycle_sample_rate():
        return
    allowed_fields = {
        "accepted",
        "cost_usd",
        "generated",
        "latency_ms",
        "process_budget",
        "reason",
        "status",
        "valid",
        "window_seconds",
    }
    logger.info(
        json.dumps(
            {"event": name, **{key: fields[key] for key in allowed_fields & fields.keys()}},
            default=str,
            sort_keys=True,
        )
    )
