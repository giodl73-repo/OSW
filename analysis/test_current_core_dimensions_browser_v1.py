import copy,unittest
from unittest.mock import patch
import check_current_core_dimensions_browser_v1 as browser

class BrowserScopeTests(unittest.TestCase):
    def test_workflow_selector_and_artifact_paths_match_browser_driver(self):
        workflow=(browser.ROOT/'.github/workflows/current-core-dimensions-browser-v1.yml').read_text(encoding='utf-8')
        self.assertEqual(workflow.count(browser.REQUEST),3)
        output=browser.OUT.relative_to(browser.ROOT).as_posix()
        self.assertIn(output+'/*.json',workflow)
        self.assertIn(output+'/*.png',workflow)
        self.assertIn('python analysis/check_current_core_dimensions_browser_v1.py',workflow)
        self.assertIn('group: osw-current-gap-delivery',workflow)
        self.assertIn('cancel-in-progress: false',workflow)

    def test_exact_reviewed_saved_candidate_has_eighteen_files(self):
        self.assertEqual(len(browser.saved_files(browser.read(browser.SAVED+'result.json'))),18)
    def test_changed_engine_identity_or_member_hash_refused(self):
        for case in range(3):
            value=browser.read(browser.SAVED+'result.json')
            if case==0:value['logical_sha256']='0'*64
            elif case==1:value['generated_files']['almanac/query-engine.manifest.json']['sha256']='0'*64
            else:value['run_id']='wrong'
            with self.assertRaises(ValueError):browser.saved_files(value)
    def test_local_browser_refuses_before_payload_access(self):
        with patch.object(browser.os,'name','nt'),patch.object(browser.Path,'read_bytes',side_effect=AssertionError('No local payload read')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):browser.controls()

if __name__=='__main__':unittest.main()
