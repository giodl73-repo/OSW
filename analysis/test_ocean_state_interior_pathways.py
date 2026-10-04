import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_interior_pathways.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_interior_pathways", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_pathway_screen_regenerates_from_pinned_assignment():
    committed = json.loads((ROOT / "research/ocean-state-interior-sant-pathways-current-geometry-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert committed["status"] == "bounded_kinematic_screen_not_transport_or_budget"
    assert committed["join_status"] == "not_joined_to_archived_2018_contents_or_boundary_accounts"
    assert len(committed["selection"]["seeds"]) == 3
    assert len(committed["months"]) == 4


def test_screen_retains_predeclared_controls_and_nonzero_continuous_motion():
    payload = MODULE.build()
    for month in payload["months"]:
        assert len(month["tracks"]) == 14
        assert month["completed_track_count"] == 14
        assert len(month["relative_motion"]) == 3
        assert all(track["status"] == "completed_interior_screen" for track in month["tracks"])
    eastern_may = next(track for track in payload["months"][1]["tracks"] if track["id"] == "eastern")
    assert eastern_may["points"][0]["longitude_deg"] != eastern_may["points"][-1]["longitude_deg"]
    western_may = next(item for item in payload["months"][1]["relative_motion"] if item["seed"] == "western")
    assert western_may["mean_control_separation_change_km"] < 0
    assert "not horizontal convergence" in western_may["boundary"]


def test_assignment_and_velocity_receipts_are_checksum_bound():
    payload = MODULE.build()
    assignment = ROOT / payload["membership_source"]["path"]
    assert payload["membership_source"]["sha256"] == hashlib.sha256(assignment.read_bytes()).hexdigest()
    for month in payload["months"]:
        state = ROOT / month["state_path"]
        assert month["state_sha256"] == hashlib.sha256(state.read_bytes()).hexdigest()
