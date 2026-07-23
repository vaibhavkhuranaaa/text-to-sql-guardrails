"""Write status-only verification evidence for the temporary anonymous demo."""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


def fetch_json(url: str) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "text-to-sql-release-check/1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.status, json.load(response)


def fetch_status(url: str) -> int:
    request = urllib.request.Request(url, headers={"User-Agent": "text-to-sql-release-check/1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        response.read(1)
        return response.status


parser = argparse.ArgumentParser()
parser.add_argument("--base-url", required=True)
parser.add_argument("--revision", required=True)
parser.add_argument("--image", required=True)
parser.add_argument("--digest", required=True)
parser.add_argument("--expires-at", required=True)
parser.add_argument("--owner", required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()

base_url = args.base_url.rstrip("/")
checks = []
for label, path in [
    ("root", "/"),
    ("evaluation", "/v1/evaluation"),
    ("examples", "/v2/examples"),
    ("safe_preview", "/v2/data-preview?limit=1"),
]:
    status = fetch_status(f"{base_url}{path}")
    checks.append({"id": label, "path": path, "httpStatus": status, "result": "pass"})

status_code, status_payload = fetch_json(f"{base_url}/v1/status")
snapshot = status_payload["snapshot"]
if snapshot.get("state") != "demo_fixture":
    raise SystemExit("public deployment is not using the disclosed demo fixture")
checks.append(
    {
        "id": "fixture_boundary",
        "path": "/v1/status",
        "httpStatus": status_code,
        "result": "pass",
        "observed": {
            "state": snapshot.get("state"),
            "fixtureSha256": snapshot.get("sha256"),
        },
    }
)

record = {
    "schemaVersion": 1,
    "kind": "temporary-anonymous-demo",
    "productionClaim": False,
    "exposure": "anonymous",
    "baseUrl": base_url,
    "revision": args.revision,
    "image": args.image,
    "imageDigest": args.digest,
    "verifiedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    "expiresAt": args.expires_at,
    "expiryOwner": args.owner,
    "checks": checks,
    "limitations": [
        "No caller identity or authorization boundary.",
        "The deployed revision predates source-level rate and process-budget controls.",
        "No production availability, alerting, or SLO evidence.",
        "Proposal state is single-replica SQLite under /tmp and is lost on restart.",
    ],
}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(f"{json.dumps(record, indent=2)}\n", encoding="utf-8")
print(json.dumps({"result": "pass", "checks": len(checks), "out": str(args.out)}))
