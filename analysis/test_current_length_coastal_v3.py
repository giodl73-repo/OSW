import hashlib
import json
import unittest
import estimate_current_reference_extents_v3 as estimates
import check_current_length_geography_v3 as geography


class CoastalLengths(unittest.TestCase):
    def test_reproducible_complete_grid_and_bound_geography(self):
        document = estimates.build()
        self.assertEqual(document, json.loads((estimates.ROOT / estimates.OUTPUT).read_bytes()))
        report = json.loads((estimates.ROOT / geography.OUTPUT).read_bytes())
        self.assertEqual(report['estimate_file_sha256'], hashlib.sha256((estimates.ROOT / estimates.OUTPUT).read_bytes()).hexdigest())
        self.assertEqual({r['entity_id'] for r in document['records']}, {r['entity_id'] for r in report['records']})
        self.assertEqual(sum(len(r['scenarios']) for r in document['records']), 396)
        self.assertTrue(all(r['all_clear'] and r['scenarios'] == r['coarse_land_clear'] == 36 for r in report['records']))
        for row in document['records']:
            low, high = row['scenario_range_km']
            self.assertTrue(all(low <= s['length_km'] <= high for s in row['scenarios']))
            self.assertIsNone(row['annual_length_range_km'])
            self.assertIsNone(row['uncertainty_km'])
            self.assertFalse(row['physical_axis_admitted'])

    def test_failed_baffin_grid_survives_and_revised_route_is_explicit(self):
        directory = estimates.ROOT / 'research/current-length-reference-extents-v3-initial-diagnostic'
        review = json.loads((directory / 'review.json').read_bytes())
        self.assertEqual(review['failed_initial_cases'], 12)
        for name, pin in review['original_sha256'].items():
            self.assertEqual(hashlib.sha256((directory / name).read_bytes()).hexdigest(), pin)
        row = next(r for r in estimates.build()['records'] if r['entity_id'] == 'current:baffin')
        self.assertEqual(row['coordinates_lon_lat'][-2], [-60.5, 66.8])
        self.assertEqual(len(row['scenarios']), 36)

    def test_short_routes_retain_declared_rounding_and_identity_notes(self):
        rows = {r['entity_id']: r for r in estimates.build()['records']}
        self.assertEqual(rows['current:north-cape']['rounding_km'], 50)
        self.assertEqual(rows['current:spitsbergen-atlantic']['rounding_km'], 50)
        self.assertTrue(rows['current:norwegian']['identity_interpretation'])
        self.assertTrue(rows['current:spitsbergen-atlantic']['identity_interpretation'])
        self.assertIn('Somali', rows['current:east-african-coastal']['identity_interpretation'])


if __name__ == '__main__':
    unittest.main()
