import copy
import os
import unittest
from unittest.mock import patch
import current_core_dimensions_query_v1 as query
import current_core_dimensions_index_v1 as index
import current_core_dimensions_engine_v1 as engine
import check_current_core_dimensions_delivery_v1 as delivery

class DeliveryTests(unittest.TestCase):
    def test_local_cloud_controls_refuse_before_packet_or_index_access(self):
        with patch.object(os,'name','nt'),patch.object(delivery.Path,'read_bytes',side_effect=AssertionError('No packet/index reads')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):delivery.controls()
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):index.controls()

    def test_all_prior_index_documents_and_six_additions_required(self):
        expected={'original_sources_verified':672,'original_source_strings_preserved':672,'replaced_source_paths':[],'added_source_paths':index.DOCUMENTS,'scientific_source_documents_replaced':0}
        index.verify_audit(expected)
        for key,value in [('original_source_strings_preserved',671),('replaced_source_paths',['old.json']),('added_source_paths',index.DOCUMENTS[:-1])]:
            changed={**expected,key:value}
            with self.assertRaises(ValueError):index.verify_audit(changed)

    def test_entire_production_closure_and_unrelated_input_refusal(self):
        parent=query.read('research/pacific-sec-gourdeau-2008-installation-saved-engine-manifest-v1.json')
        inventory=copy.deepcopy(query.read('research/pacific-sec-gourdeau-2008-delivery-run-v2/compile-inventory.json'))
        for p in inventory['rust_source_sha256']:inventory['rust_source_sha256'][p]=query.sha(p)
        for p in engine.RUST_ADDED:inventory['rust_source_sha256'][p]=query.sha(p)
        inventory['compile_time_data_sha256'][engine.CONTRACT]=query.sha(engine.CONTRACT)
        proof=copy.deepcopy(query.read('research/pacific-sec-gourdeau-2008-delivery-run-v2/dependency-proof.json'))
        proof['production_dependencies']=sorted(set(proof['production_dependencies'])|engine.RUST_ADDED|{engine.CONTRACT})
        proof['production_dependency_count']=len(proof['production_dependencies']);self.assertEqual(proof['production_dependency_count'],284)
        replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256'],**{p:query.sha(p) for p in engine.PRESENTATION|set(index.DOCUMENTS)},'almanac/query-engine.wasm':'e'*64}
        options=dict(inventory=inventory,proof=proof,source_commit='fixture',logical_sha='f'*64,wasm_sha='e'*64,compiler='rustc 1.95.0 (fixture)',source_documents=index.DOCUMENTS)
        result=engine.engine_manifest(parent,replacements,**options)
        self.assertEqual(result[engine.KEY]['regional_reach_records_after'],4)
        self.assertEqual({k:v for k,v in result.items() if k not in ['sha256','rustc',engine.KEY]},{k:v for k,v in parent.items() if k not in ['sha256','rustc']})
        with self.assertRaises(ValueError):engine.engine_manifest(parent,{**replacements,'almanac/query-charts.js':'0'*64},**options)

    def test_workflow_pins_selector_driver_and_both_output_directories(self):
        body=(query.ROOT/'.github/workflows/current-core-dimensions-delivery-v1.yml').read_text()
        self.assertEqual(body.count(delivery.REQUEST),3)
        self.assertIn(str(delivery.OUT.relative_to(query.ROOT)).replace('\\','/')+'/',body)
        self.assertIn(str(delivery.WORK.relative_to(query.ROOT)).replace('\\','/')+'/artifact/',body)
        self.assertIn('analysis/check_current_core_dimensions_delivery_v1.py',body)
        self.assertIn('group: osw-current-gap-delivery',body)
        self.assertEqual(len(delivery.new_requests(query.build_contract())),18)

if __name__=='__main__':unittest.main()
