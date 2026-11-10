import copy,hashlib,io,json,tempfile,unittest,urllib.error
from pathlib import Path
import acquire_nec_huang2022_primary_html_v1 as source


class Response(io.BytesIO):
    def __init__(self,body,status=200):super().__init__(body);self.code=status;self.headers={}


class Transport:
    def __init__(self,values):self.values=iter(values);self.calls=[]
    def open(self,request,timeout):
        assert timeout==25;self.calls.append(request.full_url);value=next(self.values)
        if isinstance(value,Exception):raise value
        return value


class Custody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((source.ROOT/source.OPERATOR).read_bytes())
    def html(self):return ('<html><h1>'+source.TITLE+'</h1><p>979442 70 m 90 m 430 m 400 m 1-year</p></html>').encode()
    def test_exact_two_assets_and_hashes(self):
        figure=b'RIFF0000WEBPsynthetic';transport=Transport([Response(self.html()),Response(figure)])
        with tempfile.TemporaryDirectory() as d:
            report=source.acquire(self.op,Path(d),transport);self.assertEqual((Path(d)/'figure2.webp').read_bytes(),figure)
        self.assertEqual(report['status'],'PRIMARY_HTML_AND_ORIGINAL_FIGURE_RETAINED_PENDING_REVIEW');self.assertEqual(len(transport.calls),2);self.assertEqual(report['requests'][1]['body_sha256'],hashlib.sha256(figure).hexdigest())
    def test_wrong_article_missing_results_or_invalid_figure_rejected(self):
        for values in [[Response(b'<html>wrong</html>')],[Response(self.html().replace(b'430 m',b'430'))],[Response(self.html()),Response(b'wrong figure')]]:
            with tempfile.TemporaryDirectory() as d:report=source.acquire(self.op,Path(d),Transport(values))
            self.assertEqual(report['requests'][-1]['status'],'FAILED_NOT_RETRIED')
    def test_HTTP_and_timeout_failures_never_retried(self):
        for value in [Response(b'blocked',403),TimeoutError('offline'),urllib.error.HTTPError(source.TARGETS[0][1],302,'',{},io.BytesIO(b'redirect'))]:
            t=Transport([value])
            with tempfile.TemporaryDirectory() as d:report=source.acquire(self.op,Path(d),t)
            self.assertEqual(len(t.calls),1);self.assertEqual(report['automatic_retries'],0);self.assertEqual(report['requests'][0]['status'],'FAILED_NOT_RETRIED')
    def test_fixed_caps_and_no_physical_promotion(self):
        for key,value in [('timeout_seconds',60),('maximum_attempts_per_url',2),('follow_redirects',True),('maximum_joint_body_bytes',2400001)]:
            op=copy.deepcopy(self.op);op[key]=value
            with self.assertRaises(ValueError):source.validate_operator(op)
        op=copy.deepcopy(self.op);op['eligibility']['measurement_admission']=True
        with self.assertRaises(ValueError):source.validate_operator(op)
    def test_oversized_body_stops_before_second_request(self):
        t=Transport([Response(b'x'*(source.TARGETS[0][2]+1))])
        with tempfile.TemporaryDirectory() as d:report=source.acquire(self.op,Path(d),t)
        self.assertEqual(len(t.calls),1);self.assertEqual(report['requests'][0]['status'],'FAILED_NOT_RETRIED')
    def test_existing_attempt_cannot_be_replayed(self):
        with tempfile.TemporaryDirectory() as d:
            source.acquire(self.op,Path(d),Transport([TimeoutError('offline')]))
            with self.assertRaises(ValueError):source.acquire(self.op,Path(d),Transport([]))
    def test_input_pins(self):
        for file,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((source.ROOT/file).read_bytes()).hexdigest(),pin)


if __name__=='__main__':unittest.main()
