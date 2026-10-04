import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_closed_box_density_inventory.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_closed_box_density_inventory", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_closed_box_density_inventory_regenerates_without_transformation_claim():
    committed = json.loads((ROOT / "research/ocean-state-sant-closed-box-density-inventory-2018.json").read_text(encoding="utf-8"))
    assert MODULE.build() == committed
    assert committed["status"] == "fixed_box_TEOS10_density_stratum_occupancy_not_transformation"
    assert len(committed["boxes"]) == 4
    for box in committed["boxes"]:
        assert len(box["months"]) == 4
        assert len(box["successive_endpoint_stratum_volume_differences"]) == 3
        for month in box["months"]:
            assert len(month["strata"]) == 4
            assert abs(sum(item["volume_fraction"] for item in month["strata"]) - 1.0) < 1e-7
    assert "do not establish class-volume flux" in committed["boundary"]
