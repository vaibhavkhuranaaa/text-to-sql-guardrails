"""Privacy-preserving structured observability for the local prototype."""

import json
import logging

logger = logging.getLogger("guardrails")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def event(name: str, **fields: object) -> None:
    """Log lifecycle metadata only; raw analyst questions are never included."""
    logger.info(json.dumps({"event": name, **fields}, default=str, sort_keys=True))
