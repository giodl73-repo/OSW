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
REQUEST='research/pacific-sec-gourdeau-2008-delivery-request-v1.json'
PREFLIGHT='research/pacific-sec-gourdeau-2008-delivery-preflight-v1.json'
OUT=ROOT/'.pytest_cache/pacific-sec-gourdeau-2008-delivery-v1'
WORK=ROOT/'.pytest_cache/pacific-sec-gourdeau-2008-delivery-work-v1'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())

def failure_report(error,source_commit):
    result={'status':'FAIL','error':str(error),'source_commit':source_commit}
    stderr=getattr(error,'stderr',None)
    if stderr:
        raw=stderr.encode('utf-8') if isinstance(stderr,str) else bytes(stderr)
        result.update(stderr_text=raw[:16384].decode('utf-8',errors='replace'),
            stderr_bytes=len(raw),stderr_sha256=hashlib.sha256(raw).hexdigest(),stderr_truncated=len(raw)>16384)
    return result

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_PACIFIC_SEC_JET_WIDTHS_DELIVERY_V1')!='1'):
        raise ValueError('Scoped cloud regional jet-width candidate delivery only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required: '+key)
    request=read(REQUEST)
    if request.get('schema')!='osw.pacific-sec-jet-widths-delivery-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT):raise ValueError('Disabled or changed delivery request')
    for key in ['cloud_parent_packet_read_permitted','cloud_index_registration_permitted','cloud_candidate_files_permitted','native_build_permitted','wasm_build_permitted','cloud_engine_artifact_permitted']:
        if request.get(key) is not True:raise ValueError('Missing permission: '+key)
    for key in ['browser_permitted','installation_permitted','ocean_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled: '+key)
    if request.get('max_cloud_jobs')!=1 or request.get('max_local_heavy_jobs')!=0:raise ValueError('Job bounds differ')
    for ref,wanted in [('main','19148702de6433253dbf412a0a28c0cb4f8e409e'),('codex/current-measurement-gaps',os.environ['GITHUB_SHA'])]:
        if subprocess.check_output(['git','ls-remote','origin','refs/heads/'+ref],text=True,timeout=55).split()[0]!=wanted:raise ValueError('Branch moved: '+ref)
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
    result=[]
    def add(collection,field,value,**extra):
        result.append({'kind':'query','request':{'collection':collection,'filters':[{'field':field,'op':'eq','value':value}],'limit':100,**extra}})
    owner='current:pacific-south-equatorial'
    add('widths','current_id','pacific-south-equatorial')
    add('widths','current_id','pacific-south-equatorial',limit=1,offset=1)
    add('widths','id',contract['width_records'][0]['id'])
    add('widths','current_id','south-equatorial')
    add('objects','id',owner)
    add('sources','id',contract['new_source']['id'])
    result.extend({'kind':'object','request':{'id':identity}} for identity in (owner,'current:south-equatorial'))
    result.extend({'kind':'snapshot','name':name} for name in ('atlas','seasons','dashboard'))
    return result


