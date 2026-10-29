import copy
import unittest
import equatorial_basin_identity_cases_v2 as m


def response(request, expected):
    order = request.get('sort', {'field': 'id', 'direction': 'asc'})
    rows = sorted(expected, key=lambda r: r[order['field']], reverse=order['direction'] == 'desc')
    start = request.get('offset', 0)
    scene = None
    if request['collection'] in {'objects', 'reference_routes'}:
        scene = {'features': [], 'matching_objects': len(expected), 'mapped_objects': 0,
                 'unmapped_objects': len(expected), 'omitted_features': []}
    return {'ok': True, 'total': len(expected), 'rows': rows[start:start + request['limit']], 'map_scene': scene,
            'chart_scene': m.runtime.membership_scene(rows) if request['collection'] == 'current_basin_memberships' else None,
            'taxonomy_scope':m.query.TAXONOMY_SCOPE if request.get('taxonomy') else None}


class QueryCases(unittest.TestCase):
    def cases(self):
        #Only new contract rows; no installed packet is read.
        rows = copy.deepcopy(m.runtime.contract()['additions'])
        for family in m.runtime.contract()['prior_family_records'].values():rows['objects'].extend(copy.deepcopy(family['objects']))
        rows.update(widths=[], reference_routes=[])
        return m.main_cases(rows)

    def test_inventory_migration_is_exact_and_does_not_change_other_cases(self):
        target = {'collection': 'objects', 'record_type': 'named_current', 'limit': 1}
        width = {'collection': 'widths', 'limit': 1}
        cases = [(target, 106), (width, 178)]
        before = copy.deepcopy(cases)
        self.assertEqual(m.adapt_legacy_cases(cases), [(target, 111), (width, 178)])
        self.assertEqual(cases, before)
        for bad in [[], [(target, 105)], [(target, True)], [(target, 106), (target, 106)]]:
            with self.assertRaises(ValueError):
                m.adapt_legacy_cases(bad)

    def test_66_cases_cover_each_new_identity_and_empty_measurement_collections(self):
        cases = self.cases()
        self.assertEqual(len(cases), 66)
        for request, expected in cases:
            m.verify(request, expected, response(request, expected))
        for name in ['entities', 'objects', 'names', 'length_assessments', 'current_identity_admissions', 'route_decisions']:
            selected = [(q, rows) for q, rows in cases if q['collection'] == name and not q.get('taxonomy')]
            self.assertEqual(len(selected), 5)
            self.assertTrue(all(len(rows) == 1 for _, rows in selected))
        for name in ['widths', 'reference_routes']:
            self.assertTrue(all(rows == [] for q, rows in cases if q['collection'] == name))

    def test_paginated_membership_scene_retains_all_matches_in_sorted_order(self):
        request, expected = next((q, rows) for q, rows in self.cases() if q.get('offset') == 2)
        actual = response(request, expected)
        self.assertEqual(len(actual['rows']), 1)
        self.assertEqual(len(actual['chart_scene']['members']), 5)
        actual['chart_scene']['members'] = actual['chart_scene']['members'][2:3]
        with self.assertRaises(ValueError):
            m.verify(request, expected, actual)

    def test_wrong_filter_rows_total_or_order_refused(self):
        request, expected = self.cases()[0]
        for mutation in ['total', 'rows', 'order']:
            actual = response(request, expected)
            if mutation == 'total':
                actual['total'] += 1
            elif mutation == 'rows':
                actual['rows'][0] = {'id': 'wrong'}
            else:
                actual['rows'].reverse()
            with self.assertRaises(ValueError):
                m.verify(request, expected, actual)

    def test_general_family_queries_include_all_members_and_keep_editorial_scope(self):
        cases=[(q,rows) for q,rows in self.cases() if q.get('taxonomy')]
        self.assertEqual(len(cases),8)
        for q,rows in cases:
            actual=response(q,rows);m.verify(q,rows,actual)
            self.assertTrue(rows)
            actual['taxonomy_scope']=None
            with self.assertRaises(ValueError):m.verify(q,rows,actual)
        children=[(q,rows) for q,rows in cases if q['taxonomy']['relation']=='children']
        self.assertEqual(sorted(len(rows) for _,rows in children),[2,3])

    def test_seven_canonical_link_queries_preserve_relation_scope(self):
        cases=[(q,rows) for q,rows in self.cases() if q['collection']=='taxonomy_links']
        self.assertEqual(len(cases),7)
        for q,rows in cases:
            self.assertTrue(all(r['physical_connectivity_eligible'] is False and r['measurement_inheritance_eligible'] is False for r in rows))
            actual=response(q,rows);actual['rows'][0]=dict(actual['rows'][0],physical_connectivity_eligible=True)
            with self.assertRaises(ValueError):m.verify(q,rows,actual)

    def test_identity_and_empty_route_maps_reject_fabricated_geometry(self):
        for name in ['current_basin_memberships', 'objects', 'widths', 'reference_routes']:
            request, expected = next((q, rows) for q, rows in self.cases() if q['collection'] == name)
            actual = response(request, expected)
            actual['map_scene'] = {'features': [{'geometry': {'type': 'Point', 'coordinates': [0, 0]}}]}
            with self.assertRaises(ValueError, msg=name):
                m.verify(request, expected, actual)


if __name__ == '__main__':
    unittest.main()
