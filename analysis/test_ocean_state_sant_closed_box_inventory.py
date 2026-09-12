import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_closed_box_inventory.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_closed_box_inventory", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_closed_box_inventory_screen_regenerates_without_tendency_or_budget_claim():
    committed = json.loads((ROOT / "research/ocean-state-sant-closed-box-inventory-change-screen-2018.json").read_text(encoding="utf-8"))
    assert MODULE.build() == committed
    assert committed["status"] == "fixed_box_column_heat_content_endpoints_not_tendency_or_budget"
    assert len(committed["boxes"]) == 4
    for box in committed["boxes"]:
        assert len(box["endpoints"]) == 4
        assert len(box["successive_endpoint_differences"]) == 3
        assert all(endpoint["valid_cells"] == 256 for endpoint in box["endpoints"])
    assert "not a tendency" in committed["boundary"]
