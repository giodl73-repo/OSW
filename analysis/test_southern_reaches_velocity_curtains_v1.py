"""Southern reaches preserve weak eastward source thresholds and all original gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_southern_reaches_velocity_curtains_v1 as derive
import derive_nec_subarctic_velocity_curtains_v1 as kernel


class SouthernReachCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):
            cls.batches=[derive.build(owner=owner) for owner in derive.BATCH_COUNTS]
        cases=[c for report,raw in cls.batches for c in report['cases']];cls.raw=max((raw for report,raw in cls.batches),key=len)
        cls.report={**cls.batches[0][0],'cases':cases,'counts':derive.counts(cases),'counts_by_cohort':{'southern-reaches':derive.counts(cases)},'counts_by_current':{owner:derive.counts([c for c in cases if c['entity_id']==owner]) for owner in derive.BATCH_COUNTS},'counts_by_primary_threshold_m_s':{str(v):derive.counts([c for c in cases if c['velocity_threshold_m_s']==v]) for v in [.05,.1]}}
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all18cases_twoowners_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],18);self.assertEqual(set(r['counts_by_current']),{'current:south-pacific','current:south-australian'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'southern-reaches':18});self.assertLess(len(self.raw),2400000)
    def test_original15interior_and3unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':15,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':3})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':18,'0.1':0})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:south-pacific':.05,'current:south-australian':.05}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_two_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),18)
    def test_no_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            for k in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[k])
            for k in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[k])
        for k in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[k],0)
    def test_original_vertical_rules_and_counts_reused(self):
        import derive_surface_regional_velocity_curtains_v1 as prior
        self.assertIs(derive.frozen.curtain,kernel.curtain);self.assertIs(derive.counts,prior.counts)
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator','research/wrong-operator.json'),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:south-pacific')
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:south-pacific')

    def test_two_bounded_batches_cover_exact_original_plan(self):
        files=[]
        for report,raw in self.batches:
            self.assertLess(len(raw),2400000);self.assertEqual(report['source_plan_case_count'],18);self.assertEqual(report['counts']['cases'],derive.BATCH_COUNTS[report['batch_current_id']]);self.assertEqual(set(report['counts_by_current']),{report['batch_current_id']});files.extend(c['source_file'] for c in report['cases'])
        self.assertEqual(len(files),18);self.assertEqual(len(set(files)),18)
        with self.assertRaises(ValueError):derive.build()
    def test_original_zonal_validator_selector_and_curtain_unchanged(self):
        import acquire_zonal_current_depth_sections_v1 as original
        self.assertIs(derive.frozen.validate_retained,original.validate_retained);self.assertIs(derive.frozen.diagnose,original.diagnose)
    def test_source_frames_gates_and_surface_topology_preserved(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for c in self.report['cases']:
            config={**op,**op['currents'][c['entity_id']]};self.assertEqual(c['component_bearing_degrees_true'],90);self.assertEqual(config['surface_component_gate_m_s'],.02);self.assertIsNone(config['temperature_gate']);self.assertEqual(c['native_surface_seed_connected'],any(run['native_depth_indices_inclusive'][0]==0 for col in c['columns'] for run in col['connected_depth_runs']))
    def test_source_unchanged_and_original_geometry_time_diagnosis_mutations_rejected(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for owner in derive.BATCH_COUNTS:
            file=self.op['cohorts'][0]['section_files_by_current'][owner][0];source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);config={**op,**op['currents'][owner]};derive.frozen.curtain(source,config,file);self.assertEqual(source,before)
            for key,value in [('component_bearing_degrees_true',0),('maximum_nearest_longitude_distance_km',999),('source_returned_timestamp_utc','2022-01-16T00:00:00Z')]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.frozen.curtain(bad,config,file)
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.frozen.curtain(bad,config,file)

    def test_no_qualification_gate_and_upper_support_edges_remain_distinct(self):
        from collections import Counter
        statuses=Counter(c['original_horizontal_selection_status'] for c in self.report['cases']);self.assertEqual(statuses['no_qualifying_surface_connected_component_column'],1);self.assertEqual(statuses['section_gate_edge_maximum_axis_unresolved'],1);self.assertEqual(statuses['upper_layer_support_edge_maximum_axis_unresolved'],1)
        for c in self.report['cases']:
            if c['original_horizontal_selection_status']=='no_qualifying_surface_connected_component_column':self.assertIsNone(c['original_selected_column_index']);self.assertIsNone(c['original_primary_layer']);self.assertEqual(c['columns'],[])


if __name__=='__main__':unittest.main()
