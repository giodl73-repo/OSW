"""Small metadata, refusal and adversarial archive tests; no engine loads."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import install_chen_indian_sec_saved_v1 as install


class SavedInstallation(unittest.TestCase):
    def test_local_refusal_precedes_all_io(self):
        with patch.object(install, 'read', side_effect=AssertionError('No files allowed')), \
             patch.object(install, 'head', side_effect=AssertionError('No network allowed')), \
             patch.dict(install.os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'Cloud-only'):
                install.controls()

    def test_exact_reviewed_metadata(self):
        files, raw = install.evidence()
        self.assertEqual(len(files), 18)
        self.assertEqual(install.sha(raw), install.contract.FINAL_MANIFEST)

    def test_archive_exact_bytes_and_refusal(self):
        raw = b'bounded\x00binary\r\n'
        path = 'almanac/query-parts/test.bin'
        files = {path: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}}
        for case in ('valid', 'extra', 'duplicate', 'traversal', 'symlink', 'changed', 'size'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                archive = root / 'saved.zip'
                with zipfile.ZipFile(archive, 'w') as saved:
                    item = zipfile.ZipInfo('../outside' if case == 'traversal' else path)
                    if case == 'symlink':
                        item.create_system = 3
                        item.external_attr = 0o120777 << 16
                    saved.writestr(item, b'wrong' if case == 'changed' else raw)
                    if case == 'extra':saved.writestr('extra', b'x')
                    if case == 'duplicate':
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter('ignore', UserWarning)
                            saved.writestr(path, raw)
                metadata = {k: dict(v) for k, v in files.items()}
                if case == 'size':metadata[path]['bytes'] += 1
                if case == 'valid':
                    install.extract_exact(archive, root / 'out', metadata)
                    self.assertEqual((root / 'out' / path).read_bytes(), raw)
                else:
                    with self.assertRaises(ValueError):install.extract_exact(archive, root / 'out', metadata)
                self.assertFalse((root / 'outside').exists())


if __name__ == '__main__':unittest.main()
