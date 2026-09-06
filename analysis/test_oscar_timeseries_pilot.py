import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("fetch_oscar_timeseries_pilot.py")
SPEC = importlib.util.spec_from_file_location("fetch_oscar_timeseries_pilot", MODULE_PATH)
timeseries = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(timeseries)


def fixture(rows):
    return ("\n".join(",".join(map(str, row)) for row in rows) + "\n").encode()


class OscarTimeseriesPilotTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ("2018-01-06T00:00:00Z", 15, 0, 20, 0.5, -0.25),
            ("2018-01-01T00:00:00Z", 15, 10, 40, 0.1234, -0.5),
            ("2018-01-01T00:00:00Z", 15, 10, 20, "NaN", "NaN"),
            ("2018-01-06T00:00:00Z", 15, 10, 40, 0.1, 0.2),
            ("2018-01-01T00:00:00Z", 15, 0, 40, 0.3, 0.4),
            ("2018-01-06T00:00:00Z", 15, 10, 20, 0.6, 0.7),
            ("2018-01-01T00:00:00Z", 15, 0, 20, 0.0, 0.0),
            ("2018-01-06T00:00:00Z", 15, 0, 40, "NaN", 0.4),
        ]

    def test_packages_ordered_complete_frames_with_joint_mask(self):
        result = timeseries.package(fixture(self.rows), "2018-01-01", "2018-01-06", 20, "2026-01-01T00:00:00Z", "test")
        self.assertEqual([2, 2, 2], result["shape"])
        self.assertEqual([10.0, 0.0], result["latitude_values"])
        self.assertEqual([20.0, 40.0], result["longitude_values"])
        self.assertEqual([None, 123, 0, 300], result["frames"][0]["u_mm_s"])
        self.assertEqual([-500], [x for x in result["frames"][0]["v_mm_s"] if x == -500])
        self.assertEqual(3, result["frames"][0]["valid_cells"])
        self.assertEqual(3, result["frames"][1]["valid_cells"])
        self.assertEqual({"minimum": 5.0, "maximum": 5.0}, result["observed_cadence_days"])

    def test_rejects_incomplete_grid(self):
        with self.assertRaisesRegex(ValueError, "incomplete OSCAR grid"):
            timeseries.package(fixture(self.rows[:-1]), "2018-01-01", "2018-01-06", 20, "now", "test")

    def test_rejects_duplicate_cell(self):
        with self.assertRaisesRegex(ValueError, "duplicate OSCAR grid cell"):
            timeseries.package(fixture(self.rows + [self.rows[0]]), "2018-01-01", "2018-01-06", 20, "now", "test")

    def test_regional_query_keeps_descending_latitude_axis(self):
        query = timeseries.build_query("2017-12-01", "2018-11-21", 2, -45, -70, 280, 320)
        self.assertIn("(-45):2:(-70)", query)
        self.assertIn("(280):2:(320)", query)

    def test_rejects_reversed_regional_extent(self):
        with self.assertRaisesRegex(ValueError, "north > south"):
            timeseries.build_query("2017-12-01", "2018-11-21", 2, -70, -45, 280, 320)


if __name__ == "__main__":
    unittest.main()
