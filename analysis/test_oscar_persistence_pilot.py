import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("fetch_oscar_persistence_pilot.py")
SPEC = importlib.util.spec_from_file_location("fetch_oscar_persistence_pilot", MODULE_PATH)
persistence = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(persistence)


class OscarPersistencePilotTests(unittest.TestCase):
    def test_query_has_temporal_and_spatial_strides(self):
        query = persistence.build_query("2018-01-01", "2018-11-21", 6, 16)
        self.assertIn("(2018-01-01):6:(2018-11-21)", query)
        self.assertIn("(80):16:(-80)", query)
        self.assertIn(",v%5B", query)

    def test_ratio_distinguishes_alignment_from_cancellation(self):
        rows = []
        for time, first_u, second_u in (("t1", 1, 1), ("t2", 1, -1), ("t3", 1, 1), ("t4", 1, -1)):
            rows.append(f"{time},15,0,20,{first_u},0")
            rows.append(f"{time},15,0,30,{second_u},0")
        payload = persistence.package(
            ("\n".join(rows) + "\n").encode(), "2018-01-01", "2018-11-21", 6, 16,
            "2026-08-29T00:00:00Z", "https://example.test/query", minimum_samples=4,
        )
        self.assertEqual([1, 2], payload["shape"])
        self.assertEqual([1000, 0], payload["mean_u_mm_s"])
        self.assertEqual([1000, 0], payload["directional_persistence_thousandths"])
        self.assertEqual([4, 4], payload["sample_count"])
        self.assertIn("not a fixed current boundary", payload["boundary"])


if __name__ == "__main__":
    unittest.main()

