import copy,csv,hashlib,io,json,unittest
import build_current_depth_projection_member_index_v2 as p
from load_current_depth_projection_inventory_v1 import load_inventory


class MemberProjectionDiscoveryRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read=staticmethod(lambda f:(p.ROOT/f).read_bytes())
        cls.op=json.loads(cls.read(p.OPERATOR));cls.manifest=json.loads(cls.read(cls.op['projection_inventory_file']))
        cls.source=json.loads(cls.read(cls.op['member_reference_index_file']));cls.membership=json.loads(cls.read(cls.op['membership_file']))
        cls.view=load_inventory(cls.manifest,cls.read)
        cls.index,cls.gaps,cls.pieces=p.build()

    def test_every_link_resolves_to_exact_original_case_and_member_owner(self):
        by_id={r['id']:r for r in self.view['projections']+self.view['unresolved_reference_cases']}
        for parent in self.index['records']:
            for member in parent['members']:
                for ref in member['regional_projection_refs']+member['unresolved_reference_case_refs']:
                    raw=self.read(ref['source_file']);self.assertEqual(hashlib.sha256(raw).hexdigest(),ref['source_sha256'])
                    data=json.loads(raw)
                    for key in ref['source_pointer'].strip('/').split('/'):data=data[int(key)] if isinstance(data,list) else data[key]
                    self.assertEqual(data,by_id[ref['case_id']]);self.assertEqual(data['entity_id'],member['entity_id']);self.assertEqual(ref['owner_entity_id'],member['entity_id'])
                    self.assertEqual(ref['case_scope'],{k:data[k] for k in ref['case_scope']})

    def test_all_declared_members_preserved_and_shared_cases_deduplicated(self):
        self.assertEqual(self.index['counts']['parents'],9);self.assertEqual(self.index['counts']['member_links'],23)
        for parent,original in zip(self.index['records'],self.source['records']):
            self.assertEqual([m['entity_id'] for m in parent['members']],[m['entity_id'] for m in original['members']])
            for member,old in zip(parent['members'],original['members']):self.assertEqual(member['source_depth_reference_ids'],old['depth_reference_ids'])
        rows=list(csv.DictReader(io.StringIO(self.pieces['member-case-links.csv'].decode())))
        self.assertGreater(len(rows),len({r['case_id'] for r in rows}))
        self.assertEqual(len({(r['source_file'],r['source_pointer'],r['case_id']) for r in rows}),self.index['counts']['deduplicated_source_case_references'])

    def test_missing_members_remain_gaps_and_unresolved_cases_never_count_as_supported(self):
        for parent in self.index['records']:
            expected=[]
            for member in parent['members']:
                supported={c['id'] for c in self.view['projections'] if c['entity_id']==member['entity_id']}
                blocked={c['id'] for c in self.view['unresolved_reference_cases'] if c['entity_id']==member['entity_id']}
                self.assertEqual({r['case_id'] for r in member['regional_projection_refs']},supported)
                self.assertEqual({r['case_id'] for r in member['unresolved_reference_case_refs']},blocked)
                if not supported:expected.append(member['entity_id'])
            self.assertEqual(parent['members_without_supported_regional_cases'],expected)

    def test_parent_depths_ranges_and_volumes_remain_unknown(self):
        for parent in self.index['records']:
            for key in ['parent_depth_m','parent_depth_range_m','parent_volume_km3','aggregation_operator']:self.assertIsNone(parent[key])
            self.assertFalse(parent['parent_depth_values_inherited']);self.assertFalse(parent['whole_route_depth_profile_established']);self.assertFalse(parent['volume_eligible'])
        self.assertEqual(self.index['counts']['new_projection_cases'],0);self.assertEqual(self.index['counts']['new_measurements'],0)
        self.assertFalse(self.index['query_ui_integration_performed'])

    def test_gap_audit_is_exact_complement_without_reclassifying_own_coverage(self):
        expected={r['entity_id'] for r in self.view['records'] if not r['projection_ids']}
        self.assertEqual({r['entity_id'] for r in self.gaps['records']},expected);self.assertEqual(len(expected),27)
        self.assertEqual(self.index['regional_projection_counts_unchanged'],self.view['counts'])
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],84)
        self.assertEqual(self.view['counts']['regional_projection_scenarios'],235)
        jutland=next(r for r in self.gaps['records'] if r['entity_id']=='current:jutland')
        self.assertEqual(jutland['gap_kind'],'regional_model_cases_unresolved');self.assertEqual(len(jutland['own_unresolved_reference_case_ids']),4)

    def test_changed_membership_owners_duplicates_and_aliases_rejected(self):
        for mutation in ['duplicate','unknown','alias','parent']:
            source=copy.deepcopy(self.source);membership=copy.deepcopy(self.membership)
            if mutation=='duplicate':membership['conventions'][0]['members'].append(membership['conventions'][0]['members'][0])
            if mutation=='unknown':source['records'][0]['members'][0]['entity_id']='current:invented'
            if mutation=='alias':source['records'][0]['identity_level']='current'
            if mutation=='parent':source['records'][0]['mapping_source_pointer']='/conventions/999'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):p.index_view(self.manifest,self.view,source,membership,self.read)

    def test_every_input_pin_matches_and_corrupt_source_piece_is_rejected(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256(self.read(f)).hexdigest(),pin)
        part=self.manifest['addenda'][-1]['json']['file']
        with self.assertRaises(ValueError):load_inventory(self.manifest,lambda f:self.read(f)+b' ' if f==part else self.read(f))
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))



    def test_atlantic_secc_dual_contexts_linked_and_pacific_neuc_stays_missing(self):
        self.assertEqual(self.index['counts']['parents_with_all_declared_members_projected'],8)
        missing={e for parent in self.index['records'] for e in parent['members_without_supported_regional_cases']}
        self.assertEqual(missing,{'current:pacific-north-equatorial-undercurrent'})
        parent=next(r for r in self.index['records'] if r['entity_id']=='current:south-equatorial-countercurrent')
        member=next(r for r in parent['members'] if r['entity_id']=='current:atlantic-south-equatorial-countercurrent')
        self.assertEqual(len(member['regional_projection_refs']),8)
        self.assertEqual({r['case_scope']['diagnostic_context_id'] for r in member['regional_projection_refs']},{'shallow','deep'})
        for ref in member['regional_projection_refs']:
            self.assertFalse(ref['case_scope']['vertical_contexts_are_additive']);self.assertFalse(ref['case_scope']['contexts_are_independent_observations'])
        rows=list(csv.DictReader(io.StringIO(self.pieces['member-case-links.csv'].decode())))
        for row in rows:
            if row['member_entity_id']=='current:atlantic-south-equatorial-countercurrent':
                self.assertIn(row['diagnostic_context_id'],['shallow','deep']);self.assertEqual(row['vertical_contexts_are_additive'],'False');self.assertEqual(row['contexts_are_independent_observations'],'False')

if __name__=='__main__':unittest.main()
