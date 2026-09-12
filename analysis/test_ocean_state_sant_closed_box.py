import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def module(name: str):
    script = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), script)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


SELECTOR = module("select_ocean_state_sant_closed_box.py")
ANALYZER = module("analyze_ocean_state_sant_closed_box.py")


def test_committed_geometry_selection_regenerates_before_flux_outcomes():
    committed = json.loads((ROOT / "research/ocean-state-sant-closed-box-selection-current-geometry-v1.json").read_text(encoding="utf-8"))
    assert SELECTOR.build() == committed
    assert committed["eligible_box_count"] == 1598
    assert committed["primary"]["cell_count"] == 256
    assert len(committed["one_cell_displaced_controls"]) == 3


def test_committed_closed_horizontal_account_regenerates_without_total_convergence_claim():
    committed = json.loads((ROOT / "research/ocean-state-sant-closed-box-horizontal-account-2018.json").read_text(encoding="utf-8"))
    assert ANALYZER.build() == committed
    assert committed["status"] == "closed_horizontal_advective_boundary_screen_not_total_convergence_or_budget"
    assert len(committed["months"]) == 4
    for month in committed["months"]:
        assert len(month["outcomes"]) == 4
        assert all(outcome["horizontal_boundary"]["boundary_face_count"] == 64 for outcome in month["outcomes"])
    assert "not total convergence" in committed["boundary"]
