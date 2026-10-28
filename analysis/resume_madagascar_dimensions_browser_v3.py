"""Verify the exact saved Madagascar candidate in a browser; no build or installation."""
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from install_published_current_speed_saved_v1 import extract_candidate
import madagascar_dimensions_query_v1 as query
import madagascar_dimensions_delivery_v5 as delivery
import madagascar_dimensions_runtime_v4 as runtime

ROOT=query.ROOT
OUT=ROOT/'.pytest_cache/madagascar-dimensions-browser-resume-v3'
REQUEST='research/madagascar-dimensions-browser-resume-request-v3.json'
PREFLIGHT='research/madagascar-dimensions-browser-resume-preflight-v3.json'
WORKFLOW='.github/workflows/madagascar-dimensions-browser-resume-v3.yml'
EVIDENCE='research/madagascar-dimensions-engine-run-v5/engine.json'
ENGINE_SOURCE='0bd52f559de7a7133b5fe5a196f479055353a0ce'
ARTIFACT={'id':12838474693,'bytes':96400134,'sha256':'1a52416f7b4cb912477de8d312b42707cb9ccd51ae92d08445859db96898ce4c'}


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
            or os.environ.get('OSW_MADAGASCAR_DIMENSIONS_BROWSER_RESUME_V3')!='1'
            or os.environ.get('OSW_MADAGASCAR_DIMENSIONS_DELIVERY_V5')!='1'):
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
            or engine.get('logical_sha256')!='b00b870ae929172cf5108b08066541fd31d5bf602ef86f4142819fdf91e11049'
            or engine.get('logical_bytes')!=190594973
            or engine.get('wasm_sha256')!='d32afcbfa6de6cc3f195e3cbb9dab881196f58f36d1a2776f92963d05c10c516'
            or engine.get('rust_tests_passed')!=256 or engine.get('main_query_comparisons')!=117
            or engine.get('source_query_comparisons')!=45 or engine.get('complete_api_comparisons')!=3
            or engine.get('prior_speed_whole_responses_preserved')!=2 or engine.get('browser_verified') is not False
            or engine.get('new_flow_event_references')!=8 or engine.get('new_width_records')!=1
            or engine.get('new_length_records')!=0 or engine.get('new_independent_observations')!=0
            or engine.get('installed') is not False or len(engine.get('generated_sha256',{}))!=18):
        raise ValueError('Exact independently verified saved engine required')


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
    if hashlib.sha256(raw).hexdigest()!=query.PARENT or len(raw)!=190579739:raise ValueError('Exact installed logical parent required')
    parent=OUT/'parent.json';parent.write_bytes(raw);del raw;gc.collect()
    subprocess.run(['node','--max-old-space-size=1536','analysis/check_madagascar_dimensions_snapshots_v5.mjs','parent',
        str(ROOT/delivery.WASM),str(parent),str(OUT),delivery.PARENT_WASM,query.PARENT],cwd=ROOT,check=True,timeout=600)
    verify_parent_capture(read('research/madagascar-dimensions-engine-run-v5/parent-snapshots.json'),read(OUT/'parent-snapshots.json'))
    metadata=json.loads(subprocess.check_output(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}"],timeout=55))
    if (metadata['expired'] or metadata['size_in_bytes']!=ARTIFACT['bytes'] or metadata['digest']!='sha256:'+ARTIFACT['sha256']
            or metadata['workflow_run']['id']!=40739985519 or metadata['workflow_run']['head_sha']!=ENGINE_SOURCE):raise ValueError('Saved artifact metadata differs')
    archive=OUT/'candidate.zip'
    with archive.open('xb') as stream:subprocess.run(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=300)
    if archive.stat().st_size!=ARTIFACT['bytes'] or sha(archive)!=ARTIFACT['sha256']:raise ValueError('Saved ZIP bytes differ')
    hashes=engine['generated_sha256'];extracted=extract_candidate(archive,hashes,sha(EVIDENCE),OUT/'unpacked')
    for path,pin in hashes.items():
        if sha(extracted/path)!=pin:raise ValueError('Saved candidate member differs')
        dst=ROOT/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(extracted/path,dst)
    manifest=read(delivery.MANIFEST)
    if manifest!=read('research/madagascar-dimensions-engine-run-v5/engine-manifest.json'):
        raise ValueError('Saved engine manifest differs from independently retained evidence')
    verify_active_sources(manifest)
    from check_madagascar_dimensions_browser_v7 import browser_review
    write(OUT/'browser.json',browser_review(ROOT,OUT))
    for path,pin in hashes.items():
        if sha(path)!=pin:raise ValueError('Browser changed saved candidate')
    if read(delivery.MANIFEST)!=manifest:raise ValueError('Browser changed engine manifest')
    shutil.copyfile(ROOT/EVIDENCE,OUT/'engine.json')
    shutil.copyfile(ROOT/delivery.MANIFEST,OUT/'engine-manifest.json')
    write(OUT/'result.json',{**engine,'browser_verified':True,'browser_source_commit':source,
        'browser_run_id':os.environ['GITHUB_RUN_ID'],'browser_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_artifact':ARTIFACT,'saved_engine_evidence_sha256':sha(EVIDENCE),
        'browser_harness_sha256':sha('analysis/check_madagascar_dimensions_browser_v7.py'),
        'generated_sha256':hashes,'manifest_updated_for_presentation':False,
        'native_or_wasm_rebuild':False,'runtime_assets_changed':False,'scientific_data_or_wasm_changed':False,'visual_review_complete':False,'installed':False,'full_goal_complete':False})


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':write(OUT/'resume-failure.json',{'status':'FAIL','error':str(error)[:4000],'installed':False})
        raise
