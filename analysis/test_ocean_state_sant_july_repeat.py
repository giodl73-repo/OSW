import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_july_repeat.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_july_repeat", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_preselected_july_repeat_screen_keeps_negative_control_case():
    committed = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
    assert MODULE.build() == committed
    MODULE.validate(committed)
    assert committed["decision"] == "repeat_year_sign_screen_fails"
    assert [year["predeclared_sign_pass"] for year in committed["years"]] == [True, False, True]
    failed = committed["years"][1]["outcomes"][3]
    assert failed["box"] == "east_control"
    assert failed["schemes"][1]["bins"][2]["upstream_net_outward_Sv"] < 0
    assert all(scheme["bins"][2][method] > 0 for year in committed["years"] for scheme in year["outcomes"][0]["schemes"] for method in ("centered_net_outward_Sv", "upstream_net_outward_Sv"))


def test_prior_july_source_archive_is_bound_to_frozen_selection():
    source = json.loads(MODULE.FIELDS.read_text(encoding="utf-8"))
    assert source["selection_rule"]["sha256"] == MODULE.sha256(MODULE.SELECTION_RULE)
    assert source["output"]["sha256"] == MODULE.sha256(ROOT / source["output"]["path"])
    assert [entry["month"] for entry in source["months"]] == ["201607", "201707"]
    assert source["shape_year_z_y_x"] == [2, 75, 20, 19]
