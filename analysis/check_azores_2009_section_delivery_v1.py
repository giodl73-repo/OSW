"""One sequential cloud-only Azores section delivery; candidate stays uninstalled."""
import argparse
import gc
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import azores_2009_section_projection_v1 as p
import azores_2009_section_engine_v1 as e
import azores_2009_section_cases_v1 as cases

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/azores-2009-section-delivery-v1'
TARGET = OUTPUT / 'build'
REQUEST = 'research/azores-2009-section-delivery-request-v1.json'
PREFLIGHT = 'research/azores-2009-section-delivery-preflight-v1.json'
WORKFLOW = '.github/workflows/azores-2009-section-delivery-v1.yml'
SCOPE = 'research/azores-2009-section-runtime-scope-v1.json'
INVENTORY = 'research/south-java-reference-full-delivery-compile-inventory-v4.json'


def read(path):
    return json.loads((ROOT / path).read_bytes())


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def controls(clean=True):
    # Refuse locally before opening any installed packet or engine artifact.
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'
            or os.environ.get('OSW_AZORES_SECTION_DELIVERY_V1') != '1'):
        raise ValueError('Exact cloud working-branch section delivery push required')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One cloud CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS', 'RUST_TEST_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1':
            raise ValueError('Single worker required: ' + key)
    request = read(REQUEST)
    if (request.get('schema') != 'osw.azores-2009-section-delivery-request.v1'
            or request.get('workflow') != WORKFLOW or request.get('execute') is not True
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0):
        raise ValueError('Scoped cloud request disabled or changed')
    for key in ['cloud_candidate_files_permitted', 'native_build_permitted', 'wasm_build_permitted', 'browser_permitted']:
        if request.get(key) is not True:
            raise ValueError('Scoped cloud phase not authorized: ' + key)
    for key in ['scientific_source_processing_permitted', 'working_branch_installation_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False:
            raise ValueError('Unrelated execution permission enabled: ' + key)
    phase = read('research/current-gap-delivery-phase.json')
    if phase.get('phase') != 'source-review-only-v1' or phase.get('heavy_work_permitted') is not False:
        raise ValueError('Global scientific source processing must remain disabled')
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']:
        raise ValueError('Changed frozen source preflight')
    preflight = read(PREFLIGHT)
    for path, expected in preflight['input_sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Changed frozen section delivery source: ' + path)
    for path in preflight['disabled_requests']:
        item = read(path)
        if item.get('execute', item.get('execution_permitted')) is not False:
            raise ValueError('Another execution request is enabled: ' + path)
    if clean:
        for path, expected in preflight['parent_file_sha256'].items():
            if digest(ROOT / path) != expected:
                raise ValueError('Installed parent changed before execution: ' + path)
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    remote = json.loads(subprocess.check_output(['gh', 'api', 'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != os.environ.get('GITHUB_SHA') or head != remote:
        raise ValueError('Exact current working-branch checkout required')
    if clean and subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean checkout required before engine preparation')
    return head


def run(args, *, env=None, output=None, timeout=1200):
    if output:
        with Path(output).open('wb') as stream:
            subprocess.run(args, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=timeout)
    else:
        subprocess.run(args, cwd=ROOT, env=env, check=True, timeout=timeout)


def native(cli, payload, request, *, index=False):
    policy = read('research/eicc-reference-response-budgets-v1.json')
    limit = policy['scene_or_source_response_bytes'] if index or request.get('collection') in policy['main_collections_with_scene_budget'] else policy['scalar_response_bytes']
    result = subprocess.run([str(cli)] + (['--index'] if index else []) + [str(payload), '-'],
        input=json.dumps(request).encode(), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    if result.returncode or len(result.stdout) > limit or len(result.stderr) > 32768:
        raise ValueError('Native query failed/budget exceeded: ' + result.stderr[-3500:].decode(errors='replace'))
    response = json.loads(result.stdout)
    if response.get('ok') is not True:
        raise ValueError('Native query refused: ' + str(response.get('error')))
    return response


def snapshots(wasm, payload, mode, wasm_sha, logical_sha):
    run(['node', '--max-old-space-size=1536', 'analysis/check_eicc_snapshots_v3.mjs', mode,
         str(wasm), str(payload), str(OUTPUT), wasm_sha, logical_sha],
        env=dict(os.environ, OSW_EICC_SNAPSHOTS_V3='1'))


def engine_phase():
    head = controls()
    from query_packet import read_bundle_bytes, write_packet, descriptors
    from south_java_catalog_engine_v1 import dependencies
    if OUTPUT.exists():
        raise ValueError('Refuse to overwrite a prior cloud delivery')
    OUTPUT.mkdir(parents=True)
    if shutil.disk_usage(ROOT).free < 4 * 1024**3:
        raise ValueError('At least4GiB cloud disk required')
    if digest(ROOT / e.MANIFEST) != e.PARENT_MANIFEST_SHA or digest(ROOT / e.WASM) != e.PARENT_WASM_SHA:
        raise ValueError('Exact installed parent binary and engine manifest required')
    parent, scope = read(e.MANIFEST), read(SCOPE)
    custody = e.verify_parent(parent, lambda path: (digest(ROOT / path), (ROOT / path).stat().st_size),
        read('research/eacc-connection-presentation-parent-source-bindings-v3.json')['bindings'], scope)
    write(OUTPUT / 'parent-custody.json', custody)
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    if len(raw) != 190512457 or p.sha(raw) != p.PARENT:
        raise ValueError('Exact installed logical parent required')
    parent_path = OUTPUT / 'parent.json'
    parent_path.write_bytes(raw)
    del raw
    gc.collect()
    snapshots(ROOT / e.WASM, parent_path, 'parent', e.PARENT_WASM_SHA, p.PARENT)
    bundle = json.loads(parent_path.read_bytes())
    counts = {name: len(rows) for name, rows in bundle['collections'].items()}
    science_sha = p.sha(p.encode(bundle['collections']))
    child = p.prepare(bundle, logical_parent_sha256=p.PARENT)
    generated, audit = p.source_index(read('almanac/index-catalog.json'),
        (ROOT / 'almanac/index-data.json.gz').read_bytes(), read('almanac/index-sources.json'))
    child['manifest'] = p.packet_manifest(child['manifest'], generated, audit)
    if child['collections'] is not bundle['collections'] or p.sha(p.encode(child['collections'])) != science_sha:
        raise ValueError('An original scientific collection changed')
    old_manifest, new_manifest = bundle['manifest'], child['manifest']
    if set(new_manifest) != set(old_manifest) | {p.KEY, 'azores_2009_section_source_index_v1'}:
        raise ValueError('Unexpected bundle manifest namespace changed')
    for key in set(old_manifest) - {'input_sha256'}:
        if new_manifest[key] != old_manifest[key]:
            raise ValueError('Inherited bundle manifest namespace changed: ' + key)
    for path, expected in old_manifest['input_sha256'].items():
        if path not in e.INDEX and new_manifest['input_sha256'].get(path) != expected:
            raise ValueError('Original unrelated source pin changed: ' + path)
    main_cases = cases.main_cases(child['collections'])
    candidate_path = OUTPUT / 'candidate.json'
    candidate_path.write_bytes(p.encode(child))
    del bundle, child, old_manifest, new_manifest
    gc.collect()
    packet = write_packet(ROOT / 'almanac/query-data.json', candidate_path.read_bytes())
    for path, body in generated.items():
        (ROOT / path).write_bytes(body)
    del generated
    inventory = e.compile_inventory(read(INVENTORY), parent, scope,
        catalog_sha=digest(ROOT / 'almanac/index-catalog.json'), logical_sha=packet['logical_sha256'])
    for path, expected in {**inventory['rust_source_sha256'], **inventory['compile_time_data_sha256']}.items():
        if digest(ROOT / path) != expected:
            raise ValueError('Actual compiler input differs: ' + path)
    write(OUTPUT / 'compile-inventory.json', inventory)
    write(OUTPUT / 'prepared.json', {'status': 'CANDIDATE_PREPARED_NOT_INSTALLED', 'source_commit': head,
        'logical_sha256': packet['logical_sha256'], 'logical_bytes': packet['logical_byte_length'],
        'collection_counts': counts, 'all_original_collections_sha256': science_sha,
        'source_index_audit': audit, 'new_measurements': 0})
    index_path = OUTPUT / 'index.json'
    with gzip.open(ROOT / 'almanac/index-data.json.gz', 'rb') as src, index_path.open('xb') as dst:
        shutil.copyfileobj(src, dst, length=1048576)
    catalog = read('almanac/index-catalog.json')
    if digest(index_path) != catalog['bundle_sha256'] or index_path.stat().st_size != catalog['bundle_bytes']:
        raise ValueError('Candidate logical source-index identity differs')
    env = dict(os.environ, CARGO_TARGET_DIR=str(TARGET))
    cargo = ['cargo', '+1.95.0']
    manifest = ['--offline', '--locked', '--manifest-path', 'rust/osw-query/Cargo.toml']
    run(cargo + ['build'] + manifest + ['--bin', 'osw-query-cli'], env=env)
    namespaces = [('azores_section_review', 3), ('indian_coastal_context', 8), ('current_gap_admissions', 7),
                  ('south_java_reference', 5), ('pacific_secc_reference', 5), ('planning', 6),
                  ('nwasc_reference_route', 4), ('madagascar_coastal_curve', 4)]
    for name, count in namespaces:
        log = OUTPUT / (name + '-tests.txt')
        run(cargo + ['test'] + manifest + ['--lib', name+'::tests', '--', '--test-threads=1'], env=env, output=log)
        if not re.search(r'test result: ok\. ' + str(count) + r' passed; 0 failed;', log.read_text()):
            raise ValueError('Complete Rust test namespace did not pass: ' + name)
    cli = TARGET / 'debug/osw-query-cli'
    query, expected = main_cases[20]
    cases.verify_response(query, expected, native(cli, candidate_path, query))
    write(OUTPUT / 'native-smoke.json', {'status': 'PASS', 'before_wasm_build': True})
    run(cargo + ['rustc', '--offline', '--locked', '--release', '--target', 'wasm32-unknown-unknown',
        '--lib', '--crate-type', 'cdylib', '--manifest-path', 'rust/osw-query/Cargo.toml'], env=env)
    wasm = TARGET / 'wasm32-unknown-unknown/release/osw_query.wasm'
    if not 8 < wasm.stat().st_size <= 64000000 or wasm.read_bytes()[:8] != b'\0asm\x01\0\0\0':
        raise ValueError('Invalid matching WASM candidate')
    wasm_sha = digest(wasm)
    proof = dependencies(wasm.with_suffix('.d').read_text(), ROOT, inventory)
    fixtures = {'main': [], 'index': []}
    for query, expected in main_cases:
        response = native(cli, candidate_path, query)
        cases.verify_response(query, expected, response)
        fixtures['main'].append({'request': query, 'expected': response})
    for path in cases.index_cases():
        query = {'document': path, 'pointer': '', 'limit': 500, 'offset': 0}
        response = native(cli, index_path, query, index=True)
        reconstructed = {r['source_key']: r['record'] for r in response['rows']}
        if response['source_sha256'] != digest(ROOT / path) or reconstructed != read(path):
            raise ValueError('Complete indexed source reconstruction differs: ' + path)
        fixtures['index'].append({'request': query, 'expected': response})
    wrong = OUTPUT / 'wrong-index.json'
    wrong.write_bytes(b'{"schema":"osw.almanac-index-bundle.v1","documents":{}}')
    refused = subprocess.run([str(cli), '--index', str(wrong)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    if refused.returncode != 2 or b'Changed index bundle or compiled catalog' not in refused.stderr:
        raise ValueError('Native compiled-catalog mismatch guard failed')
    for mode, payload in [('main', candidate_path), ('index', index_path)]:
        metadata = OUTPUT / (mode + '-metadata.json')
        with metadata.open('xb') as stream:
            subprocess.run([str(cli)] + (['--index'] if mode == 'index' else []) + [str(payload)],
                cwd=ROOT, stdout=stream, check=True, timeout=240)
        fixture = OUTPUT / (mode + '-fixtures.json')
        write(fixture, {'payload_sha256': digest(payload), 'queries': fixtures[mode]})
        run(['node', '--max-old-space-size=1536', 'analysis/check_azores_2009_section_parity_v1.mjs', mode,
             str(wasm), str(payload), str(fixture), str(metadata), str(OUTPUT / (mode + '-parity.json')), wasm_sha])
    snapshot_checks = {}
    for name in ['atlas', 'seasons']:
        path = OUTPUT / (name + '-native.json')
        with path.open('xb') as stream:
            subprocess.run([str(cli), str(candidate_path), '--' + name], cwd=ROOT, stdout=stream, check=True, timeout=240)
        if path.stat().st_size > 134217728:
            raise ValueError('Complete snapshot exceeds128MiB')
        old, new = read(OUTPUT / ('parent-' + name + '.json')), read(path)
        if (new.get('ok') is not True or set(new) != set(old) | {'azores_2009_section_scene'}
                or new['bundle_sha256'] != packet['logical_sha256']
                or new['azores_2009_section_scene']['records'] != read(p.BINDINGS)['records']):
            raise ValueError('Complete snapshot shape or reviewed section rows differ')
        for key in set(old) - {'bundle_sha256'}:
            if old[key] != new[key]:
                raise ValueError('Unrelated complete snapshot field changed: ' + key)
        snapshot_checks[name] = {'status': 'PASS', 'response_bytes': path.stat().st_size, 'sha256': digest(path)}
        del old, new
        gc.collect()
    write(OUTPUT / 'snapshot-preservation.json', snapshot_checks)
    snapshots(wasm, candidate_path, 'candidate', wasm_sha, packet['logical_sha256'])
    parts = {'almanac/' + part['path'] for part in descriptors(packet)}
    pin_paths = set(read(PREFLIGHT)['input_sha256']) | {PREFLIGHT}
    paths = e.GENERATED | parts | pin_paths | e.CHANGES | e.CONTRACTS | {e.ADAPTER}
    replacements = {path: digest(ROOT / path) for path in paths}
    compiler = subprocess.check_output(['rustc', '+1.95.0', '--version']).decode().strip()
    overlay = e.engine_manifest(parent, inventory, scope, replacements,
        logical_sha=packet['logical_sha256'], wasm_sha=wasm_sha, compiler=compiler,
        parent_manifest_sha=e.PARENT_MANIFEST_SHA, source_commit=head, dependency_proof=proof)
    shutil.copyfile(wasm, ROOT / e.WASM)
    write(ROOT / e.MANIFEST, overlay)
    generated_paths = e.GENERATED | parts | {e.WASM, e.MANIFEST}
    hashes = {path: digest(ROOT / path) for path in generated_paths}
    for path in generated_paths:
        destination = OUTPUT / 'artifact' / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, destination)
    write(OUTPUT / 'engine.json', {'status': 'PASS', 'source_commit': head, 'stage': 'engine_verified',
        'logical_sha256': packet['logical_sha256'], 'logical_bytes': packet['logical_byte_length'],
        'generated_sha256': hashes, 'compiler': compiler, 'wasm_sha256': wasm_sha, 'dependency_proof': proof,
        'rust_test_counts': dict(namespaces), 'main_query_comparisons': cases.MAIN_CASE_COUNT,
        'source_query_comparisons': cases.INDEX_CASE_COUNT, 'presentation_api_comparisons': 2,
        'native_smoke_before_wasm_build': True, 'browser_verified': False, 'working_branch_installed': False})


def browser_phase():
    head = controls(clean=False)
    saved = read(OUTPUT / 'engine.json')
    if saved.get('status') != 'PASS' or saved.get('source_commit') != head or saved.get('stage') != 'engine_verified':
        raise ValueError('Verified matching-engine phase required before browser')
    for path, expected in saved['generated_sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Saved candidate changed before browser: ' + path)
    overlay = read(e.MANIFEST)
    if overlay[e.KEY]['matching_binary_sha256'] != saved['wasm_sha256'] or overlay[e.KEY]['logical_sha256'] != saved['logical_sha256']:
        raise ValueError('Saved matching engine manifest differs')
    from check_azores_2009_section_browser_v1 import browser_review
    write(OUTPUT / 'browser.json', browser_review(ROOT, OUTPUT))
    for path, expected in saved['generated_sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Browser changed candidate artifacts')
    write(OUTPUT / 'result.json', {**saved, 'schema': 'osw.azores-2009-section-delivery-result.v1',
        'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'browser_verified': True, 'visual_review_complete': False, 'new_physical_dimensions': 0,
        'working_branch_installed': False, 'main_merged': False, 'full_goal_complete': False})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'engine', 'browser'])
    args = parser.parse_args()
    try:
        if args.action == 'preflight':
            controls()
        elif args.action == 'engine':
            engine_phase()
        else:
            browser_phase()
    except Exception as error:
        if os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true':
            write(OUTPUT / (args.action + '-failure.json'), {'status': 'FAIL', 'stage': args.action,
                'source_commit': os.environ.get('GITHUB_SHA'), 'error': str(error)[:4000], 'installed': False})
        raise
