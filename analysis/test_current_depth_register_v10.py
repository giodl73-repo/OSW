"""Verify censored reach, partial seasonal branches and spatial depth variation."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v9 as previous
import build_current_depth_register_v10 as depth


class CoastalDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][119:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,original,changes):
        for field,value in changes:
            row=copy.deepcopy(original);row[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.validate(row)

    def test_prior_evidence_and_full_inventory_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:119],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':124,'identities_with_scoped_depth_reference':51,'identities_not_yet_assessed':60,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_censored_zeehan_reach_does_not_become_bottom(self):
        row=self.rows['zeehan-cresswell-2000-dec1997-below300']
        self.assertEqual(row['lower_bound_m'],300);self.assertTrue(row['lower_bound_exclusive'])
        self.assertEqual(row['section_sampling_month'],'1997-12');self.assertIsNone(row['approximate_value_m'])
        self.reject(row,[('lower_bound_exclusive',False),('lower_bound_operator','>='),('approximate_value_m',300),('lower_boundary_m',300),('sampling_limit_is_flow_boundary',True),('section_sampling_month','1997-03')])

    def test_winter_branch_not_all_seasons_or_neighboring_current(self):
        row=self.rows['monsoon-anutaliya-2022-winter-branch-reach']
        self.assertEqual(row['approximate_value_m'],1000);self.assertEqual(row['calendar_months'],[11,12,1,2])
        self.reject(row,[('entity_id','current:east-india-coastal'),('source_branch','summer_monsoon_current'),('branch_section_scope','whole_current'),('calendar_months',[6,7,8]),('calendar_source_locator',None),('section_sampling_month','2015-01'),('campaign_window',{'start_month':'2015-01','end_month':'2015-12'})])

    def test_meander_layer_thickness_is_not_current_or_eddy_bottom(self):
        row=self.rows['algerian-taupier-letage-2003-meander-aw-thickness']
        self.assertEqual(row['metric'],'reported_vertical_thickness');self.assertEqual(row['vertical_datum'],'not_applicable_thickness_distance')
        self.reject(row,[('metric','lower_flow_boundary_depth'),('vertical_datum','local_sea_surface_positive_down'),('approximate_value_m',2800),('branch_section_scope','developed_algerian_eddy'),('section_sampling_month','1997-07')])

    def test_wicc_regional_variation_keeps_campaign_precision_and_access(self):
        for tag,lat,value in [('southern',10,200),('northern',22,400)]:
            row=self.rows['wicc-shetye-1991-'+tag+'-winter-reach']
            self.assertEqual(row['approximate_value_m'],value);self.assertEqual(row['section_latitude_degrees_north'],lat)
            self.assertEqual(row['campaign_window'],{'start_month':'1987-12','end_month':'1988-01'})
            self.reject(row,[('section_latitude_degrees_north',22 if lat==10 else 10),('source_access_scope','full_original_article'),('section_sampling_month','1988-01'),('window_role','exact_section_occupation'),('annual_range_m',[200,400])])

    def test_no_unreviewed_geometry_uncertainty_or_playback(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('thickness_m',200),('uncertainty_m',20),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('whole_current_representative',True),('same_source_width_reference_id','unreviewed-width'),('independent_observation_count_claimed',True)])

    def test_source_facts_json_and_csv_reproduce(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(len(self.new),5)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        self.assertEqual(rows['zeehan-cresswell-2000-dec1997-below300']['lower_bound_operator'],'>')
        self.assertEqual(rows['monsoon-anutaliya-2022-winter-branch-reach']['source_branch'],'winter_monsoon_current')
        self.assertEqual(rows['wicc-shetye-1991-northern-winter-reach']['source_access_scope'],'primary_publisher_abstract')


if __name__=='__main__':unittest.main()
