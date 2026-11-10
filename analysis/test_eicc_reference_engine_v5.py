"""Small fixtures verify compiler/source overlays and engine-to-browser custody."""
import copy
import json
import unittest

import eicc_reference_delivery_v5 as delivery
import eicc_reference_query_v1 as context
import eicc_reference_snapshot_custody_v3 as snapshots
from query_packet import PART_LIMIT


class EiccEngineCustody(unittest.TestCase):
    def test_guard_correction_requires_the_exact_preserved_candidate_bytes(self):
        packet = {'logical_byte_length': 190404811,
                  'logical_sha256': '93c7c184e547ad0c2801ff2183cc5f88f2e11f6150b69b7583fc2f0db05ab696'}
        delivery.verify_candidate_identity(packet)
        for key, value in [('logical_byte_length', 190404812), ('logical_byte_length', True),
                           ('logical_sha256', '0' * 64)]:
            changed = {**packet, key: value}
            with self.assertRaises(ValueError): delivery.verify_candidate_identity(changed)

    @classmethod
    def setUpClass(cls):
        cls.scope = json.loads((context.ROOT / delivery.SCOPE).read_bytes())
        cls.contract = context.build_contract()

    def overlay(self):
        rust = {p: c['parent_sha256'] for p, c in self.scope['runtime_source_changes'].items()}
        rust['rust/osw-query/src/index_store.rs'] = '1' * 64
        rust.update({'rust/osw-query/src/fixture_' + str(i) + '.rs': '1' * 64 for i in range(91)})
        data = {delivery.CATALOG: '2' * 64, **{'research/fixture_' + str(i) + '.json': '3' * 64 for i in range(143)}}
        original = {'rust_source_sha256': rust, 'compile_time_data_sha256': data,
                    'excluded_test_only_data_references': ['test-only-' + str(i) for i in range(6)]}
        parent = {'schema': 'osw.query-engine-manifest.v1', 'abi_version': 1,
            'sha256': {**rust, **data, delivery.CATALOG: '4' * 64, delivery.WASM: delivery.PARENT_WASM_SHA,
                       **{p: c['parent_sha256'] for p, c in self.scope['presentation_source_changes'].items()}},
            'loop_published_metrics_presentation_revision_v1': {'archive': 'retained'}}
        packet = {'schema': 'osw.query-packet.v1', 'logical_schema': 'osw.query-bundle.v1',
            'hash_algorithm': 'sha256', 'part_byte_limit': PART_LIMIT, 'logical_sha256': '7' * 64,
            'logical_byte_length': 8, 'parts': [{'index': 0, 'path': 'query-parts/000000-' + '8' * 64 + '.bin',
                                              'sha256': '8' * 64, 'byte_length': 8}]}
        pins = {**{p: '6' * 64 for p in delivery.DOCUMENTS}, **self.contract['input_sha256'],
                context.FILE: delivery.sha(context.encoded(self.contract)), delivery.SCOPE: delivery.sha(delivery.encoded(self.scope)),
                delivery.projection.MODULE: delivery.sha((context.ROOT / delivery.projection.MODULE).read_bytes())}
        for path, change in delivery.checked_scope(self.scope).items():
            pins[path] = change['candidate_sha256']; pins[change['archive_path']] = change['parent_sha256']
            if change.get('executed_v2_archive_path'):
                pins[change['executed_v2_archive_path']] = change['working_branch_parent_sha256']
            if change.get('executed_v4_archive_path'):
                pins[change['executed_v4_archive_path']] = change['working_branch_v4_sha256']
        if self.scope.get('prior_scope_file'):
            pins[self.scope['prior_scope_file']] = self.scope['prior_scope_sha256']
        for relocation in self.scope['historical_source_relocations']:
            pins[relocation['archive_path']] = relocation['historical_sha256']
        replacements = {p: '6' * 64 for p in delivery.GENERATED | delivery.DOCUMENTS}
        replacements.update(pins); replacements['almanac/' + packet['parts'][0]['path']] = '8' * 64
        inventory = delivery.compile_inventory(original, parent, replacements[delivery.CATALOG], packet['logical_sha256'], self.scope)
        actual = sorted(delivery.RUNTIME | {delivery.CATALOG, 'rust/osw-query/src/index_store.rs'})
        proof = {'compiled_catalog_dependency_verified': True, 'test_only_fixtures_compiled': 0,
                 'production_dependencies': actual, 'production_dependency_count': len(actual)}
        return dict(parent=parent, original_inventory=original, inventory=inventory,
            replacements=replacements, source_pins=pins, packet=packet, scope=copy.deepcopy(self.scope),
            wasm_sha='9' * 64, compiler='rustc 1.95.0 (fixture)', parent_manifest_sha=delivery.PARENT_MANIFEST_SHA,
            source_commit='a' * 40, dependency_proof=proof)

    def test_only_six_runtime_sources_and_catalog_change_in_compiler_inventory(self):
        args = self.overlay(); before = copy.deepcopy(args)
        result = delivery.engine_manifest(**args)
        self.assertEqual(args, before)
        changed = {p for p, pin in args['original_inventory']['rust_source_sha256'].items()
                   if args['inventory']['rust_source_sha256'][p] != pin}
        self.assertEqual(changed, delivery.RUNTIME)
        data = args['original_inventory']['compile_time_data_sha256']
        self.assertEqual({p for p, pin in data.items() if args['inventory']['compile_time_data_sha256'][p] != pin}, {delivery.CATALOG})
        self.assertEqual(result['loop_published_metrics_presentation_revision_v1'], {'archive': 'retained'})
        for path, change in delivery.checked_scope(self.scope).items():
            self.assertEqual(result['sha256'][path], change['candidate_sha256'])
            self.assertEqual(result['sha256'][change['archive_path']], change['parent_sha256'])

    def test_undeclared_runtime_ui_archive_and_dependency_changes_rejected(self):
        for mutation in ['extra_scope', 'wrong_ui_parent', 'archive', 'runtime', 'missing_dependency', 'old_source']:
            with self.subTest(mutation=mutation):
                args = self.overlay()
                if mutation == 'extra_scope': args['scope']['runtime_source_changes']['extra.rs'] = {}
                elif mutation == 'wrong_ui_parent': args['parent']['sha256']['almanac/reference-routes.js'] = '0' * 64
                elif mutation == 'archive': args['source_pins'][next(iter(self.scope['runtime_source_changes'].values()))['archive_path']] = '0' * 64
                elif mutation == 'runtime': args['inventory']['rust_source_sha256']['rust/osw-query/src/index_store.rs'] = '0' * 64
                elif mutation == 'missing_dependency':
                    args['dependency_proof']['production_dependencies'].remove('rust/osw-query/src/atlas_data.rs')
                    args['dependency_proof']['production_dependency_count'] -= 1
                else:
                    path = 'research/prior-science.json'
                    args['parent']['sha256'][path] = '0' * 64
                    args['source_pins'][path] = '1' * 64; args['replacements'][path] = '1' * 64
                with self.assertRaises(ValueError): delivery.engine_manifest(**args)

    def phase(self):
        args = self.overlay(); manifest = delivery.engine_manifest(**args)
        paths = delivery.GENERATED | {delivery.MANIFEST, delivery.WASM} | {'almanac/' + args['packet']['parts'][0]['path']}
        generated = {p: manifest['sha256'][p] for p in paths - {delivery.MANIFEST}}
        generated[delivery.MANIFEST] = 'b' * 64
        parity = {mode: {'status': 'PASS', 'wasm_sha256': '9' * 64, 'initialization_metadata_equal': True,
                         'checks': [{'entire_response_equal': True} for _ in range(count)],
                         'mismatched_corpus_refused': mode == 'index'}
                  for mode, count in [('main', 24), ('index', 25), ('snapshots', 2)]}
        engine = {'status': 'PASS', 'stage': 'engine_verified', 'source_commit': 'a' * 40,
                  'browser_verified': False, 'working_branch_installed': False,
                  'engine_manifest_sha256': 'b' * 64, 'wasm_sha256': '9' * 64,
                  'verified_generated_sha256': generated, 'verified_generated_artifact_paths': sorted(generated),
                  'native_wasm_parity': parity, 'rust_planning_tests_passed': 6, 'rust_route_inventory_tests_passed': 2, 'native_smoke_verified': True}
        return dict(engine=engine, manifest=manifest, packet=args['packet'], generated_hashes=generated,
                    manifest_sha='b' * 64, source_commit='a' * 40)

    def test_browser_phase_requires_complete_engine_proof_and_all_derived_files(self):
        args = self.phase(); before = copy.deepcopy(args)
        proof = delivery.browser_phase_custody(**args)
        self.assertEqual(proof['status'], 'PASS')
        self.assertFalse(proof['browser_started'])
        self.assertEqual(args, before)
        for mutation in ['partial_queries', 'wrong_artifact', 'source_commit', 'missing_rust_tests', 'missing_route_tests', 'repeat_browser', 'missing_snapshot']:
            with self.subTest(mutation=mutation):
                bad = copy.deepcopy(args)
                if mutation == 'partial_queries': bad['engine']['native_wasm_parity']['main']['checks'].pop()
                elif mutation == 'wrong_artifact': bad['generated_hashes'][delivery.WASM] = '0' * 64
                elif mutation == 'source_commit': bad['source_commit'] = 'c' * 40
                elif mutation == 'missing_rust_tests': bad['engine']['rust_planning_tests_passed'] = 0
                elif mutation == 'missing_route_tests': bad['engine']['rust_route_inventory_tests_passed'] = 0
                elif mutation == 'repeat_browser': bad['engine']['browser_verified'] = True
                else: bad['engine']['native_wasm_parity'].pop('snapshots')
                with self.assertRaises(ValueError): delivery.browser_phase_custody(**bad)


