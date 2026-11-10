"""Solomon undercurrents retain latitude geometry, source intervals and distinct evidence."""
import copy,json,unittest
from unittest.mock import patch
import derive_solomon_undercurrents_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class SolomonUndercurrentCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):
            cls.batches=[derive.build(owner=owner) for owner in derive.BATCH_COUNTS]
        cases=[c for report,raw in cls.batches for c in report['cases']];cls.raw=max((raw for report,raw in cls.batches),key=len)
        cls.report={**cls.batches[0][0],'cases':cases,'counts':derive.counts(cases),'counts_by_cohort':{'solomon-undercurrents':derive.counts(cases)},'counts_by_current':{owner:derive.counts([c for c in cases if c['entity_id']==owner]) for owner in derive.BATCH_COUNTS},'counts_by_primary_threshold_m_s':{str(v):derive.counts([c for c in cases if c['velocity_threshold_m_s']==v]) for v in [.05,.1]}}
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all32cases_twoowners_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],32);self.assertEqual(set(r['counts_by_current']),{'current:new-ireland-coastal-undercurrent', 'current:solomon-island-coastal-undercurrent'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'solomon-undercurrents':32});self.assertLess(len(self.raw),2400000)
    def test_original26interior_and6unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':26,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':6})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':0,'0.1':32})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:new-ireland-coastal-undercurrent':.1,'current:solomon-island-coastal-undercurrent':.1}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_four_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),32)
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
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:new-ireland-coastal-undercurrent')
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:new-ireland-coastal-undercurrent')

    def test_two_bounded_batches_cover_exact_original_plan(self):
        files=[]
        for report,raw in self.batches:
            self.assertLess(len(raw),2400000);self.assertEqual(report['source_plan_case_count'],32);self.assertEqual(report['counts']['cases'],derive.BATCH_COUNTS[report['batch_current_id']]);self.assertEqual(set(report['counts_by_current']),{report['batch_current_id']});files.extend(c['source_file'] for c in report['cases'])
        self.assertEqual(len(files),32);self.assertEqual(len(set(files)),32)
        with self.assertRaises(ValueError):derive.build()
    def test_original_interval_validator_selector_and_curtain_unchanged(self):
        import mixed_interval_section_geometry_v1 as original
        import interval_depth_diagnostic_v1 as diagnostic
        self.assertIs(derive.frozen.validate_retained,original.validate_retained);self.assertIs(derive.frozen.diagnose,diagnostic.diagnose)
    def test_source_frames_intervals_and_absent_surface_gate_preserved(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for c in self.report['cases']:
            config={**op,**op['currents'][c['entity_id']]};self.assertEqual(c['component_bearing_degrees_true'],0);self.assertIsNone(config['surface_component_gate_m_s']);self.assertIsNone(config['temperature_gate']);self.assertEqual(config['selection_depth_interval_m'],[100,350]);self.assertEqual(config['core_search_depth_interval_m'],[100,350]);self.assertEqual(c['source_geometry'],'latitude');self.assertNotIn('geometry_adapter',c);self.assertEqual(c['identity_evidence_basis'],derive.EVIDENCE_BASES[c['entity_id']])
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());self.assertFalse(source['diagnosis']['surface_velocity_qualification_applied'])
    def test_source_unchanged_and_original_geometry_time_diagnosis_mutations_rejected(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for owner in derive.BATCH_COUNTS:
            file=self.op['cohorts'][0]['section_files_by_current'][owner][0];source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);config={**op,**op['currents'][owner]};derive.source_curtain(source,config,file);self.assertEqual(source,before)
            for key,value in [('component_bearing_degrees_true',90),('nearest_latitude_distance_km',999),('source_returned_timestamp_utc','2022-01-16T00:00:00Z')]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(bad,config,file)
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.source_curtain(bad,config,file)

    def test_no_qualification_gate_and_support_edges_remain_distinct(self):
        from collections import Counter
        statuses=Counter(c['original_horizontal_selection_status'] for c in self.report['cases'])
        self.assertEqual(statuses['no_qualifying_interval_component_column'],1);self.assertEqual(statuses['section_gate_edge_maximum_axis_unresolved'],3);self.assertEqual(statuses['selection_interval_support_edge_maximum_axis_unresolved'],2)
        for c in self.report['cases']:
            if c['original_horizontal_selection_status']=='no_qualifying_interval_component_column':self.assertIsNone(c['original_selected_column_index']);self.assertIsNone(c['original_primary_layer']);self.assertEqual(c['columns'],[])
    def test_original_latitude_schema_tags_and_distinct_identity_evidence_required(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes());file=self.op['cohorts'][0]['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes());config={**op,**op['currents'][source['entity_id']]}
        for key,value in [('source_section_geometry','longitude'),('schema','invented')]:
            bad=copy.deepcopy(source);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(bad,config,file)
        for field,value in [('surface_component_gate_m_s',.05),('identity_evidence_basis','invented')]:
            bad_config=copy.deepcopy(config);bad_config[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):derive.source_curtain(source,bad_config,file)
        self.assertNotEqual(*derive.EVIDENCE_BASES.values())
        for report,raw in self.batches:self.assertEqual(report['identity_evidence_basis_by_current'],{report['batch_current_id']:derive.EVIDENCE_BASES[report['batch_current_id']]})


if __name__=='__main__':unittest.main()
