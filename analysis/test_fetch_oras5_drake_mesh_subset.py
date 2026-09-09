import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("fetch_oras5_drake_mesh_subset.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_drake_mesh_subset", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeMeshSubsetTests(unittest.TestCase):
    def test_mesh_contract_includes_tracer_and_velocity_masks(self):
        self.assertEqual(("tmask", "umask", "vmask"), module.THREE_D)

    def test_discovers_and_pads_native_index_box(self):
        lon = np.array([[-100, -80, -60, -40], [-100, -80, -60, -40], [-100, -80, -60, -40]])
        lat = np.array([[-75] * 4, [-60] * 4, [-45] * 4])
        box = module.discover_index_box(
            lon, lat, {"west": -75, "east": -45, "south": -65, "north": -55}, stride=4, padding=1
        )
        self.assertEqual({"y_start": 0, "y_stop_exclusive": 12, "x_start": 4, "x_stop_exclusive": 16}, box)

    def test_normalizes_wrapped_longitude(self):
        values = module.normalize_longitude(np.array([0, 180, 295, 359]))
        np.testing.assert_array_equal(np.array([0, -180, -65, -1]), values)

    def test_native_shape_caps_padded_box(self):
        lon = np.array([[0, 10], [0, 10]])
        lat = np.array([[0, 0], [10, 10]])
        box = module.discover_index_box(
            lon, lat, {"west": -1, "east": 11, "south": -1, "north": 11},
            stride=8, padding=4, native_shape=(10, 12),
        )
        self.assertEqual(10, box["y_stop_exclusive"])
        self.assertEqual(12, box["x_stop_exclusive"])

    def test_rejects_inverted_bounds(self):
        lon = np.zeros((2, 2)); lat = np.zeros((2, 2))
        with self.assertRaisesRegex(ValueError, "west < east"):
            module.discover_index_box(
                lon, lat, {"west": 10, "east": -10, "south": -5, "north": 5}, stride=1
            )

    def test_fails_when_coarse_sample_misses_target(self):
        lon = np.zeros((2, 2)); lat = np.zeros((2, 2))
        with self.assertRaisesRegex(ValueError, "no point"):
            module.discover_index_box(
                lon, lat, {"west": -80, "east": -40, "south": -70, "north": -50}, stride=1
            )


if __name__ == "__main__":
    unittest.main()
