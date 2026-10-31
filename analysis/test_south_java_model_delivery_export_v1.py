"""Refuse local or wrong-branch export before any packet/index/binary reads."""
import unittest
from unittest.mock import patch
import export_south_java_model_delivery_v1 as export


class Refusal(unittest.TestCase):
    def test_local_host_opens_no_data(self):
        with patch.object(export.Path, 'read_bytes', side_effect=AssertionError('File read')):
            with self.assertRaises(RuntimeError):
                export.controls({})

    def test_wrong_branch_opens_no_data(self):
        with patch.object(export.Path, 'read_bytes', side_effect=AssertionError('File read')):
            with self.assertRaises(RuntimeError):
                export.controls({'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'giodl73-repo/OSW',
                                 'GITHUB_REF': 'refs/heads/main'})


if __name__ == '__main__':
    unittest.main()
