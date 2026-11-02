import copy
import csv
import hashlib
import io
import json
import unittest
from collections import Counter
from datetime import datetime
import build_current_depth_register_v47 as depth


class FloridaFittedDepthAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = depth.build()
        cls.rows = cls.data['evidence'][-38:]
        cls.old = json.loads((depth.ROOT / 'research/current-depth-register-v46.json').read_bytes())
        cls.source = json.loads((depth.ROOT / 'research/source-data/florida-spray-seasonal-depth-v1/candidate.json').read_bytes())

    def profile(self, row):
        return self.source['records'][int(row['source_profile_pointer'].split('/')[-1])]

    def test_previous453_references_and_coverage_preserved(self):
        self.assertEqual(self.data['evidence'][:453], self.old['evidence'])
        self.assertEqual(self.data['counts'], {'identities': 111, 'depth_references': 491,
            'identities_with_scoped_depth_reference': 101, 'identities_not_yet_assessed': 10,
            'whole_route_depth_profiles': 0, 'volume_estimates': 0})

    def test38_descriptors_share13_fitted_profiles(self):
        self.assertEqual(Counter(r['metric'] for r in self.rows), {'core_depth': 13,
            'derived_supported_component_penetration_lower_bound': 13,
            'derived_relative_core_component_decay_depth': 12})
        self.assertEqual(Counter(Counter(r['source_case_id'] for r in self.rows).values()), {3: 12, 2: 1})
        self.assertTrue(all(not r['independent_observation_count_claimed'] for r in self.rows))

    def test_sampled_cores_and_shallow_edges_not_surface(self):
        for row in self.rows:
            sample = self.profile(row)
            primary = sample['selected_profile']['absolute_component_threshold_layers'][0]
            if row['metric'] == 'core_depth':
                self.assertEqual(row['approximate_value_m'], primary['core_depth_m'])
            self.assertEqual(row['source_sampled_core_at_shallowest_valid_level'], primary['core_depth_m'] == 10)
            self.assertEqual(row['source_shallowest_fitted_depth_m'], 10)
            self.assertIsNone(row['upper_boundary_m'])
            self.assertIsNone(row['thickness_m'])

    def test_half_core_crossings_native_brackets_and_component_frame(self):
        for row in self.rows:
            if row['metric'] != 'derived_relative_core_component_decay_depth':
                continue
            sample = self.profile(row)
            z = sample['depth_levels_m']
            v = sample['selected_profile']['source_values']['northward_velocity']
            a, b = row['source_native_bracketing_depths_m']
            ia, ib = z.index(a), z.index(b)
            self.assertEqual(ib, ia + 1)
            threshold = row['source_velocity_threshold_m_s']
            peak = max(value for dep, value in zip(z, v) if 0 <= dep <= 200 and value is not None and value > .05)
            self.assertAlmostEqual(threshold, .5 * peak)
            self.assertGreater(v[ia], threshold)
            self.assertLessEqual(v[ib], threshold)
            computed = a + (threshold - v[ia]) * (b - a) / (v[ib] - v[ia])
            self.assertAlmostEqual(computed, row['source_computed_depth_before_display_rounding_m'], places=9)
            self.assertEqual(row['approximate_value_m'], int(10 * round(computed / 10)))
            self.assertEqual(row['source_relative_core_fraction'], .5)

    def test_supported_reach_is_inclusive_bound_not_bottom(self):
        for row in self.rows:
            if row['metric'] != 'derived_supported_component_penetration_lower_bound':
                continue
            sample = self.profile(row)
            z = sample['depth_levels_m']
            v = sample['selected_profile']['source_values']['northward_velocity']
            primary = sample['selected_profile']['absolute_component_threshold_layers'][0]
            index = z.index(row['lower_bound_m'])
            self.assertEqual(row['lower_bound_operator'], '>=')
            self.assertFalse(row['lower_bound_exclusive'])
            self.assertIsNone(row['approximate_value_m'])
            self.assertEqual(row['lower_bound_m'], primary['lower_last_connected_depth_m'])
            self.assertTrue(all(x is not None and x > .05 for x in v[primary['core_index']:index+1]))
            self.assertIsNone(v[index+1])
            self.assertIsNone(primary['lower_depth_m'])
            self.assertIsNone(row['lower_boundary_m'])
            self.assertFalse(row['source_product_limit_is_current_bottom'])

    def test_raw_phase_coordinates_and_nominal_phase_keys_separate(self):
        for row in self.rows:
            sample = self.profile(row)
            self.assertEqual(row['source_actual_provider_phase_timestamp_utc'], sample['actual_provider_phase_timestamp_utc'])
            self.assertFalse(row['source_original_time_coordinate_modified'])
            self.assertFalse(row['source_phase_timestamp_is_observation_date'])
            self.assertFalse(row['source_is_monthly_average'])
            self.assertIsNone(row['observed_period'])
            if row['calendar_months'] is not None:
                actual = datetime.fromisoformat(row['source_actual_provider_phase_timestamp_utc'].replace('Z', '+00:00'))
                nominal = datetime.fromisoformat(row['source_nominal_phase_calendar_date'] + 'T00:00:00+00:00')
                self.assertLessEqual(abs((actual - nominal).total_seconds()), 600)
                self.assertEqual(nominal.month, row['calendar_months'][0])
                self.assertEqual(nominal.day, 15)
            self.assertEqual(row['source_documented_fit_observation_period'], ['2015-07-16', '2023-05-30'])

    def test_missing_november_relative_depth_not_filled(self):
        november = [r for r in self.rows if r['calendar_months'] == [11]]
        self.assertEqual(len(november), 2)
        self.assertFalse(any(r['metric'] == 'derived_relative_core_component_decay_depth' for r in november))
        source = self.profile(november[0])['selected_profile']['half_sampled_core_component_decay']
        self.assertIsNone(source['lower_depth_m'])
        self.assertEqual(source['lower_status'], 'censored_before_missing_or_dry_level')

    def test_florida_scope_no_system_inheritance_or_volume(self):
        self.assertTrue(all(r['entity_id'] == 'current:florida' for r in self.rows))
        for entity in ['current:gulf-stream', 'current:north-atlantic']:
            self.assertEqual([r for r in self.old['records'] if r['entity_id'] == entity],
                             [r for r in self.data['records'] if r['entity_id'] == entity])
        for row in self.rows:
            self.assertFalse(row['reference_route_projection_eligible'])
            self.assertFalse(row['volume_eligible'])
            self.assertFalse(row['physical_state_join_eligible'])
            self.assertFalse(row['source_component_uncertainty_is_depth_error'])
            self.assertIsNone(row['uncertainty_m'])
            self.assertIsNone(row['same_source_width_reference_id'])

    def test_mutations_reject_bound_role_clock_and_promotions(self):
        for row in self.rows:
            for key, value in [('entity_id', 'current:gulf-stream'), ('source_relative_core_fraction', .6),
                               ('source_is_monthly_average', True), ('source_original_time_coordinate_modified', True),
                               ('source_product_limit_is_current_bottom', True), ('uncertainty_m', 10),
                               ('volume_eligible', True), ('lower_bound_operator', '>')]:
                changed = copy.deepcopy(row)
                changed[key] = value
                with self.subTest(reference=row['id'], field=key), self.assertRaises(ValueError):
                    depth.validate_context(changed)

    def test_exact_outputs_and_previous_csv_cells(self):
        self.assertEqual(self.data, json.loads((depth.ROOT / depth.OUTPUT).read_bytes()))
        raw = depth.csv_bytes(self.data)
        self.assertEqual(raw, (depth.ROOT / depth.CSV).read_bytes())
        rows = list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        old = list(csv.DictReader(io.StringIO((depth.ROOT / 'research/current-depth-register-v46.csv').read_text(encoding='utf8'))))
        for before, after in zip(old, rows):
            for key, value in before.items():
                self.assertEqual(value, after[key], (before['id'], key))
        bound = next(r for r in rows[-38:] if r['metric'] == 'derived_supported_component_penetration_lower_bound')
        self.assertEqual(bound['lower_bound_operator'], '>=')
        self.assertEqual(bound['approximate_value_m'], '')

    def test_input_pins_and_source_fit_support_retained(self):
        for path, pin in self.data['input_sha256'].items():
            self.assertEqual(hashlib.sha256((depth.ROOT / path).read_bytes()).hexdigest(), pin)
        for row in self.rows:
            support = self.profile(row)['selected_profile']['source_fit_support']
            self.assertEqual(set(support), {'along_stream_scale', 'cross_stream_scale', 'downstream_direction',
                'n_pts_fit', 'n_missions_fit', 'max_gap', 'arc_fit'})
            self.assertFalse(row['source_native_grid_is_independent_observation_spacing'])


if __name__ == '__main__':
    unittest.main()
