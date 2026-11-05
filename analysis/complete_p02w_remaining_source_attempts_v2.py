"""Finish only the two unattempted resources in the original three-GET case."""
import copy,hashlib,json,os,signal,socket,time,urllib.request
from pathlib import Path
from acquire_a20_gulf_stream_cast_headers_v1 import acquire,NoRedirect,write_json
from inspect_retained_a20_gulf_stream_headers_v2 import inspect

ROOT=Path(__file__).resolve().parents[1]
OP='research/p02w-remaining-source-attempts-operator-v2.json'
PRIOR='research/source-data/p02w-kuroshio-native-depths-v1/journal.json'
SOURCE_OP='research/p02w-kuroshio-native-depth-operator-v1.json'


def remaining(prior,targets):
    if prior['case_operation_cap']!=3 or prior['case_response_byte_cap']!=600000 or prior['case_time_cap_seconds']!=180:
        raise ValueError('Original case operation/byte/time caps unchanged')
    allowed={t['url'] for t in targets};used=[r['url'] for r in prior['operations']]
    if len(used)>3 or len(set(used))!=len(used) or not set(used)<=allowed:
        raise ValueError('No duplicate/reassigned source operations')
    rows=[t for t in targets if t['url'] not in used]
    if len(rows)!=3-len(used):raise ValueError('Only original unattempted targets, no new resource allowance')
    return rows


def main():
    def stopped(*a):raise SystemExit('Stopped remaining source attempts; never replay targets')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    phase_start=float(os.environ['OSW_P02W_REMAINING_PHASE_START'])
    if not 0<=time.monotonic()-phase_start<30:raise ValueError('Shared synthetic-test/producer phase clock')
    op=json.loads((ROOT/OP).read_bytes())
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
    prior=json.loads((ROOT/PRIOR).read_bytes());source_op=json.loads((ROOT/SOURCE_OP).read_bytes())
    targets=remaining(prior,source_op['targets'])
    if [r['cast_id'] for r in targets]!=['00701','00801'] or prior['native_array_values_decoded']!=0:
        raise ValueError('Exactly two original unattempted casts; no prior native values')
    journal=copy.deepcopy(prior);prior_charge=prior['case_time_charge_seconds']
    out=ROOT/'p02w-remaining-source-attempts-v2';out.mkdir(exist_ok=False)
    write_json(out/'journal.json',journal);valid=[];outcomes=[]
    try:
        opener=urllib.request.build_opener(NoRedirect())
        for t in targets:
            if prior_charge+time.monotonic()-phase_start+30>180:
                outcomes.append({'cast_id':t['cast_id'],'status':'not_attempted_original_case_deadline'});continue
            try:
                path=acquire({'station':t['cast_id'],'url':t['url']},out,journal,opener)
                valid.append((t,path));outcomes.append({'cast_id':t['cast_id'],'status':'original_native_bytes_retained_once'})
            except Exception as error:
                outcomes.append({'cast_id':t['cast_id'],'status':'failed_once_no_retry','error_type':type(error).__name__})
                # Continue with the DIFFERENT unattempted target only. No reconnect to failed target.
        signal.alarm(max(1,min(45,int(180-prior_charge-(time.monotonic()-phase_start)))))
        socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('All permitted source requests finished'))
        metadata={'prior_failed_numeric_attribute_values':0,'reconstruction_numeric_attribute_touches':0,'new_numeric_attribute_values_touched':0}
        headers=[]
        for t,path in valid:
            try:
                headers.append({'cast_id':t['cast_id'],'raw_file':path.name,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'header':inspect(path,metadata),'status':'bounded_headers_only_no_native_values'})
            except Exception as error:
                headers.append({'cast_id':t['cast_id'],'status':'header_qualification_unresolved_raw_preserved','error_type':type(error).__name__})
        write_json(out/'headers.json',{'schema':'osw.p02w-partial-native-headers.v2','headers':headers,'numeric_attribute_ledger':metadata,
            'native_variable_values_read':0})
        report={'schema':'osw.p02w-remaining-source-attempts.v2','status':'ORIGINAL_UNATTEMPTED_TARGETS_FINISHED_NO_SCIENTIFIC_DEPTH_ADMISSION',
            'source_original_run':42020357768,'source_original_failure':'00601_connection_timeout_zero_body_no_retry',
            'new_outcomes':outcomes,'native_files_retained':len(valid),'original_operations_used':len(journal['operations']),
            'original_operations_remaining':3-len(journal['operations']),'original_response_bytes':journal['case_response_bytes'],
            'numeric_metadata_attributes_touched':metadata['new_numeric_attribute_values_touched'],
            'native_array_values_decoded':0,'new_depth_references':0,'minimum_three_valid_new_native_profiles_established':False,
            'runtime_changed':False,'full_goal_complete':False}
        write_json(out/'continuation.json',report)
        journal['metadata_numeric_attribute_values']=metadata['new_numeric_attribute_values_touched']
        journal['producer_status']=report['status'];print(json.dumps(report))
    finally:
        signal.alarm(0);journal['case_time_charge_seconds']=prior_charge+time.monotonic()-phase_start
        write_json(out/'journal.json',journal)
        if journal['case_time_charge_seconds']>180:raise TimeoutError('Original case time cap, no phase reset')


if __name__=='__main__':main()
