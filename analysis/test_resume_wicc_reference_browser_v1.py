import copy
import json
import os
import unittest
from unittest.mock import patch
import resume_wicc_reference_browser_v1 as resume


class SavedBrowser(unittest.TestCase):
    def test_exact_engine_and_changed_binary_refused(self):
        engine=resume.read(resume.EVIDENCE);resume.verify_engine(engine)
        engine['wasm_sha256']='0'*64
        with self.assertRaises(ValueError):resume.verify_engine(engine)

    def test_local_refusal_precedes_any_read_or_download(self):
        with patch.dict(os.environ,{},clear=True),patch.object(resume,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):resume.controls()

    def test_parent_capture_requires_exact_three_api_hashes(self):
        old=resume.read('research/wicc-reference-engine-run-v1/parent-snapshots.json')
        resume.verify_parent_capture(old,copy.deepcopy(old))
        changed=copy.deepcopy(old);changed['checks'][0]['response_sha256']='0'*64
        with self.assertRaises(ValueError):resume.verify_parent_capture(old,changed)

    def test_harness_only_opens_normal_disclosure_and_preserves_other_checks(self):
        original=(resume.ROOT/'analysis/check_wicc_winter_reference_browser_v1.py').read_bytes()
        revised=(resume.ROOT/'analysis/check_wicc_winter_reference_browser_v2.py').read_bytes()
        added=b"                page.locator('#source-query-panel > summary').click()\n"
        self.assertEqual(revised.replace(added,b''),original)
        self.assertLess(revised.index(added),revised.index(b"page.locator('#source-query-document').select_option"))

    def test_workflow_enables_both_guards_and_has_no_build_step(self):
        body=(resume.ROOT/resume.WORKFLOW).read_text()
        for flag in ['OSW_WICC_REFERENCE_BROWSER_RESUME_V1','OSW_WICC_REFERENCE_DELIVERY_V1']:
            self.assertIn(flag+': "1"',body)
        self.assertNotIn('cargo ',body)
        self.assertNotIn('rustup ',body)


if __name__=='__main__':unittest.main()
