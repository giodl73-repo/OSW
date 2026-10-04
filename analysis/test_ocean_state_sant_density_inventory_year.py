import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_density_inventory_year.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_density_inventory_year", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_annual_inventory_reproduces_four_custodied_months_and_partitions_volume():
    committed = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
    assert MODULE.build() == committed
    MODULE.validate(committed)
    assert committed["baseline"]["reproduced_months"] == ["201802", "201805", "201808", "201811"]
    for box in committed["boxes"]:
        volumes = [month["valid_volume_m3"] for month in box["months"]]
        assert max(volumes) - min(volumes) < 0.01
        for month in box["months"]:
            assert abs(sum(item["volume_m3"] for item in month["strata"]) - month["valid_volume_m3"]) < 0.1
    primary = committed["boxes"][0]["months"]
    assert all(primary[index]["strata"][1]["volume_m3"] == 0 for index in (6, 7, 8, 9))
    assert "not matched class-volume tendencies" in committed["boundary"]
