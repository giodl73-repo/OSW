import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_surface_storage.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_surface_storage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_open_surface_storage_account_regenerates():
    committed = json.loads((ROOT / "research/ocean-state-sant-current-geometry-surface-storage-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert committed["status"] == "open_surface_forcing_and_storage_account_no_convergence_or_closure"
    assert len(committed["monthly_account"]) == 12
    assert len(committed["successive_storage_differences"]) == 11


def test_account_retains_state_coverage_without_claiming_convergence():
    payload = MODULE.build()
    assert min(item["valid_area_fraction"] for item in payload["monthly_account"]) > .99
    assert "not heat convergence" in payload["boundary"]
