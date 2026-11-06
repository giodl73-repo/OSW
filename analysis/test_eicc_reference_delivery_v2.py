"""Source-only tests of the planning-receipt and declared Rust-source correction."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import eicc_reference_delivery_v2 as delivery
import eicc_reference_query_v1 as context
import test_eicc_reference_delivery_v1 as fixtures


class EiccPlanningRevision(unittest.TestCase):
    def bundle(self):
        bundle = fixtures.EiccDelivery().bundle()
        rows = bundle['collections']
        rows[context.ROUTES] = []
        owner = rows['objects'][0]
        owner['route_ids'] = []
        owner['capabilities']['reference_route'] = 0
        decision = rows['route_decisions'][0]
        decision.update(route_ids=[], candidate_count=0, source_catalog_file=delivery.OLD_SOURCE,
                        source_catalog_sha256='1' * 64, source_url='https://example.org/original')
        decision['source_decision'].update(candidate_ids=[], name_source_url=decision['source_url'])
        dashboard = json.loads(bundle['manifest']['dashboard_receipt']['source_json'])
        dashboard['entries'] = copy.deepcopy(rows['objects'])
        raw = delivery.encoded(dashboard)
        bundle['manifest']['dashboard_receipt'].update(source_json=raw.decode(), source_sha256=delivery.sha(raw))
        bundle['manifest']['input_sha256'][delivery.DASHBOARD] = delivery.sha(raw)
        bundle['manifest']['input_sha256'][delivery.OLD_SOURCE] = '1' * 64
        return bundle

    def test_candidate_source_url_matches_nested_projection_and_prior_is_exact(self):
        parent = self.bundle(); before = delivery.encoded(parent)
        child, _, audit = delivery.candidate(parent, context.build_contract())
        self.assertEqual(delivery.encoded(parent), before)
        decision = child['collections']['route_decisions'][0]
        self.assertEqual(decision['source_url'], decision['source_decision']['name_source_url'])
        self.assertEqual(decision['prior_route_decision'], parent['collections']['route_decisions'][0])
        receipt = child['manifest'][delivery.RECEIPT]['planning_revision']
        self.assertEqual(json.loads(receipt['prior_decision_json']), decision['prior_route_decision'])
        self.assertEqual(delivery.sha(receipt['source_json'].encode()), receipt['source_sha256'])
        self.assertEqual(receipt['source_file'], decision['source_catalog_file'])
        self.assertEqual(receipt['source_sha256'], decision['source_catalog_sha256'])
        self.assertTrue(audit['planning_source_url_projection_consistent'])
        for name in ['widths', 'width_samples', 'length_assessments', 'geometries', 'state_links']:
            self.assertEqual(child['collections'][name], parent['collections'][name])

    def overlay(self):
        fixture = fixtures.EiccDelivery()
        fixture.contract = context.build_contract()
        args = fixture.overlay()
        args['original_inventory']['rust_source_sha256'][delivery.PLANNING] = 'a' * 64
        args['parent']['sha256'][delivery.PLANNING] = 'a' * 64
        scope = {'schema': 'osw.eicc-reference-planning-runtime-scope.v2', 'runtime_source_changes': {
            delivery.PLANNING: {'parent_sha256': 'a' * 64, 'candidate_sha256': 'b' * 64, 'archive_path': delivery.ARCHIVE}}}
        args['scope'] = scope
        args['inventory'] = delivery.compile_inventory(args['original_inventory'], args['parent'],
            args['replacements'][delivery.CATALOG], args['packet']['logical_sha256'], scope)
        pins = {delivery.PLANNING: 'b' * 64, delivery.ARCHIVE: 'a' * 64, delivery.SCOPE: delivery.sha(delivery.encoded(scope))}
        args['source_pins'].update(pins); args['replacements'].update(pins)
        args['dependency_proof']['production_dependencies'].append(delivery.PLANNING)
        args['dependency_proof']['production_dependency_count'] += 1
        return args

    def test_compile_overlay_changes_exactly_declared_planning_source_and_catalog(self):
        args = self.overlay(); before = copy.deepcopy(args)
        result = delivery.engine_manifest(**args)
        self.assertEqual(args, before)
        self.assertEqual(result['sha256'][delivery.PLANNING], 'b' * 64)
        self.assertEqual(result['sha256'][delivery.ARCHIVE], 'a' * 64)
        self.assertEqual(result['loop_published_metrics_presentation_revision_v1'],
                         args['parent']['loop_published_metrics_presentation_revision_v1'])
        changes = {p for p, pin in args['parent']['sha256'].items() if result['sha256'][p] != pin}
        self.assertEqual(changes, {delivery.PLANNING, delivery.CATALOG, delivery.WASM})

    def test_scope_archive_parent_identity_and_unrelated_runtime_changes_rejected(self):
        for mutation in ['archive', 'scope', 'parent', 'other_runtime', 'missing_dependency']:
            with self.subTest(mutation=mutation):
                args = self.overlay()
                if mutation == 'archive': args['source_pins'][delivery.ARCHIVE] = '0' * 64
                elif mutation == 'scope': args['scope']['runtime_source_changes']['extra.rs'] = {}
                elif mutation == 'parent': args['scope']['runtime_source_changes'][delivery.PLANNING]['parent_sha256'] = '0' * 64
                elif mutation == 'other_runtime': args['inventory']['rust_source_sha256']['rust/osw-query/src/index_store.rs'] = '0' * 64
                else:
                    args['dependency_proof']['production_dependencies'].remove(delivery.PLANNING)
                    args['dependency_proof']['production_dependency_count'] -= 1
                with self.assertRaises(ValueError): delivery.engine_manifest(**args)

    def test_revised_controller_refuses_local_execution_before_source_reads(self):
        import check_eicc_reference_delivery_v2 as controller
        with patch.object(controller, 'read', side_effect=AssertionError('Unexpected source read')):
            with self.assertRaises(RuntimeError): controller.controls({})

    def test_failed_native_query_retains_bounded_stderr_and_hash(self):
        import check_eicc_reference_delivery_v2 as controller
        message = b'Planning projection differs in source_url\n' + b'x' * 3000
        result = subprocess.CompletedProcess(['fixture'], 2, stdout=b'', stderr=message)
        with tempfile.TemporaryDirectory() as folder, patch.object(controller, 'OUTPUT', Path(folder)), \
                patch.object(controller, 'QUERY_AUDIT', []), patch.object(controller.subprocess, 'run', return_value=result):
            with self.assertRaisesRegex(ValueError, 'Planning projection differs in source_url'):
                controller.native_query('fixture', Path(folder) / 'unused.json', {'collection': context.ROUTES})
            audit = json.loads((Path(folder) / 'native-response-custody.json').read_bytes())[0]
            self.assertEqual(audit['stderr_bytes'], len(message))
            self.assertEqual(audit['stderr_sha256'], delivery.sha(message))
            self.assertEqual(len(audit['stderr_preview']), 2000)


if __name__ == '__main__': unittest.main()
