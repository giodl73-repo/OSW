import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).with_name("fetch_oras5_drake_current_geometry_surface_terms.py")
SPEC = importlib.util.spec_from_file_location("drake_current_geometry_surface_terms", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_surface_term_urls_cover_the_fixed_2018_contract():
    assert len(MODULE.MONTHS) == 12
    assert MODULE.source_url("sohefldo", "201801").endswith("sohefldo_ORAS5_1m_201801_grid_T_02.nc")
    assert MODULE.source_url("sohtcbtm", "201812").endswith("sohtcbtm_ORAS5_1m_201812_grid_T_02.nc")
    with pytest.raises(ValueError):
        MODULE.source_url("vovecrtz", "201808")
