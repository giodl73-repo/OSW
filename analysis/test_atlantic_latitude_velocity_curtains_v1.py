"""Complete AtlanticLatitude cohorts retain original5/10cm/s primary thresholds and gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_atlantic_latitude_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class AtlanticLatitudeCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all48cases_fourowners_and_cohorts_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],48);self.assertEqual(set(r['counts_by_current']),{'current:florida','current:portugal','current:irminger','current:west-spitsbergen'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'florida-portugal':20,'irminger-wsc':28});self.assertLess(len(self.raw),2400000)
    def test_original37interior_and11unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':37,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':11})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.02':10,'0.1':38})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:florida':.1,'current:portugal':.02,'current:irminger':.1,'current:west-spitsbergen':.1}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_two_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),48)
    def test_no_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            for k in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[k])
            for k in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[k])
        for k in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[k],0)
    def test_original_vertical_rules_and_counts_reused(self):
        import derive_surface_regional_velocity_curtains_v1 as prior
        self.assertIs(derive.component,kernel.component);self.assertIs(derive.runs,kernel.runs);self.assertIs(derive.connected_layer,kernel.connected_layer);self.assertIs(derive.counts,prior.counts)
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator',self.op['cohorts'][1]['source_operator']),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)

    def test_native_surface_flag_is_topology_only(self):
        for c in self.report['cases']:self.assertEqual(c['native_surface_seed_connected'],any(run['native_depth_indices_inclusive'][0]==0 and c['depth_levels_m'][0]==0 for col in c['columns'] for run in col['connected_depth_runs']))
    def test_original_noninterval_validator_and_selector_reused(self):
        import latitude_depth_section_geometry_v1 as original
        self.assertIs(derive.validate_retained,original.validate_retained);self.assertIs(derive.diagnose,original.diagnose)
        for case in self.report['cases']:
            source=json.loads((derive.ROOT/case['source_file']).read_bytes())
            self.assertNotIn('selection_depth_interval_m',source['diagnosis']);self.assertNotIn('source_section_geometry',source)
    def test_geometry_rotation_diagnosis_and_time_mutations_rejected(self):
        for cohort in self.op['cohorts']:
            file=cohort['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes());op=json.loads((derive.ROOT/cohort['source_operator']).read_bytes());config={**op,**op['currents'][source['entity_id']]}
            for key,value in [('component_bearing_degrees_true',config['component_bearing_degrees_true']+1),('source_returned_timestamp_utc','2022-01-16T00:00:00Z'),('nearest_latitude_distance_km',999)]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.curtain(bad,config,file)
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.curtain(bad,config,file)
    def test_portugal_cutoff_surface_gate_and_frame_preserved(self):
        sourceop=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes());p=sourceop['currents']['current:portugal']
        self.assertEqual(p['primary_threshold_m_s'],.02);self.assertEqual(p['surface_component_gate_m_s'],.01);self.assertEqual(p['component_bearing_degrees_true'],180);self.assertEqual(sourceop['thresholds_m_s'].index(.02),0)
        for case in self.report['cases']:
            if case['entity_id']=='current:portugal' and case['original_selected_column_index'] is not None:
                source=json.loads((derive.ROOT/case['source_file']).read_bytes());self.assertEqual(case['original_primary_layer'],source['diagnosis']['selected_column_threshold_layers'][0])


if __name__=='__main__':unittest.main()
