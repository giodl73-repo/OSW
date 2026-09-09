import importlib.util
import math
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_agulhas_motion.py")
SPEC = importlib.util.spec_from_file_location("analyze_agulhas_motion", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class AgulhasMotionTests(unittest.TestCase):
    def test_seasons_cover_all_months_once(self):
        months = [month for values in module.SEASON_MONTHS.values() for month in values]
        self.assertEqual(list(range(1, 13)), sorted(months))

    def test_window_indices_respect_declared_extent(self):
        payload = {
            "latitude_values": [-1, -2, -3],
            "longitude_values": [10, 11, 12, 13],
        }
        extent = {"south": -3, "north": -2, "west": 11, "east": 12}
        self.assertEqual([5, 6, 9, 10], module.window_indices(payload, extent))

    def test_vector_coherence_distinguishes_turning_from_alignment(self):
        aligned = module.summarize_samples([(1, 0), (2, 0)])
        turning = module.summarize_samples([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.assertAlmostEqual(1, aligned["vector_coherence"])
        self.assertAlmostEqual(0, turning["vector_coherence"])
        self.assertTrue(math.isclose(1, turning["mean_speed_m_s"]))

    def test_release_ids_are_unique(self):
        ids = [seed["id"] for seed in module.SEEDS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_shipped_receipt_preserves_junction_result(self):
        root = pathlib.Path(__file__).parents[1]
        receipt = module.run(root / "atlas/data/oscar-timeseries-agulhas-native-2018.js")
        windows = {window["id"]: window["annual"] for window in receipt["windows"]}
        self.assertGreater(windows["boundary-current"]["southward_fraction"], 0.60)
        self.assertGreater(windows["return-current"]["eastward_fraction"], 0.70)
        self.assertLess(windows["retroflection"]["vector_coherence"], 0.10)
        self.assertLess(windows["cape-basin"]["vector_coherence"], 0.12)
        self.assertEqual(28, receipt["track_summary"]["completed"])


if __name__ == "__main__":
    unittest.main()
