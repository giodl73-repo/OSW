import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("fetch_oisst_mhw_point.py")
SPEC = importlib.util.spec_from_file_location("fetch_oisst_mhw_point", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_query_is_one_exact_surface_cell():
    url, hyperslab = MODULE.build_query(1991)
    assert url.endswith("sst.day.mean.1991.nc")
    assert hyperslab == "sst[0:1:364][528][1240]"


def test_query_can_bound_event_window():
    _, hyperslab = MODULE.build_query(2026, 151, 231)
    assert hyperslab == "sst[151:1:231][528][1240]"
