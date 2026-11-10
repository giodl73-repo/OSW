"""Verify partial-strait cores and avoid treating transport zeros as physical geometry."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v13 as previous
import build_current_depth_register_v14 as depth


class StraitAndTransportDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][150:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,original,changes):
        for field,value in changes:
            row=copy.deepcopy(original);row[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.validate(row)

    def test_prior_150_references_and_all_identities_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:150],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':157,'identities_with_scoped_depth_reference':67,'identities_not_yet_assessed':44,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_itf_observed_mean_retains_partial_strait_and_caption_years(self):
        row=self.rows['itf-jiang-2019-makassar-observed-mean-core']
        self.assertEqual(row['approximate_value_m'],100);self.assertEqual(row['averaging_years'],[2004,2012]);self.assertEqual(row['observing_record_span_years'],[2004,2017])
        self.reject(row,[('averaging_years',[2004,2017]),('averaging_source_locator',None),('reference_dataset','SODA'),('approximate_value_m',200),('source_branch','all_straits'),('branch_section_scope','whole_current'),('core_definition',{'kind':'salinity_maximum'})])

    def test_egcc_snapshot_not_bathymetry_or_offshore_current(self):
        row=self.rows['egcc-bacon-2002-aug1997-reach']
        self.assertEqual(row['approximate_value_m'],100);self.assertEqual(row['section_sampling_month'],'1997-08')
        self.reject(row,[('approximate_value_m',160),('entity_id','current:east-greenland'),('source_access_scope','original_full_paper_pixels'),('section_sampling_month','2002-07')])

    def test_arc_integration_limit_does_not_claim_total_extent(self):
        row=self.rows['agulhas-return-lutjeharms-2007-transport-depth']
        self.assertEqual(row['approximate_value_m'],1500);self.assertEqual(row['metric'],'transport_selected_depth_extent')
        self.assertFalse(row['source_total_vertical_extent_established'])
        self.reject(row,[('metric','reported_vertical_extent'),('depth_basis','physical_flow_bottom'),('source_total_vertical_extent_established',True),('section_sampling_month','2007-01')])

    def test_agulhas_zero_transport_depths_keep_regional_sections(self):
        for tag,name,latitude,value in [('rb','Richards Bay',-30,1500),('ps','Port Shepstone',-32,3100),('el','East London',-34,1900),('pe','Port Elizabeth',-36,3500)]:
            row=self.rows['agulhas-casal-2009-'+tag+'-zero-net-transport-depth']
            self.assertEqual((row['section_name'],row['section_latitude_degrees_north'],row['approximate_value_m']),(name,latitude,value))
            self.assertEqual(row['metric'],'net_section_transport_zero_depth')
            self.reject(row,[('metric','lower_flow_boundary_depth'),('metric','reported_vertical_extent'),('depth_basis','pointwise_zero_velocity'),('section_latitude_degrees_north',-31),('window_role','exact_section_occupation'),('section_sampling_month','2003-02')])

    def test_transport_diagnostic_retains_section_specific_eddy_treatment(self):
        row=self.rows['agulhas-casal-2009-pe-zero-net-transport-depth']
        changed=copy.deepcopy(row);changed['diagnostic_definition']['section_exception']='no_eddy_cancellation'
        with self.assertRaises(ValueError):self.validate(changed)
        changed=copy.deepcopy(row);changed['diagnostic_definition']['kind']='zero_velocity_at_every_lateral_point'
        with self.assertRaises(ValueError):self.validate(changed)
        self.reject(row,[('velocity_reconstruction','unreferenced_geostrophy')])

    def test_no_geometry_uncertainty_or_annual_promotion(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('lower_boundary_m',row['approximate_value_m']),('thickness_m',row['approximate_value_m']),('uncertainty_m',50),('annual_range_m',[1500,3500]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('same_source_width_reference_id','unreviewed-width'),('independent_observation_count_claimed',True)])

    def test_source_facts_json_and_csv_reproduce_without_duplicate_columns(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());self.assertEqual(len(self.new),7)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        columns=next(csv.reader(io.StringIO(depth.csv_bytes(self.data).decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        row=rows['agulhas-casal-2009-el-zero-net-transport-depth']
        self.assertEqual(json.loads(row['diagnostic_definition'])['section_exception'],'weak_deep_flows_within_error_bars_excluded')
        self.assertEqual(rows['itf-jiang-2019-makassar-observed-mean-core']['averaging_years'],'[2004,2012]')


if __name__=='__main__':unittest.main()
