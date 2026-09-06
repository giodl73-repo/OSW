import hashlib
import json
import pathlib
import xml.etree.ElementTree as ET

import numpy as np

from analyze_gfs_mhw_surface_flux import run
from fetch_gfs_mhw_surface_flux import averaged_surface_entry, parse_index, subset


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas/data/gfs-mhw-surface-flux-north-atlantic-20260807-20260812.json"


def test_compact_gfs_source_is_complete_and_pinned():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert payload["window"]["interval_count"] == len(payload["rows"]) == 5
    assert payload["grid"]["shape"] == [34, 42]
    encoded = json.dumps(payload["rows"], separators=(",", ":")).encode()
    assert hashlib.sha256(encoded).hexdigest() == payload["extracted_rows_sha256"] == "ede79dcc95b74ae920c4ed32e140419a8401ebf03a497041eed40ceb7be8e189"
    assert len(payload["files"]) == 5
    assert all(len(day["forecast_files"]) == 4 for day in payload["files"])
    messages = [message for day in payload["files"] for file in day["forecast_files"] for message in file["messages"]]
    assert len(messages) == 120
    assert all(file["etag"] for day in payload["files"] for file in day["forecast_files"])
    assert all(message["message_sha256"] and message["metadata"]["grid_type"] == "regular_gg" for message in messages)
    assert all(message["metadata"]["type_of_statistical_processing"] == 0 for message in messages)


def test_index_selection_and_rectangular_subset_contract():
    text = "1:0:d=2026081100:LHTFL:surface:0-6 hour ave fcst:\n2:120:d=2026081100:LHTFL:surface:6 hour fcst:\n"
    entries = parse_index(text, 250)
    assert entries[0]["offset"] == 0 and entries[0]["end"] == 119
    assert entries[1]["offset"] == 120 and entries[1]["end"] == 249
    assert averaged_surface_entry(entries, "LHTFL", 6) == entries[0]
    latitude = np.repeat(np.array([[39.0], [40.0], [41.0], [42.0], [43.0], [44.0]]), 8, axis=1)
    longitude = np.repeat(np.arange(-53.0, -45.0)[None, :], 6, axis=0)
    local_latitude, local_longitude, local_values = subset(latitude, longitude, latitude + longitude)
    assert local_latitude.shape == local_longitude.shape == local_values.shape == (4, 6)


def test_bridge_surface_gain_is_material_but_depth_sensitive():
    result = run()
    bridge = result["bridge_evaluation"]
    assert bridge["gfs_box_net_downward_surface_flux_w_m2"] == 112.61
    assert bridge["anchor_net_downward_surface_flux_w_m2"] == 87.08
    assert bridge["rtofs_grid_flux_equivalent_start_depth_c_per_day"] == 0.2876
    assert bridge["rtofs_grid_flux_equivalent_endpoint_mean_depth_c_per_day"] == 0.3381
    start = bridge["depth_floor_sensitivity"]["start_depth"]
    assert start["minimum_5_m_depth_c_per_day"] == 0.18
    assert start["box_mean_flux_over_box_mean_depth_c_per_day"] == 0.1219
    assert start["cell_fraction_below_2_m"] == 0.041
    assert bridge["fraction_of_rtofs_pre_flux_remainder_start_depth"] == 0.613
    net_fluxes = [interval["gfs_net_downward_surface_flux_w_m2"]["latitude_weighted_mean"] for interval in result["intervals"]]
    assert [value > 0 for value in net_fluxes] == [False, False, False, True, True]


def test_committed_analysis_matches_and_svg_states_cross_system_boundary():
    committed = json.loads((ROOT / "research/osw-d12-gfs-surface-flux-screen-2026.json").read_text(encoding="utf-8"))
    assert committed == run()
    svg = ROOT / "figures/osw-d12-gfs-surface-flux-screen-2026.svg"
    ET.parse(svg)
    text = svg.read_text(encoding="utf-8")
    for token in ("SURFACE FLUX TURNS POSITIVE", "+113 W/m²", "5 m floor", "CROSS-SYSTEM ENERGY-SCALE TEST", "NOT REANALYSIS", "OSW-D12"):
        assert token in text
