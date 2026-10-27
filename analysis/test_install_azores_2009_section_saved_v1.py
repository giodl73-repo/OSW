"""Compact review/request/archive fixtures; no installed packet or binary reads."""
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import install_azores_2009_section_saved_v1 as install


class SavedAzoresInstallation(unittest.TestCase):
    def documents(self):
        return [json.loads(Path(p).read_bytes()) for p in [install.FULL,install.EXECUTION,install.REVIEW,install.BROWSER]]

    def test_exact_combined_engine_browser_visual_review_passes(self):
        hashes = install.verify_results(*self.documents())
        self.assertEqual(len(hashes),18)
        install.verify_browser_result(json.loads(Path('research/azores-2009-section-browser-resume-result-v1.json').read_bytes()))

    def test_unreviewed_clipped_or_rebound_evidence_refused(self):
        for change in [lambda d:d[0].update(wasm_sha256='wrong'),
                       lambda d:d[1]['verification'].update(original_scientific_collections_changed=1),
                       lambda d:d[2]['images'][0].update(individually_inspected=False),
                       lambda d:d[3]['screenshots'][0]['geometry'].update(clipped_axes=['vertical'])]:
            docs = copy.deepcopy(self.documents());change(docs)
            with self.assertRaises(AssertionError):install.verify_results(*docs)

    def test_browser_result_must_reuse_the_same_saved_engine(self):
        original=json.loads(Path('research/azores-2009-section-browser-resume-result-v1.json').read_bytes())
        for field,value in [('logical_sha256','wrong'),('native_builds',1),('saved_candidate_files_verified',17),('browser_verified',False)]:
            bad=copy.deepcopy(original);bad[field]=value
            with self.assertRaises(AssertionError):install.verify_browser_result(bad)

    def test_request_permits_only_cloud_branch_installation(self):
        request={'schema':'osw.azores-2009-section-installation-request.v1',
            'execution_permitted':True,'working_branch_installation_permitted':True,'cloud_git_object_transport_permitted':True,
            'max_cloud_jobs':1,'max_heavy_local_jobs':0}
        forbidden=['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
                   'scientific_source_processing_permitted','local_bulk_sync_permitted','main_merge_permitted']
        request.update({key:False for key in forbidden});install.verify_request(request)
        for field in forbidden:
            bad=copy.deepcopy(request);bad[field]=True
            with self.assertRaises(AssertionError):install.verify_request(bad)

    def test_exact_archive_inventory_and_bytes_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/'saved.zip';body=b'reviewed\x00\r\nbytes'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('almanac/tiny.bin',body)
            install.extract_verified(archive,{'almanac/tiny.bin':install.sha(body)},root/'out')
            self.assertEqual((root/'out/almanac/tiny.bin').read_bytes(),body)
            with self.assertRaises(AssertionError):
                install.extract_verified(archive,{'almanac/tiny.bin':'wrong'},root/'wrong')
            with self.assertRaises(AssertionError):
                install.extract_verified(archive,{'../escape.bin':install.sha(body)},root/'escape')

    def test_local_execution_refuses_before_request_or_artifact_read(self):
        with patch.object(install,'read',side_effect=AssertionError('Unexpected artifact read')):
            with patch.dict(os.environ,{'GITHUB_ACTIONS':'false'},clear=False):
                with self.assertRaises(AssertionError):install.controls()


if __name__=='__main__':unittest.main()
