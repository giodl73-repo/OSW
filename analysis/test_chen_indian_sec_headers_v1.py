import io
import json
from pathlib import Path
import tempfile
import unittest

import inspect_chen_indian_sec_headers_v1 as subject


class Response(io.BytesIO):
    status = 200
    def __init__(self, body, declared=None, url=subject.URL):
        super().__init__(body)
        self.headers = {} if declared is None else {'Content-Length': str(declared)}
        self.url = url
        self.reads = 0
    def geturl(self):
        return self.url
    def read(self, size=-1):
        self.reads += 1
        return super().read(size)


class SourceGuards(unittest.TestCase):
    def attempt(self, response):
        with tempfile.TemporaryDirectory() as directory:
            return subject.acquire(response, Path(directory) / 'sample.mat')

    def test_declared_oversize_refused_before_read(self):
        response = Response(b'', subject.MAX_BYTES + 1)
        with self.assertRaisesRegex(ValueError, 'budget'):
            self.attempt(response)
        self.assertEqual(response.reads, 0)

    def test_unannounced_oversize_refused(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            self.attempt(Response(b'x' * (subject.MAX_BYTES + 1)))

    def test_redirect_refused_before_read(self):
        response = Response(b'', url='https://example.org/login')
        with self.assertRaisesRegex(ValueError, 'response'):
            self.attempt(response)
        self.assertEqual(response.reads, 0)

    def test_html_or_truncated_content_is_not_a_mat_file(self):
        with self.assertRaisesRegex(ValueError, 'supported'):
            self.attempt(Response(b'<html>login</html>'))
        with self.assertRaisesRegex(ValueError, 'declaration'):
            self.attempt(Response(b'x' * 128, 200))

    def test_exact_small_mat5_custody(self):
        body = b'MATLAB 5.0 MAT-file'.ljust(124, b' ') + b'\x00\x01IM'
        self.assertEqual(len(body), 128)
        result = self.attempt(Response(body, 128))
        self.assertEqual(result['sha256'], subject.digest(body))
        self.assertEqual(result['bytes'], 128)

    def test_freeze_and_permission_tampering_refused(self):
        script = Path(subject.__file__).read_bytes()
        metadata = Path(subject.METADATA).read_bytes()
        request = json.loads(Path(subject.REQUEST).read_bytes())
        request['execute'] = True
        subject.validate_request(request, script, metadata)
        for key, value in [('execute',False), ('script_sha256','bad'), ('metadata_sha256','bad'),
                           ('max_download_bytes',subject.MAX_BYTES*2), ('url','https://example.org'),
                           ('field_value_processing_permitted',True)]:
            altered = dict(request, **{key:value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.validate_request(altered, script, metadata)


if __name__ == '__main__':
    unittest.main()
