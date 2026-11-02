from datetime import datetime
import unittest
from acquire_eac_mooring_depth_benchmark_v1 import day_index, check_budget, diagnose


class MooringBenchmark(unittest.TestCase):
    def test_exact_source_day_not_nearest_time(self):
        times = [datetime(2022, 1, 14, 12), datetime(2022, 1, 15, 12)]
        self.assertEqual(day_index(times, '2022-01-15'), 1)
        with self.assertRaises(ValueError):
            day_index(times, '2022-01-16')

    def test_duplicate_date_rejected(self):
        with self.assertRaises(ValueError):
            day_index([datetime(2022, 1, 15), datetime(2022, 1, 15, 12)], '2022-01-15')

    def test_budget_before_field_retrieval(self):
        self.assertEqual(check_budget(3770, 182, 0, 20000), 1456)
        for args in [(90000, 182, 0, 20000), (3770, 501, 0, 20000), (3770, 182, 19500, 20000)]:
            with self.assertRaises(ValueError):
                check_budget(*args)

    def test_true_north_poleward_sign_and_thickness(self):
        south, rows = diagnose([0, 100, 200], [0, -.2, 0], [.1])
        self.assertEqual(south, [0, .2, 0])
        self.assertEqual(rows[0]['layer_thickness_m'], 100)
        self.assertEqual(rows[0]['status'], 'resolved_connected_processed_observation_threshold_layer')

    def test_missing_surface_not_zero(self):
        _, rows = diagnose([0, 20, 100, 200], [None, -.2, -.3, 0], [.1])
        self.assertIsNone(rows[0]['upper_depth_m'])
        self.assertIsNotNone(rows[0]['lower_depth_m'])
        self.assertIsNone(rows[0]['layer_thickness_m'])

    def test_missing_deeper_not_bathymetry(self):
        _, rows = diagnose([0, 100, 200, 500], [None, -.3, None, 0], [.1])
        self.assertIsNone(rows[0]['lower_depth_m'])

    def test_no_poleward_core_remains_unknown(self):
        _, rows = diagnose([0, 100, 200], [None, .2, .1], [.05])
        self.assertEqual(rows[0]['status'], 'no_qualifying_core')


if __name__ == '__main__':
    unittest.main()
