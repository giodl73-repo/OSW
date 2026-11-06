import copy,time,unittest
from pathlib import Path
from acquire_i06s_agulhas_cast_headers_v1 import collect,validate_operator,IDS

class SourceSafety(unittest.TestCase):
    def test_failure_does_not_retry_or_skip_other_original_target(self):
        calls=[]
        def fetch(t,*args):
            calls.append(t['station'])
            if t['station']=='046':raise TimeoutError('synthetic connection failure')
            return Path(t['station']+'.nc')
        valid,rows=collect([{'station':s} for s in IDS],None,{},None,time.monotonic(),fetch)
        self.assertEqual(calls,IDS)
        self.assertEqual([t['station'] for t,p in valid],['047','048'])
        self.assertEqual(rows[0]['status'],'failed_once_no_retry')

    def test_stop_unwinds_without_new_target(self):
        calls=[]
        def fetch(t,*args):calls.append(t['station']);raise SystemExit('synthetic stop')
        with self.assertRaises(SystemExit):collect([{'station':s} for s in IDS],None,{},None,time.monotonic(),fetch)
        self.assertEqual(calls,['046'])

    def test_expired_case_makes_no_request(self):
        def fetch(*args):raise AssertionError('must not request')
        valid,rows=collect([{'station':s} for s in IDS],None,{},None,time.monotonic()-160,fetch)
        self.assertFalse(valid)
        self.assertTrue(all(r['status']=='not_attempted_case_deadline' for r in rows))

    def test_changed_scope_rejected_before_acquisition(self):
        import json
        op=json.loads((Path(__file__).resolve().parents[1]/'research/i06s-agulhas-cast-acquisition-operator-v1.json').read_bytes())
        validate_operator(op)
        for field in ['case_operation_cap','native_scalar_case_cap','future_selected_levels_per_cast_cap']:
            bad=copy.deepcopy(op);bad[field]+=1
            with self.assertRaises(ValueError):validate_operator(bad)
        bad=copy.deepcopy(op);bad['targets'][0]['url']=bad['targets'][1]['url']
        with self.assertRaises(ValueError):validate_operator(bad)

if __name__=='__main__':unittest.main()
