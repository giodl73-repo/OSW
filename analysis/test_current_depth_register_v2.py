"""Verify typed source quantities without promoting them into physical volumes."""
import copy
import json
import unittest
import build_current_depth_register_v1 as legacy
import build_current_depth_register_v2 as depth


class DepthBatchTwoTests(unittest.TestCase):
    def setUp(self):
        self.data=depth.build()
        self.rows={r['id']:r for r in self.data['evidence']}
        self.identities={r['entity_id'] for r in self.data['records']}
        self.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']
        self.sample=self.rows['indian-euc-siswanto-2019-march-2017-flow-band']

    def validate(self,row):depth.validate_reference(row,self.identities,self.metrics)

    def test_all_identities_and_entire_previous_evidence_preserved(self):
        prior=legacy.build()
        self.assertEqual(self.data['evidence'][:4],prior['evidence'])
        self.assertEqual(self.identities,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':17,'identities_with_scoped_depth_reference':8,'identities_not_yet_assessed':103,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertTrue(self.data['previous_evidence_preserved'])

    def test_saved_json_csv_and_raw_source_records_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.data['evidence'][4:]:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})

    def test_layer_and_core_location_ranges_have_no_invented_midpoints(self):
        self.assertEqual(self.sample['range_m'],[80,150])
        self.assertIsNone(self.sample['approximate_value_m'])
        atl=self.rows['atlantic-seuc-molinari-1981-core-depth-range']
        self.assertEqual(atl['metric'],'core_depth');self.assertEqual(atl['range_m'],[150,200])
        for key,value in [('approximate_value_m',115),('range_m',[150,80]),('range_interpretation',None)]:
            row=copy.deepcopy(self.sample);row[key]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_deep_reach_bounds_remain_strict_and_have_no_points(self):
        for id,bound in [('atlantic-seuc-molinari-1981-deep-core-bound',300),('indian-seuc-chen-2022-climatological-deep-reach-bound',2000)]:
            row=self.rows[id]
            self.assertEqual(row['lower_bound_m'],bound);self.assertTrue(row['lower_bound_exclusive']);self.assertIsNone(row['approximate_value_m'])
            changed=copy.deepcopy(row);changed['lower_bound_exclusive']=False
            with self.assertRaises(ValueError):self.validate(changed)

    def test_model_core_thickness_retains_longitude_and_aggregation(self):
        east=self.rows['indian-seuc-chen-2022-core-thickness-east-minimum']
        center=self.rows['indian-seuc-chen-2022-core-thickness-central-maximum']
        median=self.rows['indian-seuc-chen-2022-core-thickness-longitude-median']
        self.assertEqual([east['approximate_value_m'],center['approximate_value_m'],median['approximate_value_m']],[57,1719,1025])
        self.assertIn('95 E',east['geographic_scope']);self.assertIn('74 E',center['geographic_scope'])
        self.assertEqual(median['aggregation_statistic'],'median_across_longitudes')
        self.assertEqual(len({r['source_case_id'] for r in [east,center,median]}),1)
        for key,value in [('velocity_threshold_operator','>='),('model_product',None),('aggregation_statistic',None)]:
            row=copy.deepcopy(median);row[key]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_paired_geometry_uncertainty_and_physical_volume_remain_unresolved(self):
        for key,value in [('upper_boundary_m',80),('lower_boundary_m',150),('thickness_m',70),('uncertainty_m',7),('volume_eligible',True),('physical_state_join_eligible',True),('whole_current_representative',True)]:
            row=copy.deepcopy(self.sample);row[key]=value
            with self.assertRaises(ValueError):self.validate(row)
        for row in self.data['records']:self.assertIsNone(row['volume_km3'])

    def test_seasons_require_explicit_calendar_and_do_not_make_annual_extrema(self):
        row=copy.deepcopy(self.sample);row['calendar_months']=[3]
        with self.assertRaises(ValueError):self.validate(row)
        for id in ['indian-euc-siswanto-2019-winter-core-depth','indian-euc-siswanto-2019-spring-core-depth']:
            self.assertIsNone(self.rows[id]['calendar_months'])
        for key,value in [('annual_range_m',[50,100]),('seasonal_playback_eligible',True),('annual_extrema_eligible',True)]:
            row=copy.deepcopy(self.sample);row[key]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_invalid_values_pressure_and_unknown_identity_rejected(self):
        for key,value in [('range_m',[False,150]),('range_m',[80,float('inf')]),('unit','dbar'),('entity_id','current:unverified-child'),('metric','bathymetry')]:
            row=copy.deepcopy(self.sample);row[key]=value
            with self.assertRaises(ValueError):self.validate(row)


if __name__=='__main__':unittest.main()
