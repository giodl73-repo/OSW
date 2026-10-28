import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import check_eacc_cited_width_delivery_v1 as cloud


class EaccCitedCloudTests(unittest.TestCase):
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
