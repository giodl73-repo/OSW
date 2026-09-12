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
    assert coverage["interior_convergence"]["status"] == "partial_open_account_not_supported_for_convergence"
    assert coverage["transformation"]["status"] == "density_strata_supported_transformation_not_supported"
    assert coverage["vertical_transfer"]["status"] == "not_supported"
    assert "Vertical velocity" in coverage["vertical_transfer"]["required_evidence"]


def test_synthesis_keeps_source_families_separate_and_has_seasonal_results():
    payload = MODULE.build()
    assert payload["source_families"]["current_geometry_dynamics"]["status"] == "separate_unjoined_source_family"
    assert len(payload["bounded_results"]["seasonal_relative_motion"]) == 4
    assert len(payload["bounded_results"]["central_seed_vertical_interfaces"]) == 4
    assert payload["bounded_results"]["partial_perimeter_geometry"]["missing_subset_edge_sides"]["total_missing_subset_edge_sides"] == 176
    assert payload["bounded_results"]["surface_storage_month_count"] == 12


def test_browser_derivative_matches_synthesis():
    source = (ROOT / "exchange/interior-dynamics.js").read_text(encoding="utf-8")
    prefix = "window.OSW_INTRA_STATE_DYNAMICS = "
    assert source.startswith(prefix) and source.endswith(";\n")
    assert json.loads(source[len(prefix):-2]) == MODULE.build()
