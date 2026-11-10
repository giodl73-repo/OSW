import copy
import unittest
from unittest.mock import patch
import install_seasonal_core_velocity_saved_v1 as m


class SeasonalInstallationTests(unittest.TestCase):
    def docs(self):
        return [m.read(p) for p in ['research/seasonal-core-velocity-engine-evidence-v1.json',m.EVIDENCE+'engine.json',m.EXECUTION,m.REVIEW,m.EVIDENCE+'browser.json']]

    def test_exact_engine_and_reviewed_browser_candidate(self):
        self.assertEqual(len(m.verify_evidence(*self.docs())),18)

    def test_manifest_revision_reconstructs_exact_reviewed_candidate(self):
        parent=m.read(m.EVIDENCE+'source-engine-manifest.json')
        revision=m.read('research/seasonal-core-velocity-browser-revision-v2.json')
        expected=m.resume.revise_manifest(parent,revision,source_commit=m.SOURCE,
            verification_inputs=m.read('research/seasonal-core-velocity-browser-resume-preflight-v2.json')['input_sha256'])
        self.assertEqual(expected,m.read(m.EVIDENCE+'candidate-engine-manifest.json'))
        self.assertEqual(m.file_sha(m.ROOT/(m.EVIDENCE+'candidate-engine-manifest.json')),m.FINAL_MANIFEST)

    def test_changed_engine_source_counts_and_visual_evidence_refused(self):
        for change in [lambda d:d[0].update(pemba_whole_response_preserved=False),
                       lambda d:d[1].update(wasm_sha256='wrong'),
                       lambda d:d[1]['generated_sha256'].update({'almanac/index-catalog.json':'wrong'}),
                       lambda d:d[2].update(seasonal_core_velocity_estimates=5),
                       lambda d:d[2].update(new_length_records=1),
                       lambda d:d[3].update(independent_visual_review_complete=False),
                       lambda d:d[4]['screenshots'][0]['geometry'].update(clipped_axes=['vertical'])]:
            docs=copy.deepcopy(self.docs());change(docs)
            with self.assertRaises(AssertionError):m.verify_evidence(*docs)

    def test_only_scoped_cloud_installation_permitted(self):
        request={'schema':'osw.seasonal-core-velocity-installation-request.v1','workflow':m.WORKFLOW,
                 'execution_permitted':True,'working_branch_installation_permitted':True,'cloud_git_object_transport_permitted':True,
                 'max_cloud_jobs':1,'max_heavy_local_jobs':0}
        flags=['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
               'scientific_source_processing_permitted','source_field_processing_permitted','local_bulk_sync_permitted','main_merge_permitted']
        request.update({key:False for key in flags});m.verify_request(request)
        for key in flags:
            changed=dict(request);changed[key]=True
            with self.assertRaises(AssertionError):m.verify_request(changed)
        changed=dict(request);changed['execution_permitted']=1
        with self.assertRaises(AssertionError):m.verify_request(changed)

    def test_local_execution_refused_before_any_evidence_or_packet_read(self):
        with patch.dict(m.os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(m,'read',side_effect=AssertionError('Unexpected read')):
            with self.assertRaises(AssertionError):m.controls()


if __name__=='__main__':unittest.main()
