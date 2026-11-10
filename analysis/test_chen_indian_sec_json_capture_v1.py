"""Reproduce precision loss caused by re-encoding native JSON through JS Number."""
import json
import subprocess
import unittest

class JsonCapture(unittest.TestCase):
    def test_js_roundtrip_is_not_a_lossless_native_response_capture(self):
        raw='{"safe":1000.0,"large_float":1.8446744073709552e19,"large_integer":9007199254740993}'
        output=subprocess.check_output(['node','-e','process.stdout.write(JSON.stringify(JSON.parse(process.argv[1])))',raw])
        original,recoded=json.loads(raw),json.loads(output)
        self.assertEqual(original['safe'],recoded['safe'])
        self.assertNotEqual(original['large_float'],recoded['large_float'])
        self.assertNotEqual(original['large_integer'],recoded['large_integer'])
        # Carrying the original JSON as a string preserves its full numeric tokens.
        envelope=subprocess.check_output(['node','-e','process.stdout.write(JSON.stringify({raw_response_json:process.argv[1]}))',raw])
        retained=json.loads(envelope)['raw_response_json']
        self.assertEqual(retained,raw);self.assertEqual(json.loads(retained),original)

if __name__=='__main__':unittest.main()
