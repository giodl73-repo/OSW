import base64,hashlib,json,struct,unittest
from pathlib import Path
from unittest.mock import patch
import inspect_hycom_mean_header_v1 as p


def uint(n):return struct.pack('>I',n)
def name(s):
    raw=s.encode();return uint(len(raw))+raw+b'\0'*((-len(raw))%4)
def attr(s,kind,values):
    raw=values if kind==2 else struct.pack('>'+str(len(values))+p.TYPES[kind][0],*values)
    return name(s)+uint(kind)+uint(len(values))+raw+b'\0'*((-len(raw))%4)
def fixture(version=2,begin=4096):
    dims=uint(10)+uint(2)+name('time')+uint(0)+name('depth')+uint(2)
    ga=uint(12)+uint(1)+attr('history',2,b'precomputed temporal mean')
    va=uint(12)+uint(2)+attr('units',2,b'm/s')+attr('_FillValue',3,[-30000])
    variable=name('water_u')+uint(2)+uint(0)+uint(1)+va+uint(3)+uint(4)+(uint(begin) if version==1 else struct.pack('>Q',begin))
    return b'CDF'+bytes([version])+uint(1)+dims+ga+uint(11)+uint(1)+variable


class HeaderInspectionTests(unittest.TestCase):
    def parse(self,raw,**kwargs):
        self.requests=[]
        def fetch(start,n):
            self.assertEqual(start,sum(k for _,k in self.requests));self.assertLessEqual(start+n,len(raw));self.requests.append((start,n));return raw[start:start+n]
        return p.inspect(fetch,**kwargs)
    def test_cdf1_and_cdf2_parse_records_types_dimensions_and_attributes(self):
        for version in [1,2]:
            r=self.parse(fixture(version));self.assertEqual(r['format'],'CDF'+str(version));self.assertEqual(r['record_count'],1);v=r['variables'][0];self.assertEqual(v['dimension_names'],['time','depth']);self.assertTrue(v['is_record_variable']);self.assertEqual(v['nc_type'],3);self.assertEqual(v['attributes']['_FillValue']['values'],[-30000]);self.assertEqual(v['attributes']['units']['values'],'m/s')
    def test_exact_header_bytes_hash_and_no_data_prefetch(self):
        raw=fixture();r=self.parse(raw);self.assertEqual(r['header_bytes'],len(raw));self.assertEqual(base64.b64decode(r['header_base64']),raw);self.assertEqual(r['header_sha256'],hashlib.sha256(raw).hexdigest());self.assertFalse(r['variable_data_read']);self.assertFalse(r['axis_values_read']);self.assertFalse(r['ocean_velocity_values_read'])
    def test_empty_header_stops_at32bytes(self):
        r=self.parse(b'CDF\x01'+b'\0'*28);self.assertEqual(r['header_bytes'],32);self.assertEqual(r['variables'],[])
    def test_large_cdf2_begin_not_truncated_to32bit(self):
        begin=2**32+4096;r=self.parse(fixture(begin=begin));self.assertEqual(r['variables'][0]['begin'],begin)
    def test_unknown_magic_invalid_tags_and_excessive_counts_rejected(self):
        for raw in [b'\x89HDF',b'CDF\x05',b'CDF\x02'+uint(1)+uint(11)+uint(2),b'CDF\x02'+uint(1)+uint(10)+uint(33)]:
            with self.subTest(raw=raw[:12]),self.assertRaises(ValueError):self.parse(raw)
    def test_truncation_padding_and_header_byte_budget_rejected(self):
        with self.assertRaises(AssertionError):self.parse(fixture()[:-1])
        with self.assertRaises(ValueError):self.parse(fixture(),maximum_bytes=20)
        raw=fixture().replace(name('water_u'),name('water_u')[:-1]+b'x')
        with self.assertRaises(ValueError):self.parse(raw)
    def test_invalid_dimension_record_placement_and_data_overlap_rejected(self):
        raw=fixture();needle=name('water_u')+uint(2)+uint(0)+uint(1)
        for changed in [raw.replace(needle,name('water_u')+uint(2)+uint(0)+uint(9)),raw.replace(needle,name('water_u')+uint(2)+uint(1)+uint(0)),fixture(begin=4)]:
            with self.assertRaises(ValueError):self.parse(changed)
    def test_http_budget_rejects_replay_or_overrun_before_network(self):
        s=object.__new__(p.HttpHeaderRanges);s.end=8;s.length=100;s.total=8;s.maximum_bytes=10;s.maximum_requests=1;s.rows=[]
        with patch('urllib.request.urlopen',side_effect=AssertionError('No request allowed')):
            for start,n in [(0,4),(8,4),(8,0)]:
                with self.assertRaises(ValueError):s.read(start,n)
    def test_http_refuses_full_body_or_mismatched_ranges_without_reading(self):
        class Response:
            status=200;url='https://data.hycom.org/test';headers={}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,*args):raise AssertionError('Do not read full or mismatched body')
        s=object.__new__(p.HttpHeaderRanges);s.url=Response.url;s.modified='old';s.end=0;s.length=100;s.total=0;s.maximum_bytes=20;s.maximum_requests=3;s.rows=[]
        for status in [200,206]:
            Response.status=status
            with patch('urllib.request.urlopen',return_value=Response()),self.assertRaises(ValueError):s.read(0,4)
    def test_operator_pins_and_no_region_or_averaging_claim(self):
        op=json.loads((p.ROOT/p.OPERATOR).read_bytes());self.assertEqual(op['maximum_header_bytes'],200000);self.assertEqual(op['maximum_header_requests'],1024);self.assertEqual(op['new_ocean_velocity_values_permitted'],0)
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)


if __name__=='__main__':unittest.main()
