"""Local refusal checks never read packet files or invoke a compiler."""
import unittest
import subprocess
from unittest.mock import patch
import check_south_java_model_layer_cloud_v1 as check


class ResourceRefusalTests(unittest.TestCase):
    def test_native_failure_preserves_stderr_instead_of_parsing_empty_stdout(self):
        result=subprocess.CompletedProcess([],1,stdout=b'',stderr=b'Native source validation failed')
        with self.assertRaisesRegex(ValueError,'exit 1.*Native source validation failed'):
            check.decode_native_result(result)

    def test_silent_native_kill_or_empty_success_has_explicit_diagnostic(self):
        for code,message in [(-9,'exit -9'),(0,'empty or invalid JSON')]:
            with self.subTest(code=code),self.assertRaisesRegex(ValueError,message):
                check.decode_native_result(subprocess.CompletedProcess([],code,stdout=b'',stderr=b''))

    def test_valid_native_json_is_retained(self):
        self.assertEqual(check.decode_native_result(subprocess.CompletedProcess([],0,stdout=b'{"ok":true,"rows":[]}',stderr=b'')),
                         {'ok':True,'rows':[]})

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
