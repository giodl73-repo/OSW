"""Offline source-correspondence gate, preserving original case limits."""
import datetime,hashlib,json,os,signal,socket,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/gaspe1991-metadata-scope-closure-operator-v1.json'
SOURCE='research/gaspe1991-adcp-variable-metadata-v1.json'
PRIOR='research/gaspe1991-adcp-info-ledger-v1.json'
def parse_utc(v):return datetime.datetime.fromisoformat(v.replace('Z','+00:00'))
def assess(info):
    if info['schema']!='osw.gaspe1991-original-adcp-variable-metadata.v1' or info['native_data_rows_decoded']!=0:raise ValueError('Original variable metadata only')
    g=info['global_attributes'];v=info['variables']
    if g['DOI']!='https://doi.org/10.26071/ogsl-9acdc006-20cb' or g['cdm_data_type']!='Profile':raise ValueError('Exact original profile product')
    lo,hi=[float(x.strip()) for x in v['time']['attributes']['actual_range'].split(',')]
    origin=parse_utc('1970-01-01T00:00:00Z')
    numeric=[origin+datetime.timedelta(seconds=x) for x in [lo,hi]]
    declared=[parse_utc(g[k]) for k in ['time_coverage_start','time_coverage_end']]
    if numeric!=declared or not declared[0]<=declared[1]:raise ValueError('Independent numeric/ISO metadata clock consistency')
    requested=[parse_utc('1991-09-01T00:00:00Z'),parse_utc('1991-10-01T00:00:00Z')]
    overlap=declared[0]<requested[1] and declared[1]>=requested[0]
    return {'requested_period':['1991-09-01T00:00:00Z','1991-10-01T00:00:00Z'],'advertised_coverage':[g[k] for k in ['time_coverage_start','time_coverage_end']],
        'numeric_time_range_matches_iso_attributes':True,'advertised_coverage_overlaps_requested_period':overlap,
        'eastward_cf_label_present':v['x_vel']['attributes'].get('standard_name')=='eastward_sea_water_velocity',
        'northward_cf_label_present':v['y_vel']['attributes'].get('standard_name')=='northward_sea_water_velocity',
        'cf_labels_establish_ship_motion_corrected_absolute_velocity':False,
        'seafloor_velocity_fields_establish_correction_formula':False,
        'native_depth_domain_from_metadata_m':v['depth']['attributes']['actual_range'],
        'native_depth_domain_is_current_bottom':False,
        'native_measurement_request_qualified':False,
        'reason':'Advertised coverage does not support requested1991period; metadata labels alone also do not establish navigation/shipmotion processing. Do not substitute1993GPS-limited cruise or invent correction signs.',
        'proves_1991_data_absent_from_entire_provider_archive':False}
def main():
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline source-scope gate only'))
    start=float(os.environ['OSW_GASPE1991_CLOSE_START']);out=ROOT/'gaspe1991-metadata-scope-closure-v1';out.mkdir(exist_ok=False)
    def stopped(*a):raise TimeoutError('Original cumulative source deadline or SIGTERM')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(50)
    encode=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
    try:
        opraw=(ROOT/OP).read_bytes();srcraw=(ROOT/SOURCE).read_bytes();priorraw=(ROOT/PRIOR).read_bytes()
        newbound=2*len(opraw)+2*len(srcraw)+2*len(priorraw)+2000
        # Strict small packet bounds before any source metadata JSON decoding.
        if max(len(opraw),len(srcraw),len(priorraw))>100000 or newbound+12998>250000:raise ValueError('Original source-case metadata numeric upper bound')
        op=json.loads(opraw);prior=json.loads(priorraw)
        if prior['status']!='ERDDAP_VARIABLE_METADATA_RETAINED_NATIVE_SELECTION_PENDING' or prior['case_numeric_upper_bound']!=12998 or prior['attempted_provider_operations']!=2 or prior['remaining_provider_operations']!=6 or prior['provider_case_closed'] is not False:raise ValueError('Exact open original case and carried counters')
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen source changed:'+p)
        info=json.loads(srcraw);result=assess(info)
        if result['advertised_coverage_overlaps_requested_period'] is not False or result['advertised_coverage']!=['1993-06-06T00:00:18Z','1993-06-11T06:19:30Z']:raise ValueError('Reviewed source mismatch changed')
        elapsed=time.monotonic()-start;cumulative=prior['cumulative_active_seconds']+elapsed
        if cumulative>60:raise ValueError('Original cumulative case time cap')
        report={'schema':'osw.gaspe1991-observed-source-correspondence-review.v1','status':'REQUESTED_1991_PERIOD_UNSUPPORTED_BY_ADVERTISED_1993_COVERAGE','source_metadata_sha256':hashlib.sha256(srcraw).hexdigest(),'scope_gate':result,
            'new_native_requests':0,'new_depth_references':0,'native_values_decoded':0,'runtime_changed':False,'full_goal_complete':False}
        ledger=dict(prior,status='CLOSED_SOURCE_PERIOD_AND_PROCESSING_NOT_QUALIFIED',provider_case_closed=True,remaining_provider_operations=0,
            unused_provider_operations_surrendered=6,new_provider_operations=0,new_phase_metadata_numeric_upper_bound=newbound,
            case_numeric_upper_bound=prior['case_numeric_upper_bound']+newbound,prior_info_ledger_sha256=hashlib.sha256(priorraw).hexdigest(),
            cumulative_active_seconds=cumulative,closure_phase_active_seconds=elapsed,source_operation_or_native_budget_renewed=False)
        a,b=encode(report),encode(ledger)
        if json.loads(a)!=report or json.loads(b)!=ledger or len(a)+len(b)+prior['raw_bytes']>1600000:raise ValueError('Exact closure roundtrip/cumulative output gate')
        (out/'source-correspondence.json').write_bytes(a);(out/'ledger.json').write_bytes(b);print(json.dumps(report));print(json.dumps(ledger))
    finally:signal.alarm(0)
if __name__=='__main__':main()
