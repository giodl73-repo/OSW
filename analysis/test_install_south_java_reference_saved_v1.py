"""Small archive, permission and exact reviewed-evidence refusal checks."""
import copy
import io
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

import install_south_java_reference_saved_v1 as install


class SavedInstallation(unittest.TestCase):
    def test_local_execution_refused_before_data_reads(self):
            with patch.dict('os.environ', {}, clear=True):
                with self.assertRaises(AssertionError):
                    install.controls()

    def archive(self, rows):
            data = io.BytesIO()
            with zipfile.ZipFile(data, 'w') as saved:
                for name, raw in rows:
                    saved.writestr(name, raw)
            data.seek(0)
            return data

    def test_verified_shared_packaging_prefix(self):
            with tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                install.extract_verified(self.archive([('artifact/almanac/test.bin', b'preserve\r\n')]),
                    {'almanac/test.bin': install.sha(b'preserve\r\n')}, target)
                self.assertEqual((target / 'almanac/test.bin').read_bytes(), b'preserve\r\n')

    def test_traversal_refused(self):
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(AssertionError):
                    install.extract_verified(self.archive([('../escape', b'x')]),
                        {'../escape': install.sha(b'x')}, Path(directory))

    def test_duplicate_member_refused(self):
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(AssertionError):
                    install.extract_verified(self.archive([('a', b'x'), ('a', b'x')]),
                        {'a': install.sha(b'x')}, Path(directory))

    def test_wrong_file_hash_refused(self):
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(AssertionError):
                    install.extract_verified(self.archive([('a', b'changed')]),
                        {'a': install.sha(b'reviewed')}, Path(directory))

    def test_disabled_or_overbroad_request_refused(self):
            request = install.read(install.REQUEST)
            request.update(execution_permitted=True, working_branch_installation_permitted=True,
                           cloud_git_object_transport_permitted=True)
            install.verify_request(request)
            for mutation in [{'execution_permitted': False}, {'execution_permitted': 1},
                             {'native_build_permitted': True}, {'local_bulk_sync_permitted': True},
                             {'cloud_git_object_transport_permitted': False}]:
                candidate = {**request, 'execution_permitted': True, 'working_branch_installation_permitted': True,
                             **mutation}
                with self.assertRaises(AssertionError):
                    install.verify_request(candidate)

    def test_exact_reviewed_artifact_and_visual_evidence_are_accepted(self):
        hashes = install.verify_results(*[install.read(p) for p in [install.FULL, install.EXECUTION, install.REVIEW, install.BROWSER]])
        self.assertEqual(len(hashes), 20)
        self.assertEqual(hashes[install.MANIFEST], install.FINAL_MANIFEST)

    def test_changed_binary_scope_source_or_unreviewed_screenshot_are_refused(self):
        originals = [install.read(p) for p in [install.FULL, install.EXECUTION, install.REVIEW, install.BROWSER]]
        for mode in ['binary', 'physical', 'source', 'visual']:
            rows = copy.deepcopy(originals)
            if mode == 'binary': rows[0]['generated_sha256']['almanac/query-engine.wasm'] = '0' * 64
            elif mode == 'physical': rows[0]['new_physical_dimensions'] = 1
            elif mode == 'source': rows[0]['source_commit'] = '0' * 40
            else: rows[2]['screenshots'][0]['sha256'] = '0' * 64
            with self.assertRaises(AssertionError):
                install.verify_results(*rows)


if __name__ == '__main__':
    unittest.main()
