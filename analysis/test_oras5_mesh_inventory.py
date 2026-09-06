import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("fetch_oras5_mesh_inventory.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_mesh_inventory", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class Oras5MeshInventoryTests(unittest.TestCase):
    def test_parses_dds_and_exposes_vertical_face_gap(self):
        raw = b"""Dataset {
          Float64 e2u[t = 1][y = 1021][x = 1442];
          Float64 e1v[t = 1][y = 1021][x = 1442];
          Byte umask[t = 1][z = 75][y = 1021][x = 1442];
          Byte vmask[t = 1][z = 75][y = 1021][x = 1442];
          Float32 glamu[t = 1][y = 1021][x = 1442];
          Float32 gphiu[t = 1][y = 1021][x = 1442];
          Float32 glamv[t = 1][y = 1021][x = 1442];
          Float32 gphiv[t = 1][y = 1021][x = 1442];
          Int16 mbathy[t = 1][y = 1021][x = 1442];
          Float64 e3t_ps[t = 1][y = 1021][x = 1442];
          Float64 e3t_0[t = 1][z = 75];
        } mesh;"""
        result = module.package(raw, "2026-08-30T00:00:00+00:00")
        self.assertEqual(11, len(result["variables"]))
        missing = result["section_readiness_from_mesh_alone"]["missing"]
        self.assertIn("u_layer_thickness", missing)
        self.assertIn("v_layer_thickness", missing)
        self.assertNotIn("u_face_width", missing)
        self.assertTrue(result["face_thickness_reconstruction_candidate"]["available"])
        self.assertTrue(result["face_thickness_reconstruction_candidate"]["status"].startswith("not_accepted"))

    def test_rejects_non_dds_payload(self):
        with self.assertRaisesRegex(ValueError, "no recognized"):
            module.parse(b"not a DDS")


if __name__ == "__main__":
    unittest.main()
