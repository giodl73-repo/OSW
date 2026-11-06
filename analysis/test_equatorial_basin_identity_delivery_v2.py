import ast
import copy
import os
import unittest
from unittest.mock import patch
import equatorial_basin_identity_delivery_v2 as delivery
import equatorial_basin_identity_runtime_v2 as runtime
import check_equatorial_basin_delivery_v2 as controller
import check_equatorial_basin_browser_v2 as browser


class Delivery(unittest.TestCase):
    def setup_manifest(self):
        scope = runtime.scopes()
        parent = runtime.query.read(scope['parent_engine_manifest_file'])
        inventory = delivery.inventory(scope, logical_sha='b' * 64, catalog_sha='c' * 64)
        replacements = {**inventory['rust_source_sha256'], **inventory['compile_time_data_sha256']}
        replacements.update({p: r['candidate_sha256'] for p, r in scope['runtime_source_changes'].items()})
        proof = {'production_dependencies': [runtime.query.FILE, runtime.query.PLANNING,
                  'rust/osw-query/src/equatorial_basin_identities.rs', 'rust/osw-query/src/taxonomy.rs', 'almanac/index-catalog.json',
                  'rust/osw-query/src/index_store.rs'], 'test_only_fixtures_compiled': 0,
                 'compiled_catalog_dependency_verified': True}
        kwargs = {'generated_paths': {'almanac/index-catalog.json'}, 'logical_sha': 'b' * 64,
                  'wasm_sha': 'd' * 64, 'source_commit': 'e' * 40, 'compiler': 'rustc 1.95.0 fixture',
                  'inventory': inventory, 'proof': proof}
        return scope, parent, replacements, kwargs

    def test_local_controller_and_browser_refuse_before_data_read(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(controller, 'sha', side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):
                controller.controls()
        with patch.dict(os.environ, {}, clear=True), patch.object(runtime, 'contract', side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):
                browser.browser_review(None, None)

    def test_inventory_contains_all_frozen_sources_and_two_new_production_documents(self):
        scope = runtime.scopes()
        before = copy.deepcopy(scope)
        inventory = delivery.inventory(scope, logical_sha='b' * 64, catalog_sha='c' * 64)
        self.assertEqual(scope, before)
        self.assertEqual(len(inventory['rust_source_sha256']), 111)
        self.assertEqual(len(inventory['compile_time_data_sha256']), 164)
        self.assertEqual(inventory['compile_time_data_sha256']['almanac/index-catalog.json'], 'c' * 64)
        for path in [runtime.query.FILE, runtime.query.PLANNING]:
            self.assertEqual(inventory['compile_time_data_sha256'][path], runtime.query.sha(path))
            self.assertNotIn(path, inventory['excluded_test_only_data_references'])

    def test_engine_receipt_preserves_all_historical_namespaces_and_reports_no_measurements(self):
        scope, parent, replacements, kwargs = self.setup_manifest()
        before = copy.deepcopy(parent)
        result = delivery.engine_manifest(parent, replacements, scope, **kwargs)
        self.assertEqual(parent, before)
        for key in parent:
            if key not in ['sha256', 'rustc']:
                self.assertEqual(result[key], parent[key])
        receipt = result[delivery.KEY]
        self.assertEqual(receipt['new_identity_records'], 5)
        self.assertEqual(receipt['source_documents_after'], 639)
        self.assertEqual(receipt['new_publication_sources'], 0)
        self.assertEqual(receipt['new_width_records'], 0)
        self.assertEqual(receipt['new_length_records'], 0)
        self.assertEqual(receipt['previous_binary_sha256'], runtime.PARENT_WASM)

    def test_rebinding_unrelated_source_or_changed_candidate_source_refused(self):
        scope, parent, replacements, kwargs = self.setup_manifest()
        for path in ['rust/osw-query/src/index_store.rs', 'rust/osw-query/src/lib.rs']:
            bad = copy.deepcopy(replacements)
            bad[path] = 'f' * 64
            with self.assertRaises(ValueError):
                delivery.engine_manifest(parent, bad, scope, **kwargs)

    def test_missing_required_production_dependency_or_compiled_fixture_refused(self):
        scope, parent, replacements, kwargs = self.setup_manifest()
        for path in kwargs['proof']['production_dependencies']:
            bad = copy.deepcopy(kwargs)
            bad['proof']['production_dependencies'].remove(path)
            with self.assertRaises(ValueError, msg=path):
                delivery.engine_manifest(parent, replacements, scope, **bad)
        for key, value in [('test_only_fixtures_compiled', 1), ('compiled_catalog_dependency_verified', False)]:
            bad = copy.deepcopy(kwargs)
            bad['proof'][key] = value
            with self.assertRaises(ValueError):
                delivery.engine_manifest(parent, replacements, scope, **bad)

    def test_wrong_parent_compiler_and_repeated_extension_refused(self):
        scope, parent, replacements, kwargs = self.setup_manifest()
        with self.assertRaises(ValueError):
            delivery.engine_manifest(parent, replacements, scope, **{**kwargs, 'compiler': 'rustc other'})
        result = delivery.engine_manifest(parent, replacements, scope, **kwargs)
        with self.assertRaises(ValueError):
            delivery.engine_manifest(result, replacements, scope, **kwargs)
        bad = copy.deepcopy(parent)
        bad['sha256'][delivery.WASM] = '0' * 64
        with self.assertRaises(ValueError):
            delivery.engine_manifest(bad, replacements, scope, **kwargs)

    def test_workflow_serializes_candidate_and_keeps_installation_separate(self):
        workflow = (runtime.query.ROOT / controller.WORKFLOW).read_text()
        self.assertIn('group: osw-current-gap-delivery', workflow)
        self.assertIn('cancel-in-progress: false', workflow)
        self.assertIn('OSW_EQUATORIAL_BASIN_IDENTITY_DELIVERY_V2: "1"', workflow)
        self.assertIn('if: needs.select-request.outputs.execute == \'true\'', workflow)
        self.assertNotIn('install_equatorial', workflow)
        for name in ['check_equatorial_basin_delivery_v2.py', 'check_equatorial_basin_browser_v2.py',
                     'equatorial_basin_identity_delivery_v2.py']:
            ast.parse((runtime.query.ROOT / 'analysis' / name).read_text())


if __name__ == '__main__':
    unittest.main()
