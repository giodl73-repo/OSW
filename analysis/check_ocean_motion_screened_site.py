"""Check that the portable atlas includes only screened data and linked assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from build_ocean_motion_screened_site import ASSETS, DATA, MAP_GROUND, OUTPUT, ROOT
from check_ocean_motion_safe_preview import check as check_screened_data


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check() -> None:
    check_screened_data()
    manifest = json.loads((OUTPUT / "site-manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "standalone_rights_screened_review_site_not_published"
    assert manifest["data_manifest_sha256"] == digest(DATA / "manifest.json")
    actual = {path.relative_to(OUTPUT).as_posix() for path in OUTPUT.rglob("*") if path.is_file()}
    expected = {row["path"] for row in manifest["files"]} | {"site-manifest.json"}
    assert actual == expected
    for row in manifest["files"]:
        path = OUTPUT / row["path"]
        assert path.is_file() and digest(path) == row["sha256"]
        if row["path"].startswith("data/"):
            assert path.read_bytes() == (DATA / row["path"].removeprefix("data/")).read_bytes()
    for asset in ASSETS:
        content = (OUTPUT / asset).read_text(encoding="utf-8")
        assert "../research/" not in content and "release/v0.1.0/" not in content
        assert "../" not in content, "Portable UI must not fetch or link above its served root"
    assert (OUTPUT / MAP_GROUND.name).read_bytes() == MAP_GROUND.read_bytes()
    assert "Natural Earth 1:110m land, public domain" in MAP_GROUND.read_text(encoding="utf-8")
    assert not (OUTPUT / "research").exists() and not (OUTPUT / "release").exists()
    full_sources = json.loads((ROOT / "almanac" / "release" / "v0.1.0" /
                               "sources.json").read_text(encoding="utf-8"))
    blocked_urls = [row["url"] for row in full_sources if row.get("kind") == "external" and
                    row.get("rights_status", "").startswith("pending") and row.get("url")]
    for path in OUTPUT.rglob("*"):
        if path.is_file() and path.suffix in {".json", ".js", ".html", ".md", ".csv", ".svg"}:
            content = path.read_text(encoding="utf-8")
            assert not any(url in content for url in blocked_urls), path
    data_report = json.loads((OUTPUT / "data" / "screening-report.json").read_text(encoding="utf-8"))
    assert data_report["counts"]["entities"] == 218
    assert data_report["counts"]["tiles"] == 70
    assert data_report["retained_claim_reviews"] == {"not_individually_reviewed": 8709}
    print(f"Screened site valid: {len(manifest['files'])} files, 218 objects, 70 NASA crops")


if __name__ == "__main__":
    check()
