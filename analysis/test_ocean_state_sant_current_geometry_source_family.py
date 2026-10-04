import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_ocean_state_sant_current_geometry_source_family.py")
SPEC = importlib.util.spec_from_file_location("sant_current_geometry_source_family", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_source_family_regenerates_with_all_t_s_u_v_months():
    committed = json.loads((ROOT / "research/ocean-state-sant-current-geometry-physical-source-family-2018.json").read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert len(committed["months"]) == 4
    assert all(record["salinity"]["finite_core_fraction"] > 0.8 for record in committed["months"])
    assert committed["surface_storage_terms"]["month_count"] == 12
    assert (ROOT / committed["capability_audit"]["path"]).exists()
    assert "practical_salinity_on_T_cells" in committed["field_capabilities"]["available"]
    assert "native_vertical_velocity" in str(committed["field_capabilities"]["not_available_from_probed_ICDC_ORAS5_contract"])
