"""Exact complete cohorts,immutable selection and explicit unresolved cases."""
import copy,json,unittest
from unittest.mock import patch
import derive_mediterranean_regional_velocity_curtains_v2 as derive
import native_velocity_depth_curtain_v2 as frozen


class MediterraneanCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all72cases_fourowners_and_two_cohorts_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],72);self.assertEqual(set(r['counts_by_current']),{'current:balearic','current:ligurian','current:northern-mediterranean','current:algerian'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'balearic-ligurian':32,'mediterranean-boundary':40});self.assertLess(len(self.raw),2400000)
    def test_original63interior_and9unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':63,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':9})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_quarterly_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'})
        self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),72)
    def test_no_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            for k in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[k])
            for k in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[k])
        for k in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[k],0)
    def test_original_curtain_function_used_without_copy_or_retune(self):
        import derive_surface_regional_velocity_curtains_v1 as prior
        self.assertIs(derive.counts,prior.counts);self.assertIs(derive.frozen.curtain,frozen.curtain);self.assertEqual(frozen.component([0,10],[[.2,.1],[.1,.3],[0,0]],0,0,.1),{(0,0)})
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator',self.op['cohorts'][1]['source_operator']),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)
    def test_legacy_adapter_only_adds_declared_tag_after_original_validation(self):
        cohort=self.op['cohorts'][1];file=cohort['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);op=json.loads((derive.ROOT/cohort['source_operator']).read_bytes());config={**op,**op['currents'][source['entity_id']]}
        view,adapter=derive.geometry_view(source,config,cohort['id']);self.assertEqual(source,before);self.assertNotIn('source_section_geometry',source);self.assertEqual(view['source_section_geometry'],'longitude');del view['source_section_geometry'];self.assertEqual(view,source);self.assertEqual(adapter,'LEGACY_LONGITUDE_VALIDATED_THEN_IN_MEMORY_GEOMETRY_TAG_ONLY')
        for c in self.report['cases']:self.assertEqual(c['geometry_adapter'],'LEGACY_LONGITUDE_VALIDATED_THEN_IN_MEMORY_GEOMETRY_TAG_ONLY' if c['cohort_id']=='mediterranean-boundary' else 'ORIGINAL_MIXED_GEOMETRY_TAG')
    def test_scopes_have_own_source_intervals_and_frames(self):
        for cohort in self.op['cohorts']:
            source=json.loads((derive.ROOT/cohort['source_operator']).read_bytes())
            for c in [v for v in self.report['cases'] if v['cohort_id']==cohort['id']]:self.assertEqual(c['component_bearing_degrees_true'],source['currents'][c['entity_id']]['component_bearing_degrees_true'])
            self.assertEqual(source['core_search_depth_interval_m'],[0,200])

    def test_exact_source_primary_thresholds_balearic_five_others_ten_cm(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':16,'0.1':56})
        for c in self.report['cases']:
            self.assertEqual(c['velocity_threshold_m_s'],.05 if c['entity_id']=='current:balearic' else .1)
            if c['entity_id']=='current:balearic':self.assertEqual(c['original_primary_layer']['threshold_m_s'],.05)
    def test_all56_non_balearic_entire_cases_match_retained_v1_exactly(self):
        previous=json.loads((derive.ROOT/'research/mediterranean-regional-velocity-depth-curtains-v1.json').read_bytes());old={c['source_file']:c for c in previous['cases']};checked=0
        for c in self.report['cases']:
            if c['entity_id']=='current:balearic':continue
            self.assertEqual(c,old[c['source_file']]);checked+=1
        self.assertEqual(checked,56)
    def test_balearic_uses_original_five_cm_seed_and_leaves_sources_unchanged(self):
        previous=json.loads((derive.ROOT/'research/mediterranean-regional-velocity-depth-curtains-v1.json').read_bytes());old={c['source_file']:c for c in previous['cases']}
        for c in self.report['cases']:
            if c['entity_id']!='current:balearic':continue
            raw=(derive.ROOT/c['source_file']).read_bytes();source=json.loads(raw);before=copy.deepcopy(source);op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};view,adapter=derive.geometry_view(source,config,c['cohort_id']);current=derive.frozen.curtain(view,config,c['source_file'])
            self.assertEqual(current['original_primary_layer'],source['diagnosis']['selected_column_threshold_layers'][0]);self.assertEqual(current['original_selected_column_index'],old[c['source_file']]['original_selected_column_index']);self.assertEqual(old[c['source_file']]['velocity_threshold_m_s'],.1);self.assertEqual(source,before);self.assertEqual((derive.ROOT/c['source_file']).read_bytes(),raw)


if __name__=='__main__':unittest.main()
