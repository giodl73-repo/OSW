import copy
import hashlib
import unittest
import pacific_nec_nominal_width_source_cases_v1 as m


class OriginalSources(unittest.TestCase):
    def response(self, request, expected):
        pairs = enumerate(expected) if isinstance(expected, list) else expected.items()
        return {'ok': True, 'total': len(expected), **request,
                'source_sha256': hashlib.sha256((m.query.ROOT/request['document']).read_bytes()).hexdigest(),
                'rows': [{'source_key': str(key), 'source_pointer': request['pointer']+'/'+str(key).replace('~', '~0').replace('/', '~1'),
                          'record': copy.deepcopy(value)} for key, value in pairs]}

    def test_all_three_complete_documents_and_three_key_pointers(self):
        cases = m.cases()
        self.assertEqual(len(cases), 6)
        for request, expected in cases:
            m.verify(request, expected, self.response(request, expected))

    def test_fabricated_annual_range_is_rejected_even_with_correct_document_hash(self):
        request, expected = next((r, e) for r, e in m.cases() if r['pointer'] == '/nominal_surface_width')
        response = self.response(request, expected)
        row = next(row for row in response['rows'] if row['source_key'] == 'annual_width_range_km')
        self.assertIsNone(row['record'])
        row['record'] = [900, 1100]
        with self.assertRaises(ValueError):
            m.verify(request, expected, response)

    def test_missing_duplicate_and_wrong_source_are_rejected(self):
        request, expected = m.cases()[0]
        for change in ['missing', 'duplicate', 'hash', 'total', 'document', 'pointer', 'row_pointer']:
            response = self.response(request, expected)
            if change == 'missing': response['rows'].pop()
            elif change == 'duplicate': response['rows'][-1] = copy.deepcopy(response['rows'][0])
            elif change == 'hash': response['source_sha256'] = '0'*64
            elif change == 'document': response['document'] = 'other.json'
            elif change == 'pointer': response['pointer'] = '/other'
            elif change == 'row_pointer': response['rows'][0]['source_pointer'] = '/other'
            else: response['total'] += 1
            with self.assertRaises(ValueError, msg=change):
                m.verify(request, expected, response)

    def test_related_publications_cannot_be_collapsed_or_reordered(self):
        request, expected = next((r, e) for r, e in m.cases() if r['pointer'] == '/new_sources')
        response = self.response(request, expected)
        self.assertEqual(len(response['rows']), 2)
        response['rows'].reverse()
        with self.assertRaises(ValueError):
            m.verify(request, expected, response)


if __name__ == '__main__': unittest.main()
