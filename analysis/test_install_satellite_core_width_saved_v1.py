import copy
import json
import unittest
from unittest.mock import patch
import install_satellite_core_width_saved_v1 as m

class SatelliteInstallationTests(unittest.TestCase):
    def test_all_actual_saved_parity_receipt_formats(self):
        for name in ['main','index','snapshots']:
            m.verify_parity_receipt(name,m.read(m.EVIDENCE+name+'-parity.json'))
        self.assertEqual(m.file_sha(m.ROOT/m.PARITY_SOURCE),m.PARITY_SOURCE_SHA)

    def test_changed_parity_payload_mode_or_response_is_rejected(self):
        for name in ['main','index','snapshots']:
            original=m.read(m.EVIDENCE+name+'-parity.json')
            for field,value in [('payload_sha256','0'*64),('mode','parent'),('wasm_sha256','0'*64)]:
                changed=copy.deepcopy(original);changed[field]=value
                with self.assertRaises(AssertionError):m.verify_parity_receipt(name,changed)
            changed=copy.deepcopy(original);changed['checks'][0]['entire_response_equal']=False
            with self.assertRaises(AssertionError):m.verify_parity_receipt(name,changed)

    def evidence(self):
        return [m.read(m.EVIDENCE+'engine.json'),m.read(m.EVIDENCE+'result.json'),m.read(m.EXECUTION),m.read(m.REVIEW),m.read(m.EVIDENCE+'browser.json')]

    def test_exact_reviewed_engine_browser_and_visual_evidence(self):
        hashes=m.verify_evidence(*self.evidence())
        self.assertEqual(len(hashes),18);self.assertEqual(hashes[m.delivery.MANIFEST],m.FINAL_MANIFEST)

    def test_changed_verification_or_artifact_cannot_be_installed(self):
        for mutation in ['tests','artifact','result','screenshot']:
            values=copy.deepcopy(self.evidence())
            if mutation=='tests':values[0]['rust_tests_passed']=222
            elif mutation=='artifact':values[2]['candidate_artifact']['id']=1
            elif mutation=='result':values[1]['browser_verified']=False
            else:values[3]['screenshots'][0]['geometry']['clipped_axes']=['x']
            with self.assertRaises(AssertionError):m.verify_evidence(*values)

    def test_install_request_has_no_rebuild_or_main_permission(self):
        request={'schema':'osw.satellite-core-width-installation-request.v1','workflow':m.WORKFLOW,
            'execution_permitted':True,'working_branch_installation_permitted':True,'cloud_git_object_transport_permitted':True,
            'max_cloud_jobs':1,'max_heavy_local_jobs':0,**{key:False for key in ['native_build_permitted','wasm_build_permitted',
            'browser_automation_permitted','scientific_source_processing_permitted','source_field_processing_permitted','local_bulk_sync_permitted','main_merge_permitted']}}
        m.verify_request(request)
        for key in ['execution_permitted','native_build_permitted','main_merge_permitted','max_cloud_jobs']:
            changed=dict(request);changed[key]=False if key=='execution_permitted' else True if key.endswith('permitted') else 2
            with self.assertRaises(AssertionError):m.verify_request(changed)

    def test_local_invocation_refused_before_any_installed_file_read(self):
        with patch.dict(m.os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(m,'read',side_effect=AssertionError('Unexpected file read')):
            with self.assertRaises(AssertionError):m.controls()

if __name__=='__main__':unittest.main()
