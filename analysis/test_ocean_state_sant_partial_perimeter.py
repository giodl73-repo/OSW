import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_partial_perimeter.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_partial_perimeter", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_partial_perimeter_regenerates_and_keeps_missing_sides():
    committed = json.loads((ROOT / "research/ocean-state-sant-current-geometry-partial-perimeter-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert committed["status"] == "partial_in_domain_lateral_perimeter_screen_not_closed_volume_or_convergence"
    assert committed["geometry"]["in_domain_face_count"] == 474
    assert committed["geometry"]["missing_subset_edge_sides"]["total_missing_subset_edge_sides"] == 176


def test_each_season_has_depth_resolved_partial_flux_without_closure_claim():
    payload = MODULE.build()
    for month in payload["months"]:
        assert month["all_depths"]["wet_face_level_count"] == 26587
        assert len(month["by_depth"]) == 4
    assert "not convergence" in payload["boundary"]
