import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("derive_oras5_drake_gate.py")
SPEC = importlib.util.spec_from_file_location("derive_oras5_drake_gate", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeGateTests(unittest.TestCase):
    def test_wet_runs_are_half_open(self):
        self.assertEqual([(1, 3), (4, 7)], module.wet_runs([0, 1, 1, 0, 1, 1, 1]))

    def test_selects_land_bounded_run_nearest_target_longitude(self):
        ny, nx = 20, 3
        wet = np.zeros((ny, nx), dtype=int)
        wet[2:18, 0] = 1; wet[2:18, 1] = 1
        lat = np.tile(np.linspace(-66, -54, ny)[:, None], (1, nx))
        lon = np.tile(np.array([-70, -67, -62])[None, :], (ny, 1))
        result = module.derive(wet, lon, lat)
        self.assertEqual(1, result["selected"]["x"])
        self.assertEqual(2, result["selected"]["y_start"])
        self.assertEqual(18, result["selected"]["y_stop_exclusive"])
        self.assertEqual("native +i / approximately eastward", result["selected"]["positive_normal"])

    def test_rejects_run_touching_subset_edge(self):
        wet = np.ones((20, 2), dtype=int)
        lat = np.tile(np.linspace(-66, -54, 20)[:, None], (1, 2))
        lon = np.full((20, 2), -67)
        with self.assertRaisesRegex(ValueError, "no land-bounded"):
            module.derive(wet, lon, lat)


if __name__ == "__main__":
    unittest.main()
