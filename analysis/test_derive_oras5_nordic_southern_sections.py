import json
import math
import pathlib

import derive_oras5_nordic_southern_sections as southern


ROOT = pathlib.Path(__file__).resolve().parents[1]


def assert_nested_close(actual, expected, path="root") -> None:
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            assert_nested_close(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for index, value in enumerate(expected):
            assert_nested_close(actual[index], value, f"{path}[{index}]")
    elif isinstance(expected, float):
        assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), path
    else:
        assert actual == expected, path


def test_three_sections_are_coastal_connected_and_disjoint() -> None:
    payload = southern.derive(ROOT / "atlas/data/oras5-nordic-seas-mesh.nc")
    assert [item["id"] for item in payload["sections"]] == ["denmark_strait", "iceland_faroe", "faroe_scotland"]
    assert payload["union_topology"]["unique_faces"]
    for section in payload["sections"]:
        assert section["start_node"]["modeled_coast"]
        assert section["stop_node"]["modeled_coast"]
        assert section["topology"]["connected_corner_chain"]
        assert section["topology"]["unique_faces"]
        assert section["face_count"] == section["u_face_count"] + section["v_face_count"]
        assert max(section["endpoint_offset_km"].values()) < 50.0


def test_committed_receipt_matches_derivation() -> None:
    expected = southern.derive(ROOT / "atlas/data/oras5-nordic-seas-mesh.nc")
    committed = json.loads((ROOT / "research/osw-m4-oras5-nordic-southern-sections.json").read_text(encoding="utf-8"))
    assert_nested_close(committed, expected)
