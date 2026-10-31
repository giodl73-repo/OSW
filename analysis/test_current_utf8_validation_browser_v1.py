import copy
import os
import unittest
from unittest.mock import patch
import check_current_utf8_validation_browser_v1 as rebuilt

class RebuiltBrowserTests(unittest.TestCase):
    def test_local_browser_refuses_before_payload_access_or_global_configuration(self):
        prior=rebuilt.browser.SAVED
        with patch.object(os,'name','nt'),patch.object(rebuilt.Path,'read_bytes',side_effect=AssertionError('No local payload')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):rebuilt.run()
        self.assertEqual(rebuilt.browser.SAVED,prior)

    def test_exact_rebuilt_engine_metadata_has_eighteen_files(self):
        result=rebuilt.browser.read(rebuilt.SAVED+'result.json')
        self.assertEqual(len(rebuilt.validate_candidate(result)),18)

    def test_direct_manifest_mode_preserves_exact_bytes_without_reading_an_old_overlay(self):
        raw=b'{"verified":"candidate"}\n'
        with patch.object(rebuilt.Path,'read_bytes',side_effect=AssertionError('No old overlay read')):
            bound,updates=rebuilt.browser.bind_client_manifest(raw,False)
        self.assertIs(bound,raw)
        self.assertEqual(updates,[])

    def test_changed_custody_binary_manifest_test_count_or_file_inventory_refused(self):
        original=rebuilt.browser.read(rebuilt.SAVED+'result.json')
        for key,value in [('source_commit','old'),('rust_tests_passed',314),('logical_sha256','0'*64),('wasm_sha256','0'*64)]:
            with self.assertRaises(ValueError):rebuilt.validate_candidate({**original,key:value})
        for path in ['almanac/query-engine.manifest.json','almanac/query-engine.wasm']:
            changed=copy.deepcopy(original);changed['generated_files'][path]['sha256']='0'*64
            with self.assertRaises(ValueError):rebuilt.validate_candidate(changed)
        changed=copy.deepcopy(original);changed['generated_files'].pop('almanac/query-engine.wasm')
        with self.assertRaises(ValueError):rebuilt.validate_candidate(changed)

if __name__=='__main__':unittest.main()
