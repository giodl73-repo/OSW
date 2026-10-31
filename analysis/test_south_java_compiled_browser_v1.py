"""Small overlay-authenticity and local refusal fixtures; no browser or data."""
import json
import unittest
from unittest.mock import patch

import check_south_java_compiled_browser_v1 as browser
import south_java_compiled_browser_custody_v1 as custody
import south_java_catalog_engine_v1 as engine
from south_java_model_delivery_v1 import sha
import test_south_java_catalog_engine_v1 as fixtures


class CompiledBrowser(unittest.TestCase):
    def fixture(self):
        inventory, parent, scope = fixtures.CatalogEngine().fixture()
        raw = (json.dumps(parent, indent=2) + '\n').encode()
        proof = engine.dependencies(fixtures.CatalogEngine().depinfo(), '/cloud/OSW', inventory)
        updated = engine.overlay(parent, inventory, scope, wasm_sha256='2' * 64,
                                 compiler='rustc 1.95.0 (verified)', parent_manifest_sha256=sha(raw), dependency_proof=proof)
        manifest = (json.dumps(updated, indent=2, allow_nan=False) + '\n').encode()
        result = {'status': 'PASS', 'main_query_responses_equal': 11, 'source_query_responses_equal': 3,
                  'native_and_wasm_mismatched_corpus_refused': True,
                  'restoration': {'parent_manifest_sha256': sha(raw)}, 'wasm_sha256': '2' * 64,
                  'wasm_bytes': 100, 'engine_manifest_sha256': sha(manifest),
                  'compiler': 'rustc 1.95.0 (verified)', 'dependency_proof': proof}
        return raw, manifest, result, inventory, scope

    def test_exact_declared_overlay_is_recomputed(self):
        raw, manifest, result, inventory, scope = self.fixture()
        proof = custody.verify(raw, manifest, '2' * 64, 100, result, inventory, scope)
        self.assertTrue(proof['declared_manifest_overlay_recomputed'])

    def test_wrong_binary_or_parent_refused(self):
        raw, manifest, result, inventory, scope = self.fixture()
        with self.assertRaisesRegex(ValueError, 'binary differs'):
            custody.verify(raw, manifest, '4' * 64, 100, result, inventory, scope)
        with self.assertRaisesRegex(ValueError, 'parent engine'):
            custody.verify(raw + b' ', manifest, '2' * 64, 100, result, inventory, scope)

    def test_matching_hash_alone_cannot_admit_undeclared_manifest_change(self):
        raw, manifest, result, inventory, scope = self.fixture()
        changed = json.loads(manifest); changed['hidden_source_change'] = True
        corrupt = (json.dumps(changed, indent=2) + '\n').encode()
        result['engine_manifest_sha256'] = sha(corrupt)
        with self.assertRaisesRegex(ValueError, 'declared source/data/binary overlay'):
            custody.verify(raw, corrupt, '2' * 64, 100, result, inventory, scope)

    def test_incomplete_source_api_proof_refused(self):
        raw, manifest, result, inventory, scope = self.fixture()
        result['source_query_responses_equal'] = 0
        with self.assertRaisesRegex(ValueError, 'Complete matching-catalog API proof'):
            custody.verify(raw, manifest, '2' * 64, 100, result, inventory, scope)

    def test_local_refusal_before_data_or_browser(self):
        with patch.object(browser.Path, 'read_bytes', side_effect=AssertionError('File read')):
            with self.assertRaises(RuntimeError): browser.controls({})

    def test_wrong_branch_refusal_before_data_or_browser(self):
        with patch.object(browser.Path, 'read_bytes', side_effect=AssertionError('File read')):
            with self.assertRaises(RuntimeError):
                browser.controls({'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'giodl73-repo/OSW',
                                  'GITHUB_REF': 'refs/heads/main'})


if __name__ == '__main__': unittest.main()
