import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("fetch_oscar_seasonal_pilot.py")
SPEC = importlib.util.spec_from_file_location("fetch_oscar_seasonal_pilot", MODULE_PATH)
seasonal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(seasonal)


class OscarSeasonalPilotTests(unittest.TestCase):
    def test_meteorological_seasons(self):
        self.assertEqual("DJF", seasonal.season_key("2018-01-10T00:00:00Z"))
        self.assertEqual("MAM", seasonal.season_key("2018-04-10T00:00:00Z"))
        self.assertEqual("JJA", seasonal.season_key("2018-07-10T00:00:00Z"))
        self.assertEqual("SON", seasonal.season_key("2018-10-10T00:00:00Z"))

    def test_query_requests_every_time_and_thins_space(self):
        query = seasonal.build_query("2017-12-01", "2018-11-21", 20)
        self.assertIn("(2017-12-01):1:(2018-11-21)", query)
        self.assertIn("(80):20:(-80)", query)

    def test_summary_alignment(self):
        vectors = {(0.0, 20.0): [(1.0, 0.0), (1.0, 0.0)]}
        result = seasonal.summarize(vectors, [0.0], [20.0], 2)
        self.assertEqual([1000], result["mean_u_mm_s"])
        self.assertEqual([1000], result["directional_persistence_thousandths"])
        self.assertEqual([2], result["sample_count"])


if __name__ == "__main__":
    unittest.main()

