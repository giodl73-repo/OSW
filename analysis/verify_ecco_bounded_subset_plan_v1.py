"""Cloud-only synthetic verification report; no ocean fields or metadata acquired."""
import hashlib,json,os,signal,socket,time
from pathlib import Path
from test_ecco_bounded_subset_plan_v1 import fixture,window
from ecco_bounded_subset_plan_v1 import plan_subset,prerequisite_report

def main():
    start=float(os.environ['OSW_ECCO_GUARD_START'])
    def stop(*args):raise TimeoutError('Shared60-second test/report limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    elapsed=time.monotonic()-start
    if not 0<=elapsed<60:raise TimeoutError('Shared test/report clock expired')
    signal.alarm(max(1,int(60-elapsed)));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline synthetic verification only'))
    try:
        root=Path(__file__).resolve().parents[1];out=root/'ecco-bounded-subset-plan-v1';out.mkdir(exist_ok=False)
        report={'schema':'osw.ecco-subset-guard-synthetic-verification.v1','status':'SYNTHETIC_BOUNDS_ONLY_NOT_ACTUAL_ECCO_ACCESS','synthetic_plan':plan_subset(fixture(),window()),'prerequisite_report':prerequisite_report(earthdata_available=False,metadata_verified=False,server_subset_verified=False,transport_bound_verified=False,scientific_operator_frozen=False),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['analysis/ecco_bounded_subset_plan_v1.py','analysis/test_ecco_bounded_subset_plan_v1.py','analysis/verify_ecco_bounded_subset_plan_v1.py']},'tests_expected':12,'new_depth_references':0,'native_requests':0,'real_metadata_requests':0,'compiled_scientific_inputs_read':0,'runtime_changed':False,'full_goal_complete':False,'shared_active_seconds_including_tests':time.monotonic()-start}
        raw=(json.dumps(report,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')
        if json.loads(raw)!=report:raise ValueError('Complete synthetic report roundtrip')
        if len(raw)>2400000:raise ValueError('Whole output cap')
        (out/'verification-report.json').write_bytes(raw);print(raw.decode('utf8'))
    finally:signal.alarm(0)

if __name__=='__main__':main()
