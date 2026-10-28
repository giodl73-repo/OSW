"""One cloud build/parity/browser sequence; never installs its candidate."""
import copy
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
import satellite_core_width_delivery_v1 as delivery
import published_satellite_core_widths_v1 as core
import published_satellite_core_width_index_v1 as index
import satellite_core_width_cases_v1 as cases
import published_seasonal_core_velocities_v1 as velocity
import published_current_speed_statistics_v1 as pemba
import azores_2009_section_cases_v1 as previous_cases
from check_published_current_speeds_v1 import verify_case

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/satellite-core-width-delivery-v1'
REQUEST='research/satellite-core-width-delivery-request-v1.json'
PREFLIGHT='research/satellite-core-width-delivery-preflight-v3.json'
WORKFLOW='.github/workflows/satellite-core-width-delivery-v1.yml'
CONTRACT='research/atlantic-ax08-core-velocity-query-contract-v1.json'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def run(args,**kwargs):return subprocess.run(args,cwd=ROOT,check=True,timeout=3600,**kwargs)


def controls(clean=True):
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('GITHUB_EVENT_NAME')!='push' or os.environ.get('OSW_SATELLITE_CORE_WIDTH_DELIVERY_V1')!='1':raise ValueError('Exact cloud delivery required before installed artifact access')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required: '+key)
    request=read(REQUEST)
    if request.get('execute') is not True or request.get('workflow')!=WORKFLOW or request.get('preflight_sha256')!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Scoped cloud request disabled or changed')
    for key in ['cloud_candidate_files_permitted','native_build_permitted','wasm_build_permitted','browser_permitted']:
        if request.get(key) is not True:raise ValueError('Verification permission missing: '+key)
    for key in ['installation_permitted','source_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled: '+key)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Scientific field processing must remain disabled')
    pref=read(PREFLIGHT);generated={} if clean else read(OUT/'engine.json')['generated_sha256']
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=generated.get(path,pin):raise ValueError('Frozen input differs: '+path)
    for path,row in pref['installed_files'].items():
        if sha(path)!=generated.get(path,row['sha256']):raise ValueError('Installed/candidate artifact differs: '+path)
    for path in pref['disabled_requests']:
        doc=read(path)
        if doc.get('execute',doc.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+path)
    delivery.scopes()
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    remote=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head!=remote or head!=os.environ['GITHUB_SHA']:raise ValueError('Exact current branch checkout required')
    if clean and subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean checkout required')
    return head,pref


