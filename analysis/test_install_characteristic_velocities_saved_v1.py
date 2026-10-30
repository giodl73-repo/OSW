"""Installation evidence checks use compact metadata, never local engine payloads."""
import copy
import unittest
from unittest.mock import patch
import install_characteristic_velocities_saved_v1 as install
import characteristic_velocities_installation_contract_v1 as contract

class InstallationTests(unittest.TestCase):
    def evidence(self):
        raw=(install.ROOT/(install.ENGINE+'engine-manifest.json')).read_bytes()
        return [install.read(install.ENGINE+'result.json'),
            {key:install.read(install.ENGINE+'compare-'+key+'.json') for key in ('main','index')},
            install.read(install.BROWSER+'result.json'),install.read(install.BROWSER+'browser.json'),
            install.read(install.VISUAL),install.read(install.ENGINE+'engine-manifest.json'),len(raw)]

    def test_exact_reviewed_metadata_requires_eighteen_files(self):
        self.assertEqual(len(contract.verify_evidence(*self.evidence())),18)
        files,raw=install.evidence()
        self.assertEqual(len(files),18);self.assertEqual(install.sha(raw),contract.FINAL_MANIFEST)

    def test_partial_comparisons_unreviewed_images_or_changed_binary_refused(self):
        for case in range(7):
            args=self.evidence()
            if case==0:args[1]['main']['checks'].pop()
            elif case==1:args[4]['independent_visual_review_complete']=False
            elif case==2:args[2]['wasm_sha256']='0'*64
            elif case==3:args[4]['blocking_issues']=['Unresolved source or visual issue']
            elif case==4:args[2]['saved_engine_run']=0
            elif case==5:args[0]['packet_comparison']['width_records_added']=2
            else:args[0]['source_index_audit']['original_sources_verified']=0
            with self.assertRaises(ValueError):contract.verify_evidence(*args)

    def test_local_installation_refuses_before_payload_or_network_access(self):
        with patch.object(install.os,'name','nt'),patch.object(install.Path,'read_bytes',side_effect=AssertionError('No local payload read')):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):install.controls()

    def test_build_or_main_permissions_refused(self):
        request={'schema':'osw.characteristic-velocities-installation-request.v1','workflow':install.WORKFLOW,
            'execution_permitted':True,'working_branch_installation_permitted':True,
            'cloud_git_object_transport_permitted':True,'max_cloud_jobs':1,'max_heavy_local_jobs':0}
        for key in ('native_build_permitted','wasm_build_permitted','browser_automation_permitted',
            'scientific_source_processing_permitted','source_field_processing_permitted','local_bulk_sync_permitted','main_merge_permitted'):
            request[key]=False
        install.verify_request(request)
        for key in ('native_build_permitted','main_merge_permitted'):
            changed=copy.deepcopy(request);changed[key]=True
            with self.assertRaises(ValueError):install.verify_request(changed)

if __name__=='__main__':unittest.main()
