"""Cloud-only matching-engine verification; never install or process ocean fields."""
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import published_current_speed_statistics_v1 as projection

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.pytest_cache/published-current-speed-verification-v1'
REQUEST = 'research/published-current-speed-verification-request-v1.json'
PREFLIGHT = 'research/published-current-speed-verification-preflight-v1.json'
SCOPE = 'research/published-current-speed-runtime-scope-v1.json'
WORKFLOW = '.github/workflows/published-current-speed-verification-v1.yml'


def read(path):
    return json.loads((ROOT / path).read_bytes())


def sha(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(name, value):
    (OUT / name).write_bytes((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, timeout=3600, **kwargs)


def controls():
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'
            or os.environ.get('OSW_SPEED_VERIFICATION_V1') != '1'):
        raise ValueError('Exact cloud working-branch verification required')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1':
            raise ValueError('Single numerical/build worker required')
    request = read(REQUEST)
    if (request.get('execute') is not True or request.get('workflow') != WORKFLOW
            or request.get('preflight_sha256') != sha(PREFLIGHT)
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0
            or request.get('installation_permitted') is not False
            or request.get('source_field_processing_permitted') is not False):
        raise ValueError('Scoped verification request disabled or changed')
    phase = read('research/current-gap-delivery-phase.json')
    if phase['heavy_work_permitted'] is not False:
        raise ValueError('Global source-field processing must remain disabled')
    preflight = read(PREFLIGHT)
    for path, pin in preflight['input_sha256'].items():
        if sha(path) != pin:
            raise ValueError('Frozen verification input changed: ' + path)
    for path, row in preflight['installed_files'].items():
        if sha(path) != row['sha256'] or (ROOT / path).stat().st_size != row['bytes']:
            raise ValueError('Installed artifact changed: ' + path)
    scope, engine = read(SCOPE), read('almanac/query-engine.manifest.json')
    for path, row in scope['runtime_source_changes'].items():
        if (engine['sha256'][path] != row['historical_sha256']
                or sha(row['archive_path']) != row['historical_sha256']
                or (ROOT / row['archive_path']).stat().st_size != row['bytes']
                or sha(path) != row['candidate_sha256']):
            raise ValueError('Installed/candidate source custody differs: ' + path)
    old = read('research/azores-2009-section-compile-inventory-v1.json')
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path, pin in old[group].items():
            expected = scope['runtime_source_changes'].get(path, {}).get('candidate_sha256', pin)
            if sha(path) != expected:
                raise ValueError('Unrelated compiler input differs: ' + path)
    for path in preflight['disabled_requests']:
        doc = read(path)
        if doc.get('execute', doc.get('execution_permitted')) is not False:
            raise ValueError('Another execution request enabled: ' + path)
    head = subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    remote = json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != remote or head != os.environ['GITHUB_SHA']:
        raise ValueError('Exact current branch checkout required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain'],cwd=ROOT).strip():
        raise ValueError('Clean checkout required')
    return preflight


def verify_case(case, response):
    if response.get('ok') is not True or response['total'] != case['expected_total']:
        raise ValueError('Query failed or count differs: ' + case['name'])
    rows, scene = response['rows'], response['chart_scene']
    if response.get('map_scene') is not None:
        raise ValueError('Regional speed summaries must not invent map geometry')
    if case['expected_total'] and not isinstance(scene, dict):
        raise ValueError('Speed chart dispatch missing: ' + case['name'])
    for key, index in [('expected_first_id',0),('expected_last_id',-1)]:
        if key in case and rows[index]['id'] != case[key]:
            raise ValueError('Sorted query endpoint differs')
    for key, field in [('expected_median','median'),('expected_minimum','minimum')]:
        if key in case and rows[0][field] != case[key]:
            raise ValueError('Published table statistic differs')
    if 'expected_returned_rows' in case and len(rows) != case['expected_returned_rows']:
        raise ValueError('Pagination row count differs')
    if 'expected_scene_records' in case and len(scene['records']) != case['expected_scene_records']:
        raise ValueError('Filtered scene support differs')
    if case.get('expected_source_conflicts') and not scene['source_conflicts']:
        raise ValueError('Source conflict disappeared')
    if 'expected_scene' in case and scene != case['expected_scene']:
        raise ValueError('Empty scene differs')
    if 'expected_scene_kind' in case and scene['kind'] != case['expected_scene_kind']:
        raise ValueError('Speed chart kind differs')


