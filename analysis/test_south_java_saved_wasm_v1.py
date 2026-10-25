"""Resource refusal checks: these never load the atlas or WASM binary."""
import unittest
from unittest.mock import patch
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


if __name__ == '__main__':
    unittest.main()
