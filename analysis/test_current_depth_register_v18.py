"""Protect monthly sample-edge maxima, branch bounds and approximate flow-depth support."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v17 as previous
import build_current_depth_register_v18 as depth


class LocalMonthlyDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][279:]
        cls.rows={r['id']:r for r in cls.new};cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_all_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:279],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':284,'identities_with_scoped_depth_reference':78,'identities_not_yet_assessed':33,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_ngcc_not_undercurrent_or_deep_seasonal_signal(self):
        row=self.rows['ngcc-zhang-2020-upper100-reach'];self.validate(row)
        self.reject(row,[('entity_id','current:new-guinea-coastal-undercurrent'),('approximate_value_m',400),('approximate_value_m',800),('mooring_lon_lat',[142,-1]),('evidence_kind','published_model_climatology')])

    def test_months_directions_and_shallow_edge_maximum(self):
        for tag,month,value,direction,edge in [('february',2,30,'southeastward',True),('august',8,80,'northwestward',False)]:
            row=self.rows['ngcc-zhang-2020-'+tag+'-profile-maximum'];self.validate(row)
            self.assertEqual((row['calendar_months'],row['approximate_value_m']),([month],value))
            self.assertEqual(row['core_definition']['flow_direction'],direction)
            self.assertIs(row['reported_maximum_at_shallowest_retained_bin'],edge)
            self.reject(row,[('calendar_months',[1]),('calendar_source_locator',None),('reported_maximum_at_shallowest_retained_bin',not edge),('approximate_value_m',0),('core_definition',{'kind':'true_core_including_unsampled_surface','flow_direction':direction})])

    def test_record_gaps_processing_and_unobserved_surface_preserved(self):
        for row in self.new[:3]:
            self.reject(row,[('minimum_retained_depth_m',0),('upper_30m_unsampled',False),('data_gap_note',None),('climatology_record_span',{'start_month':'1980-01','end_month':'2018-12'}),('processing','raw_uninterrupted_observations'),('interannual_signal_may_contaminate_monthly_climatology',False)])

    def test_hiri_strict_reach_and_regional_hindcast_scope(self):
        row=self.rows['hiri-wijeratne-2018-australian-branch-reach'];self.validate(row)
        self.assertEqual(row['lower_bound_m'],300)
        self.reject(row,[('lower_bound_operator','>='),('lower_bound_exclusive',False),('lower_bound_m',2000),('model_product','OFES'),('data_assimilation',True),('hindcast_period',{'start_date':'1999-06-01','end_date':'2014-12-31'}),('branch_section_scope','whole_PNG_arc')])

    def test_tasman_observational_support_not_exact_zero_or_uniform_dates(self):
        row=self.rows['tasman-front-sutton-2014-norfolk-extent'];self.validate(row)
        self.assertEqual(row['approximate_value_m'],800)
        self.reject(row,[('exact_zero_depth_observed',True),('processing_reference_depth_m',2000),('approximate_value_m',2000),('exact_uniform_instrument_window',True),('array_sampling_span',{'start_month':'2003-07','end_month':'2003-10'}),('mean_flow_direction_by_nominal_depth',{'500m':'eastward','1000m':'eastward'}),('branch_section_scope','whole_Tasman_Front_route')])

    def test_no_unreviewed_geometry_extrema_or_repeat_claim(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('thickness_m',800),('lower_boundary_m',800),('annual_range_m',[30,80]),('uncertainty_m',50),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_and_source_provenance_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(rows['ngcc-zhang-2020-february-profile-maximum']['reported_maximum_at_shallowest_retained_bin'],'True')
        self.assertEqual(json.loads(rows['tasman-front-sutton-2014-norfolk-extent']['mean_flow_direction_by_nominal_depth'])['500m'],'eastward')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
