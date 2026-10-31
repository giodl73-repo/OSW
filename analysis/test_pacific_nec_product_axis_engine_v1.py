import copy
import hashlib
import json
from pathlib import Path
import unittest
import pacific_nec_product_axis_engine_v1 as engine

ROOT=Path(__file__).resolve().parents[1]
class CompleteEngineBinding(unittest.TestCase):
    def fixture(self):
        parent=json.loads((ROOT/'research/chen-indian-sec-installation-saved-engine-manifest-v1.json').read_bytes())
        inventory=json.loads((ROOT/'research/pacific-nec-product-axis-runtime-run-v1/compile-inventory.json').read_bytes())
        proof=json.loads((ROOT/'research/pacific-nec-product-axis-runtime-run-v1/dependency-proof.json').read_bytes())
        replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256']}
        for p in engine.PRESENTATION|engine.ADDED:replacements[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
        replacements['almanac/query-engine.wasm']='b'*64
        return parent,replacements,{'inventory':inventory,'proof':proof,'source_commit':'candidate','logical_sha':'a'*64,'wasm_sha':'b'*64,'compiler':'rustc 1.95.0 test','source_documents':[engine.CONTRACT]}
    def test_every_historical_namespace_and_unrelated_hash_is_preserved(self):
        parent,replacements,kwargs=self.fixture();result=engine.engine_manifest(parent,replacements,**kwargs)
        for key in parent:
            if key not in ('sha256','rustc'):self.assertEqual(result[key],parent[key])
        for key,value in parent['sha256'].items():
            if key not in replacements:self.assertEqual(result['sha256'][key],value)
        self.assertEqual(result[engine.KEY]['new_reported_lengths'],0)
    def test_unrelated_compiled_data_and_control_rebinding_are_refused(self):
        for path in ['research/current-gap-delivery-phase.json','research/ocean-motion-dashboard.json']:
            parent,replacements,kwargs=self.fixture();replacements[path]='f'*64
            if path in kwargs['inventory']['compile_time_data_sha256']:kwargs['inventory']['compile_time_data_sha256'][path]='f'*64
            with self.assertRaisesRegex(ValueError,'Unrelated'):engine.engine_manifest(parent,replacements,**kwargs)
    def test_missing_production_input_or_required_dependency_is_refused(self):
        parent,replacements,kwargs=self.fixture();del replacements[engine.CONTRACT]
        with self.assertRaises(ValueError):engine.engine_manifest(parent,replacements,**kwargs)
        parent,replacements,kwargs=self.fixture();kwargs['proof']['production_dependencies'].remove(engine.CONTRACT)
        with self.assertRaises(ValueError):engine.engine_manifest(parent,replacements,**kwargs)
    def test_new_input_cannot_overwrite_an_existing_engine_source(self):
        parent,replacements,kwargs=self.fixture();parent['sha256']['almanac/surface-product-axes.js']='c'*64
        with self.assertRaises(ValueError):engine.engine_manifest(parent,replacements,**kwargs)

if __name__=='__main__':unittest.main()
