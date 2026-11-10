"""Correct an extra retained-metadata test parse; do not reanalyse native fields."""
import hashlib,json,os,signal,socket,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/a20-gulf-stream-core-direction-depths-v2.json'
TEST='analysis/test_a20_gulf_stream_core_direction_depths_v2.py'
OP='research/a20-depth-resource-accounting-operator-v1.json'


def numbers(value):
    if isinstance(value,dict):return sum(numbers(v) for v in value.values())
    if isinstance(value,list):return sum(numbers(v) for v in value)
    return int(type(value) in (int,float))


def reconcile(counts,audit_packet_numbers):
    extra=counts['typed_source_packet_numbers_per_pass']
    if counts['case_metadata_touch_bound']!=5015 or counts['case_scalar_bound_including_prior_phases_one_actual_test_and_producer']!=13123 or extra!=496:
        raise ValueError('Exact frozen source counters required')
    metadata=counts['case_metadata_touch_bound']+extra+audit_packet_numbers
    scalars=counts['case_scalar_bound_including_prior_phases_one_actual_test_and_producer']+extra+audit_packet_numbers
    if audit_packet_numbers>2500 or metadata>10000 or scalars>250000:raise ValueError('Original cumulative caps unchanged')
    return {'source_reported_metadata_touch_bound':5015,'source_reported_case_scalar_bound':13123,
        'extra_test_direct_metadata_packet_numbers':extra,'audit_retained_metadata_packet_numbers':audit_packet_numbers,
        'corrected_case_metadata_touch_bound_including_audit':metadata,
        'corrected_case_scalar_bound_including_audit':scalars,
        'original_metadata_cap_unchanged':10000,'original_scalar_cap_unchanged':250000,
        'new_native_ocean_values_decoded':0,'new_provider_requests':0}


def main():
    def stopped(*a):raise SystemExit('Stopped offline resource accounting audit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline accounting only'))
    signal.alarm(30);start=float(os.environ['OSW_A20_ACCOUNTING_PHASE_START'])
    if not 0<=time.monotonic()-start<60:raise ValueError('Shared phase clock required')
    op=json.loads((ROOT/OP).read_bytes())
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
    if 'old=json.loads((ROOT/SOURCE).read_bytes());r=build()' not in (ROOT/TEST).read_text():
        raise ValueError('Reviewed extra direct test parse plus actual build must remain identifiable')
    raw=(ROOT/SOURCE).read_bytes()
    if len(raw)>400000:raise ValueError('Bounded retained metadata packet')
    source=json.loads(raw);result=reconcile(source['counts'],numbers(source))
    result.update(schema='osw.a20-depth-resource-accounting-audit.v1',
        status='EXTRA_TEST_METADATA_PARSE_CORRECTED_NATIVE_RESULTS_UNCHANGED',
        source_file=SOURCE,source_sha256=hashlib.sha256(raw).hexdigest(),input_sha256=op['input_sha256'],
        original_case_operations_used=3,original_case_operations_remaining=0,original_case_response_bytes=425028,
        source_native_results_modified=False,physical_current_bottom_established=False,
        runtime_changed=False,full_goal_complete=False)
    result['new_accounting_phase_seconds']=time.monotonic()-start
    result['cumulative_case_time_charge_seconds']=source['cumulative_case_time_charge_seconds']+result['new_accounting_phase_seconds']
    if result['cumulative_case_time_charge_seconds']>180:raise ValueError('Original case time cap unchanged')
    folder=ROOT/'a20-depth-resource-accounting-v1';folder.mkdir(exist_ok=False)
    (folder/'accounting.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(result))


if __name__=='__main__':main()
