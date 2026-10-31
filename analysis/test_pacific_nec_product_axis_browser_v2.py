import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import check_pacific_nec_product_axis_browser_v2 as browser

class SavedEngineBrowserScope(unittest.TestCase):
    def test_local_browser_is_refused_before_source_or_payload_access(self):
        with patch.object(browser.os,'name','nt'),patch.object(browser.Path,'read_bytes',side_effect=AssertionError('No local payload access')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):browser.main()
    def test_only_the_exact_passing_saved_candidate_is_admitted(self):
        saved=json.loads((Path(__file__).resolve().parents[1]/(browser.SAVED+'result.json')).read_bytes())
        self.assertEqual(len(browser.saved_files(saved)),18)
        for key,value in [('run_attempt','2'),('logical_sha256','changed'),('status','STARTED'),('source_commit','different')]:
            changed=copy.deepcopy(saved);changed[key]=value
            with self.assertRaises(ValueError):browser.saved_files(changed)
    def test_changed_or_extra_engine_members_are_refused(self):
        saved=json.loads((Path(__file__).resolve().parents[1]/(browser.SAVED+'result.json')).read_bytes())
        for extra in [True,False]:
            changed=copy.deepcopy(saved)
            if extra:changed['generated_files']['unexpected']={'sha256':'a'*64,'bytes':1}
            else:changed['generated_files']['almanac/query-engine.manifest.json']['sha256']='f'*64
            with self.assertRaises(ValueError):browser.saved_files(changed)

if __name__=='__main__':unittest.main()
