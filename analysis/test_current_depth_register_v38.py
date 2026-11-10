"""Keep calculated monthly descriptors distinct from physical boundaries."""
import copy
import csv
import io
import json
import math
import unittest
import build_current_depth_register_v37 as previous
import build_current_depth_register_v38 as depth


class MonthlyCalculatedDescriptorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][333:]
        cls.candidate=json.loads((depth.ROOT/'research/source-data/leeuwin-seasonal-depth-v1/seasonal-candidate.json').read_bytes())
        cls.ids={r['entity_id'] for r in cls.data['records']};cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(key=k),self.assertRaises(ValueError):
                depth.validate_reference(changed,self.ids,self.metrics);depth.validate_context(changed)

    def test_prior333_references_and_scope_preserved(self):
        self.assertEqual(self.data['evidence'][:333],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':342,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.data['metadata_correction_count'],3)

    def test_monthly_scalar_is_rounded_calculated_crossing_with_real_sign_bracket(self):
        self.assertEqual([(r['calendar_months'][0],r['approximate_value_m']) for r in self.rows],[(1,280),(2,320),(4,270),(5,290),(6,290),(7,320),(9,240),(10,290),(12,300)])
        for row in self.rows:
            p=next(p for p in self.candidate['profiles'] if p['id']==row['derived_profile_id'])
            self.assertEqual(p['calendar_months'],row['calendar_months'])
            a,b=row['interpolation_bracket_m'];i=p['depth_levels_m'].index(a)
            self.assertEqual(p['depth_levels_m'][i+1],b)
            va,vb=p['mean_along_velocity_m_s'][i:i+2];self.assertLess(va,0);self.assertGreaterEqual(vb,0)
            computed=a-va*(b-a)/(vb-va)
            self.assertAlmostEqual(computed,row['computed_zero_crossing_depth_m'],places=10)
            self.assertEqual(row['approximate_value_m'],10*math.floor(computed/10+.5))

    def test_source_product_flags_period_and_rotation_not_changed_to_paper_reproduction(self):
        for row in self.rows:
            self.assertEqual(row['source_record_period'],{'start':'2011-08-01','end':'2023-05-01','daily_records':4292})
            self.assertEqual(row['source_accepted_quality_flags'],[1,2,3,4])
            self.reject(row,[('local_along_mean_bearing_degrees_true',332),('source_accepted_quality_flags',[1]),('evidence_kind','published_observational_climatology'),('calculated_descriptor_not_published_depth',False),('source_record_period',{'start':'2010-01-01','end':'2023-05-31'})])

    def test_new_metric_does_not_become_full_flow_bottom_or_uncertainty(self):
        for row in self.rows:
            self.assertEqual(row['metric'],'derived_mean_velocity_zero_crossing_depth')
            self.reject(row,[('metric','lower_flow_boundary_depth'),('lower_boundary_m',row['approximate_value_m']),('thickness_m',row['approximate_value_m']),('uncertainty_m',5),('annual_range_m',[240,320]),('volume_eligible',True),('seasonal_playback_eligible',True),('reference_route_projection_eligible',True),('independent_observation_count_claimed',True)])

    def test_unresolved_months_are_unknown_not_the475m_sampling_limit(self):
        series=json.loads((depth.ROOT/'research/leeuwin-monthly-depth-descriptors-v1.json').read_bytes())
        self.assertEqual(series['counts'],{'calendar_months':12,'supported_local_descriptors':9,'unknown_boundary_depths':3})
        unknown=[p for p in series['months'] if p['depth_reference_id'] is None]
        self.assertEqual([p['month'] for p in unknown],[3,8,11])
        for p in unknown:self.assertIsNone(p['display_depth_m']);self.assertFalse(p['sampling_limit_is_boundary'])
        self.assertIsNone(series['annual_depth_range_m']);self.assertFalse(series['seasonal_interpolation_performed'])

    def test_near_halt_diagnostic_not_mistaken_for_strict_reversal(self):
        sensitivity=json.loads((depth.ROOT/'research/source-data/leeuwin-seasonal-depth-v1/sensitivity-v1.json').read_bytes())
        phase=next(p for p in sensitivity['profiles'] if p['phase_id']=='phase_2_3')
        self.assertEqual(len(phase['methods']),4)
        for method in phase['methods']:
            self.assertIsNone(method['strict_zero_crossing']['boundary_depth_m'])
            for peak in method['negative_local_velocity_maxima']:
                self.assertFalse(peak['is_flow_boundary']);self.assertLess(peak['velocity_m_s'],0)

    def test_member_index_unchanged_and_no_leeuwin_inheritance(self):
        index=json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes())
        self.assertEqual(index['counts']['distinct_member_depth_references'],47)
        for row in index['records']:self.assertNotIn('current:leeuwin',[m['entity_id'] for m in row['members']])

    def test_json_csv_reproduce_with_computational_and_display_quantities_separate(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-9:]
        for row,out in zip(self.rows,rows):
            self.assertEqual(float(out['computed_zero_crossing_depth_m']),row['computed_zero_crossing_depth_m'])
            self.assertEqual(json.loads(out['source_accepted_quality_flags']),[1,2,3,4])
            self.assertEqual(out['derived_profile_id'],row['derived_profile_id'])


if __name__=='__main__':unittest.main()
