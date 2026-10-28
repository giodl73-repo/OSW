import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import check_eacc_cited_width_delivery_v3 as cloud


class EaccCitedCloudTests(unittest.TestCase):
    def test_every_reused_cloud_harness_receives_its_required_environment(self):
        import re
        workflow=(cloud.ROOT/cloud.WORKFLOW).read_text()
        supplied=dict(re.findall(r'^  (OSW_[A-Z0-9_]+): "([^"]+)"$',workflow,re.M))
        self.assertEqual(supplied['OSW_EACC_CITED_WIDTH_DELIVERY_V3'],'1')
        for filename in ['analysis/check_eacc_cited_width_parity_v1.mjs','analysis/check_eacc_cited_width_browser_v1.py']:
            source=(cloud.ROOT/filename).read_text()
            required=set(re.findall(r'OSW_EACC_[A-Z0-9_]+',source))
            self.assertTrue(required,filename)
            for name in required:self.assertEqual(supplied.get(name),'1',(filename,name))
        self.assertIn("os.environ.get('OSW_EACC_CITED_WIDTH_DELIVERY_V1')!='1'",(cloud.ROOT/'analysis/check_eacc_cited_width_delivery_v3.py').read_text())

    def test_complete_api_refusal_retains_actual_validator_reason(self):
        result=subprocess.CompletedProcess([],2,None,b'Constraint duplicate or prior playback support differs')
        with tempfile.TemporaryDirectory() as tmp,patch.object(cloud,'OUT',Path(tmp)),patch.object(cloud.subprocess,'run',return_value=result):
            with self.assertRaisesRegex(ValueError,'Constraint duplicate'):
                cloud.native_snapshot('unused','unused','atlas',Path(tmp)/'atlas-native.json')
            receipt=json.loads((Path(tmp)/'native-api-failure.json').read_bytes())
            self.assertEqual(receipt['api'],'atlas');self.assertFalse(receipt['installed'])

    def test_local_execution_refused_before_installed_artifact_access(self):
        with patch.dict(cloud.os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(cloud,'read',side_effect=AssertionError('Unexpected artifact access')):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):cloud.controls()

    def test_native_refusal_retains_actual_validator_reason(self):
        result=subprocess.CompletedProcess([],2,b'{"ok":false,"error":"EACC bound owner differs"}',b'')
        with tempfile.TemporaryDirectory() as tmp,patch.object(cloud,'OUT',Path(tmp)),patch.object(cloud.subprocess,'run',return_value=result):
            with self.assertRaisesRegex(ValueError,'EACC bound owner differs'):cloud.native('unused','unused',{'collection':'objects'})
            receipt=json.loads((Path(tmp)/'native-failure.json').read_bytes())
            self.assertEqual(receipt['returncode'],2);self.assertFalse(receipt['installed'])

    def test_workflow_checks_existing_test_files_and_uses_shared_sequential_queue(self):
        text=(cloud.ROOT/cloud.WORKFLOW).read_text()
        self.assertIn('group: osw-current-gap-delivery',text)
        self.assertIn('cancel-in-progress: false',text)
        import re
        for filename in re.findall(r"-p '(test_[^']+)'",text):
            self.assertTrue((cloud.ROOT/'analysis'/filename).is_file(),filename)
        self.assertIn('taskset -c "$cpu" nice -n 15',text)
        self.assertIn('CARGO_BUILD_JOBS: "1"',text)

    def test_complete_parity_counts_and_mismatched_index_refusal_retained(self):
        parity=(cloud.ROOT/'analysis/check_eacc_cited_width_parity_v1.mjs').read_text()
        snapshots=(cloud.ROOT/'analysis/check_eacc_cited_width_snapshots_v1.mjs').read_text()
        self.assertIn("mode==='main'?71:27",parity)
        self.assertIn("assert.equal(refused.ok,false)",parity)
        self.assertIn("['atlas', 'seasons', 'dashboard']",snapshots)
        self.assertIn('assert.deepEqual(actual',snapshots)


if __name__=='__main__':unittest.main()