def run():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    import pacific_sec_jet_widths_query_v1 as query
    import pacific_sec_jet_widths_index_v1 as index
    import pacific_sec_jet_widths_delivery_rules_v1 as rules
    from pacific_sec_jet_widths_engine_v1 import engine_manifest
    from chen_indian_sec_native_batch_v2 import encode_case,case_key,run_batch
    from query_packet import read_bundle_bytes,write_packet
    from captured_response_files_v1 import read_captured_json
    from south_java_catalog_engine_v1 import dependencies
    contract=query.build_contract()
    if query.encoded(contract)!=(ROOT/query.FILE).read_bytes():raise ValueError('Frozen contract differs')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if hashlib.sha256(raw).hexdigest()!=query.PARENT or len(raw)!=195320893:raise ValueError('Exact parent logical packet required')
    parent_path=WORK/'parent.json';parent_path.write_bytes(raw);parent=json.loads(raw);del raw
    parent_index=WORK/'parent-index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as source,parent_index.open('xb') as target:shutil.copyfileobj(source,target,1048576)
    catalog=read('almanac/index-catalog.json')
    if sha(parent_index)!=catalog['bundle_sha256'] or parent_index.stat().st_size!=catalog['bundle_bytes']:raise ValueError('Parent index differs')
    requests={mode:[{'kind':r['kind'],**({'name':r['name']} if r['kind']=='snapshot' else {'request':json.loads(r['request_json'])})} for r in read('research/richardson-walsh-1986-characteristic-velocity-delivery-run-v2/compare-'+mode+'.json')['checks']] for mode in ['main','index']}
    if [len(requests[k]) for k in ['main','index']]!=[343,105]:raise ValueError('Complete 448 historical API cases required')
    new_main=new_requests(contract)
    historical_main_count=len(requests['main'])
    requests['main']+=new_main
    engine=read('almanac/query-engine.manifest.json')
    def parity(mode,wasm,payload,cases):
        rows=[encode_case(item) for item in cases];extra={}
        if mode.startswith('compare'):
            batch,cache=batches['index' if mode.endswith('index') else 'main']
            rows=[{**item,'raw_response_json':cache[case_key(item)]} for item in rows];extra={'metadata_json':batch['metadata_json']}
        if mode.startswith('compare'):
            from bounded_parity_cases_v1 import partition,encoded,expected_descriptor
            def store_expected(label,raw):
                descriptor,body=expected_descriptor(mode+'-'+label+'.expected.json',raw)
                with (WORK/descriptor['file']).open('xb') as stream:stream.write(body)
                return descriptor
            expected_metadata=store_expected('metadata',extra['metadata_json'])
            referenced=[]
            for number,row in enumerate(rows,1):
                referenced.append({**{k:v for k,v in row.items() if k!='raw_response_json'},
                    'expected_response':store_expected(str(number),row['raw_response_json'])})
            groups=partition({'schema':'osw.bounded-expected-response-fixture.v1','payload_sha256':sha(payload),
                              'expected_metadata':expected_metadata},referenced)
            write(OUT/(mode+'-transport.json'),{'expected_transport':'hash_checked_one_complete_response_file_at_a_time',
                'case_count':len(referenced),'initialization_response_bytes':expected_metadata['bytes'],
                'largest_expected_response_bytes':max(r['expected_response']['bytes'] for r in referenced),
                'fixture_bytes':[len(encoded(group)) for group in groups],'all_expected_files_cloud_only':True})
            reports=[]
            for number,group in enumerate(groups,1):
                fixture=WORK/(mode+f'-fixture-{number}.json');fixture.write_bytes(encoded(group))
                output=OUT/(mode+f'-part-{number}.json')
                subprocess.run(['node','--max-old-space-size=1536','analysis/check_bounded_native_wasm_v1.mjs',mode,str(wasm),str(payload),str(fixture),str(output),sha(wasm)],check=True,timeout=1800)
                report=read(output)
                if (report['status']!='PASS' or report['mode']!=mode or report['payload_sha256']!=group['payload_sha256']
                    or report['wasm_sha256']!=sha(wasm) or report['complete_initialization_equal'] is not True
                    or report.get('initialization_response_sha256')!=group['expected_metadata']['sha256']
                    or len(report['checks'])!=len(group['cases'])):raise ValueError('Incomplete bounded parity report')
                if mode.endswith('index') and report['mismatched_corpus_refused'] is not True:raise ValueError('Index mismatch refusal missing')
                for wanted,actual in zip(group['cases'],report['checks']):
                    if (actual['kind']!=wanted['kind'] or actual['name']!=wanted.get('name')
                        or actual['request_json']!=wanted.get('request_json') or actual['entire_response_equal'] is not True
                        or actual['response_bytes']!=wanted['expected_response']['bytes']
                        or actual['response_sha256']!=wanted['expected_response']['sha256']):
                        raise ValueError('Bounded comparison changed case identity or complete response')
                reports.append(report)
            combined={**reports[0],'checks':[check for report in reports for check in report['checks']],
                'max_wasm_linear_memory_bytes':max(r['max_wasm_linear_memory_bytes'] for r in reports),
                'bounded_fixture_bytes':64*1024*1024,'sequential_comparison_parts':len(reports)}
            if len(combined['checks'])!=len(cases):raise ValueError('Bounded comparisons lost cases')
            write(OUT/(mode+'.json'),combined)
            return combined
        fixture=WORK/(mode+'-fixture.json');write(fixture,{'payload_sha256':sha(payload),'cases':rows,**extra})
        output=(WORK if mode.startswith('capture') else OUT)/(mode+'.json')
        subprocess.run(['node','--max-old-space-size=1536','analysis/capture_bounded_wasm_responses_v1.mjs',mode,str(wasm),str(payload),str(fixture),str(output),sha(wasm)],check=True,timeout=1800)
        captured=read(output)
        if (captured.get('status')!='PASS_COMPLETE_RESPONSE_FILES_CAPTURED' or captured['mode']!=mode
            or captured['payload_sha256']!=sha(payload) or captured['wasm_sha256']!=sha(wasm)
            or len(captured['cases'])!=len(rows)
            or [{k:v for k,v in row.items() if k!='response'} for row in captured['cases']]!=rows):
            raise ValueError('Incomplete capture or altered ordered case inventory')
        if json.loads(read_captured_json(WORK,captured['metadata'],payload.stat().st_size+2097152)).get('ok') is not True:
            raise ValueError('Invalid complete captured initialization')
        write(OUT/(mode+'-transport.json'),captured)
        return captured
    collections,manifest=query.prepare(parent['collections'],parent['manifest'],contract,parent_logical_sha256=query.PARENT)
    child={**parent,'collections':collections,'manifest':manifest};comparison=rules.verify_extension(parent,child,contract)
    generated,audit=index.source_index((ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    child=index.attach(child,generated,audit,contract);candidate=WORK/'candidate.json';candidate.write_bytes(index.encode(child));logical=sha(candidate)
    prior_collections={name:copy.deepcopy(parent['collections'][name]) for name in ('sources','widths','objects')}
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
    if b'test result: ok. 307 passed; 0 failed;' not in (OUT/'rust-tests.txt').read_bytes():raise ValueError('Expected 307 native regression tests')
    new_source=[{'kind':'query','request':{'document':path,'pointer':'','limit':500}} for path in index.DOCUMENTS]
    probe=WORK/'build/debug/examples/delivery_probe_v2'
    batches={mode:run_batch(probe,mode,payload,requests[mode]+new) for mode,payload,new in [('main',candidate,[]),('index',new_index,new_source)]}
    baseline={mode:parity('capture-'+mode,ROOT/'almanac/query-engine.wasm',payload,requests[mode]) for mode,payload in [('main',parent_path),('index',parent_index)]}
    def native(mode,item):return json.loads(batches[mode][1][case_key(encode_case(item))])
    for mode in ['main','index']:
        for saved in baseline[mode]['cases']:
            item={k:v for k,v in saved.items() if k in ('kind','name')}
            if 'request_json' in saved:item['request']=json.loads(saved['request_json'])
            old=json.loads(read_captured_json(WORK,saved['response'],134217728 if item['kind']=='snapshot' else 16777216));actual=native(mode,item)
            if mode=='index':expected=old
            elif item['kind']=='snapshot':expected=rules.expected_snapshot(item['name'],old,contract,logical);actual=rules.normalized_snapshot(item['name'],actual)
            elif item['kind']=='object':expected=rules.expected_object(item['request']['id'],old,contract,logical)
            else:expected=rules.expected_query(item['request'],old,contract,prior_collections)
            try:rules.verify_response(expected,actual)
            except ValueError:
                from chen_indian_sec_semantic_diff_v2 import differences
                delta=differences(expected,actual);write(OUT/'preservation-failure.json',{'mode':mode,'case':item,'difference_count':len(delta),'first_differences':delta[:30]});raise
    for item in new_source:
        path=item['request']['document'];actual=native('index',item)
        if actual['source_sha256']!=sha(path) or not rules.same({r['source_key']:r['record'] for r in actual['rows']},read(path)):raise ValueError('New indexed source differs: '+path)
    write(OUT/'native-preservation.json',{'status':'PASS_COMPLETE_NATIVE_PRESERVATION_AND_NEW_SOURCE_QUERIES',
        'historical_main_cases':historical_main_count,'historical_source_cases':105,'additional_main_cases':len(new_main),
        'additional_source_cases':len(new_source),'complete_response_checks':len(requests['main'])+105+len(new_source)})
    cli=WORK/'build/debug/osw-query-cli'
    for mode,item in [('main',new_main[0]),('index',new_source[0])]:
        payload=candidate if mode=='main' else new_index
        response=subprocess.run([str(cli),*(['--index'] if mode=='index' else []),str(payload),'-'],input=json.dumps(item['request']).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=600)
        rules.verify_response(native(mode,item),json.loads(response.stdout))
    del baseline;gc.collect()
    cargo(['rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib'],'wasm-build.txt')
    wasm=WORK/'build/wasm32-unknown-unknown/release/osw_query.wasm';proof=dependencies(wasm.with_suffix('.d').read_text(),ROOT,inventory);write(OUT/'dependency-proof.json',proof)
    for mode,payload,new in [('main',candidate,[]),('index',new_index,new_source)]:parity('compare-'+mode,wasm,payload,requests[mode]+new)
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
    report={'schema':'osw.pacific-sec-jet-widths-delivery-result.v1','query_contract_file':query.FILE,'status':'PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'logical_sha256':logical,'logical_bytes':packet['logical_byte_length'],'wasm_sha256':sha(wasm),'rust_tests_passed':307,'historical_main_api_cases':historical_main_count,'historical_source_api_cases':105,
        'new_main_api_cases':len(new_main),'new_source_api_cases':len(new_source),'ordinary_cli_equivalence_checks':2,'source_index_audit':audit,'packet_comparison':comparison,'generated_files':files,
        'request_sha256':sha(REQUEST),'preflight_sha256':sha(PREFLIGHT),'browser_review_completed':False,'installed':False,'main_updated':False,'local_bulk_sync':False,'full_goal_complete':False}
    write(OUT/'result.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',failure_report(error,os.environ.get('GITHUB_SHA')))
        raise
