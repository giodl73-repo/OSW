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

    def test_corrected_saved_engine_already_binds_current_presentation(self):
        manifest=browser.read(browser.SAVED+'engine-manifest.json')
        for path in presentation.FILES:self.assertEqual(manifest['sha256'][path],browser.sha(path))
        self.assertEqual(manifest['sha256']['almanac/query-engine.wasm'],browser.BINARY)
        result=browser.read(browser.SAVED+'result.json')
        self.assertEqual(result['query_contract_file'],'research/dimoune-2023-width-query-contract-v2.json')
        self.assertEqual(result['packet_comparison']['width_records_added'],6)

if __name__=='__main__':unittest.main()
