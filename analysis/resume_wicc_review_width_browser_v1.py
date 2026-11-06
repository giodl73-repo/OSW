"""Review the exact saved WICC engine in one cloud browser job; no rebuild."""
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from install_published_current_speed_saved_v1 import extract_candidate
import published_wicc_review_width_v1 as core
import wicc_review_width_delivery_v1 as delivery

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/wicc-review-width-browser-resume-v1'
REQUEST='research/wicc-review-width-browser-resume-request-v1.json'
PREFLIGHT='research/wicc-review-width-browser-resume-preflight-v1.json'
EVIDENCE='research/wicc-review-width-engine-run-v1/engine.json'
ARTIFACT={'id':12798651340,'bytes':96271344,'sha256':'ade6f51185032f8907d034321f7b2bf8c08123b20cee8930e716a528bfaf4b3f'}
ENGINE_SOURCE='93ae2beb342200f39ef22ad9ec91e824ebc9e83c'

def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_WICC_BROWSER_RESUME_V1')!='1'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME')!='push'):raise ValueError('Exact cloud browser resume required')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One numerical worker required')
    request=read(REQUEST)
    if request.get('execute') is not True or request.get('preflight_sha256')!=sha(PREFLIGHT):raise ValueError('Resume disabled or unpinned')
    if request.get('browser_permitted') is not True or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Scoped browser permission missing')
    for key in ['native_build_permitted','wasm_build_permitted','installation_permitted','source_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled')
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Field processing must remain disabled')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen input differs: '+path)
    for path,row in pref['installed_files'].items():
        if sha(path)!=row['sha256']:raise ValueError('Installed parent changed: '+path)
    for path in pref['disabled_requests']:
        doc=read(path)
        if doc.get('execute',doc.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+path)
    source=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    remote=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if source!=remote or source!=os.environ['GITHUB_SHA']:raise ValueError('Exact current source checkout required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean checkout required')
    return source,pref


def verify_engine(engine):
    if (engine.get('status')!='PASS' or engine.get('source_commit')!=ENGINE_SOURCE
        or engine.get('logical_sha256')!='360e775a1dbb49d5c7934cca1f288ab2f2f8cd71bfa8fd1368fb35b086f4e1e0'
        or engine.get('logical_bytes')!=190547331
        or engine.get('wasm_sha256')!='037b6cfcee4d21bff80443bc77e0ab12c797eccc419e4ff39665cb09441e0ee0'
        or engine.get('rust_tests_passed')!=230 or engine.get('main_query_comparisons')!=61
        or engine.get('source_query_comparisons')!=25 or engine.get('complete_api_comparisons')!=3
        or engine.get('prior_speed_whole_responses_preserved')!=2 or len(engine.get('generated_sha256',{}))!=18):
        raise ValueError('Exact verified saved WICC engine required')


def verify_parent_capture(old,new):
    if old.get('status')!='PASS' or new.get('status')!='PASS' or old.get('mode')!='parent' or new.get('mode')!='parent':
        raise ValueError('Successful parent capture required')
    for key in ['wasm_sha256','payload_sha256','checks']:
        if old.get(key)!=new.get(key):raise ValueError('Parent snapshot custody differs: '+key)
    if len(new['checks'])!=3 or {r['view'] for r in new['checks']}!={'atlas','seasons','dashboard'}:
        raise ValueError('Three exact parent APIs required')


def main():
    source,pref=controls()
    if OUT.exists():raise ValueError('Refuse to overwrite browser evidence')
    OUT.mkdir(parents=True)
    engine=read(EVIDENCE);verify_engine(engine)
    # Recapture the installed parent before overlaying any candidate artifacts.
    # This supplies the dashboard baseline, bound to the original run's hashes.
    from query_packet import read_bundle_bytes
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if hashlib.sha256(raw).hexdigest()!=core.PARENT or len(raw)!=190540300:
        raise ValueError('Exact installed logical parent required')
    parent=OUT/'parent.json';parent.write_bytes(raw);del raw;gc.collect()
    subprocess.run(['node','--max-old-space-size=1536','analysis/check_wicc_review_width_snapshots_v1.mjs',
        'parent',str(ROOT/delivery.WASM),str(parent),str(OUT),delivery.PARENT_WASM,core.PARENT],
        cwd=ROOT,env=dict(os.environ,OSW_WICC_REVIEW_WIDTH_SNAPSHOTS_V1='1'),check=True,timeout=600)
    verify_parent_capture(read('research/wicc-review-width-engine-run-v1/parent-snapshots.json'),read(OUT/'parent-snapshots.json'))
    metadata=json.loads(subprocess.check_output(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}"],timeout=55))
    if (metadata['expired'] or metadata['size_in_bytes']!=ARTIFACT['bytes'] or metadata['digest']!='sha256:'+ARTIFACT['sha256']
        or metadata['workflow_run']['id']!=40647043885 or metadata['workflow_run']['head_sha']!=ENGINE_SOURCE):
        raise ValueError('Saved artifact metadata differs')
    archive=OUT/'candidate.zip'
    with archive.open('xb') as stream:
        subprocess.run(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=300)
    if archive.stat().st_size!=ARTIFACT['bytes'] or sha(archive)!=ARTIFACT['sha256']:
        raise ValueError('Saved artifact identity differs')
    hashes=engine['generated_sha256']
    extracted=extract_candidate(archive,hashes,sha(EVIDENCE),OUT/'unpacked')
    for path,pin in hashes.items():
        if sha(extracted/path)!=pin:raise ValueError('Saved candidate member differs')
        dst=ROOT/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(extracted/path,dst)
    manifest=read(delivery.MANIFEST);scope=delivery.scopes()
    for path,pin in {**{p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()},
                     **scope['added_source_sha256'],**scope['source_dependencies_sha256']}.items():
        if manifest['sha256'].get(path)!=pin or sha(path)!=pin:raise ValueError('Saved runtime source differs: '+path)
    from check_wicc_review_width_browser_v2 import browser_review
    write(OUT/'browser.json',browser_review(ROOT,OUT))
    for path,pin in hashes.items():
        if sha(path)!=pin:raise ValueError('Browser changed saved candidate')
    shutil.copyfile(ROOT/EVIDENCE,OUT/'engine.json')
    result={**engine,'browser_verified':True,'browser_source_commit':source,
        'browser_run_id':os.environ['GITHUB_RUN_ID'],'browser_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_artifact':ARTIFACT,'saved_engine_evidence_sha256':sha(EVIDENCE),
        'browser_harness_sha256':sha('analysis/check_wicc_review_width_browser_v2.py'),
        'native_or_wasm_rebuild':False,'runtime_assets_changed':False,'visual_review_complete':False,'installed':False,'full_goal_complete':False}
    write(OUT/'result.json',result)


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'installed':False})
        raise

