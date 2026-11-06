import copy,hashlib,io,json,tempfile,unittest,urllib.error
from pathlib import Path
import acquire_ncc_skagseth_table1_v1 as p


class Response(io.BytesIO):
    def __init__(self,body,code=200,content_type='text/plain'):
        super().__init__(body);self.code=code;self.headers={'Content-Type':content_type}


class Transport:
    def __init__(self,result):self.result=result;self.calls=[]
    def open(self,request,timeout):
        self.calls.append((request.full_url,timeout,dict(request.header_items())))
        if isinstance(self.result,Exception):raise self.result
        return self.result


class SourceCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def run_request(self,result,op=None):
        transport=Transport(result)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);report=p.acquire(op or self.op,path,transport);body=(path/'response-body.bin').read_bytes() if (path/'response-body.bin').exists() else None
        return report,body,transport
    def test_success_retains_exact_bytes_without_measurement_promotion(self):
        raw=b'Depth\tMean\n28-44\t34.1\n';r,body,t=self.run_request(Response(raw));self.assertEqual(body,raw);self.assertEqual(r['body_sha256'],hashlib.sha256(raw).hexdigest());self.assertTrue(r['source_table_retained']);self.assertFalse(r['numeric_table_parsing_performed']);self.assertEqual(r['new_current_measurements_admitted'],0);self.assertEqual(len(t.calls),1);self.assertEqual(t.calls[0][:2],(p.URL,25))
    def test_error_and_redirect_body_never_accepted_or_retried(self):
        for code in [302,403,429,500]:
            response=urllib.error.HTTPError(p.URL,code,'error',{},io.BytesIO(b'blocked'))
            r,body,t=self.run_request(response);self.assertEqual(body,b'blocked');self.assertEqual(r['http_status'],code);self.assertFalse(r['source_table_retained']);self.assertEqual(len(t.calls),1);self.assertEqual(r['automatic_retries'],0);self.assertEqual(r['redirects_followed'],0)
        self.assertIsNone(p.NoRedirect().redirect_request(None,None,302,'',{},'https://example.com'))
    def test_transport_failure_does_not_retry_or_claim_body(self):
        r,body,t=self.run_request(urllib.error.URLError('mock timeout'));self.assertEqual(r['status'],'TRANSPORT_FAILURE');self.assertIsNone(body);self.assertIsNone(r['body_sha256']);self.assertEqual(len(t.calls),1)
    def test_body_limit_and_html_utf8_guards(self):
        for body,status in [(b'x'*(p.MAX_BODY_BYTES+1),'RESPONSE_BODY_LIMIT_EXCEEDED'),(b'<!DOCTYPE html><html>challenge','NON_TABLE_OR_EMPTY_RESPONSE'),(b'','NON_TABLE_OR_EMPTY_RESPONSE'),(b'\xff','NON_UTF8_TABLE_RESPONSE')]:
            r,retained,t=self.run_request(Response(body));self.assertEqual(r['status'],status);self.assertFalse(r['source_table_retained']);self.assertEqual(len(t.calls),1)
            if status=='RESPONSE_BODY_LIMIT_EXCEEDED':self.assertIsNone(retained)
    def test_no_url_limit_timeout_retry_or_redirect_widening(self):
        for k,v in [('url','https://example.com'),('maximum_http_attempts',2),('maximum_response_body_bytes',70000),('timeout_seconds',60),('follow_redirects',True),('automatic_retry',True)]:
            op=copy.deepcopy(self.op);op[k]=v
            with tempfile.TemporaryDirectory() as directory,self.subTest(key=k),self.assertRaises(ValueError):p.acquire(op,Path(directory),Transport(Response(b'never')))
    def test_no_depth_or_volume_promotions_and_all_input_pins(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin)
        for key in self.op['eligibility']:
            op=copy.deepcopy(self.op);op['eligibility'][key]=True
            with tempfile.TemporaryDirectory() as directory,self.subTest(key=key),self.assertRaises(ValueError):p.acquire(op,Path(directory),Transport(Response(b'never')))


if __name__=='__main__':unittest.main()
