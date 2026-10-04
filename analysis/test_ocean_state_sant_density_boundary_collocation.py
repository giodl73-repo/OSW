import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_density_boundary_collocation.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_density_boundary_collocation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_upstream_cell_follows_native_velocity_direction():
    t = np.array([[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]])
    s = t + 30.0
    u_t, u_s = MODULE.upstream_pair({"face": "U", "y": 0, "x": 0}, t, s, np.array([1.0, -1.0]))
    v_t, v_s = MODULE.upstream_pair({"face": "V", "y": 0, "x": 0}, t, s, np.array([-1.0, 1.0]))
    assert u_t.tolist() == [1.0, 6.0] and u_s.tolist() == [31.0, 36.0]
    assert v_t.tolist() == [3.0, 5.0] and v_s.tolist() == [33.0, 35.0]


def test_committed_sensitivity_reproduces_baseline_and_conserves_total_flux():
    committed = json.loads((ROOT / "research/ocean-state-sant-density-boundary-collocation-sensitivity-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    MODULE.validate(committed)
    assert committed["status"] == "method_sensitivity_only_not_transformation_or_budget"
    primary = [month["outcomes"][0] for month in committed["months"]]
    assert any(outcome["changed_bin_face_level_count"] > 0 for outcome in primary)
    assert max(abs(item["upstream_minus_centered_Sv"]) for outcome in primary for item in outcome["strata"]) > 0.5
