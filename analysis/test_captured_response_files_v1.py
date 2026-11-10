import hashlib
import tempfile
import unittest
from pathlib import Path
from captured_response_files_v1 import read_captured_json


class CaptureTests(unittest.TestCase):
    def test_original_bytes_preserved_and_changed_or_unconfined_capture_refused(self):
        with tempfile.TemporaryDirectory(prefix='osw-captured-json-') as directory:
            raw = ' {"ok":true,"integer":9007199254740993,"name":"é → Ω","v":1.2300}\n'
            body = raw.encode('utf-8')
            name = 'capture-main-1.response.json'
            target = Path(directory) / name
            target.write_bytes(body)
            descriptor = {'file': name, 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
            self.assertEqual(read_captured_json(directory, descriptor, 1024), raw)
            for changed in [dict(descriptor, file='../'+name), dict(descriptor, bytes=True),
                            dict(descriptor, bytes=len(body)+1), dict(descriptor, sha256='0'*64),
                            dict(descriptor, extra=True)]:
                with self.assertRaises(ValueError):
                    read_captured_json(directory, changed, 1024)
            with self.assertRaises(ValueError):
                read_captured_json(directory, descriptor, len(body)-1)
            target.write_bytes(body.replace(b'1.2300', b'1.2400'))
            with self.assertRaises(ValueError):
                read_captured_json(directory, descriptor, 1024)


if __name__ == '__main__':
    unittest.main()
