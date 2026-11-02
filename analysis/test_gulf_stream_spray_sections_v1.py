import unittest
from acquire_gulf_stream_spray_sections_v1 import project, select_axis, check_budget, subset_query, FIELDS, diagnose


class GulfStreamSectionOperator(unittest.TestCase):
    def candidate(self, north=.4, east=0., direction=0.):
        return {'source_lon_lat': [-75, 35],
                'source_values': {'eastward_velocity': [east] * 100, 'northward_velocity': [north] * 100},
                'source_fit_support': {'downstream_direction': [direction] * 100}}

    def test_direction_is_clockwise_from_north_and_signed(self):
        self.assertAlmostEqual(project(.4, .2, 90), .4)
        self.assertAlmostEqual(project(.4, .2, 0), .2)
        self.assertLess(project(-.4, -.2, 45), 0)
        self.assertIsNone(project(None, .2, 45))

    def test100m_frame_does_not_turn_deep_return_flow_positive(self):
        z = list(range(10, 1001, 10))
        c = self.candidate()
        c['source_values']['northward_velocity'][49:] = [-.3] * 51
        c['source_fit_support']['downstream_direction'][49:] = [180] * 51
        selected, audit = select_axis(z, [c])
        self.assertEqual(selected, 0)
        locked = audit[0]['reference_direction_at100m_degrees_clockwise_from_north']
        self.assertEqual(locked, 0)
        self.assertLess(project(0, -.3, locked), 0)
        self.assertGreater(project(0, -.3, 180), 0)

    def test_prescribed_sector_rejects_equatorward_return(self):
        z = list(range(10, 1001, 10))
        selected, rows = select_axis(z, [self.candidate(north=-.4, direction=180)])
        self.assertIsNone(selected)
        self.assertIsNone(rows[0]['upper10_to200m_signed_integral_m2_s'])

    def test_fixed_support_ties_and_missing_values(self):
        z = list(range(10, 1001, 10))
        missing = self.candidate(north=2)
        missing['source_values']['northward_velocity'][5] = None
        selected, rows = select_axis(z, [missing, self.candidate(), self.candidate()])
        self.assertEqual(selected, 1)
        self.assertIsNone(rows[0]['upper10_to200m_signed_integral_m2_s'])
        self.assertAlmostEqual(rows[1]['upper10_to200m_signed_integral_m2_s'], 76.)

    def test_missing_reference_direction_not_invented(self):
        c = self.candidate()
        c['source_fit_support']['downstream_direction'][9] = None
        self.assertIsNone(select_axis(list(range(10, 1001, 10)), [c])[0])

    def test_budget_before_one_dimensional_section_request(self):
        self.assertEqual(check_budget(100, 1, 31, 0, 3000000), 34100)
        for args in [(100, 2, 2, 0, 3000000), (100, 1, 51, 0, 3000000), (100, 1, 31, 2990000, 3000000)]:
            with self.assertRaises(ValueError):
                check_budget(*args)

    def test_batched_query_uses_exact_indices_all_fields(self):
        query = subset_query(123, 20, 20, 10, 40)
        self.assertEqual(len(query.split(',')), len(FIELDS))
        self.assertTrue(all(v.endswith('[123][0:1:99][20:1:20][10:1:40]') for v in query.split(',')))
        self.assertTrue(query.startswith('eastward_velocity['))

    def test_crossings_preserve_top10m_censoring_and_deep_sign(self):
        layers, half = diagnose([10, 100, 200, 300], [.8, .6, .2, -.2], [.05])
        self.assertAlmostEqual(layers[0]['lower_depth_m'], 237.5)
        self.assertIsNone(layers[0]['upper_depth_m'])
        self.assertIsNone(layers[0]['layer_thickness_m'])
        self.assertAlmostEqual(half['lower_depth_m'], 150)


if __name__ == '__main__':
    unittest.main()
