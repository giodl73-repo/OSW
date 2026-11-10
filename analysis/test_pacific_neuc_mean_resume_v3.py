import base64,copy,hashlib,json,unittest
from unittest.mock import patch
import pacific_neuc_mean_resume_v3 as p
from bounded_hycom_http_ranges_v1 import BoundedHttpRanges


class RecoveryTests(unittest.TestCase):
    def fixture(self):
        header={'source_object_url':'https://data.hycom.org/datasets/GLBv0.08/expt_53.X/meanstd/netcdf/test_uv3z.nc','source_content_length':10000,'source_last_modified':'fixed'}
        raw=b'1234';row={'ranges':[[100,4]],'status':'success','response_body_bytes':4,'parts':[{'start':100,'length':4,'sha256':hashlib.sha256(raw).hexdigest()}]}
        ledger={'source_url':header['source_object_url'],'source_bytes':10000,'source_last_modified':'fixed','automatic_retries':0,'requests':[{'ranges':[[200,4]],'status':'failed_no_replay'},row],'completed_ranges':1,'attempted_requested_bytes':8,'response_body_bytes':4}
        cp={'schema':'osw.neuc-completed-ranges.v1','source_url':header['source_object_url'],'source_last_modified':'fixed','parts':[{'start':100,'length':4,'raw_base64':base64.b64encode(raw).decode()}]}
        op={'maximum_ranges_per_request':5,'maximum_http_requests':1000,'maximum_requested_bytes':1000000,'maximum_response_body_bytes':2048,'maximum_total_response_body_bytes':7000000}
        return header,ledger,cp,op
    def test_imported_success_and_all_prior_attempts_are_carried(self):
        h,l,c,op=self.fixture();parts,rows,requested,body=p.import_custody([l],c,h)
        self.assertEqual(parts,{(100,4):b'1234'});self.assertEqual((len(rows),requested,body),(2,8,4))
        rows[0]['status']='changed';self.assertEqual(l['requests'][0]['status'],'failed_no_replay')
    def test_changed_source_corrupt_checkpoint_missing_or_duplicate_success_rejected(self):
        h,l,c,op=self.fixture()
        for kind in ['identity','bytes','missing','duplicate','counts','partial_failure','nonterminal']:
            ll=copy.deepcopy(l);cc=copy.deepcopy(c)
            if kind=='identity':ll['source_last_modified']='changed'
            if kind=='bytes':cc['parts'][0]['raw_base64']='AAAAAA=='
            if kind=='missing':cc['parts']=[]
            if kind=='duplicate':cc['parts']*=2
            if kind=='counts':ll['completed_ranges']=2
            if kind=='partial_failure':ll['requests'][0]['response_body_bytes']=1;ll['response_body_bytes']=5
            if kind=='nonterminal':ll['requests'][0]['status']='reserved'
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.import_custody([ll],cc,h)
    def test_only_missing_ranges_requested_with_no_duplicate_or_cap_reset(self):
        h,l,c,op=self.fixture();parts,rows,requested,body=p.import_custody([l],c,h)
        allowed=[(i,4) for i in range(100,240,10)];b=p.recovery_plan(allowed,parts,rows,requested,body,op)
        self.assertEqual([len(x) for x in b],[5,5,3]);self.assertNotIn((100,4),[r for batch in b for r in batch]);self.assertIn((200,4),[r for batch in b for r in batch])
        for key,value in [('maximum_http_requests',4),('maximum_requested_bytes',59),('maximum_total_response_body_bytes',6147),('maximum_ranges_per_request',6)]:
            bad={**op,key:value}
            with self.subTest(key=key),self.assertRaises(ValueError):p.recovery_plan(allowed,parts,rows,requested,body,bad)
        with self.assertRaises(ValueError):p.recovery_plan(allowed+[allowed[0]],parts,rows,requested,body,op)
    def test_seeded_reader_refuses_replaying_imported_success_before_io(self):
        h,l,c,op=self.fixture();parts,rows,requested,body=p.import_custody([l],c,h)
        reader=BoundedHttpRanges(h['source_object_url'],10000,'fixed',[(100,4),(200,4)],1000,1000000,2048,7000000)
        reader.rows=rows;reader.requested_bytes=requested;reader.body_bytes=body;reader.completed=set(parts);reader.attempted=set(parts)
        with patch('urllib.request.urlopen',side_effect=AssertionError('No network allowed')):
            with self.assertRaises(ValueError):reader.read([(100,4)])
        self.assertEqual(reader.receipt()['attempted_requested_bytes'],8)
    def test_actual_plan_preserves_frozen_geometry_and_all_prior_budget(self):
        op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        old=json.loads((p.ROOT/op['geometry_operator_file']).read_bytes());h=json.loads((p.ROOT/old['header_file']).read_bytes());axes=json.loads((p.ROOT/old['coordinates_file']).read_bytes())['coordinate_arrays']
        sections,patches,_,counts=p.rectangle_plan(axes,h,old);allowed=[r for patch in patches for r in patch['ranges']]
        parts,rows,requested,body=p.import_custody([json.loads((p.ROOT/f).read_bytes()) for f in op['prior_ledger_files']],json.loads((p.ROOT/op['prior_checkpoint_file']).read_bytes()),h)
        b=p.recovery_plan(allowed,parts,rows,requested,body,op)
        self.assertEqual((len(allowed),len(parts),len(b),len(rows),requested,body),(4080,1,816,3,4480,128))
        self.assertEqual(counts['cell_pairs'],130560);self.assertEqual(requested+sum(n for batch in b for _,n in batch),526592)
        self.assertEqual(set(allowed),set(parts)|{r for batch in b for r in batch});self.assertEqual(len([r for batch in b for r in batch]),4079)
        self.assertEqual(old['selection_depth_interval_m'],[300.,1500.]);self.assertEqual(old['primary_threshold_m_s'],.02)


if __name__=='__main__':unittest.main()
