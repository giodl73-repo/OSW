import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_oras5_barents_section_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_barents_section_sensitivity", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class BarentsSectionSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.run(ROOT / "atlas/data/oras5-arctic-entrances-mesh.nc")

    def test_design_has_27_cases_per_semantics(self):
        self.assertEqual(27, self.result["observational_proxy"]["summary"]["case_count"])
        self.assertEqual(27, self.result["model_closure"]["summary"]["case_count"])
        self.assertEqual(43, self.result["baseline_reproduction"]["proxy_face_count"])
        self.assertEqual(73, self.result["baseline_reproduction"]["closure_face_count"])

    def test_all_cases_remain_topologically_valid(self):
        self.assertTrue(self.result["observational_proxy"]["summary"]["all_topology_checks_pass"])
        self.assertTrue(self.result["model_closure"]["summary"]["all_topology_checks_pass"])

    def test_sensitivity_changes_paths_without_becoming_uncertainty(self):
        self.assertGreater(self.result["observational_proxy"]["summary"]["unique_path_count"], 1)
        self.assertGreater(self.result["model_closure"]["summary"]["unique_path_count"], 1)
        self.assertEqual(9, self.result["observational_proxy"]["summary"]["scale_invariant_endpoint_case_count"])
        self.assertEqual(9, self.result["model_closure"]["summary"]["scale_invariant_endpoint_case_count"])
        self.assertIn("not ocean variability", self.result["boundary"])


if __name__ == "__main__":
    unittest.main()
