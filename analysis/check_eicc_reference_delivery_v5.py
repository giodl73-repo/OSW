"""One sequential cloud case: EICC extension, matching engines, source and UI checks."""
import argparse
import copy
import gc
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import check_south_java_model_layer_cloud_v1 as environment
import eicc_reference_delivery_v5 as delivery
import eicc_reference_snapshot_custody_v3 as snapshot_custody
import eicc_reference_projection_v3 as projection
import eicc_reference_delivery_cases_v1 as cases
import eicc_reference_query_v1 as context
import south_java_catalog_engine_v1 as compiler
from query_packet import descriptors, read_bundle_bytes, write_packet

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/eicc-reference-delivery-v5'
TARGET = OUTPUT / 'build'
REQUEST = 'research/eicc-reference-delivery-request-v5.json'
PREFLIGHT = 'research/eicc-reference-delivery-preflight-v5.json'
WORKFLOW = '.github/workflows/eicc-reference-delivery-v5.yml'
INVENTORY = 'research/south-java-compiled-catalog-build-inputs-v1.json'
INSTALLED = 'research/loop-published-metrics-installed-v1.json'
QUERY_AUDIT = []


def read(path): return json.loads((ROOT / path).read_bytes())
def write(path, value): Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def source_controls(env, clean=True):
    environment.cloud_environment(env)  # Must refuse locally before any file is read.
    if env.get('GITHUB_EVENT_NAME') != 'push' or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('Low-priority exact working-branch push required')
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != env.get('GITHUB_SHA') or (clean and subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip()):
        raise ValueError('Clean exact source checkout required')
    remote = json.loads(subprocess.check_output(['gh', 'api', 'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))
    if remote['object']['sha'] != head: raise ValueError('Stale working-branch case refused')
    request = read(REQUEST)
    if request.get('schema') != 'osw.eicc-reference-delivery-request.v5' or request.get('workflow') != WORKFLOW:
        raise ValueError('Wrong request schema/workflow')
    for key in ['execution_permitted', 'cloud_candidate_files_permitted', 'native_build_permitted',
                'wasm_build_permitted', 'browser_automation_permitted']:
        if request.get(key) is not True: raise ValueError('Cloud delivery disabled: ' + key)
    for key in ['scientific_source_processing_permitted', 'working_branch_installation_permitted',
                'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False: raise ValueError('Forbidden delivery permission: ' + key)
    if type(request.get('max_cloud_jobs')) is not int or request['max_cloud_jobs'] != 1 or type(request.get('max_heavy_local_jobs')) is not int or request['max_heavy_local_jobs'] != 0:
        raise ValueError('One cloud job and no heavy local jobs required')
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']: raise ValueError('Changed delivery preflight')
    preflight = read(PREFLIGHT)
    for path, expected in preflight['input_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed delivery source: ' + path)
    proof = read(INSTALLED)
    relocations = []
    for path, count in preflight['preserve_inventories'].items():
        pins = read(path)['input_sha256']
        if len(pins) != count: raise ValueError('Changed historical input inventory')
        for name, expected in pins.items():
            if name == 'almanac/loop-published-metrics.html':
                archive = proof['presentation_overlay']['original_page_archive_path']
                if (proof['presentation_overlay']['original_page_sha256'] != expected
                        or digest(ROOT / archive) != expected
                        or digest(ROOT / name) != proof['files'][name]['sha256']):
                    raise ValueError('Historical Loop page relocation differs')
                relocations.append({'inventory': path, 'archive_path': archive, 'historical_sha256': expected})
            elif digest(ROOT / name) != expected:
                matches = [r for r in read(delivery.SCOPE)['historical_source_relocations']
                           if r['inventory'] == path and r['historical_path'] == name and r['historical_sha256'] == expected]
                if len(matches) != 1 or digest(ROOT / matches[0]['archive_path']) != expected or digest(ROOT / name) != matches[0]['candidate_sha256']:
                    raise ValueError('Unverified historical source relocation: ' + name)
                relocations.append(matches[0])
    if len(preflight['disabled_requests']) != 21: raise ValueError('Earlier request inventory changed')
    for path in preflight['disabled_requests']:
        if read(path)['execution_permitted'] is not False: raise ValueError('Older execution enabled: ' + path)
    phase = read('research/current-gap-delivery-phase.json')
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain')
    return relocations


def controls(env):
    relocations = source_controls(env)
    proof = read(INSTALLED)
    for path, pin in proof['files'].items():
        if digest(ROOT / path) != pin['sha256'] or (ROOT / path).stat().st_size != pin['bytes']:
            raise ValueError('Installed Loop custody differs: ' + path)
    packet = read('almanac/query-data.json')
    descriptors(packet)
    if packet['logical_sha256'] != delivery.PARENT_LOGICAL_SHA or packet['logical_byte_length'] != delivery.PARENT_LOGICAL_BYTES:
        raise ValueError('Exact installed Loop packet required')
    if digest(ROOT / delivery.MANIFEST) != delivery.PARENT_MANIFEST_SHA or digest(ROOT / delivery.WASM) != delivery.PARENT_WASM_SHA:
        raise ValueError('Installed engine identity differs')
    inventory, parent = read(INVENTORY), read(delivery.MANIFEST)
    if len(inventory['rust_source_sha256']) != 98 or len(inventory['compile_time_data_sha256']) != 144 or len(inventory['excluded_test_only_data_references']) != 6:
        raise ValueError('Original compiler inventory changed')
    checked = delivery.compile_inventory(inventory, parent, parent['sha256'][delivery.CATALOG], delivery.PARENT_LOGICAL_SHA, read(delivery.SCOPE))
    for path, pin in {**checked['rust_source_sha256'], **checked['compile_time_data_sha256']}.items():
        if digest(ROOT / path) != pin: raise ValueError('Installed compiler input differs: ' + path)
    if (ROOT / context.FILE).read_bytes() != context.encoded(context.build_contract()):
        raise ValueError('Changed prepared EICC contract')
    return inventory, relocations


def prepare(inventory, relocations):
    if shutil.disk_usage(ROOT).free < 4 * 1024**3: raise ValueError('At least4GiB cloud disk required')
    available = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    if available < 6 * 1024**3: raise ValueError('At least6GiB cloud memory required')
    parent = read(delivery.MANIFEST)
    for path in delivery.GENERATED:
        if digest(ROOT / path) != parent['sha256'][path]: raise ValueError('Parent generated custody differs')
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    if len(raw) != delivery.PARENT_LOGICAL_BYTES or delivery.sha(raw) != delivery.PARENT_LOGICAL_SHA:
        raise ValueError('Parent logical bytes differ')
    parent_path = OUTPUT / 'parent.json'; parent_path.write_bytes(raw); del raw
    subprocess.run(['node', '--max-old-space-size=1536', 'analysis/check_eicc_snapshots_v3.mjs',
        'parent', str(ROOT / delivery.WASM), str(parent_path), str(OUTPUT), delivery.PARENT_WASM_SHA,
        delivery.PARENT_LOGICAL_SHA], cwd=ROOT, env=dict(os.environ, OSW_EICC_SNAPSHOTS_V3='1'), check=True, timeout=1200)
    bundle = json.loads(parent_path.read_bytes())
    rows = bundle['collections']
    if (sum(map(len, rows.values())) != 108574 or len(rows['objects']) != 246 or len(rows['widths']) != 172
            or sum(r['type'] == 'named_current' for r in rows['objects']) != 106
            or any(r['current_id'] == context.CURRENT for r in rows[context.ROUTES])):
        raise ValueError('Installed parent inventory or EICC route history differs')
    contract = context.build_contract()
    candidate, dashboard, preservation = delivery.candidate(bundle, contract)
    del bundle, rows; gc.collect()
    documents = {p: (ROOT / p).read_bytes() for p in delivery.DOCUMENTS}
    generated, audit = delivery.source_index(read(delivery.CATALOG), (ROOT / 'almanac/index-data.json.gz').read_bytes(),
                                             read('almanac/index-sources.json'), documents, dashboard)
    candidate['manifest'] = delivery.packet_manifest(candidate['manifest'], generated, documents, audit)
    parent_atlas = read(str((OUTPUT / 'parent-atlas.json').relative_to(ROOT)))
    parent_seasons = read(str((OUTPUT / 'parent-seasons.json').relative_to(ROOT)))
    if delivery.encoded(parent_atlas['working_reference_routes']) != delivery.encoded(parent_seasons['working_reference_routes']):
        raise ValueError('Parent atlas and seasonal catalogs differ')
    expected_catalog = projection.catalog_projection(parent_atlas['working_reference_routes'], candidate)
    catalog_counts = {'parent': copy.deepcopy(parent_atlas['working_reference_routes']['counts']),
                      'candidate': copy.deepcopy(expected_catalog['counts']),
                      'meaning': 'Route-card catalogue counts; not whole-current measurement completeness.'}
    write(OUTPUT / 'expected-catalog.json', expected_catalog)
    del parent_atlas, parent_seasons, expected_catalog; gc.collect()
    main = OUTPUT / 'candidate.json'; main.write_bytes(delivery.encoded(candidate))
    expected = {n: copy.deepcopy(contract['collections'][n]) for n in context.OWNER_FIELDS}
    expected['sources'] = copy.deepcopy(contract['collections']['sources'])
    expected['owner'] = next(r for r in candidate['collections']['objects'] if r['id'] == context.TARGET)
    expected['decision'] = next(r for r in candidate['collections']['route_decisions'] if r['entity_id'] == context.TARGET)
    for key, collection in [('loop_summaries', 'current_reported_contour_length_summaries'),
                            ('loop_events', 'current_reported_separation_events'),
                            ('legacy_depths', 'current_model_depth_context')]:
        expected[key] = copy.deepcopy(candidate['collections'][collection])
    if len(expected['loop_summaries']) != 2 or len(expected['loop_events']) != 12 or len(expected['legacy_depths']) != 3:
        raise ValueError('Historical scalar inventory differs')
    counts = {n: len(r) for n, r in candidate['collections'].items()}
    if sum(counts.values()) != 108592 or preservation['new_source_records'] != 3:
        raise ValueError('Candidate should add15 evidence rows and3 sources')
    del candidate; gc.collect()
    with main.open('rb') as stream: packet = write_packet(ROOT / 'almanac/query-data.json', stream.read())
    delivery.verify_candidate_identity(packet)
    for path, body in {**generated, delivery.DASHBOARD: dashboard}.items(): (ROOT / path).write_bytes(body)
    updated_inventory = delivery.compile_inventory(inventory, parent, digest(ROOT / delivery.CATALOG), packet['logical_sha256'], read(delivery.SCOPE))
    for path, pin in updated_inventory['compile_time_data_sha256'].items():
        if digest(ROOT / path) != pin: raise ValueError('Undeclared compile data change')
    index = OUTPUT / 'index.json'
    with gzip.open(ROOT / 'almanac/index-data.json.gz', 'rb') as source, index.open('xb') as dest:
        for chunk in iter(lambda: source.read(1048576), b''):
            dest.write(chunk)
            if dest.tell() > 536870912: raise ValueError('Index exceeds finite byte budget')
    catalog = read(delivery.CATALOG)
    if digest(index) != catalog['bundle_sha256'] or index.stat().st_size != catalog['bundle_bytes']:
        raise ValueError('Candidate logical index differs')
    if audit['original_sources_verified'] != 601 or catalog['source_count'] != 609:
        raise ValueError('Unexpected index extension scope')
    write(OUTPUT / 'prepared.json', {'logical_sha256': packet['logical_sha256'], 'logical_bytes': packet['logical_byte_length'],
          'collection_counts': counts, 'preservation': preservation, 'source_index_audit': audit,
          'route_catalog_counts': catalog_counts, 'candidate_bytes_unchanged_from_v3': True,
          'source_commit': os.environ['GITHUB_SHA'], 'historical_source_relocations': relocations,
          'source_processing': False, 'compile_inventory': updated_inventory})
    return parent, updated_inventory, packet, expected


def compile_engine():
    env = dict(os.environ, CARGO_TARGET_DIR=str(TARGET))
    commands = [
        ['cargo', '+1.95.0', 'build', '--offline', '--locked', '--manifest-path', 'rust/osw-query/Cargo.toml', '--bin', 'osw-query-cli'],
        ['cargo', '+1.95.0', 'rustc', '--offline', '--locked', '--release', '--target', 'wasm32-unknown-unknown',
         '--lib', '--crate-type', 'cdylib', '--manifest-path', 'rust/osw-query/Cargo.toml']]
    subprocess.run(commands[0], cwd=ROOT, env=env, check=True, timeout=1200)
    tests = subprocess.run(['cargo', '+1.95.0', 'test', '--offline', '--locked', '--manifest-path',
        'rust/osw-query/Cargo.toml', '--lib', 'planning::tests', '--', '--nocapture'],
        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1200)
    if tests.returncode or len(tests.stdout) > 131072 or len(tests.stderr) > 131072 or b'6 passed; 0 failed' not in tests.stdout:
        raise ValueError('Six Rust planning tests required: ' + tests.stderr[-4000:].decode(errors='replace')
                         + tests.stdout[-4000:].decode(errors='replace'))
    write(OUTPUT / 'planning-tests.json', {'tests_passed': 6, 'exit_code': tests.returncode,
        'stdout_sha256': delivery.sha(tests.stdout), 'stderr_sha256': delivery.sha(tests.stderr)})
    inventory_tests = subprocess.run(['cargo', '+1.95.0', 'test', '--offline', '--locked', '--manifest-path',
        'rust/osw-query/Cargo.toml', '--lib', 'eicc_extension_', '--', '--nocapture'],
        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1200)
    inventory_receipt = {'tests_passed': 2 if inventory_tests.returncode == 0
        and b'2 passed; 0 failed' in inventory_tests.stdout else 0, 'exit_code': inventory_tests.returncode,
        'stdout_sha256': delivery.sha(inventory_tests.stdout), 'stderr_sha256': delivery.sha(inventory_tests.stderr),
        'stdout_preview': inventory_tests.stdout[-4000:].decode(errors='replace'),
        'stderr_preview': inventory_tests.stderr[-4000:].decode(errors='replace')}
    write(OUTPUT / 'route-inventory-tests.json', inventory_receipt)
    if (inventory_receipt['tests_passed'] != 2 or len(inventory_tests.stdout) > 131072
            or len(inventory_tests.stderr) > 131072):
        raise ValueError('Both global route-inventory tests required: ' + json.dumps(inventory_receipt))
    cli = TARGET / 'debug/osw-query-cli'
    first = context.build_contract()['collections'][context.ROUTES][0]
    request = cases.request(context.ROUTES, 'id', first['id'], limit=1)
    response = native_query(cli, OUTPUT / 'candidate.json', request)
    cases.verify_response(request, [first], response)
    write(OUTPUT / 'native-smoke.json', {'status': 'PASS', 'selected_route_id': first['id'],
        'mapped_features': len(response['map_scene']['features']), 'before_wasm_build': True})
    subprocess.run(commands[1], cwd=ROOT, env=env, check=True, timeout=1200)
    return TARGET / 'debug/osw-query-cli', TARGET / 'wasm32-unknown-unknown/release/osw_query.wasm'


def response_budget(request, index=False):
    return 2097152 if index or request.get('collection') in ['objects', context.ROUTES] else 131072


def native_query(cli, payload, request, index=False):
    result = subprocess.run([str(cli)] + (['--index'] if index else []) + [str(payload), '-'],
        input=json.dumps(request).encode(), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    budget = response_budget(request, index)
    audit = {'request': request, 'mode': 'index' if index else 'main', 'exit_code': result.returncode,
             'stdout_bytes': len(result.stdout), 'response_limit_bytes': budget,
             'stdout_sha256': delivery.sha(result.stdout), 'stderr_bytes': len(result.stderr),
             'stderr_sha256': delivery.sha(result.stderr),
             'stderr_preview': result.stderr[:2000].decode('utf-8', errors='replace')}
    QUERY_AUDIT.append(audit); write(OUTPUT / 'native-response-custody.json', QUERY_AUDIT)
    if result.returncode or len(result.stdout) > budget or len(result.stderr) > 32768:
        raise ValueError('Native query failed or exceeded declared budget: ' + json.dumps(audit))
    response = json.loads(result.stdout)
    if response.get('ok') is not True: raise ValueError('Native query refused: ' + str(response.get('error'))[:1000])
    return response


def resolve(document, pointer):
    value = document
    for token in pointer.split('/')[1:] if pointer else []:
        key = token.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def source_cases():
    result = [(path, '', read(path)) for path in sorted(delivery.DOCUMENTS)]
    contract = context.build_contract()
    for name in context.OWNER_FIELDS:
        for row in contract['collections'][name]:
            result.append((row['source_file'], row['source_pointer'], resolve(read(row['source_file']), row['source_pointer'])))
    for path in ['research/loop-manta-2023-published-metrics-v1.json',
                 'research/south-java-iskandar-2006-layer-source-facts-v1.json']:
        result.append((path, '', read(path)))
    if len(result) != cases.INDEX_CASE_COUNT: raise ValueError('Declared source-query scope changed')
    return result


def verify_engine(cli, wasm, parent, original_inventory, inventory, packet, expected):
    if not 8 < wasm.stat().st_size <= 64000000: raise ValueError('Compiled binary outside finite budget')
    with wasm.open('rb') as stream:
        if stream.read(8) != b'\x00asm\x01\x00\x00\x00': raise ValueError('Invalid WASM binary')
    deps = compiler.dependencies(wasm.with_suffix('.d').read_text(), ROOT, inventory)
    wasm_sha = digest(wasm)
    main_fixtures = []
    for request, rows in cases.main_cases(expected):
        response = native_query(cli, OUTPUT / 'candidate.json', request)
        cases.verify_response(request, rows, response)
        main_fixtures.append({'request': request, 'expected': response})
    index_fixtures = []
    for path, pointer, original in source_cases():
        request = {'document': path, 'pointer': pointer, 'limit': 500, 'offset': 0}
        response = native_query(cli, OUTPUT / 'index.json', request, index=True)
        rebuilt = {r['source_key']: r['record'] for r in response['rows']}
        if response['source_sha256'] != digest(ROOT / path) or context.encoded(rebuilt) != context.encoded(original):
            raise ValueError('Complete source query reconstruction differs: ' + path + pointer)
        index_fixtures.append({'request': request, 'expected': response})
    wrong = OUTPUT / 'wrong-index.json'; wrong.write_text('{"schema":"osw.almanac-index-bundle.v1","documents":{}}')
    refused = subprocess.run([str(cli), '--index', str(wrong)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    if refused.returncode != 2 or b'Changed index bundle or compiled catalog' not in refused.stderr:
        raise ValueError('Native compiled-catalog guard weakened')
    parity = {}
    for mode, payload, fixtures in [('main', OUTPUT / 'candidate.json', main_fixtures), ('index', OUTPUT / 'index.json', index_fixtures)]:
        metadata = OUTPUT / (mode + '-metadata.json')
        with metadata.open('xb') as stream:
            subprocess.run([str(cli)] + (['--index'] if mode == 'index' else []) + [str(payload)],
                           cwd=ROOT, stdout=stream, check=True, timeout=240)
        if metadata.stat().st_size > payload.stat().st_size + 2097152: raise ValueError('Metadata budget exceeded')
        fixture_path = OUTPUT / (mode + '-fixtures.json')
        write(fixture_path, {'payload_sha256': digest(payload), 'queries': fixtures})
        output = OUTPUT / (mode + '-parity.json')
        subprocess.run(['node', '--max-old-space-size=1536', 'analysis/check_eicc_reference_parity_v1.mjs', mode,
            str(wasm), str(payload), str(fixture_path), str(metadata), str(output), wasm_sha], cwd=ROOT,
            env=dict(os.environ, OSW_EICC_REFERENCE_DELIVERY_V1='1'), check=True, timeout=1200)
        parity[mode] = json.loads(output.read_bytes())
    snapshot_audit = {}
    expected_catalog = read(str((OUTPUT / 'expected-catalog.json').relative_to(ROOT)))
    for name in ['atlas', 'seasons']:
        path = OUTPUT / (name + '-native.json')
        with path.open('xb') as stream:
            subprocess.run([str(cli), str(OUTPUT / 'candidate.json'), '--' + name], cwd=ROOT,
                           stdout=stream, check=True, timeout=240)
        if path.stat().st_size > 134217728: raise ValueError('Complete presentation snapshot exceeds128MiB budget')
        parent_snapshot = read(str((OUTPUT / ('parent-' + name + '.json')).relative_to(ROOT)))
        child_snapshot = json.loads(path.read_bytes())
        snapshot_audit[name] = snapshot_custody.verify(parent_snapshot, child_snapshot, expected_catalog,
            (ROOT / delivery.DASHBOARD).read_text(encoding='utf-8'), packet['logical_sha256'])
        snapshot_audit[name].update(native_response_bytes=path.stat().st_size, native_response_sha256=digest(path))
        del parent_snapshot, child_snapshot; gc.collect()
    del expected_catalog; gc.collect()
    write(OUTPUT / 'snapshot-preservation.json', snapshot_audit)
    subprocess.run(['node', '--max-old-space-size=1536', 'analysis/check_eicc_snapshots_v3.mjs', 'candidate',
        str(wasm), str(OUTPUT / 'candidate.json'), str(OUTPUT), wasm_sha, packet['logical_sha256']],
        cwd=ROOT, env=dict(os.environ, OSW_EICC_SNAPSHOTS_V3='1'), check=True, timeout=1200)
    parity['snapshots'] = read(str((OUTPUT / 'snapshots-parity.json').relative_to(ROOT)))
    pins = read(PREFLIGHT)['input_sha256']
    # Pin the preflight itself too; request is deliberately mutable activation control.
    pins = {**pins, PREFLIGHT: digest(ROOT / PREFLIGHT)}
    paths = delivery.GENERATED | delivery.DOCUMENTS | set(pins) | {'almanac/' + p['path'] for p in descriptors(packet)}
    replacements = {p: digest(ROOT / p) for p in paths}
    version = subprocess.check_output(['rustc', '+1.95.0', '--version'], text=True).strip()
    manifest = delivery.engine_manifest(parent, original_inventory, inventory, replacements, pins, packet, read(delivery.SCOPE),
        wasm_sha=wasm_sha, compiler=version, parent_manifest_sha=delivery.PARENT_MANIFEST_SHA,
        source_commit=os.environ['GITHUB_SHA'], dependency_proof=deps)
    shutil.copyfile(wasm, ROOT / delivery.WASM); write(ROOT / delivery.MANIFEST, manifest)
    return {'wasm_sha256': wasm_sha, 'wasm_bytes': wasm.stat().st_size, 'compiler': version,
            'engine_manifest_sha256': digest(ROOT / delivery.MANIFEST), 'native_cli_sha256': digest(cli),
            'dependency_proof': deps, 'native_wasm_parity': parity}


def run_engine(inventory, relocations):
    OUTPUT.mkdir(parents=True, exist_ok=False)
    try:
        parent, updated_inventory, packet, expected = prepare(inventory, relocations)
        cli, wasm = compile_engine()
        engine = verify_engine(cli, wasm, parent, inventory, updated_inventory, packet, expected)
        paths = delivery.GENERATED | {delivery.WASM, delivery.MANIFEST} | {'almanac/' + p['path'] for p in descriptors(packet)}
        for path in sorted(paths):
            destination = OUTPUT / 'artifact' / path; destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, destination)
        engine.update(status='PASS', stage='engine_verified', rust_planning_tests_passed=6, rust_route_inventory_tests_passed=2, native_smoke_verified=True,
            verified_generated_artifact_paths=sorted(paths), verified_generated_sha256={p: digest(ROOT / p) for p in paths},
            source_commit=os.environ['GITHUB_SHA'], browser_verified=False, working_branch_installed=False)
        write(OUTPUT / 'engine.json', engine)
    except Exception as error:
        write(OUTPUT / 'failure.json', {'status': 'FAIL', 'stage': 'engine', 'source_commit': os.environ['GITHUB_SHA'],
            'error': (type(error).__name__ + ': ' + str(error))[:4000], 'working_branch_installed': False})
        raise


def browser_phase(env):
    source_controls(env, clean=False)  # Before opening derived payloads or starting any browser.
    if (OUTPUT / 'browser.json').exists() or (OUTPUT / 'result.json').exists():
        raise ValueError('Browser phase already completed')
    try:
        engine = read(str((OUTPUT / 'engine.json').relative_to(ROOT)))
        manifest, packet = read(delivery.MANIFEST), read('almanac/query-data.json')
        delivery.verify_candidate_identity(packet)
        paths = delivery.GENERATED | {delivery.WASM, delivery.MANIFEST} | {'almanac/' + p['path'] for p in descriptors(packet)}
        hashes = {p: digest(ROOT / p) for p in paths}
        custody = delivery.browser_phase_custody(engine, manifest, packet, hashes,
            manifest_sha=digest(ROOT / delivery.MANIFEST), source_commit=env['GITHUB_SHA'])
        prepared = read(str((OUTPUT / 'prepared.json').relative_to(ROOT)))
        inventory = prepared['compile_inventory']
        for path, pin in {**inventory['rust_source_sha256'], **inventory['compile_time_data_sha256']}.items():
            if digest(ROOT / path) != pin: raise ValueError('Engine phase compiled input changed: ' + path)
        write(OUTPUT / 'browser-phase-custody.json', custody)
        from check_eicc_reference_browser_v3 import browser_review
        browser = browser_review(ROOT, OUTPUT); write(OUTPUT / 'browser.json', browser)
        write(OUTPUT / 'result.json', {'schema': 'osw.eicc-reference-delivery-result.v5', 'status': 'PASS',
            'source_commit': env['GITHUB_SHA'], 'run_id': env['GITHUB_RUN_ID'], 'run_attempt': env['GITHUB_RUN_ATTEMPT'],
            'parent_logical_sha256': delivery.PARENT_LOGICAL_SHA, 'logical_sha256': packet['logical_sha256'],
            'logical_bytes': packet['logical_byte_length'], 'candidate_records': 108592,
            'artifact_paths': sorted(paths), 'generated_sha256': hashes, 'new_evidence_records': 15,
            'new_source_records': 3, 'named_currents': 106, 'scoped_width_records': 172,
            'main_query_comparisons': 24, 'source_query_comparisons': 25, 'presentation_api_comparisons': 2,
            'rust_planning_tests_passed': 6, 'rust_route_inventory_tests_passed': 2, 'native_smoke_before_wasm_build': True,
            'engine_verified_before_browser_installation': True, 'new_ranked_lengths': 0,
            'new_physical_dimensions_admitted': 0, 'new_named_eddies': 0, 'new_state_intersections': 0,
            'scientific_source_processing': False, 'browser_verified': True, 'visual_review_complete': False,
            'working_branch_installed': False, 'main_merged': False, 'full_goal_complete': False})
    except Exception as error:
        write(OUTPUT / 'failure.json', {'status': 'FAIL', 'stage': 'browser', 'source_commit': env['GITHUB_SHA'],
            'error': (type(error).__name__ + ': ' + str(error))[:4000], 'working_branch_installed': False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-delivery', action='store_true'); parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--engine-only', action='store_true'); parser.add_argument('--browser-only', action='store_true')
    args = parser.parse_args()
    if not args.cloud_delivery or sum([args.preflight_only, args.engine_only, args.browser_only]) != 1:
        parser.error('Choose exactly one explicit cloud phase; no payload opened')
    if args.browser_only: browser_phase(dict(os.environ)); return
    inventory, relocations = controls(dict(os.environ))
    if args.preflight_only: print('EICC v5 source preflight passed'); return
    run_engine(inventory, relocations)


if __name__ == '__main__': main()
