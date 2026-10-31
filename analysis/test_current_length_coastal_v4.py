import hashlib
import json
import unittest
import estimate_current_reference_extents_v4 as estimates
import check_current_length_geography_v4 as geography


class ReversingCoastalLengths(unittest.TestCase):
    def test_complete_grid_reproduces_and_geography_is_bound(self):
        document = estimates.build()
        raw = (estimates.ROOT / estimates.OUTPUT).read_bytes()
        self.assertEqual(document, json.loads(raw))
        report = json.loads((estimates.ROOT / geography.OUTPUT).read_bytes())
        self.assertEqual(report['estimate_file_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual({r['entity_id'] for r in document['records']}, {r['entity_id'] for r in report['records']})
        self.assertEqual(sum(len(r['scenarios']) for r in document['records']), 324)
        self.assertTrue(all(r['all_clear'] and r['scenarios'] == r['coarse_land_clear'] == 36 for r in report['records']))
        for r in document['records']:
            low, high = r['scenario_range_km']
            self.assertTrue(all(low <= s['length_km'] <= high for s in r['scenarios']))
            self.assertIsNone(r['annual_length_range_km'])
            self.assertFalse(r['physical_axis_admitted'])

    def test_headland_controls_and_original_failed_grid_survive(self):
        directory = estimates.ROOT / 'research/current-length-reference-extents-v4-initial-diagnostic'
        review = json.loads((directory / 'review.json').read_bytes())
        self.assertEqual(sum(review['failed_initial_cases'].values()), 32)
        for name, pin in review['original_sha256'].items():
            self.assertEqual(hashlib.sha256((directory / name).read_bytes()).hexdigest(), pin)
        for r in estimates.build()['records']:
            for i in r.get('fixed_drawing_vertex_indices', []):
                self.assertTrue(all(s['coordinates_lon_lat'][i] == r['coordinates_lon_lat'][i] for s in r['scenarios']))

    def test_phase_and_conditional_extent_are_not_hidden(self):
        rows = {r['entity_id']: r for r in estimates.build()['records']}
        self.assertIn('November', rows['current:east-india-coastal']['source_time_convention'])
        self.assertIn('Southwest', rows['current:monsoon']['source_time_convention'])
        self.assertIn('uncertain', rows['current:east-greenland-coastal']['identity_interpretation'])
        self.assertIn('segment', rows['current:ligurian']['identity_interpretation'])
        self.assertIn('extended', rows['current:loop']['source_time_convention'])


if __name__ == '__main__':
    unittest.main()
