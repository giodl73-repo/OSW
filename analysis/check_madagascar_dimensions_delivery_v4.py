"""One sequenced cloud build/query/API/browser verification; never installs."""
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
import check_eacc_cited_width_delivery_v3 as prior
import madagascar_dimensions_query_v1 as query
import wicc_winter_reference_query_v1 as wicc_query
import madagascar_dimensions_runtime_v4 as runtime
import madagascar_dimensions_index_v4 as index
import madagascar_dimensions_delivery_v4 as delivery
import wicc_winter_reference_cases_v1 as cases
import eac_mean_core_cases_v1 as core_cases
import madagascar_dimensions_cases_v1 as dimension_cases

ROOT=query.ROOT
OUT=ROOT/'.pytest_cache/madagascar-dimensions-delivery-v4'
REQUEST='research/madagascar-dimensions-delivery-request-v4.json'
PREFLIGHT='research/madagascar-dimensions-delivery-preflight-v4.json'
WORKFLOW='.github/workflows/madagascar-dimensions-delivery-v4.yml'
prior.OUT=OUT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')


def run(args,**kwargs):
    return subprocess.run(args,cwd=ROOT,check=True,timeout=3600,**kwargs)


def controls(clean=True):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME')!='push'
            or os.environ.get('OSW_MADAGASCAR_DIMENSIONS_DELIVERY_V4')!='1'):
        raise ValueError('Exact scoped cloud delivery required before payload access')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:
        raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('Single worker required: '+key)
    request=read(ROOT/REQUEST)
    if request.get('execute') is not True or request.get('workflow')!=WORKFLOW or request.get('preflight_sha256')!=sha(ROOT/PREFLIGHT):
        raise ValueError('Disabled or changed request')
    if request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Changed resource scope')
    for key in ['cloud_candidate_files_permitted','native_build_permitted','wasm_build_permitted','browser_permitted']:
        if request.get(key) is not True:raise ValueError('Missing scoped permission: '+key)
    for key in ['installation_permitted','source_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled: '+key)
    if read(ROOT/'research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:
        raise ValueError('Original field processing must remain disabled')
    pref=read(ROOT/PREFLIGHT);generated={} if clean else read(OUT/'engine.json')['generated_sha256']
    for path,pin in pref['input_sha256'].items():
        if sha(ROOT/path)!=generated.get(path,pin):raise ValueError('Frozen input differs: '+path)
    for path,row in pref['installed_files'].items():
        if sha(ROOT/path)!=generated.get(path,row['sha256']):raise ValueError('Installed/candidate file differs: '+path)
    for path in pref['disabled_requests']:
        r=read(ROOT/path)
        if r.get('execute',r.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+path)
    delivery.scopes()
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    remote=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head!=remote or head!=os.environ['GITHUB_SHA']:raise ValueError('Stale source checkout refused')
    if clean and subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain'],cwd=ROOT).strip():raise ValueError('Clean exact checkout required')
    return head,pref


def parity(mode,wasm,payload,fixture,output,wasm_sha):
    run(['node','--max-old-space-size=1536','analysis/check_madagascar_dimensions_parity_v4.mjs',mode,str(wasm),str(payload),str(fixture),str(OUT/(mode+'-metadata.json')),str(output),wasm_sha])


def snapshots(mode,wasm,payload,wasm_sha,logical_sha):
    run(['node','--max-old-space-size=1536','analysis/check_madagascar_dimensions_snapshots_v4.mjs',mode,str(wasm),str(payload),str(OUT),wasm_sha,logical_sha])


def engine():
    head,pref=controls()
    from query_packet import read_bundle_bytes,write_packet,descriptors
    from south_java_catalog_engine_v1 import dependencies
    if OUT.exists():raise ValueError('Refuse to overwrite execution evidence')
    if shutil.disk_usage(ROOT).free<4*1024**3:raise ValueError('At least4GiB free disk required')
    OUT.mkdir(parents=True)
    if sha(ROOT/delivery.MANIFEST)!=delivery.PARENT_MANIFEST or sha(ROOT/delivery.WASM)!=delivery.PARENT_WASM:
        raise ValueError('Installed engine identity differs')
    parent_engine=read(ROOT/delivery.MANIFEST);raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if delivery.sha(raw)!=query.PARENT or len(raw)!=190579739:raise ValueError('Installed logical parent differs')
    parent_path=OUT/'parent.json';parent_path.write_bytes(raw);del raw;gc.collect()
    snapshots('parent',ROOT/delivery.WASM,parent_path,delivery.PARENT_WASM,query.PARENT)
    speed_queries=[{'collection':prior.pemba.COLLECTION,'limit':100},{'collection':prior.velocity.COLLECTION,'limit':100}]
    speed_fixture=OUT/'parent-speeds-fixture.json'
    write(speed_fixture,{'payload_sha256':query.PARENT,'queries':[{'request':q} for q in speed_queries]})
    parity('parent',ROOT/delivery.WASM,parent_path,speed_fixture,OUT/'parent-speeds.json',delivery.PARENT_WASM)
    parent=read(parent_path);child=dict(parent);child['collections']=dict(parent['collections']);child['manifest']=copy.deepcopy(parent['manifest'])
    query.prepare(child['collections'],child['manifest'],query.build_contract(),parent_logical_sha256=query.PARENT)
    generated,audit=index.source_index((ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    child=index.attach(child,generated,audit);delivery.verify_collections(parent,child)
    old_cases=cases.adapt(prior.cases.adapt_legacy_cases(prior.wicc_cases.adapt_legacy_cases(prior.satellite_cases.adapt_legacy_cases(prior.previous_cases.main_cases(child['collections'])))))
    satellite_cases=prior.satellite_cases.main_cases(child['collections']);width_cases=prior.wicc_cases.main_cases(child['collections']);constraint_cases=prior.cases.main_cases(child['collections']);route_cases=cases.main_cases(child['collections']);mean_core_cases=core_cases.main_cases(child['collections']);new_cases=dimension_cases.main_cases(child['collections'])
    candidate=OUT/'candidate.json';candidate.write_bytes(index.encode(child));del child,parent;gc.collect()
    packet=write_packet(ROOT/'almanac/query-data.json',candidate.read_bytes())
    for path,body in generated.items():(ROOT/path).write_bytes(body)
    del generated;gc.collect();write(OUT/'source-index-audit.json',audit)
    scope=delivery.scopes();inventory=delivery.inventory(scope,logical_sha=packet['logical_sha256'],catalog_sha=sha(ROOT/'almanac/index-catalog.json'))
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in inventory[group].items():
            if sha(ROOT/path)!=pin:raise ValueError('Compiler input differs: '+path)
    write(OUT/'compile-inventory.json',inventory);index_path=OUT/'index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as src,index_path.open('xb') as dst:shutil.copyfileobj(src,dst,1048576)
    catalog=read(ROOT/'almanac/index-catalog.json')
    if sha(index_path)!=catalog['bundle_sha256'] or index_path.stat().st_size!=catalog['bundle_bytes']:raise ValueError('Index identity differs')
    env=dict(os.environ,CARGO_TARGET_DIR=str(OUT/'build'),CARGO_INCREMENTAL='0');cargo=['cargo','+1.95.0'];locked=['--offline','--locked','--manifest-path','rust/osw-query/Cargo.toml']
    run(cargo+['build']+locked+['--bin','osw-query-cli'],env=env)
    with (OUT/'rust-tests.txt').open('wb') as stream:run(cargo+['test']+locked+['--lib','--','--test-threads=1'],env=env,stdout=stream,stderr=subprocess.STDOUT)
    if not re.search(rb'test result: ok\. 256 passed; 0 failed;',(OUT/'rust-tests.txt').read_bytes()):raise ValueError('Complete256-test library suite did not pass')
    cli=OUT/'build/debug/osw-query-cli';fixtures={'main':[],'index':[]}
    def retain(request,response,source=False):fixtures['index' if source else 'main'].append({'request':request,'expected':response})
    for request,expected in old_cases:
        response=prior.native(cli,candidate,request);prior.previous_cases.verify_response(request,expected,response);retain(request,response)
    for case in read(ROOT/'research/published-current-speed-query-cases-v1.json')['cases']:
        response=prior.native(cli,candidate,case['query']);prior.verify_case(case,response);retain(case['query'],response)
    for request,expected in zip(speed_queries,read(OUT/'parent-speeds.json')['responses']):
        if prior.native(cli,candidate,request)!=expected:raise ValueError('Prior speed whole response changed')
    expected_rows={r['id']:r for r in prior.velocity.records()}
    for case in read(ROOT/prior.CONTRACT)['cases']:
        request=case['request']
        if request['collection']==prior.pemba.COLLECTION:continue
        response=prior.native(cli,candidate,request);scene=response['chart_scene'];count=0 if scene is None else len(scene['records'])
        if response['total']!=case['expected_total'] or count!=case['expected_scene_records'] or response['map_scene'] is not None:raise ValueError('Prior velocity support differs')
        if scene is not None and scene['kind']!='published_seasonal_core_velocities':raise ValueError('Wrong velocity scene')
        if 'expected_row_count' in case and len(response['rows'])!=case['expected_row_count']:raise ValueError('Prior velocity pagination differs')
        if 'expected_record_ids' in case and [r['id'] for r in response['rows']]!=case['expected_record_ids']:raise ValueError('Prior velocity IDs differ')
        if any(row!=expected_rows[row['id']] for row in response['rows']):raise ValueError('Prior velocity rows differ')
        retain(request,response)
    for group,checker in [(satellite_cases,prior.satellite_cases.verify_response),(width_cases,prior.wicc_cases.verify_response),
                           (constraint_cases,prior.cases.verify_response),(route_cases,cases.verify),(mean_core_cases,core_cases.verify),(new_cases,dimension_cases.verify)]:
        for request,expected in group:
            response=prior.native(cli,candidate,request);checker(request,expected,response);retain(request,response)
    paths=prior.previous_cases.index_cases()+[prior.pemba.SOURCE,prior.velocity.SOURCE,prior.satellite.SOURCE,prior.wicc.SOURCE,prior.core.SOURCE,wicc_query.CANDIDATE,core_cases.query.facts.FACTS,query.source.FACTS]
    for path in paths:
        request={'document':path,'pointer':'','limit':500,'offset':0};response=prior.native(cli,index_path,request,True)
        if response['source_sha256']!=sha(ROOT/path) or {r['source_key']:r['record'] for r in response['rows']}!=read(ROOT/path):raise ValueError('Source root differs: '+path)
        retain(request,response,True)
    for path in [prior.velocity.SOURCE,prior.satellite.SOURCE,prior.wicc.SOURCE,prior.core.SOURCE]:
        for i,original in enumerate(read(ROOT/path)['records']):
            request={'document':path,'pointer':f'/records/{i}','limit':100};response=prior.native(cli,index_path,request,True)
            if {r['source_key']:r['record'] for r in response['rows']}!=original:raise ValueError('Source pointer differs')
            retain(request,response,True)
    request={'document':wicc_query.CANDIDATE,'pointer':'/scenarios/0','limit':100};response=prior.native(cli,index_path,request,True)
    if {r['source_key']:r['record'] for r in response['rows']}!=read(ROOT/wicc_query.CANDIDATE)['scenarios'][0]:raise ValueError('Route source pointer differs')
    retain(request,response,True)
    for i,original in enumerate(read(ROOT/core_cases.query.facts.FACTS)['records']):
        request={'document':core_cases.query.facts.FACTS,'pointer':f'/records/{i}','limit':100};response=prior.native(cli,index_path,request,True)
        if {r['source_key']:r['record'] for r in response['rows']}!=original:raise ValueError('EAC source table pointer differs')
        retain(request,response,True)
    source_facts=read(ROOT/query.source.FACTS)
    pointers=[('/width_summary',source_facts['width_summary'])]+[(f'/event_index/{i}',row) for i,row in enumerate(source_facts['event_index'])]
    for pointer,original in pointers:
        request={'document':query.source.FACTS,'pointer':pointer,'limit':100};response=prior.native(cli,index_path,request,True)
        if {r['source_key']:r['record'] for r in response['rows']}!=original:raise ValueError('Madagascar source pointer differs')
        retain(request,response,True)
    if len(fixtures['main'])!=117 or len(fixtures['index'])!=45:raise ValueError('Whole-response case inventory differs')
    run(cargo+['rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib','--manifest-path','rust/osw-query/Cargo.toml'],env=env)
    wasm=OUT/'build/wasm32-unknown-unknown/release/osw_query.wasm';wasm_sha=sha(wasm)
    proof=dependencies(wasm.with_suffix('.d').read_text(),ROOT,inventory);write(OUT/'dependency-proof.json',proof)
    for mode,payload in [('main',candidate),('index',index_path)]:
        with (OUT/(mode+'-metadata.json')).open('wb') as stream:run([str(cli)]+(['--index'] if mode=='index' else [])+[str(payload)],stdout=stream)
        fixture=OUT/(mode+'-fixtures.json');write(fixture,{'payload_sha256':sha(payload),'queries':fixtures[mode]});parity(mode,wasm,payload,fixture,OUT/(mode+'-parity.json'),wasm_sha)
    for name in ['atlas','seasons','dashboard']:
        path=OUT/(name+'-native.json');prior.native_snapshot(cli,candidate,name,path)
        delivery.verify_snapshot(name,read(OUT/('parent-'+name+'.json')),read(path));gc.collect()
    snapshots('candidate',wasm,candidate,wasm_sha,packet['logical_sha256'])
    parts={'almanac/'+r['path'] for r in descriptors(packet)};generated_paths=index.INDEX|{'almanac/query-data.json'}|parts
    paths=generated_paths|set(scope['runtime_source_changes'])|set(scope['added_source_sha256'])|set(scope['source_dependencies_sha256'])|set(inventory['rust_source_sha256'])|set(inventory['compile_time_data_sha256'])|{p for p in pref['input_sha256'] if p not in parent_engine['sha256']}|{PREFLIGHT}
    replacements={p:sha(ROOT/p) for p in paths};compiler=subprocess.check_output(['rustc','+1.95.0','--version']).decode().strip()
    overlay=delivery.engine_manifest(parent_engine,replacements,scope,generated_paths=generated_paths,logical_sha=packet['logical_sha256'],wasm_sha=wasm_sha,source_commit=head,compiler=compiler,inventory=inventory,proof=proof)
    shutil.copyfile(wasm,ROOT/delivery.WASM);write(ROOT/delivery.MANIFEST,overlay);generated_paths|={delivery.WASM,delivery.MANIFEST};hashes={p:sha(ROOT/p) for p in generated_paths}
    for path in generated_paths:
        dst=OUT/'artifact'/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dst)
    shutil.copyfile(ROOT/delivery.MANIFEST,OUT/'engine-manifest.json')
    write(OUT/'engine.json',{'status':'PASS','source_commit':head,'logical_sha256':packet['logical_sha256'],'logical_bytes':packet['logical_byte_length'],'wasm_sha256':wasm_sha,'compiler':compiler,'generated_sha256':hashes,'source_index_audit':audit,'rust_tests_passed':256,'main_query_comparisons':117,'source_query_comparisons':45,'complete_api_comparisons':3,'prior_speed_whole_responses_preserved':2,'new_flow_event_references':8,'new_width_records':1,'new_length_records':0,'new_independent_observations':0,'browser_verified':False,'installed':False})


def browser():
    head,_=controls(False);saved=read(OUT/'engine.json')
    if saved.get('status')!='PASS' or saved['source_commit']!=head:raise ValueError('Verified matching engine required')
    from check_madagascar_dimensions_browser_v4 import browser_review
    write(OUT/'browser.json',browser_review(ROOT,OUT))
    for path,pin in saved['generated_sha256'].items():
        if sha(ROOT/path)!=pin:raise ValueError('Browser changed candidate bytes')
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
