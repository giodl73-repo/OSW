"""First field analysis after a proven predecode packaging failure, no acquisition."""
import hashlib,json,os,re,signal,socket,time
from pathlib import Path
from derive_wsc_f3_warm_flow_brackets_v1 import selected_profiles,bracket,THRESHOLDS
ROOT=Path(__file__).resolve().parents[1]
OP='research/wsc-f3-offline-recovery-operator-v2.json'
FAILED='research/wsc-f3-packaging-failure-ledger-v1.json'
RAW='research/source-data/wsc-f3-bounded-preview-v1/preview.html'

def recovery_gate(prior):
    if prior.get('status')!='FAILED_NO_RETRY_CASE_CLOSED' or prior.get('error_type')!='FileNotFoundError' or not prior.get('error','').endswith("/analysis/capture_wsc_f3_bounded_preview_v1.py'"):
        raise ValueError('Exact packaging-only failure required')
    if prior.get('provider_case_closed') is not True or prior.get('remaining_provider_operations')!=0 or prior.get('attempted_provider_operations')!=2 or prior.get('native_numeric_values_decoded')!=0 or prior.get('case_numeric_upper_bound')!=147160:
        raise ValueError('Unchanged closed acquisition and never-decoded fields required')
    if 'additional_selection_and_output_numeric_upper_bound_reserved' in prior:raise ValueError('First unused analysis reservation only; no failed native-analysis replay')
    if len(prior.get('source_responses',[]))!=2 or any(r.get('http_status')!=200 or r.get('status')!='ORIGINAL_RAW_RETAINED_TARGET_CLOSED' for r in prior['source_responses']):raise ValueError('Exact retained successful original responses required')

def main():
    start=float(os.environ['OSW_F3_RECOVERY_START']);out=ROOT/'wsc-f3-offline-brackets-v2';out.mkdir(exist_ok=False)
    prior=json.loads((ROOT/FAILED).read_bytes());recovery_gate(prior)
    ledger=dict(prior,status='CLOSED_ACQUISITION_FIRST_OFFLINE_FIELD_ANALYSIS_RESERVED',packaging_failure_active_seconds=prior['cumulative_active_seconds'],prior_numeric_upper_bound=147160,new_provider_operations=0)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
    def save():(out/'ledger.json').write_bytes(encode(ledger))
    def stopped(*a):raise TimeoutError('Same original source-case cumulative deadline or SIGTERM')
    elapsed=prior['cumulative_active_seconds']+time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared recovery tests/producer clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save()
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No provider, network or archive replay'))
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen recovery input changed:'+p)
        ledger.update(additional_selection_and_output_numeric_upper_bound_reserved=30000,case_numeric_upper_bound=177160);save()
        profiles,nrows,gears=selected_profiles((ROOT/RAW).read_bytes());complete=all(len(p['levels'])>=2 for p in profiles)
        records=[bracket(p if complete else dict(p,levels=[]),t) for p in profiles for t in THRESHOLDS]
        if not complete:
            for row in records:row['status']='INSUFFICIENT_THREE_PROFILE_NATIVE_COHORT_NO_MEASUREMENT_ADMITTED'
        report={'schema':'osw.wsc-f3-warm-northward-flow-brackets.v2','status':'DATED_NATIVE_RESULTS_AFTER_PREDECODE_PACKAGING_REPAIR',
            'source_doi':'10.1594/PANGAEA.800346','source_raw_sha256':'54aa3e8bab52d710dcb1ce30474a883d41859bf429e67113fd416fbf34445ea1',
            'profiles':profiles,'records':records,'selected_cohort_complete':complete,'native_preview_rows':nrows,'velocity_gears_in_preview':gears,
            'qualification_protocol':'plans/wsc-f3-warm-flow-brackets-protocol-v1.md',
            'qualifications':['The first native field analysis follows a proven missing-file failure before any fields or additional numeric allowance were decoded/reserved. Original provider targets remain closed, zero new requests.','Original two-pass source reservation and cumulative failure clock are carried. Only the originally declared unused30000 scalar analysis allowance is spent; no case or budget is renewed.','Exact source flags, positive water-depth metres, nativecm/s components, declared dates, T>2degC and5/10/20cm/s thresholds use frozen v1 methods.','The component lower edge is a conditional native-level bracket, with sparse-level connectivity assumption. It is not a physical whole-current bottom, midpoint, uncertainty interval, thickness or annual range.','Only the original first2000 rows are available. Missing selected dates/levels are not proof of absence in the annual archive.','Provider meridional components are not independently recalibrated and this archive is not assumed to have the paper filtering/gridding. No tides removed here.','No upper-boundary extrapolation, volume estimate, full-route coverage or UI/runtime change. Threshold variants and same-mooring dates are not independent observations.'],
            'canonical_depth_reference_admitted':False,'runtime_changed':False,'full_goal_complete':False}
        raw=encode(report);charge=2*len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw))+5000
        if charge>30000 or json.loads(raw)!=report:raise ValueError('Original numeric allowance and complete JSON roundtrip')
        (out/'warm-flow-brackets.json').write_bytes(raw)
        ledger.update(status='CLOSED_CASE_FIRST_NATIVE_ANALYSIS_RETAINED_NO_NEW_ACQUISITION',selected_profile_dates=len(profiles),selected_profiles_with_native_velocity_levels=sum(bool(p['levels']) for p in profiles),
            selected_native_levels=sum(len(p['levels']) for p in profiles),native_numeric_values_decoded=sum(len(p['levels'])*4 for p in profiles),
            decoded_cells=sum(len(p['levels'])*10 for p in profiles),measurement_nodes=sum(len(p['levels'])*3 for p in profiles),
            original_unused_provider_operations_surrendered=6,new_provider_operations=0,new_depth_references=0,source_native_field_parse_attempts=1)
        save()
        if sum(p.stat().st_size for p in out.iterdir())>2400000:raise ValueError('Whole original scientific output cap')
        print(json.dumps({'cohort_complete':complete,'native_levels':ledger['selected_native_levels'],'records':records,'preview_rows':nrows}),flush=True)
    except BaseException as e:
        ledger.update(status='FAILED_FIRST_OFFLINE_FIELD_ANALYSIS_NO_REPLAY',recovery_error_type=type(e).__name__,recovery_error=str(e)[:400]);raise
    finally:
        ledger['cumulative_active_seconds']=prior['cumulative_active_seconds']+time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)

if __name__=='__main__':main()
