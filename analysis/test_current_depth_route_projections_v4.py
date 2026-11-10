"""Guard model-only core interpolation and nominal section geometry."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_route_projections_v3 as previous
import build_current_depth_route_projections_v4 as depth


class AtlanticEUCModelConnectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.p=cls.data['projections'][-1]
        cls.operator=json.loads((depth.ROOT/depth.OPERATOR).read_bytes());cls.case=cls.operator['case']
        cls.source=json.loads((depth.ROOT/cls.operator['depth_register_file']).read_bytes());cls.refs={r['id']:r for r in cls.source['evidence']}

    def test_previous_five_preserved_and_six_catalog_profiles(self):
        self.assertEqual(self.data['projections'][:5],previous.build()['projections'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':6,'identities_not_yet_projected':105,'regional_projection_scenarios':6,'source_anchor_references':16,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0})
        for record,source in zip(self.data['records'],self.source['records']):self.assertEqual(record['depth_reference_ids'],source['depth_reference_ids'])

    def test_only_matching_flame70_and50_levels_in_connector(self):
        self.assertEqual([a['approximate_depth_descriptor_m'] for a in self.p['anchors']],[70,50])
        self.assertEqual([a['nominal_lon_lat'] for a in self.p['anchors']],[[-35,0],[-10,0]])
        used=set(self.p['source_reference_ids']);excluded=set(self.p['excluded_comparison_reference_ids'])
        self.assertFalse(used.intersection(excluded));self.assertEqual(len(excluded),2)
        for ref in used:self.assertEqual(self.refs[ref]['model_product'],'FLAME_Hormann2007')

    def test_observed_and_spinup_or_wrong_hindcast_period_rejected(self):
        ref_id=self.case['anchors'][0]['reference_id']
        for key,value in [('model_product','SPFLAME_Hormann2007'),('model_product',None),('evidence_kind','published_observed_mean_section'),('model_time_basis',{'kind':'repeating_ECMWF_climatological_forcing','analysis_window':'last_two_spinup_years'}),('approximate_value_m',100)]:
            refs=copy.deepcopy(self.refs);refs[ref_id][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):depth.validate_case(self.case,refs)

    def test_connector25_degrees_is_not_exact_off_equatorial_core_axis(self):
        self.assertAlmostEqual(self.p['route_length_km'],2782.987,places=3)
        self.assertEqual(self.p['geometry_role'],'nominal_equatorial_section_connector_not_exact_core_axis')
        for anchor in self.p['anchors']:
            self.assertIsNone(anchor['exact_core_latitude_degrees_north'])
            self.assertEqual(anchor['source_core_latitude_relation'],'slightly_south_of_equator_exact_latitude_not_reported')
        ref_id=self.case['anchors'][0]['reference_id'];refs=copy.deepcopy(self.refs);refs[ref_id]['section_latitude_degrees_north']=0
        with self.assertRaises(ValueError):depth.validate_case(self.case,refs)

    def test_source_anchors_and_assumed_intermediate_values_keep_status(self):
        samples=self.p['samples'];self.assertEqual(samples[0]['projected_depth_descriptor_m'],70);self.assertEqual(samples[-1]['projected_depth_descriptor_m'],50)
        self.assertEqual(len([s for s in samples if s['status']=='source_model_mean_anchor_at_nominal_section']),2)
        for sample in samples:
            self.assertTrue(50<=sample['projected_depth_descriptor_m']<=70)
            self.assertEqual(sample['model_output_years'],[1990,2002])
            if sample['status'].startswith('assumed_'):self.assertEqual(sample['source_reference_ids'],self.p['source_reference_ids'])

    def test_mean_model_period_does_not_admit_physical_thickness_or_annual_range(self):
        self.assertEqual(self.p['model_time_basis'],{'kind':'interannually_forced_hindcast_monthly_mean','output_years':[1990,2002]})
        self.assertFalse(any(self.p['eligibility'].values()))
        for key in ['observed_common_record_period','campaign_window','physical_thickness_profile','physical_lower_boundary_profile','volume_km3','annual_depth_range_m','calendar_months']:self.assertIsNone(self.p[key])
        for sample in self.p['samples']:self.assertIsNone(sample['depth_uncertainty_m']);self.assertIsNone(sample['physical_thickness_m'])

    def test_json_csv_reproduce_with_model_years_and_null_exact_latitude(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        rows=[r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['entity_id']=='current:atlantic-equatorial-undercurrent']
        self.assertEqual(len(rows),len(self.p['samples']))
        for row in rows:
            self.assertEqual(json.loads(row['model_output_years']),[1990,2002])
            self.assertEqual(row['model_product'],'FLAME_Hormann2007')
            self.assertEqual(row['exact_core_latitude_degrees_north'],'')
            self.assertEqual(row['metric'],'projected_model_period_mean_core_depth_descriptor')


if __name__=='__main__':unittest.main()
