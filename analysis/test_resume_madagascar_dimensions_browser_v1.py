import ast
import copy
import os
import unittest
from unittest.mock import patch
import resume_madagascar_dimensions_browser_v1 as m


class Resume(unittest.TestCase):
    def test_local_resume_refused_before_any_payload_hash(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m,'sha',side_effect=AssertionError('early payload access')):
            with self.assertRaises(ValueError):m.controls()

    def test_exact_saved_engine_identity_counts_and_scope_required(self):
        engine=m.read(m.EVIDENCE);m.verify_engine(engine)
        changes={'source_commit':'other','logical_sha256':'other','logical_bytes':1,'wasm_sha256':'other',
            'rust_tests_passed':255,'main_query_comparisons':116,'source_query_comparisons':44,
            'complete_api_comparisons':2,'new_flow_event_references':7,'new_width_records':2,
            'new_length_records':1,'new_independent_observations':1,'installed':True,'browser_verified':True,
            'generated_sha256':{}}
        for key,value in changes.items():
            with self.assertRaises(ValueError,msg=key):m.verify_engine({**engine,key:value})

    def test_original_three_api_parent_capture_must_match(self):
        old=m.read('research/madagascar-dimensions-engine-run-v5/parent-snapshots.json')
        m.verify_parent_capture(old,copy.deepcopy(old))
        for key in ['wasm_sha256','payload_sha256','checks']:
            bad=copy.deepcopy(old);bad[key]=[] if key=='checks' else 'other'
            with self.assertRaises(ValueError):m.verify_parent_capture(old,bad)

    def test_browser_fix_changes_only_one_exact_unicode_expectation(self):
        old=(m.ROOT/'analysis/check_madagascar_dimensions_browser_v5.py').read_text(encoding='utf8').splitlines()
        new=(m.ROOT/'analysis/check_madagascar_dimensions_browser_v6.py').read_text(encoding='utf8').splitlines()
        self.assertEqual(len(old),len(new))
        changes=[(a,b) for a,b in zip(old,new) if a!=b];self.assertEqual(len(changes),1)
        self.assertIn("'About 60\\u2013100 km'",changes[0][1])
        constants=[n.value for n in ast.walk(ast.parse('\n'.join(new))) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        self.assertIn('About 60\u2013100 km',constants)
        self.assertIn('About 120 km',constants)
        workflow=(m.ROOT/m.WORKFLOW).read_text(encoding='utf8')
        for text in ['group: osw-current-gap-delivery','cancel-in-progress: false','resume-failure.json','browser-failure.json']:
            self.assertIn(text,workflow)
        self.assertNotIn('rustup ',workflow);self.assertNotIn('cargo ',workflow)


if __name__=='__main__':unittest.main()
