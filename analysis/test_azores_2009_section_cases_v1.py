"""Exercise independent expected scene semantics using two tiny source rows."""
import copy
import json
import unittest
from unittest.mock import patch
import azores_2009_section_cases_v1 as cases
import azores_2009_section_projection_v1 as p


class SectionCases(unittest.TestCase):
    def test_six_cases_keep_full_comparison_across_sort_and_pagination(self):
        rows = json.loads((p.ROOT / p.BINDINGS).read_bytes())['records']
        doc = json.loads((p.ROOT / p.REVIEW).read_bytes())
        with patch.object(cases.legacy, 'main_cases', return_value=[({}, [])] * 20):
            actual = cases.main_cases({'widths': rows})
        self.assertEqual(len(actual), 26)
        for query, expected in actual[20:]:
            filtered = sorted(expected['section_rows'], key=lambda r: r['id'],
                              reverse=query['sort']['direction'] == 'desc')
            offset = query.get('offset', 0)
            scene = {'kind': 'azores_2009_section_review', 'records': rows,
                     'matching_ids': sorted(r['id'] for r in filtered),
                     'section_context': doc['shared_section_context'],
                     'enrichments': doc['existing_measurement_enrichments'],
                     'figure_file': p.FIGURE, 'figure_sha256': p.sha((p.ROOT / p.FIGURE).read_bytes())}
            response = {'ok': True, 'total': len(filtered), 'rows': filtered[offset:offset+query['limit']],
                        'chart_scene': scene}
            cases.verify_response(query, expected, response)
            bad = copy.deepcopy(response)
            bad['chart_scene']['section_context']['date_discrepancy']['resolved'] = True
            with self.assertRaises(ValueError):
                cases.verify_response(query, expected, bad)
        self.assertEqual(len(cases.index_cases()), 12)


if __name__ == '__main__':
    unittest.main()
