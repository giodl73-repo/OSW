import copy
import json
from pathlib import Path
import unittest
import chen_indian_sec_engine_manifest_v2 as module

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_bytes())


class ManifestProvenance(unittest.TestCase):
    def fixture(self):
        # Metadata only; never open a packet, index bundle or WASM binary.
        parent=read('research/pacific-nec-nominal-width-installation-saved-engine-manifest-v1.json')
        pref=read('research/chen-indian-sec-delivery-preflight-v3.json')
        inventory=read('research/chen-indian-sec-delivery-run-v3/compile-inventory.json')
        scope=read('research/chen-indian-sec-presentation-source-scope-v1.json')
        replacements={**pref['input_sha256'],**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256']}
        options={'scope':scope,'inventory':inventory,
                 'allowed_changes':set(pref['runtime_source_changes'])|{'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'},
                 'proof':read('research/chen-indian-sec-delivery-run-v3/dependency-proof.json'),
                 'compiler':'rustc 1.95.0 fixture','source_commit':'fixture',
                 'logical_sha':'000ec593c4fd1eb597a0a7204824b5c8c8e19cd8e2683080095a46ec50609cb1',
                 'wasm_sha':read('research/chen-indian-sec-delivery-run-v3/compare-main.json')['wasm_sha256']}
        return parent,replacements,options

    def test_real_frozen_input_metadata_constructs_manifest_with_historical_controls(self):
        parent,replacements,options=self.fixture()
        result=module.engine_manifest(parent,replacements,**options)
        self.assertEqual(result['sha256'][module.PHASE],parent['sha256'][module.PHASE])
        provenance=result[module.KEY]['delivery_source_provenance_v2']
        self.assertEqual(provenance['operational_inputs'][module.PHASE]['current_sha256'],replacements[module.PHASE])
        for p in module.PRESENTATION|module.ADDED:self.assertEqual(result['sha256'][p],replacements[p])
        for k in parent:
            if k not in ('sha256','rustc'):self.assertEqual(result[k],parent[k])
        self.assertEqual(result['sha256']['almanac/query-engine.wasm'],options['wasm_sha'])
        for p,h in parent['sha256'].items():
            if p not in replacements and p!='almanac/query-engine.wasm':self.assertEqual(result['sha256'][p],h)

    def test_rejects_incorrect_or_broadened_scopes(self):
        for change in ('old_pin','new_pin','extra_ui','compiled_control','phase_pin','added_pin'):
            parent,replacements,options=self.fixture();scope=options['scope']
            if change=='old_pin':scope['presentation_source_changes']['almanac/query.html']['parent_sha256']='0'*64
            elif change=='new_pin':replacements['almanac/query.html']='0'*64
            elif change=='extra_ui':scope['presentation_source_changes']['unrelated.js']={}
            elif change=='compiled_control':options['proof']['production_dependencies'].append(module.PHASE)
            elif change=='phase_pin':scope['operational_inputs'][module.PHASE]['current_sha256']='0'*64
            else:scope['added_presentation_sha256']['almanac/regional-model-atlas.js']='0'*64
            with self.subTest(change=change),self.assertRaises(ValueError):
                module.engine_manifest(parent,replacements,**options)


if __name__=='__main__':unittest.main()
