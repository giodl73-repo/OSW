import hashlib
import json
import unittest
from pathlib import Path
import estimate_current_reference_extents_v2 as estimates
import check_current_length_geography_v2 as geography


class BasinLengths(unittest.TestCase):
    def test_dateline_uses_short_route_and_continuous_geography(self):
        points=geography.dense([[170,0],[-170,0]])
        self.assertAlmostEqual(estimates.length([[170,0],[-170,0]]),2226.389816,places=4)
        self.assertGreaterEqual(min(p[0] for p in points),170)
        self.assertLessEqual(max(p[0] for p in points),190)
        self.assertTrue(all(abs(a[0]-b[0])<1 for a,b in zip(points,points[1:])))

    def test_all_declared_scenarios_and_geographic_owners_are_retained(self):
        document=estimates.build();saved=json.loads((estimates.ROOT/estimates.OUTPUT).read_bytes())
        self.assertEqual(document,saved)
        report=json.loads((geography.ROOT/geography.OUTPUT).read_bytes())
        self.assertEqual(report['estimate_file_sha256'],hashlib.sha256((estimates.ROOT/estimates.OUTPUT).read_bytes()).hexdigest())
        self.assertEqual({r['entity_id'] for r in document['records']},{r['entity_id'] for r in report['records']})
        self.assertEqual(sum(len(r['scenarios']) for r in document['records']),216)
        self.assertTrue(all(r['all_clear'] and r['scenarios']==r['coarse_land_clear']==36 for r in report['records']))
        for row in document['records']:
            low,high=row['scenario_range_km'];self.assertTrue(all(low<=x['length_km']<=high for x in row['scenarios']))
            self.assertIsNone(row['annual_length_range_km']);self.assertIsNone(row['uncertainty_km'])

    def test_geographic_control_is_explicit_and_failed_initial_cases_survive(self):
        row=next(r for r in estimates.build()['records'] if r['entity_id']=='current:pacific-south-equatorial')
        self.assertEqual(row['fixed_drawing_vertex_indices'],[5])
        self.assertTrue(all(s['coordinates_lon_lat'][5]==[162,-12] for s in row['scenarios']))
        initial=Path(estimates.ROOT/'research/current-length-reference-extents-v2-initial-diagnostic')
        review=json.loads((initial/'review.json').read_bytes())
        self.assertEqual(review['failed_case_indices'],[8,17,26,35])
        for path,pin in review['original_sha256'].items():self.assertEqual(hashlib.sha256((initial/path).read_bytes()).hexdigest(),pin)
        necc=next(r for r in estimates.build()['records'] if r['entity_id']=='current:pacific-north-equatorial-countercurrent')
        self.assertIn('February',necc['source_time_convention']);self.assertIn('88E',necc['source_typography_note'])


if __name__=='__main__':unittest.main()
