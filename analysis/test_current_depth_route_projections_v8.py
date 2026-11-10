import copy,csv,io,json
import unittest
import build_current_depth_route_projections_v7 as previous
import build_current_depth_route_projections_v8 as profile


class MatchedNwASCCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=profile.build();cls.p=cls.data['projections'][-1];cls.volumes=profile.build_volume_scenarios(cls.data)
        cls.op=json.loads((profile.ROOT/profile.OPERATOR).read_bytes());cls.geometry=json.loads((profile.ROOT/cls.op['geometry_source_file']).read_bytes())
        cls.refs={r['id']:r for r in json.loads((profile.ROOT/cls.op['depth_register_file']).read_bytes())['evidence']}

    def test_previous_nine_profiles_and_first_volume_preserved(self):
        self.assertEqual(self.data['projections'][:9],previous.build()['projections'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':10,'identities_not_yet_projected':101,'regional_projection_scenarios':10,'source_anchor_references':28,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':2})
        old=json.loads((profile.ROOT/'research/current-regional-core-volume-scenarios-v1.json').read_bytes())
        self.assertEqual(self.volumes['records'][0],old['records'][0])
        self.assertEqual(self.volumes['counts'],{'regional_reference_geometry_scenarios':2,'whole_current_volume_estimates':0,'observed_water_volume_estimates':0})

    def test_matched_depth_area_anchors_and_midpoint(self):
        self.assertEqual([(r['section_name'],r['source_path_distance_km'],r['maximum_core_depth_m'],r['cross_section_area_km2']) for r in self.p['anchors']],[('Gimsoy',0,530,8),('Bjornoya',750,580,17)])
        self.assertEqual(self.p['samples'][0]['projected_depth_descriptor_m'],530);self.assertEqual(self.p['samples'][-1]['projected_depth_descriptor_m'],580)
        # An intermediate area comes from the same two sections, not depth*width.
        s=next(s for s in self.p['samples'] if s['distance_along_reported_source_path_km']==250)
        self.assertEqual(s['projected_core_cross_section_area_km2'],11)
        self.assertEqual(s['source_reference_ids'],self.p['source_reference_ids'])

    def test_regional_area_integral_not_source_box_or_depth_rectangle(self):
        v=self.volumes['records'][-1]
        self.assertEqual(v['computed_integral_km3'],9375)
        self.assertEqual(v['scenario_volume_km3'],9000)
        self.assertEqual(v['source_heat_budget_box_context']['reported_box_volume_km3'],7500)
        self.assertFalse(v['source_heat_budget_box_used_for_integration']);self.assertFalse(v['source_box_difference_is_uncertainty'])
        self.assertNotEqual(v['computed_integral_km3'],50*.580*750)
        self.assertIsNone(v['uncertainty_km3']);self.assertIsNone(v['confidence_interval_km3'])

    def test_mismatched_sections_areas_periods_and_bso_operator_fail(self):
        for field,value in [('cross_section_area_km2',10),('maximum_core_depth_m',200),('section_name','BSO')]:
            case=copy.deepcopy(self.op['case']);case['anchors'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):profile.validate_case(case,self.refs,self.geometry)
        case=copy.deepcopy(self.op['case']);case['anchors'][1]['source_context']['climatology_years']=[2011,2023]
        with self.assertRaises(ValueError):profile.validate_case(case,self.refs,self.geometry)
        changed=copy.deepcopy(self.data);changed['projections'][-1]['anchors'][1]['cross_section_area_km2']=10
        with self.assertRaises(ValueError):profile.build_volume_scenarios(changed)

    def test_abstract_reported_path_does_not_invent_map_or_osw_route_distance(self):
        self.assertEqual(self.p['source_reported_path_length_km'],750);self.assertTrue(self.p['source_path_length_is_approximate'])
        self.assertIsNone(self.p['route_id']);self.assertIsNone(self.p['route_length_km'])
        for s in self.p['samples']:
            self.assertIsNone(s['longitude']);self.assertIsNone(s['latitude']);self.assertIsNone(s['distance_along_reference_route_km']);self.assertIsNone(s['physical_thickness_m']);self.assertFalse(s['volume_eligible'])

    def test_uneven_static_mean_is_not_seasonal_or_full_current_volume(self):
        self.assertEqual(self.p['source_period_years'],[1993,2022]);self.assertIsNone(self.p['calendar_months']);self.assertIsNone(self.p['annual_range_m'])
        self.assertFalse(any(self.p['eligibility'].values()))
        v=self.volumes['records'][-1]
        for k in ['whole_current_volume_estimate','observed_water_volume','mean_of_instantaneous_core_volumes','physical_state_join_eligible','global_total_eligible']:self.assertFalse(v[k])
        self.assertTrue(v['regional_scenario_admitted'])
        self.assertIsNone(self.p['anchors'][1]['source_context']['core_definition']['shoreward_isobath_m'])
        self.assertEqual(self.p['anchors'][0]['source_context']['core_definition']['shoreward_isobath_m'],2500)

    def test_latest_reference_ownership_and_json_reproduce(self):
        register=json.loads((profile.ROOT/self.op['depth_register_file']).read_bytes());self.assertEqual(register['counts']['depth_references'],343)
        for row in self.data['records']:
            source=next(r for r in register['records'] if r['entity_id']==row['entity_id']);self.assertEqual(row['depth_reference_ids'],source['depth_reference_ids'])
        self.assertEqual(self.data,json.loads((profile.ROOT/profile.OUTPUT).read_bytes()))
        self.assertEqual(self.volumes,json.loads((profile.ROOT/profile.VOLUME_OUTPUT).read_bytes()))

    def test_profile_and_volume_csv_preserve_old_cells_and_distinct_coordinates(self):
        raw=profile.csv_bytes(self.data);self.assertEqual(raw,(profile.ROOT/profile.CSV).read_bytes())
        old=list(csv.DictReader(io.StringIO((profile.ROOT/previous.CSV).read_text(encoding='utf8'))));new=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[len(old):]:
            self.assertEqual(r['longitude'],'');self.assertEqual(r['latitude'],'');self.assertEqual(r['distance_along_reference_route_km'],'');self.assertNotEqual(r['distance_along_reported_source_path_km'],'');self.assertEqual(json.loads(r['source_period_years']),[1993,2022])
        raw=profile.volume_csv_bytes(self.volumes);self.assertEqual(raw,(profile.ROOT/profile.VOLUME_CSV).read_bytes())
        old=next(csv.DictReader(io.StringIO((profile.ROOT/'research/current-regional-core-volume-scenarios-v1.csv').read_text(encoding='utf8'))));new=next(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        self.assertEqual(old,{k:new[k] for k in old})


if __name__=='__main__':unittest.main()
