import ast
import hashlib
import json
from pathlib import Path
import unittest
import sample_atlantic_current_depth_v1 as frozen
import sample_atlantic_current_depth_v2 as current


class AtlanticSecondBatchContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((current.ROOT/current.OPERATOR).read_bytes())

    def test_three_exact_owners_original_route_counts_and_case_budget(self):
        self.assertEqual([(r['current_id'],r['expected_route_vertices']) for r in self.op['currents']],[('north-brazil',7),('north-atlantic',6),('labrador',9)])
        self.assertEqual(len(self.op['snapshot_times_utc'])*sum(r['expected_route_vertices'] for r in self.op['currents']),44)
        self.assertEqual(self.op['normal_offsets_km'],[-40,-20,0,20,40])
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])

    def test_current_specific_primary_thresholds_and_scope_are_explicit(self):
        for case in self.op['currents']:
            self.assertEqual(case['primary_threshold_m_s'],.1 if case['current_id']=='north-brazil' else .05)
            self.assertEqual(case['thresholds_m_s'],[.05,.1,.2]);self.assertEqual(case['core_search_depth_interval_m'],[0,200])
            self.assertTrue(case['scope']);self.assertIn('Exploratory OSW',case['threshold_basis'])
        self.assertFalse(any(self.op['eligibility'].values()))

    def test_frozen_pure_helpers_are_reused_exactly(self):
        for name in ['wrapped_longitude','nearest_longitude_index','route_context','diagnoses','validate_retained']:
            self.assertIs(getattr(current,name),getattr(frozen,name))

    def test_retrieval_main_changes_only_output_schema_versions(self):
        old=Path(frozen.__file__).read_text(encoding='utf8');new=Path(current.__file__).read_text(encoding='utf8')
        new=new.replace('osw.atlantic-current-depth-candidate.v2','osw.atlantic-current-depth-candidate.v1').replace('osw.atlantic-current-depth-manifest.v2','osw.atlantic-current-depth-manifest.v1')
        main=lambda code:next(n for n in ast.parse(code).body if isinstance(n,ast.FunctionDef) and n.name=='main')
        self.assertEqual(ast.dump(main(old)),ast.dump(main(new)))

    def test_real_routes_keep_source_order_distances_and_owners(self):
        for case in self.op['currents']:
            route=json.loads((current.ROOT/case['route_file']).read_bytes())
            points,distances,bearings=current.route_context(route,case)
            self.assertEqual(points,route['coordinates_lon_lat']);self.assertEqual(len(points),case['expected_route_vertices'])
            self.assertTrue(all(a<b for a,b in zip(distances,distances[1:])))
            self.assertEqual(len(bearings),len(points));self.assertTrue(all(-180<=p[0]<0 for p in points))

    def test_direct_inputs_are_frozen_and_prior_source_reviews_retained(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((current.ROOT/f).read_bytes()).hexdigest(),pin)
        self.assertEqual(self.op['maximum_total_cell_pairs'],250000);self.assertEqual(self.op['maximum_total_decoded_velocity_bytes'],7000000)
        self.assertIn('research/atlantic-current-depth-source-review-v1.json',self.op['input_sha256'])


if __name__=='__main__':unittest.main()
