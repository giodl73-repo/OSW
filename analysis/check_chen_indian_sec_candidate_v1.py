"""Cloud-only complete packet materialization and native acceptance; compact evidence only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/chen-indian-sec-candidate-request-v1.json'
PREFLIGHT='research/chen-indian-sec-candidate-preflight-v1.json'
OUT=ROOT/'.pytest_cache/chen-indian-sec-candidate-v1'
WORK=ROOT/'.pytest_cache/chen-indian-sec-candidate-work-v1'

def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode()

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Candidate packet access permitted only in the scoped cloud job')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required: '+key)
    request=read(REQUEST)
    if request.get('schema')!='osw.chen-indian-sec-candidate-request.v1' or request.get('execute') is not True:
        raise ValueError('Disabled or changed candidate request')
    for key in ['cloud_parent_packet_read_permitted','cloud_candidate_materialization_permitted','cloud_native_cli_build_permitted']:
        if request.get(key) is not True:raise ValueError('Candidate operation not enabled: '+key)
    for key in ['wasm_build_permitted','index_load_permitted','index_rebuild_permitted','ocean_field_processing_permitted','browser_permitted','installation_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated operation enabled: '+key)
    if sha(PREFLIGHT)!=request['preflight_sha256']:raise ValueError('Changed candidate freeze')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen input changed: '+path)
    for path,row in pref['installed_files'].items():
        if sha(path)!=row['sha256'] or (ROOT/path).stat().st_size!=row['bytes']:raise ValueError('Installed parent changed: '+path)
    for path in pref['disabled_requests']:
        r=read(path)
        if r.get('execute',r.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+path)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad processing must remain disabled')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()!=os.environ['GITHUB_SHA']:
        raise ValueError('Exact source checkout required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean checkout required')
    return pref

def verify_extension(parent,child,contract):
    """Compare the complete packet against only the declared exact changes."""
    if set(child)!=set(parent) or any(child[k]!=parent[k] for k in parent if k not in ['collections','manifest']):
        raise ValueError('Packet envelope changed')
    before,after=parent['collections'],child['collections']
    if set(after)!=set(before)|{'current_length_sensitivities'}:raise ValueError('Collection inventory differs')
    changed=0
    for name,rows in before.items():
        if name=='objects':expected=[contract['final_owner'] if r.get('id')=='current:indian-south-equatorial' else r for r in rows]
        elif name=='length_assessments':expected=[contract['final_length_assessment'] if r.get('entity_id')=='current:indian-south-equatorial' else r for r in rows]
        elif name=='current_length_series':expected=rows+[contract['series_record']]
        elif name=='current_length_readings':expected=rows+contract['reading_records']
        elif name=='sources':expected=rows+contract['new_sources']
        else:expected=rows
        if after[name]!=expected:raise ValueError('Historical rows/order changed: '+name)
        changed+=name in ['objects','length_assessments','current_length_series','current_length_readings','sources']
    if after['current_length_sensitivities']!=contract['sensitivity_records']:raise ValueError('Sensitivity records differ')
    if {k:len(v) for k,v in after.items()}!=contract['expected_totals']:raise ValueError('Complete collection counts differ')
    old,new=parent['manifest'],child['manifest'];key='indian_sec_model_grid_lengths_v1'
    if set(new)!=set(old)|{key} or any(new[k]!=old[k] for k in old if k!='input_sha256'):raise ValueError('Historical manifest changed')
    pins={**contract['input_sha256'],'research/chen-indian-sec-ridge-length-query-contract-v1.json':hashlib.sha256((json.dumps(contract,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()).hexdigest()}
    if new['input_sha256']!={**old.get('input_sha256',{}),**pins}:raise ValueError('Manifest scientific input pins differ')
    if any(p in pins and pins[p]!=h for p,h in old.get('input_sha256',{}).items()):raise ValueError('Historical input rebound')
    marker={'schema':'osw.indian-sec-model-grid-length-runtime.v1','contract_file':'research/chen-indian-sec-ridge-length-query-contract-v1.json','contract_sha256':pins['research/chen-indian-sec-ridge-length-query-contract-v1.json'],'parent_logical_sha256':contract['parent_logical_sha256'],'series_added':1,'readings_added':75,'sensitivities_added':120,'qualified_model_grid_lengths':8,'withheld_readings':67,'reported_lengths_added':0,'reference_routes_added':0,'widths_added':0,'physical_state_joins_added':0}
    if new[key]!=marker:raise ValueError('Candidate receipt differs')
    return {'existing_collections_compared':len(before),'declared_changed_collections':changed,'unchanged_collections':len(before)-changed,'new_collections':1}

def run():
    pref=controls();OUT.mkdir(exist_ok=False,parents=True);WORK.mkdir(exist_ok=False,parents=True)
    from query_packet import read_bundle_bytes
    import chen_indian_sec_ridge_query_v1 as query
    contract=query.read(query.FILE)
    if query.encoded(query.build_contract())!=(ROOT/query.FILE).read_bytes():raise ValueError('Frozen scientific contract replay differs')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if hashlib.sha256(raw).hexdigest()!=query.PARENT or len(raw)!=190686988:raise ValueError('Installed logical parent differs')
    parent=json.loads(raw);del raw
    if {k:len(v) for k,v in parent['collections'].items()}!=contract['parent_collection_counts']:raise ValueError('Complete parent counts differ')
    collections,manifest=query.prepare(parent['collections'],parent['manifest'],contract,parent_logical_sha256=query.PARENT)
    child={**parent,'collections':collections,'manifest':manifest}
    comparison=verify_extension(parent,child,contract)
    candidate=WORK/'candidate.json';candidate.write_bytes(encoded(child));candidate_sha=sha(candidate)
    del child,collections,manifest,parent
    toolchain=subprocess.check_output(['rustc','+1.95.0','--version'],timeout=30).decode().strip()
    if not toolchain.startswith('rustc 1.95.0 '):raise ValueError('Frozen compiler required')
    env=dict(os.environ,CARGO_TARGET_DIR=str(WORK/'target'),CARGO_INCREMENTAL='0')
    build=subprocess.run(['cargo','+1.95.0','build','--locked','--manifest-path','rust/osw-query/Cargo.toml','--bin','osw-query-cli'],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=2100)
    (OUT/'native-build.txt').write_bytes(build.stdout)
    if build.returncode:raise ValueError('Native CLI build failed; exact log retained')
    binary=WORK/'target/debug/osw-query-cli';proofs=[]
    def cli(name,args,request=None):
        result=subprocess.run([str(binary),str(candidate),*args],input=encoded(request) if request else None,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=600)
        (OUT/(name+'-stderr.txt')).write_bytes(result.stderr)
        if result.returncode:raise ValueError(name+' native acceptance failed: '+result.stderr.decode(errors='replace')[:1500])
        value=json.loads(result.stdout)
        if value.get('ok') is not True:raise ValueError(name+' API did not succeed')
        proofs.append({'case':name,'response_sha256':hashlib.sha256(result.stdout).hexdigest(),'response_bytes':len(result.stdout)})
        return value
    for name,collection,filters,expected in [
        ('all-readings',query.READINGS,[('series_id',query.SERIES_ID)],contract['reading_records']),
        ('withheld-readings',query.READINGS,[('series_id',query.SERIES_ID),('length_km',None)],[r for r in contract['reading_records'] if r['length_km'] is None]),
        ('nominal-qualified',query.READINGS,[('series_id',query.SERIES_ID),('kernel_cells',3),('status','regional_model_grid_estimate')],[r for r in contract['reading_records'] if r['kernel_cells']==3 and r['length_km'] is not None]),
        ('all-sensitivities',query.SENSITIVITIES,[('series_id',query.SERIES_ID)],contract['sensitivity_records'])]:
        request={'collection':collection,'filters':[{'field':k,'op':'eq','value':v} for k,v in filters],'limit':200}
        result=cli(name,['-'],request);scene=result['chart_scene']
        # Default stable query ordering is by ID; compare full rows by identity, never just counts.
        if result['total']!=len(expected) or {r['id']:r for r in result['rows']}!={r['id']:r for r in expected}:raise ValueError(name+' complete matching records differ')
        if scene['kind']!='regional_model_core_length_series' or scene['selected_records']!=result['rows'] or scene['selected_count']!=len(expected):raise ValueError(name+' filtered scene differs')
        proofs[-1]['matching_records']=len(expected)
    result=cli('current-card',['--object-view',query.ENTITY]);scene=result['regional_model_length_scene']
    if scene['readings']!=contract['reading_records'] or scene['sensitivities']!=contract['sensitivity_records'] or scene['series']!=contract['series_record']:raise ValueError('Complete current-card scene differs')
    for path,row in pref['installed_files'].items():
        if sha(path)!=row['sha256'] or (ROOT/path).stat().st_size!=row['bytes']:raise ValueError('Installed file changed during execution')
    report={'schema':'osw.chen-indian-sec-candidate-result.v1','status':'PASS_COMPLETE_PACKET_NATIVE_ACCEPTANCE','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'request_sha256':sha(REQUEST),'preflight_sha256':sha(PREFLIGHT),'parent_logical_sha256':query.PARENT,'candidate_logical_sha256':candidate_sha,'candidate_logical_bytes':candidate.stat().st_size,'comparison':comparison,'native_api_checks':proofs,'compiler':toolchain,'native_binary_sha256':sha(binary),'native_build_log_sha256':sha(OUT/'native-build.txt'),'installed_parent_files_preserved':21,'candidate_packet_uploaded':False,'wasm_built':False,'index_loaded':False,'index_rebuilt':False,'browser_run':False,'installed_data_changed':False,'local_bulk_sync':False,'full_goal_complete':False}
    (OUT/'result.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(exist_ok=True,parents=True);(OUT/'failure.json').write_bytes((json.dumps({'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')},indent=2)+'\n').encode())
        raise
