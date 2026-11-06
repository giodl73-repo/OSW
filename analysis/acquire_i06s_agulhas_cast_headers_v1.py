"""One-shot original custody for a new three-cast Agulhas-region cohort."""
import hashlib,json,os,signal,socket,time,urllib.request
from pathlib import Path
from acquire_a20_gulf_stream_cast_headers_v1 import acquire,NoRedirect,write_json
from inspect_retained_a20_gulf_stream_headers_v2 import inspect

ROOT=Path(__file__).resolve().parents[1]
OP='research/i06s-agulhas-cast-acquisition-operator-v1.json'
IDS=['046','047','048']

def validate_operator(op):
    expected={'case_operation_cap':3,'case_response_byte_cap':600000,'per_response_byte_cap':200000,
        'case_time_cap_seconds':180,'metadata_numeric_attribute_cap':10000,
        'native_scalar_case_cap':250000,'native_byte_case_cap':7000000,
        'future_selected_levels_per_cast_cap':40,'maximum_native_profiles':3,
        'maximum_section_cells':20000,'maximum_measurement_nodes':6000,'geometry_tolerance_m':5000}
    if any(op.get(k)!=v for k,v in expected.items()):raise ValueError('Prospective whole-case caps required')
    if [t['station'] for t in op['targets']]!=IDS:raise ValueError('Exact independent three-cast cohort required')
    for t in op['targets']:
        if t['url']!='https://currents.soest.hawaii.edu/go-ship/ladcp/downloads/2019_I06S/'+t['station']+'.nc':
            raise ValueError('No source substitution or padding/host retries')
    if any(op['eligibility'].values()):raise ValueError('Custody is not a depth measurement')

def collect(targets,out,journal,opener,start,fetch=acquire):
    valid=[];outcomes=[]
    for target in targets:
        if time.monotonic()-start+31>180:
            outcomes.append({'station':target['station'],'status':'not_attempted_case_deadline'});continue
        try:
            path=fetch(target,out,journal,opener)
            valid.append((target,path));outcomes.append({'station':target['station'],'status':'native_bytes_retained_once'})
        except Exception as error:
            outcomes.append({'station':target['station'],'status':'failed_once_no_retry','error_type':type(error).__name__})
    return valid,outcomes

def main():
    def stopped(*a):raise SystemExit('Stopped one-shot source case; preserve journal, no replay')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    start=float(os.environ['OSW_I06S_CASE_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    op=json.loads((ROOT/OP).read_bytes());validate_operator(op)
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Pinned dependency changed: '+p)
    out=ROOT/'i06s-agulhas-cast-headers-v1';out.mkdir(exist_ok=False)
    journal={'schema':'osw.i06s-agulhas-source-journal.v1','operations':[],
        'case_operation_cap':3,'case_response_byte_cap':600000,'case_response_bytes':0,
        'case_time_cap_seconds':180,'case_time_charge_seconds':0,
        'native_scalar_case_cap':250000,'native_byte_case_cap':7000000,
        'metadata_numeric_attribute_cap':10000,'native_array_values_decoded':0,
        'native_selected_level_counts':{s:0 for s in IDS},'new_canonical_depth_references':0}
    write_json(out/'journal.json',journal)
    try:
        valid,outcomes=collect(op['targets'],out,journal,urllib.request.build_opener(NoRedirect()),start)
        signal.alarm(max(1,min(45,int(180-(time.monotonic()-start)))))
        socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Source operations closed; offline inspection only'))
        metadata={'prior_failed_numeric_attribute_values':0,'reconstruction_numeric_attribute_touches':0,'new_numeric_attribute_values_touched':0}
        headers=[]
        for t,path in valid:
            try:
                headers.append({'station':t['station'],'raw_file':path.name,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'header':inspect(path,metadata),'status':'headers_only_no_native_array_values'})
            except Exception as error:
                headers.append({'station':t['station'],'status':'header_unresolved_raw_preserved','error_type':type(error).__name__})
        write_json(out/'headers.json',{'schema':'osw.i06s-agulhas-cast-headers.v1','headers':headers,
            'numeric_attribute_ledger':metadata,'native_array_values_decoded':0})
        report={'schema':'osw.i06s-agulhas-source-custody.v1','status':'PROSPECTIVE_SOURCE_ATTEMPTS_FINISHED_NOT_DEPTH_MEASUREMENTS',
            'outcomes':outcomes,'native_files_retained':len(valid),'provider_operations_used':len(journal['operations']),
            'provider_operations_remaining':3-len(journal['operations']),'response_bytes':journal['case_response_bytes'],
            'numeric_metadata_attributes_touched':metadata['new_numeric_attribute_values_touched'],
            'native_array_values_decoded':0,'new_depth_references':0,'source_current_axis_membership_verified':False,
            'source_software_qualified_for_measurement':False,'source_final_QC_verified':False,
            'runtime_changed':False,'full_goal_complete':False}
        write_json(out/'custody.json',report)
        journal['metadata_numeric_attribute_values']=metadata['new_numeric_attribute_values_touched']
        journal['producer_status']=report['status']
        if sum(p.stat().st_size for p in out.iterdir())>2400000:raise ValueError('Whole output chunk cap')
        print(json.dumps(report))
    finally:
        signal.alarm(0);journal['case_time_charge_seconds']=time.monotonic()-start
        write_json(out/'journal.json',journal)
        if journal['case_time_charge_seconds']>180:raise TimeoutError('Original case time, never reset per phase')

if __name__=='__main__':main()
