"""One cloud CPU: compile/test the prepared batch without processing runtime data."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/current-reference-profile-native-request-v1.json'
PREFLIGHT='research/current-reference-profile-native-preflight-v1.json'
WORKFLOW='.github/workflows/current-reference-profile-native-v1.yml'
OUT=ROOT/'.pytest_cache/current-reference-profile-native-v1'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW'+path],timeout=55))
def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('RUNNER_OS')!='Linux'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
        or os.environ.get('GITHUB_EVENT_NAME')!='push' or os.environ.get('OSW_REFERENCE_PROFILE_NATIVE_V1')!='1'):
        raise ValueError('Scoped cloud native qualification only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One low-priority CPU required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','CARGO_BUILD_JOBS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    r=read(REQUEST)
    for key,value in {'schema':'osw.current-reference-profile-native-request.v1','workflow':WORKFLOW,'execute':True,'native_tests_permitted':True,'installed_asset_hashing_permitted':True,'max_cloud_jobs':1,'max_heavy_local_jobs':0}.items():
        if type(r.get(key)) is not type(value) or r[key]!=value:raise ValueError('Disabled or changed request: '+key)
    for key in ['runtime_packet_parse_permitted','wasm_build_permitted','browser_permitted','source_index_registration_permitted','ocean_field_processing_permitted','working_branch_installation_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        if r.get(key) is not False:raise ValueError('Unrelated operation enabled: '+key)
    if sha(PREFLIGHT)!=r['preflight_sha256']:raise ValueError('Changed preflight')
    pref=read(PREFLIGHT)
    for p,pin in pref['input_sha256'].items():
        if sha(p)!=pin:raise ValueError('Changed frozen input: '+p)
    for p,row in pref['installed_files'].items():
        if (ROOT/p).stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:raise ValueError('Installed artifact changed: '+p)
    for p in pref['disabled_requests']:
        old=read(p)
        if old.get('execute',old.get('execution_permitted')) is not False:raise ValueError('Another request enabled: '+p)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad processing enabled')
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    if head!=os.environ['GITHUB_SHA'] or api('/git/ref/heads/codex/current-measurement-gaps')['object']['sha']!=head or api('/git/ref/heads/main')['object']['sha']!=MAIN:raise ValueError('Source or main moved')
    parents=subprocess.check_output(['git','-c','core.fsmonitor=false','show','-s','--format=%P','HEAD']).decode().strip().split()
    if parents!=[pref['source_parent_commit']] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact source parent required')
    return pref
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    pref=controls()
    if args.preflight_only:print('PASS_FROZEN_CLOUD_NATIVE_QUALIFICATION_PREFLIGHT');return
    OUT.mkdir(parents=True,exist_ok=False)
    import current_reference_profile_batch_query_v1 as query
    if query.encoded(query.build_contract())!=(ROOT/query.FILE).read_bytes():raise ValueError('Frozen scientific contract differs')
    compiler=subprocess.check_output(['rustc','+1.95.0','--version']).decode().strip()
    if not compiler.startswith('rustc 1.95.0 '):raise ValueError('Pinned compiler required')
    env=dict(os.environ,CARGO_TARGET_DIR=str(OUT/'build'),CARGO_INCREMENTAL='0')
    with (OUT/'rust-tests.txt').open('wb') as log:
        subprocess.run(['cargo','+1.95.0','test','--locked','--manifest-path','rust/osw-query/Cargo.toml','--lib'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=2400)
    if b'test result: ok. 326 passed; 0 failed;' not in (OUT/'rust-tests.txt').read_bytes():raise ValueError('Expected all326 Rust regression tests')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Tracked input changed')
    write(OUT/'result.json',{'schema':'osw.current-reference-profile-native-result.v1','status':'PASS_COMPLETE_NATIVE_REGRESSIONS_DELIVERY_PENDING','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'rust_tests_passed':326,'rustc':compiler,'rust_tests_log_sha256':sha(OUT.relative_to(ROOT)/'rust-tests.txt'),'frozen_input_count':len(pref['input_sha256']),'installed_files_preserved':21,'runtime_packet_parsed':False,'source_index_registered':False,'wasm_built':False,'browser_reviewed':False,'installed':False,'main_updated':False,'full_goal_complete':False})
    print('PASS326 Rust regression tests; complete native/WASM and browser delivery remain pending.')
if __name__=='__main__':
    try:main()
    except Exception as e:
        if os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error_type':type(e).__name__,'error':str(e)[:1500],'source_commit':os.environ.get('GITHUB_SHA'),'installed':False})
        raise
