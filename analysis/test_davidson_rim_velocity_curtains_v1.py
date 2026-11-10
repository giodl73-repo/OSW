"""Davidson and Rim retain original mixed geometry and positive surface qualification."""
import copy,json,unittest
from unittest.mock import patch
import derive_davidson_rim_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class DavidsonRimCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):
            cls.batches=[derive.build(owner=owner) for owner in derive.BATCH_COUNTS]
        cases=[c for report,raw in cls.batches for c in report['cases']];cls.raw=max((raw for report,raw in cls.batches),key=len)
        cls.report={**cls.batches[0][0],'cases':cases,'counts':derive.counts(cases),'counts_by_cohort':{'davidson-rim':derive.counts(cases)},'counts_by_current':{owner:derive.counts([c for c in cases if c['entity_id']==owner]) for owner in derive.BATCH_COUNTS},'counts_by_primary_threshold_m_s':{str(v):derive.counts([c for c in cases if c['velocity_threshold_m_s']==v]) for v in [.05,.1]}}
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all32cases_twoowners_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],32);self.assertEqual(set(r['counts_by_current']),{'current:davidson', 'current:black-sea-rim'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'davidson-rim':32});self.assertLess(len(self.raw),2400000)
    def test_original23interior_and9unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':23,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':9})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':0,'0.1':32})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:davidson':.1,'current:black-sea-rim':.1}
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
    def test_frozen_tracing_body_graph_and_counts_reused(self):
        import ast,inspect
        import derive_surface_regional_velocity_curtains_v1 as prior
        for name in ['component','runs','connected_layer']:self.assertIs(getattr(derive.frozen,name),getattr(kernel,name))
        self.assertEqual(ast.dump(ast.parse(inspect.getsource(derive.frozen.curtain))),ast.dump(ast.parse(inspect.getsource(kernel.curtain))))
        self.assertIs(derive.counts,prior.counts)
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator','research/wrong-operator.json'),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:davidson')
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c,'current:davidson')

    def test_two_bounded_batches_cover_exact_original_plan(self):
        files=[]
        for report,raw in self.batches:
            self.assertLess(len(raw),2400000);self.assertEqual(report['source_plan_case_count'],32);self.assertEqual(report['counts']['cases'],derive.BATCH_COUNTS[report['batch_current_id']]);self.assertEqual(set(report['counts_by_current']),{report['batch_current_id']});files.extend(c['source_file'] for c in report['cases'])
        self.assertEqual(len(files),32);self.assertEqual(len(set(files)),32)
        with self.assertRaises(ValueError):derive.build()
    def test_original_surface_validator_and_classic_selector_bindings(self):
        import surface_qualified_mixed_geometry_v1 as original
        import acquire_three_current_depth_sections_v1 as classic
        self.assertIs(derive.frozen.validate_retained,original.validate_retained);self.assertIs(derive.frozen.diagnose,classic.diagnose)
    def test_source_frames_windows_surface_rules_and_geometry_preserved(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for c in self.report['cases']:
            owner=c['entity_id'];config={**op,**op['currents'][owner]};self.assertEqual(c['component_bearing_degrees_true'],0 if owner=='current:davidson' else 90);self.assertEqual(config['surface_component_gate_m_s'],.05);self.assertIsNone(config['temperature_gate']);self.assertEqual(config['selection_depth_interval_m'],[0,200]);self.assertEqual(config['core_search_depth_interval_m'],[0,200]);self.assertEqual(c['source_geometry'],derive.SOURCE_AXES[owner]);self.assertNotIn('geometry_adapter',c);self.assertTrue(c['original_surface_velocity_qualification_applied']);self.assertEqual(c['original_surface_component_gate_m_s'],.05);self.assertFalse(c['surface_gate_requires_primary_surface_connectivity'])
    def test_source_unchanged_and_original_geometry_time_diagnosis_mutations_rejected(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for owner in derive.BATCH_COUNTS:
            file=self.op['cohorts'][0]['section_files_by_current'][owner][0];source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);config={**op,**op['currents'][owner]};derive.source_curtain(source,config,file);self.assertEqual(source,before)
            distance_key='nearest_latitude_distance_km' if derive.SOURCE_AXES[owner]=='latitude' else 'maximum_nearest_longitude_distance_km'
            for key,value in [('component_bearing_degrees_true',(config['component_bearing_degrees_true']+90)%360),(distance_key,999),('source_returned_timestamp_utc','2022-01-16T00:00:00Z')]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(bad,config,file)
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.source_curtain(bad,config,file)

    def test_no_qualification_gate_and_support_edges_remain_distinct(self):
        from collections import Counter
        statuses=Counter(c['original_horizontal_selection_status'] for c in self.report['cases'])
        self.assertEqual(statuses['no_qualifying_surface_connected_component_column'],5);self.assertEqual(statuses['section_gate_edge_maximum_axis_unresolved'],3);self.assertEqual(statuses['upper_layer_support_edge_maximum_axis_unresolved'],1)
        for c in self.report['cases']:
            if c['original_horizontal_selection_status']=='no_qualifying_surface_connected_component_column':self.assertIsNone(c['original_selected_column_index']);self.assertIsNone(c['original_primary_layer']);self.assertEqual(c['columns'],[])
    def test_original_schema_geometry_and_surface_qualification_required(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes())
        for owner in derive.BATCH_COUNTS:
            file=self.op['cohorts'][0]['section_files_by_current'][owner][0];source=json.loads((derive.ROOT/file).read_bytes());config={**op,**op['currents'][owner]}
            for key,value in [('source_section_geometry','longitude' if derive.SOURCE_AXES[owner]=='latitude' else 'latitude'),('schema','invented'),('surface_velocity_qualification_applied',False),('surface_component_gate_m_s',None)]:
                bad=copy.deepcopy(source);bad[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):derive.source_curtain(bad,config,file)
            bad_config=copy.deepcopy(config);bad_config['surface_component_gate_m_s']=None
            with self.assertRaises(ValueError):derive.source_curtain(source,bad_config,file)
    def modified_fixture(self,entity,surface):
        import test_davidson_rim_surface_qualified_depth_sections_v1 as original
        from sample_eac_hycom_route_depth_v1 import canonical_hash,along_velocity
        original.DavidsonRimSurfaceQualifiedSourceTests.setUpClass();fixture=original.DavidsonRimSurfaceQualifiedSourceTests();p,c=fixture.source(entity);column=p['columns'][1]
        if surface is None:column['eastward_velocity_m_s'][0]=None;column['northward_velocity_m_s'][0]=None;column['signed_reference_component_m_s'][0]=None
        else:
            u,v=(0.,surface) if c['component_bearing_degrees_true']==0 else (surface,0.)
            column['eastward_velocity_m_s'][0]=u;column['northward_velocity_m_s'][0]=v;column['signed_reference_component_m_s'][0]=float(along_velocity(u,v,c['component_bearing_degrees_true']))
        p['decoded_columns_sha256']=canonical_hash(p['columns']);p['diagnosis']=derive.frozen.diagnose(p['depth_levels_m'],[col['signed_reference_component_m_s'] for col in p['columns']],c)
        return p,c
    def test_qualifying_surface_does_not_force_primary_isotach_to_surface(self):
        for owner in derive.BATCH_COUNTS:
            p,c=self.modified_fixture(owner,.08);result=derive.frozen.curtain(p,c,'fixture');self.assertEqual(result['original_selected_column_index'],1);self.assertGreater(result['original_primary_layer']['upper_depth_m'],0);self.assertTrue(result['columns']);seed=[run for col in result['columns'] for run in col['connected_depth_runs'] if run['contains_original_core']];self.assertEqual(len(seed),1);self.assertGreater(seed[0]['native_depth_indices_inclusive'][0],0)
    def test_opposed_weak_or_missing_surface_does_not_turn_deep_jet_into_davidson(self):
        for owner in derive.BATCH_COUNTS:
            for surface in [-.2,.04,None]:
                p,c=self.modified_fixture(owner,surface);result=derive.frozen.curtain(p,c,'fixture');self.assertIsNone(result['original_selected_column_index']);self.assertEqual(result['status'],'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN');self.assertEqual(result['columns'],[])


if __name__=='__main__':unittest.main()
