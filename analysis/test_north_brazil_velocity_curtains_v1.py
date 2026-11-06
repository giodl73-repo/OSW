"""NBC preserves legacy records, reversible aliases and original censored boundaries."""
import copy,json,unittest
from unittest.mock import patch
import derive_north_brazil_velocity_curtains_v1 as derive
import derive_three_current_velocity_curtains_v1 as kernel


class NorthBrazilCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):
            cls.batches=[derive.build(owner=owner) for owner in derive.BATCH_COUNTS]
        cases=[c for report,raw in cls.batches for c in report['cases']];cls.raw=max((raw for report,raw in cls.batches),key=len)
        cls.report={**cls.batches[0][0],'cases':cases,'counts':derive.counts(cases),'counts_by_cohort':{'north-brazil':derive.counts(cases)},'counts_by_current':{owner:derive.counts([c for c in cases if c['entity_id']==owner]) for owner in derive.BATCH_COUNTS},'counts_by_primary_threshold_m_s':{str(v):derive.counts([c for c in cases if c['velocity_threshold_m_s']==v]) for v in [.05,.1]}}
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all14cases_oneowner_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],14);self.assertEqual(set(r['counts_by_current']),{'current:north-brazil'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'north-brazil':14});self.assertLess(len(self.raw),2400000)
    def test_original14interior_and0unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':14})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':0,'0.1':14})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:north-brazil':.1}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config=op;d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_two_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),14)
    def test_no_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            for k in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[k])
            for k in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[k])
        for k in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[k],0)
    def test_original_vertical_rules_and_counts_reused(self):
        import derive_surface_regional_velocity_curtains_v1 as prior
        import ast,inspect
        self.assertEqual(ast.dump(ast.parse(inspect.getsource(derive.frozen.curtain))),ast.dump(ast.parse(inspect.getsource(kernel.curtain))))
        for name in ['component','runs','connected_layer']:self.assertIs(getattr(derive.frozen,name),getattr(kernel,name))
        self.assertIs(derive.counts,prior.counts)
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator','research/wrong-operator.json'),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:north-brazil')
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:north-brazil')

    def test_one_bounded_batch_cover_exact_original_plan(self):
        files=[]
        for report,raw in self.batches:
            self.assertLess(len(raw),2400000);self.assertEqual(report['source_plan_case_count'],14);self.assertEqual(report['counts']['cases'],derive.BATCH_COUNTS[report['batch_current_id']]);self.assertEqual(set(report['counts_by_current']),{report['batch_current_id']});files.extend(c['source_file'] for c in report['cases'])
        self.assertEqual(len(files),14);self.assertEqual(len(set(files)),14)
        with self.assertRaises(ValueError):derive.build()
    def test_exact_frozen_legacy_selection_and_classic_trace_bindings(self):
        import acquire_three_current_depth_sections_v1 as classic
        import derive_pacific_madagascar_velocity_curtains_v1 as geometry
        import ast,inspect
        self.assertIs(derive.legacy.selection,classic.base_selection);self.assertIs(derive.frozen.original_diagnose,derive.legacy.diagnose);self.assertEqual(ast.dump(ast.parse(inspect.getsource(derive.frozen.validate_retained))),ast.dump(ast.parse(inspect.getsource(geometry.validate_retained))))
    def test_original_northwest_frame_surface_gate_and_view_geometry_preserved(self):
        for c in self.report['cases']:
            self.assertEqual(c['component_bearing_degrees_true'],315);self.assertEqual(c['source_geometry']['section_definition']['entity_id'],'current:north-brazil');self.assertNotIn('fixed_axis',c['source_geometry']['section_definition']);self.assertFalse(c['schema_adapter_changes_source_bytes']);self.assertFalse(c['component_values_changed_by_adapter']);self.assertIsNone(c['original_horizontal_temperature_gate']);source=json.loads((derive.ROOT/c['source_file']).read_bytes());self.assertEqual(c['original_decoded_columns_sha256'],source['decoded_columns_sha256'])
    def test_source_unchanged_and_original_geometry_time_diagnosis_mutations_rejected(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for owner in derive.BATCH_COUNTS:
            file=self.op['cohorts'][0]['section_files_by_current'][owner][0];source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);config=op;derive.source_curtain(source,config,file);self.assertEqual(source,before)
            for key,value in [('component_bearing_degrees_true',90),('nearest_latitude_distance_km',999),('source_returned_timestamp_utc','2022-01-16T00:00:00Z')]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(bad,config,file)
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.source_curtain(bad,config,file)

    def test_all_original_interiors_and_two_primary_censors_are_preserved(self):
        self.assertEqual({c['original_horizontal_selection_status'] for c in self.report['cases']},{'interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis'});self.assertEqual(sum(c['original_primary_layer']['lower_depth_m'] is None for c in self.report['cases']),2)
    def test_original_schema_and_single_component_alias_required(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes());file=self.op['cohorts'][0]['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes())
        for key,value in [('source_section_geometry','latitude'),('schema','invented'),('native100m_temperature_degrees_celsius',None)]:
            bad=copy.deepcopy(source);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):derive.source_view(bad,op)
    def test_round_trip_restores_every_original_source_record(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for file in self.op['cohorts'][0]['section_files']:
            source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);view,config=derive.source_view(source,op);self.assertEqual(source,before);self.assertEqual(derive.restore_source(view,source['decoded_columns_sha256']),source);self.assertNotEqual(view['decoded_columns_sha256'],source['decoded_columns_sha256']);self.assertIsNone(view['native100m_temperature_degrees_celsius']);self.assertIsNone(config['temperature_gate'])
            for old,new in zip(source['columns'],view['columns']):self.assertEqual(old['signed_northwest_component_m_s'],new['signed_reference_component_m_s']);self.assertEqual(set(new),(set(old)-{'signed_northwest_component_m_s'})|{'signed_reference_component_m_s'})
    def test_raw_component_mutation_rejected_even_after_legacy_hash_refresh(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes());source=json.loads((derive.ROOT/self.op['cohorts'][0]['section_files'][0]).read_bytes());index=source['diagnosis']['selected_column_index'];source['columns'][index]['eastward_velocity_m_s'][0]+=.1;source['decoded_columns_sha256']=derive.legacy.canonical_hash(source['columns']);derive.legacy.validate_retained(source,op)
        with self.assertRaises(ValueError):derive.source_curtain(source,op,'fixture')
    def test_censored_seed_boundaries_not_filled_from_neighboring_profiles(self):
        for case in self.report['cases']:
            primary=case['original_primary_layer']
            if primary['lower_depth_m'] is not None:continue
            seed=[run['threshold_layer'] for col in case['columns'] for run in col['connected_depth_runs'] if run['contains_original_core']];self.assertEqual(len(seed),1)
            for key in ['lower_depth_m','lower_status','lower_last_connected_depth_m']:self.assertEqual(seed[0][key],primary[key])
            self.assertIsNone(case['physical_thickness_m']);self.assertIsNone(case['volume_m3'])

    def test_decoded_binary32_evidence_and_exact_reproduction_are_explicit(self):
        manifest=json.loads((derive.ROOT/'research/source-data/north-brazil-depth-sections-v1/manifest.json').read_bytes());self.assertEqual(manifest['decoded_velocity_cell_pairs'],63440);self.assertEqual(manifest['decoded_velocity_array_bytes'],507520)
        for case in self.report['cases']:self.assertTrue(case['legacy_binary32_component_reproduction_exact'])


if __name__=='__main__':unittest.main()
