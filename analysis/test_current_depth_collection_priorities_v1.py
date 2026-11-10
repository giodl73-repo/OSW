import copy,csv,hashlib,io,json,unittest
import build_current_depth_collection_priorities_v1 as p
from load_current_depth_projection_inventory_v1 import load_inventory
from load_current_depth_reference_inventory_v2 import load_inventory as load_references


class CollectionPriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.index,cls.gaps,cls.audit,cls.pieces=p.build();read=lambda f:json.loads((p.ROOT/f).read_bytes());reader=lambda f:(p.ROOT/f).read_bytes();cls.manifest=read(cls.op['projection_inventory_file']);cls.view=load_inventory(cls.manifest,reader);cls.refs=load_references(read(cls.op['reference_inventory_file']),reader);cls.lengths=read(cls.op['length_register_file']);cls.source=read(cls.op['member_reference_index_file']);cls.membership=read(cls.op['membership_file']);cls.case_refs=p.case_references(cls.manifest,reader)
    def test_all111owners_and_302supported27blocked_cases_retained_with_exact_pointers(self):
        self.assertEqual(len(self.audit['records']),111);summaries=[c for r in self.audit['records'] for c in r['cases']];self.assertEqual(len(summaries),329);self.assertEqual({c['case_id'] for c in summaries},{c['id'] for c,ref in self.case_refs})
        for s in summaries:
            value=json.loads((p.ROOT/s['source_file']).read_bytes())
            for key in s['source_pointer'].split('/')[1:]:value=value[int(key)] if isinstance(value,list) else value[key]
            self.assertEqual(value['id'],s['case_id']);self.assertEqual(value['entity_id'],s['owner_entity_id']);self.assertEqual(hashlib.sha256((p.ROOT/s['source_file']).read_bytes()).hexdigest(),s['source_sha256'])
    def test_gap_list_refreshed_to15_without_claiming_new_measurements(self):
        self.assertEqual(self.gaps['counts']['identities_without_own_supported_regional_cases'],15);self.assertEqual(len(self.gaps['records']),15);self.assertEqual(self.audit['model_projection_counts_unchanged'],self.view['counts']);self.assertEqual(self.audit['reference_counts_unchanged'],self.refs['counts']);self.assertEqual(self.audit['counts']['new_measurements'],0);self.assertEqual(self.audit['counts']['new_projection_cases'],0)
    def test_qualified_mean_cross_sections_explicitly_not_along_current_profiles(self):
        rows=[r for r in self.audit['records'] if r['priority_kind']=='cross_sections_without_along_current_profile'];self.assertEqual({r['entity_id'] for r in rows},{'current:west-australian','current:pacific-north-equatorial-undercurrent'})
        for r in rows:
            self.assertEqual(r['supported_mean_cross_section_count'],4);self.assertEqual(r['other_supported_regional_case_count'],0)
            for c in r['cases']:self.assertEqual(c['geometry_class'],'sampled_qualified_mean_cross_section');self.assertFalse(c['declared_length_route_key_match']);self.assertIsNone(c['case_scope']['snapshot_time_utc']);self.assertEqual(c['case_scope']['nominal_provider_period'],'1994_01_2015_12');self.assertFalse(c['case_scope']['axis_selection_applied'])
    def test_route_key_match_is_not_coverage_and_no_length_ratio_is_computed(self):
        case={'id':'test','entity_id':'current:test','route_id':'same','route_file':'file.json','anchors':[]};ref={'case_id':'test'};length={'selected_route_id':'same','record_file':'file.json'}
        summary=p.case_summary(case,ref,length);self.assertTrue(summary['declared_length_route_key_match']);self.assertFalse(summary['full_current_route_depth_coverage_established']);self.assertIsNone(summary['canonical_route_length_fraction_computed'])
        field={**case,'field_geometry_kind':'native_zonal_mean_field_section_not_along_current_axis'};self.assertFalse(p.case_summary(field,ref,length)['declared_length_route_key_match'])
        with self.assertRaises(ValueError):p.case_summary({**case,'field_geometry_kind':'unknown'},ref,length)
    def test_legacy_unspecified_eligibility_not_counted_as_rejected_or_missing(self):
        case={'anchors':[{'distance_km':0},{'lower_projection_eligible':True},{'lower_projection_eligible':False}],'segments':[]};summary=p.case_summary(case,{}, {'selected_route_id':None,'record_file':'x'})
        self.assertEqual(summary['anchor_occurrence_count'],3);self.assertEqual(summary['anchors_with_explicit_lower_eligibility'],2);self.assertEqual(summary['eligible_lower_anchor_occurrences'],1);self.assertEqual(summary['legacy_or_other_metric_anchor_occurrences'],1)
        with self.assertRaises(ValueError):p.case_summary({'anchors':[{'lower_projection_eligible':1}]},{},{'selected_route_id':None,'record_file':'x'})
    def test_member_case_scopes_preserve_mean_branch_non_additive_and_method_metadata(self):
        originals={c['id']:c for c,ref in self.case_refs};qualified=0
        for parent in self.index['records']:
            for m in parent['members']:
                for ref in m['regional_projection_refs']+m['unresolved_reference_case_refs']:
                    case=originals[ref['case_id']]
                    for key in p.SCOPE_KEYS:
                        if key in case:self.assertEqual(ref['case_scope'][key],case[key])
                    if case.get('field_geometry_kind'):
                        qualified+=1;self.assertIsNone(ref['case_scope']['snapshot_time_utc']);self.assertFalse(ref['case_scope']['mean_is_mean_of_instantaneous_depths'])
        self.assertGreater(qualified,0)
    def test_member_reference_ids_use_latest715reference_view_without_parent_inheritance(self):
        refs={r['entity_id']:r for r in self.refs['records']}
        for parent in self.index['records']:
            self.assertIsNone(parent['parent_depth_m']);self.assertIsNone(parent['parent_depth_range_m']);self.assertIsNone(parent['parent_volume_km3']);self.assertFalse(parent['parent_depth_values_inherited'])
            for m in parent['members']:self.assertEqual(m['source_depth_reference_ids'],refs[m['entity_id']]['depth_reference_ids'])
        self.assertEqual(self.index['counts']['parents'],9);self.assertEqual(self.index['counts']['distinct_member_identities'],20)
    def test_gap_reference_counts_include_new_redsox_and_pgw_evidence(self):
        gaps={r['entity_id']:r for r in self.gaps['records']};self.assertEqual(gaps['current:red-sea-saline-overflow']['own_source_depth_reference_count'],13);self.assertEqual(gaps['current:persian-gulf-saline-overflow']['own_source_depth_reference_count'],3)
    def test_case_scope_csv_is_valid_json_and_neuc_detachment_context_flags_survive(self):
        rows=list(csv.DictReader(io.StringIO(self.pieces['member-case-links.csv'].decode())));source={c['id']:ref['case_scope'] for c,ref in self.case_refs}
        for row in rows:self.assertEqual(json.loads(row['case_scope_json']),source[row['case_id']]);self.assertEqual(row['parent_depth_m'],'');self.assertEqual(row['parent_volume_km3'],'')
        neuc=[json.loads(r['case_scope_json']) for r in rows if r['member_entity_id']=='current:pacific-north-equatorial-undercurrent'];self.assertTrue(neuc)
        for scope in neuc:self.assertTrue(scope['primary_detached_layer_required']);self.assertTrue(scope['independent_latitude_context_required'])
    def test_priority_csv_matches_all_catalog_records_and_has_no_measurement_values(self):
        rows=list(csv.DictReader(io.StringIO(self.pieces['collection-priorities.csv'].decode())));self.assertEqual([r['entity_id'] for r in rows],[r['entity_id'] for r in sorted(self.audit['records'],key=lambda r:(r['collection_priority_rank'],r['entity_id']))]);self.assertEqual(len(rows),111)
        for row in rows:self.assertNotIn('depth_m',row);self.assertNotIn('volume_km3',row);self.assertTrue(row['next_collection_action'])
    def test_catalog_join_mutations_fail_before_creating_a_queue(self):
        for kind in ['missing','duplicate']:
            lengths=copy.deepcopy(self.lengths)
            if kind=='missing':lengths['records'].pop()
            if kind=='duplicate':lengths['records'].append(lengths['records'][0])
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.build_audit(self.manifest,self.view,self.refs,lengths,self.source,self.membership,lambda f:(p.ROOT/f).read_bytes())
    def test_all_global_depth_volume_annual_and_coverage_values_remain_unknown(self):
        for row in self.audit['records']:self.assertIsNone(row['depth_m']);self.assertIsNone(row['annual_depth_range_m']);self.assertIsNone(row['volume_km3']);self.assertFalse(row['full_current_route_depth_coverage_established']);self.assertIsNone(row['canonical_route_length_fraction_computed']);self.assertFalse(row['regional_cases_are_independent_observations'])
        self.assertEqual(self.audit['counts']['full_current_route_depth_coverage_established'],0);self.assertFalse(self.audit['runtime_changed']);self.assertFalse(self.audit['query_ui_integration_performed']);self.assertFalse(self.audit['full_goal_complete'])
    def test_input_pins_and_fixed_per_file_caps(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))


if __name__=='__main__':unittest.main()
