"""Complete NECAleutian cohorts retain original5/10cm/s primary thresholds and gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_nec_subarctic_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class NECAleutianCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all34cases_threeowners_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],34);self.assertEqual(set(r['counts_by_current']),{'current:pacific-north-equatorial','current:atlantic-north-equatorial','current:aleutian'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'nec-subarctic':34});self.assertLess(len(self.raw),2400000)
    def test_original29interior_and5unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':29,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':5})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':12,'0.1':22})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:pacific-north-equatorial':.1,'current:atlantic-north-equatorial':.1,'current:aleutian':.05}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_two_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),34)
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

    def test_original29_and_completion5_provenance_preserved(self):
        from collections import Counter
        self.assertEqual(Counter(c['transport_origin'] for c in self.report['cases']),{'recovered_original_attempt2':29,'completion_missing_five':5})
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());self.assertEqual(c['source_collection_operator'],source['operator_file'])
            if c['transport_origin']=='completion_missing_five':self.assertEqual(c['entity_id'],'current:aleutian');self.assertEqual(c['snapshot_time_utc'],'2022-07-15T00:00:00Z')
    def test_original_frames_surface_gates_and_first_primary_layer_preserved(self):
        original=json.loads((derive.ROOT/derive.ORIGINAL).read_bytes())
        for c in self.report['cases']:
            aleutian=c['entity_id']=='current:aleutian';config=original['currents'][c['entity_id']];self.assertEqual(c['component_bearing_degrees_true'],90 if aleutian else 270);self.assertEqual(config['surface_component_gate_m_s'],.02 if aleutian else .05)
            self.assertEqual(c['native_surface_seed_connected'],any(run['native_depth_indices_inclusive'][0]==0 for col in c['columns'] for run in col['connected_depth_runs']))
            if aleutian and c['original_selected_column_index'] is not None:
                source=json.loads((derive.ROOT/c['source_file']).read_bytes());self.assertEqual(c['original_primary_layer'],source['diagnosis']['selected_column_threshold_layers'][0])
    def test_original_noninterval_zonal_validator_and_tampering_rejection(self):
        import acquire_zonal_current_depth_sections_v1 as original_method
        self.assertIs(derive.validate_retained,original_method.validate_retained);self.assertIs(derive.diagnose,original_method.diagnose)
        original=json.loads((derive.ROOT/derive.ORIGINAL).read_bytes())
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());config={**original,**original['currents'][source['entity_id']]};self.assertNotIn('source_section_geometry',source);self.assertNotIn('selection_depth_interval_m',source['diagnosis'])
            for key,value in [('component_bearing_degrees_true',0),('maximum_nearest_longitude_distance_km',999),('source_returned_timestamp_utc','2022-01-16T00:00:00Z')]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.curtain(bad,config,c['source_file'])
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.curtain(bad,config,c['source_file'])


if __name__=='__main__':unittest.main()
