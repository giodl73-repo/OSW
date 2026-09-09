import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("fetch_oscar_historical_pilot.py")
SPEC = importlib.util.spec_from_file_location("fetch_oscar_historical_pilot", MODULE_PATH)
pilot = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(pilot)


class OscarHistoricalPilotTests(unittest.TestCase):
    def test_query_declares_both_components_and_domain(self):
        query = pilot.build_query("2018-11-16", 16)
        self.assertIn("yearly_336c_0b32_9cd3.csv0", query)
        self.assertIn("u%5B", query)
        self.assertIn(",v%5B", query)
        self.assertIn(":16:", query)

    def test_package_quantizes_and_masks_vectors(self):
        raw = (
            b"2018-11-16T00:00:00Z,15,10,20,0.125,-0.25\n"
            b"2018-11-16T00:00:00Z,15,10,30,NaN,NaN\n"
            b"2018-11-16T00:00:00Z,15,0,20,-0.5,0.75\n"
            b"2018-11-16T00:00:00Z,15,0,30,0,0\n"
        )
        payload = pilot.package(raw, "2018-11-16", 16, "2026-08-29T00:00:00Z", "https://example.test/query")
        self.assertEqual([2, 2], payload["shape"])
        self.assertEqual([125, None, -500, 0], payload["u_mm_s"])
        self.assertEqual([-250, None, 750, 0], payload["v_mm_s"])
        self.assertEqual(15, payload["nominal_depth_m"])
        self.assertIn("not OSCAR v2.0", payload["boundary"])


if __name__ == "__main__":
    unittest.main()
