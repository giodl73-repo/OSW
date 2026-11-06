import ast
import copy
import os
import unittest
from unittest.mock import patch
import resume_azcc_onken_browser_v1 as m


OLD_CAPTURE="capture(details.locator('article').last,'azcc-atlas-comparison-'+suffix);no_overflow(page)"
NEW_CAPTURE="card=details.locator('article').last\n                    capture(card.locator('h4'),'azcc-atlas-heading-'+suffix)\n                    capture(card.locator('svg'),'azcc-atlas-width-chart-'+suffix)\n                    capture(card.get_by_role('link',name='Source evidence record',exact=True),'azcc-atlas-source-link-'+suffix);no_overflow(page)"

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
        old=m.read('research/azcc-onken-engine-run-v1/parent-snapshots.json')
        m.verify_parent_capture(old,copy.deepcopy(old))
        for key in ['wasm_sha256','payload_sha256','checks']:
            bad=copy.deepcopy(old);bad[key]=[] if key=='checks' else 'other'
            with self.assertRaises(ValueError):m.verify_parent_capture(old,bad)

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



    def test_only_capture_target_changes_and_no_clipping_gate_is_removed(self):
        old=(m.ROOT/'analysis/check_azcc_onken_browser_v1.py').read_text(encoding='utf8')
        new=(m.ROOT/'analysis/check_azcc_onken_browser_v2.py').read_text(encoding='utf8')
        self.assertEqual(new,old.replace(OLD_CAPTURE,NEW_CAPTURE))
        self.assertIn('verify_capture_geometry(geometry)',new)
        self.assertIn("expect(card).to_have_class(re.compile(r'\\bupdated\\b'))",new)
        workflow=(m.ROOT/m.WORKFLOW).read_text(encoding='utf8')
        for text in ['group: osw-current-gap-delivery','cancel-in-progress: false','browser-observation-failure.json','resume-failure.json']:
            self.assertIn(text,workflow)
        self.assertNotIn('rustup ',workflow);self.assertNotIn('cargo ',workflow)
        self.assertIn("observed.get('actual_screenshots')!=22",(m.ROOT/'analysis/resume_azcc_onken_browser_v1.py').read_text())

if __name__=='__main__':unittest.main()
