"""Small fixtures use the real admitted EICC plan; no full packet or native build."""
import copy
import json
import unittest

import eicc_reference_projection_v3 as projection
import eicc_reference_delivery_v1 as delivery
import eicc_reference_query_v1 as context
import test_eicc_reference_delivery_v1 as fixtures


class EiccAdmissionProjection(unittest.TestCase):
    def bundle(self):
        bundle = fixtures.EiccDelivery().bundle()
        rows = bundle['collections']
        rows[context.ROUTES] = []
        rows['objects'][0]['route_ids'] = []
        rows['objects'][0]['capabilities']['reference_route'] = 0
        rows['route_decisions'][0] = copy.deepcopy(projection.original_decision())
        identity = projection.source(projection.IDENTITY)[1]
        rows['sources'].extend(copy.deepcopy(identity['additions']['sources']))
        rows['objects'][0]['source_ids'].extend(row['id'] for row in identity['additions']['sources'])
        rows['objects'][0]['linked_source_count'] = len(rows['objects'][0]['source_ids'])
        for path in [projection.IDENTITY, projection.PLANNING]:
            bundle['manifest']['input_sha256'][path] = delivery.sha(projection.source(path)[0])
        dashboard = json.loads(bundle['manifest']['dashboard_receipt']['source_json'])
        dashboard['entries'] = copy.deepcopy(rows['objects'])
        raw = delivery.encoded(dashboard)
        bundle['manifest']['dashboard_receipt'].update(source_json=raw.decode(), source_sha256=delivery.sha(raw))
        bundle['manifest']['input_sha256'][delivery.DASHBOARD] = delivery.sha(raw)
        return bundle

    def revised(self): return projection.candidate(self.bundle(), context.build_contract())[0]

    def test_real_admission_source_and_exact_prior_decision_are_preserved(self):
        parent = self.bundle(); original = delivery.encoded(parent)
        child, _, audit = projection.candidate(parent, context.build_contract())
        self.assertEqual(delivery.encoded(parent), original)
        decision = child['collections']['route_decisions'][0]
        self.assertEqual(decision['prior_route_decision'], projection.original_decision())
        self.assertEqual(decision['source_url'], decision['source_decision']['name_source_url'])
        receipt = child['manifest'][delivery.RECEIPT]['planning_revision']
        self.assertEqual(json.loads(receipt['query_contract_json']), context.build_contract())
        self.assertEqual(delivery.sha(receipt['query_contract_json'].encode()), receipt['query_contract_sha256'])
        self.assertEqual(audit['original_admission_planning_source'], projection.PLANNING)
        for name in ['widths', 'width_samples', 'length_assessments', 'geometries', 'state_links']:
            self.assertEqual(child['collections'][name], parent['collections'][name])

    def test_wrong_base_or_receipts_are_rejected_without_parent_mutation(self):
        for mutation in ['legacy_worklist', 'nested_source', 'missing_receipt']:
            with self.subTest(mutation=mutation):
                bundle = self.bundle()
                if mutation == 'legacy_worklist':
                    bundle['collections']['route_decisions'][0]['source_catalog_file'] = 'research/ocean-current-reference-path-candidates.json'
                elif mutation == 'nested_source':
                    bundle['collections']['route_decisions'][0]['source_decision']['name_source_url'] = 'https://example.org/wrong'
                else: bundle['manifest']['input_sha256'].pop(projection.PLANNING)
                before = delivery.encoded(bundle)
                with self.assertRaises(ValueError): projection.candidate(bundle, context.build_contract())
                self.assertEqual(delivery.encoded(bundle), before)

    def test_inline_reports_keep_complete_saved_geometry_and_separate_sensitivity_spans(self):
        contract = context.build_contract()
        reports = projection.atlas_reports(contract)
        self.assertEqual(list(reports), [row['id'] for row in contract['collections'][context.ROUTES]])
        self.assertEqual([r['scenario_range_km'] for r in reports.values()], [[590, 600], [620, 640]])
        for feature in contract['owner_map_features']:
            report = reports[feature['candidate_id']]
            self.assertEqual(report['coordinates_lon_lat'], feature['geometry']['coordinates'])
            self.assertGreater(len(report['coordinates_lon_lat']), 500)
            self.assertEqual(len(report['source_reference_anchors']), 3)
            self.assertEqual(report['nasa_movie_context'], [])
            self.assertIsNone(report['nominal_atlas_state_crossings'])
            for flag in ['rank_eligible', 'physical_current_axis_admitted', 'physical_state_join_eligible', 'seasonal_playback_eligible']:
                self.assertFalse(report[flag])
            self.assertIsNone(report['whole_current_length_km'])
            self.assertIsNone(report['annual_length_range_km'])

    def test_atlas_counts_one_new_owner_two_cards_and_preserves_length_order(self):
        child = self.revised()
        catalog = {'candidates': [{'id': 'old-route', 'current_id': 'other'}],
            'reference_route_length_order': ['old-route'],
            'remaining_current_decisions': [copy.deepcopy(projection.original_decision()['source_decision']),
                                            {'current_id': 'other', 'candidate_ids': ['old-route']}],
            'counts': {'accepted_current_names': 3, 'route_candidates': 1, 'currents_with_route_candidates': 1,
                       'currents_without_route_candidates': 2, 'currents_without_any_reference_card': 2},
            'planning_taxonomy': {'strategies': [{'id': 'source_axis_definition_required', 'current_count': 1, 'unbuilt_count': 1}]}}
        original = copy.deepcopy(catalog)
        result = projection.catalog_projection(catalog, child)
        self.assertEqual(catalog, original)
        self.assertEqual(result['counts'], {'accepted_current_names': 3, 'route_candidates': 3,
            'currents_with_route_candidates': 2, 'currents_without_route_candidates': 1, 'currents_without_any_reference_card': 1})
        self.assertEqual(result['reference_route_length_order'], ['old-route'])
        self.assertEqual(result['candidates'][0], catalog['candidates'][0])
        self.assertEqual(result['remaining_current_decisions'][1], catalog['remaining_current_decisions'][1])
        self.assertEqual(result['planning_taxonomy']['strategies'][0]['unbuilt_count'], 0)
        for row in result['candidates'][1:]:
            self.assertIn('report_inline', row)
            self.assertEqual(row['candidate_file'], context.CANDIDATE)
            self.assertEqual(row['state_intersection_status'], 'unassessed_no_physical_join_admitted')
            self.assertFalse(row['rank_eligible'])
        with self.assertRaises(ValueError): projection.catalog_projection(result, child)


if __name__ == '__main__': unittest.main()
