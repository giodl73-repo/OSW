"""Verify the exact saved EAC candidate in a browser; no build or installation."""
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from install_published_current_speed_saved_v1 import extract_candidate
import eac_mean_core_query_v1 as query
import eac_mean_core_delivery_v1 as delivery

ROOT=query.ROOT
OUT=ROOT/'.pytest_cache/eac-mean-core-browser-resume-v1'
REQUEST='research/eac-mean-core-browser-resume-request-v1.json'
PREFLIGHT='research/eac-mean-core-browser-resume-preflight-v1.json'
WORKFLOW='.github/workflows/eac-mean-core-browser-resume-v1.yml'
EVIDENCE='research/eac-mean-core-engine-run-v1/engine.json'
ENGINE_SOURCE='c67596d8a89f1f8da11868cca3d24d05bb0bd9b4'
ARTIFACT={'id':12823102905,'bytes':96366209,'sha256':'2b647ca57866b4cadf137b14aaca312eae765ee9c2c183d06d4e6f5ed5d7ca2a'}


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
            or os.environ.get('OSW_EAC_MEAN_CORE_BROWSER_RESUME_V1')!='1'
            or os.environ.get('OSW_EAC_MEAN_CORE_DELIVERY_V1')!='1'):
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
            or engine.get('logical_sha256')!='23f70fec771c7302b2351d8d254ec0acc988397543eb96d233ac10385b384ffb'
            or engine.get('logical_bytes')!=190579739
            or engine.get('wasm_sha256')!='f7d4f6eca6fb1c85ca8b27c9bf0d72682804d98ac6e335e2e7b46e822a64f9d0'
            or engine.get('rust_tests_passed')!=248 or engine.get('main_query_comparisons')!=99
            or engine.get('source_query_comparisons')!=35 or engine.get('complete_api_comparisons')!=3
            or engine.get('prior_speed_whole_responses_preserved')!=2 or engine.get('browser_verified') is not False
            or engine.get('new_mean_core_section_records')!=5 or engine.get('new_width_records')!=0
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


def main():
    source,_=controls()
    if OUT.exists():raise ValueError('Refuse to overwrite execution evidence')
    OUT.mkdir(parents=True)
    engine=read(EVIDENCE);verify_engine(engine)
    from query_packet import read_bundle_bytes
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if hashlib.sha256(raw).hexdigest()!=query.PARENT or len(raw)!=190565683:raise ValueError('Exact installed logical parent required')
    parent=OUT/'parent.json';parent.write_bytes(raw);del raw;gc.collect()
    subprocess.run(['node','--max-old-space-size=1536','analysis/check_eac_mean_core_snapshots_v1.mjs','parent',
        str(ROOT/delivery.WASM),str(parent),str(OUT),delivery.PARENT_WASM,query.PARENT],cwd=ROOT,check=True,timeout=600)
    verify_parent_capture(read('research/eac-mean-core-engine-run-v1/parent-snapshots.json'),read(OUT/'parent-snapshots.json'))
    metadata=json.loads(subprocess.check_output(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}"],timeout=55))
    if (metadata['expired'] or metadata['size_in_bytes']!=ARTIFACT['bytes'] or metadata['digest']!='sha256:'+ARTIFACT['sha256']
            or metadata['workflow_run']['id']!=40700928560 or metadata['workflow_run']['head_sha']!=ENGINE_SOURCE):raise ValueError('Saved artifact metadata differs')
    archive=OUT/'candidate.zip'
    with archive.open('xb') as stream:subprocess.run(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=300)
    if archive.stat().st_size!=ARTIFACT['bytes'] or sha(archive)!=ARTIFACT['sha256']:raise ValueError('Saved ZIP bytes differ')
    hashes=engine['generated_sha256'];extracted=extract_candidate(archive,hashes,sha(EVIDENCE),OUT/'unpacked')
    for path,pin in hashes.items():
        if sha(extracted/path)!=pin:raise ValueError('Saved candidate member differs')
        dst=ROOT/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(extracted/path,dst)
    import eac_mean_core_dashboard_context_v1 as context
    manifest=read(delivery.MANIFEST)
    updated=context.updated_manifest(manifest,source)
    write(delivery.MANIFEST,updated)
    hashes={**hashes,delivery.MANIFEST:sha(delivery.MANIFEST)}
    from check_eac_mean_core_browser_v2 import browser_review
    write(OUT/'browser.json',browser_review(ROOT,OUT))
    for path,pin in hashes.items():
        if sha(path)!=pin:raise ValueError('Browser changed saved candidate')
    context.verify_manifest_delta(manifest,read(delivery.MANIFEST),source)
    shutil.copyfile(ROOT/EVIDENCE,OUT/'engine.json')
    shutil.copyfile(ROOT/delivery.MANIFEST,OUT/'engine-manifest.json')
    write(OUT/'result.json',{**engine,'browser_verified':True,'browser_source_commit':source,
        'browser_run_id':os.environ['GITHUB_RUN_ID'],'browser_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_artifact':ARTIFACT,'saved_engine_evidence_sha256':sha(EVIDENCE),
        'browser_harness_sha256':sha('analysis/check_eac_mean_core_browser_v2.py'),
        'generated_sha256':hashes,'presentation_contract_sha256':sha(context.FILE),
        'parent_engine_manifest_sha256':context.sha(context.OLD),'manifest_updated_for_presentation':True,
        'native_or_wasm_rebuild':False,'runtime_assets_changed':True,'scientific_data_or_wasm_changed':False,'visual_review_complete':False,'installed':False,'full_goal_complete':False})


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'installed':False})
        raise
