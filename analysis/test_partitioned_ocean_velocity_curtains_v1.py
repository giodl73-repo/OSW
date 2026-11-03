"""Complete PartitionedOcean cohorts retain original5/10cm/s primary thresholds and gaps."""
import copy,json,unittest
from unittest.mock import patch
import derive_partitioned_ocean_velocity_curtains_v1 as derive
import native_velocity_depth_curtain_v2 as kernel


class PartitionedOceanCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No ocean retrieval allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No HTTP allowed')):cls.report,cls.raw=derive.build()
        cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes())
    def test_all64cases_twoowners_and_cohort_present(self):
        r=self.report;self.assertEqual(r['counts']['cases'],64);self.assertEqual(set(r['counts_by_current']),{'current:south-atlantic','current:tasman-front'});self.assertEqual({k:v['cases'] for k,v in r['counts_by_cohort'].items()},{'partitioned-ocean':64});self.assertLess(len(self.raw),2400000)
    def test_original53interior_and11unresolved_remain(self):
        self.assertEqual(self.report['counts']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':53,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':11})
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':self.assertEqual(c['columns'],[])
    def test_threshold_contexts_counted_separately(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_primary_threshold_m_s'].items()},{'0.05':32,'0.1':32})
    def test_original_source_primary_threshold_is_preserved_on_every_case(self):
        expected={'current:south-atlantic':.05,'current:tasman-front':.1}
        for c in self.report['cases']:self.assertEqual(c['velocity_threshold_m_s'],expected[c['entity_id']])
    def test_original_core_and_boundaries_exact_for_every_source(self):
        for c in self.report['cases']:
            source=json.loads((derive.ROOT/c['source_file']).read_bytes());op=json.loads((derive.ROOT/c['source_operator']).read_bytes());config={**op,**op['currents'][c['entity_id']]};d=source['diagnosis'];self.assertEqual(c['original_horizontal_selection_status'],d['horizontal_selection_status']);self.assertEqual(c['original_selected_column_index'],d['selected_column_index']);self.assertEqual(c['source_sha256'],derive.digest((derive.ROOT/c['source_file']).read_bytes()))
            if c['columns']:self.assertEqual(c['original_primary_layer'],d['selected_column_threshold_layers'][config['thresholds_m_s'].index(config['primary_threshold_m_s'])]);self.assertEqual(sum(v['contains_original_core'] for col in c['columns'] for v in col['connected_depth_runs']),1)
    def test_quarterly_dates_remain_individual_snapshots(self):
        self.assertEqual({c['snapshot_time_utc'] for c in self.report['cases']},{'2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'});self.assertEqual(len({(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in self.report['cases']}),64)
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
            with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)
        c=copy.deepcopy(self.op['cohorts'][0]);c['section_files'][-1]=c['section_files'][0]
        with self.assertRaises(ValueError):derive.derive_cohort(derive.ROOT,c)

    def test_four_search_partitions_remain_two_owners_without_cross_partition_join(self):
        self.assertEqual({k:v['cases'] for k,v in self.report['counts_by_partition'].items()},{'sac-northern-search':16,'sac-southern-search':16,'tasman-north-bank-search':16,'tasman-south-bank-search':16});self.assertFalse(self.report['partition_profile_counts_are_independent_observation_counts'])
        for c in self.report['cases']:
            self.assertEqual(c['search_partition_kind'],'editorial_latitude_search_context');self.assertFalse(c['partition_is_current_identity']);self.assertFalse(c['cross_partition_join_performed']);self.assertFalse(c['front_or_water_mass_classification_performed']);self.assertEqual(c['component_bearing_degrees_true'],90)
    def test_original_partition_validators_and_tag_only_adapter_preserve_sources(self):
        import current_depth_search_partitions_v1 as original
        self.assertIs(derive.validate_partitions,original.validate_partitions);self.assertIs(derive.validate_section_partition,original.validate_section_partition)
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes());derive.validate_partitions(op)
        for file in self.op['cohorts'][0]['section_files']:
            source=json.loads((derive.ROOT/file).read_bytes());before=copy.deepcopy(source);config={**op,**op['currents'][source['entity_id']]};view=derive.geometry_view(source,config);self.assertEqual(view.pop('source_section_geometry'),'longitude');self.assertEqual(view,source);self.assertEqual(source,before)
    def test_partition_owner_window_and_physical_identity_mutations_rejected(self):
        op=json.loads((derive.ROOT/self.op['cohorts'][0]['source_operator']).read_bytes());file=self.op['cohorts'][0]['section_files'][0];source=json.loads((derive.ROOT/file).read_bytes());config={**op,**op['currents'][source['entity_id']]}
        for key,value in [('search_partition_id','invented'),('entity_id','current:tasman-front'),('front_or_water_mass_classification_performed',True)]:
            bad=copy.deepcopy(source);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):derive.geometry_view(bad,config)
        bad=copy.deepcopy(source);bad['section_definition']['latitude_gate_degrees_north'][0]-=.1
        with self.assertRaises(ValueError):derive.geometry_view(bad,config)


if __name__=='__main__':unittest.main()
