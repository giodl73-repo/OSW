import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("extract_oras5_arctic_sections.py")
SPEC = importlib.util.spec_from_file_location("extract_oras5_arctic_sections", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)


class ArcticSectionExtractionTests(unittest.TestCase):
    def fixture(self):
        mesh = {
            "e3t_0": np.array([10.0, 20.0]), "mbathy": np.ones((3, 3), dtype=int) * 2,
            "e3t_ps": np.ones((3, 3)) * 20.0, "umask": np.ones((2, 3, 3), dtype=int),
            "vmask": np.ones((2, 3, 3), dtype=int), "e2u": np.ones((3, 3)) * 100.0,
            "e1v": np.ones((3, 3)) * 200.0,
        }
        state = {
            "votemper": np.arange(18, dtype=float).reshape(2, 3, 3),
            "vosaline": np.ones((2, 3, 3)) * 35.0,
            "vozocrtx": np.ones((2, 3, 3)) * 0.5,
            "vomecrty": np.ones((2, 3, 3)) * 0.25,
        }
        faces = [
            {"face": "U", "y": 0, "x": 0, "sign_into_barents": 1, "longitude_deg": 20, "latitude_deg": 70},
            {"face": "V", "y": 0, "x": 1, "sign_into_barents": -1, "longitude_deg": 20, "latitude_deg": 71},
        ]
        return mesh, state, faces

    def test_mixed_faces_preserve_width_sign_and_salinity(self):
        mesh, state, faces = self.fixture()
        result = module.build_payload(mesh, state, "Barents", "test", faces, "201802", {"month": "201802"})
        self.assertEqual([2, 2], result["shape"])
        self.assertEqual([100.0, 200.0], result["segment_width_m"])
        self.assertEqual([0.5, -0.25, 0.5, -0.25], result["normal_velocity_m_s"])
        self.assertEqual([35.0] * 4, result["practical_salinity_PSU"])

    def test_collocation_uses_correct_neighbors_for_each_face(self):
        mesh, state, faces = self.fixture()
        result = module.build_payload(mesh, state, "Barents", "test", faces, "201802", {"month": "201802"})
        self.assertEqual([0.5, 2.5, 9.5, 11.5], result["potential_temperature_degC"])

    def test_rejects_bad_sign_or_collocation(self):
        mesh, state, faces = self.fixture()
        faces[0]["sign_into_barents"] = 0
        with self.assertRaisesRegex(ValueError, "sign"):
            module.build_payload(mesh, state, "Barents", "test", faces, "201802", {})
        with self.assertRaisesRegex(ValueError, "collocation"):
            module.collocate(state["votemper"], state["vozocrtx"][:, 0, 0], faces[1], "cubic")


if __name__ == "__main__":
    unittest.main()
