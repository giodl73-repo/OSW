"""Verify selection and scientific meaning of the declared runtime checks."""
import copy
import unittest

import eicc_reference_delivery_cases_v1 as cases
import eicc_reference_query_v1 as context


class EiccRuntimeCases(unittest.TestCase):
    def test_declared_cases_include_route_identity_and_null_semantics(self):
        contract = context.build_contract()
        expected = {**contract['collections'], 'owner': {'id': context.TARGET}, 'decision': {'id': 'decision'},
                    'loop_summaries': [{'id': 'summary'}], 'loop_events': [{'id': 'event'}], 'legacy_depths': []}
        declared = cases.main_cases(expected)
        self.assertEqual(len(declared), 24)
        route_ids = {q['filters'][0]['value'] for q, _ in declared
                     if q['collection'] == context.ROUTES and q['filters'][0]['field'] == 'id'}
        self.assertEqual(route_ids, {r['id'] for r in contract['collections'][context.ROUTES]})
        width_checks = [q for q, _ in declared if q['collection'] == context.SCALES
                        and q['filters'][0]['field'] == 'paired_current_width_km']
        self.assertEqual([q['filters'][0]['value'] for q in width_checks], [None, 0])
        false_cases = [(q, rows) for q, rows in declared if q['collection'] == context.POINTS
                       and q['filters'][0]['field'] == 'is_strict_eicc_path_reference']
        self.assertEqual(len(false_cases), 1)
        self.assertEqual(false_cases[0][1][0]['source_point_label'], 'G')

    def test_route_scene_must_match_selected_route_and_reject_other_geometry(self):
        row = {'id': 'reference:a'}
        query = {'collection': context.ROUTES}
        valid = {'ok': True, 'total': 1, 'rows': [row], 'map_scene': {
            'inspection_collection': context.ROUTES, 'matching_objects': 1, 'mapped_objects': 1,
            'unmapped_objects': 0, 'omitted_features': [], 'features': [
                {'entity_id': row['id'], 'role': 'editorial_reference_route', 'primitive': {'d': 'M 1 2 L 3 4'}}]}}
        cases.verify_response(query, [row], valid)
        for mutation in ['wrong_id', 'extra_feature', 'wrong_role', 'omitted']:
            with self.subTest(mutation=mutation):
                bad = copy.deepcopy(valid)
                if mutation == 'wrong_id': bad['map_scene']['features'][0]['entity_id'] = 'reference:other'
                elif mutation == 'extra_feature': bad['map_scene']['features'].append(copy.deepcopy(bad['map_scene']['features'][0]))
                elif mutation == 'wrong_role': bad['map_scene']['features'][0]['role'] = 'observed_axis'
                else: bad['map_scene']['omitted_features'] = [{'reason': 'invalid geometry'}]
                with self.assertRaises(ValueError): cases.verify_response(query, [row], bad)

    def test_diagnostics_cannot_gain_scenes_or_false_values(self):
        row = {'id': 'scale', 'paired_current_width_km': None}
        valid = {'ok': True, 'total': 1, 'rows': [row], 'map_scene': None, 'chart_scene': None}
        query = {'collection': context.SCALES}
        cases.verify_response(query, [row], valid)
        for mutation in ['map', 'chart', 'zero']:
            bad = copy.deepcopy(valid)
            if mutation == 'map': bad['map_scene'] = {'features': []}
            elif mutation == 'chart': bad['chart_scene'] = {'points': []}
            else: bad['rows'][0]['paired_current_width_km'] = 0
            with self.assertRaises(ValueError): cases.verify_response(query, [row], bad)

    def test_controller_refuses_local_execution_before_reading_files(self):
        import check_eicc_reference_delivery_v1 as controller
        from unittest.mock import patch
        with patch.object(controller, 'read', side_effect=AssertionError('Unexpected source read')):
            with self.assertRaises(RuntimeError): controller.controls({})
        self.assertEqual(controller.response_budget({'collection': context.ROUTES}), 2097152)
        self.assertEqual(controller.response_budget({'collection': context.SCALES}), 131072)


if __name__ == '__main__': unittest.main()
