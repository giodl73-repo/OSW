import copy
import os
import unittest
from unittest.mock import patch
import wicc_reference_card_context_v1 as context
import resume_wicc_reference_browser_v2 as resume

class CardContext(unittest.TestCase):
    def test_exact_saved_sources_and_three_presentation_pins(self):
        old=context.read(context.OLD)
        new=context.updated_manifest(old,'browser-source-fixture')
        context.verify_manifest_delta(old,new,'browser-source-fixture')
        self.assertEqual(len(context.read(context.FILE)['bindings']),3)

    def test_scientific_or_wasm_manifest_change_refused(self):
        old=context.read(context.OLD);new=context.updated_manifest(old,'browser-source-fixture')
        changed=copy.deepcopy(new);changed['sha256']['almanac/query-engine.wasm']='0'*64
        with self.assertRaises(ValueError):context.verify_manifest_delta(old,changed,'browser-source-fixture')
        changed=copy.deepcopy(new);changed['abi_version']=999
        with self.assertRaises(ValueError):context.verify_manifest_delta(old,changed,'browser-source-fixture')

    def test_custody_or_asset_change_refused(self):
        old=context.read(context.OLD);new=context.updated_manifest(old,'browser-source-fixture')
        with self.assertRaises(ValueError):context.verify_manifest_delta(old,new,'other-source')
        new['sha256']['almanac/reference-routes.js']='0'*64
        with self.assertRaises(ValueError):context.verify_manifest_delta(old,new,'browser-source-fixture')

    def test_local_execution_refused_before_reads(self):
        with patch.dict(os.environ,{},clear=True),patch.object(resume,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):resume.controls()

    def test_exact_engine_preserved(self):
        engine=resume.read(resume.EVIDENCE);resume.verify_engine(engine)
        engine['logical_sha256']='0'*64
        with self.assertRaises(ValueError):resume.verify_engine(engine)

    def test_browser_retains_prior_checks_and_adds_citation_and_context(self):
        prior=(context.ROOT/'analysis/check_wicc_winter_reference_browser_v2.py').read_bytes()
        revised=(context.ROOT/'analysis/check_wicc_winter_reference_browser_v3.py').read_bytes()
        lines=[line for line in revised.splitlines(keepends=True) if b"expect(card.get_by_role('link',name='doi:" not in line and b"expect(card).to_contain_text('Editorial map overlap only:" not in line and b"expect(card).to_contain_text('Physical current passage through atlas regions" not in line]
        self.assertEqual(b''.join(lines),prior)

    def test_workflow_has_no_build_or_install(self):
        body=(context.ROOT/resume.WORKFLOW).read_text(encoding='utf8')
        self.assertIn('OSW_WICC_REFERENCE_BROWSER_RESUME_V2: "1"',body)
        self.assertNotIn('cargo ',body);self.assertNotIn('rustup ',body)
        self.assertIn('engine-manifest.json',body)

if __name__=='__main__':unittest.main()
