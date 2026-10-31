"""Sequential cloud candidate admission, complete API comparisons and matching engine."""
import copy
import gc
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/pacific-nec-product-axis-delivery-request-v1.json'
PREFLIGHT='research/pacific-nec-product-axis-delivery-preflight-v1.json'
OUT=ROOT/'.pytest_cache/pacific-nec-product-axis-delivery-v1'
WORK=ROOT/'.pytest_cache/pacific-nec-product-axis-delivery-work-v1'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_PACIFIC_NEC_PRODUCT_DELIVERY_V1')!='1'):
        raise ValueError('Scoped cloud candidate delivery only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required: '+key)
    request=read(REQUEST)
    if request.get('schema')!='osw.pacific-nec-product-axis-delivery-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT):raise ValueError('Disabled or changed delivery request')
    for key in ['cloud_parent_packet_read_permitted','cloud_index_registration_permitted','cloud_candidate_files_permitted','native_build_permitted','wasm_build_permitted','cloud_engine_artifact_permitted']:
        if request.get(key) is not True:raise ValueError('Missing permission: '+key)
    for key in ['browser_permitted','installation_permitted','ocean_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled: '+key)
    pref=read(PREFLIGHT)
    for path,digest in pref['input_sha256'].items():
        if sha(path)!=digest:raise ValueError('Frozen input differs: '+path)
    for path,record in pref['installed_files'].items():
        if sha(path)!=record['sha256'] or (ROOT/path).stat().st_size!=record['bytes']:raise ValueError('Installed parent differs: '+path)
    for path in pref['disabled_requests']:
        old=read(path)
        if old.get('execute',old.get('execution_permitted')) is not False:raise ValueError('Other request enabled: '+path)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad phase enabled')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact source checkout required')
    return pref

def new_requests(contract):
    eq=lambda field,value:{'field':field,'op':'eq','value':value}
    result=[]
    def add(name,filters=(),limit=100,offset=0,sort=None):
        request={'collection':name,'filters':list(filters),'limit':limit,'offset':offset}
        if sort:request['sort']=sort
        result.append({'kind':'query','request':request})
    for name in contract['collections_added']:
        add(name);add(name,limit=1,offset=1);add(name,[eq('rank_eligible',True)]);add(name,[eq('entity_id','current:north-equatorial')])
    for series in contract['collections_added']['current_axis_series']:
        add('current_axis_readings',[eq('series_id',series['id'])],sort={'field':'month','direction':'desc'})
    for month in range(1,13):add('current_axis_readings',[eq('month',month)])
    for kind in ['core_method','anchor_grid','vertex_thinning']:add('current_axis_scenarios',[eq('scenario_kind',kind)])
    add('current_axis_scenarios',[eq('length_km',None)])
    add('current_axis_section_spans',[eq('width_km',None)])
    for source in contract['new_sources']:add('sources',[eq('id',source['id'])])
    for reading in contract['collections_added']['current_axis_readings'][::12]:add('current_axis_readings',[eq('id',reading['id'])])
    return result

def selected_rows(request,contract):
    from pacific_nec_product_axis_delivery_contract_v1 import same
    rows=[r for r in contract['collections_added'][request['collection']] if all(same(r.get(f['field']),f['value']) for f in request.get('filters',[]))]
    rows=sorted(rows,key=lambda r:r['id'])
    if 'sort' in request:rows.sort(key=lambda r:r[request['sort']['field']],reverse=request['sort']['direction']=='desc')
    return rows

def query_response(request,rows,scene=None):
    offset=request.get('offset',0);limit=request.get('limit',100)
    return {'ok':True,'engine':'rust-osw-query-v1','collection':request['collection'],'total':len(rows),'offset':offset,'limit':limit,
        'rows':rows[offset:offset+limit],'chart_scene':scene,'map_scene':None,'taxonomy_scope':None,'network_paths':None,'spatial_scope':None}

