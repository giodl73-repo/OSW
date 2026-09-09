import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_oras5_arctic_transport_pilot.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_arctic_transport_pilot", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticTransportPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.run(ROOT)

    def test_three_sections_and_two_barents_semantics_survive(self):
        self.assertEqual({"fram", "barents-proxy", "barents-closure"}, set(self.result["sections"]))
        self.assertGreater(self.result["barents_definition_difference"]["closure_minus_proxy_net_Sv"], 0)
        self.assertEqual("endpoint/section semantics difference, not an uncertainty interval", self.result["barents_definition_difference"]["interpretation"])

    def test_internal_transport_and_collocation_audits_pass(self):
        checks = self.result["checks"]
        self.assertTrue(checks["all_reference_identity_residuals_below_1W"])
        self.assertTrue(checks["volume_invariant_to_tracer_collocation"])
        self.assertLess(checks["maximum_absolute_collocation_heat_shift_percent"], 2)

    def test_atlantic_water_class_is_joint_temperature_salinity(self):
        for slug, section in self.result["sections"].items():
            threshold = section["atlantic_water_comparison_class"]["threshold"]
            self.assertIn("temperature_gt_degC", threshold)
            self.assertEqual(34.8, threshold["salinity_gt_PSU"])


if __name__ == "__main__":
    unittest.main()
