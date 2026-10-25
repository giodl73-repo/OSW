"""Tiny source/dependency/manifest fixtures; never invokes a compiler."""
import copy
import unittest

import south_java_catalog_engine_v1 as engine


class CatalogEngine(unittest.TestCase):
    def fixture(self):
        sources = {'rust/osw-query/src/lib.rs': 'a' * 64, 'rust/osw-query/src/index_store.rs': 'b' * 64}
        data = {engine.CATALOG: 'c' * 64, 'research/kept.json': 'd' * 64}
        inventory = {'rust_source_sha256': sources, 'compile_time_data_sha256': data,
                     'excluded_test_only_data_references': {'research/test-only.json': []},
                     'saved_candidate_catalog_sha256': 'c' * 64, 'saved_candidate_logical_sha256': 'e' * 64}
        parent = {'schema': 'osw.query-engine-manifest.v1', 'abi_version': 1,
                  'sha256': {**sources, **data, engine.WASM: 'f' * 64, 'almanac/query-data.json': '1' * 64},
                  'historical_receipt': {'retained': True}}
        parent['sha256']['rust/osw-query/src/lib.rs'] = '0' * 64
        scope = {'source_pin_differences': [{'path': 'rust/osw-query/src/lib.rs',
                  'installed_engine_source_sha256': '0' * 64, 'current_native_source_sha256': 'a' * 64}]}
        return inventory, parent, scope

    def depinfo(self, extra=''):
        return '/build/osw_query.wasm: /cloud/OSW/rust/osw-query/src/lib.rs \\\n /cloud/OSW/rust/osw-query/src/index_store.rs /cloud/OSW/rust/osw-query/src/../../../almanac/index-catalog.json ' + extra + '\n'

    def test_compiler_dependencies_require_pinned_catalog_and_guard(self):
        inventory, _, _ = self.fixture()
        proof = engine.dependencies(self.depinfo(), '/cloud/OSW', inventory)
        self.assertEqual(proof['production_dependency_count'], 3)
        self.assertEqual(proof['test_only_fixtures_compiled'], 0)
        with self.assertRaisesRegex(ValueError, 'catalog/guard missing'):
            engine.dependencies('/target: /cloud/OSW/rust/osw-query/src/lib.rs', '/cloud/OSW', inventory)

    def test_unpinned_test_fixture_or_external_dependency_is_refused(self):
        inventory, _, _ = self.fixture()
        for extra in ['/cloud/OSW/research/test-only.json', '/cloud/OSW/unknown.json', '/elsewhere/private.json']:
            with self.assertRaises(ValueError): engine.dependencies(self.depinfo(extra), '/cloud/OSW', inventory)

    def make_overlay(self, inventory, parent, scope):
        return engine.overlay(parent, inventory, scope, wasm_sha256='2' * 64,
            compiler='rustc 1.95.0 (verified)', parent_manifest_sha256='3' * 64,
            dependency_proof=engine.dependencies(self.depinfo(), '/cloud/OSW', inventory))

    def test_overlay_changes_declared_runtime_and_binary_with_provenance(self):
        inventory, parent, scope = self.fixture()
        before = copy.deepcopy(parent)
        updated = self.make_overlay(inventory, parent, scope)
        self.assertEqual(updated['sha256']['almanac/query-data.json'], '1' * 64)
        self.assertEqual(updated['historical_receipt'], parent['historical_receipt'])
        self.assertEqual(updated['sha256'][engine.WASM], '2' * 64)
        self.assertEqual(parent, before)

    def test_unlisted_runtime_change_is_refused(self):
        inventory, parent, scope = self.fixture()
        inventory['rust_source_sha256']['rust/osw-query/src/index_store.rs'] = '4' * 64
        with self.assertRaisesRegex(ValueError, 'declared prior'): self.make_overlay(inventory, parent, scope)

    def test_scientific_or_saved_catalog_pin_cannot_be_rewritten(self):
        for path in ['research/kept.json', engine.CATALOG]:
            inventory, parent, scope = self.fixture()
            inventory['compile_time_data_sha256'][path] = '4' * 64
            with self.assertRaises(ValueError): self.make_overlay(inventory, parent, scope)


if __name__ == '__main__': unittest.main()
