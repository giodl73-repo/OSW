import base64,copy,hashlib,json,struct,unittest
from unittest.mock import patch
import bounded_hycom_http_ranges_v1 as p
import acquire_neuc_mean_coordinates_v1 as c

URL='https://data.hycom.org/datasets/GLBv0.08/expt_53.X/meanstd/netcdf/test_uv3z.nc'
def multipart(parts,total=100,boundary='abc'):
    return b''.join(b'--'+boundary.encode()+b'\r\nContent-Type: application/octet-stream\r\nContent-Range: bytes '+str(s).encode()+b'-'+str(s+len(raw)-1).encode()+b'/'+str(total).encode()+b'\r\n\r\n'+raw+b'\r\n' for s,raw in parts)+b'--'+boundary.encode()+b'--\r\n'
class Response:
    def __init__(self,body,headers,status=206):self.body=body;self.headers=headers;self.status=status;self.url=URL;self.reads=0
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):self.reads+=1;return self.body[:n]
class BoundedRangeTests(unittest.TestCase):
    def reader(self,allowed=[(0,4),(50,4)],maximum_requests=2,maximum_requested_bytes=16,maximum_response_body_bytes=2000,maximum_total_response_body_bytes=4000):return p.BoundedHttpRanges(URL,100,'fixed',allowed,maximum_requests,maximum_requested_bytes,maximum_response_body_bytes,maximum_total_response_body_bytes)
    def test_binary_parts_exact_even_when_payload_contains_boundary_bytes(self):
        parts=[(0,b'\xff\0\r\n--abc'),(50,b'\r\nxx')];body=multipart(parts);r=p.parse_multipart(body,'multipart/byteranges; boundary=abc',[(s,len(x)) for s,x in parts],100);self.assertEqual(r,{(s,len(x)):x for s,x in parts})
    def test_part_order_and_quoted_boundary_supported_without_reorientation(self):
        body=multipart([(50,b'last'),(0,b'head')]);self.assertEqual(p.parse_multipart(body,'multipart/byteranges; boundary="abc"',[(0,4),(50,4)],100),{(0,4):b'head',(50,4):b'last'})
    def test_extra_missing_duplicate_coalesced_and_changed_total_rejected(self):
        for parts,total in [([(0,b'head')],100),([(0,b'head'),(50,b'last'),(80,b'extra')],100),([(0,b'head'),(0,b'head')],100),([(0,b'head'),(50,b'last')],101),([(0,b'x'*54)],100)]:
            with self.assertRaises(ValueError):p.parse_multipart(multipart(parts,total),'multipart/byteranges; boundary=abc',[(0,4),(50,4)],100)
    def test_truncated_payload_bad_part_length_and_bad_delimiters_rejected(self):
        body=multipart([(0,b'head'),(50,b'last')])
        for changed in [body[:-8],body.replace(b'bytes 0-3',b'bytes 0-4'),body.replace(b'--abc',b'--wrong',1),body+b'extra']:
            with self.assertRaises(ValueError):p.parse_multipart(changed,'multipart/byteranges; boundary=abc',[(0,4),(50,4)],100)
    def test_range_plan_rejects_overlap_duplicates_unbounded_or_negative(self):
        for plan in [[],[(0,0)],[(-1,4)],[(0,4),(3,2)],[(0,4),(0,4)],[(i*4,2) for i in range(129)]]:
            with self.assertRaises(ValueError):p.validate_plan(plan)
    def test_successful_multipart_single_shared_ledger_and_no_success_replay(self):
        r=self.reader();body=multipart([(0,b'head'),(50,b'last')]);resp=Response(body,{'Last-Modified':'fixed','Content-Length':str(len(body)),'Content-Type':'multipart/byteranges; boundary=abc'})
        with patch('urllib.request.urlopen',return_value=resp):self.assertEqual(r.read([(0,4),(50,4)])[(0,4)],b'head')
        self.assertEqual(r.receipt()['completed_ranges'],2);self.assertEqual(r.receipt()['attempted_requested_bytes'],8)
        with patch('urllib.request.urlopen',side_effect=AssertionError('Replay forbidden')),self.assertRaises(ValueError):r.read([(0,4)])
    def test_fullbody_changed_identity_encoding_and_merged_range_rejected_before_body(self):
        for status,headers in [(200,{}),(206,{'Last-Modified':'changed'}),(206,{'Last-Modified':'fixed','Content-Encoding':'gzip'}),(206,{'Last-Modified':'fixed','Content-Length':'99','Content-Type':'application/octet-stream'})]:
            r=self.reader();resp=Response(b'never',headers,status)
            with patch('urllib.request.urlopen',return_value=resp),self.assertRaises(ValueError):r.read([(0,4),(50,4)])
            self.assertEqual(resp.reads,0);self.assertEqual(r.receipt()['requests'][0]['status'],'failed_no_replay')
    def test_unplanned_requests_and_future_first_attempt_budget_fail_before_network(self):
        for r,plan in [(self.reader(),[(4,4)]),(self.reader(maximum_requests=1),[(0,4)]),(self.reader(maximum_total_response_body_bytes=2000),[(0,4)])]:
            with patch('urllib.request.urlopen',side_effect=AssertionError('No request allowed')),self.assertRaises(ValueError):r.read(plan)
        with self.assertRaises(ValueError):self.reader(maximum_requested_bytes=4)
    def test_exact_single_range_then_other_ranges_share_counters(self):
        r=self.reader();resp=Response(b'head',{'Last-Modified':'fixed','Content-Length':'4','Content-Range':'bytes 0-3/100'})
        with patch('urllib.request.urlopen',return_value=resp):self.assertEqual(r.read([(0,4)])[(0,4)],b'head')
        self.assertEqual(len(r.rows),1);self.assertEqual(r.body_bytes,4);self.assertEqual(r.requested_bytes,4)
    def test_verified_header_layout_ends_before_velocity_and_rejects_gap_or_overlap(self):
        h=json.loads((c.ROOT/'research/source-data/pacific-neuc-mean-header-inspection-v1/header-inspection.json').read_bytes());start,n,parts=c.coordinate_layout(h);self.assertEqual((start,n),(2064,62336));self.assertEqual(start+n,64400)
        for delta in [-8,8]:
            bad=copy.deepcopy(h);next(v for v in bad['variables'] if v['name']=='lon')['begin']+=delta
            with self.assertRaises(ValueError):c.coordinate_layout(bad)
    def test_coordinate_decoder_preserves_values_and_rejects_missing_or_nonmonotonic(self):
        dims=[{'name':k,'declared_length':2} for k in ['depth','lat','lon']]+[{'name':'time','declared_length':0}];parts=[(0,16,'depth'),(16,16,'lat'),(32,16,'lon'),(48,8,'time')];raw=struct.pack('>7d',0,10,-1,1,130,140,42);r=c.decode_coordinates(raw,0,parts,dims,1);self.assertEqual(r['time'],[42]);self.assertEqual(r['lat'],[-1,1])
        for bad in [raw[:-1],struct.pack('>7d',0,10,1,-1,130,140,42),struct.pack('>7d',0,10,float('nan'),1,130,140,42)]:
            with self.assertRaises(ValueError):c.decode_coordinates(bad,0,parts,dims,1)
    def test_pins_and_metadata_only_contract(self):
        op=json.loads((c.ROOT/c.OPERATOR).read_bytes());self.assertEqual(op['expected_coordinate_block'],[2064,62336]);self.assertEqual(op['maximum_ocean_velocity_values'],0)
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((c.ROOT/f).read_bytes()).hexdigest(),pin,f)

if __name__=='__main__':unittest.main()
