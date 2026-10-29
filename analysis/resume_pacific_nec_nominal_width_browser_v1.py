"""Verify the exact saved basin candidate with object readiness; no build or installation."""
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from install_published_current_speed_saved_v1 import extract_candidate
import pacific_nec_nominal_width_query_v1 as query
import pacific_nec_nominal_width_delivery_v2 as delivery
import pacific_nec_nominal_width_runtime_v2 as runtime

ROOT=query.ROOT
OUT=ROOT/'.pytest_cache/pacific-nec-nominal-width-browser-resume-v1'
REQUEST='research/pacific-nec-nominal-width-browser-resume-request-v1.json'
PREFLIGHT='research/pacific-nec-nominal-width-browser-resume-preflight-v1.json'
WORKFLOW='.github/workflows/pacific-nec-nominal-width-browser-resume-v1.yml'
EVIDENCE='research/pacific-nec-nominal-width-engine-run-v2/engine.json'
ENGINE_SOURCE='624e8601d39e5e6459a9d23688b19ba6496885c8'
ARTIFACT={'id':12873661202,'bytes':96505620,'sha256':'0938ec1a179cd7155b30d149581591f57817b5684f3b8d61763d0c298143433f'}


def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')


def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME')!='push'
            or os.environ.get('OSW_PACIFIC_NEC_NOMINAL_WIDTH_BROWSER_RESUME_V1')!='1'
            or os.environ.get('OSW_PACIFIC_NEC_NOMINAL_WIDTH_DELIVERY_V1')!='1'):
        raise ValueError('Exact cloud browser resume and pinned harness environment required')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('Single worker required: '+key)
    request=read(REQUEST)
    if (request.get('execute') is not True or request.get('workflow')!=WORKFLOW
            or request.get('preflight_sha256')!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1
            or request.get('max_heavy_local_jobs')!=0 or request.get('browser_permitted') is not True
            or request.get('cloud_candidate_files_permitted') is not True):raise ValueError('Resume disabled or changed')
    for key in ['native_build_permitted','wasm_build_permitted','installation_permitted','source_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled: '+key)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Original field processing must stay disabled')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen input differs: '+path)
    for path,row in pref['installed_files'].items():
        if sha(path)!=row['sha256']:raise ValueError('Installed parent differs: '+path)
    for path in pref['disabled_requests']:
        r=read(path)
        if r.get('execute',r.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+path)
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    remote=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head!=remote or head!=os.environ['GITHUB_SHA']:raise ValueError('Exact current checkout required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain'],cwd=ROOT).strip():raise ValueError('Clean checkout required')
    return head,pref


def verify_engine(engine):
    if (engine.get('status')!='PASS' or engine.get('source_commit')!=ENGINE_SOURCE
            or engine.get('logical_sha256')!='3e8dad713d264d5ae4bd4538a503a695174444f2e190803da445b72e62229a38'
            or engine.get('logical_bytes')!=190686988
            or engine.get('wasm_sha256')!='68c9b946ee919198987dfabc48ecba510b3ae187173443fb89ae112a3690fcad'
            or engine.get('rust_tests_passed')!=282 or engine.get('main_query_comparisons')!=215
            or engine.get('source_query_comparisons')!=79 or engine.get('complete_api_comparisons')!=3
            or engine.get('complete_object_api_comparisons')!=7 or engine.get('prior_speed_whole_responses_preserved')!=2
            or engine.get('browser_verified') is not False or engine.get('new_identity_records')!=0
            or engine.get('new_width_records')!=1 or engine.get('new_length_records')!=0
            or engine.get('new_independent_observations')!=0 or engine.get('installed') is not False
            or len(engine.get('generated_sha256',{}))!=18
            or engine['generated_sha256'].get('almanac/query-engine.manifest.json')!='0f5a5b1a32f0b1602687ed2ecb6bdda7e110a26ad07947f4fd7a3cf7f7b9572d'
            or engine['generated_sha256'].get('almanac/index-catalog.json')!='37c952c060d812bdde797b11d76d3673829dd1459e50635974763f03e38c3243'):
        raise ValueError('Exact independently verified saved basin engine required')
    audit=engine.get('source_index_audit',{})
    if (audit.get('original_source_strings_preserved')!=639 or audit.get('original_sources_verified')!=639
        or audit.get('replaced_source_paths')!=[] or audit.get('scientific_source_documents_replaced')!=0
        or audit.get('added_source_paths')!=sorted([query.FILE,query.nominal.FACTS,query.nominal.FILE])):
        raise ValueError('Saved source-string preservation differs')


