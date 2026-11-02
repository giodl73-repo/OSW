from datetime import datetime
import unittest
from acquire_florida_spray_seasonal_depth_v1 import phase_indices, select_axis, check_budget, diagnose, source_doi_matches


class FloridaSprayDepth(unittest.TestCase):
    def test_exact_published_doi_spellings_only(self):
        self.assertTrue(source_doi_matches('10.21238/S8TC9W'))
        self.assertTrue(source_doi_matches('https://doi.org/10.21238/S8TC9W'))
        self.assertFalse(source_doi_matches('10.21238/S8SPRAY2675'))
        self.assertFalse(source_doi_matches('https://example.org/10.21238/S8TC9W'))

    def test_phase_labels_not_observation_year_or_monthly_average(self):
        times = [datetime(2016 if m < 7 else 2015, m, 15) for m in range(1, 13)]
        self.assertEqual(phase_indices(times), [(m, m - 1) for m in range(1, 13)])

    def test_missing_or_duplicate_phase_rejected(self):
        times = [datetime(2016, m, 15) for m in range(1, 13)]
        for changed in [times[:-1], times + [times[0]]]:
            with self.assertRaises(ValueError):
                phase_indices(changed)

    def test_axis_complete_signed_integrals_and_ties(self):
        selected, scores = select_axis([10, 100, 200], [[.3, .2, .1], [.4, .3, .2], [.4, .3, .2]])
        self.assertEqual(selected, 1)
        self.assertEqual(scores[1], 56.5)

    def test_missing_core_support_no_convenient_partial_integral(self):
        selected, scores = select_axis([10, 100, 200], [[2, None, 2], [.2, .2, .2]])
        self.assertEqual(selected, 1)
        self.assertIsNone(scores[0])
        self.assertIsNone(select_axis([10, 100, 200], [[-.2, -.2, -.2]])[0])

    def test_absolute_and_relative_depths_remain_distinct(self):
        rows, half = diagnose([10, 100, 200], [1, .6, .1], [.05, .1, .2])
        self.assertIsNone(rows[0]['lower_depth_m'])
        self.assertEqual(rows[1]['lower_depth_m'], 200)
        self.assertAlmostEqual(half['lower_depth_m'], 120)
        self.assertEqual(half['relative_sampled_core_fraction'], .5)

    def test10m_shallowest_level_not_surface_or_thickness(self):
        rows, half = diagnose([10, 100, 200], [1, .6, 0], [.05])
        self.assertIsNone(rows[0]['upper_depth_m'])
        self.assertIsNone(rows[0]['layer_thickness_m'])
        self.assertIsNone(half['layer_thickness_m'])

    def test_bounded_section_before_source_field_read(self):
        self.assertEqual(check_budget(100, 11, 0, 100000), 5100)
        for args in [(100, 30, 0, 100000), (100, 11, 99000, 100000), (99, 11, 0, 100000)]:
            with self.assertRaises(ValueError):
                check_budget(*args)

    def test_incomplete_prescribed_axis_rejected(self):
        with self.assertRaises(ValueError):
            select_axis([10, 100, 190], [[1, 1, 1]])


if __name__ == '__main__':
    unittest.main()
