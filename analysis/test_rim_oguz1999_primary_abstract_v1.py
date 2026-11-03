import copy,hashlib,io,json,tempfile,unittest,urllib.error
from pathlib import Path
import acquire_rim_oguz1999_primary_abstract_v1 as source


class Response(io.BytesIO):
    def __init__(self,raw,code=200):super().__init__(raw);self.code=code


class Transport:
    def __init__(self,value):self.value=value;self.calls=0
    def open(self,request,timeout):
        assert request.full_url==source.URL and timeout==25;self.calls+=1
        if isinstance(self.value,Exception):raise self.value
        return self.value


class Custody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((source.ROOT/source.OPERATOR).read_bytes())
    def body(self):return b'<html>Observations on the Rim Current structure April 1993 between 100 and 200 m observed to 350 dbar</html>'
    def test_exact_primary_bytes_and_no_article_claim(self):
        raw=self.body();t=Transport(Response(raw))
        with tempfile.TemporaryDirectory() as d:
            report=source.acquire(self.op,Path(d),t);self.assertEqual((Path(d)/'institutional-record.html').read_bytes(),raw)
        self.assertEqual(report['body_sha256'],hashlib.sha256(raw).hexdigest());self.assertFalse(report['full_article_obtained']);self.assertEqual(t.calls,1)
    def test_wrong_units_or_missing_abstract_rejected(self):
        for raw in [self.body().replace(b'350 dbar',b'350 m'),b'<html>wrong article</html>']:
            with self.assertRaises(ValueError):source.validate_body(raw)
    def test_http_timeout_and_overflow_not_retried(self):
        for value in [Response(b'blocked',403),TimeoutError('offline'),Response(b'x'*(source.MAX_BYTES+1))]:
            t=Transport(value)
            with tempfile.TemporaryDirectory() as d:report=source.acquire(self.op,Path(d),t)
            self.assertEqual(t.calls,1);self.assertEqual(report['status'],'FAILED_NOT_RETRIED')
    def test_bounds_source_identity_and_eligibility_frozen(self):
        for key,value in [('url','https://example.com'),('maximum_response_body_bytes',700000),('maximum_attempts',2),('follow_redirects',True),('timeout_seconds',60)]:
            op=copy.deepcopy(self.op);op[key]=value
            with tempfile.TemporaryDirectory() as d,self.assertRaises(ValueError):source.acquire(op,Path(d),Transport(Response(self.body())))
    def test_source_pins_and_success_cannot_be_replayed(self):
        for file,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((source.ROOT/file).read_bytes()).hexdigest(),pin)
        with tempfile.TemporaryDirectory() as d:
            source.acquire(self.op,Path(d),Transport(Response(self.body())))
            with self.assertRaises(ValueError):source.acquire(self.op,Path(d),Transport(Response(self.body())))


if __name__=='__main__':unittest.main()
