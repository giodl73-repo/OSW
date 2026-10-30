import copy,unittest
from unittest.mock import patch
import check_current_core_dimensions_atlas_visual_v1 as browser

class BrowserScopeTests(unittest.TestCase):
    def test_workflow_selector_and_artifact_paths_match_browser_driver(self):
        workflow=(browser.ROOT/'.github/workflows/current-core-dimensions-atlas-visual-v1.yml').read_text(encoding='utf-8')
        self.assertEqual(workflow.count(browser.REQUEST),3)
        output=browser.OUT.relative_to(browser.ROOT).as_posix()
        self.assertIn(output+'/*.json',workflow)
        self.assertIn(output+'/*.png',workflow)
        self.assertIn('python analysis/check_current_core_dimensions_atlas_visual_v1.py',workflow)
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
    def test_presentation_overlay_changes_only_manifest_descriptor(self):
        original=browser.saved_files(browser.read(browser.SAVED+'result.json'))
        final,raw=browser.presentation_files(original)
        self.assertEqual(set(final),set(original))
        self.assertEqual({p:v for p,v in final.items() if p!='almanac/query-engine.manifest.json'},
                         {p:v for p,v in original.items() if p!='almanac/query-engine.manifest.json'})
        self.assertEqual(final['almanac/query-engine.manifest.json']['sha256'],browser.hashlib.sha256(raw).hexdigest())
        import current_core_dimensions_atlas_presentation_v1 as presentation
        original_read=browser.Path.read_bytes
        def changed(path):
            value=original_read(path)
            if path==browser.ROOT/presentation.FILE:
                doc=browser.json.loads(value);doc['sha256']['almanac/query-engine.wasm']='0'*64
                return browser.json.dumps(doc).encode()
            return value
        with patch.object(browser.Path,'read_bytes',changed):
            with self.assertRaisesRegex(ValueError,'Presentation overlay differs'):browser.presentation_files(original)

    def test_local_browser_refuses_before_payload_access(self):
        with patch.object(browser.os,'name','nt'),patch.object(browser.Path,'read_bytes',side_effect=AssertionError('No local payload read')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):browser.controls()

if __name__=='__main__':unittest.main()
