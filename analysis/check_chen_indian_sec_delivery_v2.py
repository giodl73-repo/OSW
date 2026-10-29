"""One sequential cloud native/WASM matching-build gate. Never installs remotely."""
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
REQUEST='research/chen-indian-sec-delivery-request-v2.json'
PREFLIGHT='research/chen-indian-sec-delivery-preflight-v2.json'
OUT=ROOT/'.pytest_cache/chen-indian-sec-delivery-v2'
WORK=ROOT/'.pytest_cache/chen-indian-sec-delivery-work-v2'
OWNERS=['current:atlantic-north-equatorial','current:pacific-north-equatorial','current:atlantic-south-equatorial','current:pacific-south-equatorial','current:indian-south-equatorial','current:north-equatorial','current:south-equatorial']
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with (ROOT/p).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_CHEN_INDIAN_SEC_DELIVERY_V2')!='1'):
        raise ValueError('Scoped cloud delivery only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for k in ['CARGO_BUILD_JOBS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(k)!='1':raise ValueError('One worker required')
    r=read(REQUEST)
    if r.get('schema')!='osw.chen-indian-sec-delivery-request.v2' or r.get('execute') is not True or sha(PREFLIGHT)!=r['preflight_sha256']:raise ValueError('Disabled/changed delivery request')
    for k in ['cloud_parent_packet_read_permitted','cloud_index_registration_permitted','cloud_candidate_files_permitted','native_build_permitted','wasm_build_permitted','cloud_engine_artifact_permitted']:
        if r.get(k) is not True:raise ValueError('Missing scoped permission: '+k)
    for k in ['browser_permitted','installation_permitted','ocean_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if r.get(k) is not False:raise ValueError('Unrelated permission enabled')
    p=read(PREFLIGHT)
    for f,h in p['input_sha256'].items():
        if sha(f)!=h:raise ValueError('Frozen source changed: '+f)
    for f,row in p['installed_files'].items():
        if sha(f)!=row['sha256'] or (ROOT/f).stat().st_size!=row['bytes']:raise ValueError('Installed parent differs: '+f)
    for f in p['disabled_requests']:
        v=read(f)
        if v.get('execute',v.get('execution_permitted')) is not False:raise ValueError('Older request enabled')
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad work enabled')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact checkout required')
    return p

def run():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    import chen_indian_sec_ridge_index_v1 as index
    import chen_indian_sec_delivery_contract_v1 as rules
    from chen_indian_sec_native_batch_v2 import encode_case,case_key,run_batch
    from check_chen_indian_sec_candidate_v2 import verify_extension
    from query_packet import read_bundle_bytes,write_packet
    from south_java_catalog_engine_v1 import dependencies
    query=index.query;c,replay=query.validated_contract();write(OUT/'canonical-replay.json',replay)
    engine=read('almanac/query-engine.manifest.json');oldwasm=sha('almanac/query-engine.wasm')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if index.sha(raw)!=query.PARENT:raise ValueError('Changed parent logical bytes')
    parentpath=WORK/'parent.json';parentpath.write_bytes(raw);parent=json.loads(raw);del raw
    oldindex=WORK/'parent-index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as src,oldindex.open('xb') as dst:shutil.copyfileobj(src,dst,1048576)
    catalog=read('almanac/index-catalog.json')
    if sha(oldindex)!=catalog['bundle_sha256'] or oldindex.stat().st_size!=catalog['bundle_bytes']:raise ValueError('Parent decompressed index differs')
    requests={mode:[{'kind':'query','request':r['request']} for r in read('research/pacific-nec-nominal-width-engine-run-v2/'+mode+'-parity.json')['checks']] for mode in ['main','index']}
    if [len(requests[k]) for k in ['main','index']]!=[215,79]:raise ValueError('Historical case inventory differs')
    requests['main'] += [{'kind':'snapshot','name':n} for n in ['atlas','seasons','dashboard']]+[{'kind':'object','request':{'id':o}} for o in OWNERS]
    def parity(mode,wasm,payload,cases,metadata=None):
        rows=[encode_case(item) for item in cases]
        extra={}
        if mode.startswith('compare'):
            batch,cache=native_batches['index' if mode.endswith('index') else 'main']
            rows=[{**item,'raw_response_json':cache[case_key(item)]} for item in rows]
            extra={'metadata_json':batch['metadata_json']}
        fixture=WORK/(mode+'-fixture.json');write(fixture,{'payload_sha256':sha(payload),'cases':rows,**extra})
        output=(WORK if mode.startswith('capture') else OUT)/(mode+'.json')
        subprocess.run(['node','--max-old-space-size=1536','analysis/check_chen_indian_sec_parity_v2.mjs',mode,str(wasm),str(payload),str(fixture),str(output),sha(wasm)],check=True,timeout=1800)
        return json.loads(output.read_bytes())
    baseline={k:parity('capture-'+k,ROOT/'almanac/query-engine.wasm',p,requests[k]) for k,p in [('main',parentpath),('index',oldindex)]}
    old_sources=parent['collections']['sources']
    collections,manifest=query.prepare(parent['collections'],parent['manifest'],c,parent_logical_sha256=query.PARENT)
    child={**parent,'collections':collections,'manifest':manifest};comparison=verify_extension(parent,child,c)
    generated,audit=index.source_index((ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    child=index.attach(child,generated,audit);candidate=WORK/'candidate.json';candidate.write_bytes(index.encode(child));logical=sha(candidate)
    if logical!='000ec593c4fd1eb597a0a7204824b5c8c8e19cd8e2683080095a46ec50609cb1':raise ValueError('Previously verified indexed candidate differs')
    for p,b in generated.items():(ROOT/p).write_bytes(b)
    newindex=WORK/'index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as src,newindex.open('xb') as dst:shutil.copyfileobj(src,dst,1048576)
    newcatalog=read('almanac/index-catalog.json')
    if sha(newindex)!=newcatalog['bundle_sha256']:raise ValueError('New decompressed index differs')
    inventory=copy.deepcopy(pref['compile_inventory']);inventory['saved_candidate_logical_sha256']=logical;inventory['saved_candidate_catalog_sha256']=sha('almanac/index-catalog.json');inventory['compile_time_data_sha256']['almanac/index-catalog.json']=sha('almanac/index-catalog.json')
    allowed=set(pref['runtime_source_changes'])|index.INDEX
    rules.verify_inventory(inventory,engine,allowed)
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for p,h in inventory[group].items():
            if sha(p)!=h:raise ValueError('Compiler input changed: '+p)
    write(OUT/'compile-inventory.json',inventory)
    env=dict(os.environ,CARGO_TARGET_DIR=str(WORK/'build'),CARGO_INCREMENTAL='0')
    def cargo(args,log):
        with (OUT/log).open('wb') as stream:subprocess.run(['cargo','+1.95.0',*args,'--manifest-path','rust/osw-query/Cargo.toml'],env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=2400)
    cargo(['build','--locked','--bin','osw-query-cli','--example','delivery_probe_v2'],'native-build.txt')
    with (OUT/'rust-tests.txt').open('wb') as stream:subprocess.run(['cargo','+1.95.0','test','--locked','--lib','--manifest-path','rust/osw-query/Cargo.toml','--','--test-threads=1'],env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=1800)
    if b'test result: ok. 289 passed; 0 failed;' not in (OUT/'rust-tests.txt').read_bytes():raise ValueError('Expected289 native tests')
    cli=WORK/'build/debug/osw-query-cli'
    def eq(k,v):return {'field':k,'op':'eq','value':v}
    new_specs=[
        (query.SERIES,[eq('id',query.SERIES_ID)],100,0),
        (query.READINGS,[eq('series_id',query.SERIES_ID)],200,0),
        (query.READINGS,[eq('series_id',query.SERIES_ID),eq('length_km',None)],200,0),
        (query.READINGS,[eq('series_id',query.SERIES_ID),eq('kernel_cells',3),eq('status','regional_model_grid_estimate')],200,0),
        (query.READINGS,[eq('series_id',query.SERIES_ID),eq('provider_year',1995)],100,0),
        (query.READINGS,[eq('series_id',query.SERIES_ID)],1,1),
        (query.READINGS,[eq('series_id',query.SERIES_ID),eq('rank_eligible',True)],100,0),
        (query.READINGS,[eq('entity_id','current:south-equatorial')],100,0),
        (query.SENSITIVITIES,[eq('series_id',query.SERIES_ID)],200,0)]
    new_main=[{'kind':'query','request':{'collection':name,'filters':filters,'limit':limit,'offset':offset}}
              for name,filters,limit,offset in new_specs]
    new_index=[{'kind':'query','request':{'document':path,'pointer':'','limit':500}} for path in index.DOCUMENTS]
    probe=WORK/'build/debug/examples/delivery_probe_v2'
    native_batches={mode:run_batch(probe,mode,payload,requests[mode]+new)
        for mode,payload,new in [('main',candidate,new_main),('index',newindex,new_index)]}
    for mode,count in [('main',234),('index',86)]:
        if len(native_batches[mode][0]['cases'])!=count:raise ValueError('Incomplete native batch inventory')
    def native(payload,item=None,source=False):
        mode='index' if source else 'main';batch,cache=native_batches[mode]
        if payload!=(newindex if source else candidate):raise ValueError('Wrong native payload')
        return json.loads(batch['metadata_json'] if item is None else cache[case_key(encode_case(item))])
    # Verify both batch API modes against the ordinary CLI independently.
    samples=[(candidate,{'kind':'snapshot','name':'atlas'},False),
             (candidate,requests['main'][0],False),
             (newindex,requests['index'][0],True)]
    for payload,item,source in samples:
        args=[str(cli)]+(['--index'] if source else [])+[str(payload)]
        data=None
        if item['kind']=='snapshot':args+=['--'+item['name']]
        else:args+=['-'];data=json.dumps(item['request']).encode()
        single=subprocess.run(args,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=600)
        if json.loads(single.stdout)!=native(payload,item,source):raise ValueError('Batch differs from ordinary CLI')
    write(OUT/'native-batch-summary.json',{'case_counts':{k:len(v[0]['cases']) for k,v in native_batches.items()},
        'elapsed_seconds':{k:v[0]['elapsed_seconds'] for k,v in native_batches.items()},
        'ordinary_cli_equivalence_checks':len(samples),'lossless_response_strings':True})
    cases={'main':[],'index':[]}
    for mode,payload in [('main',candidate),('index',newindex)]:
        for item in baseline[mode]['cases']:
            request={k:v for k,v in item.items() if k in ('kind','name')}
            if 'request_json' in item:request['request']=json.loads(item['request_json'])
            actual=native(payload,request,mode=='index');old=json.loads(item['raw_response_json'])
            try:
                if mode=='index':
                    if actual!=old:raise ValueError('Historical source response changed')
                elif item['kind']=='snapshot':rules.verify_snapshot(item['name'],old,actual,c)
                elif item['kind']=='object':rules.verify_object(request['request']['id'],old,actual,c)
                elif actual!=rules.expected_query(request['request'],old,c,old_sources):raise ValueError('Historical query response changed outside declared scope: '+str(request['request']))
            except (ValueError,AssertionError):
                import chen_indian_sec_snapshot_diff_v1 as diagnostic
                from chen_indian_sec_semantic_diff_v2 import differences
                if mode=='index':expected=old
                elif item['kind']=='snapshot':
                    expected=diagnostic.expected_snapshot(item['name'],old,c,logical)
                    actual=diagnostic.normalized_snapshot(item['name'],actual)
                elif item['kind']=='object':
                    expected=rules.transform_rows(old,c);expected['bundle_sha256']=logical
                    expected['collections']['sources']+=copy.deepcopy(c['new_sources'])
                    if request['request']['id']==rules.OWNER:expected['regional_model_length_scene']=rules.full_scene(c)
                else:expected=rules.expected_query(request['request'],old,c,old_sources)
                delta=differences(expected,actual)
                write(OUT/'preservation-failure-differences.json',{'case':request,'mode':mode,
                    'difference_count':len(delta),'first_differences':delta[:50],
                    'report_only_acceptance_unchanged':True})
                raise
            cases[mode].append({**request,'expected':actual})
    for name,filters,limit,offset in new_specs:
        request={'collection':name,'filters':filters,'limit':limit,'offset':offset};item={'kind':'query','request':request};actual=native(candidate,item)
        expected=sorted([r for r in child['collections'][name] if all(r.get(f['field'])==f['value'] for f in filters)],key=lambda r:r['id'])
        if actual['total']!=len(expected) or actual['rows']!=expected[offset:offset+limit]:raise ValueError('New regional query rows differ')
        scene=actual['chart_scene']
        if expected:
            wanted={'kind':'regional_model_core_length_series','entity_id':rules.OWNER,'title':'Indian SEC: regional model-grid lengths','series':c['series_record'],'selected_collection':name,'selected_count':len(expected),'selected_records':expected,'scope':c['series_record']['scope'],'figure':'figures/chen-indian-sec-regional-ridge-lengths-v1.svg'}
            if scene!=wanted:raise ValueError('New regional chart scene differs')
        elif scene is not None:raise ValueError('Empty/family query acquired regional scene')
        cases['main'].append({**item,'expected':actual})
    for path in index.DOCUMENTS:
        original=read(path);item={'kind':'query','request':{'document':path,'pointer':'','limit':500}}
        actual=native(newindex,item,True)
        if actual['source_sha256']!=sha(path) or {r['source_key']:r['record'] for r in actual['rows']}!=original:raise ValueError('New indexed root differs')
        cases['index'].append({**item,'expected':actual})
    del parent,child,collections,manifest,baseline;gc.collect()
    cargo(['rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib'],'wasm-build.txt')
    wasm=WORK/'build/wasm32-unknown-unknown/release/osw_query.wasm';proof=dependencies(wasm.with_suffix('.d').read_text(),ROOT,inventory);write(OUT/'dependency-proof.json',proof)
    for mode,payload in [('main',candidate),('index',newindex)]:parity('compare-'+mode,wasm,payload,cases[mode],native(payload,source=mode=='index'))
    artifact=WORK/'artifact';(artifact/'almanac').mkdir(parents=True);packet=write_packet(artifact/'almanac/query-data.json',candidate.read_bytes())
    for p,b in generated.items():target=artifact/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
    shutil.copyfile(wasm,artifact/'almanac/query-engine.wasm')
    generated_paths={p.relative_to(artifact).as_posix() for p in artifact.rglob('*') if p.is_file()}
    replacements={**pref['input_sha256'],**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256'],**{p:sha(artifact/p) for p in generated_paths}}
    compiler=subprocess.check_output(['rustc','+1.95.0','--version']).decode().strip()
    overlay=rules.engine_manifest(engine,replacements,inventory=inventory,allowed_changes=allowed|generated_paths,proof=proof,compiler=compiler,source_commit=os.environ['GITHUB_SHA'],logical_sha=logical,wasm_sha=sha(wasm))
    write(artifact/'almanac/query-engine.manifest.json',overlay);write(OUT/'engine-manifest.json',overlay)
    generated_files={p.relative_to(artifact).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in artifact.rglob('*') if p.is_file()}
    report={'schema':'osw.chen-indian-sec-delivery-result.v2','status':'PASS_MATCHED_NATIVE_WASM_ENGINE_BROWSER_PENDING','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'logical_sha256':logical,'logical_bytes':packet['logical_byte_length'],'wasm_sha256':sha(wasm),'rust_tests_passed':289,'historical_main_queries':215,'historical_source_queries':79,'new_main_queries':9,'new_source_queries':7,'complete_api_snapshots':3,'complete_object_apis':7,'generated_files':generated_files,'source_index_audit':audit,'packet_comparison':comparison,'request_sha256':sha(REQUEST),'preflight_sha256':sha(PREFLIGHT),'browser_review_completed':False,'installed':False,'main_updated':False,'local_bulk_sync':False,'full_goal_complete':False}
    write(OUT/'result.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(exist_ok=True,parents=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')})
        raise
