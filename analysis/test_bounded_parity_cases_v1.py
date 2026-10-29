import unittest
from bounded_parity_cases_v1 import encoded,partition,expected_descriptor

class BoundedParityTests(unittest.TestCase):
    def test_utf8_escaping_order_and_repeated_cases_are_retained(self):
        header={'payload_sha256':'a'*64,'metadata_json':'{"ok":true}'}
        cases=[{'kind':'snapshot','raw_response_json':'{"name":"été\\n海"}'} for _ in range(5)]
        cases.insert(2,{'kind':'object','raw_response_json':'{"id":"different"}'})
        bound=len(encoded({**header,'cases':cases[:2]}))
        result=partition(header,cases,maximum_bytes=bound)
        self.assertGreater(len(result),1)
        self.assertEqual([row for group in result for row in group['cases']],cases)
        self.assertTrue(all(len(encoded(group))<=bound for group in result))
        self.assertTrue(all(group['metadata_json']==header['metadata_json'] for group in result))

    def test_exact_single_case_bound_and_overflow(self):
        header={'metadata_json':'{"ok":true}'};cases=[{'raw_response_json':'x'*40}]
        bound=len(encoded({**header,'cases':cases}))
        self.assertEqual(partition(header,cases,maximum_bytes=bound),[{**header,'cases':cases}])
        with self.assertRaisesRegex(ValueError,'One complete response'):partition(header,cases,maximum_bytes=bound-1)

    def test_invalid_headers_and_empty_inventory_refused(self):
        for header,cases,bound in [({'cases':[]},[{}],100),({},[],100),({},[{}],0)]:
            with self.assertRaises(ValueError):partition(header,cases,maximum_bytes=bound)

    def test_large_expected_metadata_and_responses_stay_outside_request_fixture(self):
        metadata,body=expected_descriptor('compare-main-metadata.expected.json','é'*5000)
        response,other=expected_descriptor('compare-main-1.expected.json','海'*3000)
        self.assertEqual(metadata['bytes'],10000);self.assertEqual(response['bytes'],9000)
        self.assertEqual(body.decode(),'é'*5000);self.assertEqual(other.decode(),'海'*3000)
        groups=partition({'expected_metadata':metadata},[{'kind':'snapshot','name':'atlas','expected_response':response}],maximum_bytes=1024)
        self.assertLess(len(encoded(groups[0])),1024)
        with self.assertRaises(ValueError):expected_descriptor('../compare-main-1.expected.json','{}')

if __name__=='__main__':unittest.main()
