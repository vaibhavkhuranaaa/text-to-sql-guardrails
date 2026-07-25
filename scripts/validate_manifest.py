"""Validate the repository manifest against the shared v2 lifecycle contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def require(value: dict, fields: list[str], label: str) -> None:
    missing = [field for field in fields if value.get(field) in (None, "", [])]
    if missing:
        raise AssertionError(f"{label} requires: {', '.join(missing)}")


def http_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--profile",
    choices=["draft", "first-demo", "publication", "live"],
    default="first-demo",
)
args = parser.parse_args()

manifest = json.loads(Path("portfolio/project.json").read_text(encoding="utf-8"))
source_manifest = json.loads(Path("data/source_manifest.json").read_text(encoding="utf-8"))
assert manifest["version"] == 2
assert manifest["slug"] == "text-to-sql-guardrails"
assert manifest["githubUrl"] is None or http_url(manifest["githubUrl"])
assert manifest["liveUrl"] is None or http_url(manifest["liveUrl"])
deployment = manifest["deployment"]
assert deployment["status"] in {"local", "temporary-demo", "release-pending", "live"}
assert deployment["exposure"] in {"private", "authenticated", "anonymous"}
assert isinstance(deployment["productionClaim"], bool)

if args.profile != "draft":
    require(
        manifest,
        [
            "title",
            "summary",
            "outcome",
            "industries",
            "categories",
            "stack",
            "metrics",
            "stages",
            "architecture",
            "evaluation",
            "operationalTradeoffs",
            "disclaimer",
            "dataDisclosure",
            "evidence",
            "story",
        ],
        args.profile,
    )
    require(
        manifest["dataDisclosure"],
        [
            "source",
            "license",
            "classification",
            "permittedUse",
            "includedFields",
            "excludedFields",
            "deployedArtifactContents",
        ],
        "dataDisclosure",
    )
    require(
        manifest["story"],
        [
            "recruiterSummary",
            "technicalNarrative",
            "scalabilityRoadmap",
            "executiveSummary",
            "intendedUser",
            "example",
            "technologyDecisions",
            "evidence",
            "limitations",
        ],
        "story",
    )
    evidence_ids = {item["id"] for item in manifest["evidence"]}
    assert len(evidence_ids) == len(manifest["evidence"]), "evidence IDs must be unique"
    references = [
        *deployment.get("evidenceRefs", []),
        *[
            reference
            for item in manifest["story"]["evidence"]
            for reference in item.get("evidenceRefs", [])
        ],
        *[
            reference
            for item in manifest.get("resume", {}).get("bulletCandidates", [])
            for reference in item.get("evidenceRefs", [])
        ],
    ]
    assert set(references) <= evidence_ids, "every evidence reference must resolve"
    for item in manifest["evidence"]:
        assert Path(item["source"].split(" and ")[0]).exists(), (
            f"missing evidence source: {item['source']}"
        )
if args.profile in {"publication", "live"}:
    assert http_url(manifest["githubUrl"]), "publication requires githubUrl"
    require(manifest.get("resume", {}), ["bulletCandidates"], "publication resume")

if args.profile == "live":
    assert deployment["status"] == "live"
    assert http_url(manifest["liveUrl"])
    require(deployment, ["verifiedAt", "evidenceRefs"], "live deployment")

assert source_manifest["doi"] == "10.17632/zhj366m53p.2"
assert source_manifest["version"] == 2
assert source_manifest["license"] == "CC BY 4.0"
assert source_manifest["files"], "source manifest must name the approved source files"
print(f"Manifest v2 {args.profile} profile passed.")
