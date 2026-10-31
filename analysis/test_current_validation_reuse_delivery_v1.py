import copy
import os
import unittest
from unittest.mock import patch
import atlantic_nsec_reference_query_v1 as query
import atlantic_nsec_reference_index_v1 as index
import current_validation_reuse_engine_v1 as engine
import check_current_validation_reuse_delivery_v1 as delivery

class ValidationReuseDeliveryTests(unittest.TestCase):
    def test_local_delivery_refuses_before_any_payload_or_compiler_access(self):
        with patch.object(os,'name','nt'),patch.object(delivery.Path,'read_bytes',side_effect=AssertionError('No local bulk reads')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):delivery.run()

    def fixture(self):
        parent=query.read('research/current-core-dimensions-installation-saved-engine-manifest-v1.json')
        inventory=copy.deepcopy(query.read('research/atlantic-nsec-reference-delivery-run-v1/compile-inventory.json'))
        for p in inventory['rust_source_sha256']:inventory['rust_source_sha256'][p]=query.sha(p)
        inventory['rust_source_sha256'][engine.MODULE]=query.sha(engine.MODULE)
        proof=copy.deepcopy(query.read('research/atlantic-nsec-reference-delivery-run-v1/dependency-proof.json'))
        proof['production_dependencies']=sorted(set(proof['production_dependencies'])|{engine.MODULE});proof['production_dependency_count']=len(proof['production_dependencies'])
        replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256'],**{p:query.sha(p) for p in engine.PRESENTATION|set(index.DOCUMENTS)},'almanac/query-engine.wasm':'e'*64}
        options=dict(inventory=inventory,proof=proof,source_commit='fixture',logical_sha=engine.LOGICAL,wasm_sha='e'*64,compiler='rustc 1.95.0 (fixture)',source_documents=index.DOCUMENTS)
        return parent,replacements,options

    def test_complete_new_compiler_and_active_client_bindings_preserve_historical_namespaces(self):
        parent,replacements,options=self.fixture();result=engine.engine_manifest(parent,replacements,**options)
        self.assertEqual(result[engine.KEY]['dependency_proof']['production_dependency_count'],287)
        self.assertFalse(result[engine.KEY]['validation_reuse']['results_survive_scope_exit'])
        self.assertEqual(result[engine.KEY]['logical_sha256'],engine.LOGICAL)
        self.assertEqual({k:v for k,v in result.items() if k not in ['sha256','rustc',engine.KEY]},{k:v for k,v in parent.items() if k not in ['sha256','rustc']})

    def test_changed_data_incomplete_closure_or_unrelated_client_binding_refused(self):
        parent,replacements,options=self.fixture()
        with self.assertRaises(ValueError):engine.engine_manifest(parent,replacements,**{**options,'logical_sha':'0'*64})
        with self.assertRaises(ValueError):engine.engine_manifest(parent,{**replacements,'almanac/query-charts.js':'0'*64},**options)
        with self.assertRaises(ValueError):engine.engine_manifest(parent,{p:v for p,v in replacements.items() if p!=engine.MODULE},**options)
        incomplete=copy.deepcopy(options);incomplete['proof']['production_dependency_count']=286
        with self.assertRaises(ValueError):engine.engine_manifest(parent,replacements,**incomplete)

if __name__=='__main__':unittest.main()
