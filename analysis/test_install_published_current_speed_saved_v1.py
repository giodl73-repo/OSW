import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import install_published_current_speed_saved_v1 as m


class SavedSpeedInstallationTests(unittest.TestCase):
    def docs(self):return [m.read(p) for p in [m.FULL,m.EXECUTION,m.REVIEW,m.BROWSER]]

    def test_reviewed_engine_source_index_and_browser_evidence(self):
        self.assertEqual(len(m.verify_evidence(*self.docs())),18)

    def test_reject_changed_identity_cohort_and_visual_review(self):
        for change in [lambda d:d[0].update(wasm_sha256='wrong'),
                       lambda d:d[1].update(underlying_observations=656),
                       lambda d:d[2].update(independent_visual_review_complete=False),
                       lambda d:d[3]['screenshots'][0]['geometry'].update(clipped_axes=['horizontal'])]:
            docs=copy.deepcopy(self.docs());change(docs)
            with self.assertRaises(AssertionError):m.verify_evidence(*docs)

    def test_only_saved_cloud_branch_installation_can_be_enabled(self):
        req={'schema':'osw.published-current-speed-installation-request.v1','workflow':m.WORKFLOW,'execution_permitted':True,
             'working_branch_installation_permitted':True,'cloud_git_object_transport_permitted':True,
             'max_cloud_jobs':1,'max_heavy_local_jobs':0}
        flags=['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
               'scientific_source_processing_permitted','source_field_processing_permitted',
               'local_bulk_sync_permitted','main_merge_permitted']
        req.update({f:False for f in flags});m.verify_request(req)
        for flag in flags:
            bad=dict(req);bad[flag]=True
            with self.assertRaises(AssertionError):m.verify_request(bad)
        bad=dict(req);bad['execution_permitted']=1
        with self.assertRaises(AssertionError):m.verify_request(bad)

    def test_both_exact_upload_layouts_preserve_binary_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);body=b'exact\x00\r\nbytes';engine=b'{"status":"PASS"}\n'
            for index,folder in enumerate(['artifact/','']):
                archive=root/f'saved-{index}.zip'
                with zipfile.ZipFile(archive,'w') as z:
                    z.writestr(folder+'almanac/tiny.bin',body);z.writestr('engine.json',engine)
                target=m.extract_candidate(archive,{'almanac/tiny.bin':m.sha(body)},m.sha(engine),root/f'out-{index}')
                self.assertEqual((target/'almanac/tiny.bin').read_bytes(),body)
                with self.assertRaises(AssertionError):m.extract_candidate(archive,{'almanac/tiny.bin':'wrong'},m.sha(engine),root/f'bad-{index}')

    def test_extra_or_unsafe_archive_members_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/'bad.zip';body=b'x'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('../escape.bin',body);z.writestr('engine.json',body)
            with self.assertRaises(AssertionError):m.extract_candidate(archive,{'../escape.bin':m.sha(body)},m.sha(body),root/'out')
            self.assertFalse((root/'escape.bin').exists())

    def test_local_execution_refused_before_any_artifact_read(self):
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(m,'read',side_effect=AssertionError('Artifact read')):
            with self.assertRaises(AssertionError):m.controls()


if __name__=='__main__':unittest.main()
