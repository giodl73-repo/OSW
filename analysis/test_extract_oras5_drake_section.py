import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("extract_oras5_drake_section.py")
SPEC = importlib.util.spec_from_file_location("extract_oras5_drake_section", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeSectionExtractionTests(unittest.TestCase):
    def fixture(self):
        mesh = {
            "e3t_0": np.array([10.0, 20.0]),
            "mbathy": np.array([[2, 1, 0], [2, 2, 0], [0, 0, 0]]),
            "e3t_ps": np.array([[15.0, 7.0, 0], [20.0, 12.0, 0], [0, 0, 0]]),
            "umask": np.zeros((2, 3, 3), dtype=int),
            "e2u": np.ones((3, 3)) * 100,
        }
        mesh["umask"][:, 0:2, 0] = np.array([[1, 1], [0, 1]])
        state = {
            "votemper": np.ones((2, 3, 3)) * 2,
            "vozocrtx": np.ones((2, 3, 3)) * .5,
        }
        selected = {
            "x": 0, "y_start": 0, "y_stop_exclusive": 2,
            "longitude_deg": [-67, -67], "latitude_deg": [-64, -56],
            "positive_normal": "native +i / approximately eastward",
        }
        return mesh, state, selected

    def test_builds_level_major_explicit_face_contract(self):
        result = module.build_payload(*self.fixture(), {"month": "201802"})
        self.assertEqual([2, 2], result["shape"])
        self.assertEqual([7.0, 10.0, None, 12.0], result["cell_thickness_m"])
        self.assertEqual([1, 1, 0, 1], result["wet_fraction"])
        self.assertEqual([2.0, 2.0, None, 2.0], result["potential_temperature_degC"])

    def test_rejects_mask_thickness_disagreement(self):
        mesh, state, selected = self.fixture()
        mesh["umask"][0, 0, 0] = 0
        with self.assertRaisesRegex(ValueError, "disagrees"):
            module.build_payload(mesh, state, selected, {"month": "201802"})

    def test_temperature_collocation_variants_are_explicit(self):
        mesh, state, selected = self.fixture()
        state["votemper"][:, :, 0] = 1
        state["votemper"][:, :, 1] = 3
        state["vozocrtx"][0, 0, 0] = -0.5
        west = module.build_payload(mesh, state, selected, {"month": "201802"}, "west")
        east = module.build_payload(mesh, state, selected, {"month": "201802"}, "east")
        upwind = module.build_payload(mesh, state, selected, {"month": "201802"}, "upwind")
        self.assertEqual(1, west["potential_temperature_degC"][0])
        self.assertEqual(3, east["potential_temperature_degC"][0])
        self.assertEqual(3, upwind["potential_temperature_degC"][0])

    def test_rejects_unknown_temperature_collocation(self):
        with self.assertRaisesRegex(ValueError, "mean, west, east, or upwind"):
            module.build_payload(*self.fixture(), {"month": "201802"}, "cubic")


if __name__ == "__main__":
    unittest.main()
