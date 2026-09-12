import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).with_name("fetch_oras5_drake_current_geometry_salinity.py")
SPEC = importlib.util.spec_from_file_location("drake_current_geometry_salinity", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_salinity_url_and_month_validation():
    assert MODULE.source_url("201808").endswith("vosaline_ORAS5_1m_201808_grid_T_02.nc")
    with pytest.raises(ValueError):
        MODULE.source_url("201813")
