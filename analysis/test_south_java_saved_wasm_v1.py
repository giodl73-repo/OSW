"""Resource refusal checks: these never load the atlas or WASM binary."""
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
import check_south_java_saved_wasm_v1 as stage


class Refusal(unittest.TestCase):
    def test_local_refusal_precedes_data_reads(self):
        with patch.object(stage.Path, 'read_bytes', side_effect=AssertionError('Data read')):
            with self.assertRaises(RuntimeError):
                stage.controls({})

    def test_wrong_branch_refusal_precedes_data_reads(self):
        with patch.object(stage.Path, 'read_bytes', side_effect=AssertionError('Data read')):
            with self.assertRaises(RuntimeError):
                stage.controls({'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'giodl73-repo/OSW',
                                'GITHUB_REF': 'refs/heads/main'})

    def test_metadata_export_retains_exit_length_and_error(self):
        class Process:
            returncode = 2
            def poll(self): return self.returncode
        def spawn(*args, **kwargs):
            kwargs['stdout'].write(b'{}\n')
            kwargs['stderr'].write(b'Native refusal')
            return Process()
        with TemporaryDirectory() as folder, patch.object(stage.subprocess, 'Popen', side_effect=spawn):
            with self.assertRaisesRegex(ValueError, 'exit=2, bytes=3, budget=10: Native refusal'):
                stage.write_native_metadata('cli', 'candidate', Path(folder) / 'metadata.json', 10)

    def test_completed_metadata_export_still_obeys_budget(self):
        class Process:
            returncode = 0
            def poll(self): return self.returncode
        def spawn(*args, **kwargs):
            kwargs['stdout'].write(b'{}\n')
            return Process()
        with TemporaryDirectory() as folder, patch.object(stage.subprocess, 'Popen', side_effect=spawn):
            with self.assertRaisesRegex(ValueError, 'exit=0, bytes=3, budget=2'):
                stage.write_native_metadata('cli', 'candidate', Path(folder) / 'metadata.json', 2)


if __name__ == '__main__':
    unittest.main()
