import ast
import copy
import os
import unittest
from unittest.mock import patch
import resume_madagascar_dimensions_browser_v3 as m


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
        new=(m.ROOT/'analysis/check_madagascar_dimensions_browser_v7.py').read_text(encoding='utf8').splitlines()
        self.assertEqual(len(old),len(new))
        changes=[(a,b) for a,b in zip(old,new) if a!=b];self.assertEqual(len(changes),2)
        self.assertIn("'About 60\\u2013100 km'",next(b for a,b in changes if 'About 60' in b))
        constants=[n.value for n in ast.walk(ast.parse('\n'.join(new))) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        self.assertIn('About 60\u2013100 km',constants)
        self.assertIn('About 120 km',constants)
        workflow=(m.ROOT/m.WORKFLOW).read_text(encoding='utf8')
        for text in ['group: osw-current-gap-delivery','cancel-in-progress: false','resume-failure.json','browser-failure.json']:
            self.assertIn(text,workflow)
        self.assertNotIn('rustup ',workflow);self.assertNotIn('cargo ',workflow)


    def test_active_sources_guard_preserves_historical_manifest_and_rejects_changed_active_pins(self):
        scope={'runtime_source_changes':{'active.py':{'candidate_sha256':'a'}},
            'added_source_sha256':{'added.js':'b'},'source_dependencies_sha256':{'dependency.json':'c'},
            'candidate_rust_source_sha256':{'runtime.rs':'d'}}
        pins={'active.py':'a','added.js':'b','dependency.json':'c','runtime.rs':'d'}
        manifest={'sha256':{**pins,'historical-workflow.yml':'old'},'preserved_namespace':{'record':1}}
        before=copy.deepcopy(manifest)
        with patch.object(m.runtime,'scopes',return_value=scope),patch.object(m,'sha',side_effect=pins.__getitem__):
            self.assertEqual(m.verify_active_sources(manifest)['active_source_files'],4)
            self.assertEqual(manifest,before)
            for path in pins:
                for action in ['change','omit']:
                    bad=copy.deepcopy(manifest)
                    if action=='change':bad['sha256'][path]='other'
                    else:del bad['sha256'][path]
                    with self.assertRaises(ValueError):m.verify_active_sources(bad)
        with patch.object(m.runtime,'scopes',return_value=scope),patch.object(m,'sha',return_value='changed'):
            with self.assertRaises(ValueError):m.verify_active_sources(manifest)
        with patch.object(m.runtime,'scopes',side_effect=ValueError('Changed failed inventory source')):
            with self.assertRaises(ValueError):m.verify_active_sources(manifest)



    def test_dashboard_baseline_matches_real_storage_key_and_update_gate_remains(self):
        import re
        dashboard=(m.ROOT/'almanac/dashboard.js').read_text(encoding='utf8')
        harness=(m.ROOT/'analysis/check_madagascar_dimensions_browser_v7.py').read_text(encoding='utf8')
        key=re.search(r"const key = '([^']+)';",dashboard).group(1)
        self.assertEqual(key,'osw-motion-dashboard-seen-v2')
        self.assertIn('localStorage.setItem("'+key+'"',harness)
        self.assertNotIn('osw-motion-dashboard-seen-v3',harness)
        self.assertIn("expect(card).to_have_class(re.compile(r'\\bupdated\\b'))",harness)
        self.assertIn("page.locator('#dashboard-changed').check()",harness)
        self.assertIn("if row!=(contract['dashboard_after']",harness)
        old=(m.ROOT/'analysis/check_madagascar_dimensions_browser_v6.py').read_text(encoding='utf8')
        self.assertEqual(harness,old.replace('osw-motion-dashboard-seen-v3',key))


if __name__=='__main__':unittest.main()
