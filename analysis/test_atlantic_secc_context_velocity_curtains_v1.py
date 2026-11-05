"""Preserve both original contexts without turning shared source cases into new bodies."""
import copy,json,unittest
from unittest.mock import patch
import derive_atlantic_secc_context_velocity_curtains_v1 as derive


class AtlanticContextCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No retrieval')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP')):
            cls.batches={context:derive.build(context=context) for context in derive.CONTEXTS}
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes());cls.source_op=json.loads((derive.ROOT/derive.SOURCE_OPERATOR).read_bytes());cls.cfg={**cls.source_op,**cls.source_op['currents'][derive.OWNER]}
    def test_two_contexts_one_owner_sixteen_shared_source_cases(self):
        keys=[]
        for context,(report,raw) in self.batches.items():
            self.assertEqual(report['entity_id'],derive.OWNER);self.assertEqual(report['diagnostic_context_id'],context);self.assertEqual(report['counts']['cases'],16);self.assertEqual(report['source_plan_case_count'],16);self.assertLess(len(raw),2400000);keys.append({(c['source_file'],c['source_sha256']) for c in report['cases']})
        self.assertEqual(keys[0],keys[1]);self.assertEqual(len(keys[0]),16)
    def test_shallow_original_ten_contours_six_unresolved(self):
        self.assertEqual(self.batches['shallow'][0]['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':10,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':6})
    def test_every_context_candidate_core_primary_layer_and_boundary_reproduces(self):
        for context,(report,raw) in self.batches.items():
            for c in report['cases']:
                section=json.loads((derive.ROOT/c['source_file']).read_bytes());d=section['context_diagnoses'][context]['diagnosis'];self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['source_context_diagnosis_sha256'],derive.digest(derive.encode(d)));self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
                primary=d['selected_column_threshold_layers'][1] if d['selected_column_index'] is not None else None;self.assertEqual(c['original_primary_layer'],primary)
                if c['columns']:
                    seeds=[run for col in c['columns'] for run in col['connected_depth_runs'] if run['contains_original_core']];self.assertEqual(len(seeds),1);self.assertEqual(seeds[0]['threshold_layer'],primary)
    def test_entire_validated_tracer_and_original_context_helpers_unchanged(self):
        import native_velocity_depth_curtain_v2 as kernel
        import atlantic_secc_depth_contexts_v1 as original
        import mixed_interval_section_geometry_v1 as geometry
        self.assertIs(derive.frozen.curtain,kernel.curtain);self.assertIs(derive.original,original);self.assertIs(derive.frozen.validate_retained,geometry.validate_retained)
    def test_reversible_context_view_preserves_every_source_field(self):
        for file in self.op['section_files']:
            source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source)
            for context in derive.CONTEXTS:
                view,cfg=derive.context_view(source,self.cfg,context);view['diagnosis']=copy.deepcopy(view['context_diagnoses']['shallow']['diagnosis']);self.assertEqual(view,source);self.assertEqual(source,before)
    def test_original_windows_frame_null_gates_and_native_geometry(self):
        for context,(report,raw) in self.batches.items():
            expected={'shallow':[0,100],'deep':[150,350]}[context]
            for c in report['cases']:
                self.assertEqual(c['selection_depth_interval_m'],expected);self.assertEqual(c['core_search_depth_interval_m'],expected);self.assertEqual(c['component_bearing_degrees_true'],90);self.assertEqual(c['velocity_threshold_m_s'],.1);self.assertEqual(c['source_geometry'],'longitude');self.assertFalse(c['source_arrays_changed']);self.assertFalse(c['diagnostic_view_changes_source_bytes'])
        self.assertIsNone(self.cfg['surface_component_gate_m_s']);self.assertIsNone(self.cfg['temperature_gate'])
    def test_non_additive_contexts_never_independent_observations_or_extra_currents(self):
        for context,(report,raw) in self.batches.items():
            self.assertFalse(report['vertical_contexts_are_additive']);self.assertFalse(report['contexts_are_independent_observations']);self.assertEqual(report['source_default_diagnostic_context_id'],'shallow')
            for c in report['cases']:self.assertFalse(c['vertical_contexts_are_additive']);self.assertFalse(c['contexts_are_independent_observations']);self.assertEqual(c['entity_id'],derive.OWNER)
    def test_all_four_quarterly_dates_exactly_once_per_section_per_context(self):
        for context,(report,raw) in self.batches.items():
            self.assertEqual({c['snapshot_time_utc'] for c in report['cases']},set(self.source_op['snapshot_times_utc']));self.assertEqual(len({(c['section_id'],c['snapshot_time_utc']) for c in report['cases']}),16)
    def test_unresolved_selections_keep_original_indices_layers_and_empty_curtains(self):
        for context,(report,raw) in self.batches.items():
            for c in report['cases']:
                self.assertFalse(c['core_reselected'])
                if c['original_horizontal_selection_status']!=derive.frozen.INTERIOR:self.assertEqual(c['status'],'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN');self.assertEqual(c['columns'],[])
    def test_mutation_of_either_context_diagnosis_rejected_before_tracing(self):
        file=self.op['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes())
        for target in derive.CONTEXTS:
            for requested in derive.CONTEXTS:
                bad=copy.deepcopy(source);bad['context_diagnoses'][target]['diagnosis']['selected_column_index']=-1
                with self.assertRaises(ValueError):derive.source_curtain(bad,self.cfg,file,requested)
    def test_wrong_context_schema_owner_geometry_and_non_additive_flags_rejected(self):
        file=self.op['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes())
        for field,value in [('schema','invented'),('entity_id','current:other'),('source_section_geometry','latitude'),('default_diagnostic_context_id','deep'),('vertical_contexts_are_additive',True),('contexts_are_independent_observations',True)]:
            bad=copy.deepcopy(source);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):derive.source_curtain(bad,self.cfg,file,'shallow')
    def test_modified_window_primary_cutoff_surface_gate_and_frame_rejected(self):
        file=self.op['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes())
        for field,value in [('component_bearing_degrees_true',270),('surface_component_gate_m_s',.05)]:
            bad=copy.deepcopy(self.cfg);bad[field]=value
            with self.assertRaises(ValueError):derive.source_curtain(source,bad,file,'deep')
        for field,value in [('selection_depth_interval_m',[100,350]),('primary_threshold_m_s',.05)]:
            bad=copy.deepcopy(self.cfg);bad['diagnostic_contexts']['deep'][field]=value
            with self.assertRaises(ValueError):derive.source_curtain(source,bad,file,'deep')
    def test_geometry_component_time_and_native_hash_mutations_rejected(self):
        file=self.op['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes())
        for field,value in [('component_bearing_degrees_true',270),('maximum_nearest_longitude_distance_km',999),('source_returned_timestamp_utc','2022-01-01T00:00:00Z'),('decoded_columns_sha256','0'*64)]:
            bad=copy.deepcopy(source);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):derive.source_curtain(bad,self.cfg,file,'deep')
    def test_explicit_context_required(self):
        for context in [None,'all','alternate']:
            with self.assertRaises(ValueError):derive.build(context=context)
    def test_no_physical_bottom_area_volume_annual_or_runtime_promotion(self):
        for context,(report,raw) in self.batches.items():
            for key in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(report[key],0)
            self.assertFalse(report['runtime_changed']);self.assertFalse(report['full_goal_complete'])
            for c in report['cases']:
                for key in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[key])
                for key in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[key])


if __name__=='__main__':unittest.main()
