import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("derive_oras5_barents_section_bakeoff.py")
SPEC = importlib.util.spec_from_file_location("derive_oras5_barents_section_bakeoff", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class BarentsSectionBakeoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.derive_file(ROOT / "atlas/data/oras5-arctic-entrances-mesh.nc")

    def test_both_paths_pass_topology_contract(self):
        for name in ("observational_proxy", "model_closure"):
            topology = self.result[name]["topology"]
            self.assertTrue(topology["connected_corner_chain"])
            self.assertTrue(topology["unique_faces"])
            self.assertTrue(topology["endpoint_degree_one"])
            self.assertTrue(topology["all_internal_degrees_two"])
            self.assertEqual(0, topology["corner_duplication_count"])

    def test_paths_preserve_different_endpoint_semantics(self):
        proxy = self.result["observational_proxy"]
        closure = self.result["model_closure"]
        self.assertFalse(proxy["stop_node"]["modeled_coast"])
        self.assertTrue(closure["stop_node"]["modeled_coast"])
        self.assertGreater(self.result["comparison"]["closure_stop_distance_from_bear_target_km"], 200.0)
        self.assertNotEqual((proxy["stop_node"]["y"], proxy["stop_node"]["x"]), (closure["stop_node"]["y"], closure["stop_node"]["x"]))

    def test_each_path_uses_both_native_face_types(self):
        for name in ("observational_proxy", "model_closure"):
            self.assertGreater(self.result[name]["u_face_count"], 0)
            self.assertGreater(self.result[name]["v_face_count"], 0)


if __name__ == "__main__":
    unittest.main()
