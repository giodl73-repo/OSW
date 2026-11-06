import base64,copy,io,json,tempfile,unittest,urllib.error,urllib.request
from pathlib import Path
import probe_hycom_native_metadata_v1 as p


def body(spec):
    if spec['kind']=='das':return b'Attributes { NC_GLOBAL { String field_type "instantaneous"; } }'
    if spec['kind']=='axis':return ('Dataset { Float64 '+spec['axis']+'[sample = 1]; } sample;').encode()
    return b'Dataset { Float32 water_u; Float32 water_v; Float32 salinity; } sample;'


class Response(io.BytesIO):
    status=200


class Opener:
    def __init__(self,transform=None,hook=None):self.calls=[];self.transform=transform;self.hook=hook
    def open(self,request,timeout):
        self.calls.append((request.full_url,timeout));spec=next(v for v in p.REQUESTS if v['url']==request.full_url)
        if self.hook:self.hook()
        raw=body(spec)
        if self.transform:raw=self.transform(spec,raw)
        return Response(raw)


class MetadataProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def run_probe(self,opener):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);out=Path(tmp.name);p.probe(out=out,opener=opener);return out,json.loads((out/'probe-report.json').read_bytes())
    def test_closed_metadata_urls_and_only_eight_coordinate_scalars(self):
        self.assertEqual(len(p.REQUESTS),12);self.assertEqual(len({v['url'] for v in p.REQUESTS}),12);self.assertEqual(sum(v['kind']=='axis' for v in p.REQUESTS),8)
        for v in p.REQUESTS:
            self.assertTrue(v['url'].startswith(p.PREFIX));self.assertNotIn('water_u',v['url']);self.assertNotIn('water_v',v['url']);self.assertNotIn('salinity',v['url'])
    def test_dds_das_and_axis_recognition_not_html(self):
        for spec in p.REQUESTS:self.assertTrue(p.recognized(spec,body(spec)));self.assertFalse(p.recognized(spec,b'<html>Provider unavailable</html>'));self.assertFalse(p.recognized(spec,b''))
    def test_complete_bounded_probe_retains_all_twelve_responses(self):
        opener=Opener();out,report=self.run_probe(opener);self.assertEqual(report['status'],'ALL12_METADATA_ENDPOINTS_RESPONDED');self.assertEqual(len(report['requests']),12);self.assertEqual(len(list(out.glob('*.json'))),13)
        for row in report['requests']:
            piece=row['response'];raw=(out/piece['file']).read_bytes();self.assertEqual(p.digest(raw),piece['sha256']);self.assertEqual(len(raw),piece['bytes']);record=json.loads(raw);response=base64.b64decode(record['retained_response_body_base64']);self.assertEqual(record['retained_response_body_sha256'],p.digest(response));self.assertEqual(response,body(row));self.assertFalse(record['wire_hash_claimed'])
        self.assertEqual(report['new_velocity_or_salinity_field_requests'],0);self.assertFalse(report['native_coordinate_pairing_established']);self.assertFalse(report['full_goal_complete'])
    def test_network_operation_timeout_and_no_retries(self):
        opener=Opener();out,report=self.run_probe(opener);self.assertEqual(opener.calls,[(v['url'],15) for v in p.REQUESTS]);self.assertTrue(all(v['attempts']==1 for v in report['requests']))
    def test_timeout_records_each_failure_without_new_field_queries(self):
        def timeout(spec,raw):raise TimeoutError('simulated')
        opener=Opener(timeout);out,report=self.run_probe(opener);self.assertEqual(len(opener.calls),12);self.assertTrue(all(v['error_type']=='TimeoutError' for v in report['requests']));self.assertEqual(report['status'],'SOURCE_METADATA_DIAGNOSIS_COMPLETE_WITH_UNAVAILABLE_ENDPOINTS')
    def test_http_error_body_and_status_retained(self):
        def failure(spec,raw):raise urllib.error.HTTPError(spec['url'],503,'unavailable',{},io.BytesIO(b'Unavailable'))
        out,report=self.run_probe(Opener(failure));self.assertTrue(all(v['http_status']==503 for v in report['requests']));record=json.loads((out/report['requests'][0]['response']['file']).read_bytes());self.assertEqual(base64.b64decode(record['retained_response_body_base64']),b'Unavailable')
    def test_oversize_response_is_explicitly_truncated_not_recognized(self):
        seen=[]
        def transform(spec,raw):seen.append(spec);return b'x'*(p.LIMIT+1) if len(seen)==1 else raw
        out,report=self.run_probe(Opener(transform));record=json.loads((out/report['requests'][0]['response']['file']).read_bytes());self.assertEqual(record['retained_response_body_bytes'],p.LIMIT);self.assertTrue(record['response_body_truncated']);self.assertEqual(report['requests'][0]['status'],'METADATA_UNAVAILABLE_OR_UNRECOGNIZED');self.assertLess(sum(v.stat().st_size for v in out.glob('*.json')),2400000)
    def test_pending_receipt_saved_before_each_network_operation(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);observed=[]
            def hook():observed.append(json.loads((out/'probe-report.json').read_bytes())['requests'][-1]['status'])
            p.probe(out=out,opener=Opener(hook=hook));self.assertEqual(observed,['REQUEST_PENDING']*12)
    def test_redirect_outside_exact_metadata_set_rejected(self):
        handler=p.MetadataRedirects();req=urllib.request.Request(p.REQUESTS[0]['url'])
        for url in ['http://tds.hycom.org/a','https://example.org/metadata',p.PREFIX+'uv3z/2022.ascii?water_u']:
            with self.assertRaises(ValueError):handler.redirect_request(req,None,302,'redirect',{},url)
    def test_even_metadata_redirect_cannot_add_a_second_http_attempt(self):
        with self.assertRaises(ValueError):p.MetadataRedirects().redirect_request(urllib.request.Request(p.REQUESTS[0]['url']),None,302,'redirect',{},p.REQUESTS[1]['url'])
    def test_request_set_and_resource_bounds_cannot_change(self):
        for key,value in [('maximum_response_body_bytes',250000),('network_operation_timeout_seconds',90),('new_velocity_or_salinity_field_requests',1),('requests',[])]:
            op=copy.deepcopy(self.op);op[key]=value
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);(root/p.OPERATOR).parent.mkdir(parents=True);(root/p.OPERATOR).write_text(json.dumps(op));opener=Opener()
                with self.subTest(key=key),self.assertRaises(ValueError):p.probe(root=root,out=root/'out',opener=opener)
                self.assertEqual(opener.calls,[])
    def test_public_input_pins_required_before_any_request(self):
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(p.digest((p.ROOT/file).read_bytes()),pin,file)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/p.OPERATOR).parent.mkdir(parents=True);(root/p.OPERATOR).write_bytes((p.ROOT/p.OPERATOR).read_bytes());file=next(iter(self.op['input_sha256']));(root/file).parent.mkdir(parents=True,exist_ok=True);(root/file).write_bytes(b'changed');opener=Opener()
            with self.assertRaises(ValueError):p.probe(root=root,out=root/'out',opener=opener)
            self.assertEqual(opener.calls,[])


if __name__=='__main__':unittest.main()
