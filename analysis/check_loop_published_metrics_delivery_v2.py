"""One sequential cloud candidate, matching-engine and browser delivery case."""
import argparse
import copy
import functools
import gc
import gzip
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading

import loop_published_metrics_delivery_v1 as delivery
import loop_published_metrics_query_v1 as context
import check_south_java_model_layer_cloud_v1 as native
import check_south_java_catalog_engine_cloud_v1 as prior
import south_java_catalog_engine_v1 as compiler
from query_packet import read_bundle_bytes, write_packet, descriptors
from south_java_model_browser_custody_v1 import digest

ROOT = native.ROOT
OUTPUT = ROOT / '.pytest_cache/loop-published-metrics-delivery-v2'
TARGET = OUTPUT / 'build'
REQUEST = 'research/loop-published-metrics-delivery-request-v2.json'
PREFLIGHT = 'research/loop-published-metrics-delivery-preflight-v2.json'
WORKFLOW = '.github/workflows/loop-published-metrics-delivery-v2.yml'
QUERY_AUDIT = []


def read(path): return json.loads((ROOT / path).read_bytes())
def write(path, value): Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def response_budget(request, index=False):
    # Detailed pre-existing object records include geographic/evidence payloads.
    # Keep scalar responses at the original bound; never truncate any response.
    return 2097152 if index or request.get('collection') == 'objects' else 131072


def decode_response(result, request, index=False):
    budget = response_budget(request, index)
    if result.returncode or len(result.stdout) > budget or len(result.stderr) > 32768:
        raise ValueError(f"Native query exit={result.returncode}; collection={request.get('collection')}; "
                         f"document={request.get('document')}; stdout={len(result.stdout)}; limit={budget}; "
                         f"stderr={len(result.stderr)}")
    try: value = json.loads(result.stdout)
    except (ValueError, UnicodeError) as error: raise ValueError('Native query returned invalid JSON') from error
    if not isinstance(value, dict) or value.get('ok') is not True:
        raise ValueError('Native query refused: ' + str(value.get('error', 'invalid response') if isinstance(value, dict) else 'invalid response')[:1000])
    return value


