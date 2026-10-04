import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_closed_box_density_boundary.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_closed_box_density_boundary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_closed_box_density_boundary_regenerates_without_transformation_or_budget_claim():
    committed = json.loads((ROOT / "research/ocean-state-sant-closed-box-density-boundary-screen-2018.json").read_text(encoding="utf-8"))
    assert MODULE.build() == committed
    assert committed["status"] == "closed_horizontal_density_stratum_boundary_terms_not_transformation_or_budget"
    assert len(committed["months"]) == 4
    for month in committed["months"]:
        assert len(month["outcomes"]) == 4
        for outcome in month["outcomes"]:
            boundary = outcome["horizontal_density_boundary"]
            assert boundary["boundary_face_count"] == 64
            assert len(boundary["strata"]) == 4
            assert sum(item["wet_face_level_count"] for item in boundary["strata"]) == boundary["all_valid_wet_face_level_count"]
    assert "not density-class transformation rates" in committed["boundary"]
