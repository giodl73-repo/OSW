"""Local refusal and cloud orchestration source fixtures; no ocean data opened."""
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import check_loop_published_metrics_delivery_v1 as cloud
import loop_published_metrics_query_v1 as context


class CloudCase(unittest.TestCase):
    def test_local_execution_refused_before_file_or_binary_read(self):
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('File opened')):
            with self.assertRaises(RuntimeError): cloud.controls({})

    def test_exact_cloud_source_environment_required(self):
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('File opened')):
            with self.assertRaises(RuntimeError):
                cloud.controls({'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'giodl73-repo/OSW',
                                'GITHUB_REF': 'refs/heads/main'})

    def test_cloud_wasm_runner_refuses_local_before_opening_payload(self):
        env = dict(os.environ)
        for name in ['GITHUB_ACTIONS', 'GITHUB_REPOSITORY', 'GITHUB_REF', 'OSW_LOOP_PUBLISHED_METRICS_DELIVERY']:
            env.pop(name, None)
        result = subprocess.run(['node', 'analysis/check_loop_published_metrics_parity_v1.mjs', 'main',
                                 'missing.wasm', 'missing.json'], cwd=cloud.ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'AssertionError', result.stderr)
        self.assertNotIn(b'ENOENT', result.stderr)

    def test_native_cases_cover_nulls_typing_owner_sources_and_legacy_context(self):
        contract = context.build_contract()
        expected = {name: rows for name, rows in contract['collections'].items()}
        expected['owner'] = {'id': context.TARGET}
        expected['legacy_depths'] = [{'id': 'old-depth'}]
        cases = cloud.main_requests(expected)
        self.assertEqual(len(cases), 11)
        self.assertEqual(len(cases[2][1]), 2)
        self.assertEqual(cases[3][0]['filters'][0]['value'], None)
        self.assertEqual(cases[4][0]['filters'][0]['value'], 0)
        self.assertEqual(cases[4][1], [])
        self.assertEqual(cases[9][0]['record_type'], 'named_current')
        self.assertEqual(cases[10][0]['collection'], 'current_model_depth_context')


if __name__ == '__main__': unittest.main()
