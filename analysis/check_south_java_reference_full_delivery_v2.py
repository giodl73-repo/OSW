"""Single sequential cloud delivery; generated candidates remain uninstalled."""
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

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/south-java-reference-full-delivery-v2'
TARGET = OUTPUT / 'build'
REQUEST = 'research/south-java-reference-full-delivery-request-v2.json'
PREFLIGHT = 'research/south-java-reference-full-delivery-preflight-v2.json'
WORKFLOW = '.github/workflows/south-java-reference-full-delivery-v2.yml'
INVENTORY = 'research/pacific-secc-full-delivery-compile-inventory-v1.json'
SCOPE = 'research/south-java-reference-runtime-scope-v2.json'


def read(path): return json.loads((ROOT / path).read_bytes())
def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def controls(clean=True):
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'
            or os.environ.get('OSW_SOUTH_JAVA_REFERENCE_DELIVERY_V1') != '1'):
        raise ValueError('Exact cloud South Java reference delivery push required')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS', 'RUST_TEST_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1': raise ValueError('Single worker required: ' + key)
    request = read(REQUEST)
    if (request.get('schema') != 'osw.south-java-reference-full-delivery-request.v2'
            or request.get('workflow') != WORKFLOW or request.get('execute') is not True
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0):
        raise ValueError('Exact full-delivery request is disabled or invalid')
    for key in ['cloud_candidate_files_permitted', 'native_build_permitted', 'wasm_build_permitted', 'browser_permitted']:
        if request.get(key) is not True: raise ValueError('Cloud phase not authorized: ' + key)
    for key in ['scientific_source_processing_permitted', 'working_branch_installation_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False: raise ValueError('Forbidden delivery permission: ' + key)
    phase = read('research/current-gap-delivery-phase.json')
    if phase.get('phase') != 'source-review-only-v1' or phase.get('heavy_work_permitted') is not False:
        raise ValueError('Global scientific phase must remain disabled')
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']: raise ValueError('Changed frozen delivery preflight')
    preflight = read(PREFLIGHT)
    for path, sha in preflight['input_sha256'].items():
        if digest(ROOT / path) != sha: raise ValueError('Changed frozen delivery source: ' + path)
    if clean:
        for path, sha in preflight['prepared_presentation_sha256'].items():
            if digest(ROOT / path) != sha: raise ValueError('Changed prepared presentation source: ' + path)
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    remote = json.loads(subprocess.check_output(['gh', 'api', 'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != os.environ.get('GITHUB_SHA') or remote != head: raise ValueError('Exact current working-branch checkout required')
    if clean and subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean exact checkout required before engine phase')
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
    if response.get('ok') is not True: raise ValueError('Native query refused: ' + str(response.get('error')))
    return response


def engine_phase():
    head = controls()
    import south_java_reference_engine_delivery_v2 as engine
    import south_java_reference_runtime_v1 as runtime
    import south_java_reference_delivery_v1 as delivery
    import south_java_reference_full_delivery_cases_v1 as cases
    import south_java_catalog_engine_v1 as compiler
    from query_packet import read_bundle_bytes, write_packet, descriptors
    q = runtime.query
    if OUTPUT.exists(): raise ValueError('Refuse to overwrite a prior cloud delivery')
    OUTPUT.mkdir(parents=True)
    if shutil.disk_usage(ROOT).free < 4 * 1024**3: raise ValueError('At least4GiB cloud disk required')
    if digest(ROOT / engine.MANIFEST) != engine.PARENT_MANIFEST_SHA or digest(ROOT / engine.WASM) != engine.PARENT_WASM_SHA:
        raise ValueError('Exact installed engine and binary required')
    parent = read(engine.MANIFEST); scope = read(SCOPE); original = read(INVENTORY)
    bindings = read('research/eacc-connection-presentation-parent-source-bindings-v3.json')['bindings']
    custody = engine.verify_parent(parent, lambda p: (digest(ROOT / p), (ROOT / p).stat().st_size), bindings, scope)
    write(OUTPUT / 'parent-custody.json', custody)
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    if len(raw) != 190476712 or runtime.sha(raw) != runtime.query.PARENT:
        raise ValueError('Exact installed logical parent required')
    parent_path = OUTPUT / 'parent.json'; parent_path.write_bytes(raw); del raw
    run(['node', '--max-old-space-size=1536', 'analysis/check_eicc_snapshots_v3.mjs', 'parent',
         str(ROOT / engine.WASM), str(parent_path), str(OUTPUT), engine.PARENT_WASM_SHA, runtime.query.PARENT],
         env=dict(os.environ, OSW_EICC_SNAPSHOTS_V3='1'))
    bundle = json.loads(parent_path.read_bytes())
    child, dashboard, preservation = delivery.candidate(bundle, runtime.build_contract(),
        parent_logical_sha256=runtime.query.PARENT)
    documents = {p: (ROOT / p).read_bytes() for p in delivery.DOCUMENTS}
    generated, index_audit = delivery.source_index(read(delivery.CATALOG), (ROOT / 'almanac/index-data.json.gz').read_bytes(),
        read('almanac/index-sources.json'), documents, dashboard)
    child['manifest'] = delivery.packet_manifest(child['manifest'], generated, documents, index_audit)
    main_cases = cases.main_cases(child['collections'])
    projection_rows = {name: child['collections'][name] for name in ['sources', 'route_decisions', 'reference_routes']}
    counts = {n: len(rows) for n, rows in child['collections'].items()}
    currents = [r for r in child['collections']['objects'] if r['type'] == 'named_current']
    route_owners = {'current:' + r['current_id'] for r in child['collections']['reference_routes']}
    published = {r['id'] for r in currents if r['published_length_km'] is not None}
    coverage = {'accepted_current_identities': len(currents), 'canonical_length_field_owners': len(published),
        'reference_route_records': counts['reference_routes'], 'reference_route_owners': len(route_owners),
        'either_canonical_length_field_or_reference_route': len(published | route_owners),
        'missing_both_fields': len(currents) - len(published | route_owners),
        'owners_with_scoped_width_capability': sum(r['capabilities']['scoped_width'] > 0 for r in currents),
        'owners_with_width_sample_capability': sum(r['capabilities']['width_samples'] > 0 for r in currents)}
    if counts['sources'] != 211 or counts['reference_routes'] != 82 or coverage['reference_route_owners'] != 75:
        raise ValueError('Candidate source/route inventory differs')
    candidate_path = OUTPUT / 'candidate.json'; candidate_path.write_bytes(delivery.encoded(child))
    del bundle, child; gc.collect()
    parent_atlas = read(OUTPUT / 'parent-atlas.json'); parent_seasons = read(OUTPUT / 'parent-seasons.json')
    if parent_atlas['working_reference_routes'] != parent_seasons['working_reference_routes']:
        raise ValueError('Complete parent route catalog differs between atlas and seasons')
    expected_catalog = runtime.catalog_projection(parent_atlas['working_reference_routes'], projection_rows, runtime.build_contract())
    write(OUTPUT / 'expected-catalog.json', expected_catalog)
    del parent_atlas, parent_seasons, expected_catalog, projection_rows; gc.collect()
    packet = write_packet(ROOT / 'almanac/query-data.json', candidate_path.read_bytes())
    for path, body in {**generated, delivery.DASHBOARD: dashboard, q.PAGE: q.support_page(runtime.build_contract()['query_contract'], installed=True).encode()}.items():
        (ROOT / path).write_bytes(body)
    inventory = engine.compile_inventory(original, parent, scope, digest(ROOT / delivery.CATALOG), packet['logical_sha256'])
    for path, sha in {**inventory['rust_source_sha256'], **inventory['compile_time_data_sha256']}.items():
        if digest(ROOT / path) != sha: raise ValueError('Actual compiler input differs: ' + path)
    write(OUTPUT / 'compile-inventory.json', inventory)
    write(OUTPUT / 'prepared.json', {'status': 'CANDIDATE_PREPARED_NOT_INSTALLED', 'source_commit': head,
        'logical_sha256': packet['logical_sha256'], 'logical_bytes': packet['logical_byte_length'],
        'preservation': preservation, 'source_index_audit': index_audit, 'candidate_structural_coverage': coverage})
    index_path = OUTPUT / 'index.json'
    with gzip.open(ROOT / 'almanac/index-data.json.gz', 'rb') as src, index_path.open('xb') as dst:
        shutil.copyfileobj(src, dst, length=1048576)
    catalog = read(delivery.CATALOG)
    if digest(index_path) != catalog['bundle_sha256'] or index_path.stat().st_size != catalog['bundle_bytes']:
        raise ValueError('Candidate logical index identity differs')
    env = dict(os.environ, CARGO_TARGET_DIR=str(TARGET))
    run(['cargo', '+1.95.0', 'build', '--offline', '--locked', '--manifest-path', 'rust/osw-query/Cargo.toml', '--bin', 'osw-query-cli'], env=env)
    test_counts = {}
    for namespace, expected in [('current_gap_admissions::tests', 7), ('south_java_reference::tests', 5), ('pacific_secc_reference::tests', 5), ('planning::tests', 6),
                                 ('nwasc_reference_route::tests', 4), ('madagascar_coastal_curve::tests', 4)]:
        name = namespace.split('::')[0]; path = OUTPUT / (name + '-tests.txt')
        run(['cargo', '+1.95.0', 'test', '--offline', '--locked', '--manifest-path', 'rust/osw-query/Cargo.toml',
             '--lib', namespace, '--', '--test-threads=1'], env=env, output=path)
        if not re.search(r'test result: ok\. ' + str(expected) + r' passed; 0 failed;', path.read_text()):
            raise ValueError('Declared complete Rust test namespace did not pass: ' + namespace)
        test_counts[namespace] = expected
    cli = TARGET / 'debug/osw-query-cli'
    cases.verify_response(main_cases[0][0], main_cases[0][1], native(cli, candidate_path, main_cases[0][0]))
    write(OUTPUT / 'native-smoke.json', {'status': 'PASS', 'before_wasm_build': True, 'route_id': q.ROUTE})
    run(['cargo', '+1.95.0', 'rustc', '--offline', '--locked', '--release', '--target', 'wasm32-unknown-unknown',
         '--lib', '--crate-type', 'cdylib', '--manifest-path', 'rust/osw-query/Cargo.toml'], env=env)
    wasm = TARGET / 'wasm32-unknown-unknown/release/osw_query.wasm'
    if not 8 < wasm.stat().st_size <= 64000000 or wasm.read_bytes()[:8] != b'\0asm\x01\0\0\0':
        raise ValueError('Invalid matching WASM candidate')
    wasm_sha = digest(wasm)
    dependencies = compiler.dependencies(wasm.with_suffix('.d').read_text(), ROOT, inventory)
    fixtures = {'main': [], 'index': []}
    for request, expected in main_cases:
        response = native(cli, candidate_path, request); cases.verify_response(request, expected, response)
        fixtures['main'].append({'request': request, 'expected': response})
    for path in cases.index_cases():
        request = {'document': path, 'pointer': '', 'limit': 500, 'offset': 0}
        response = native(cli, index_path, request, index=True)
        reconstructed = {r['source_key']: r['record'] for r in response['rows']}
        if response['source_sha256'] != digest(ROOT / path) or q.encoded(reconstructed) != q.encoded(read(path)):
            raise ValueError('Complete source-document reconstruction differs: ' + path)
        fixtures['index'].append({'request': request, 'expected': response})
    wrong = OUTPUT / 'wrong-index.json'; wrong.write_bytes(b'{"schema":"osw.almanac-index-bundle.v1","documents":{}}')
    refused = subprocess.run([str(cli), '--index', str(wrong)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if refused.returncode != 2 or b'Changed index bundle or compiled catalog' not in refused.stderr:
        raise ValueError('Native compiled-catalog guard failed')
    for mode, payload in [('main', candidate_path), ('index', index_path)]:
        metadata = OUTPUT / (mode + '-metadata.json')
        with metadata.open('xb') as stream:
            subprocess.run([str(cli)] + (['--index'] if mode == 'index' else []) + [str(payload)],
                cwd=ROOT, stdout=stream, check=True, timeout=240)
        fixture = OUTPUT / (mode + '-fixtures.json')
        write(fixture, {'payload_sha256': digest(payload), 'queries': fixtures[mode]})
        run(['node', '--max-old-space-size=1536', 'analysis/check_south_java_reference_parity_v1.mjs', mode,
             str(wasm), str(payload), str(fixture), str(metadata), str(OUTPUT / (mode + '-parity.json')), wasm_sha])
    expected_catalog = read(OUTPUT / 'expected-catalog.json'); snapshot_checks = {}
    for name in ['atlas', 'seasons']:
        path = OUTPUT / (name + '-native.json')
        with path.open('xb') as stream:
            subprocess.run([str(cli), str(candidate_path), '--' + name], cwd=ROOT, stdout=stream, check=True, timeout=240)
        if path.stat().st_size > 134217728: raise ValueError('Complete presentation API exceeds128MiB')
        old = read(OUTPUT / ('parent-' + name + '.json')); new = read(path)
        if (new.get('ok') is not True or set(old) != set(new) or new['working_reference_routes'] != expected_catalog
                or new['bundle_sha256'] != packet['logical_sha256']):
            raise ValueError('Complete ' + name + ' identity/catalog projection differs')
        for key in set(old) - {'bundle_sha256', 'working_reference_routes', 'sources_json'}:
            if old[key] != new[key]: raise ValueError('Unrelated presentation field changed: ' + key)
        if set(old['sources_json']) != set(new['sources_json']): raise ValueError('Presentation source inventory changed')
        for key, value in old['sources_json'].items():
            if new['sources_json'][key] != (dashboard.decode() if key == delivery.DASHBOARD else value):
                raise ValueError('Prior presentation source string changed: ' + key)
        snapshot_checks[name] = {'status': 'PASS', 'response_bytes': path.stat().st_size, 'sha256': digest(path)}
        del old, new; gc.collect()
    write(OUTPUT / 'snapshot-preservation.json', snapshot_checks)
    run(['node', '--max-old-space-size=1536', 'analysis/check_eicc_snapshots_v3.mjs', 'candidate', str(wasm),
         str(candidate_path), str(OUTPUT), wasm_sha, packet['logical_sha256']], env=dict(os.environ, OSW_EICC_SNAPSHOTS_V3='1'))
    pins = {**read(PREFLIGHT)['input_sha256'], PREFLIGHT: digest(ROOT / PREFLIGHT)}
    parts = {'almanac/' + p['path'] for p in descriptors(packet)}
    paths = engine.GENERATED | delivery.DOCUMENTS | set(pins) | parts
    replacements = {p: digest(ROOT / p) for p in paths}
    version = subprocess.check_output(['rustc', '+1.95.0', '--version']).decode().strip()
    manifest = engine.engine_manifest(parent, inventory, scope, packet, replacements, pins, dependencies,
        wasm_sha=wasm_sha, compiler=version, parent_manifest_sha=engine.PARENT_MANIFEST_SHA, source_commit=head)
    shutil.copyfile(wasm, ROOT / engine.WASM); write(ROOT / engine.MANIFEST, manifest)
    generated_paths = engine.GENERATED | {engine.WASM, engine.MANIFEST} | parts
    hashes = {p: digest(ROOT / p) for p in generated_paths}
    for path in generated_paths:
        destination = OUTPUT / 'artifact' / path; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, destination)
    write(OUTPUT / 'engine.json', {'status': 'PASS', 'source_commit': head, 'stage': 'engine_verified',
        'logical_sha256': packet['logical_sha256'], 'logical_bytes': packet['logical_byte_length'],
        'generated_sha256': hashes, 'compiler': version, 'wasm_sha256': wasm_sha,
        'dependency_proof': dependencies, 'rust_test_counts': test_counts,
        'main_query_comparisons': cases.MAIN_CASE_COUNT, 'source_query_comparisons': cases.INDEX_CASE_COUNT, 'presentation_api_comparisons': 2,
        'native_smoke_before_wasm_build': True, 'browser_verified': False, 'working_branch_installed': False})


def browser_phase():
    head = controls(clean=False)
    import south_java_reference_engine_delivery_v2 as engine
    saved = read(OUTPUT / 'engine.json')
    if saved.get('status') != 'PASS' or saved.get('source_commit') != head or saved.get('stage') != 'engine_verified':
        raise ValueError('Verified engine phase required before browser')
    for path, sha in saved['generated_sha256'].items():
        if digest(ROOT / path) != sha: raise ValueError('Saved engine candidate changed before browser: ' + path)
    manifest = read(engine.MANIFEST)
    if (manifest[engine.KEY]['matching_binary_sha256'] != saved['wasm_sha256']
            or manifest[engine.KEY]['logical_sha256'] != saved['logical_sha256']):
        raise ValueError('Saved engine manifest does not match verified candidate')
    from check_south_java_reference_browser_v1 import browser_review
    browser = browser_review(ROOT, OUTPUT); write(OUTPUT / 'browser.json', browser)
    for path, sha in saved['generated_sha256'].items():
        if digest(ROOT / path) != sha: raise ValueError('Browser phase changed candidate bytes')
    write(OUTPUT / 'result.json', {**saved, 'schema': 'osw.south-java-reference-full-delivery-result.v2',
        'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'browser_verified': True, 'visual_review_complete': False, 'new_physical_dimensions': 0,
        'candidate_structural_coverage': read(OUTPUT / 'prepared.json')['candidate_structural_coverage'],
        'working_branch_installed': False, 'main_merged': False, 'full_goal_complete': False})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'engine', 'browser'])
    args = parser.parse_args()
    try:
        if args.action == 'preflight': controls()
        elif args.action == 'engine': engine_phase()
        else: browser_phase()
    except Exception as error:
        if os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true':
            write(OUTPUT / (args.action + '-failure.json'), {'status': 'FAIL', 'stage': args.action,
                'source_commit': os.environ.get('GITHUB_SHA'), 'error': str(error)[:4000], 'installed': False})
        raise
