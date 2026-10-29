"""Cloud-only native unit-test gate for the frozen backend source; no data installation."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/chen-indian-sec-ridge-rust-core-request-v2.json'
PREFLIGHT='research/chen-indian-sec-ridge-rust-core-preflight-v2.json'
OUTPUT=ROOT/'.pytest_cache/chen-indian-sec-ridge-rust-core-v2'


def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def controls():
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps':
        raise ValueError('Native compilation permitted only in the scoped cloud branch job')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:
        raise ValueError('One CPU and low priority required')
    for name in ['CARGO_BUILD_JOBS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(name)!='1':raise ValueError('Single worker required: '+name)
    request=read(REQUEST)
    if request['schema']!='osw.chen-indian-sec-ridge-rust-core-request.v2' or request['execute'] is not True or request['cloud_native_unit_tests_permitted'] is not True:
        raise ValueError('Disabled or changed native gate request')
    for name in ['wasm_build_permitted','index_rebuild_permitted','ocean_field_processing_permitted','browser_permitted','installation_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        if request.get(name) is not False:raise ValueError('Unrelated operation enabled: '+name)
    if sha(PREFLIGHT)!=request['preflight_sha256']:raise ValueError('Changed native gate freeze')
    preflight=read(PREFLIGHT)
    for path,expected in preflight['input_sha256'].items():
        if sha(path)!=expected:raise ValueError('Frozen native input changed: '+path)
    for path,record in preflight['installed_files'].items():
        if (ROOT/path).stat().st_size!=record['bytes'] or sha(path)!=record['sha256']:
            raise ValueError('Installed parent file changed: '+path)
    for path in preflight['disabled_requests']:
        if read(path).get('execute',read(path).get('execution_permitted')) is not False:
            raise ValueError('Older request enabled: '+path)
    phase=read('research/current-gap-delivery-phase.json')
    if phase['heavy_work_permitted'] is not False:raise ValueError('Broad heavy work must remain disabled')
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    if head!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():
        raise ValueError('Clean exact source checkout required')
    return preflight


def run():
    preflight=controls()
    OUTPUT.mkdir(parents=True,exist_ok=False)
    compiler=subprocess.check_output(['rustc','+1.95.0','--version'],timeout=30).decode().strip()
    if not compiler.startswith('rustc 1.95.0 '):raise ValueError('Frozen compiler required')
    environment=dict(os.environ,CARGO_TARGET_DIR=str(ROOT/'.pytest_cache/chen-indian-sec-ridge-rust-core-target-v2'),CARGO_INCREMENTAL='0')
    command=['cargo','+1.95.0','test','--manifest-path','rust/osw-query/Cargo.toml','--locked','--lib','--','--test-threads=1']
    result=subprocess.run(command,cwd=ROOT,env=environment,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=2100)
    (OUTPUT/'native-tests.txt').write_bytes(result.stdout)
    log=result.stdout.decode('utf8',errors='replace')
    matches=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;',log)
    passed=int(matches[-1][0]) if matches else 0
    report={'schema':'osw.chen-indian-sec-ridge-rust-core-result.v2','source_commit':os.environ['GITHUB_SHA'],
            'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
            'status':'PASS_NATIVE_CORE_UNIT_TESTS' if result.returncode==0 and passed==288 else 'FAIL_NATIVE_CORE_UNIT_TESTS',
            'compiler':compiler,'cargo_exit_code':result.returncode,'native_tests_passed':passed,
            'expected_native_tests':288,'test_log_sha256':hashlib.sha256(result.stdout).hexdigest(),
            'preflight_sha256':sha(PREFLIGHT),'request_sha256':sha(REQUEST),
            'rust_source_files':preflight['rust_source_file_count'],'installed_parent_files_checked':21,
            'candidate_data_materialized':False,'wasm_built':False,'index_rebuilt':False,'browser_run':False,
            'installed_data_changed':False,'local_bulk_sync':False,'full_goal_complete':False}
    (OUTPUT/'result.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps(report),flush=True)
    if report['status']!='PASS_NATIVE_CORE_UNIT_TESTS':raise RuntimeError('Native core gate failed; retain exact logs and source version')


if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUTPUT.mkdir(parents=True,exist_ok=True)
            (OUTPUT/'failure.json').write_bytes((json.dumps({'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')},indent=2)+'\n').encode())
        raise
