"""Complete BoundarySubsurface cohorts retain original5/10cm/s primary thresholds and gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_boundary_subsurface_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class BoundarySubsurfaceCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all60cases_fourowners_and_twocohorts_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],60);self.assertEqual(set(r['counts_by_current']),{'current:mauritanian','current:baffin','current:pacific-north-subsurface-countercurrent','current:atlantic-north-equatorial-undercurrent'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'mauritania-baffin':40,'northern':20});self.assertLess(len(self.raw),2400000)
    def test_original41interior_and19unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':41,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':19})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':20,'0.1':40})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:mauritanian':.1,'current:baffin':.05,'current:pacific-north-subsurface-countercurrent':.1,'current:atlantic-north-equatorial-undercurrent':.1}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_each_original_cohort_dates_remain_individual_snapshots(self):
        self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),60)
        for cohort in self.op['cohorts']:
            sourceop=json.loads((derive.ROOT/cohort['source_operator']).read_bytes());self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases'] if c['cohort_id']==cohort['id']},set(sourceop['snapshot_times_utc']))
    def test_no_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            for k in ['physical_current_bottom_established','water_mass_classification_performed','named_current_axis_independently_validated','annual_extrema_established']:self.assertFalse(c[k])
            for k in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[k])
        for k in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[k],0)
    def test_original_vertical_rules_and_counts_reused(self):
        import derive_surface_regional_velocity_curtains_v1 as prior
        self.assertIs(derive.frozen.curtain,kernel.curtain);self.assertIs(derive.counts,prior.counts)
    def test_incomplete_duplicate_or_wrong_operator_cohort_rejected(self):
        for key,value in [('section_files',self.op['cohorts'][0]['section_files'][:-1]),('source_operator',self.op['cohorts'][1]['source_operator']),('id','other')]:
            c=copy.deepcopy(self.op['cohorts'][0]);c[key]=value
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)

    def test_original_frames_strata_and_null_surface_gates(self):
        expected={'current:mauritanian':(0,[50,300]),'current:baffin':(180,[100,300]),'current:pacific-north-subsurface-countercurrent':(90,[100,400]),'current:atlantic-north-equatorial-undercurrent':(90,[100,400])}
        for c in self.report['cases']:
            op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};bearing,interval=expected[c['entity_id']]
            self.assertEqual(c['component_bearing_degrees_true'],bearing);self.assertEqual(config['selection_depth_interval_m'],interval);self.assertEqual(config['core_search_depth_interval_m'],interval);self.assertIsNone(config['surface_component_gate_m_s'])
    def test_geometry_adapter_only_adds_tag_and_validates_before_adaptation(self):
        for cohort in self.op['cohorts']:
            op=json.loads((derive.ROOT/cohort['source_operator']).read_bytes())
            for file in cohort['section_files']:
                source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);config={**op,**op['currents'][source['entity_id']]};view=derive.geometry_view(source,config,cohort['id'])
                self.assertEqual(source,before);self.assertEqual(view.pop('source_section_geometry'),derive.AXES[cohort['id']]);self.assertEqual(view,source)
            bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=-1
            with self.assertRaises(ValueError):derive.geometry_view(bad,config,cohort['id'])
            bad=copy.deepcopy(source);bad['section_definition']['fixed_axis']='latitude' if derive.AXES[cohort['id']]=='longitude' else 'longitude'
            with self.assertRaises(ValueError):derive.geometry_view(bad,config,cohort['id'])


if __name__=='__main__':unittest.main()
