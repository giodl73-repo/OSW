import json
import pathlib

import derive_oras5_nordic_control_volume as control


ROOT = pathlib.Path(__file__).resolve().parents[1]


def derive_repository_volume():
    return control.derive(
        ROOT / "atlas/data/oras5-nordic-seas-mesh.nc",
        ROOT / "research/osw-m4-oras5-nordic-southern-sections.json",
        ROOT / "research/osw-m4-oras5-nordic-barents-section.json",
        ROOT / "research/osw-m3-oras5-arctic-gate-readiness.json",
    )


def test_five_sections_close_one_interior_component() -> None:
    payload = derive_repository_volume()
    assert payload["status"] == "closed_surface_control_volume"
    assert payload["topology"]["section_count"] == 5
    assert payload["topology"]["unique_boundary_faces"]
    assert not payload["topology"]["inside_reaches_mesh_edge"]
    assert payload["topology"]["every_boundary_face_separates_inside_from_outside"]
    assert payload["topology"]["inside_wet_t_cell_count"] > 10000
    assert payload["southern_candidate_selection"]["selected_representation"] == "three_land_bounded_southern_closures"
    assert not payload["southern_candidate_selection"]["three_named_path_closed_combination_found"]


def test_fram_remap_is_exact_and_land_bounded() -> None:
    payload = derive_repository_volume()
    fram = next(section for section in payload["sections"] if section["id"] == "fram_strait")
    assert fram["face_count"] == 60
    assert fram["unique_faces"]
    assert fram["land_bounded_at_surface"]
    assert fram["maximum_remap_offset_km"] < 0.001


def test_committed_receipt_matches_derivation() -> None:
    expected = derive_repository_volume()
    committed = json.loads((ROOT / "research/osw-m4-oras5-nordic-control-volume.json").read_text(encoding="utf-8"))
    assert committed == expected