def run():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    import pacific_nec_product_axis_query_v1 as query
    import pacific_nec_product_axis_index_v1 as index
    import pacific_nec_product_axis_delivery_contract_v1 as rules
    from pacific_nec_product_axis_engine_v1 import engine_manifest
    from chen_indian_sec_native_batch_v2 import encode_case,case_key,run_batch
    from query_packet import read_bundle_bytes,write_packet
    from south_java_catalog_engine_v1 import dependencies
    contract=query.build_contract()
    if query.data.encoded(contract)!=(ROOT/query.FILE).read_bytes():raise ValueError('Frozen contract differs')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if hashlib.sha256(raw).hexdigest()!=query.PARENT or len(raw)!=191109635:raise ValueError('Exact parent logical packet required')
    parent_path=WORK/'parent.json';parent_path.write_bytes(raw);parent=json.loads(raw);del raw
    parent_index=WORK/'parent-index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as source,parent_index.open('xb') as target:shutil.copyfileobj(source,target,1048576)
    catalog=read('almanac/index-catalog.json')
    if sha(parent_index)!=catalog['bundle_sha256'] or parent_index.stat().st_size!=catalog['bundle_bytes']:raise ValueError('Parent index differs')
    requests={mode:[{'kind':r['kind'],**({'name':r['name']} if r['kind']=='snapshot' else {'request':json.loads(r['request_json'])})} for r in read('research/chen-indian-sec-delivery-run-v4/compare-'+mode+'.json')['checks']] for mode in ['main','index']}
    if [len(requests[k]) for k in ['main','index']]!=[234,86]:raise ValueError('Complete 320 historical API cases required')
    engine=read('almanac/query-engine.manifest.json')
    def parity(mode,wasm,payload,cases):
        rows=[encode_case(item) for item in cases];extra={}
        if mode.startswith('compare'):
            batch,cache=batches['index' if mode.endswith('index') else 'main']
            rows=[{**item,'raw_response_json':cache[case_key(item)]} for item in rows];extra={'metadata_json':batch['metadata_json']}
        fixture=WORK/(mode+'-fixture.json');write(fixture,{'payload_sha256':sha(payload),'cases':rows,**extra})
        output=(WORK if mode.startswith('capture') else OUT)/(mode+'.json')
        subprocess.run(['node','--max-old-space-size=1536','analysis/check_chen_indian_sec_parity_v2.mjs',mode,str(wasm),str(payload),str(fixture),str(output),sha(wasm)],check=True,timeout=1800)
        return read(output)
    baseline={mode:parity('capture-'+mode,ROOT/'almanac/query-engine.wasm',payload,requests[mode]) for mode,payload in [('main',parent_path),('index',parent_index)]}
    collections,manifest=query.prepare(parent['collections'],parent['manifest'],contract,parent_logical_sha256=query.PARENT)
    child={**parent,'collections':collections,'manifest':manifest};comparison=rules.verify_extension(parent,child,contract)
    generated,audit=index.source_index((ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    child=index.attach(child,generated,audit,contract);candidate=WORK/'candidate.json';candidate.write_bytes(index.encode(child));logical=sha(candidate)
    old_sources=copy.deepcopy(parent['collections']['sources'])
    del parent,child,collections,manifest;gc.collect()
    for path,raw in generated.items():(ROOT/path).write_bytes(raw)
    new_index=WORK/'index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as source,new_index.open('xb') as target:shutil.copyfileobj(source,target,1048576)
    if sha(new_index)!=read('almanac/index-catalog.json')['bundle_sha256']:raise ValueError('Candidate index differs')
    inventory=copy.deepcopy(pref['compile_inventory']);inventory['compile_time_data_sha256']['almanac/index-catalog.json']=sha('almanac/index-catalog.json')
    for group in ['rust_source_sha256','compile_time_data_sha256','test_fixture_sha256']:
        for path,digest in inventory[group].items():
            if sha(path)!=digest:raise ValueError('Compiler/fixture input differs: '+path)
    write(OUT/'compile-inventory.json',inventory)
    env=dict(os.environ,CARGO_TARGET_DIR=str(WORK/'build'),CARGO_INCREMENTAL='0')
    def cargo(args,log):
        with (OUT/log).open('wb') as stream:subprocess.run(['cargo','+1.95.0',*args,'--manifest-path','rust/osw-query/Cargo.toml'],env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=2400)
    cargo(['build','--locked','--bin','osw-query-cli','--example','delivery_probe_v2'],'native-build.txt')
    cargo(['test','--locked','--lib'],'rust-tests.txt')
    if b'test result: ok. 295 passed; 0 failed;' not in (OUT/'rust-tests.txt').read_bytes():raise ValueError('Expected 295 native regression tests')
    new_main=new_requests(contract)
    new_source=[{'kind':'query','request':{'document':path,'pointer':'','limit':500}} for path in index.DOCUMENTS]
    probe=WORK/'build/debug/examples/delivery_probe_v2'
    batches={mode:run_batch(probe,mode,payload,requests[mode]+new) for mode,payload,new in [('main',candidate,new_main),('index',new_index,new_source)]}
    def native(mode,item):return json.loads(batches[mode][1][case_key(encode_case(item))])
    for mode in ['main','index']:
        for saved in baseline[mode]['cases']:
            item={k:v for k,v in saved.items() if k in ('kind','name')}
            if 'request_json' in saved:item['request']=json.loads(saved['request_json'])
            old=json.loads(saved['raw_response_json']);actual=native(mode,item)
            if mode=='index':expected=old
            elif item['kind']=='snapshot':expected=rules.expected_snapshot(item['name'],old,contract,logical);actual=rules.normalized_snapshot(item['name'],actual)
            elif item['kind']=='object':expected=rules.expected_object(item['request']['id'],old,contract,logical)
            else:expected=rules.expected_query(item['request'],old,contract,old_sources)
            try:rules.verify_response(expected,actual)
            except ValueError:
                from chen_indian_sec_semantic_diff_v2 import differences
                delta=differences(expected,actual);write(OUT/'preservation-failure.json',{'mode':mode,'case':item,'difference_count':len(delta),'first_differences':delta[:30]});raise
    for item in new_main:
        request=item['request'];actual=native('main',item)
        if request['collection']=='sources':
            wanted=[r for r in contract['new_sources'] if r['id']==request['filters'][0]['value']]
            rules.verify_response(query_response(request,wanted),actual)
            continue
        selected=selected_rows(request,contract)
        expected=query_response(request,selected,rules.query_scene(request['collection'],selected,contract))
        rules.verify_response(expected,actual)
    for item in new_source:
        path=item['request']['document'];actual=native('index',item)
        if actual['source_sha256']!=sha(path) or not rules.same({r['source_key']:r['record'] for r in actual['rows']},read(path)):raise ValueError('New indexed source differs: '+path)
    cli=WORK/'build/debug/osw-query-cli'
    for mode,item in [('main',new_main[0]),('index',new_source[0])]:
        payload=candidate if mode=='main' else new_index
        response=subprocess.run([str(cli),*(['--index'] if mode=='index' else []),str(payload),'-'],input=json.dumps(item['request']).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=600)
        rules.verify_response(native(mode,item),json.loads(response.stdout))
    del baseline;gc.collect()
    cargo(['rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib'],'wasm-build.txt')
    wasm=WORK/'build/wasm32-unknown-unknown/release/osw_query.wasm';proof=dependencies(wasm.with_suffix('.d').read_text(),ROOT,inventory);write(OUT/'dependency-proof.json',proof)
    for mode,payload,new in [('main',candidate,new_main),('index',new_index,new_source)]:parity('compare-'+mode,wasm,payload,requests[mode]+new)
    artifact=WORK/'artifact';(artifact/'almanac').mkdir(parents=True)
    packet=write_packet(artifact/'almanac/query-data.json',candidate.read_bytes())
    for path,raw in generated.items():target=artifact/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    shutil.copyfile(wasm,artifact/'almanac/query-engine.wasm')
    generated_paths={p.relative_to(artifact).as_posix() for p in artifact.rglob('*') if p.is_file()}
    replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256'],**pref['presentation_sha256'],**{p:sha(p) for p in index.DOCUMENTS},**{p:sha(artifact/p) for p in generated_paths}}
    compiler=subprocess.check_output(['rustc','+1.95.0','--version']).decode().strip()
    overlay=engine_manifest(engine,replacements,inventory=inventory,proof=proof,source_commit=os.environ['GITHUB_SHA'],logical_sha=logical,wasm_sha=sha(wasm),compiler=compiler,source_documents=index.DOCUMENTS)
    write(artifact/'almanac/query-engine.manifest.json',overlay);write(OUT/'engine-manifest.json',overlay)
    files={p.relative_to(artifact).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in artifact.rglob('*') if p.is_file()}
    report={'schema':'osw.pacific-nec-product-axis-delivery-result.v1','status':'PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'logical_sha256':logical,'logical_bytes':packet['logical_byte_length'],'wasm_sha256':sha(wasm),'rust_tests_passed':295,'historical_main_api_cases':234,'historical_source_api_cases':86,
        'new_main_api_cases':len(new_main),'new_source_api_cases':len(new_source),'ordinary_cli_equivalence_checks':2,'source_index_audit':audit,'packet_comparison':comparison,'generated_files':files,
        'request_sha256':sha(REQUEST),'preflight_sha256':sha(PREFLIGHT),'browser_review_completed':False,'installed':False,'main_updated':False,'local_bulk_sync':False,'full_goal_complete':False}
    write(OUT/'result.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')})
        raise
