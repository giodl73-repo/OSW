import copy
import os
import unittest
from unittest.mock import patch
import atlantic_nsec_reference_query_v1 as query
import atlantic_nsec_reference_index_v1 as index
import atlantic_nsec_reference_engine_v1 as engine
import atlantic_nsec_reference_response_rules_v1 as rules
import check_atlantic_nsec_reference_delivery_v1 as delivery


class DeliveryScopeTests(unittest.TestCase):
    def test_local_delivery_and_index_refuse_before_payload_access(self):
        with patch.object(os,'name','nt'),patch.object(delivery.Path,'read_bytes',side_effect=AssertionError('No payload reads')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):delivery.controls()
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):index.controls()

    def test_all_678_original_source_strings_and_seven_additions_required(self):
        expected={'original_sources_verified':678,'original_source_strings_preserved':678,'replaced_source_paths':[],
            'added_source_paths':index.DOCUMENTS,'scientific_source_documents_replaced':0}
        self.assertEqual(len(index.DOCUMENTS),7);index.verify_audit(expected)
        for key,value in [('original_source_strings_preserved',677),('replaced_source_paths',['old.json']),('added_source_paths',index.DOCUMENTS[:-1])]:
            with self.assertRaises(ValueError):index.verify_audit({**expected,key:value})

    def test_empty_table_page_retains_both_source_bound_routes_on_map(self):
        c=query.build_contract();request={'collection':'reference_routes','filters':[{'field':'current_id','op':'eq','value':'atlantic-south-equatorial'}],'limit':1,'offset':2}
        old={'total':0,'rows':[],'map_scene':{'projection':'equirectangular_display_only','view_box':[0,0,360,180],
            'matching_objects':0,'mapped_objects':0,'unmapped_objects':0,'features':[],'omitted_features':[],
            'inspection_collection':'reference_routes','scope':'retained scope'}}
        result=rules.expected_query(request,old,c,{'reference_routes':[]})
        self.assertEqual(result['rows'],[]);self.assertEqual(result['total'],2)
        self.assertEqual(result['map_scene']['mapped_objects'],2)
        self.assertEqual({f['entity_id'] for f in result['map_scene']['features']},{r['id'] for r in c['routes']})
        self.assertTrue(result['map_scene']['features'][0]['primitive']['d'].startswith('M 180.00000 88.00000 '))
        self.assertTrue(all(f['role']=='editorial_reference_route' for f in result['map_scene']['features']))

    def test_family_queries_do_not_inherit_member_map_geometry(self):
        c=query.build_contract()
        self.assertFalse(rules.owner_selected({'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:south-equatorial'}]},c))
        self.assertTrue(rules.owner_selected({'collection':'objects','taxonomy':{'root_id':'current:south-equatorial','relation':'children','include_root':False}},c))
        self.assertFalse(rules.owner_selected({'collection':'objects','taxonomy':{'root_id':query.OWNER,'relation':'ancestors','include_root':False}},c))

    def test_full_compiler_closure_and_unrelated_binding_refusal(self):
        parent=query.read('research/current-core-dimensions-installation-saved-engine-manifest-v1.json')
        inventory=copy.deepcopy(query.read('research/current-core-dimensions-delivery-run-v1/compile-inventory.json'))
        for p in inventory['rust_source_sha256']:inventory['rust_source_sha256'][p]=query.sha(p)
        for p in engine.RUST_ADDED:inventory['rust_source_sha256'][p]=query.sha(p)
        inventory['compile_time_data_sha256'][engine.CONTRACT]=query.sha(engine.CONTRACT)
        proof=copy.deepcopy(query.read('research/current-core-dimensions-delivery-run-v1/dependency-proof.json'))
        proof['production_dependencies']=sorted(set(proof['production_dependencies'])|engine.RUST_ADDED|{engine.CONTRACT})
        proof['production_dependency_count']=len(proof['production_dependencies']);self.assertEqual(proof['production_dependency_count'],286)
        replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256'],
            **{p:query.sha(p) for p in engine.PRESENTATION|set(index.DOCUMENTS)},'almanac/query-engine.wasm':'e'*64}
        options=dict(inventory=inventory,proof=proof,source_commit='fixture',logical_sha='f'*64,wasm_sha='e'*64,compiler='rustc 1.95.0 (fixture)',source_documents=index.DOCUMENTS)
        result=engine.engine_manifest(parent,replacements,**options)
        self.assertEqual(result[engine.KEY]['reference_route_records_after'],85)
        self.assertEqual({k:v for k,v in result.items() if k not in ['sha256','rustc',engine.KEY]},{k:v for k,v in parent.items() if k not in ['sha256','rustc']})
        with self.assertRaises(ValueError):engine.engine_manifest(parent,{**replacements,'almanac/query-charts.js':'0'*64},**options)

    def test_workflow_selector_and_full_output_paths(self):
        body=(query.ROOT/'.github/workflows/atlantic-nsec-reference-delivery-v1.yml').read_text(encoding='utf8')
        self.assertEqual(body.count(delivery.REQUEST),3)
        self.assertIn(delivery.OUT.relative_to(query.ROOT).as_posix()+'/',body)
        self.assertIn(delivery.WORK.relative_to(query.ROOT).as_posix()+'/artifact/',body)
        self.assertIn('analysis/check_atlantic_nsec_reference_delivery_v1.py',body)
        self.assertIn('group: osw-current-gap-delivery',body)
        self.assertEqual(len(delivery.new_requests(query.build_contract())),20)


if __name__=='__main__':unittest.main()