def main():
    preflight = controls()  # Before opening the installed packet or starting builds.
    from query_packet import read_bundle_bytes
    from south_java_catalog_engine_v1 import dependencies
    if OUT.exists():
        raise ValueError('Refuse prior verification output')
    OUT.mkdir(parents=True)
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    if hashlib.sha256(raw).hexdigest() != projection.PARENT or len(raw) != 190487048:
        raise ValueError('Exact installed logical parent required')
    parent_path = OUT / 'parent.json'; parent_path.write_bytes(raw)
    snapshots = ['node','--max-old-space-size=1536','analysis/check_eicc_snapshots_v3.mjs']
    snap_env = dict(os.environ,OSW_EICC_SNAPSHOTS_V3='1')
    scope = read(SCOPE)
    run(snapshots + ['parent','almanac/query-engine.wasm',str(parent_path),str(OUT),scope['parent_wasm_sha256'],projection.PARENT],env=snap_env)
    parent = json.loads(raw); del raw
    child = projection.prepare(parent,logical_parent_sha256=projection.PARENT)
    for name, rows in parent['collections'].items():
        actual = child['collections'][name]
        if name == 'objects':
            actual = [dict(r) for r in actual]
            for row in actual:
                if row['id'] == projection.OWNER: row.pop('speed_statistic_ids')
        if actual != rows:
            raise ValueError('Historical collection changed: ' + name)
    candidate = OUT / 'candidate.json'
    candidate.write_bytes((json.dumps(child,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode())
    candidate_sha = sha(candidate)
    del parent,child;gc.collect()
    inventory = read('research/azores-2009-section-compile-inventory-v1.json')
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path in inventory[group]: inventory[group][path] = sha(path)
    inventory['rust_source_sha256']['rust/osw-query/src/published_current_speeds.rs'] = sha('rust/osw-query/src/published_current_speeds.rs')
    inventory['compile_time_data_sha256'][projection.SOURCE] = sha(projection.SOURCE)
    write('compile-inventory.json',inventory)
    env = dict(os.environ,CARGO_TARGET_DIR=str(OUT/'build'),CARGO_INCREMENTAL='0')
    cargo = ['cargo','+1.95.0']; manifest=['--offline','--locked','--manifest-path','rust/osw-query/Cargo.toml']
    with (OUT/'rust-tests.txt').open('wb') as stream:
        run(cargo+['test']+manifest+['--lib','--','--test-threads=1'],env=env,stdout=stream,stderr=subprocess.STDOUT)
    run(cargo+['build']+manifest+['--bin','osw-query-cli'],env=env)
    cli=OUT/'build/debug/osw-query-cli'
    cases=read('research/published-current-speed-query-cases-v1.json')['cases'];queries=[]
    for case in cases:
        p=run([str(cli),str(candidate),'-'],input=json.dumps(case['query']).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if len(p.stdout)>1048576:raise ValueError('Speed response exceeds1MiB')
        response=json.loads(p.stdout);verify_case(case,response);queries.append({'request':case['query'],'expected':response})
    metadata=OUT/'main-metadata.json'
    with metadata.open('wb') as stream:run([str(cli),str(candidate)],stdout=stream)
    run(cargo+['rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib','--manifest-path','rust/osw-query/Cargo.toml'],env=env)
    wasm=OUT/'build/wasm32-unknown-unknown/release/osw_query.wasm';wasm_sha=sha(wasm)
    write('dependency-proof.json',dependencies(wasm.with_suffix('.d').read_text(),ROOT,inventory))
    write('fixtures.json',{'payload_sha256':candidate_sha,'queries':queries})
    run(['node','--max-old-space-size=1536','analysis/check_published_current_speed_parity_v1.mjs',str(wasm),str(candidate),str(OUT/'fixtures.json'),str(metadata),str(OUT/'query-parity.json'),wasm_sha])
    preservation={}
    for name in ['atlas','seasons']:
        path=OUT/(name+'-native.json')
        with path.open('wb') as stream:run([str(cli),str(candidate),'--'+name],stdout=stream)
        old,new=read(OUT/('parent-'+name+'.json')),read(path)
        if new['ok'] is not True or set(new)!=set(old)|{'published_speed_scenes'}:
            raise ValueError('Complete snapshot keys differ: '+name)
        scene=new['published_speed_scenes']['east-african-coastal']
        if len(scene['records'])!=15:raise ValueError('Snapshot speed records missing')
        for key in set(old)-{'bundle_sha256'}:
            if new[key]!=old[key]:raise ValueError('Unrelated snapshot field changed: '+name+'/'+key)
        preservation[name]={'sha256':sha(path),'bytes':path.stat().st_size,'prior_fields_preserved':True}
        del old,new;gc.collect()
    run(snapshots+['candidate',str(wasm),str(candidate),str(OUT),wasm_sha,candidate_sha],env=snap_env)
    for path,row in preflight['installed_files'].items():
        if sha(path)!=row['sha256']:raise ValueError('Installed artifact was modified')
    write('result.json',{'status':'PASS','source_commit':os.environ['GITHUB_SHA'],'candidate_sha256':candidate_sha,'wasm_sha256':wasm_sha,'query_cases':len(cases),'whole_native_wasm_responses_equal':True,'snapshot_preservation':preservation,'installed_files_modified':0,'browser_verified':False,'source_index_extended':False,'runtime_installation_complete':False})


if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='preflight':controls()
    else:main()
