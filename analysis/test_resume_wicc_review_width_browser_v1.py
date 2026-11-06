import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import resume_wicc_review_width_browser_v1 as m


class SavedWiccBrowserTests(unittest.TestCase):
    def test_local_execution_refused_before_any_candidate_access(self):
        with patch.dict(m.os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(m,'read',side_effect=AssertionError('Unexpected artifact access')):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):m.controls()

    def test_only_the_exact_verified_saved_engine_is_accepted(self):
        engine=json.loads((m.ROOT/m.EVIDENCE).read_bytes());m.verify_engine(engine)
        for key,value in [('source_commit','0'*40),('wasm_sha256','0'*64),('rust_tests_passed',229),
                          ('main_query_comparisons',60),('complete_api_comparisons',2)]:
            changed=copy.deepcopy(engine);changed[key]=value
            with self.assertRaises(ValueError):m.verify_engine(changed)

    def test_parent_baseline_must_reproduce_all_original_api_hashes(self):
        original=json.loads((m.ROOT/'research/wicc-review-width-engine-run-v1/parent-snapshots.json').read_bytes())
        m.verify_parent_capture(original,copy.deepcopy(original))
        for change in [lambda d:d['checks'].pop(),lambda d:d['checks'][0].update(response_sha256='0'*64),
                       lambda d:d.update(payload_sha256='0'*64),lambda d:d.update(mode='candidate')]:
            changed=copy.deepcopy(original);change(changed)
            with self.assertRaises(ValueError):m.verify_parent_capture(original,changed)


if __name__=='__main__':unittest.main()