def verify_parent_capture(old,new):
    if old.get('status')!='PASS' or new.get('status')!='PASS' or old.get('mode')!='parent' or new.get('mode')!='parent':
        raise ValueError('Successful parent capture required')
    for key in ['wasm_sha256','payload_sha256','checks']:
        if old.get(key)!=new.get(key):raise ValueError('Parent snapshot custody differs: '+key)
    if len(new['checks'])!=3 or {r['view'] for r in new['checks']}!={'atlas','seasons','dashboard'}:
        raise ValueError('Three exact parent APIs required')


def verify_active_sources(manifest):
    scope=runtime.scopes()
    expected={}
    for pins in [{p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()},
            scope['added_source_sha256'],scope['source_dependencies_sha256'],scope['candidate_rust_source_sha256']]:
        for path,pin in pins.items():
            if path in expected and expected[path]!=pin:raise ValueError('Conflicting active source pin: '+path)
            expected[path]=pin
    for path,pin in expected.items():
        if manifest['sha256'].get(path)!=pin or sha(path)!=pin:
            raise ValueError('Saved active engine source changed: '+path)
    return {'active_source_files':len(expected),'historical_manifest_preserved':True}


def main():
    source,_=controls()
    if OUT.exists():raise ValueError('Refuse to overwrite execution evidence')
    OUT.mkdir(parents=True)
    engine=read(EVIDENCE);verify_engine(engine)
    from query_packet import read_bundle_bytes
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if hashlib.sha256(raw).hexdigest()!=query.PARENT or len(raw)!=190678008:raise ValueError('Exact installed logical parent required')
    parent=OUT/'parent.json';parent.write_bytes(raw);del raw;gc.collect()
    subprocess.run(['node','--max-old-space-size=1536','analysis/check_pacific_nec_nominal_width_snapshots_v1.mjs','parent',
        str(ROOT/delivery.WASM),str(parent),str(OUT),delivery.PARENT_WASM,query.PARENT],cwd=ROOT,check=True,timeout=600)
    verify_parent_capture(read('research/pacific-nec-nominal-width-engine-run-v2/parent-snapshots.json'),read(OUT/'parent-snapshots.json'))
    metadata=json.loads(subprocess.check_output(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}"],timeout=55))
    if (metadata['expired'] or metadata['size_in_bytes']!=ARTIFACT['bytes'] or metadata['digest']!='sha256:'+ARTIFACT['sha256']
            or metadata['workflow_run']['id']!=40815058182 or metadata['workflow_run']['head_sha']!=ENGINE_SOURCE):raise ValueError('Saved artifact metadata differs')
    archive=OUT/'candidate.zip'
    with archive.open('xb') as stream:subprocess.run(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=300)
    if archive.stat().st_size!=ARTIFACT['bytes'] or sha(archive)!=ARTIFACT['sha256']:raise ValueError('Saved ZIP bytes differ')
    hashes=engine['generated_sha256'];extracted=extract_candidate(archive,hashes,sha(EVIDENCE),OUT/'unpacked')
    for path,pin in hashes.items():
        if sha(extracted/path)!=pin:raise ValueError('Saved candidate member differs')
        dst=ROOT/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(extracted/path,dst)
    manifest=read(delivery.MANIFEST)
    if manifest!=read('research/pacific-nec-nominal-width-engine-run-v2/engine-manifest.json'):
        raise ValueError('Saved engine manifest differs from independently retained evidence')
    verify_active_sources(manifest)
    from check_pacific_nec_nominal_width_browser_v2 import browser_review
    observed=browser_review(ROOT,OUT)
    if observed.get('actual_screenshots')!=82:raise ValueError('Eighty-two complete browser captures required')
    write(OUT/'browser.json',observed)
    for path,pin in hashes.items():
        if sha(path)!=pin:raise ValueError('Browser changed saved candidate')
    if read(delivery.MANIFEST)!=manifest:raise ValueError('Browser changed engine manifest')
    shutil.copyfile(ROOT/EVIDENCE,OUT/'engine.json')
    shutil.copyfile(ROOT/delivery.MANIFEST,OUT/'engine-manifest.json')
    write(OUT/'result.json',{**engine,'browser_verified':True,'browser_source_commit':source,
        'browser_run_id':os.environ['GITHUB_RUN_ID'],'browser_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_artifact':ARTIFACT,'saved_engine_evidence_sha256':sha(EVIDENCE),
        'browser_harness_sha256':sha('analysis/check_pacific_nec_nominal_width_browser_v2.py'),
        'generated_sha256':hashes,'manifest_updated_for_presentation':False,
        'native_or_wasm_rebuild':False,'runtime_assets_changed':False,'scientific_data_or_wasm_changed':False,'visual_review_complete':False,'installed':False,'full_goal_complete':False})


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':write(OUT/'resume-failure.json',{'status':'FAIL','error':str(error)[:4000],'installed':False})
        raise
