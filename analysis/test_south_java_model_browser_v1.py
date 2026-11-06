"""Small archive/transport fixtures and local refusal; no browser or real data."""
import hashlib
import json
from pathlib import Path
import stat
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

import check_south_java_model_browser_v1 as browser
import south_java_model_browser_custody_v1 as custody
from south_java_model_delivery_v1 import DOCUMENTS, FIGURE, GENERATED, UI, WASM


def sha(raw): return hashlib.sha256(raw).hexdigest()


class BrowserCustody(unittest.TestCase):
    def test_fresh_checkout_initializes_once_and_refuses_existing_run(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / '.pytest_cache' / 'browser-case'
            proof = {'synthetic_custody_verified': True}
            with patch.object(browser, 'OUTPUT', output), patch.object(browser, 'controls'), \
                    patch.object(browser, 'restore', return_value=proof) as restore, \
                    patch.object(browser, 'run_browser') as run, \
                    patch('sys.argv', ['check', '--cloud-browser']):
                browser.main()
                self.assertEqual(json.loads((output / 'custody.json').read_bytes()), proof)
                restore.assert_called_once_with()
                run.assert_called_once_with(proof)
                with self.assertRaises(FileExistsError): browser.main()
                self.assertEqual(restore.call_count, 1)

    def test_local_refusal_before_files_or_browser(self):
        with patch.object(browser.Path, 'read_bytes', side_effect=AssertionError('Data read')):
            with self.assertRaises(RuntimeError): browser.controls({})

    def test_wrong_branch_refusal_before_files_or_browser(self):
        with patch.object(browser.Path, 'read_bytes', side_effect=AssertionError('Data read')):
            with self.assertRaises(RuntimeError):
                browser.controls({'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'giodl73-repo/OSW',
                                  'GITHUB_REF': 'refs/heads/main'})

    def info(self, path):
        info = zipfile.ZipInfo(path); info.file_size = 1
        return info

    def test_only_expected_derived_members_allowed(self):
        info = self.info('almanac/query-data.json')
        self.assertEqual(custody.members([info], [info.filename]), [info])
        with self.assertRaises(ValueError): custody.members([info, info], [info.filename])
        with self.assertRaises(ValueError): custody.members([info], ['other.json'])

    def test_member_traversal_and_symlinks_refused(self):
        for path in ['../outside', '/absolute', 'a\\b', 'a:b']:
            with self.assertRaises(ValueError): custody.members([self.info(path)], [path])
        info = self.info('almanac/query-data.json')
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaises(ValueError): custody.members([info], [info.filename])

    def test_member_byte_budget_refused(self):
        info = self.info('almanac/query-data.json'); info.file_size = 201326593
        with self.assertRaises(ValueError): custody.members([info], [info.filename])

    def fixture(self, root):
        body = b'{"schema":"osw.query-bundle.v1"}\n'
        pin = sha(body); part_path = 'almanac/query-parts/000000-' + pin + '.bin'
        packet = {'schema': 'osw.query-packet.v1', 'logical_schema': 'osw.query-bundle.v1',
                  'hash_algorithm': 'sha256', 'logical_sha256': pin, 'logical_byte_length': len(body),
                  'part_byte_limit': 16777216, 'parts': [{'index': 0, 'path': part_path[8:],
                    'sha256': pin, 'byte_length': len(body)}]}
        files = {path: b'{}\n' for path in GENERATED | UI | DOCUMENTS | {FIGURE}}
        files['almanac/query-data.json'] = json.dumps(packet).encode()
        files[part_path] = body; files[WASM] = b'tiny-test-binary'
        wasm_sha = sha(files[WASM])
        files['almanac/query-engine.manifest.json'] = json.dumps({'sha256': {p: sha(v) for p, v in files.items()}}).encode()
        for path, raw in files.items():
            target = root / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        generated = GENERATED | {'almanac/query-engine.manifest.json'}
        result = {'generated_sha256': {path: sha(files[path]) for path in generated},
                  'artifact_paths': sorted(generated | {part_path}), 'logical_sha256': pin, 'logical_bytes': len(body)}
        return result, part_path, wasm_sha

    def test_streamed_logical_and_engine_custody(self):
        with TemporaryDirectory() as folder:
            root = Path(folder); result, _, wasm_sha = self.fixture(root)
            with patch.object(custody, 'WASM_SHA', wasm_sha):
                proof = custody.verify(root, result)
            self.assertEqual(proof['verified_packet_parts'], 1)
            self.assertFalse(proof['full_packet_parsed'])
            self.assertFalse(proof['source_index_decompressed_in_python'])

    def test_changed_part_and_changed_display_source_refused(self):
        with TemporaryDirectory() as folder:
            root = Path(folder); result, part, wasm_sha = self.fixture(root)
            with patch.object(custody, 'WASM_SHA', wasm_sha):
                original = (root / part).read_bytes(); (root / part).write_bytes(b'x' * len(original))
                with self.assertRaisesRegex(ValueError, 'part hash'): custody.verify(root, result)
                (root / part).write_bytes(original)
                (root / 'almanac/model-section-card.js').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'source pin'): custody.verify(root, result)


if __name__ == '__main__': unittest.main()
