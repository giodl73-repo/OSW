import hashlib
import json
import unittest
import estimate_current_reference_extents_v7 as estimates
import check_current_length_geography_v7 as geography
import check_current_length_geography_v2 as spatial
import build_current_length_register_v1 as register


class FinalRouteLengths(unittest.TestCase):
    def test_all_final_grids_reproduce_and_exact_geography_is_bound(self):
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
            self.assertIsNone(r['uncertainty_km'])
            self.assertFalse(r['physical_axis_admitted'])

    def test_circuit_is_closed_exactly_once_and_failed_revisions_survive(self):
        row = next(r for r in estimates.build()['records'] if r['entity_id']=='current:antarctic-coastal')
        for scenario in row['scenarios']:
            points = scenario['coordinates_lon_lat']
            self.assertEqual(points[0], points[-1])
            unwrapped = spatial.dense(points)
            self.assertAlmostEqual(unwrapped[-1][0]-unwrapped[0][0], -360)
        for suffix, failures in [('initial', 114), ('revision1', 16)]:
            directory = estimates.ROOT / f'research/current-length-reference-extents-v7-{suffix}-diagnostic'
            review = json.loads((directory/'review.json').read_bytes())
            counts = review['failed_initial_cases']
            self.assertEqual(sum(counts.values()) if isinstance(counts,dict) else counts, failures)
            for name,pin in review['original_sha256'].items():
                self.assertEqual(hashlib.sha256((directory/name).read_bytes()).hexdigest(),pin)

    def test_complete_inventory_keeps_reported_hypothesis_separate(self):
        document = register.build();rows={r['entity_id']:r for r in document['records']}
        self.assertEqual(len(rows),111)
        self.assertTrue(all(r['length_estimate_km']>0 and not r['needs_full_extent_estimate'] for r in rows.values()))
        proposed=rows['current:greenland-middle-atlantic-shelf-hypothesis']
        self.assertEqual(proposed['length_estimate_km'],5000)
        self.assertEqual(proposed['status'],'reported_hypothesis')
        self.assertEqual(proposed['method'],'source_reported_hypothesis')
        self.assertTrue(proposed['conditional_extent'])
        self.assertIn('hypothesizes',proposed['scope'])
        self.assertEqual(sum(r['status']=='reported' for r in rows.values()),13)
        source=json.loads((register.ROOT/'research/ocean-current-live-measurements.json').read_bytes())
        for r in source['length_assessments']:
            if r.get('published_length_km') is not None:
                self.assertEqual(rows[r['entity_id']]['length_estimate_km'],r['published_length_km'])


if __name__=='__main__':
    unittest.main()
