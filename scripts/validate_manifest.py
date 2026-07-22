import json
from pathlib import Path

manifest = json.loads(Path("portfolio/project.json").read_text())
required = {
    "version",
    "slug",
    "title",
    "summary",
    "outcome",
    "deployment",
    "metrics",
    "disclaimer",
    "story",
}
missing = required - set(manifest)
assert not missing, f"missing manifest keys: {sorted(missing)}"
assert manifest["version"] == 2
for asset in manifest["assets"]:
    assert Path(asset).exists(), f"missing asset: {asset}"
