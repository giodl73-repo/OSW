"""One cloud job: indexed matching engine, parity, then actual browser delivery."""
import gc
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import published_current_speed_delivery_v1 as delivery
import published_current_speed_statistics_v1 as speeds
import published_current_speed_source_index_v1 as source_index
import azores_2009_section_cases_v1 as previous_cases
from check_published_current_speeds_v1 import verify_case

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/published-current-speed-delivery-v1'
REQUEST='research/published-current-speed-delivery-request-v1.json'
PREFLIGHT='research/published-current-speed-delivery-preflight-v1.json'
WORKFLOW='.github/workflows/published-current-speed-delivery-v1.yml'


def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def run(args,**kwargs):return subprocess.run(args,cwd=ROOT,check=True,timeout=3600,**kwargs)


def controls(clean=True):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME')!='push'
            or os.environ.get('OSW_SPEED_DELIVERY_V1')!='1'):
        raise ValueError('Exact cloud delivery required before packet/index/browser access')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:
        raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('Single worker required: '+key)
    request=read(REQUEST)
    if (request.get('execute') is not True or request.get('workflow')!=WORKFLOW
            or request.get('preflight_sha256')!=sha(PREFLIGHT)
            or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0):
        raise ValueError('Scoped delivery request disabled or changed')
    for key in ['cloud_candidate_files_permitted','native_build_permitted','wasm_build_permitted','browser_permitted']:
        if request.get(key) is not True:raise ValueError('Delivery phase not enabled: '+key)
    for key in ['installation_permitted','source_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled: '+key)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:
        raise ValueError('Global scientific field processing must remain disabled')
    pref=read(PREFLIGHT);saved={} if clean else read(OUT/'engine.json')['generated_sha256']
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=saved.get(path,pin):raise ValueError('Frozen source changed: '+path)
    for path,row in pref['installed_files'].items():
        if sha(path)!=saved.get(path,row['sha256']):raise ValueError('Unexpected parent/candidate change: '+path)
    for path in pref['disabled_requests']:
        doc=read(path)
        if doc.get('execute',doc.get('execution_permitted')) is not False:
            raise ValueError('Another execution request enabled: '+path)
    delivery.scopes()
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    remote=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head!=remote or head!=os.environ['GITHUB_SHA']:raise ValueError('Exact current branch checkout required')
    if clean and subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain'],cwd=ROOT).strip():
        raise ValueError('Clean checkout required before assembly')
    return head,pref


