"""Controller refusal and diagnostic fixtures; never loads the real candidate."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import check_south_java_catalog_engine_cloud_v1 as cloud


class Controller(unittest.TestCase):
    def test_original_source_comparison_distinguishes_false_zero_and_null(self):
        raw = b'{"eligible":false,"width":null}'
        response = {'source_sha256': cloud.native.digest(raw),
                    'rows': [{'source_key': 'eligible', 'record': False}, {'source_key': 'width', 'record': None}]}
        self.assertTrue(cloud.original_source_matches(response, raw))
        response['rows'][0]['record'] = 0
        self.assertFalse(cloud.original_source_matches(response, raw))
        response['rows'][0]['record'] = False; response['rows'][1]['record'] = 0
        self.assertFalse(cloud.original_source_matches(response, raw))

    def test_local_refusal_precedes_payload_reads(self):
        with patch.object(cloud.Path, 'read_bytes', side_effect=AssertionError('File read')):
            with self.assertRaises(RuntimeError): cloud.controls({})

    def test_wrong_branch_refusal_precedes_payload_reads(self):
        with patch.object(cloud.Path, 'read_bytes', side_effect=AssertionError('File read')):
            with self.assertRaises(RuntimeError):
                cloud.controls({'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'giodl73-repo/OSW',
                                'GITHUB_REF': 'refs/heads/main'})

    def test_saved_catalog_byte_mismatch_has_exact_input_diagnostic(self):
        with TemporaryDirectory() as folder, patch.object(cloud, 'ROOT', Path(folder)):
            (Path(folder) / 'catalog.json').write_bytes(b'new')
            with self.assertRaisesRegex(ValueError, 'catalog.json; expected=old; actual='):
                cloud.data_inputs({'compile_time_data_sha256': {'catalog.json': 'old'}})

    def test_native_metadata_exit_and_size_are_retained(self):
        class Process:
            def wait(self, timeout): return 2
        def spawn(*args, **kwargs):
            kwargs['stdout'].write(b'{}\n'); kwargs['stderr'].write(b'Exact native refusal')
            return Process()
        with TemporaryDirectory() as folder, patch.object(cloud.subprocess, 'Popen', side_effect=spawn):
            with self.assertRaisesRegex(ValueError, 'exit=2, bytes=3, limit=10: Exact native refusal'):
                cloud.capture(['synthetic'], Path(folder) / 'metadata.json', 10)


if __name__ == '__main__': unittest.main()
