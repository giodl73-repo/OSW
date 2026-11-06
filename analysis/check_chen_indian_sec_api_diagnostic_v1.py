"""Cloud-only native batch diagnosis of complete APIs; preserves acceptance rules."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/chen-indian-sec-api-diagnostic-request-v1.json'
PREFLIGHT='research/chen-indian-sec-api-diagnostic-preflight-v1.json'
OUT=ROOT/'.pytest_cache/chen-indian-sec-api-diagnostic-v1'
WORK=ROOT/'.pytest_cache/chen-indian-sec-api-diagnostic-work-v1'
OWNERS=['current:atlantic-north-equatorial','current:pacific-north-equatorial','current:atlantic-south-equatorial','current:pacific-south-equatorial','current:indian-south-equatorial','current:north-equatorial','current:south-equatorial']
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with (ROOT/p).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):raise ValueError('Scoped cloud API diagnostic only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for k in ['CARGO_BUILD_JOBS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(k)!='1':raise ValueError('One worker required')
    r=read(REQUEST)
    if r.get('schema')!='osw.chen-indian-sec-api-diagnostic-request.v1' or r.get('execute') is not True or sha(PREFLIGHT)!=r['preflight_sha256']:raise ValueError('Disabled/changed request')
    for k in ['cloud_parent_packet_read_permitted','cloud_index_registration_permitted','native_probe_build_permitted']:
        if r.get(k) is not True:raise ValueError('Missing diagnostic permission')
    for k in ['wasm_build_permitted','browser_permitted','installation_permitted','main_merge_permitted','local_bulk_sync_permitted','ocean_field_processing_permitted']:
        if r.get(k) is not False:raise ValueError('Unrelated permission enabled')
    p=read(PREFLIGHT)
    for f,h in p['input_sha256'].items():
        if sha(f)!=h:raise ValueError('Changed frozen input: '+f)
    for f,row in p['installed_files'].items():
        if sha(f)!=row['sha256'] or (ROOT/f).stat().st_size!=row['bytes']:raise ValueError('Changed installed file: '+f)
    for f in p['disabled_requests']:
        v=read(f)
        if v.get('execute',v.get('execution_permitted')) is not False:raise ValueError('Older request enabled')
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad work enabled')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact checkout required')
    return p

def run():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    import chen_indian_sec_ridge_index_v1 as index
    import chen_indian_sec_snapshot_diff_v1 as diagnostic
    from query_packet import read_bundle_bytes
    from check_chen_indian_sec_candidate_v2 import verify_extension
    query=index.query;c,replay=query.validated_contract()
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if index.sha(raw)!=query.PARENT:raise ValueError('Changed parent packet')
    parentpath=WORK/'parent.json';parentpath.write_bytes(raw);parent=json.loads(raw);del raw
    cases=[{'kind':'snapshot','name':n} for n in ['atlas','seasons','dashboard']]+[{'kind':'object','request':{'id':o}} for o in OWNERS]
    fixture=WORK/'parent-request.json';write(fixture,{'payload_sha256':query.PARENT,'cases':cases})
    parentresult=WORK/'parent-results.json'
    subprocess.run(['node','--max-old-space-size=1536','analysis/check_chen_indian_sec_parity_v1.mjs','capture-main',str(ROOT/'almanac/query-engine.wasm'),str(parentpath),str(fixture),str(parentresult),sha('almanac/query-engine.wasm')],check=True,timeout=600)
    baseline=json.loads(parentresult.read_bytes())
    collections,manifest=query.prepare(parent['collections'],parent['manifest'],c,parent_logical_sha256=query.PARENT)
    child={**parent,'collections':collections,'manifest':manifest};verify_extension(parent,child,c)
    generated,audit=index.source_index((ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    child=index.attach(child,generated,audit);candidate=WORK/'candidate.json';candidate.write_bytes(index.encode(child));logical=sha(candidate)
    if logical!='000ec593c4fd1eb597a0a7204824b5c8c8e19cd8e2683080095a46ec50609cb1':raise ValueError('Changed indexed candidate')
    for p,b in generated.items():(ROOT/p).write_bytes(b)
    inventory=read('research/chen-indian-sec-delivery-run-v1/compile-inventory.json')
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for p,h in inventory[group].items():
            if sha(p)!=h:raise ValueError('Production source differs from failed native build: '+p)
    env=dict(os.environ,CARGO_TARGET_DIR=str(WORK/'build'),CARGO_INCREMENTAL='0')
    with (OUT/'native-probe-build.txt').open('wb') as log:subprocess.run(['cargo','+1.95.0','build','--locked','--manifest-path','rust/osw-query/Cargo.toml','--example','delivery_probe_v1','--bin','osw-query-cli'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
    probe=WORK/'build/debug/examples/delivery_probe_v1';cli=WORK/'build/debug/osw-query-cli'
    result=subprocess.run([str(probe),'main',str(candidate)],input=json.dumps({'cases':cases}).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=600)
    (WORK/'native-results.json').write_bytes(result.stdout);batch=json.loads(result.stdout)
    if len(batch['cases'])!=10:raise ValueError('Complete ten-case batch required')
    checks=[]
    for old,new in zip(baseline['cases'],batch['cases']):
        if {k:v for k,v in old.items() if k!='expected'}!={k:v for k,v in new.items() if k!='expected'}:raise ValueError('Probe reordered case identities')
        actual=new['expected'];prior=old['expected']
        if actual.get('bundle_sha256')!=logical:raise ValueError('Probe loaded wrong candidate')
        if old['kind']=='snapshot':
            expected=diagnostic.expected_snapshot(old['name'],prior,c,logical);normalized=diagnostic.normalized_snapshot(old['name'],actual)
            delta=diagnostic.differences(expected,normalized)
        else:
            expected=diagnostic.rules.transform_rows(prior,c);expected['bundle_sha256']=logical;expected['collections']['sources']+=copy.deepcopy(c['new_sources'])
            if old['request']['id']==diagnostic.rules.OWNER:expected['regional_model_length_scene']=diagnostic.rules.full_scene(c)
            delta=diagnostic.differences(expected,actual)
        checks.append({'case':{k:v for k,v in old.items() if k!='expected'},'difference_count':len(delta),'first_differences':delta[:50],
            'parent_response_sha256':index.sha(index.encode(prior)),'native_response_sha256':index.sha(index.encode(actual))})
    # Independently confirm representative batch wrappers equal the ordinary CLI.
    for i,args in [(0,['--atlas']),(4,['--object-view',OWNERS[1]])]:
        single=subprocess.run([str(cli),str(candidate),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=300)
        if json.loads(single.stdout)!=batch['cases'][i]['expected']:raise ValueError('Batch probe differs from ordinary CLI')
    report={'schema':'osw.chen-indian-sec-api-diagnostic-result.v1','status':'DIAGNOSTIC_COMPLETE_NO_ACCEPTANCE_RULE_CHANGES','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'request_sha256':sha(REQUEST),'preflight_sha256':sha(PREFLIGHT),'candidate_logical_sha256':logical,'checks':checks,'native_probe_elapsed_seconds':batch['elapsed_seconds'],'native_probe_cli_equivalence_checks':2,'native_probe_source_sha256':sha('rust/osw-query/examples/delivery_probe_v1.rs'),'production_rust_or_scientific_inputs_changed':False,'wasm_built':False,'installed':False,'full_goal_complete':False}
    write(OUT/'result.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':OUT.mkdir(exist_ok=True,parents=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')})
        raise
