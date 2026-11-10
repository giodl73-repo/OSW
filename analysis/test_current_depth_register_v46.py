import copy
import csv
import hashlib
import io
import json
import unittest
from collections import Counter
import build_current_depth_register_v46 as depth


class EACFixedStationDepthAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = depth.build()
        cls.rows = cls.data['evidence'][-14:]
        cls.old = json.loads((depth.ROOT / 'research/current-depth-register-v45.json').read_bytes())
        cls.source = json.loads((depth.ROOT / 'research/source-data/eac-mooring-depth-benchmark-v1/candidate.json').read_bytes())

    def test_previous439_references_and_identity_coverage(self):
        self.assertEqual(self.data['evidence'][:439], self.old['evidence'])
        self.assertEqual(self.data['counts'], {'identities': 111, 'depth_references': 453,
            'identities_with_scoped_depth_reference': 101, 'identities_not_yet_assessed': 10,
            'whole_route_depth_profiles': 0, 'volume_estimates': 0})

    def test_four_stations_six_profiles_not14_independent_observations(self):
        self.assertEqual(Counter(r['source_station_id'] for r in self.rows),
                         {'EAC0500': 1, 'EAC2000': 1, 'EAC3200': 6, 'EAC4200': 6})
        self.assertEqual(sorted(Counter(r['source_case_id'] for r in self.rows).values()), [1, 1, 3, 3, 3, 3])
        self.assertTrue(all(not r['independent_observation_count_claimed'] for r in self.rows))
        self.assertTrue(all(r['entity_id'] == 'current:east-australian' for r in self.rows))

    def test_native_component_crossing_not_speed_or_interpolated_gap(self):
        for row in self.rows:
            sample = self.source['samples'][int(row['source_profile_pointer'].split('/')[-1])]
            layer = sample['threshold_layers'][int(row['source_layer_pointer'].split('/')[-1])]
            self.assertEqual(layer['lower_status'], 'adjacent_isotach_crossing')
            self.assertEqual(row['mooring_lon_lat'], sample['lon_lat'])
            z = sample['depth_levels_m']
            a, b = row['source_native_bracketing_depths_m']
            ia, ib = z.index(a), z.index(b)
            self.assertEqual(ib, ia + 1)
            va, vb = (-sample['source_values']['VCUR'][i] for i in [ia, ib])
            t = row['source_velocity_threshold_m_s']
            self.assertGreater(va, t)
            self.assertLessEqual(vb, t)
            computed = a + (t - va) * (b - a) / (vb - va)
            self.assertAlmostEqual(computed, row['source_computed_depth_before_display_rounding_m'], places=9)
            self.assertEqual(row['approximate_value_m'], int(10 * round(computed / 10)))

    def test_unknown_upper_boundary_not_zero_thickness(self):
        for row in self.rows:
            self.assertEqual(row['source_upper_boundary_status'], 'censored_before_missing_or_dry_level')
            self.assertIsNone(row['upper_boundary_m'])
            self.assertIsNone(row['lower_boundary_m'])
            self.assertIsNone(row['thickness_m'])
            self.assertEqual(row['metric'], 'derived_fixed_station_component_isotach_depth')
            self.assertFalse(row['volume_eligible'])

    def test_daily_filtered_support_not_instantaneous_or_climatology(self):
        for row in self.rows:
            self.assertIn(row['source_daily_calendar_date'], ['2022-01-15', '2022-07-15'])
            self.assertTrue(row['source_actual_daily_timestamp_utc'].startswith(row['source_daily_calendar_date']))
            self.assertEqual(row['source_daily_filter_days'], 5)
            self.assertIsNone(row['observed_period'])
            self.assertIsNone(row['calendar_months'])
            self.assertIsNone(row['annual_range_m'])
            self.assertFalse(row['source_SOM_filled_velocity_used'])
            self.assertFalse(row['source_spatially_mapped_bottom_boundary_used'])

    def test_offshore_thickness_and_missing_profiles_not_admitted(self):
        self.assertTrue(any(s['station'] == '4800' and s['threshold_layers'][0]['layer_thickness_m'] is not None
                            for s in self.source['samples']))
        self.assertTrue(all(r['source_station_id'] not in ['EAC4700', 'EAC4800', 'EACNRSNSI'] for r in self.rows))
        for row in self.rows:
            self.assertFalse(row['source_model_observation_colocation_or_identity_validated'])
            self.assertFalse(row['reference_route_projection_eligible'])
            self.assertFalse(row['physical_state_join_eligible'])
            self.assertIsNone(row['uncertainty_m'])

    def test_mutations_reject_station_time_sign_and_promotions(self):
        for row in self.rows:
            for key, value in [('source_station_id', 'EAC4800'), ('source_daily_filter_days', 1),
                               ('source_SOM_filled_velocity_used', True), ('thickness_m', 900),
                               ('source_velocity_quantity', 'horizontal_speed'), ('uncertainty_m', 20),
                               ('source_component_uncertainty_is_depth_error', True),
                               ('source_model_observation_colocation_or_identity_validated', True),
                               ('volume_eligible', True)]:
                mutated = copy.deepcopy(row)
                mutated[key] = value
                with self.subTest(reference=row['id'], field=key), self.assertRaises(ValueError):
                    depth.validate_context(mutated)

    def test_exact_json_csv_and_previous_cells(self):
        self.assertEqual(self.data, json.loads((depth.ROOT / depth.OUTPUT).read_bytes()))
        raw = depth.csv_bytes(self.data)
        self.assertEqual(raw, (depth.ROOT / depth.CSV).read_bytes())
        rows = list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        old = list(csv.DictReader(io.StringIO((depth.ROOT / 'research/current-depth-register-v45.csv').read_text(encoding='utf8'))))
        for before, after in zip(old, rows):
            for key, value in before.items():
                self.assertEqual(value, after[key], (before['id'], key))
        self.assertEqual(json.loads(rows[-1]['mooring_lon_lat']), self.rows[-1]['mooring_lon_lat'])

    def test_all_source_pins_and_retained_uncertainty_fields(self):
        for path, pin in self.data['input_sha256'].items():
            self.assertEqual(hashlib.sha256((depth.ROOT / path).read_bytes()).hexdigest(), pin)
        for row in self.rows:
            sample = self.source['samples'][int(row['source_profile_pointer'].split('/')[-1])]
            self.assertEqual(len(sample['source_values']['VCUR_uncertainty']), len(sample['depth_levels_m']))
            self.assertFalse(row['source_component_uncertainty_is_depth_error'])


if __name__ == '__main__':
    unittest.main()
