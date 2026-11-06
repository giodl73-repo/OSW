import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import chen_indian_sec_browser_contract_v1 as contract
import check_chen_indian_sec_browser_v1 as browser

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_bytes())


class SavedBrowserContract(unittest.TestCase):
    def test_refuses_local_browser_before_any_payload_access(self):
        with patch.dict('os.environ',{},clear=True),patch.object(browser,'read') as read:
            with self.assertRaisesRegex(ValueError,'Scoped cloud browser only'):browser.controls()
            read.assert_not_called()

    def test_only_exact_verified_engine_is_accepted(self):
        result=read('research/chen-indian-sec-delivery-run-v4/result.json')
        self.assertEqual(len(contract.verify_saved_result(result)),18)
        for key,value in [('wasm_sha256','0'*64),('historical_main_queries',214),('installed',True),('rust_tests_passed',True)]:
            broken=copy.deepcopy(result);broken[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):contract.verify_saved_result(broken)

    def test_navigation_overlay_preserves_binary_and_all_other_manifest_fields(self):
        old=read('research/chen-indian-sec-delivery-run-v4/engine-manifest.json')
        scope=read('research/chen-indian-sec-query-navigation-source-scope-v1.json')
        new=contract.navigation_manifest(old,scope,'browser-source')
        self.assertEqual({k for k in new if k not in old},{contract.NAV_KEY})
        for key in old:
            if key!='sha256':self.assertEqual(new[key],old[key])
        changed={p for p in old['sha256'] if old['sha256'][p]!=new['sha256'][p]}
        self.assertEqual(changed,contract.NAV_PATHS)
        self.assertEqual(new['sha256']['almanac/query-engine.wasm'],contract.BINARY)
        for change in ('old_pin','extra_path','repeat'):
            broken=copy.deepcopy(scope);parent=old
            if change=='old_pin':broken['source_changes']['almanac/query.js']['parent_sha256']='0'*64
            elif change=='extra_path':broken['source_changes']['unrelated.js']={}
            else:parent=new
            with self.subTest(change=change),self.assertRaises(ValueError):contract.navigation_manifest(parent,broken,'source')


if __name__=='__main__':unittest.main()
