"""Independent projection and preservation checks against bounded metadata."""
import copy
import json
import unittest
from unittest.mock import patch
import dimoune_2023_width_query_v1 as query
import dimoune_2023_width_delivery_rules_v1 as rules
import dimoune_2023_width_index_v1 as index
import dimoune_2023_width_engine_v1 as engine

class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=query.build_contract()

    def test_basin_width_query_and_full_matching_scene_survive_pagination(self):
        req={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'atlantic-south-equatorial'}],'limit':1,'offset':1}
        old={'ok':True,'total':0,'rows':[],'chart_scene':None,'offset':1,'limit':1}
        expected=rules.expected_query(req,old,self.contract,{'widths':[]})
        self.assertEqual(expected['total'],4);self.assertEqual(len(expected['rows']),1)
        self.assertEqual(len(expected['chart_scene']['width_records']),4)
        self.assertEqual(expected['chart_scene']['entity_id'],'current:atlantic-south-equatorial')
        bad=copy.deepcopy(expected);bad['chart_scene']['width_records'][0]['width_range_km']=[70,550]
        with self.assertRaises(ValueError):rules.verify_response(expected,bad)

    def test_source_query_adds_one_matching_publication(self):
        req={'collection':'sources','filters':[{'field':'id','op':'eq','value':self.contract['new_source']['id']}],'limit':100}
        expected=rules.expected_query(req,{'total':0,'rows':[]},self.contract,{'sources':self.contract['prior_source_inventory']})
        self.assertEqual(expected['rows'],[self.contract['new_source']]);self.assertEqual(expected['total'],1)

    def test_family_object_query_remains_unmodified(self):
        row=self.contract['prior_owners']['current:south-equatorial']['objects'][0]
        old={'rows':[row],'total':1,'taxonomy_scope':{'root_id':'current:south-equatorial'}}
        expected=rules.expected_query({'collection':'objects','taxonomy':{'root_id':row['id']}},old,self.contract,{})
        self.assertEqual(expected,old)

    def test_dashboard_changes_only_declared_fields(self):
        old={'entries':[self.contract['prior_owners'][owner]['objects'][0] for owner in query.OWNERS],
            'snapshot_fingerprint':'previous','counts':{'named_current':111},'unrelated':'preserve'}
        new=rules.dashboard_document(old,self.contract)
        self.assertEqual(new['counts'],old['counts']);self.assertEqual(new['unrelated'],'preserve')
        self.assertNotEqual(new['snapshot_fingerprint'],old['snapshot_fingerprint'])
        self.assertEqual(next(r for r in new['entries'] if r['id']=='current:atlantic-south-equatorial')['capabilities']['scoped_width'],4)

    def test_mixed_scene_preserves_old_scenes_in_order(self):
        first={'kind':'published_current_dimension_evidence','title':'Prior study'}
        last={'kind':'another_scoped_width','title':'Unrelated'}
        old={'kind':'scoped_width_comparisons','scenes':[first,last]}
        addition=rules.scene(self.contract['width_records'],None,self.contract)
        result=rules.merge_width_scene(old,addition)
        self.assertEqual(result['scenes'],[first,addition,last]);self.assertIsNone(addition['entity_id'])

    def test_index_refuses_original_replacements_and_local_access(self):
        audit={'original_sources_verified':656,'original_source_strings_preserved':656,'replaced_source_paths':[],
            'added_source_paths':index.DOCUMENTS,'scientific_source_documents_replaced':0}
        index.verify_audit(audit)
        audit['replaced_source_paths']=['research/ocean-current-width-inventory.json']
        with self.assertRaises(ValueError):index.verify_audit(audit)
        with patch.dict(index.os.environ,{'GITHUB_ACTIONS':'false'}):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):index.controls()

    def test_engine_refuses_unrelated_scientific_rebinding(self):
        parent=query.read('research/pacific-nec-product-axis-installation-saved-engine-manifest-v1.json')
        inventory=query.read('research/dimoune-2023-width-runtime-run-v1/compile-inventory.json')
        proof=query.read('research/dimoune-2023-width-runtime-run-v1/dependency-proof.json')
        # Synthetic proof fixture follows the new uninstalled contract filename;
        # actual compilation is independently verified only by the cloud job.
        old='research/dimoune-2023-width-query-contract-v1.json'
        inventory['compile_time_data_sha256'].pop(old)
        inventory['compile_time_data_sha256'][query.FILE]=query.sha(query.FILE)
        module='rust/osw-query/src/dimoune_section_widths.rs'
        inventory['rust_source_sha256'][module]=query.sha(module)
        proof['production_dependencies']=[query.FILE if path==old else path for path in proof['production_dependencies']]
        replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256'],
            **{p:query.sha(p) for p in engine.PRESENTATION},'almanac/query-engine.wasm':'1'*64}
        args=dict(inventory=inventory,proof=proof,source_commit='2'*40,logical_sha='3'*64,wasm_sha='1'*64,
            compiler='rustc 1.95.0 synthetic-test',source_documents=index.DOCUMENTS)
        result=engine.engine_manifest(parent,replacements,**args)
        self.assertEqual(result[engine.KEY]['scoped_width_records_after'],185)
        path='research/ocean-current-width-inventory.json';replacements[path]='4'*64
        with self.assertRaisesRegex(ValueError,'Unrelated engine input'):engine.engine_manifest(parent,replacements,**args)

if __name__=='__main__':unittest.main()