def native(cli,payload,query,index=False):
    policy=read('research/eicc-reference-response-budgets-v1.json')
    limit=policy['scene_or_source_response_bytes'] if index or query.get('collection') in policy['main_collections_with_scene_budget'] else policy['scalar_response_bytes']
    p=run([str(cli)]+(['--index'] if index else [])+[str(payload),'-'],input=json.dumps(query).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if len(p.stdout)>limit or len(p.stderr)>32768:raise ValueError('Query response budget exceeded')
    result=json.loads(p.stdout)
    if result.get('ok') is not True:raise ValueError('Native query refused: '+str(result)[:1000])
    return result


def snapshots(mode,wasm,payload,wasm_sha,logical_sha):
    run(['node','--max-old-space-size=1536','analysis/check_eicc_snapshots_v3.mjs',mode,str(wasm),str(payload),str(OUT),wasm_sha,logical_sha],env=dict(os.environ,OSW_EICC_SNAPSHOTS_V3='1'))


def engine():
    head,pref=controls()
    from query_packet import read_bundle_bytes,write_packet,descriptors
    from south_java_catalog_engine_v1 import dependencies
    if OUT.exists():raise ValueError('Refuse to overwrite prior cloud evidence')
    if shutil.disk_usage(ROOT).free<4*1024**3:raise ValueError('At least4GiB cloud disk required')
    OUT.mkdir(parents=True)
    if sha(delivery.MANIFEST)!=delivery.PARENT_MANIFEST or sha(delivery.WASM)!=delivery.PARENT_WASM:
        raise ValueError('Exact installed engine required')
    parent_engine=read(delivery.MANIFEST)
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if delivery.sha(raw)!=speeds.PARENT or len(raw)!=190487048:raise ValueError('Exact installed logical bundle required')
    parent_path=OUT/'parent.json';parent_path.write_bytes(raw);del raw;gc.collect()
    snapshots('parent',ROOT/delivery.WASM,parent_path,delivery.PARENT_WASM,speeds.PARENT)
    parent=read(parent_path)
    child,generated,audit=delivery.assemble(parent,(ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    for name,rows in parent['collections'].items():
        actual=child['collections'][name]
        if name=='objects':
            actual=[dict(r) for r in actual]
            for row in actual:
                if row['id']==speeds.OWNER:row.pop('speed_statistic_ids')
        if actual!=rows:raise ValueError('Original collection changed: '+name)
    old_cases=previous_cases.main_cases(child['collections'])
    speed_cases=read('research/published-current-speed-query-cases-v1.json')['cases']
    candidate=OUT/'candidate.json';candidate.write_bytes(source_index.encode(child));del child,parent;gc.collect()
    packet=write_packet(ROOT/'almanac/query-data.json',candidate.read_bytes())
    for path,body in generated.items():(ROOT/path).write_bytes(body)
    del generated;gc.collect()
    write(OUT/'source-index-audit.json',audit)
    inventory=delivery.compile_inventory(read('research/published-current-speed-engine-compile-inventory-raw-v1.json'),catalog_sha=sha('almanac/index-catalog.json'),logical_sha=packet['logical_sha256'])
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in inventory[group].items():
            if sha(path)!=pin:raise ValueError('Verified compiler source changed: '+path)
    write(OUT/'compile-inventory.json',inventory)
    index_path=OUT/'index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as src,index_path.open('xb') as dst:shutil.copyfileobj(src,dst,1048576)
    catalog=read('almanac/index-catalog.json')
    if sha(index_path)!=catalog['bundle_sha256'] or index_path.stat().st_size!=catalog['bundle_bytes']:raise ValueError('New logical index identity differs')
    env=dict(os.environ,CARGO_TARGET_DIR=str(OUT/'build'),CARGO_INCREMENTAL='0')
    cargo=['cargo','+1.95.0'];manifest=['--offline','--locked','--manifest-path','rust/osw-query/Cargo.toml']
    run(cargo+['build']+manifest+['--bin','osw-query-cli'],env=env)
    with (OUT/'rust-tests.txt').open('wb') as stream:run(cargo+['test']+manifest+['--lib','--','--test-threads=1'],env=env,stdout=stream,stderr=subprocess.STDOUT)
    if not re.search(rb'test result: ok\. 214 passed; 0 failed;', (OUT/'rust-tests.txt').read_bytes()):raise ValueError('Complete214-test suite did not pass')
    cli=OUT/'build/debug/osw-query-cli';fixtures={'main':[],'index':[]}
    for query,expected in old_cases:
        response=native(cli,candidate,query);previous_cases.verify_response(query,expected,response);fixtures['main'].append({'request':query,'expected':response})
    for case in speed_cases:
        response=native(cli,candidate,case['query']);verify_case(case,response);fixtures['main'].append({'request':case['query'],'expected':response})
    for path in previous_cases.index_cases()+[speeds.SOURCE]:
        query={'document':path,'pointer':'','limit':500,'offset':0};response=native(cli,index_path,query,True)
        if response['source_sha256']!=sha(path) or {r['source_key']:r['record'] for r in response['rows']}!=read(path):raise ValueError('Complete indexed document reconstruction differs: '+path)
        fixtures['index'].append({'request':query,'expected':response})
    if len(fixtures['main'])!=33 or len(fixtures['index'])!=13:raise ValueError('Declared parity coverage differs')
    run(cargo+['rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib','--manifest-path','rust/osw-query/Cargo.toml'],env=env)
    wasm=OUT/'build/wasm32-unknown-unknown/release/osw_query.wasm';wasm_sha=sha(wasm)
    proof=dependencies(wasm.with_suffix('.d').read_text(),ROOT,inventory);write(OUT/'dependency-proof.json',proof)
    for mode,payload in [('main',candidate),('index',index_path)]:
        metadata=OUT/(mode+'-metadata.json')
        with metadata.open('wb') as stream:run([str(cli)]+(['--index'] if mode=='index' else [])+[str(payload)],stdout=stream)
        fixture=OUT/(mode+'-fixtures.json');write(fixture,{'payload_sha256':sha(payload),'queries':fixtures[mode]})
        run(['node','--max-old-space-size=1536','analysis/check_published_current_speed_delivery_parity_v1.mjs',mode,str(wasm),str(payload),str(fixture),str(metadata),str(OUT/(mode+'-parity.json')),wasm_sha])
    for name in ['atlas','seasons']:
        path=OUT/(name+'-native.json')
        with path.open('wb') as stream:run([str(cli),str(candidate),'--'+name],stdout=stream)
        old,new=read(OUT/('parent-'+name+'.json')),read(path)
        if new.get('ok') is not True or set(new)!=set(old)|{'published_speed_scenes'}:raise ValueError('Complete snapshot shape differs')
        if len(new['published_speed_scenes']['east-african-coastal']['records'])!=15:raise ValueError('Snapshot speed records missing')
        for key in set(old)-{'bundle_sha256'}:
            if new[key]!=old[key]:raise ValueError('Prior API field changed: '+name+'/'+key)
        del old,new;gc.collect()
    snapshots('candidate',wasm,candidate,wasm_sha,packet['logical_sha256'])
    changed,added,contracts=delivery.scopes();parts={'almanac/'+r['path'] for r in descriptors(packet)}
    paths=delivery.GENERATED|parts|set(changed)|set(added)|set(contracts)|set(inventory['rust_source_sha256'])|set(inventory['compile_time_data_sha256'])
    paths|={p for p in pref['input_sha256'] if p not in parent_engine['sha256']}|{PREFLIGHT}
    replacements={p:sha(p) for p in paths}
    compiler=subprocess.check_output(['rustc','+1.95.0','--version']).decode().strip()
    overlay=delivery.engine_manifest(parent_engine,replacements,logical_sha=packet['logical_sha256'],wasm_sha=wasm_sha,source_commit=head,compiler=compiler,inventory=inventory,proof=proof,changed_sources=changed,added_sources=added,contracts=contracts)
    shutil.copyfile(wasm,ROOT/delivery.WASM);write(Path(delivery.MANIFEST),overlay)
    paths=delivery.GENERATED|parts|{delivery.WASM,delivery.MANIFEST};hashes={p:sha(p) for p in paths}
    for path in paths:
        dst=OUT/'artifact'/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dst)
    write(OUT/'engine.json',{'status':'PASS','source_commit':head,'stage':'engine_verified','logical_sha256':packet['logical_sha256'],'logical_bytes':packet['logical_byte_length'],'wasm_sha256':wasm_sha,'compiler':compiler,'generated_sha256':hashes,'source_index_audit':audit,'rust_tests_passed':214,'main_query_comparisons':33,'source_query_comparisons':13,'complete_api_comparisons':2,'browser_verified':False,'installed':False})


def browser():
    head,_=controls(False);saved=read(OUT/'engine.json')
    if saved.get('status')!='PASS' or saved['source_commit']!=head:raise ValueError('Verified engine required')
    for path,pin in saved['generated_sha256'].items():
        if sha(path)!=pin:raise ValueError('Generated candidate changed')
    from check_published_current_speed_browser_v1 import browser_review
    write(OUT/'browser.json',browser_review(ROOT,OUT))
    for path,pin in saved['generated_sha256'].items():
        if sha(path)!=pin:raise ValueError('Browser modified candidate')
    write(OUT/'result.json',{**saved,'browser_verified':True,'visual_review_complete':False,'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'installed':False,'new_length_records':0,'new_width_records':0,'full_goal_complete':False})


if __name__=='__main__':
    action=sys.argv[1] if len(sys.argv)==2 else ''
    try:
        if action=='preflight':controls()
        elif action=='engine':engine()
        elif action=='browser':browser()
        else:raise ValueError('Use preflight, engine or browser')
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':write(OUT/(action+'-failure.json'),{'status':'FAIL','stage':action,'error':str(error)[:4000],'installed':False})
        raise
