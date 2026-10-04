import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_2017_july_ensemble.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_2017_july_ensemble", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_selected_ensemble_screen_rebuilds_from_compact_native_fields():
    saved = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
    assert MODULE.build() == saved
    MODULE.validate(saved)
    assert [member["member"] for member in saved["members"]] == ["opa0", "opa1", "opa2", "opa3", "opa4"]
    assert saved["members"][0]["east_control_baseline_upstream_Sv"] == -0.021189639
    assert saved["decision"] == {"pass_count": 0, "member_count": 5, "east_control_baseline_upstream_sign_varies": True}
    assert [member["primary_baseline_centered_Sv"] > 0 for member in saved["members"]] == [True, False, False, True, False]


def test_member_source_is_bound_to_preselected_rule_and_native_archive():
    source = json.loads(MODULE.FIELDS.read_text(encoding="utf-8"))
    assert source["selection_rule"]["sha256"] == MODULE.sha256(MODULE.RULE)
    assert source["output"]["sha256"] == MODULE.sha256(ROOT / source["output"]["path"])
    assert source["shape_member_z_y_x"] == [4, 75, 20, 19]
    assert [item["member"] for item in source["members"]] == ["opa1", "opa2", "opa3", "opa4"]
