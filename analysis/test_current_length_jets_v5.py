import hashlib
import json
import unittest
import estimate_current_reference_extents_v5 as estimates
import check_current_length_geography_v5 as geography


class JetLengths(unittest.TestCase):
    def test_complete_grid_reproduces_and_geography_is_bound(self):
        document = estimates.build()
        raw = (estimates.ROOT / estimates.OUTPUT).read_bytes()
        self.assertEqual(document, json.loads(raw))
        report = json.loads((estimates.ROOT / geography.OUTPUT).read_bytes())
        self.assertEqual(report['estimate_file_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual({r['entity_id'] for r in document['records']}, {r['entity_id'] for r in report['records']})
        self.assertEqual(sum(len(r['scenarios']) for r in document['records']), 396)
        self.assertTrue(all(r['all_clear'] and r['scenarios'] == r['coarse_land_clear'] == 36 for r in report['records']))
        for r in document['records']:
            low, high = r['scenario_range_km']
            self.assertTrue(all(low <= s['length_km'] <= high for s in r['scenarios']))
            self.assertIsNone(r['annual_length_range_km'])
            self.assertFalse(r['physical_axis_admitted'])

    def test_island_failures_and_explicit_passage_revision_survive(self):
        directory = estimates.ROOT / 'research/current-length-reference-extents-v5-initial-diagnostic'
        review = json.loads((directory / 'review.json').read_bytes())
        self.assertEqual(sum(review['failed_initial_cases'].values()), 30)
        for name, pin in review['original_sha256'].items():
            self.assertEqual(hashlib.sha256((directory / name).read_bytes()).hexdigest(), pin)
        rows = {r['entity_id']: r for r in estimates.build()['records']}
        south = rows['current:pacific-south-subsurface-countercurrent']
        self.assertTrue(all(s['coordinates_lon_lat'][1] == [152, -1.5] for s in south['scenarios']))
        self.assertEqual(rows['current:pacific-south-equatorial-countercurrent']['start_gate_options_lon_lat'], [[163,-9],[165,-9]])

    def test_conditional_endpoints_and_principal_member_convention_are_explicit(self):
        rows = {r['entity_id']: r for r in estimates.build()['records']}
        self.assertIn('working hypothesis', rows['current:atlantic-north-equatorial-undercurrent']['identity_interpretation'])
        self.assertIn('principal member', rows['current:pacific-north-equatorial-undercurrent']['identity_interpretation'])
        self.assertIn('basin-scale extent', rows['current:indian-south-equatorial-undercurrent']['identity_interpretation'])
        self.assertIn('not support extending', rows['current:pacific-north-subsurface-countercurrent']['identity_interpretation'])


if __name__ == '__main__':
    unittest.main()
