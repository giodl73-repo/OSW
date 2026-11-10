import copy
import json
from pathlib import Path
import unittest
import pacific_nec_product_axis_browser_presentation_v1 as presentation

ROOT=Path(__file__).resolve().parents[1]
class PresentationBoundary(unittest.TestCase):
    def fixture(self):return json.loads((ROOT/'research/pacific-nec-product-axis-delivery-run-v1/engine-manifest.json').read_bytes()),json.loads((ROOT/'research/pacific-nec-product-axis-presentation-scope-v1.json').read_bytes())
    def test_only_five_declared_hashes_change_and_every_historical_namespace_survives(self):
        parent,scope=self.fixture();child=presentation.presentation_manifest(parent,scope,'test')
        self.assertEqual({k for k in child['sha256'] if child['sha256'][k]!=parent['sha256'].get(k)},presentation.CHANGED)
        for key in parent:
            if key!='sha256':self.assertEqual(child[key],parent[key])
    def test_scientific_source_addition_or_rebuild_claim_is_refused(self):
        for key in ['scientific_inputs_changed','matching_binary_changed','native_or_wasm_rebuild_required']:
            parent,scope=self.fixture();scope[key]=True
            with self.assertRaises(ValueError):presentation.presentation_manifest(parent,scope,'test')
        parent,scope=self.fixture();scope['source_changes']['rust/osw-query/src/lib.rs']={'parent_sha256':'a'*64,'candidate_sha256':'b'*64}
        with self.assertRaises(ValueError):presentation.presentation_manifest(parent,scope,'test')
    def test_changed_parent_asset_is_refused(self):
        parent,scope=self.fixture();parent['sha256']['almanac/query.html']='c'*64
        with self.assertRaises(ValueError):presentation.presentation_manifest(parent,scope,'test')

if __name__=='__main__':unittest.main()
