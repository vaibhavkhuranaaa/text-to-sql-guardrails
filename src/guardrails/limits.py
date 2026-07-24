"""Bound anonymous demo usage without retaining client identifiers or questions."""

from __future__ import annotations

import hashlib
import os
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime

from .observability import event


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    status_code: int
    reason: str | None = None


class ProposalGate:
    """Per-process guardrail for a temporary, single-replica anonymous demo."""

    def __init__(
        self,
        *,
        proposals_per_minute: int | None = None,
        max_proposals_per_process: int | None = None,
        expires_at: str | None = None,
    ) -> None:
        self.proposals_per_minute = proposals_per_minute or int(
            os.getenv("GUARDRAILS_PROPOSALS_PER_MINUTE", "20")
        )
        self.max_proposals_per_process = max_proposals_per_process or int(
            os.getenv("GUARDRAILS_MAX_PROPOSALS_PER_PROCESS", "100")
        )
        self.expires_at = (
            expires_at if expires_at is not None else os.getenv("GUARDRAILS_DEMO_EXPIRES_AT")
        )
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._accepted = 0
        self._rate_limited = 0
        self._budget_refused = 0
        self._lock = threading.Lock()

    @staticmethod
    def _client_key(client: str | None) -> str:
        return hashlib.sha256((client or "unknown").encode()).hexdigest()[:16]

    def _expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now(UTC) >= datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))

    def check(self, client: str | None) -> GateDecision:
        client_key = self._client_key(client)
        with self._lock:
            if self._expired():
                event("demo_expired", client_key=client_key)
                return GateDecision(False, 410, "The temporary demo has expired.")
            if self._accepted >= self.max_proposals_per_process:
                self._budget_refused += 1
                event(
                    "proposal_budget_refused",
                    client_key=client_key,
                    accepted=self._accepted,
                    process_budget=self.max_proposals_per_process,
                )
                return GateDecision(False, 429, "The temporary demo proposal budget is exhausted.")

            now = time.monotonic()
            requests = self._requests[client_key]
            while requests and requests[0] <= now - 60:
                requests.popleft()
            if len(requests) >= self.proposals_per_minute:
                self._rate_limited += 1
                event("proposal_rate_limited", client_key=client_key, window_seconds=60)
                return GateDecision(False, 429, "Too many proposals; retry after one minute.")

            requests.append(now)
            self._accepted += 1
            event("proposal_budget_accepted", client_key=client_key, accepted=self._accepted)
            return GateDecision(True, 200)

    def status(self) -> dict:
        with self._lock:
            return {
                "scope": "single process; temporary demo only",
                "proposals_per_minute": self.proposals_per_minute,
                "max_proposals_per_process": self.max_proposals_per_process,
                "accepted_since_start": self._accepted,
                "rate_limited_since_start": self._rate_limited,
                "budget_refused_since_start": self._budget_refused,
                "expires_at": self.expires_at,
                "expired": self._expired(),
            }