def native(cli,payload,query,source=False):
    limit=2097152 if source or query.get('collection') in ['objects','widths','reference_routes'] else 131072
    p=subprocess.run([str(cli)]+(['--index'] if source else [])+[str(payload),'-'],cwd=ROOT,check=False,timeout=3600,input=json.dumps(query).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if len(p.stdout)>limit or len(p.stderr)>32768:raise ValueError('Response budget exceeded')
    if p.returncode:
        failure={'status':'FAIL','request':query,'returncode':p.returncode,'stdout':p.stdout.decode('utf8',errors='replace'),'stderr':p.stderr.decode('utf8',errors='replace'),'installed':False}
        write(OUT/'native-failure.json',failure)
        raise ValueError('Native candidate refused: '+(failure['stderr'] or failure['stdout'])[:2000])
    result=json.loads(p.stdout)
    if result.get('ok') is not True:raise ValueError('Native query refused: '+str(result)[:1000])
    return result


def snapshots(mode,wasm,payload,wasm_sha,logical_sha):
    run(['node','--max-old-space-size=1536','analysis/check_satellite_core_width_snapshots_v1.mjs',mode,str(wasm),str(payload),str(OUT),wasm_sha,logical_sha],env=dict(os.environ,OSW_SATELLITE_CORE_WIDTH_SNAPSHOTS_V1='1'))


def parity(mode,wasm,payload,fixture,output,wasm_sha):
    run(['node','--max-old-space-size=1536','analysis/check_satellite_core_width_parity_v1.mjs',mode,str(wasm),str(payload),str(fixture),str(OUT/(mode+'-metadata.json')),str(output),wasm_sha])


def engine():
    head,pref=controls()
    from query_packet import read_bundle_bytes,write_packet,descriptors
    from south_java_catalog_engine_v1 import dependencies
    if OUT.exists():raise ValueError('Refuse to overwrite cloud evidence')
    if shutil.disk_usage(ROOT).free<4*1024**3:raise ValueError('At least4GiB free disk required')
    OUT.mkdir(parents=True)
    if sha(delivery.MANIFEST)!=delivery.PARENT_MANIFEST or sha(delivery.WASM)!=delivery.PARENT_WASM:raise ValueError('Installed engine identity differs')
    parent_engine=read(delivery.MANIFEST);raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if delivery.digest(raw)!=core.PARENT or len(raw)!=190528544:raise ValueError('Installed logical parent differs')
    parent_path=OUT/'parent.json';parent_path.write_bytes(raw);del raw;gc.collect()
    snapshots('parent',ROOT/delivery.WASM,parent_path,delivery.PARENT_WASM,core.PARENT)
    speed_queries=[{'collection':pemba.COLLECTION,'limit':100},{'collection':velocity.COLLECTION,'limit':100}]
    fixture=OUT/'parent-speeds-fixture.json';write(fixture,{'payload_sha256':core.PARENT,'queries':[{'request':q} for q in speed_queries]})
    parity('parent',ROOT/delivery.WASM,parent_path,fixture,OUT/'parent-speeds.json',delivery.PARENT_WASM)
    parent=read(parent_path);child=core.prepare(parent,logical_parent_sha256=core.PARENT)
    generated,audit=index.source_index((ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    child=index.attach(child,generated,audit);delivery.verify_collections(parent,child)
    old_cases=previous_cases.main_cases(child['collections']);width_cases=cases.main_cases(child['collections'])
    candidate=OUT/'candidate.json';candidate.write_bytes(index.encode(child));del child,parent;gc.collect()
    packet=write_packet(ROOT/'almanac/query-data.json',candidate.read_bytes())
    for path,body in generated.items():(ROOT/path).write_bytes(body)
    del generated;gc.collect();write(OUT/'source-index-audit.json',audit)
    scope=delivery.scopes();inventory=delivery.compile_inventory(read(delivery.INVENTORY),scope,catalog_sha=sha('almanac/index-catalog.json'),logical_sha=packet['logical_sha256'])
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in inventory[group].items():
            if sha(path)!=pin:raise ValueError('Compiler input differs: '+path)
    write(OUT/'compile-inventory.json',inventory);index_path=OUT/'index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as src,index_path.open('xb') as dst:shutil.copyfileobj(src,dst,1048576)
    catalog=read('almanac/index-catalog.json')
    if sha(index_path)!=catalog['bundle_sha256'] or index_path.stat().st_size!=catalog['bundle_bytes']:raise ValueError('Index identity differs')
    env=dict(os.environ,CARGO_TARGET_DIR=str(OUT/'build'),CARGO_INCREMENTAL='0');cargo=['cargo','+1.95.0'];locked=['--offline','--locked','--manifest-path','rust/osw-query/Cargo.toml']
    run(cargo+['build']+locked+['--bin','osw-query-cli'],env=env)
    with (OUT/'rust-tests.txt').open('wb') as stream:run(cargo+['test']+locked+['--lib','--','--test-threads=1'],env=env,stdout=stream,stderr=subprocess.STDOUT)
    if not re.search(rb'test result: ok\. 223 passed; 0 failed;',(OUT/'rust-tests.txt').read_bytes()):raise ValueError('Complete223-test suite did not pass')
    cli=OUT/'build/debug/osw-query-cli';fixtures={'main':[],'index':[]}
    for query,expected in old_cases:
        response=native(cli,candidate,query);previous_cases.verify_response(query,expected,response);fixtures['main'].append({'request':query,'expected':response})
    for case in read('research/published-current-speed-query-cases-v1.json')['cases']:
        response=native(cli,candidate,case['query']);verify_case(case,response);fixtures['main'].append({'request':case['query'],'expected':response})
    for query,expected in zip(speed_queries,read(OUT/'parent-speeds.json')['responses']):
        if native(cli,candidate,query)!=expected:raise ValueError('Installed speed whole response changed')
    expected_rows={r['id']:r for r in velocity.records()}
    for case in read(CONTRACT)['cases']:
        query=case['request']
        if query['collection']==pemba.COLLECTION:continue
        response=native(cli,candidate,query);scene=response['chart_scene'];count=0 if scene is None else len(scene['records'])
        if response['total']!=case['expected_total'] or count!=case['expected_scene_records'] or response['map_scene'] is not None:raise ValueError('Prior velocity total or scene differs')
        if scene is not None and scene['kind']!='published_seasonal_core_velocities':raise ValueError('Wrong prior velocity scene')
        if 'expected_row_count' in case and len(response['rows'])!=case['expected_row_count']:raise ValueError('Prior pagination differs')
        if 'expected_record_ids' in case and [r['id'] for r in response['rows']]!=case['expected_record_ids']:raise ValueError('Prior record selection differs')
        if any(row!=expected_rows[row['id']] for row in response['rows']):raise ValueError('Prior velocity projection differs')
        fixtures['main'].append({'request':query,'expected':response})
    for query,expected in width_cases:
        response=native(cli,candidate,query);cases.verify_response(query,expected,response);fixtures['main'].append({'request':query,'expected':response})
    for path in previous_cases.index_cases()+[pemba.SOURCE,velocity.SOURCE,core.SOURCE]:
        query={'document':path,'pointer':'','limit':500,'offset':0};response=native(cli,index_path,query,True)
        if response['source_sha256']!=sha(path) or {r['source_key']:r['record'] for r in response['rows']}!=read(path):raise ValueError('Indexed root differs: '+path)
        fixtures['index'].append({'request':query,'expected':response})
    for path in [velocity.SOURCE,core.SOURCE]:
        for i,original in enumerate(read(path)['records']):
            query={'document':path,'pointer':f'/records/{i}','limit':100};response=native(cli,index_path,query,True)
            if {r['source_key']:r['record'] for r in response['rows']}!=original:raise ValueError('Source pointer differs')
            fixtures['index'].append({'request':query,'expected':response})
    if len(fixtures['main'])!=53 or len(fixtures['index'])!=23:raise ValueError('Parity case inventory differs')
    run(cargo+['rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib','--manifest-path','rust/osw-query/Cargo.toml'],env=env)
    wasm=OUT/'build/wasm32-unknown-unknown/release/osw_query.wasm';wasm_sha=sha(wasm);proof=dependencies(wasm.with_suffix('.d').read_text(),ROOT,inventory);write(OUT/'dependency-proof.json',proof)
    for mode,payload in [('main',candidate),('index',index_path)]:
        with (OUT/(mode+'-metadata.json')).open('wb') as stream:run([str(cli)]+(['--index'] if mode=='index' else [])+[str(payload)],stdout=stream)
        fixture=OUT/(mode+'-fixtures.json');write(fixture,{'payload_sha256':sha(payload),'queries':fixtures[mode]});parity(mode,wasm,payload,fixture,OUT/(mode+'-parity.json'),wasm_sha)
    for name in ['atlas','seasons','dashboard']:
        path=OUT/(name+'-native.json')
        with path.open('wb') as stream:run([str(cli),str(candidate),'--'+name],stdout=stream)
        delivery.verify_snapshot(name,read(OUT/('parent-'+name+'.json')),read(path));gc.collect()
    snapshots('candidate',wasm,candidate,wasm_sha,packet['logical_sha256'])
    parts={'almanac/'+r['path'] for r in descriptors(packet)};generated_paths=index.INDEX|{'almanac/query-data.json'}|parts
    paths=generated_paths|set(scope['runtime_source_changes'])|set(scope['added_source_sha256'])|set(scope['source_dependencies_sha256'])|set(inventory['rust_source_sha256'])|set(inventory['compile_time_data_sha256'])|{p for p in pref['input_sha256'] if p not in parent_engine['sha256']}|{PREFLIGHT}
    replacements={p:sha(p) for p in paths};compiler=subprocess.check_output(['rustc','+1.95.0','--version']).decode().strip()
    overlay=delivery.engine_manifest(parent_engine,replacements,scope,generated_paths=generated_paths,logical_sha=packet['logical_sha256'],wasm_sha=wasm_sha,source_commit=head,compiler=compiler,inventory=inventory,proof=proof)
    shutil.copyfile(wasm,ROOT/delivery.WASM);write(delivery.MANIFEST,overlay);generated_paths|={delivery.WASM,delivery.MANIFEST};hashes={p:sha(p) for p in generated_paths}
    for path in generated_paths:
        dst=OUT/'artifact'/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dst)
    write(OUT/'engine.json',{'status':'PASS','source_commit':head,'logical_sha256':packet['logical_sha256'],'logical_bytes':packet['logical_byte_length'],'wasm_sha256':wasm_sha,'compiler':compiler,'generated_sha256':hashes,'source_index_audit':audit,'rust_tests_passed':223,'main_query_comparisons':53,'source_query_comparisons':23,'complete_api_comparisons':3,'prior_speed_whole_responses_preserved':2,'new_width_records':2,'new_width_samples':0,'new_length_records':0,'browser_verified':False,'installed':False})


def browser():
    head,_=controls(False);saved=read(OUT/'engine.json')
    if saved.get('status')!='PASS' or saved['source_commit']!=head:raise ValueError('Verified engine required')
    from check_satellite_core_width_browser_v2 import browser_review
    write(OUT/'browser.json',browser_review(ROOT,OUT))
    for path,pin in saved['generated_sha256'].items():
        if sha(path)!=pin:raise ValueError('Browser modified candidate')
    write(OUT/'result.json',{**saved,'browser_verified':True,'visual_review_complete':False,'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'installed':False,'full_goal_complete':False})


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
