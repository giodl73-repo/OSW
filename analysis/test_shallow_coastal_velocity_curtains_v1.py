"""Complete ShallowCoastal cohorts retain original5/10cm/s primary thresholds and gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_shallow_coastal_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class ShallowCoastalCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all96cases_sixowners_and_threecohorts_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],96);self.assertEqual(set(r['counts_by_current']),{'current:norwegian-coastal','current:tsushima','current:guiana','current:east-greenland-coastal','current:gaspe','current:jutland'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'coastal-upper-layer':32,'guiana-egcc-upper-layer':32,'gaspe-jutland-shallow':32});self.assertLess(len(self.raw),2400000)
    def test_original47interior_and49unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':47,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':49})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.1':96})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={owner:.1 for owner in self.report['counts_by_current']}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_quarterly_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),96)
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

    def test_source_specific_frames_strata_and_no_surface_gate_preserved(self):
        expected={'current:norwegian-coastal':(0,[0,100]),'current:tsushima':(60,[0,200]),'current:guiana':(315,[0,100]),'current:east-greenland-coastal':(225,[0,100]),'current:gaspe':(90,[0,30]),'current:jutland':(0,[0,30])}
        for c in self.report['cases']:
            op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};bearing,interval=expected[c['entity_id']]
            self.assertEqual(c['component_bearing_degrees_true'],bearing);self.assertEqual(config['selection_depth_interval_m'],interval);self.assertEqual(config['core_search_depth_interval_m'],interval);self.assertIsNone(config['surface_component_gate_m_s'])
    def test_original_geometry_tags_and_source_bytes_unchanged(self):
        for cohort in self.op['cohorts']:
            op=json.loads((derive.ROOT/cohort['source_operator']).read_bytes())
            for file in cohort['section_files']:
                raw=(derive.ROOT/file).read_bytes();source=json.loads(raw);before=copy.deepcopy(source);config={**op,**op['currents'][source['entity_id']]};self.assertEqual(source['source_section_geometry'],source['section_definition']['fixed_axis']);derive.frozen.curtain(source,config,file);self.assertEqual(source,before);self.assertEqual((derive.ROOT/file).read_bytes(),raw)


if __name__=='__main__':unittest.main()
