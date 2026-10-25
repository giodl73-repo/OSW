"""Cloud-only temporary cohort append and actual Rust query verification."""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/south-java-model-layer-cloud-request-v1.json'
PREFLIGHT = 'research/south-java-model-layer-cloud-preflight-v1.json'
OUTPUT = ROOT / '.pytest_cache/south-java-model-layer-cloud-check-v1'
PARENT_SHA = '369004f99601dd53db77b50cb671c3875cd350aec6df66d56b0781326b37fc5c'
PARENT_BYTES = 189905442


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fingerprint(value):
    return digest(json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode())


def decode_native_result(result):
    if len(result.stdout)>131072 or len(result.stderr)>32768:
        raise ValueError('Unexpected native output size')
    if result.returncode!=0:
        detail=result.stderr.decode(errors='replace').strip()[:800]
        if not detail and result.stdout:
            try:detail=str(json.loads(result.stdout).get('error',''))[:800]
            except (ValueError,AttributeError):detail='Non-JSON native output'
        raise ValueError(f'Native CLI failed (exit {result.returncode}): '+(detail or 'No stderr or JSON error output'))
    try:actual=json.loads(result.stdout)
    except ValueError as error:raise ValueError('Native CLI returned empty or invalid JSON on exit0') from error
    if not isinstance(actual,dict) or actual.get('ok') is not True:
        raise ValueError('Native query refused: '+str(actual.get('error','Invalid response') if isinstance(actual,dict) else 'Invalid response')[:800])
    return actual


def cloud_environment(env):
    # Refuse before reading any file, including the packet descriptor.
    if (env.get('GITHUB_ACTIONS') != 'true' or env.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or env.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or env.get('GITHUB_WORKSPACE') != str(ROOT)
            or not hasattr(os,'sched_getaffinity') or len(os.sched_getaffinity(0)) != 1):
        raise RuntimeError('One cloud CPU and the exact working-branch workspace are required; no packet read.')
    for name in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if env.get(name) != '1':
            raise RuntimeError('Single-worker cloud configuration required: '+name)


def verify_controls(env):
    cloud_environment(env)
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    if head != env.get('GITHUB_SHA'):
        raise ValueError('Exact checked-out source commit required')
    request=json.loads((ROOT/REQUEST).read_bytes())
    if (request.get('schema')!='osw.south-java-model-layer-cloud-request.v1'
            or request.get('execution_permitted') is not True
            or request.get('compatibility_verification_only') is not True
            or request.get('cloud_packet_candidate_permitted') is not True
            or request.get('cloud_native_build_permitted') is not True
            or type(request.get('max_heavy_local_jobs')) is not int or type(request.get('max_cloud_jobs')) is not int
            or request.get('max_heavy_local_jobs')!=0 or request.get('max_cloud_jobs')!=1):
        raise ValueError('Temporary cloud candidate check is disabled or changed')
    for name in ['provider_requests_permitted','original_source_processing_permitted','installed_assets_change_permitted',
                 'measurement_admission_permitted','wasm_build_permitted','browser_automation_permitted','main_merge_permitted']:
        if request.get(name) is not False:
            raise ValueError('Forbidden candidate permission: '+name)
    raw=(ROOT/PREFLIGHT).read_bytes()
    if digest(raw)!=request['preflight_sha256']:
        raise ValueError('Changed cloud preflight')
    pref=json.loads(raw)
    if (pref.get('schema')!='osw.south-java-model-layer-cloud-preflight.v1'
            or pref['parent_logical_sha256']!=PARENT_SHA or pref['parent_logical_bytes']!=PARENT_BYTES):
        raise ValueError('Changed delivered parent')
    for name,expected in pref['input_sha256'].items():
        if digest((ROOT/name).read_bytes())!=expected:
            raise ValueError('Changed cloud source input: '+name)
    for name,count in [('research/eacc-coastal-reference-extent-preflight-v1.json',83),
                       ('research/current-local-extent-query-check-preflight-v2.json',23),
                       ('research/current-local-extent-ui-preflight-v1.json',20)]:
        pins=json.loads((ROOT/name).read_bytes())['input_sha256']
        if len(pins)!=count:raise ValueError('Changed preserved input count')
        for path,expected in pins.items():
            if digest((ROOT/path).read_bytes())!=expected:raise ValueError('Changed preserved input: '+path)
    phase=json.loads((ROOT/'research/current-gap-delivery-phase.json').read_bytes())
    if phase['phase']!='source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain in place')
    return pref


