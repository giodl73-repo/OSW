import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_interior_vertical_structure.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_interior_vertical_structure", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_vertical_structure_screen_regenerates_and_is_unjoined():
    committed = json.loads((ROOT / "research/ocean-state-interior-sant-vertical-structure-current-geometry-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert committed["status"] == "bounded_vertical_structure_and_shear_screen_not_vertical_transfer"
    assert committed["join_status"] == "not_joined_to_archived_2018_contents_or_boundary_accounts"


def test_profiles_have_declared_four_levels_three_interfaces_and_receipts():
    payload = MODULE.build()
    for month in payload["months"]:
        assert len(month["profiles"]) == 3
        assert hashlib.sha256((ROOT / month["state_path"]).read_bytes()).hexdigest() == month["state_sha256"]
        for profile in month["profiles"]:
            assert len(profile["levels"]) == 4
            assert len(profile["interfaces"]) == 3
            assert all(level["temperature_c"] == level["temperature_c"] for level in profile["levels"])
    august_central = next(profile for profile in payload["months"][2]["profiles"] if profile["seed"] == "central")
    assert august_central["interfaces"][0]["upper_minus_lower_temperature_c"] > 0
