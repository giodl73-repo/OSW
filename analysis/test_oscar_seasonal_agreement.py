import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("derive_oscar_seasonal_agreement.py")
SPEC = importlib.util.spec_from_file_location("derive_oscar_seasonal_agreement", MODULE_PATH)
agreement = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(agreement)


class OscarSeasonalAgreementTests(unittest.TestCase):
    def test_alignment_and_reversal(self):
        seasons = ["DJF", "MAM", "JJA", "SON"]
        source = {
            "shape": [1, 2], "latitude_values": [0], "longitude_values": [20, 30],
            "season_order": seasons, "source": "test", "source_version": "test",
            "period_start": "a", "period_stop": "b", "source_sha256": "c" * 64,
            "seasons": {},
        }
        for index, season in enumerate(seasons):
            reversing = 1000 if index % 2 == 0 else -1000
            source["seasons"][season] = {
                "mean_u_mm_s": [1000, reversing], "mean_v_mm_s": [0, 0],
                "mean_instantaneous_speed_mm_s": [1000, 1000],
                "directional_persistence_thousandths": [1000, 1000],
            }
        payload = agreement.derive(source, "d" * 64, "2026-08-29T00:00:00Z")
        self.assertEqual([1000, 0], payload["cross_season_alignment_thousandths"])
        self.assertEqual([0, 1800], payload["maximum_seasonal_turn_degrees_tenths"])
        self.assertEqual(1, payload["summary"]["aligned_candidate_cells"])
        self.assertEqual(1, payload["summary"]["turning_candidate_cells"])
        self.assertIn("not natural boundaries", payload["boundary"])


if __name__ == "__main__":
    unittest.main()

