"""Allow one exact source-only cloud compilation/parity case; never source acquisition."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess

REQUEST='research/current-local-extent-query-check-request-v2.json'
PREFLIGHT='research/current-local-extent-query-check-preflight-v2.json'
PHASE='research/current-gap-delivery-phase.json'
WORKFLOW='.github/workflows/current-local-extent-query-check-v2.yml'
EXECUTED='research/eacc-coastal-reference-extent-preflight-v1.json'
EXECUTED_SHA='f3c4bbc838386cfa69199716d512a6791146f7cd1f81cfb7079a9ee3fea239d1'
PARENT='3ad6e8e5071709d74d838057bac044132d78ecab'
DATA='research/eacc-local-extent-evidence-bundle-v1.json'
DATA_SHA='e4ca7c532c39d22efc2d6600a89424f48558669fe6e6682b1c6ec9442d00cdf8'
PROTOCOL='plans/current-local-extent-query-small-target-v2.md'
ROLES='signals/roles/check/current-local-extent-query-v2-roles-check-2026-10-24.md'
INPUTS={
    'rust/osw-query/src/local_extents.rs','rust/osw-query/src/lib.rs','rust/osw-query/src/main.rs',
    'rust/osw-query/src/scalar_query.rs','rust/osw-query/Cargo.toml','rust/osw-query/Cargo.lock',
    'rust/osw-local-extents/src/lib.rs','rust/osw-local-extents/src/main.rs',
    'rust/osw-local-extents/Cargo.toml','rust/osw-local-extents/Cargo.lock',
    'analysis/check_current_local_extent_query_parity_v2.mjs',
    'analysis/check_current_local_extent_query_cloud_v2.py','analysis/test_current_local_extent_query_cloud_v2.py',
    'analysis/check_current_local_extent_query_cloud_v1.py','analysis/test_current_local_extent_query_cloud_v1.py',
    'research/eacc-local-extent-evidence-preparation-v1.json',
    'research/current-local-extent-query-parity-result-v1.json',
    'research/current-local-extent-query-execution-review-v1.json',
    DATA,EXECUTED,PROTOCOL,ROLES,WORKFLOW}
IMMUTABLE_FROM_PARENT={'rust/osw-query/Cargo.toml','rust/osw-query/Cargo.lock','rust/osw-query/src/main.rs',
    'analysis/check_current_local_extent_query_cloud_v1.py','analysis/test_current_local_extent_query_cloud_v1.py',
    'research/eacc-local-extent-evidence-preparation-v1.json',
    'research/current-local-extent-query-parity-result-v1.json',
    'research/current-local-extent-query-execution-review-v1.json',DATA,EXECUTED}
ALLOWED_CHANGES=(INPUTS-IMMUTABLE_FROM_PARENT)|{
    REQUEST,PREFLIGHT,'.gitattributes','plans/current-gap-execution-sequence.md'}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(root,name):
    path=(root/name).resolve()
    if not path.is_relative_to(root) or path.stat().st_size>4194304:raise ValueError('Unsafe/oversized cloud input')
    return path.read_bytes()
def git(root,*args):
    return subprocess.check_output(['git','-c','core.fsmonitor=false','-c','maintenance.auto=0',
        '-c','gc.auto=0','-C',str(root),*args])


def verify(root,env):
    root=Path(root).resolve()
    if (env.get('GITHUB_ACTIONS')!='true' or env.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or env.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
            or env.get('RUNNER_OS')!='Linux' or Path(env.get('GITHUB_WORKSPACE','')).resolve()!=root):
        raise ValueError('Requires declared cloud working branch')
    affinity=getattr(os,'sched_getaffinity',None)
    workers=('CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')
    if affinity is None or len(affinity(0))!=1 or any(env.get(k)!='1' for k in workers):
        raise ValueError('One actual CPU/build job/test thread/numerical worker required')
    if (not re.fullmatch('[0-9a-f]{40}',env.get('GITHUB_SHA',''))
            or git(root,'rev-parse','HEAD').decode().strip()!=env['GITHUB_SHA']
            or git(root,'status','--porcelain','--untracked-files=no').strip()
            or any(not re.fullmatch('[1-9][0-9]*',env.get(k,'')) for k in ('GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT'))):
        raise ValueError('Clean exact committed source and run identity required')
    request_raw=read(root,REQUEST);request=json.loads(request_raw)
    phase_raw=read(root,PHASE);phase=json.loads(phase_raw)
    if (request_raw!=git(root,'show','HEAD:'+REQUEST) or phase_raw!=git(root,'show','HEAD:'+PHASE)
            or request.get('schema')!='osw.current-local-extent-query-check-request.v2'
            or request.get('execution_permitted') is not True or request.get('build_verification_only') is not True
            or any(request.get(k) is not False for k in ('provider_requests_permitted','original_source_processing_permitted',
                'measurement_admission_permitted','installed_assets_change_permitted'))
            or request.get('max_heavy_local_jobs')!=0 or request.get('max_cloud_jobs')!=1
            or request.get('workflow')!=WORKFLOW or request.get('preflight')!=PREFLIGHT
            or phase.get('phase')!='source-review-only-v1' or phase.get('heavy_work_permitted') is not False
            or phase.get('max_heavy_local_jobs')!=0 or phase.get('max_heavy_cloud_jobs')!=1):
        raise ValueError('Explicit build-only request and unchanged acquisition hold required')
    raw=read(root,PREFLIGHT);pref=json.loads(raw)
    if (digest(raw)!=request.get('preflight_sha256') or raw!=git(root,'show','HEAD:'+PREFLIGHT)
            or pref.get('schema')!='osw.current-local-extent-query-check-preflight.v2'
            or pref.get('reviewed_parent')!=PARENT or pref.get('python_exact')!='3.14.8'
            or platform.python_version()!='3.14.8' or pref.get('rust_toolchain')!='1.95.0'
            or set(pref.get('input_sha256',{}))!=INPUTS
            or pref.get('max_dedicated_wasm_bytes')!=2097152 or pref.get('max_dedicated_memory_bytes')!=67108864
            or pref.get('baseline_run_id')!=40131603572 or pref.get('baseline_artifact_id')!=12574929493):
        raise ValueError('Changed source freeze, environment or reviewed parent')
    for name,sha in pref['input_sha256'].items():
        item=read(root,name)
        if digest(item)!=sha or item!=git(root,'show','HEAD:'+name):raise ValueError('Changed/uncommitted query input: '+name)
    if digest(read(root,DATA))!=DATA_SHA or digest(read(root,EXECUTED))!=EXECUTED_SHA:
        raise ValueError('Changed scalar evidence or executed preflight')
    executed=json.loads(read(root,EXECUTED))['input_sha256']
    if len(executed)!=83:raise ValueError('All83 executed inputs required')
    for name,sha in executed.items():
        item=read(root,name)
        if digest(item)!=sha or item!=git(root,'show','HEAD:'+name):raise ValueError('Executed source changed: '+name)
    git(root,'merge-base','--is-ancestor',PARENT,'HEAD')
    changes=git(root,'diff','--name-only',PARENT,'HEAD').decode().splitlines()
    if not changes or not set(changes)<=ALLOWED_CHANGES:raise ValueError('Unexpected change to reviewed parent corpus')
    return {'schema':'osw.current-local-extent-query-check.gate.v2','source_commit':env['GITHUB_SHA'],
        'run_id':int(env['GITHUB_RUN_ID']),'run_attempt':int(env['GITHUB_RUN_ATTEMPT']),
        'preflight_sha256':digest(raw),'reviewed_parent':PARENT,'verified_inputs':len(INPUTS),
        'executed_inputs_unchanged':83,'complete_atlas_load_permitted':False,
        'source_processing_permitted':False,'installed_assets_change_permitted':False}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];result=verify(root,dict(os.environ))
    folder=root/'.pytest_cache/current-local-extent-query-check-v2';folder.mkdir(parents=True,exist_ok=True)
    with (folder/'gate.json').open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2))