def native_query(cli, payload, request, index=False):
    command = [str(cli)] + (['--index'] if index else []) + [str(payload), '-']
    result = subprocess.run(command, input=json.dumps(request).encode(), cwd=ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    audit = {'request': request, 'mode': 'index' if index else 'main', 'exit_code': result.returncode,
             'stdout_bytes': len(result.stdout), 'response_limit_bytes': response_budget(request, index),
             'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(), 'stderr_bytes': len(result.stderr)}
    try:
        response = decode_response(result, request, index)
        audit['decoded_successfully'] = True
        return response
    except Exception as error:
        audit['decoded_successfully'] = False; audit['error'] = str(error)[:1000]
        raise
    finally:
        QUERY_AUDIT.append(audit)
        if OUTPUT.is_dir(): write(OUTPUT / 'native-response-custody.json', QUERY_AUDIT)


def controls(env):
    native.cloud_environment(env)  # Refuse before opening any source, binary or payload locally.
    if env.get('GITHUB_EVENT_NAME') != 'push': raise ValueError('Exact working-branch push required')
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != env.get('GITHUB_SHA') or subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean exact source checkout required')
    remote = prior.saved.api('git/ref/heads/codex/current-measurement-gaps')['object']['sha']
    if remote != head: raise ValueError('Working branch moved; stale cloud case refused')
    request = read(REQUEST)
    if request.get('schema') != 'osw.loop-published-metrics-delivery-request.v2' or request.get('workflow') != WORKFLOW:
        raise ValueError('Wrong request schema/workflow')
    for key in ['execution_permitted', 'cloud_candidate_files_permitted', 'native_build_permitted',
                'wasm_build_permitted', 'browser_automation_permitted']:
        if request.get(key) is not True: raise ValueError('Single compatible cloud case disabled: ' + key)
    for key in ['scientific_source_processing_permitted', 'working_branch_installation_permitted',
                'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False: raise ValueError('Forbidden delivery permission: ' + key)
    if type(request.get('max_cloud_jobs')) is not int or request['max_cloud_jobs'] != 1 or type(request.get('max_heavy_local_jobs')) is not int or request['max_heavy_local_jobs'] != 0:
        raise ValueError('One cloud job and no local heavy work required')
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']: raise ValueError('Changed delivery preflight')
    for path, expected in read(PREFLIGHT)['input_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed delivery source: ' + path)
    for path, count in [*prior.FREEZES, (prior.PREFLIGHT, 21),
                        ('research/south-java-compiled-browser-preflight-v1.json', 24),
                        ('research/south-java-model-installation-preflight-v1.json', 31),
                        ('research/loop-published-metrics-query-preparation-v1.json', 17),
                        ('research/loop-published-metrics-delivery-preflight-v1.json', 53)]:
        pins = read(path)['input_sha256']
        if len(pins) != count: raise ValueError('Changed preserved input inventory')
        for name, expected in pins.items():
            if digest(ROOT / name) != expected: raise ValueError('Changed preserved source: ' + name)
    for path in read(PREFLIGHT)['disabled_requests']:
        if read(path)['execution_permitted'] is not False: raise ValueError('Older execution enabled: ' + path)
    phase = read('research/current-gap-delivery-phase.json')
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain')
    inventory = read(prior.INVENTORY)
    if len(inventory['rust_source_sha256']) != 98 or len(inventory['compile_time_data_sha256']) != 144:
        raise ValueError('Changed reviewed compiler-input inventory')
    for path, expected in {**inventory['rust_source_sha256'], **inventory['compile_time_data_sha256']}.items():
        if digest(ROOT / path) != expected: raise ValueError('Changed installed compilation input: ' + path)
    packet = read('almanac/query-data.json')
    if packet['logical_sha256'] != delivery.PARENT_LOGICAL_SHA or packet['logical_byte_length'] != delivery.PARENT_LOGICAL_BYTES:
        raise ValueError('Exact installed South Java parent required')
    if digest(ROOT / delivery.MANIFEST) != delivery.PARENT_MANIFEST_SHA or digest(ROOT / delivery.WASM) != delivery.PARENT_WASM_SHA:
        raise ValueError('Installed parent engine custody differs')
    if (ROOT / context.FILE).read_bytes() != context.encoded(context.build_contract()):
        raise ValueError('Changed prepared scalar contract')
    return inventory


def prepare(inventory):
    if shutil.disk_usage(ROOT).free < 4 * 1024**3: raise ValueError('At least4GiB cloud disk required')
    available = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    if available < 6 * 1024**3: raise ValueError('At least6GiB cloud memory required')
    parent_manifest = read(delivery.MANIFEST)
    for path in delivery.GENERATED:
        if digest(ROOT / path) != parent_manifest['sha256'][path]: raise ValueError('Parent generated-file custody differs')
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    if delivery.sha(raw) != delivery.PARENT_LOGICAL_SHA: raise ValueError('Parent packet bytes differ')
    bundle = json.loads(raw); del raw
    rows = bundle['collections']
    if (sum(map(len, rows.values())) != 108558 or len(rows['objects']) != 246
            or len(rows['widths']) != 172 or sum(r['type'] == 'named_current' for r in rows['objects']) != 106):
        raise ValueError('Installed parent inventory differs')
    contract = context.build_contract()
    candidate, dashboard, preservation = delivery.candidate(bundle, contract)
    del bundle, rows; gc.collect()
    documents = {path: (ROOT / path).read_bytes() for path in delivery.DOCUMENTS}
    generated, index_audit = delivery.source_index(read(delivery.CATALOG),
        (ROOT / 'almanac/index-data.json.gz').read_bytes(), read('almanac/index-sources.json'), documents, dashboard)
    candidate['manifest'] = delivery.packet_manifest(candidate['manifest'], generated, documents, index_audit)
    candidate['manifest'][delivery.RECEIPT]['parent_logical_sha256'] = delivery.PARENT_LOGICAL_SHA
    main = OUTPUT / 'candidate.json'; main.write_bytes(delivery.encoded(candidate))
    if main.stat().st_size != 189986194 or digest(main) != 'b4d60a69eeea0339e06088f0b1e737ef50ec2983521615dc96341dd69d736551':
        raise ValueError('Response-budget correction changed the previously prepared candidate')
    expected = {name: copy.deepcopy(candidate['collections'][name]) for name in context.OWNER_FIELDS}
    expected['sources'] = [r for r in candidate['collections']['sources'] if r['id'] in [context.PAPER, context.METHOD]]
    expected['owner'] = next(r for r in candidate['collections']['objects'] if r['id'] == context.TARGET)
    expected['legacy_depths'] = candidate['collections']['current_model_depth_context']
    counts = {name: len(values) for name, values in candidate['collections'].items()}
    del candidate; gc.collect()
    with main.open('rb') as source: packet = write_packet(ROOT / 'almanac/query-data.json', source.read())
    for path, body in {**generated, delivery.DASHBOARD: dashboard}.items(): (ROOT / path).write_bytes(body)
    updated_inventory = delivery.compile_inventory(inventory, digest(ROOT / delivery.CATALOG), packet['logical_sha256'])
    for path, expected_sha in updated_inventory['compile_time_data_sha256'].items():
        if digest(ROOT / path) != expected_sha: raise ValueError('Undeclared compile data change')
    index = OUTPUT / 'index.json'
    hashed = hashlib.sha256()
    with gzip.open(ROOT / 'almanac/index-data.json.gz', 'rb') as source, index.open('xb') as destination:
        for chunk in iter(lambda: source.read(1048576), b''):
            destination.write(chunk); hashed.update(chunk)
            if destination.tell() > 536870912: raise ValueError('Index exceeds reviewed byte budget')
    catalog = read(delivery.CATALOG)
    if hashed.hexdigest() != catalog['bundle_sha256'] or index.stat().st_size != catalog['bundle_bytes']:
        raise ValueError('Generated logical index custody differs')
    if index_audit['original_sources_verified'] != 597 or catalog['source_count'] != 601:
        raise ValueError('Unexpected source-index scope')
    write(OUTPUT / 'prepared.json', {'logical_sha256': packet['logical_sha256'], 'logical_bytes': packet['logical_byte_length'],
          'collection_counts': counts, 'preservation': preservation, 'source_index_audit': index_audit,
          'source_commit': os.environ['GITHUB_SHA'], 'source_processing': False})
    return parent_manifest, updated_inventory, packet, expected


def compile_engine():
    env = dict(os.environ, CARGO_TARGET_DIR=str(TARGET))
    commands = [
        ['cargo', '+1.95.0', 'build', '--offline', '--locked', '--manifest-path', 'rust/osw-query/Cargo.toml', '--bin', 'osw-query-cli'],
        ['cargo', '+1.95.0', 'rustc', '--offline', '--locked', '--release', '--target', 'wasm32-unknown-unknown',
         '--lib', '--crate-type', 'cdylib', '--manifest-path', 'rust/osw-query/Cargo.toml']]
    for command in commands: subprocess.run(command, cwd=ROOT, env=env, check=True, timeout=1200)
    return TARGET / 'debug/osw-query-cli', TARGET / 'wasm32-unknown-unknown/release/osw_query.wasm'


def main_requests(expected):
    summaries, events = expected[context.SUMMARIES], expected[context.EVENTS]
    def request(name, field, value): return {'collection': name, 'filters': [{'field': field, 'op': 'eq', 'value': value}], 'sort': {'field': 'id'}, 'limit': 100}
    result = [(request(context.SUMMARIES, 'entity_id', context.TARGET), summaries),
              (request(context.EVENTS, 'entity_id', context.TARGET), events),
              (context.build_contract()['example_queries'][2], [r for r in events if r['date'].startswith('2017-11')]),
              (request(context.SUMMARIES, 'uncertainty_km', None), summaries),
              (request(context.SUMMARIES, 'uncertainty_km', 0), []),
              (request(context.EVENTS, 'eddy_id', None), events)]
    for sid in [context.PAPER, context.METHOD]: result.append((request('sources', 'id', sid), [r for r in expected['sources'] if r['id'] == sid]))
    result.append((request('objects', 'id', context.TARGET), [expected['owner']]))
    result.append(({'collection': 'objects', 'record_type': 'named_current', 'limit': 1}, None))
    result.append(({'collection': 'current_model_depth_context', 'sort': {'field': 'id'}, 'limit': 100}, expected['legacy_depths']))
    return result


def verify_engine(cli, wasm, parent, original_inventory, inventory, packet, expected):
    if not 8 < wasm.stat().st_size <= 64000000: raise ValueError('Compiled binary outside reviewed size budget')
    with wasm.open('rb') as stream:
        if stream.read(8) != b'\x00asm\x01\x00\x00\x00': raise ValueError('Invalid compiled WASM format')
    deps = compiler.dependencies(wasm.with_suffix('.d').read_text(), ROOT, inventory)
    wasm_sha = digest(wasm)
    cases = main_requests(expected)
    main_fixtures = []
    for request, rows in cases:
        response = native_query(cli, OUTPUT / 'candidate.json', request)
        if rows is None:
            if response['total'] != 106: raise ValueError('Normal current inventory differs')
        else:
            key = request.get('sort', {}).get('field', 'id')
            if response['total'] != len(rows) or context.encoded(response['rows']) != context.encoded(sorted(rows, key=lambda r: r[key])):
                raise ValueError('Complete native scalar rows differ from prepared projection')
        if request['collection'] in context.OWNER_FIELDS and (response['map_scene'] is not None or response['chart_scene'] is not None):
            raise ValueError('Scalar evidence gained inferred geographic/time-series scenes')
        main_fixtures.append({'request': request, 'expected': response})
    source_requests = [(path, '', json.loads((ROOT / path).read_bytes())) for path in sorted(delivery.DOCUMENTS)]
    facts = read(context.FACTS)
    for name in context.OWNER_FIELDS:
        for row in context.build_contract()['collections'][name]:
            key, index = row['source_pointer'].strip('/').split('/')
            source_requests.append((context.FACTS, row['source_pointer'], facts[key][int(index)]))
    legacy = 'research/south-java-iskandar-2006-layer-source-facts-v1.json'
    source_requests.append((legacy, '', read(legacy)))
    index_fixtures = []
    for path, pointer, original in source_requests:
        request = {'document': path, 'pointer': pointer, 'limit': 500, 'offset': 0}
        response = native_query(cli, OUTPUT / 'index.json', request, index=True)
        rebuilt = {r['source_key']: r['record'] for r in response['rows']}
        if response['source_sha256'] != digest(ROOT / path) or native.fingerprint(rebuilt) != native.fingerprint(original):
            raise ValueError('Exact indexed source/pointer differs')
        index_fixtures.append({'request': request, 'expected': response})
    wrong = OUTPUT / 'wrong-index.json'; wrong.write_text('{"schema":"osw.almanac-index-bundle.v1","documents":{}}')
    refused = subprocess.run([str(cli), '--index', str(wrong)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    if refused.returncode != 2 or b'Changed index bundle or compiled catalog' not in refused.stderr:
        raise ValueError('Native compiled-catalog guard weakened')
    parity = {}
    for mode, payload, fixtures in [('main', OUTPUT / 'candidate.json', main_fixtures), ('index', OUTPUT / 'index.json', index_fixtures)]:
        metadata = OUTPUT / (mode + '-metadata.json')
        prior.capture([str(cli)] + (['--index'] if mode == 'index' else []) + [str(payload)], metadata, payload.stat().st_size + 2097152)
        fixture_path = OUTPUT / (mode + '-fixtures.json')
        write(fixture_path, {'payload_sha256': digest(payload), 'queries': fixtures})
        output = OUTPUT / (mode + '-parity.json')
        subprocess.run(['node', '--max-old-space-size=1536', 'analysis/check_loop_published_metrics_parity_v2.mjs', mode,
            str(wasm), str(payload), str(fixture_path), str(metadata), str(output), wasm_sha], cwd=ROOT,
            env=dict(os.environ, OSW_LOOP_PUBLISHED_METRICS_DELIVERY_V2='1'), check=True, timeout=1200)
        parity[mode] = json.loads(output.read_bytes())
    paths = delivery.GENERATED | delivery.DOCUMENTS | set(context.build_contract()['input_sha256'])
    paths |= {'almanac/' + p['path'] for p in descriptors(packet)}
    replacements = {p: digest(ROOT / p) for p in paths}
    compiler_version = subprocess.check_output(['rustc', '+1.95.0', '--version'], text=True).strip()
    manifest = delivery.engine_manifest(parent, original_inventory, inventory, replacements, packet,
        wasm_sha=wasm_sha, compiler=compiler_version, parent_manifest_sha=delivery.PARENT_MANIFEST_SHA,
        source_commit=os.environ['GITHUB_SHA'], dependency_proof=deps)
    shutil.copyfile(wasm, ROOT / delivery.WASM); write(ROOT / delivery.MANIFEST, manifest)
    return {'wasm_sha256': wasm_sha, 'wasm_bytes': wasm.stat().st_size,
            'engine_manifest_sha256': digest(ROOT / delivery.MANIFEST), 'native_cli_sha256': digest(cli),
            'compiler': compiler_version, 'dependency_proof': deps, 'native_wasm_parity': parity}


def browser_review():
    from playwright.sync_api import sync_playwright, expect
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    errors, originals, images, checked = [], [], [], []
    def snapshot(locator, name):
        path = OUTPUT / name; locator.screenshot(path=str(path))
        images.append({'path': name, 'sha256': digest(path), 'bytes': path.stat().st_size})
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--renderer-process-limit=1'])
            page = browser.new_page(viewport={'width': 1100, 'height': 950}); page.set_default_timeout(180000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda req: originals.append(req.url) if req.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
            page.goto(base + '/almanac/dashboard.html'); page.wait_for_function('window.oswDashboardSelection')
            page.locator('#dashboard-card-view').click(); page.locator('#dashboard-search').fill('Loop Current')
            card = page.locator('article[data-id="current:loop"]'); expect(card).to_be_visible()
            card.locator('details').evaluate('(el)=>el.open=true')
            link = card.get_by_role('link', name='Query published contour-length summaries'); link.focus(); link.press('Enter')
            page.wait_for_function('window.oswLastQueryResult?.collection === "current_reported_contour_length_summaries"')
            expect(page.locator('#query-rows tr')).to_have_count(2)
            expect(page.locator('#query-rows')).to_contain_text('1449 km')
            expect(page.locator('#query-rows')).to_contain_text('1495 km')
            expect(page.locator('#query-rows')).to_contain_text('not measurement error')
            checked.append('dashboard-keyboard-to-contour-summaries')
            page.locator('#query-rows button').first.focus(); page.locator('#query-rows button').first.press('Enter')
            expect(page.locator('#query-detail')).to_be_visible()
            expect(page.locator('#query-detail').get_by_role('link', name='Published source')).to_have_attribute('href', read(context.FACTS)['source']['url'])
            checked.append('publication-link-and-generic-detail')
            request = context.build_contract()['example_queries'][2]
            page.locator('#query-advanced').evaluate('(el)=>el.open=true'); page.locator('#query-json').fill(json.dumps(request))
            page.evaluate('window.oswLastQueryResult=null'); page.locator('#query-run-json').click()
            page.wait_for_function('window.oswLastQueryResult?.collection === "current_reported_separation_events"')
            expect(page.locator('#query-rows tr')).to_have_count(2)
            expect(page.locator('#query-rows')).to_contain_text('2017-11-10'); expect(page.locator('#query-rows')).to_contain_text('2017-11-21')
            checked.append('both-november-events-remain-distinct')
            for name in context.OWNER_FIELDS:
                url = context.query_url(name)
                page.goto(base + '/almanac/' + url); page.wait_for_function('window.oswLastQueryResult')
                result = page.evaluate('window.oswLastQueryResult')
                expected = context.build_contract()['collections'][name]
                if context.encoded(result['rows']) != context.encoded(sorted(expected, key=lambda r: r['date'] if name == context.EVENTS else r['id'])):
                    raise ValueError('Browser rows differ from complete prepared scalar records')
            checked.append('both-complete-collections-exact')
            # Exact source queries exercise the ordinary indexed workspace.
            source_url = context.source_query('/separation_events/0')
            page.goto(base + '/almanac/' + source_url); page.wait_for_function('window.oswSourceQueryResult')
            for path in sorted(delivery.DOCUMENTS):
                page.locator('#source-query-json').evaluate('(el)=>el.closest("details").open=true')
                page.locator('#source-query-json').fill(json.dumps({'document': path, 'pointer': '', 'limit': 500}))
                page.evaluate('window.oswSourceQueryResult=null'); page.locator('#source-query-run-json').click()
                page.wait_for_function('window.oswSourceQueryResult')
                result = page.evaluate('window.oswSourceQueryResult')
                if not prior.original_source_matches(result, (ROOT / path).read_bytes()): raise ValueError('Browser indexed source mismatch')
            checked.append('four-new-indexed-documents-exact')
            page.goto(base + '/almanac/loop-published-metrics.html')
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 950})
                expect(page.get_by_role('heading', name='Loop Current: length metrics and separation dates')).to_be_visible()
                if not page.locator('img').evaluate('(el)=>el.complete&&el.naturalWidth>0'): raise ValueError('Missing source chart')
                if page.evaluate('document.documentElement.scrollWidth>window.innerWidth'): raise ValueError('Evidence page horizontal overflow')
                expect(page.locator('time')).to_have_count(12)
                snapshot(page.locator('main'), 'loop-published-metrics-' + str(width) + 'px.png')
            checked.append('source-page-chart-and-phone-reflow')
            if errors or originals: raise ValueError('Browser errors or original downloads: ' + repr((errors, originals)))
            browser.close()
    except Exception as error:
        if 'page' in locals():
            try: page.screenshot(path=str(OUTPUT / 'browser-failure.png'), timeout=15000)
            except Exception: pass
        write(OUTPUT / 'browser-failure.json', {'status': 'FAIL', 'checks_completed': checked,
              'url': page.url if 'page' in locals() else None, 'errors': errors,
              'original_downloads': originals, 'error': str(error)[:1500]})
        raise
    finally: server.shutdown(); server.server_close()
    return {'checks': checked, 'screenshots': images, 'page_errors': errors, 'original_downloads': originals,
            'browser_verified': True, 'visual_review_complete': False}


def run(inventory):
    OUTPUT.mkdir(parents=True, exist_ok=False)
    try:
        parent, updated_inventory, packet, expected = prepare(inventory)
        cli, wasm = compile_engine()
        engine = verify_engine(cli, wasm, parent, inventory, updated_inventory, packet, expected)
        artifact_paths = delivery.GENERATED | {delivery.WASM, delivery.MANIFEST}
        artifact_paths |= {'almanac/' + p['path'] for p in descriptors(packet)}
        for path in sorted(artifact_paths):
            target = OUTPUT / 'artifact' / path; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        engine['verified_generated_artifact_paths'] = sorted(artifact_paths)
        engine['verified_generated_sha256'] = {p: digest(ROOT / p) for p in artifact_paths}
        engine['source_commit'] = os.environ['GITHUB_SHA']
        engine['browser_verified'] = False
        engine['working_branch_installed'] = False
        write(OUTPUT / 'engine.json', engine)
        del expected; gc.collect()
        browser = browser_review(); write(OUTPUT / 'browser.json', browser)
        result = {'schema': 'osw.loop-published-metrics-delivery-result.v2', 'status': 'PASS',
                  'source_commit': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
                  'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'parent_logical_sha256': delivery.PARENT_LOGICAL_SHA,
                  'logical_sha256': packet['logical_sha256'], 'logical_bytes': packet['logical_byte_length'],
                  'candidate_records': sum(read(str((OUTPUT / 'prepared.json').relative_to(ROOT)))['collection_counts'].values()),
                  'artifact_paths': sorted(artifact_paths), 'generated_sha256': {p: digest(ROOT / p) for p in artifact_paths},
                  'new_scalar_evidence_records': 14, 'named_currents': 106, 'scoped_width_records': 172,
                  'new_ranked_lengths': 0, 'new_physical_dimensions_admitted': 0, 'new_named_eddies': 0,
                  'new_state_intersections': 0, 'scientific_source_processing': False, 'browser_verified': True,
                  'visual_review_complete': False, 'working_branch_installed': False, 'main_merged': False,
                  'full_goal_complete': False}
        write(OUTPUT / 'result.json', result)
    except Exception as error:
        write(OUTPUT / 'failure.json', {'status': 'FAIL', 'source_commit': os.environ['GITHUB_SHA'],
              'error': (type(error).__name__ + ': ' + str(error))[:1500], 'working_branch_installed': False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-delivery', action='store_true'); parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    if not args.cloud_delivery: parser.error('Explicit cloud delivery required; no payload or browser opened')
    inventory = controls(dict(os.environ))
    if args.preflight_only: print('Compatible Loop delivery source preflight passed'); return
    run(inventory)


if __name__ == '__main__': main()
