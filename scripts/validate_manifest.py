import json
from pathlib import Path

manifest = json.loads(Path("portfolio/project.json").read_text())
source_manifest = json.loads(Path("data/source_manifest.json").read_text())
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
assert source_manifest["doi"] == "10.17632/zhj366m53p.2"
assert source_manifest["version"] == 2
assert source_manifest["license"] == "CC BY 4.0"
assert source_manifest["files"], "source manifest must name the approved source files"
