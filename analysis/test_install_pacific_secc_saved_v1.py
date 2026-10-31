"""Refusal checks for untrusted archive inventories and saved-artifact custody."""
import copy
import io
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

import install_pacific_secc_saved_v1 as install


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
        for mutation in [{'execution_permitted': False}, {'execution_permitted': 1},
                         {'native_build_permitted': True}, {'local_bulk_sync_permitted': True}]:
            candidate = {**request, 'execution_permitted': True, 'working_branch_installation_permitted': True,
                         **mutation}
            with self.assertRaises(AssertionError):
                install.verify_request(candidate)

    def test_reviewed_artifacts_have_exact_preserved_scientific_files(self):
        hashes = install.verify_results(install.read(install.FULL), install.read(install.COMPACT),
            install.read(install.REVIEW), (install.ROOT / install.SAVED).read_bytes())
        self.assertEqual(len(hashes), 22)

    def test_changed_scientific_file_or_unreviewed_screenshot_refused(self):
        full, compact, review = [install.read(p) for p in [install.FULL, install.COMPACT, install.REVIEW]]
        for mode in ['scientific', 'visual']:
            candidate = copy.deepcopy(compact)
            if mode == 'scientific':
                candidate['unchanged_scientific_candidate_paths']['almanac/query-engine.wasm'] = '0' * 64
            else:
                candidate['screenshots'][0]['sha256'] = '0' * 64
            with self.assertRaises(AssertionError):
                install.verify_results(full, candidate, review, (install.ROOT / install.SAVED).read_bytes())


if __name__ == '__main__':
    unittest.main()
