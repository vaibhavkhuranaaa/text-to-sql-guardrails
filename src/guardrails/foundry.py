"""Small Azure Foundry contract adapter.

The adapter intentionally has no default model or credentials.  It sends only the
curated catalog and policy, never a source file, identifier field, or prior result.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from azure.identity import DefaultAzureCredential

from .db import semantic_catalog
from .observability import proposal_telemetry


class FoundryUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class GeneratedProposal:
    sql: str
    assumptions: list[str]
    model: str
    token_cost_usd: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


def _instructions() -> str:
    return (
        "You propose one DuckDB read-only analytical SQL statement. Return JSON with "
        "sql and assumptions. Use only this curated catalog: "
        + json.dumps(semantic_catalog(), sort_keys=True)
        + ". Identifier fields are unavailable. Do not use files, network functions, "
        "writes, extensions, or unlisted fields. Preserve analytical semantics: never "
        "silently discard, zero-fill, or coalesce NULL balance values unless the question "
        "asks for that behavior; state the chosen NULL treatment in assumptions. Every "
        "ranking/window function must have an explicit ORDER BY. For unspecified ties use "
        "RANK and state that ties share a rank; use DENSE_RANK only when no rank gaps are "
        "requested and ROW_NUMBER only when unique sequential positions are requested."
    )


def _access_token() -> str:
    """Use Azure CLI locally and managed identity when the app is deployed."""
    return DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token


def generate(question: str) -> GeneratedProposal:
    endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT")
    deployment = os.environ.get("AZURE_FOUNDRY_DEPLOYMENT")
    if not endpoint or not deployment:
        raise FoundryUnavailable(
            "Azure Foundry is not configured. Set the owner-approved endpoint and deployment outside Git."
        )
    url = endpoint.rstrip("/") + "/openai/v1/chat/completions"
    body = json.dumps(
        {
            "model": deployment,
            "messages": [
                {"role": "system", "content": _instructions()},
                {"role": "user", "content": question},
            ],
            "response_format": {"type": "json_object"},
            "max_completion_tokens": 2048,
        }
    ).encode()
    started = proposal_telemetry.model_call_started()
    try:
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {_access_token()}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        proposal_telemetry.model_call_finished(started, succeeded=False)
        raise FoundryUnavailable(
            f"Azure Foundry generation was unavailable (HTTP {exc.code}); no SQL was executed."
        ) from exc
    except (OSError, json.JSONDecodeError) as exc:
        proposal_telemetry.model_call_finished(started, succeeded=False)
        raise FoundryUnavailable(
            "Azure Foundry generation was unavailable; no SQL was executed."
        ) from exc
    try:
        content = json.loads(payload["choices"][0]["message"]["content"])
        sql = str(content["sql"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        proposal_telemetry.model_call_finished(started, succeeded=False)
        raise FoundryUnavailable("Azure Foundry returned an invalid proposal contract.") from exc
    assumptions = content.get("assumptions", [])
    if not isinstance(assumptions, list) or not all(isinstance(item, str) for item in assumptions):
        assumptions = []
    usage = payload.get("usage", {})
    input_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
    output_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
    if not isinstance(input_tokens, int) or input_tokens < 0:
        input_tokens = None
    if not isinstance(output_tokens, int) or output_tokens < 0:
        output_tokens = None
    proposal_telemetry.model_call_finished(
        started,
        succeeded=True,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    return GeneratedProposal(
        sql=sql,
        assumptions=assumptions,
        model=deployment,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
