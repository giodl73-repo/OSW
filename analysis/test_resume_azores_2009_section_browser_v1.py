"""Metadata fixtures verify exact engine reuse and local execution refusal."""
import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import resume_azores_2009_section_browser_v1 as resume


class SavedBrowserResume(unittest.TestCase):
    def fixture(self):
        run = {'status': 'completed', 'conclusion': 'failure', 'head_sha': resume.SOURCE, 'run_attempt': 1}
        jobs = [{'name': 'full-delivery', 'steps': [
            {'name': 'Verify parent preservation and matching native/WASM queries and complete snapshots', 'conclusion': 'success'},
            {'name': 'Verify direct atlas/query/card links and actual desktop/mobile rendering', 'conclusion': 'failure'}]}]
        artifact = {'expired': False, 'id': resume.ARTIFACT, 'size_in_bytes': resume.ARCHIVE_BYTES,
                    'digest': 'sha256:' + resume.ARCHIVE_SHA,
                    'workflow_run': {'id': resume.RUN, 'head_sha': resume.SOURCE}}
        evidence = json.loads(Path(resume.EVIDENCE).read_bytes())
        return run, jobs, artifact, evidence

    def test_exact_passed_engine_phase_can_be_reused_after_browser_failure(self):
        resume.verify_saved_metadata(*self.fixture())

    def test_changed_archive_wrong_attempt_and_unproved_engine_refused(self):
        for change in [lambda rows: rows[0].update(run_attempt=2),
                       lambda rows: rows[0].update(status='in_progress'),
                       lambda rows: rows[2].update(digest='wrong'),
                       lambda rows: rows[1][0]['steps'][0].update(conclusion='failure'),
                       lambda rows: rows[3].update(wasm_sha256='wrong')]:
            rows = copy.deepcopy(self.fixture()); change(rows)
            with self.assertRaises(ValueError):
                resume.verify_saved_metadata(*rows)

    def test_local_execution_refuses_before_any_control_or_artifact_read(self):
        with patch.object(resume, 'read', side_effect=AssertionError('Unexpected artifact read')):
            with patch.dict(os.environ, {'GITHUB_ACTIONS': 'false'}, clear=False):
                with self.assertRaisesRegex(ValueError, 'Exact cloud'):
                    resume.controls(clean=True)


if __name__ == '__main__':
    unittest.main()
