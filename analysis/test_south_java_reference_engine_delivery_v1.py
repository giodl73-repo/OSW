"""Metadata-only matching-engine and inherited source custody checks."""
import copy
import json
import unittest

import south_java_reference_engine_delivery_v1 as engine
import south_java_reference_runtime_scope_v1 as scope_source
from query_packet import PART_LIMIT

ROOT = engine.runtime.ROOT


def read(path):
    return json.loads((ROOT / path).read_bytes())


class EngineDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = scope_source.build()
        cls.parent = read('research/pacific-secc-installation-saved-engine-manifest-v1.json')
        cls.original = read('research/pacific-secc-full-delivery-compile-inventory-v1.json')
        cls.bindings = read('research/eacc-connection-presentation-parent-source-bindings-v3.json')['bindings']

    def inventory(self):
        return engine.compile_inventory(self.original, self.parent, self.scope, 'c' * 64, 'b' * 64)

    def arguments(self):
        inventory = self.inventory()
        length = 190500000
        parts = []
        for i, offset in enumerate(range(0, length, PART_LIMIT)):
            sha = engine.runtime.sha(('fixture-part-' + str(i)).encode())
            parts.append({'index': i, 'path': f'query-parts/{i:06d}-{sha}.bin',
                          'byte_length': min(PART_LIMIT, length - offset), 'sha256': sha})
        packet = {'schema': 'osw.query-packet.v1', 'logical_schema': 'osw.query-bundle.v1',
            'hash_algorithm': 'sha256', 'part_byte_limit': PART_LIMIT, 'parts': parts,
            'logical_sha256': 'b' * 64, 'logical_byte_length': length}
        source_pins = {p: r['candidate_sha256'] for p, r in self.scope['runtime_source_changes'].items()}
        source_pins.update(self.scope['added_runtime_source'])
        source_pins.update(self.scope['additional_compiled_source_contracts'])
        part_pins = {'almanac/' + p['path']: p['sha256'] for p in parts}
        paths = engine.GENERATED | engine.delivery.DOCUMENTS | set(source_pins) | set(part_pins)
        replacements = {p: 'd' * 64 for p in paths}
        replacements.update(part_pins); replacements.update(source_pins)
        replacements[engine.delivery.CATALOG] = 'c' * 64
        actual = sorted(set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256']))
        proof = {'production_dependencies': actual, 'production_dependency_count': len(actual),
                 'test_only_fixtures_compiled': 0, 'compiled_catalog_dependency_verified': True}
        return inventory, packet, source_pins, replacements, proof

    def overlay(self, args):
        return engine.engine_manifest(self.parent, args[0], self.scope, args[1], args[3], args[2], args[4],
            wasm_sha='e' * 64, compiler='rustc 1.95.0 (test fixture)',
            parent_manifest_sha=engine.PARENT_MANIFEST_SHA, source_commit='a' * 40)

    def test_inventory_preserves_every_inherited_path_and_test_fixture_location(self):
        result = self.inventory()
        self.assertEqual(len(result['rust_source_sha256']), 100)
        self.assertEqual(len(result['compile_time_data_sha256']), 147)
        self.assertEqual(len(result['excluded_test_only_data_references']), 9)
        for p, refs in self.original['excluded_test_only_data_references'].items():
            self.assertEqual(result['excluded_test_only_data_references'][p], refs)
        for p, sha in self.original['compile_time_data_sha256'].items():
            if p != engine.delivery.CATALOG:
                self.assertEqual(result['compile_time_data_sha256'][p], sha)
        self.assertNotIn('almanac/reference-routes.js', result['rust_source_sha256'])
        bad = copy.deepcopy(self.scope)
        next(iter(bad['runtime_source_changes'].values()))['historical_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            engine.compile_inventory(self.original, self.parent, bad, 'c' * 64, 'b' * 64)

    def test_matching_overlay_preserves_all_parent_namespaces_and_other_pins(self):
        result = self.overlay(self.arguments())
        for k in self.parent:
            if k not in {'sha256', 'rustc'}:
                self.assertEqual(result[k], self.parent[k])
        allowed = engine.GENERATED | set(self.scope['runtime_source_changes']) | {engine.WASM}
        for p, sha in self.parent['sha256'].items():
            if p not in allowed:
                self.assertEqual(result['sha256'][p], sha)
        self.assertEqual(result[engine.KEY]['new_physical_dimensions'], 0)

    def test_production_proof_cannot_omit_revised_module_or_include_test_fixture(self):
        args = self.arguments()
        missing = 'rust/osw-query/src/pacific_secc_reference.rs'
        args[4]['production_dependencies'].remove(missing)
        args[4]['production_dependency_count'] -= 1
        with self.assertRaises(ValueError):
            self.overlay(args)
        args = self.arguments()
        args[4]['production_dependencies'].extend(engine.FIXTURES)
        args[4]['production_dependency_count'] += 1
        with self.assertRaises(ValueError):
            self.overlay(args)

    def test_unrelated_pin_changes_and_missing_reviewed_ui_are_refused(self):
        args = self.arguments()
        path = 'rust/osw-query/src/asca_calendar.rs'
        args[2][path] = args[3][path] = '0' * 64
        with self.assertRaises(ValueError):
            self.overlay(args)
        args = self.arguments()
        del args[2]['almanac/reference-routes.js']
        del args[3]['almanac/reference-routes.js']
        with self.assertRaises(ValueError):
            self.overlay(args)

    def test_parent_custody_checks_every_pin_and_both_versions_of_changed_sources(self):
        metadata = {p: (h, 1) for p, h in self.parent['sha256'].items()}
        for p, row in self.scope['runtime_source_changes'].items():
            metadata[p] = (row['candidate_sha256'], 2)
            metadata[row['archive_path']] = (row['historical_sha256'], row['bytes'])
        for row in self.bindings:
            metadata[row['manifest_path']] = (row['installed_path_sha256'], row['installed_path_bytes'])
            metadata[row['archive_path']] = (row['historical_sha256'], row['historical_bytes'])
        result = engine.verify_parent(self.parent, metadata.__getitem__, self.bindings, self.scope)
        self.assertEqual(result['manifest_paths_verified'], len(self.parent['sha256']))
        self.assertEqual(len(result['scoped_runtime_paths']), 8)
        archive = next(iter(self.scope['runtime_source_changes'].values()))['archive_path']
        metadata[archive] = ('0' * 64, 1)
        with self.assertRaises(ValueError):
            engine.verify_parent(self.parent, metadata.__getitem__, self.bindings, self.scope)


if __name__ == '__main__':
    unittest.main()