class EiccSnapshotCustody(unittest.TestCase):
    def fixture(self):
        parent = {'ok': True, 'bundle_sha256': delivery.PARENT_LOGICAL_SHA,
                  'working_reference_routes': {'old': True}, 'phase_plans': {'unchanged': False},
                  'sources_json': {delivery.DASHBOARD: 'old dashboard', 'research/prior.json': '{ "exact": true }\n'}}
        child = copy.deepcopy(parent); child['bundle_sha256'] = '7' * 64
        catalog = {'two_new_cards': True}; child['working_reference_routes'] = catalog
        child['sources_json'][delivery.DASHBOARD] = 'new dashboard'
        return parent, child, catalog

    def test_exact_old_sources_and_unrelated_views_are_preserved(self):
        parent, child, catalog = self.fixture()
        audit = snapshots.verify(parent, child, catalog, 'new dashboard', '7' * 64)
        self.assertEqual(audit['original_source_documents_preserved'], 1)
        self.assertTrue(audit['complete_catalog_matches_source_projection'])

    def test_unrelated_scene_source_bytes_and_catalog_differences_are_rejected(self):
        for mutation in ['scene', 'source', 'catalog', 'new_root_field']:
            with self.subTest(mutation=mutation):
                parent, child, catalog = self.fixture()
                if mutation == 'scene': child['phase_plans']['unchanged'] = 0
                elif mutation == 'source': child['sources_json']['research/prior.json'] = '{"exact":true}\n'
                elif mutation == 'catalog': child['working_reference_routes'] = {'wrong': True}
                else: child['extra'] = True
                with self.assertRaises(ValueError): snapshots.verify(parent, child, catalog, 'new dashboard', '7' * 64)


if __name__ == '__main__': unittest.main()
