import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_interior_density_structure.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_interior_density_structure", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_density_structure_screen_regenerates_and_preserves_boundary():
    committed = json.loads((ROOT / "research/ocean-state-interior-sant-density-structure-current-geometry-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert committed["status"] == "bounded_TEOS10_density_and_numeric_class_structure_not_transformation"
    assert "not named water masses" in committed["boundary"]


def test_profiles_have_finite_teos10_density_and_fixed_numeric_strata():
    payload = MODULE.build()
    assert len(payload["method"]["numeric_strata_sigma0_kg_m3"]) == 4
    for month in payload["months"]:
        assert len(month["profiles"]) == 3
        for profile in month["profiles"]:
            assert len(profile["levels"]) == 4
            assert all(level["sigma0_kg_m3"] > 20 for level in profile["levels"])
