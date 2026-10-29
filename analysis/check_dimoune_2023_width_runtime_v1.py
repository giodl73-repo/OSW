"""One-CPU cloud native/WASM gate plus exact installed-parent admission checks."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

import dimoune_2023_width_query_v1 as query

ROOT=query.ROOT
REQUEST='research/dimoune-2023-width-runtime-request-v1.json'
PREFLIGHT='research/dimoune-2023-width-runtime-preflight-v1.json'
OUT=ROOT/'.pytest_cache/dimoune-2023-width-runtime-v1'
WORK=ROOT/'.pytest_cache/dimoune-2023-width-runtime-work-v1'

def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def write(path,value):path.write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def require(value,message):
    if not value:raise ValueError(message)

def controls():
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
        and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
        and os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
        and os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('OSW_DIMOUNE_WIDTH_RUNTIME_V1')=='1',
        'Scoped cloud runtime gate only')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One CPU and nice15 required')
    for key in ('CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        require(os.environ.get(key)=='1','One worker required: '+key)
    request=read(REQUEST)
    require(request['execute'] is True and request['native_wasm_build_permitted'] is True
        and request['cloud_parent_packet_read_permitted'] is True,'Scoped gate disabled')
    for key in ('index_load_permitted','browser_automation_permitted','ocean_field_processing_permitted',
                'provider_download_permitted','installation_permitted','local_bulk_sync_permitted','main_update_permitted'):
        require(request[key] is False,'Unrelated permission enabled: '+key)
    require(request['max_cloud_jobs']==1 and request['max_local_heavy_jobs']==0,'Job bounds differ')
    require(sha(PREFLIGHT)==request['preflight_sha256'],'Preflight differs');pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(sha(path)==pin,'Input differs: '+path)
    for path in pref['disabled_requests']:
        r=read(path);require(r.get('execute',r.get('execution_permitted')) is False,'Other request enabled: '+path)
    require(read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False,'Broad phase enabled')
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],text=True,timeout=55).strip()
    require(git('rev-parse','HEAD')==os.environ['GITHUB_SHA'] and not git('status','--porcelain'),'Exact clean checkout required')
    require(git('ls-remote','origin','refs/heads/main').split()[0]=='19148702de6433253dbf412a0a28c0cb4f8e409e','Main moved')
    require(git('ls-remote','origin','refs/heads/codex/current-measurement-gaps').split()[0]==os.environ['GITHUB_SHA'],'Branch moved')
    for path,row in pref['installed_files'].items():
        require(git('rev-parse','HEAD:'+path)==row['git_blob_oid'] and int(git('cat-file','-s',row['git_blob_oid']))==row['bytes'],'Installed identity differs: '+path)
    for group in ('rust_source_sha256','compile_time_data_sha256','test_fixture_sha256'):
        for path,pin in pref['compile_inventory'][group].items():require(sha(path)==pin,'Compiler input differs: '+path)
    return pref

def requests(contract):
    result=[]
    def add(collection,field,value,**extra):
        result.append({'kind':'query','request':{'collection':collection,'filters':[{'field':field,'op':'eq','value':value}],'limit':100,**extra}})
    for owner in query.OWNERS:
        add('widths','current_id',owner.removeprefix('current:'))
        add('widths','current_id',owner.removeprefix('current:'),limit=1,offset=1)
        result.append({'kind':'object','request':{'id':owner}})
    for width in contract['width_records']:add('widths','id',width['id'])
    add('widths','current_id','south-equatorial');add('sources','id',contract['new_source']['id'])
    result.extend({'kind':'snapshot','name':name} for name in ('atlas','seasons','dashboard'))
    return result

def run():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    result={'status':'STARTED','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
        'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'installed':False,'full_goal_complete':False}
    env=dict(os.environ,CARGO_TARGET_DIR=str(WORK/'build'),CARGO_INCREMENTAL='0')
    def command(args,log):
        with (OUT/log).open('wb') as output:
            subprocess.run(args,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=2400)
    try:
        command(['python','-m','unittest','discover','-s','analysis','-p','test_dimoune_2023_width_query_v1.py','-v'],'admission-tests.txt')
        for name in ('dimoune_2023_width_ui_v1','azcc_onken_ui_v1','madagascar_dimensions_ui_v2'):
            command(['node','analysis/test_'+name+'.mjs'],name+'-tests.txt')
        command(['cargo','+1.95.0','test','--locked','--manifest-path','rust/osw-query/Cargo.toml','--lib','--','--test-threads=1'],'rust-tests.txt')
        require(b'test result: ok. 298 passed; 0 failed;' in (OUT/'rust-tests.txt').read_bytes(),'Expected 295 prior and three section-width tests')
        command(['cargo','+1.95.0','build','--offline','--locked','--manifest-path','rust/osw-query/Cargo.toml','--example','delivery_probe_v2'],'native-build.txt')
        from query_packet import read_bundle_bytes
        raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
        require(len(raw)==195248051 and hashlib.sha256(raw).hexdigest()==query.PARENT,'Exact installed logical packet required')
        parent=json.loads(raw);del raw
        contract=query.build_contract()
        collections,manifest=query.prepare(parent['collections'],parent['manifest'],contract,parent_logical_sha256=query.PARENT)
        for name,before in parent['collections'].items():
            expected=([*before,contract['new_source']] if name=='sources' else [*before,*contract['width_records']] if name=='widths'
                else [contract['final_objects'].get(r['id'],r) for r in before] if name=='objects' else before)
            require(collections[name]==expected,'Unrelated collection change: '+name)
        for key,value in parent['manifest'].items():
            if key!='input_sha256':require(manifest[key]==value,'Historical manifest namespace changed: '+key)
        candidate=WORK/'candidate.json';candidate.write_bytes(query.encoded({**parent,'collections':collections,'manifest':manifest}))
        cases=requests(contract)
        encoded_cases=[{**{k:v for k,v in item.items() if k in ('kind','name')},
            **({'request_json':json.dumps(item['request'],ensure_ascii=False)} if 'request' in item else {})} for item in cases]
        response=subprocess.run([str(WORK/'build/debug/examples/delivery_probe_v2'),'main',str(candidate)],
            input=json.dumps({'cases':encoded_cases}).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=1200)
        (OUT/'native-probe-stderr.txt').write_bytes(response.stderr)
        require(response.returncode==0,'Native complete-parent load/API failed; inspect native-probe-stderr.txt')
        batch=json.loads(response.stdout);require(len(batch['cases'])==len(cases),'Native API cases differ')
        checked=[]
        for requested,item in zip(encoded_cases,batch['cases']):
            require({k:v for k,v in item.items() if k!='raw_response_json'}==requested,'API case order differs')
            answer=json.loads(item['raw_response_json']);require(answer.get('ok') is True,'Native API failed')
            if requested['kind']=='query':
                req=json.loads(requested['request_json']);f=req['filters'][0]
                expected=sorted([r for r in collections[req['collection']] if r.get(f['field'])==f['value']],key=lambda r:r['id'])
                offset=req.get('offset',0)
                require(answer['total']==len(expected) and answer['rows']==expected[offset:offset+req['limit']],'Filtered query rows differ')
                if req['collection']=='widths' and expected:
                    scene=answer['chart_scene'];require(scene['kind']=='published_current_dimension_evidence','Mean-section scene missing')
                    require(scene['width_records']==expected,'Scene must retain all matches independent of pagination')
            elif requested['kind']=='object':
                owner=json.loads(requested['request_json'])['id'];expected=[r for r in collections['widths'] if query.owns(r,owner)]
                require(answer['current_dimension_evidence_scene']['width_records']==expected,'Current card widths differ')
            else:
                if requested['name'] in ('atlas','seasons'):
                    for owner in query.OWNERS:
                        require(answer['current_dimension_evidence_scenes'][owner.removeprefix('current:')]['width_records']
                            ==[r for r in collections['widths'] if query.owns(r,owner)],'Atlas/seasons evidence differs')
                elif requested['name']=='dashboard':
                    require(answer['entries'] and all(next(r for r in answer['entries'] if r['id']==owner)['capabilities']['scoped_width']
                        ==contract['final_objects'][owner]['capabilities']['scoped_width'] for owner in query.OWNERS),'Dashboard width coverage differs')
            checked.append({**requested,'response_sha256':hashlib.sha256(item['raw_response_json'].encode()).hexdigest()})
        write(OUT/'native-api-checks.json',{'checks':checked,'complete_parent_collections_preserved':len(collections),
            'candidate_sha256':sha(candidate),'candidate_bytes':candidate.stat().st_size})
        command(['cargo','+1.95.0','rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib',
            '--manifest-path','rust/osw-query/Cargo.toml','--crate-type','cdylib'],'wasm-build.txt')
        from south_java_catalog_engine_v1 import dependencies
        build=WORK/'build/wasm32-unknown-unknown/release'
        proof=dependencies((build/'osw_query.d').read_text(),ROOT,pref['compile_inventory'])
        require({'rust/osw-query/src/dimoune_section_widths.rs',query.FILE}<=set(proof['production_dependencies']),'New production inputs absent')
        write(OUT/'dependency-proof.json',proof);write(OUT/'compile-inventory.json',pref['compile_inventory'])
        result.update(status='PASS_NATIVE_TESTS_EXACT_PARENT_ADMISSION_APIS_AND_WASM_COMPILATION',rust_tests_passed=298,
            native_api_checks=len(checked),wasm_sha256=sha(build/'osw_query.wasm'),wasm_bytes=(build/'osw_query.wasm').stat().st_size,
            candidate_logical_sha256=sha(candidate),candidate_logical_bytes=candidate.stat().st_size,
            production_dependencies=proof['production_dependency_count'],source_index_extended=False,
            wasm_api_parity_verified=False,browser_verified=False)
    except Exception as error:
        result.update(status='FAILED',error=str(error));raise
    finally:write(OUT/'result.json',result)

if __name__=='__main__':run()
