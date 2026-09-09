import json
import pathlib

import audit_oras5_nordic_section_geometry as audit


ROOT = pathlib.Path(__file__).resolve().parents[1]


def derive_repository_audit():
    return audit.run(
        ROOT / "atlas/data/oras5-nordic-seas-mesh.nc",
        ROOT / "research/osw-m4-oras5-nordic-control-volume.json",
    )


def test_all_five_sections_pass_full_depth_internal_geometry() -> None:
    payload = derive_repository_audit()
    assert payload["status"] == "five_sections_pass_internal_full_depth_geometry"
    assert payload["all_sections_pass"]
    assert [section["id"] for section in payload["sections"]] == [
        "denmark_strait",
        "iceland_scotland_ridge",
        "northern_north_sea",
        "fram_strait",
        "norway_svalbard",
    ]
    for section in payload["sections"]:
        assert section["horizontal_face_count"] > 0
        assert section["total_section_area_m2"] > 0
        assert section["checks"]["mask_mismatch_count"] == 0
        assert section["checks"]["depth_bins_reproduce_total"]


def test_committed_audit_matches_derivation() -> None:
    expected = derive_repository_audit()
    committed = json.loads((ROOT / "research/osw-m4-oras5-nordic-section-geometry-audit.json").read_text(encoding="utf-8"))
    assert committed == expected
