import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("synthesize_oras5_arctic_seasons.py")
SPEC = importlib.util.spec_from_file_location("synthesize_oras5_arctic_seasons", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticSeasonsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.run(ROOT)

    def test_four_months_cross_all_three_sections(self):
        self.assertEqual(3, len(self.result["sections"]))
        self.assertTrue(all(len(section["months"]) == 4 for section in self.result["sections"].values()))
        self.assertEqual(24, len(self.result["receipts"]))
        self.assertEqual(4, len(self.result["state_files"]))

    def test_direction_and_heat_signs_persist(self):
        checks = self.result["checks"]
        self.assertTrue(checks["all_three_net_volume_signs_persist"])
        self.assertTrue(checks["all_three_0C_heat_signs_persist"])
        self.assertTrue(checks["closure_exceeds_proxy_net_volume_every_month"])
        self.assertTrue(all(row["net_volume_Sv"] < 0 for row in self.result["sections"]["fram"]["months"]))
        self.assertTrue(all(row["heat_transport_PW"]["0.0"] > 0 for row in self.result["sections"]["fram"]["months"]))

    def test_transports_are_hash_pinned_and_reference_identity_closes(self):
        self.assertTrue(self.result["checks"]["all_section_inputs_pin_their_transports"])
        self.assertTrue(self.result["checks"]["all_state_files_match_retrieval_receipts"])
        self.assertTrue(self.result["checks"]["all_reference_identity_residuals_below_1W"])


if __name__ == "__main__":
    unittest.main()
