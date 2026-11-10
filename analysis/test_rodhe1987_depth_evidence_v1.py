import io
import unittest
import acquire_rodhe1987_depth_evidence_v1 as m


class Response(io.BytesIO):
    status = 200
    url = m.URL
    headers = {}


class PrimaryEvidence(unittest.TestCase):
    def setUp(self):
        self.op = {'source_url': m.URL, 'maximum_requests': 1, 'timeout_seconds': 25, 'maximum_body_bytes': 2400000}

    def test_exact_single_request(self):
        calls = []
        def opener(request, timeout):
            calls.append((request.full_url, timeout)); return Response(b'%PDF-test')
        ledger = {}; self.assertEqual(m.acquire(self.op, ledger, opener), b'%PDF-test')
        self.assertEqual(calls, [(m.URL, 25)]); self.assertEqual(ledger['status'], 'success')

    def test_failed_request_not_retried(self):
        calls = []
        def opener(*args, **kwargs): calls.append(1); raise TimeoutError('test')
        ledger = {}
        with self.assertRaises(TimeoutError): m.acquire(self.op, ledger, opener)
        self.assertEqual(calls, [1]); self.assertEqual(ledger['status'], 'failed_no_retry')

    def test_reject_non_pdf_and_oversize(self):
        for raw in [b'<html>denied</html>', b'%PDF-' + b'0' * 2400000]:
            ledger = {}
            with self.assertRaises(ValueError): m.acquire(self.op, ledger, lambda *a, **k: Response(raw))
            self.assertEqual(ledger['status'], 'failed_no_retry')

    def test_original_article_identity_and_page_scope(self):
        class Page:
            def get_text(self): return 'The large-scale circulation in the Skagerrak JOHAN RODHE Jutland Current 1975 1977'
        result = m.inspect([Page()] * 9, self.op)
        self.assertEqual(result['depth_values_admitted'], 0)
        with self.assertRaises(ValueError): m.inspect([Page()] * 8, self.op)

    def test_changed_budget_refused(self):
        for key, value in [('maximum_requests', 2), ('timeout_seconds', 26), ('maximum_body_bytes', 3000000), ('source_url', 'https://example.com')]:
            op = dict(self.op); op[key] = value
            with self.assertRaises(ValueError): m.acquire(op, {}, lambda *a, **k: self.fail('Request must not occur'))


if __name__ == '__main__': unittest.main()
