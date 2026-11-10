import copy
import os
import unittest
from unittest.mock import patch
import resume_eac_mean_core_browser_v1 as m


class Resume(unittest.TestCase):
    def test_local_resume_refused_before_any_payload_hash(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m,'sha',side_effect=AssertionError('early payload access')):
            with self.assertRaises(ValueError):m.controls()

    def test_exact_saved_engine_identity_counts_and_scope_required(self):
        engine=m.read(m.EVIDENCE);m.verify_engine(engine)
        changes={'source_commit':'other','logical_sha256':'other','logical_bytes':1,'wasm_sha256':'other',
            'rust_tests_passed':247,'main_query_comparisons':98,'source_query_comparisons':34,
            'complete_api_comparisons':2,'new_mean_core_section_records':6,'new_width_records':5,
            'new_length_records':5,'new_independent_observations':5,'installed':True,'browser_verified':True}
        for key,value in changes.items():
            bad={**engine,key:value}
            with self.assertRaises(ValueError,msg=key):m.verify_engine(bad)

    def test_original_three_api_parent_capture_must_match(self):
        old=m.read('research/eac-mean-core-engine-run-v1/parent-snapshots.json')
        m.verify_parent_capture(old,copy.deepcopy(old))
        for key in ['wasm_sha256','payload_sha256','checks']:
            bad=copy.deepcopy(old);bad[key]=[] if key=='checks' else 'other'
            with self.assertRaises(ValueError):m.verify_parent_capture(old,bad)

    def test_browser_only_workflow_and_harness_preserve_failure_observations(self):
        workflow=(m.ROOT/m.WORKFLOW).read_text()
        self.assertIn('group: osw-current-gap-delivery',workflow)
        self.assertIn('cancel-in-progress: false',workflow)
        self.assertIn('OSW_EAC_MEAN_CORE_BROWSER_RESUME_V1: "1"',workflow)
        self.assertNotIn('rustup ',workflow);self.assertNotIn('cargo ',workflow)
        body=(m.ROOT/'analysis/check_eac_mean_core_browser_v2.py').read_text()
        for text in ['browser-observation-failure.json','dashboardStatus','completed_screenshots','Update check failed']:
            self.assertIn(text,body)


if __name__=='__main__':unittest.main()
