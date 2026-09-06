import json
import pathlib
import xml.etree.ElementTree as ET

from analyze_rtofs_mhw_upper_ocean_advection import run


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_depth_integrated_motion_changes_surface_only_story():
    result = run()
    bridge = result["bridge_evaluation"]
    assert bridge["rtofs_fixed_0_50_m_storage_tendency_w_m2"] == 236.03
    assert bridge["rtofs_offline_0_50_m_horizontal_advection_w_m2"] == 171.21
    assert bridge["gfs_net_downward_surface_flux_w_m2"] == 112.61
    assert bridge["cross_system_partial_residual_w_m2"] == -47.79
    assert bridge["horizontal_advection_fraction_of_storage"] == 0.725
    assert bridge["surface_plus_horizontal_fraction_of_storage"] == 1.202
    assert bridge["gradient_stencil_difference_w_m2"] == 1.07
    assert bridge["anchor_cross_system_partial_residual_w_m2"] == 936.28
    assert bridge["anchor_partial_residual_fraction_of_storage"] == 0.538
    depth_terms = result["intervals"][-1]["depth_integrated_horizontal_advection"]
    assert [depth_terms[f"zero_to_{limit}_m"]["endpoint_mean_horizontal_advection_w_m2"]["latitude_weighted_mean"] for limit in (10, 20, 30, 50)] == [21.01, 58.48, 97.22, 171.21]


def test_committed_analysis_matches_and_svg_states_partial_boundary():
    committed = json.loads((ROOT / "research/osw-d14-rtofs-mhw-upper-ocean-advection-2026.json").read_text(encoding="utf-8"))
    assert committed == run()
    svg = ROOT / "figures/osw-d14-rtofs-mhw-upper-ocean-advection-2026.svg"
    ET.parse(svg)
    text = svg.read_text(encoding="utf-8")
    for token in ("MOTION WAS HIDING BELOW THE SURFACE", "72.5%", "+171 W/m²", "partial residual", "NOT NATIVE TRACER FLUX", "OSW-D14"):
        assert token in text
