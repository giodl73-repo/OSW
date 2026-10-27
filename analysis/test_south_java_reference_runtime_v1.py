"""Receipt atomicity and complete selected catalogue preservation on small fixtures."""
import copy
import json
import unittest

import south_java_reference_fixture_v1 as fixture
import south_java_reference_runtime_v1 as runtime

query = runtime.query


class RuntimeProjection(unittest.TestCase):
    def test_prepare_preserves_unrelated_tables_and_manifest_namespaces(self):
        contract, collections, manifest, _ = fixture.unprepared()
        before = copy.deepcopy(collections)
        widths, samples = collections['widths'], collections['width_samples']
        runtime.prepare(collections, manifest, contract, parent_logical_sha256=query.PARENT)
        self.assertIs(collections['widths'], widths)
        self.assertIs(collections['width_samples'], samples)
        self.assertEqual(collections['sources'][:210], before['sources'])
        self.assertEqual(collections['reference_routes'][:81], before['reference_routes'])
        self.assertEqual(manifest['preserved_namespace'], {'sentinel': 'unchanged'})
        receipt = manifest[runtime.KEY]
        self.assertEqual(receipt['prior_owner'], before['objects'][0])
        self.assertEqual(receipt['prior_decision'], before['route_decisions'][0])
        self.assertEqual(runtime.sha(receipt['owner_fingerprint_json'].encode()), collections['objects'][0]['fingerprint'])
        self.assertEqual(json.loads(receipt['section_fingerprint_json']), collections['reference_routes'][-1])

    def test_stale_or_changed_receipts_refused_without_mutation(self):
        for mode in ['parent', 'planning', 'contract']:
            contract, collections, manifest, _ = fixture.unprepared()
            parent = query.PARENT
            if mode == 'parent':
                parent = '0' * 64
            elif mode == 'planning':
                manifest['input_sha256'][runtime.PLANNING] = '0' * 64
            else:
                contract['atlas_report']['whole_current_length_km'] = 1100
            before = copy.deepcopy((collections, manifest))
            with self.assertRaises(ValueError):
                runtime.prepare(collections, manifest, contract, parent_logical_sha256=parent)
            self.assertEqual((collections, manifest), before)

    def test_complete_catalogue_projection_preserves_prefix_and_scope(self):
        contract, collections, manifest, catalog = fixture.unprepared()
        before = copy.deepcopy(catalog)
        runtime.prepare(collections, manifest, contract, parent_logical_sha256=query.PARENT)
        output = runtime.catalog_projection(catalog, collections, contract)
        self.assertEqual(catalog, before)
        self.assertEqual(output['candidates'][:81], catalog['candidates'])
        self.assertEqual(output['counts'], {'route_candidates': 82, 'currents_with_route_candidates': 75,
            'currents_without_route_candidates': 20, 'currents_without_any_reference_card': 20})
        self.assertEqual(output['planning_taxonomy']['strategies'][1], catalog['planning_taxonomy']['strategies'][1])
        entry = output['candidates'][-1]
        self.assertEqual(entry['figure'], query.FIGURE)
        self.assertEqual(entry['compact_figure_file'], query.COMPACT)
        self.assertEqual(entry['nominal_atlas_state_crossings'], [])
        self.assertFalse(entry['physical_state_join_eligible'])
        self.assertEqual(entry['report_inline'], contract['atlas_report'])

    def test_repeat_projection_and_counter_underflow_refused(self):
        contract, collections, manifest, catalog = fixture.unprepared()
        runtime.prepare(collections, manifest, contract, parent_logical_sha256=query.PARENT)
        output = runtime.catalog_projection(catalog, collections, contract)
        with self.assertRaises(ValueError):
            runtime.catalog_projection(output, collections, contract)
        catalog['planning_taxonomy']['strategies'][0]['unbuilt_count'] = 0
        before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            runtime.catalog_projection(catalog, collections, contract)
        self.assertEqual(catalog, before)


if __name__ == '__main__':
    unittest.main()
