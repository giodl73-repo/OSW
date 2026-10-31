"""Cloud-only compilation gate; candidate packet/API/browser delivery follows separately."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/pacific-nec-product-axis-runtime-request-v1.json'
PREFLIGHT='research/pacific-nec-product-axis-runtime-preflight-v1.json'
OUT=ROOT/'.pytest_cache/pacific-nec-product-axis-runtime-v1'

def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_PACIFIC_NEC_PRODUCT_RUNTIME_V1')!='1'):
        raise ValueError('Scoped cloud runtime gate only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required: '+key)
    request=read(REQUEST)
    if request.get('execute') is not True or request.get('schema')!='osw.pacific-nec-product-axis-runtime-request.v1' or request.get('preflight_sha256')!=sha(PREFLIGHT):raise ValueError('Disabled or altered runtime request')
    for key in ['native_tests_permitted','wasm_build_permitted','cloud_fixture_packet_read_permitted']:
        if request.get(key) is not True:raise ValueError('Missing permission: '+key)
    for key in ['candidate_data_installation_permitted','browser_permitted','index_corpus_read_permitted','ocean_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated permission enabled: '+key)
    pref=read(PREFLIGHT)
    for path,digest in pref['input_sha256'].items():
        if sha(path)!=digest:raise ValueError('Frozen source differs: '+path)
    for path,record in pref['installed_files'].items():
        if sha(path)!=record['sha256'] or (ROOT/path).stat().st_size!=record['bytes']:raise ValueError('Installed parent differs: '+path)
    for path in pref['disabled_requests']:
        old=read(path)
        if old.get('execute',old.get('execution_permitted')) is not False:raise ValueError('Other request enabled: '+path)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad work enabled')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact source required')
    return pref

def run():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False)
    from south_java_catalog_engine_v1 import dependencies
    inventory=pref['compile_inventory']
    for group in ['rust_source_sha256','compile_time_data_sha256','test_fixture_sha256']:
        for path,digest in inventory[group].items():
            if sha(path)!=digest:raise ValueError('Compiler/fixture input differs: '+path)
    write(OUT/'compile-inventory.json',inventory)
    env=dict(os.environ,CARGO_TARGET_DIR=str(ROOT/'.pytest_cache/pacific-nec-product-axis-runtime-build-v1'),CARGO_INCREMENTAL='0')
    def command(args,log):
        with (OUT/log).open('wb') as stream:subprocess.run(args,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=2400)
    result={'status':'STARTED','source_commit':os.environ['GITHUB_SHA'],'candidate_data_installed':False,'browser_verified':False,'full_goal_complete':False}
    try:
        command(['node','--test','analysis/test_surface_product_axes_v1.cjs'],'renderer-tests.txt')
        command(['python','-m','unittest','discover','-s','analysis','-p','test_pacific_nec_product_axis*_v1.py'],'record-admission-tests.txt')
        command(['python','-m','unittest','discover','-s','analysis','-p','test_audit_pacific_nec_product_axis_parent_v1.py'],'parent-audit-tests.txt')
        command(['cargo','+1.95.0','test','--locked','--manifest-path','rust/osw-query/Cargo.toml','--','--test-threads=1'],'rust-tests.txt')
        if b'test result: ok. 295 passed; 0 failed;' not in (OUT/'rust-tests.txt').read_bytes():raise ValueError('Expected 289 historical and six product-axis native tests')
        command(['cargo','+1.95.0','rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--manifest-path','rust/osw-query/Cargo.toml','--crate-type','cdylib'],'wasm-build.txt')
        build=Path(env['CARGO_TARGET_DIR'])/'wasm32-unknown-unknown/release'
        proof=dependencies((build/'osw_query.d').read_text(),ROOT,inventory)
        if not {'rust/osw-query/src/pacific_nec_product_axes.rs','research/pacific-nec-product-axis-query-contract-v1.json'}<=set(proof['production_dependencies']):raise ValueError('New validator and contract absent from actual compiler dependencies')
        write(OUT/'dependency-proof.json',proof)
        result.update(status='PASS_SOURCE_BOUND_NATIVE_TESTS_AND_WASM_COMPILATION',rust_tests_passed=295,renderer_tests_passed=6,record_and_audit_tests_passed=12,wasm_sha256=sha(build/'osw_query.wasm'),wasm_bytes=(build/'osw_query.wasm').stat().st_size,production_dependencies=proof['production_dependency_count'],candidate_api_parity_verified=False)
    except Exception as error:
        result.update(status='FAILED',error=str(error));raise
    finally:write(OUT/'result.json',result)

if __name__=='__main__':run()
