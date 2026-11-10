"""Check approximate presence depth versus regional extent interval and references."""
import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_register_v30 as previous
import build_current_depth_register_v31 as depth


class SouthPacificDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.west,cls.east=cls.data['evidence'][316:]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k,value=v),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_references_and_owner_coverage(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:316],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':318,'identities_with_scoped_depth_reference':100,'identities_not_yet_assessed':11,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.validate(self.west);self.validate(self.east)

    def test_nearly500_is_not_a_rounded_inclusive_bound_or_bottom(self):
        self.assertEqual(self.west['approximate_value_m'],500)
        self.assertIsNone(self.west['lower_bound_m'])
        self.reject(self.west,[('lower_bound_m',500),('source_depth_phrase','at_least_500m'),('depth_basis','exact_detected_bottom'),('metric','lower_flow_boundary_depth'),('source_speed_context_cm_s',7),('approximate_value_m',800),('approximate_value_m',1000),('approximate_value_m',1500)])

    def test_eastern_extent_interval_not_occupied_layer_or_eddy_depth(self):
        self.assertEqual(self.east['range_m'],[200,300])
        self.reject(self.east,[('range_m',[0,300]),('approximate_value_m',800),('range_m',[780,1510]),('upper_boundary_m',200),('lower_boundary_m',300),('thickness_m',100),('metric','reported_vertical_thickness'),('source_section_id','q2'),('section_nominal_longitude_degrees_east',-83)])

    def test_regions_and_years_not_a_seasonal_pair_or_precise_axis(self):
        self.assertEqual([self.west['section_sampling_month'],self.east['section_sampling_month']],['1990-03','1968-07'])
        self.reject(self.west,[('section_sampling_month','1978-09'),('source_research_vessel','Knorr'),('section_nominal_longitude_degrees_east',-135),('source_STF_bracketing_latitude_range_degrees_north',[-36,-35])])
        self.reject(self.east,[('section_sampling_month','1990-07'),('phase_label','late_austral_summer'),('source_research_vessel','Baldrige')])
        for row in [self.west,self.east]:
            self.reject(row,[('calendar_months',[3,7]),('climatology_years',[1968,1990]),('section_latitude_degrees_north',-35),('annual_range_m',[200,500]),('temporal_operator','paired_seasonal_climatology')])

    def test_processing_references_remain_case_specific(self):
        reference=self.west['geostrophic_reference_definition']
        self.assertEqual(reference['source_table_depth_range_m'],[1800,1840])
        self.reject(self.west,[('geostrophic_reference_definition',{'kind':'constant_depth','depth_m':3500}),('geostrophic_reference_definition',dict(reference,sigma_2_kg_m3=45.82))])
        self.reject(self.east,[('source_table2_reference_flag','observed_flow_bottom'),('source_table2_reference_depth_summary_m',[1800,1840]),('figure5_reference_policy','constant_250m_for_entire_section')])

    def test_no_incompatible_width_or_whole_geometry_admission(self):
        for row in [self.west,self.east]:
            self.reject(row,[('uncertainty_m',100),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','SPC_less_than_200km'),('independent_observation_count_claimed',True)])

    def test_json_csv_source_and_frozen_member_lookup_preserved(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(json.loads(rows[self.west['id']]['geostrophic_reference_definition']),self.west['geostrophic_reference_definition'])
        self.assertEqual(json.loads(rows[self.east['id']]['range_m']),[200,300])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());review=source['source_reviews'][0]
        self.assertTrue(review['actual_original_pixels_viewed']);self.assertEqual(review['actual_reviewed_pages'],[2,3,6,7,10])
        index=json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes())
        self.assertEqual(hashlib.sha256((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes()).hexdigest(),source['retained_member_index']['sha256'])
        self.assertEqual(index['depth_register_file'],'research/current-depth-register-v30.json')
        refs={r['id']:r for r in self.data['evidence']}
        for parent in index['records']:
            for member in parent['members']:
                self.assertNotEqual(member['entity_id'],'current:south-pacific')
                for reference_id in member['depth_reference_ids']:self.assertEqual(refs[reference_id]['entity_id'],member['entity_id'])
        for row in [self.west,self.east]:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
