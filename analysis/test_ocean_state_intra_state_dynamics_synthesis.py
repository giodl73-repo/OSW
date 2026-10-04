import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_ocean_state_intra_state_dynamics_synthesis.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_intra_state_dynamics_synthesis", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_synthesis_regenerates_and_covers_all_relations():
    committed = json.loads((ROOT / "research/ocean-state-intra-state-dynamics-synthesis-sant-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert committed["status"] == "coverage_complete_for_current_custodied_evidence_not_complete_physical_dynamics"
    coverage = {item["relation"]: item for item in committed["relation_coverage"]}
    assert coverage["lateral_interior_pathway"]["status"] == "supported_bounded_kinematic_screen"
    assert coverage["partial_lateral_perimeter"]["status"] == "supported_partial_perimeter_screen"
    assert coverage["interior_convergence"]["status"] == "horizontal_advective_term_and_inventory_endpoints_supported_total_convergence_not_supported"
    assert coverage["transformation"]["status"] == "density_strata_inventory_and_horizontal_boundary_terms_supported_transformation_not_supported"
    assert coverage["vertical_transfer"]["status"] == "not_supported"
    assert "Vertical velocity" in coverage["vertical_transfer"]["required_evidence"]


def test_synthesis_keeps_source_families_separate_and_has_seasonal_results():
    payload = MODULE.build()
    assert payload["source_families"]["current_geometry_dynamics"]["status"] == "separate_unjoined_source_family"
    assert len(payload["bounded_results"]["seasonal_relative_motion"]) == 4
    assert len(payload["bounded_results"]["central_seed_vertical_interfaces"]) == 4
    assert payload["bounded_results"]["partial_perimeter_geometry"]["missing_subset_edge_sides"]["total_missing_subset_edge_sides"] == 176
    assert payload["bounded_results"]["surface_storage_month_count"] == 12
    assert len(payload["bounded_results"]["closed_box_horizontal_advective_terms"]) == 4
    assert len(payload["bounded_results"]["closed_box_primary_inventory_endpoints"]["successive_endpoint_differences"]) == 3
    assert len(payload["bounded_results"]["closed_box_primary_density_inventory"]["successive_endpoint_stratum_volume_differences"]) == 3
    assert len(payload["bounded_results"]["closed_box_primary_density_boundary_terms"]) == 4
    assert len(payload["bounded_results"]["closed_box_primary_density_collocation_sensitivity"]) == 4
    assert payload["source_families"]["current_geometry_dynamics"]["density_boundary_collocation_sensitivity"]["sha256"]
    assert payload["source_families"]["temporal_support_audit"]["sha256"]
    assert payload["source_families"]["current_geometry_dynamics"]["annual_density_boundary_series"]["sha256"]
    assert payload["source_families"]["current_geometry_dynamics"]["annual_density_inventory_series"]["sha256"]
    assert payload["source_families"]["current_geometry_dynamics"]["density_cutoff_sensitivity"]["sha256"]
    assert payload["source_families"]["current_geometry_dynamics"]["july_repeat_sign_screen"]["sha256"]
    assert payload["source_families"]["current_geometry_dynamics"]["july_ensemble_sign_screen"]["sha256"]
    annual = payload["bounded_results"]["annual_density_boundary_comparison"]
    assert len(annual) == 12
    assert all(len(month["strata"]) == 4 and all(len(item["control_centered_net_outward_Sv"]) == 3 for item in month["strata"]) for month in annual)
    july = annual[6]["strata"][2]
    assert july["primary_centered_net_outward_Sv"] > 1.5 and july["primary_upstream_net_outward_Sv"] > 1.0
    assert 0.15 < july["primary_inventory_volume_fraction"] < 0.17
    cutoff = payload["bounded_results"]["density_cutoff_sensitivity_summary"]
    assert cutoff["posthoc_challenge"] is True
    assert cutoff["july_middle_high_all_boxes_methods_shifts_outward"] is True
    assert cutoff["raised_cutoff_lighter_bin_present_july_october"] is True
    repeat = payload["bounded_results"]["july_repeat_sign_summary"]
    assert repeat["decision"] == "repeat_year_sign_screen_fails"
    assert [year["predeclared_sign_pass"] for year in repeat["years"]] == [True, False, True]
    assert repeat["years"][1]["minimum_tested_case"]["box"] == "east_control"
    ensemble = payload["bounded_results"]["july_ensemble_sign_summary"]
    assert ensemble["decision"] == {"pass_count": 0, "member_count": 5, "east_control_baseline_upstream_sign_varies": True}
    assert [member["predeclared_sign_pass"] for member in ensemble["members"]] == [False] * 5


def test_browser_derivative_matches_synthesis():
    source = (ROOT / "exchange/interior-dynamics.js").read_text(encoding="utf-8")
    prefix = "window.OSW_INTRA_STATE_DYNAMICS = "
    assert source.startswith(prefix) and source.endswith(";\n")
    assert json.loads(source[len(prefix):-2]) == MODULE.build()
