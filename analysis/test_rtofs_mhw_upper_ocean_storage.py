import hashlib
import json
import pathlib
import xml.etree.ElementTree as ET

from analyze_rtofs_mhw_upper_ocean_storage import run


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas/data/rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json"


def test_upper_ocean_source_is_complete_and_pinned():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert payload["window"]["day_count"] == len(payload["rows"]) == 6
    assert payload["grid"]["shape"] == [67, 63]
    assert payload["grid"]["valid_box_cells"] == 4221
    assert payload["vertical_support"]["standard_depths_m"] == [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
    encoded = json.dumps(payload["rows"], separators=(",", ":")).encode()
    assert hashlib.sha256(encoded).hexdigest() == payload["extracted_rows_sha256"] == "1dfb4e8f63ad31f866aee465c764310cade010aeab316c4849acdd873064a05f"
    assert all(row["potential_temperature_c_milli_by_depth"] and len(row["potential_temperature_c_milli_by_depth"]) == 15 for row in payload["rows"])
    assert all(len(row["eastward_velocity_m_s_e4_by_depth"]) == 15 and len(row["northward_velocity_m_s_e4_by_depth"]) == 15 for row in payload["rows"])
    assert all(file["three_dimensional"]["etag"] for file in payload["files"])


def test_bridge_has_surface_intensification_and_column_heat_gain():
    result = run()
    bridge = result["bridge_evaluation"]
    assert bridge["result"] == "surface intensification accompanies genuine fixed-column heat gain"
    assert bridge["box_surface_temperature_change_c"] == 0.5396
    assert bridge["box_zero_to_50_m_column_mean_temperature_change_c"] == 0.0997
    assert bridge["surface_to_column_mean_change_ratio"] == 5.412
    assert bridge["box_zero_to_50_m_storage_tendency_w_m2"] == 236.03
    assert bridge["gfs_net_downward_surface_flux_w_m2"] == 112.61
    assert bridge["gfs_surface_flux_fraction_of_rtofs_storage_scale"] == 0.477
    assert bridge["anchor_zero_to_50_m_storage_tendency_w_m2"] == 1739.02
    storage = [result["intervals"][-1]["fixed_columns"][f"zero_to_{depth}_m"]["storage_tendency_w_m2"]["latitude_weighted_mean"] for depth in (10, 20, 30, 50)]
    assert storage == [92.13, 113.25, 145.47, 236.03]


def test_committed_analysis_matches_and_svg_states_boundary():
    committed = json.loads((ROOT / "research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json").read_text(encoding="utf-8"))
    assert committed == run()
    svg = ROOT / "figures/osw-d13-rtofs-mhw-upper-ocean-storage-2026.svg"
    ET.parse(svg)
    text = svg.read_text(encoding="utf-8")
    for token in ("THE SURFACE INTENSIFIES", "UPPER OCEAN ALSO GAINS HEAT", "+236 W/m²", "48%", "NOT NATIVE-LAYER HEAT CONTENT", "OSW-D13"):
        assert token in text
