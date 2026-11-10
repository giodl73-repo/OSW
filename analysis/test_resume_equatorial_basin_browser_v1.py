import copy
import json
import os
from pathlib import Path
import tempfile
import textwrap
import unittest
from unittest.mock import patch
import resume_equatorial_basin_browser_v1 as m


class Resume(unittest.TestCase):
    def test_local_resume_refuses_before_any_payload_hash(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(m, 'sha', side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):
                m.controls()

    def test_exact_saved_engine_counts_data_binary_and_source_preservation_required(self):
        engine = m.read(m.EVIDENCE)
        m.verify_engine(engine)
        mutations = {'source_commit': 'other', 'logical_sha256': 'other', 'logical_bytes': 1,
                     'wasm_sha256': 'other', 'rust_tests_passed': 271, 'main_query_comparisons': 194,
                     'source_query_comparisons': 72, 'complete_api_comparisons': 2,
                     'complete_object_api_comparisons': 6, 'new_identity_records': 4,
                     'new_width_records': 1, 'new_length_records': 1, 'new_independent_observations': 1,
                     'browser_verified': True, 'installed': True, 'generated_sha256': {}}
        for key, value in mutations.items():
            with self.assertRaises(ValueError, msg=key):
                m.verify_engine({**engine, key: value})
        bad = copy.deepcopy(engine)
        bad['source_index_audit']['original_source_strings_preserved'] = 635
        with self.assertRaises(ValueError):
            m.verify_engine(bad)

    def test_parent_capture_custody_preserves_three_entire_response_hashes(self):
        parent = m.read('research/equatorial-basin-engine-run-v4/parent-snapshots.json')
        m.verify_parent_capture(parent, copy.deepcopy(parent))
        for key in ['wasm_sha256', 'payload_sha256', 'checks']:
            bad = copy.deepcopy(parent)
            bad[key] = [] if key == 'checks' else 'changed'
            with self.assertRaises(ValueError):
                m.verify_parent_capture(parent, bad)

    def test_saved_active_sources_preserved_and_changed_or_missing_source_refused(self):
        scope = {'runtime_source_changes': {'active.py': {'candidate_sha256': 'a'}},
                 'added_source_sha256': {'added.js': 'b'}, 'source_dependencies_sha256': {'source.json': 'c'},
                 'candidate_rust_source_sha256': {'runtime.rs': 'd'}}
        pins = {'active.py': 'a', 'added.js': 'b', 'source.json': 'c', 'runtime.rs': 'd'}
        manifest = {'sha256': {**pins, 'historical.yml': 'old'}, 'historical': {'keep': True}}
        before = copy.deepcopy(manifest)
        with patch.object(m.runtime, 'scopes', return_value=scope), patch.object(m, 'sha', side_effect=pins.__getitem__):
            self.assertEqual(m.verify_active_sources(manifest)['active_source_files'], 4)
            self.assertEqual(manifest, before)
            for path in pins:
                bad = copy.deepcopy(manifest)
                bad['sha256'][path] = 'changed'
                with self.assertRaises(ValueError):
                    m.verify_active_sources(bad)

    def test_workflow_selector_reads_its_own_request_and_build_steps_are_absent(self):
        source = (m.ROOT / m.WORKFLOW).read_text()
        self.assertEqual(source.count(m.REQUEST), 3)
        self.assertIn('sparse-checkout: ' + m.REQUEST, source)
        self.assertIn('group: osw-current-gap-delivery', source)
        self.assertIn('cancel-in-progress: false', source)
        self.assertNotIn('cargo ', source)
        self.assertNotIn('rustup ', source)
        start = source.index("          python - <<'PY'\n") + len("          python - <<'PY'\n")
        program = textwrap.dedent(source[start:source.index('\n          PY', start)])
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            request = root / m.REQUEST
            request.parent.mkdir(parents=True)
            request.write_text(json.dumps({'schema': 'osw.equatorial-basin-browser-resume-request.v1', 'execute': True}))
            output = root / 'output.txt'
            try:
                os.chdir(root)
                with patch.dict(os.environ, {'GITHUB_OUTPUT': str(output)}):
                    exec(compile(program, m.WORKFLOW, 'exec'), {})
                self.assertEqual(output.read_text(), 'execute=true\n')
            finally:
                os.chdir(previous)

    def test_saved_artifact_and_seventy_capture_requirement_match_retained_receipt(self):
        receipt = m.read('research/equatorial-basin-engine-run-v4/run-receipt.json')
        self.assertEqual(m.ARTIFACT, {'id': receipt['candidate_artifact_id'], 'bytes': receipt['candidate_artifact_bytes'],
                                     'sha256': receipt['candidate_artifact_sha256']})
        source = (m.ROOT / 'analysis/resume_equatorial_basin_browser_v1.py').read_text()
        self.assertIn("observed.get('actual_screenshots')!=70", source)
        self.assertIn('from check_equatorial_basin_browser_v3 import browser_review', source)
        self.assertNotIn("['cargo'", source)


if __name__ == '__main__':
    unittest.main()
