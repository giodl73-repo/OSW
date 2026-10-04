"""Build a standalone review atlas from only the rights-screened export."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "almanac" / "screened-atlas"
DATA = ROOT / "almanac" / "release" / "v0.1.0-rights-screened-preview"
OUTPUT = ROOT / "site-review" / "ocean-motion-screened"
ASSETS = ("index.html", "app.js", "styles.css", "footprint-view.js")
MAP_GROUND = ROOT / "figures" / "osw-province-atlas-interactive.svg"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    screened_manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    assert screened_manifest["status"] == "rights_screened_preview_not_published"
    report = json.loads((DATA / "screening-report.json").read_text(encoding="utf-8"))
    assert report["counts"]["entities"] == 218 and report["counts"]["tiles"] == 70
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data_output = OUTPUT / "data"
    data_output.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in ASSETS:
        source = SOURCE / name
        target = OUTPUT / name
        shutil.copyfile(source, target)
        copied.append(target)
    map_target = OUTPUT / MAP_GROUND.name
    shutil.copyfile(MAP_GROUND, map_target)
    copied.append(map_target)
    for source in DATA.rglob("*"):
        if not source.is_file():
            continue
        target = data_output / source.relative_to(DATA)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(target)
    assert all(path.resolve().is_relative_to(OUTPUT.resolve()) for path in copied)
    assert not (OUTPUT / "research").exists() and not (OUTPUT / "release" / "v0.1.0").exists()
    manifest = {
        "status": "standalone_rights_screened_review_site_not_published",
        "scope": "Only the screened export, four OSW-authored interface files, and the OSW state-map ground are copied.",
        "data_manifest_sha256": digest(DATA / "manifest.json"),
        "files": [{"path": path.relative_to(OUTPUT).as_posix(), "sha256": digest(path)}
                  for path in sorted(copied)],
    }
    (OUTPUT / "site-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"Built screened review site: {len(copied)} files, {report['counts']['entities']} objects")


if __name__ == "__main__":
    main()
