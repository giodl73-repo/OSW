"""Check partial reach, array support, instrument limits and classification depth."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v12 as previous
import build_current_depth_register_v13 as depth


class BranchReachTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][145:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,original,changes):
        for field,value in changes:
            row=copy.deepcopy(original);row[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.validate(row)

    def test_prior_145_references_and_all_identities_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:145],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':150,'identities_with_scoped_depth_reference':64,'identities_not_yet_assessed':47,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_antarctic_offshore_branch_strict_bound_not_bank_depth(self):
        row=self.rows['antarctic-slope-dong-2016-deep-branch-below1000']
        self.assertEqual(row['lower_bound_m'],1000);self.assertTrue(row['lower_bound_exclusive'])
        self.reject(row,[('lower_bound_operator','>='),('lower_bound_exclusive',False),('approximate_value_m',1000),('source_branch','shallow_bank_crossing_branch'),('branch_section_scope','whole_current'),('section_sampling_month','2008-02')])

    def test_northern_nec_sampling_limit_is_not_detected_bottom(self):
        row=self.rows['pacific-nec-schonau-2015-northern-reach1000']
        self.assertEqual(row['approximate_value_m'],1000);self.assertFalse(row['sampling_limit_is_flow_boundary'])
        self.assertEqual(row['section_latitude_band_degrees_north'],[14,16])
        self.reject(row,[('sampling_limit_is_flow_boundary',True),('approximate_value_m',500),('sampling_limit_m',2000),('section_latitude_band_degrees_north',[8.5,16.5]),('entity_id','current:north-equatorial'),('velocity_reconstruction','direct_ADCP')])

    def test_pacific_array_mean_not_longer_nearby_moorings_or_composites(self):
        for tag in ['necc','northern-sec']:
            row=self.rows['pacific-'+tag+'-song-2019-142e-mean']
            self.assertEqual(row['averaging_month_window'],{'start_month':'2014-08','end_month':'2015-11'})
            self.reject(row,[('section_longitude_degrees_east',140),('averaging_month_window',{'start_month':'2014-01','end_month':'2018-12'}),('processing','MJO_event_composite')])

    def test_necc_upper_bound_and_sec_partial_latitude_scope(self):
        necc=self.rows['pacific-necc-song-2019-142e-mean'];sec=self.rows['pacific-northern-sec-song-2019-142e-mean']
        self.assertEqual(necc['upper_bound_m'],200);self.assertTrue(necc['upper_bound_exclusive'])
        self.reject(necc,[('upper_bound_exclusive',False),('approximate_value_m',200),('upper_boundary_m',60),('entity_id','current:north-equatorial-countercurrent')])
        self.assertEqual(sec['approximate_value_m'],150);self.assertEqual(sec['source_branch'],'northern_equatorial_component')
        self.reject(sec,[('branch_section_scope','whole_current'),('section_latitude_band_degrees_north',[-10,2]),('entity_id','current:south-equatorial')])

    def test_south_java_definition_not_underlying_current_or_model_period(self):
        row=self.rows['south-java-ningsih-2021-surface-current-definition']
        self.assertEqual(row['approximate_value_m'],150);self.assertEqual(row['evidence_kind'],'published_literature_definition')
        self.reject(row,[('approximate_value_m',800),('approximate_value_m',1000),('depth_basis','observed_no_flow_boundary'),('evidence_kind','published_model_climatology'),('climatology_years',[1950,2013]),('calendar_months',[12,1,2])])

    def test_scoped_references_cannot_promote_whole_flow_or_playback(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('metric','lower_flow_boundary_depth'),('thickness_m',1000),('uncertainty_m',50),('annual_range_m',[150,1000]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('same_source_width_reference_id','unreviewed-width'),('independent_observation_count_claimed',True)])

    def test_source_facts_json_and_csv_reproduce_without_duplicate_columns(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());self.assertEqual(len(self.new),5)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        columns=next(csv.reader(io.StringIO(depth.csv_bytes(self.data).decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        self.assertEqual(rows['pacific-nec-schonau-2015-northern-reach1000']['sampling_limit_m'],'1000')
        self.assertEqual(rows['south-java-ningsih-2021-surface-current-definition']['depth_basis'],'source_current_classification_convention')


if __name__=='__main__':unittest.main()
