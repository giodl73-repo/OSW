"""Complete PacificMadagascar cohorts retain original5/10cm/s primary thresholds and gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_pacific_madagascar_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class PacificMadagascarCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all40cases_threeowners_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],40);self.assertEqual(set(r['counts_by_current']),{'current:california','current:alaska','current:southern-east-madagascar'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'pacific-madagascar':40});self.assertLess(len(self.raw),2400000)
    def test_original37interior_and3unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':37,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':3})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':28,'0.1':12})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:california':.05,'current:alaska':.05,'current:southern-east-madagascar':.1}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_two_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),40)
    def test_no_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            for k in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[k])
            for k in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[k])
        for k in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[k],0)
    def test_original_vertical_rules_and_counts_reused(self):
        import derive_surface_regional_velocity_curtains_v1 as prior
        self.assertIs(derive.component,kernel.component);self.assertIs(derive.runs,kernel.runs);self.assertIs(derive.connected_layer,kernel.connected_layer);self.assertIs(derive.counts,prior.counts)
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator','research/wrong-operator.json'),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)

    def source_cases(self):
        cohort=self.op['cohorts'][0];original=json.loads((derive.ROOT/cohort['source_operator']).read_bytes())
        for file in cohort['section_files']:
            source=json.loads((derive.ROOT/file).read_bytes());yield file,source,{**original,**original['currents'][source['entity_id']]}
    def test_original_component_selector_reused_and_pretag_source_unchanged(self):
        import acquire_three_current_depth_sections_v1 as original
        self.assertIs(derive.validate_original_components,original.validate_retained);self.assertIs(derive.diagnose,original.diagnose)
        for file,source,config in self.source_cases():
            before=copy.deepcopy(source);derive.validate_retained(source,config);self.assertEqual(source,before);self.assertNotIn('source_section_geometry',source);self.assertNotIn('fixed_axis',source['section_definition']);self.assertNotIn('native_source_latitude_degrees_north',source['columns'][0])
    def test_rehashed_geometry_and_source_definition_mutations_rejected(self):
        from sample_eac_hycom_route_depth_v1 import canonical_hash
        for file,source,config in self.source_cases():
            for key,value in [('nearest_latitude_distance_km',999),('actual_source_latitude_degrees_north',0),('source_time_index',-1),('component_bearing_degrees_true',90),('source_returned_timestamp_utc','2022-01-16T00:00:00Z')]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(file=file,key=key),self.assertRaises(ValueError):derive.validate_retained(bad,config)
            for key,value in [('global_longitude_index',-1),('global_latitude_index',-1),('sampled_lon_lat',[0,0])]:
                bad=copy.deepcopy(source);bad['columns'][1][key]=value;bad['decoded_columns_sha256']=canonical_hash(bad['columns'])
                with self.subTest(key=key),self.assertRaises(ValueError):derive.validate_retained(bad,config)
            bad=copy.deepcopy(source);bad['section_definition']['longitude_gate_degrees_east']=[-179,179]
            with self.assertRaises(ValueError):derive.validate_retained(bad,config)
    def test_original_frames_surface_gates_and_native_surface_topology(self):
        for c in self.report['cases']:
            self.assertEqual(c['component_bearing_degrees_true'],0 if c['entity_id']=='current:alaska' else 180);self.assertEqual(c['native_surface_seed_connected'],any(run['native_depth_indices_inclusive'][0]==0 for col in c['columns'] for run in col['connected_depth_runs']))
        for file,source,config in self.source_cases():self.assertEqual(config['surface_component_gate_m_s'],.05 if source['entity_id']=='current:southern-east-madagascar' else .02)


if __name__=='__main__':unittest.main()
