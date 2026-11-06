import copy
import json
import unittest
from unittest.mock import patch
import chen_indian_sec_native_batch_v2 as batch


class NativeBatch(unittest.TestCase):
    def test_exact_numeric_tokens_and_complete_inventory(self):
        requests = [batch.encode_case({'kind':'query','request':{'value':9007199254740993}}),
                    {'kind':'snapshot','name':'atlas'}]
        raw = '{"ok":true,"integer":9007199254740993,"float":1.8446744073709552e19}'
        response = {'schema':'osw.delivery-native-probe.v2',
                    'metadata_json':'{"ok":true}',
                    'cases':[{**item,'raw_response_json':raw} for item in requests]}
        transported = json.loads(json.dumps(response))
        result = batch.decode_batch(requests, transported)
        self.assertEqual(len(result),2)
        self.assertEqual(json.loads(requests[0]['request_json'])['value'],9007199254740993)
        self.assertTrue(all(value == raw for value in result.values()))
        for change in ('drop','reorder','identity','error'):
            broken=copy.deepcopy(response)
            if change=='drop':broken['cases'].pop()
            elif change=='reorder':broken['cases'].reverse()
            elif change=='identity':broken['cases'][0]['request_json']='{}'
            else:broken['cases'][0]['raw_response_json']='{"ok":false}'
            with self.assertRaises(ValueError):batch.decode_batch(requests,broken)

    def test_local_native_execution_refused_before_access(self):
        with patch.dict('os.environ',{},clear=True), patch.object(batch.subprocess,'run') as run:
            with self.assertRaisesRegex(ValueError,'Scoped cloud batch only'):
                batch.run_batch('nonexistent-probe','main','nonexistent-payload',[])
            run.assert_not_called()


if __name__=='__main__':unittest.main()
