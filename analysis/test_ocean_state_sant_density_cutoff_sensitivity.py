import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_density_cutoff_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_density_cutoff_sensitivity", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_cutoff_challenge_reproduces_annual_baselines_and_preserves_total_flux():
    committed = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
    assert MODULE.build() == committed
    MODULE.validate(committed)
    assert committed["method"]["cutoff_shifts_sigma0_kg_m3"] == [-0.1, 0.0, 0.1]
    assert "after inspection" in committed["method"]["selection_timing"]
    july = committed["months"][6]
    for outcome in july["outcomes"]:
        assert all(scheme["bins"][2][method] > 0 for scheme in outcome["schemes"] for method in ("centered_net_outward_Sv", "upstream_net_outward_Sv"))
    august = committed["months"][7]["outcomes"][0]
    assert august["schemes"][1]["bins"][2]["centered_net_outward_Sv"] > 0
    assert august["schemes"][1]["bins"][2]["upstream_net_outward_Sv"] < 0
    for month in committed["months"][6:10]:
        primary = month["outcomes"][0]
        assert primary["schemes"][1]["bins"][1]["volume_fraction"] == 0
        assert primary["schemes"][2]["bins"][1]["volume_fraction"] > 0
