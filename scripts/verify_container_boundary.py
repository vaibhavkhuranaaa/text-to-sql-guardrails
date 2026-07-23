"""Fail unless a built container excludes raw and approved data artifacts."""

from pathlib import Path

for forbidden in [
    Path("/app/data/Raw"),
    Path("/app/data/raw"),
    Path("/app/data/approved"),
]:
    if forbidden.exists():
        raise SystemExit(f"forbidden container path exists: {forbidden}")

required = [
    Path("/app/data/fixtures/payments.json"),
    Path("/app/data/PROVENANCE.md"),
    Path("/app/data/source_manifest.json"),
    Path("/app/evaluation/report.json"),
]
missing = [str(path) for path in required if not path.is_file()]
if missing:
    raise SystemExit(f"required runtime evidence is missing: {', '.join(missing)}")

print("Container boundary verified: fixture/evaluation present; raw and approved artifacts absent.")
