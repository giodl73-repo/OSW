import copy,hashlib,io,json,tempfile,unittest,urllib.error
from pathlib import Path
import acquire_egcc_sutherland_primary_paper_v1 as p


class Response(io.BytesIO):
    def __init__(self,raw,code=200):super().__init__(raw);self.code=code;self.headers={'Content-Type':'application/pdf'}


class Transport:
    def __init__(self,value):self.value=value;self.calls=0
    def open(self,request,timeout):
        self.calls+=1;assert request.full_url==p.URL and timeout==25
        if isinstance(self.value,Exception):raise self.value
        return self.value


class PaperCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def test_exact_success_bytes_pending_review_not_measurement(self):
        raw=b'%PDF-1.7\nsynthetic';t=Transport(Response(raw))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);r=p.acquire(self.op,path,t);self.assertEqual((path/'journal-article.pdf').read_bytes(),raw)
        self.assertEqual(t.calls,1);self.assertEqual(r['body_sha256'],hashlib.sha256(raw).hexdigest());self.assertTrue(r['primary_PDF_retained']);self.assertEqual(r['new_measurements_admitted'],0)
    def test_http_redirect_html_and_transport_failure_never_success_or_retried(self):
        for value in [Response(b'<html>blocked'),urllib.error.HTTPError(p.URL,302,'',{},io.BytesIO(b'redirect')),urllib.error.HTTPError(p.URL,403,'',{},io.BytesIO(b'blocked')),urllib.error.URLError('offline')]:
            t=Transport(value)
            with tempfile.TemporaryDirectory() as directory:r=p.acquire(self.op,Path(directory),t)
            self.assertFalse(r['primary_PDF_retained']);self.assertEqual(t.calls,1);self.assertEqual(r['automatic_retries'],0)
    def test_oversized_body_not_retained_as_source(self):
        t=Transport(Response(b'%PDF-'+b'x'*p.MAX_BODY_BYTES))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);r=p.acquire(self.op,path,t);self.assertFalse((path/'journal-article.pdf').exists());self.assertEqual(r['status'],'RESPONSE_BODY_LIMIT_EXCEEDED')
    def test_input_pins_and_no_bounds_or_eligibility_widening(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin)
        for key,value in [('url','https://example.com'),('maximum_http_attempts',2),('maximum_response_body_bytes',8000000),('timeout_seconds',60),('follow_redirects',True),('automatic_retry',True)]:
            op=copy.deepcopy(self.op);op[key]=value
            with tempfile.TemporaryDirectory() as directory,self.subTest(key=key),self.assertRaises(ValueError):p.acquire(op,Path(directory),Transport(Response(b'never')))
        op=copy.deepcopy(self.op);op['eligibility']['measurement_admission']=True
        with tempfile.TemporaryDirectory() as directory,self.assertRaises(ValueError):p.acquire(op,Path(directory),Transport(Response(b'never')))


if __name__=='__main__':unittest.main()
