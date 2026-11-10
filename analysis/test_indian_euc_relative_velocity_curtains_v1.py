"""Indian EUC retains original relative-core selection and finite surface references."""
import copy,json,unittest
from unittest.mock import patch
import derive_indian_euc_relative_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class IndianEUCRelativeCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):
            cls.batches=[derive.build(owner=owner) for owner in derive.BATCH_COUNTS]
        cases=[c for report,raw in cls.batches for c in report['cases']];cls.raw=max((raw for report,raw in cls.batches),key=len)
        cls.report={**cls.batches[0][0],'cases':cases,'counts':derive.counts(cases),'counts_by_cohort':{'indian-euc-relative':derive.counts(cases)},'counts_by_current':{owner:derive.counts([c for c in cases if c['entity_id']==owner]) for owner in derive.BATCH_COUNTS},'counts_by_primary_threshold_m_s':{str(v):derive.counts([c for c in cases if c['velocity_threshold_m_s']==v]) for v in [.05,.1]}}
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all20cases_oneowner_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],20);self.assertEqual(set(r['counts_by_current']),{'current:indian-equatorial-undercurrent'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'indian-euc-relative':20});self.assertLess(len(self.raw),2400000)
    def test_original15interior_and5unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':15,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':5})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':0,'0.1':20})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:indian-equatorial-undercurrent':.1}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_four_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),20)
    def test_no_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            for k in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[k])
            for k in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[k])
        for k in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[k],0)
    def test_frozen_tracing_body_graph_and_counts_reused(self):
        import ast,inspect
        import derive_surface_regional_velocity_curtains_v1 as prior
        for name in ['component','runs','connected_layer']:self.assertIs(getattr(derive.frozen,name),getattr(kernel,name))
        self.assertEqual(ast.dump(ast.parse(inspect.getsource(derive.frozen.curtain))),ast.dump(ast.parse(inspect.getsource(kernel.curtain))))
        self.assertIs(derive.counts,prior.counts)
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator','research/wrong-operator.json'),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:indian-equatorial-undercurrent')
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:indian-equatorial-undercurrent')

    def test_one_bounded_batch_cover_exact_original_plan(self):
        files=[]
        for report,raw in self.batches:
            self.assertLess(len(raw),2400000);self.assertEqual(report['source_plan_case_count'],20);self.assertEqual(report['counts']['cases'],derive.BATCH_COUNTS[report['batch_current_id']]);self.assertEqual(set(report['counts_by_current']),{report['batch_current_id']});files.extend(c['source_file'] for c in report['cases'])
        self.assertEqual(len(files),20);self.assertEqual(len(set(files)),20)
        with self.assertRaises(ValueError):derive.build()
    def test_original_relative_validator_and_selector_bindings(self):
        import relative_core_interval_section_audit_v1 as original
        import relative_core_interval_diagnostic_v1 as relative
        self.assertIs(derive.frozen.validate_retained,original.validate_retained);self.assertIs(derive.frozen.diagnose,relative.diagnose)
    def test_source_frame_windows_and_relative_comparison_preserved(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for c in self.report['cases']:
            config={**op,**op['currents'][c['entity_id']]};self.assertEqual(c['component_bearing_degrees_true'],90);self.assertIsNone(config['surface_component_gate_m_s']);self.assertIsNone(config['temperature_gate']);self.assertTrue(config['require_core_stronger_than_surface']);self.assertEqual(config['selection_depth_interval_m'],[50,200]);self.assertEqual(config['core_search_depth_interval_m'],[50,200]);self.assertEqual(c['source_geometry'],'longitude');self.assertTrue(c['original_subsurface_core_surface_comparison_applied']);self.assertFalse(c['original_positive_surface_speed_gate_applied']);self.assertEqual(c['original_minimum_core_minus_surface_m_s'],0);self.assertFalse(c['original_contrast_is_uncertainty_or_physical_accuracy'])
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());d=source['diagnosis'];index=d['selected_column_index'];self.assertEqual(c['original_selected_relative_candidate'],d['candidate_scores'][index] if index is not None else None)
    def test_source_unchanged_and_original_geometry_time_diagnosis_mutations_rejected(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for owner in derive.BATCH_COUNTS:
            file=self.op['cohorts'][0]['section_files_by_current'][owner][0];source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);config={**op,**op['currents'][owner]};derive.source_curtain(source,config,file);self.assertEqual(source,before)
            distance_key='maximum_nearest_longitude_distance_km'
            for key,value in [('component_bearing_degrees_true',(config['component_bearing_degrees_true']+90)%360),(distance_key,999),('source_returned_timestamp_utc','2022-01-16T00:00:00Z')]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(bad,config,file)
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.source_curtain(bad,config,file)

    def test_no_qualification_and_gate_edges_remain_distinct(self):
        from collections import Counter
        statuses=Counter(c['original_horizontal_selection_status'] for c in self.report['cases']);self.assertEqual(statuses['no_qualifying_interval_core_stronger_than_surface_column'],3);self.assertEqual(statuses['section_gate_edge_maximum_axis_unresolved'],2)
        for c in self.report['cases']:
            if c['original_horizontal_selection_status']=='no_qualifying_interval_core_stronger_than_surface_column':self.assertIsNone(c['original_selected_column_index']);self.assertIsNone(c['original_primary_layer']);self.assertIsNone(c['original_selected_relative_candidate']);self.assertEqual(c['columns'],[])
    def test_original_schema_untagged_geometry_and_relative_rule_required(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes());file=self.op['cohorts'][0]['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes());config={**op,**op['currents'][source['entity_id']]}
        for key,value in [('source_section_geometry','longitude'),('schema','invented')]:
            bad=copy.deepcopy(source);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(bad,config,file)
        for key,value in [('require_core_stronger_than_surface',False),('surface_component_gate_m_s',.05)]:
            bad_config=copy.deepcopy(config);bad_config[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(source,bad_config,file)
    def modified_fixture(self,surface,missing_neighbor=False):
        import test_indian_euc_relative_depth_sections_v1 as original
        from sample_eac_hycom_route_depth_v1 import canonical_hash,along_velocity
        original.IndianEUCRelativeSourceTests.setUpClass();p,c=original.IndianEUCRelativeSourceTests().fixture();p['schema']='osw.relative-core-interval-transverse-depth-section.v1';p['section_definition']['id']='fixture-section'
        for index,value in [(1,surface)]+([(0,None)] if missing_neighbor else []):
            column=p['columns'][index];column['eastward_velocity_m_s'][0]=value;column['northward_velocity_m_s'][0]=0. if value is not None else None;column['signed_reference_component_m_s'][0]=float(along_velocity(value,0.,90)) if value is not None else None
        p['decoded_columns_sha256']=canonical_hash(p['columns']);p['diagnosis']=derive.frozen.diagnose(p['depth_levels_m'],[col['signed_reference_component_m_s'] for col in p['columns']],c)
        return p,c
    def test_weaker_negative_zero_or_positive_surface_reference_is_accepted(self):
        for surface in [-.1,0.,.04,.2]:
            p,c=self.modified_fixture(surface);before=copy.deepcopy(p);result=derive.source_curtain(p,c,'fixture');self.assertEqual(result['original_selected_column_index'],1);self.assertTrue(result['columns']);candidate=result['original_selected_relative_candidate'];self.assertTrue(candidate['core_stronger_than_surface']);self.assertTrue(candidate['surface_reference_available']);self.assertGreater(candidate['core_minus_surface_m_s'],0);self.assertEqual(p,before)
    def test_equal_dominant_or_missing_surface_reference_is_rejected(self):
        for surface in [.3,.4,None]:
            p,c=self.modified_fixture(surface);result=derive.source_curtain(p,c,'fixture');self.assertIsNone(result['original_selected_column_index']);self.assertEqual(result['columns'],[]);self.assertIsNone(result['original_selected_relative_candidate']);self.assertFalse(p['diagnosis']['candidate_scores'][1]['eligible'])
    def test_missing_neighbor_reference_censors_selected_core_without_replacement(self):
        p,c=self.modified_fixture(-.1,missing_neighbor=True);result=derive.source_curtain(p,c,'fixture');self.assertEqual(result['original_selected_column_index'],1);self.assertEqual(result['original_horizontal_selection_status'],'selection_interval_or_surface_reference_support_edge_maximum_axis_unresolved');self.assertEqual(result['columns'],[]);self.assertIsNotNone(result['original_primary_layer'])


if __name__=='__main__':unittest.main()
