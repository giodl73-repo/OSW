"""Complete ThreeCurrent cohorts retain original5/10cm/s primary thresholds and gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_three_current_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class ThreeCurrentCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all40cases_threeowners_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],40);self.assertEqual(set(r['counts_by_current']),{'current:mindanao-current','current:oyashio','current:leeuwin'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'three-current':40});self.assertLess(len(self.raw),2400000)
    def test_original34interior_and6unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':34,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':6})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':14,'0.1':26})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:mindanao-current':.1,'current:oyashio':.1,'current:leeuwin':.05}
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
        cohort=self.op['cohorts'][0];op=json.loads((derive.ROOT/cohort['source_operator']).read_bytes())
        for file in cohort['section_files']:
            source=json.loads((derive.ROOT/file).read_bytes());yield file,source,{**op,**op['currents'][source['entity_id']]}
    def test_original_temperature_gate_only_selects_core_not_3d_membership(self):
        for c in self.report['cases']:
            self.assertFalse(c['temperature_screen_applied_to_connected_nodes']);self.assertFalse(c['water_mass_classification_performed'])
            if c['entity_id']=='current:oyashio':
                self.assertEqual(c['original_horizontal_temperature_gate'],{'native_depth_m':100,'maximum_temperature_degrees_celsius':5})
                if c['original_selected_column_index'] is not None:self.assertLessEqual(c['original_selected_native100m_temperature_degrees_celsius'],5)
            else:self.assertIsNone(c['original_horizontal_temperature_gate']);self.assertIsNone(c['original_selected_native100m_temperature_degrees_celsius'])
    def test_rehashed_warm_selected_oyashio_temperature_still_rejected(self):
        from sample_eac_hycom_route_depth_v1 import canonical_hash
        checked=0
        for file,source,config in self.source_cases():
            selected=source['diagnosis']['selected_column_index']
            if source['entity_id']!='current:oyashio' or selected is None:continue
            bad=copy.deepcopy(source);bad['native100m_temperature_degrees_celsius'][selected]=6.;bad['temperature_source']['decoded_values_sha256']=canonical_hash(bad['native100m_temperature_degrees_celsius'])
            with self.assertRaises(ValueError):derive.curtain(bad,config,file)
            checked+=1
        self.assertEqual(checked,10)
    def test_nonthermal_entire_curtain_matches_validated_prior_exactly(self):
        import derive_pacific_madagascar_velocity_curtains_v1 as prior
        self.assertIs(derive.validate_retained,prior.validate_retained)
        added=['original_horizontal_temperature_gate','original_selected_native100m_temperature_degrees_celsius','temperature_screen_applied_to_connected_nodes','temperature_support_policy']
        checked=0
        for file,source,config in self.source_cases():
            if config.get('temperature_gate') is not None:continue
            current=derive.curtain(source,config,file)
            for key in added:current.pop(key)
            self.assertEqual(current,prior.curtain(source,config,file));checked+=1
        self.assertEqual(checked,28)
    def test_original_source_unchanged_and_frames_surface_gate_preserved(self):
        for file,source,config in self.source_cases():
            before=copy.deepcopy(source);derive.curtain(source,config,file);self.assertEqual(source,before);self.assertEqual(config['component_bearing_degrees_true'],225 if source['entity_id']=='current:oyashio' else 180);self.assertEqual(config['surface_component_gate_m_s'],.05)


if __name__=='__main__':unittest.main()