def run(cli, pref):
    import south_java_layer_query_v1 as context
    from query_packet import read_bundle_bytes
    descriptor=ROOT/'almanac/query-data.json'
    packet=json.loads(descriptor.read_bytes())
    if packet.get('logical_sha256')!=PARENT_SHA or packet.get('logical_byte_length')!=PARENT_BYTES:
        raise ValueError('Cloud checkout does not contain the delivered106-current cohort')
    raw=read_bundle_bytes(descriptor)
    if len(raw)!=PARENT_BYTES or digest(raw)!=PARENT_SHA:raise ValueError('Parent byte custody differs')
    bundle=json.loads(raw);del raw
    rows=bundle['collections']
    counts={name:len(values) for name,values in rows.items()}
    if (len(rows['objects'])!=246 or sum(row['type']=='named_current' for row in rows['objects'])!=106
            or len(rows['widths'])!=172 or sum(counts.values())!=108551):
        raise ValueError('Delivered parent counts differ')
    original_manifest=json.loads(json.dumps(bundle['manifest']))
    collection_hashes={name:fingerprint(values) for name,values in rows.items()}
    old_owner=next(row for row in rows['objects'] if row['id']==context.TARGET)
    other_objects_hash=fingerprint([row for row in rows['objects'] if row['id']!=context.TARGET])
    contract=context.build_contract()
    if (ROOT/context.FILE).read_bytes()!=context.encoded(contract):raise ValueError('Changed prepared projection')
    old_prefixes={name:fingerprint(rows.get(name,[])) for name in contract['collections']}
    context.append(rows,contract)
    affected=set(contract['collections'])|{'objects'}
    for name,expected in collection_hashes.items():
        if name not in affected and fingerprint(rows[name])!=expected:
            raise ValueError('Prior collection changed: '+name)
    for name,expected in old_prefixes.items():
        if fingerprint(rows[name][:counts.get(name,0)])!=expected:raise ValueError('Prior context/source rows changed')
    if fingerprint([row for row in rows['objects'] if row['id']!=context.TARGET])!=other_objects_hash:
        raise ValueError('Other objects changed')
    owner=next(row for row in rows['objects'] if row['id']==context.TARGET)
    changed_owner_keys={name for name in set(old_owner)|set(owner) if old_owner.get(name)!=owner.get(name)}
    allowed={'model_analysis_layer_ids','model_depth_context_ids','capabilities','evidence_links','source_ids',
             'linked_source_count','section_fingerprints','fingerprint'}
    if changed_owner_keys-allowed:raise ValueError('Unexpected owner change')
    for name,value in old_owner['capabilities'].items():
        if owner['capabilities'].get(name)!=value:raise ValueError('Prior capability changed')
    for name,value in old_owner['section_fingerprints'].items():
        if owner['section_fingerprints'].get(name)!=value:raise ValueError('Prior section fingerprint changed')
    for name,value in contract['manifest_fields'].items():
        if name in bundle['manifest']:raise ValueError('Context version already exists')
        bundle['manifest'][name]=value
    key='south_java_model_context_append_v1'
    if key in bundle['manifest']:raise ValueError('Context append already recorded')
    bundle['manifest'][key]={'contract_sha256':digest((ROOT/context.FILE).read_bytes()),
        'source_input_sha256':contract['input_sha256'],'parent_logical_sha256':PARENT_SHA,
        'physical_dimension_admission':False}
    if any(bundle['manifest'][name]!=value for name,value in original_manifest.items()):
        raise ValueError('Original generator/source manifest changed')
    after_counts={name:len(values) for name,values in rows.items()}
    if sum(after_counts.values())!=sum(counts.values())+7 or len(rows['widths'])!=172:
        raise ValueError('Unexpected candidate record/width count')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    candidate=OUTPUT/'candidate.json'
    if candidate.exists():raise ValueError('Do not overwrite an earlier candidate')
    with candidate.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(bundle,stream,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':'))
        stream.write('\n')
    if candidate.stat().st_size>210000000:raise ValueError('Candidate exceeded reviewed byte budget')
    expected_rows=contract['collections'];expected_owner=owner
    del bundle,rows,old_owner,original_manifest
    gc.collect()
    checks=[]
    def query(request, expected):
        command=[str(cli),str(candidate),'-']
        result=subprocess.run(command,input=json.dumps(request).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              cwd=ROOT,timeout=180)
        try:actual=decode_native_result(result)
        except ValueError as error:
            failure={'schema':'osw.south-java-model-layer-cloud-failure.v1','status':'NATIVE_QUERY_FAILED',
                'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
                'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'native_return_code':result.returncode,
                'error':str(error),'parent_append_preservation_verified':True,
                'native_queries_completed':len(checks),'failed_query':request,
                'installed_assets_modified':False,'candidate_uploaded':False}
            (OUTPUT/'failure.json').write_text(json.dumps(failure,indent=2)+'\n')
            raise
        if actual['total']!=len(expected) or context.encoded(actual['rows'])!=context.encoded(sorted(expected,key=lambda row:row['id'])):
            raise ValueError('Native result differs from exact prepared rows')
        checks.append({'collection':request['collection'],'filters':request.get('filters',[]),
                       'total':actual['total'],'row_ids':[row['id'] for row in actual['rows']],
                       'exact_row_values_verified':True})
    def selected(name, field, value):
        return [row for row in expected_rows[name] if row.get(field)==value]
    examples=contract['example_queries']
    expected=[expected_rows[context.LAYERS],selected(context.DEPTHS,'entity_id',context.TARGET),
              selected(context.DEPTHS,'source_feature','SJCU'),[row for row in expected_rows[context.DEPTHS] if 'depth_cap_m' in row]]
    for request,records in zip(examples,expected):query({**request,'sort':{'field':'id'}},records)
    for name,field,value in [(context.LAYERS,'entity_id',None),(context.DEPTHS,'physical_width_km',None),
                             (context.DEPTHS,'physical_width_km',0),(context.DEPTHS,'physical_state_join_eligible',True)]:
        query({'collection':name,'filters':[{'field':field,'op':'eq','value':value}],'sort':{'field':'id'},'limit':100},
              selected(name,field,value))
    query({'collection':'objects','filters':[{'field':'id','op':'eq','value':context.TARGET}],'limit':100},[expected_owner])
    for source_id in [context.PAPER,context.METHOD]:
        query({'collection':'sources','filters':[{'field':'id','op':'eq','value':source_id}],'limit':100},
              selected('sources','id',source_id))
    with candidate.open('rb') as stream:candidate_sha256=hashlib.file_digest(stream,'sha256').hexdigest()
    with cli.open('rb') as stream:native_sha256=hashlib.file_digest(stream,'sha256').hexdigest()
    report={'schema':'osw.south-java-model-layer-cloud-result.v1','status':'PASS',
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'parent_logical_sha256':PARENT_SHA,'parent_logical_bytes':PARENT_BYTES,
        'preflight_sha256':digest((ROOT/PREFLIGHT).read_bytes()),
        'candidate_logical_sha256':candidate_sha256,'candidate_logical_bytes':candidate.stat().st_size,
        'native_cli_sha256':native_sha256,
        'parent_records':sum(counts.values()),'candidate_records':sum(after_counts.values()),
        'new_context_records':5,'new_provenance_entries':2,'prior_collections_preserved':len(collection_hashes),
        'original_manifest_preserved':True,'prior_context_and_source_prefixes_preserved':True,
        'other_objects_preserved':245,'prior_owner_capabilities_preserved':True,'scoped_width_records_unchanged':172,
        'native_query_checks':checks,'scientific_inputs_unchanged':83,'runtime_inputs_unchanged':23,'verified_ui_inputs_unchanged':20,
        'cloud_source_inputs_verified':len(pref['input_sha256']),'installed_assets_modified':False,
        'new_physical_dimensions_admitted':0,'source_velocity_fields_recomputed':False,
        'wasm_built':False,'browser_verified':False,'candidate_is_temporary_cloud_only':True,
        'candidate_uploaded':False,'main_merged':False}
    (OUTPUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-check',action='store_true')
    parser.add_argument('--preflight-only',action='store_true')
    parser.add_argument('--cli')
    args=parser.parse_args()
    if not args.cloud_check:parser.error('Explicit cloud check required; no packet read')
    pref=verify_controls(dict(os.environ))
    if args.preflight_only:
        print(json.dumps({'status':'SOURCE_PREFLIGHT_PASS','inputs':len(pref['input_sha256'])}));return
    if not args.cli:parser.error('Cloud native CLI required')
    cli=Path(args.cli).resolve()
    if not cli.is_relative_to(ROOT/'.pytest_cache/south-java-model-layer-cloud-build-v1/target') or not cli.is_file():
        raise ValueError('Expected freshly built cloud CLI')
    run(cli,pref)


if __name__=='__main__':
    main()
