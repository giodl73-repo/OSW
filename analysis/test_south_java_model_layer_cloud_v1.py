"""Local refusal checks never read packet files or invoke a compiler."""
import unittest
from unittest.mock import patch
import check_south_java_model_layer_cloud_v1 as check


class ResourceRefusalTests(unittest.TestCase):
    def test_local_execution_refused_before_any_file_access(self):
        with patch.object(check.Path,'read_bytes',side_effect=AssertionError('No file access permitted')):
            with self.assertRaisesRegex(RuntimeError,'no packet read'):
                check.verify_controls({})

    def test_wrong_repository_or_branch_refused_before_file_access(self):
        for changed in [{'GITHUB_REPOSITORY':'other/repo'}, {'GITHUB_REF':'refs/heads/main'}]:
            env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'giodl73-repo/OSW',
                 'GITHUB_REF':'refs/heads/codex/current-measurement-gaps','GITHUB_WORKSPACE':str(check.ROOT),**changed}
            with self.subTest(changed=changed), patch.object(check.Path,'read_bytes',side_effect=AssertionError('No file read')):
                with self.assertRaises(RuntimeError):check.verify_controls(env)


if __name__=='__main__':
    unittest.main()
