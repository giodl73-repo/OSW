import unittest
from sample_a20_gulf_stream_depth_brackets_v1 import sample_profile, coarse_indices, build


def point(u): return {'u_m_s': u, 'v_m_s': 0.0, 'uerr_m_s': .02}


class NativeDepthBracketChecks(unittest.TestCase):
    def test_linear_fixture_adjacent_native_endpoints_and_shared_level_cap(self):
        z = [float(i * 8) for i in range(801)]
        calls = []
        def read(i): calls.append(i); return point(.8 - z[i] / 2000)
        r = sample_profile(z, read)
        self.assertEqual(len(calls), len(set(calls)))
        self.assertLessEqual(len(calls), 40)
        for case in r['threshold_cases']:
            self.assertAlmostEqual(case['lower_depth_m'], (.8 - case['threshold_m_s']) * 2000)
            a, b = case['refined_bracket_indices']; self.assertEqual(b - a, 1)
            self.assertFalse(case['physical_current_bottom_established'])

    def test_hidden_earlier_reversal_never_becomes_verified_first_crossing(self):
        z = [float(i * 8) for i in range(801)]
        def read(i): return point(-.1 if z[i] == 400 or z[i] >= 1600 else .8)
        r = sample_profile(z, read)
        for c in r['threshold_cases']:
            self.assertGreater(c['lower_depth_m'], 1500)
            self.assertFalse(c['first_native_downcrossing_below_core_verified'])
            self.assertFalse(c['continuous_connection_from_core_verified'])
            self.assertTrue(c['skipped_native_levels_may_hide_earlier_reversal'])

    def test_missing_coarse_point_is_censored_not_zero(self):
        z = [float(i * 8) for i in range(801)]
        missing = coarse_indices(z)[6]
        r = sample_profile(z, lambda i: point(None if i == missing else .8))
        self.assertTrue(all(c['lower_depth_m'] is None for c in r['threshold_cases']))
        self.assertTrue(all(c['status'] == 'CENSORED_AT_MISSING_COARSE_SAMPLE' for c in r['threshold_cases']))

    def test_reverse_sign_and_deep_support_do_not_create_false_depth(self):
        z = [float(i * 8) for i in range(801)]
        negative = sample_profile(z, lambda i: point(-.8))
        self.assertTrue(all(c['status'] == 'NO_QUALIFYING_SAMPLED_UPPER200M_CORE' for c in negative['threshold_cases']))
        positive = sample_profile(z, lambda i: point(.8))
        self.assertTrue(all(c['status'] == 'RIGHT_CENSORED_ON_SAMPLED_COARSE_PATH' for c in positive['threshold_cases']))
        self.assertTrue(all(c['lower_depth_m'] is None for c in positive['threshold_cases']))

    def test_missing_bisection_midpoint_never_interpolated(self):
        z = [float(i * 8) for i in range(801)]
        initial = set(coarse_indices(z))
        r = sample_profile(z, lambda i: point(.8 - z[i] / 2000 if i in initial else None))
        self.assertTrue(all(c['status'] == 'CENSORED_AT_MISSING_REFINEMENT_SAMPLE' for c in r['threshold_cases']))
        self.assertTrue(all(c['lower_depth_m'] is None for c in r['threshold_cases']))

    def test_invalid_depth_axes_rejected_before_velocity_access(self):
        for z in [[0., 0.], [10., 0.], [0., None], [0., 10001.]]:
            with self.assertRaises(ValueError): sample_profile(z, lambda i: self.fail('No native velocity read allowed'))

    def test_actual_three_retained_casts_and_cumulative_resource_bounds(self):
        # Exactly one actual build in tests; producer is the second charged pass.
        r = build()
        self.assertEqual([p['station'] for p in r['profiles']], ['014', '015', '016'])
        self.assertEqual(r['counts']['source_cast_profiles'], 3)
        self.assertEqual(r['counts']['threshold_contexts'], 9)
        self.assertLessEqual(r['counts']['metadata_bound_including_two_packet_reads'], 10000)
        self.assertLessEqual(r['counts']['case_scalar_bound_including_one_actual_test_and_producer'], 250000)
        self.assertEqual(r['original_case_operations_remaining'], 0)
        self.assertEqual(r['counts']['provider_requests'], 0)
        self.assertFalse(r['whole_route_physical_depth_profile_established'])
        for p in r['profiles']:
            self.assertLessEqual(p['selected_native_levels'], 40)
            self.assertEqual(len(p['selected_native_indices']), len(set(p['selected_native_indices'])))
            for c in p['threshold_cases']:
                if c['lower_depth_m'] is not None:
                    a, b = c['refined_bracket_indices']; self.assertEqual(b - a, 1)
                    lo, hi = c['lower_depth_native_bracket_m']
                    self.assertLessEqual(lo, c['lower_depth_m']); self.assertLessEqual(c['lower_depth_m'], hi)
                self.assertFalse(c['local_crossing_is_first_crossing_of_entire_native_profile'])
                self.assertIsNone(c['physical_thickness_m'])
                self.assertIsNone(c['depth_confidence_interval_m'])


if __name__ == '__main__': unittest.main()
