"""Verify saved artifacts, revise four UI assets, run one cloud browser. No build."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from install_published_current_speed_saved_v1 import extract_candidate

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/seasonal-core-velocity-browser-resume-v1'
REQUEST='research/seasonal-core-velocity-browser-resume-request-v1.json'
PREFLIGHT='research/seasonal-core-velocity-browser-resume-preflight-v2.json'
REVISION='research/seasonal-core-velocity-browser-revision-v2.json'
EVIDENCE='research/seasonal-core-velocity-engine-evidence-v1.json'
KEY='published_seasonal_core_velocity_browser_revision_v1'
ARTIFACT={'id':12787263106,'bytes':96204707,'sha256':'e97c2e096341da184a244de8199ffcf5f4193ebb3d0e88ef1b60a495314f856b'}


def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())


def revise_manifest(parent,revision,*,source_commit,verification_inputs):
    if KEY in parent:raise ValueError('UI revision already applied')
    if parent['sha256'].get('almanac/query-engine.wasm')!='6caf567278cb644eed9a45c89028bcadf7d919bb4adba6381503af34fe3e0c16':raise ValueError('Exact saved binary required')
    expected={'almanac/published-current-speeds.js','almanac/query.html','almanac/reference-routes.html','almanac/seasons.html'}
    if set(revision['runtime_source_changes'])!=expected:raise ValueError('Only four UI assets may change')
    result=copy.deepcopy(parent)
    for path,row in revision['runtime_source_changes'].items():
        if parent['sha256'].get(path)!=row['historical_sha256']:raise ValueError('Saved UI source differs')
        result['sha256'][path]=row['candidate_sha256']
    result[KEY]={'source_commit':source_commit,'verified_engine_source_commit':'e66cb4fdeda19f98d4a6cd1a34e405869b7916f4',
                 'saved_engine_manifest_sha256':'f286c4705ec666456b4ef7b4cc9d912c61080a0494009faacdd700aa5ba89b3c',
                 'logical_sha256':'c27c5c8319ab59fa6069274df1b7d19c87cf5a2aea8a7a04ba808a1636b9e212',
                 'wasm_sha256':'6caf567278cb644eed9a45c89028bcadf7d919bb4adba6381503af34fe3e0c16',
                 'runtime_source_changes':copy.deepcopy(revision['runtime_source_changes']),
                 'verification_source_sha256':dict(verification_inputs),'native_or_wasm_rebuild':False}
    if any(result[k]!=parent[k] for k in parent if k!='sha256'):raise ValueError('Saved engine namespace changed')
    if {p for p in parent['sha256'] if result['sha256'][p]!=parent['sha256'][p]}!=expected:raise ValueError('Unrelated source pin changed')
    return result


def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_CORE_BROWSER_RESUME_V1')!='1'
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


def main():
    source,pref=controls()
    if OUT.exists():raise ValueError('Refuse to overwrite browser evidence')
    OUT.mkdir(parents=True)
    engine=read(EVIDENCE)
    if (engine['status']!='PASS' or engine['source_commit']!='e66cb4fdeda19f98d4a6cd1a34e405869b7916f4'
            or engine['logical_sha256']!='c27c5c8319ab59fa6069274df1b7d19c87cf5a2aea8a7a04ba808a1636b9e212'
            or engine['logical_bytes']!=190528544 or engine['wasm_sha256']!='6caf567278cb644eed9a45c89028bcadf7d919bb4adba6381503af34fe3e0c16'
            or engine['rust_tests_passed']!=216 or engine['main_query_comparisons']!=41 or engine['source_query_comparisons']!=20
            or engine['complete_api_comparisons']!=2 or engine['pemba_whole_response_preserved'] is not True):raise ValueError('Verified engine evidence required')
    archive=OUT/'candidate.zip'
    with archive.open('xb') as f:subprocess.run(['gh','api',f"repos/giodl73-repo/OSW/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=f,check=True,timeout=300)
    if archive.stat().st_size!=ARTIFACT['bytes'] or sha(archive)!=ARTIFACT['sha256']:raise ValueError('Saved artifact identity differs')
    hashes=engine['generated_sha256']
    if len(hashes)!=18:raise ValueError('Exact eighteen-file saved candidate required')
    extracted=extract_candidate(archive,hashes,sha(EVIDENCE),OUT/'unpacked')
    for path,pin in hashes.items():
        if sha(extracted/path)!=pin:raise ValueError('Saved candidate member differs')
        dst=ROOT/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(extracted/path,dst)
    manifest_path='almanac/query-engine.manifest.json';original=read(manifest_path)
    shutil.copyfile(ROOT/manifest_path,OUT/'source-engine-manifest.json')
    revision=read(REVISION)
    scientific=revision['scientific_source_file']
    if original['sha256'].get(scientific)!=revision['scientific_source_sha256'] or sha(scientific)!=revision['scientific_source_sha256']:raise ValueError('Scientific source differs from saved engine')
    for path,row in revision['runtime_source_changes'].items():
        if sha(row['archive_path'])!=row['historical_sha256'] or sha(path)!=row['candidate_sha256']:raise ValueError('UI revision source custody differs')
    updated=revise_manifest(original,revision,source_commit=source,verification_inputs=pref['input_sha256'])
    write(manifest_path,updated);hashes=dict(hashes);hashes[manifest_path]=sha(manifest_path)
    shutil.copyfile(ROOT/manifest_path,OUT/'candidate-engine-manifest.json')
    from check_seasonal_core_velocity_browser_v3 import browser_review
    write(OUT/'browser.json',browser_review(ROOT,OUT))
    for path,pin in hashes.items():
        if sha(path)!=pin:raise ValueError('Browser changed candidate')
        dst=OUT/'artifact'/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dst)
    result={**engine,'generated_sha256':hashes,'browser_verified':True,'browser_source_commit':source,'engine_run_id':40620738758,
            'browser_run_id':os.environ['GITHUB_RUN_ID'],'browser_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
            'saved_artifact':ARTIFACT,'native_or_wasm_rebuild':False,'visual_review_complete':False,'installed':False,'full_goal_complete':False}
    write(OUT/'engine.json',result);write(OUT/'result.json',result)


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'installed':False})
        raise
