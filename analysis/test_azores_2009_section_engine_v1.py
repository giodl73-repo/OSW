"""Small compiler/source metadata fixtures, never the installed data packet."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
import azores_2009_section_engine_v1 as e


def read(path):
    return json.loads(Path(path).read_bytes())


class MatchingEngine(unittest.TestCase):
    def setUp(self):
        self.parent = read('research/south-java-reference-installation-saved-engine-manifest-v1.json')
        self.inventory = read('research/south-java-reference-full-delivery-compile-inventory-v4.json')
        self.scope = read('research/azores-2009-section-runtime-scope-v1.json')
        self.legacy = read('research/eacc-connection-presentation-parent-source-bindings-v3.json')['bindings']
        # Simulate compiler/source metadata; this does not verify real 1194-file custody.
        self.metadata = {p: (h, 1) for p, h in self.parent['sha256'].items()}
        for row in self.legacy:
            self.metadata[row['manifest_path']] = (row['installed_path_sha256'], row['installed_path_bytes'])
            self.metadata[row['archive_path']] = (row['historical_sha256'], row['historical_bytes'])
        for path, row in self.scope['runtime_source_changes'].items():
            self.metadata[path] = (row['candidate_sha256'], 1)
            self.metadata[row['archive_path']] = (row['historical_sha256'], row['bytes'])
        self.metadata.update({p: (h, 1) for p, h in self.scope['added_runtime_source'].items()})
        self.metadata.update({p: (h, 1) for p, h in self.scope['additional_compiled_source_contracts'].items()})

    def candidate(self):
        return e.compile_inventory(self.inventory, self.parent, self.scope, catalog_sha='c'*64, logical_sha='d'*64)

    def proof(self, inventory):
        actual = sorted(set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256']))
        return {'production_dependencies': actual, 'production_dependency_count': len(actual),
                'compiled_catalog_dependency_verified': True, 'test_only_fixtures_compiled': 0}

    def overlay(self, replacements=None, proof=None):
        inventory = self.candidate()
        changes = {p: 'f'*64 for p in e.GENERATED}
        changes.update({p: r['candidate_sha256'] for p, r in self.scope['runtime_source_changes'].items()})
        changes.update(self.scope['added_runtime_source'])
        changes.update(self.scope['additional_compiled_source_contracts'])
        changes.update(replacements or {})
        return e.engine_manifest(self.parent, inventory, self.scope, changes, logical_sha='d'*64,
            wasm_sha='e'*64, compiler='rustc 1.95.0 fixture', parent_manifest_sha=e.PARENT_MANIFEST_SHA,
            source_commit='a'*40, dependency_proof=proof or self.proof(inventory))

    def test_nine_revisions_and_three_inherited_control_exceptions(self):
        result = e.verify_parent(self.parent, self.metadata.__getitem__, self.legacy, self.scope)
        self.assertEqual(result['manifest_paths_verified'], 1194)
        self.assertEqual(len(result['scoped_runtime_paths']), 9)
        self.assertEqual(len(result['historical_paths']), 3)

    def test_actual_small_runtime_archives_and_candidate_sources_match_scope(self):
        # These are actual byte checks, limited to the nine small source files.
        for path, row in self.scope['runtime_source_changes'].items():
            raw = Path(row['archive_path']).read_bytes()
            self.assertEqual(len(raw), row['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['historical_sha256'])
            self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), row['candidate_sha256'])
        for path, digest in {**self.scope['added_runtime_source'], **self.scope['additional_compiled_source_contracts']}.items():
            self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), digest)

    def test_missing_archive_and_unrelated_byte_change_refused(self):
        archive = next(iter(self.scope['runtime_source_changes'].values()))['archive_path']
        self.metadata[archive] = ('wrong', 1)
        with self.assertRaises(ValueError):
            e.verify_parent(self.parent, self.metadata.__getitem__, self.legacy, self.scope)
        self.setUp()
        self.metadata['rust/osw-query/src/map.rs'] = ('wrong', 1)
        with self.assertRaises(ValueError):
            e.verify_parent(self.parent, self.metadata.__getitem__, self.legacy, self.scope)

    def test_compiler_inventory_keeps_nine_test_only_sources(self):
        candidate = self.candidate()
        self.assertEqual(len(candidate['rust_source_sha256']), 101)
        self.assertEqual(len(candidate['compile_time_data_sha256']), 151)
        self.assertEqual(candidate['excluded_test_only_data_references'], self.inventory['excluded_test_only_data_references'])

    def test_overlay_preserves_complete_historical_namespaces(self):
        result = self.overlay()
        for key in self.parent:
            if key not in ['sha256', 'rustc']:
                self.assertEqual(result[key], self.parent[key])
        with self.assertRaises(ValueError):
            self.overlay({'rust/osw-query/src/map.rs': 'f'*64})

    def test_missing_actual_compiled_contract_or_fixture_leak_refused(self):
        proof = self.proof(self.candidate())
        proof['production_dependencies'].remove(e.projection.BINDINGS)
        proof['production_dependency_count'] -= 1
        with self.assertRaises(ValueError):
            self.overlay(proof=proof)
        proof = self.proof(self.candidate()); proof['test_only_fixtures_compiled'] = 1
        with self.assertRaises(ValueError):
            self.overlay(proof=proof)


if __name__ == '__main__':
    unittest.main()
