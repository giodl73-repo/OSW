import copy
import unittest
from unittest.mock import patch
import check_dimoune_2023_width_browser_v1 as browser
import dimoune_2023_width_presentation_v1 as presentation

class BrowserScopeTests(unittest.TestCase):
    def test_local_browser_refuses_before_payload_or_artifact_access(self):
        with patch.object(browser.os,'name','nt'),patch.object(browser.Path,'read_bytes',side_effect=AssertionError('No local payload access')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):browser.main()

    def test_exact_saved_file_inventory_and_manifest_required(self):
        result=browser.read(browser.SAVED+'result.json')
        self.assertEqual(len(browser.saved_files(result)),18)
        bad=copy.deepcopy(result);bad['wasm_sha256']='0'*64
        with self.assertRaises(ValueError):browser.saved_files(bad)
        bad=copy.deepcopy(result);bad['generated_files']['almanac/query-engine.manifest.json']['sha256']='0'*64
        with self.assertRaises(ValueError):browser.saved_files(bad)

    def test_presentation_changes_only_five_static_files(self):
        parent_raw=(browser.ROOT/(browser.SAVED+'engine-manifest.json')).read_bytes()
        scope=browser.read('research/dimoune-2023-width-presentation-scope-v1.json')
        parent=browser.read(browser.SAVED+'engine-manifest.json')
        result=presentation.presentation_manifest(parent_raw,scope,'a'*40)
        changed={p for p,pin in result['sha256'].items() if pin!=parent['sha256'].get(p)}
        self.assertEqual(changed,presentation.FILES)
        self.assertEqual(result['sha256']['almanac/query-engine.wasm'],parent['sha256']['almanac/query-engine.wasm'])
        self.assertEqual(result['sha256']['almanac/query-data.json'],parent['sha256']['almanac/query-data.json'])
        bad=copy.deepcopy(scope);bad['source_changes']['almanac/query-engine.wasm']=next(iter(scope['source_changes'].values()))
        with self.assertRaises(ValueError):presentation.presentation_manifest(parent_raw,bad,'a'*40)

if __name__=='__main__':unittest.main()
