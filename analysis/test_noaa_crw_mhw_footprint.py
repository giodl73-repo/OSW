import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("derive_noaa_crw_mhw_footprint.py")
SPEC = importlib.util.spec_from_file_location("derive_noaa_crw_mhw_footprint", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_component_uses_edges_not_corners():
    active = np.array([[1, 0], [0, 1]], dtype=bool)
    assert MODULE.connected_component(active, (0, 0), periodic_longitude=False) == {(0, 0)}


def test_component_wraps_at_longitude_seam():
    active = np.array([[1, 0, 1]], dtype=bool)
    assert MODULE.connected_component(active, (0, 0)) == {(0, 0), (0, 2)}


def test_run_encoding_keeps_category_changes():
    component = {(0, 0), (0, 1), (0, 2)}
    categories = np.array([[1, 1, 2]])
    rows = MODULE.encode_runs(component, categories, np.array([10.0]), np.array([20.0, 20.05, 20.1]))
    assert rows == [[10.0, [[20.0, 20.05, 1], [20.1, 20.1, 2]]]]
