"""Cloud controller: restore saved data, compile separately, verify both stores."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import check_south_java_model_browser_v1 as saved
import check_south_java_model_layer_cloud_v1 as native
import south_java_catalog_engine_v1 as engine
from south_java_model_browser_custody_v1 import digest
from query_packet import descriptors

ROOT = native.ROOT
OUTPUT = ROOT / '.pytest_cache/south-java-catalog-engine-v1'
TARGET = ROOT / '.pytest_cache/south-java-catalog-engine-build-v1/target'
REQUEST = 'research/south-java-catalog-engine-request-v1.json'
PREFLIGHT = 'research/south-java-catalog-engine-preflight-v1.json'
INVENTORY = 'research/south-java-compiled-catalog-build-inputs-v1.json'
MANIFEST = 'almanac/query-engine.manifest.json'
SCOPE = 'research/south-java-compiled-catalog-source-scope-v1.json'
FREEZES = [('research/eacc-coastal-reference-extent-preflight-v1.json', 83),
           ('research/current-local-extent-query-check-preflight-v2.json', 23),
           ('research/current-local-extent-ui-preflight-v1.json', 20), (native.PREFLIGHT, 26),
           ('research/south-java-saved-wasm-preflight-v1.json', 12),
           ('research/south-java-model-delivery-preflight-v1.json', 24),
           ('research/south-java-model-browser-preflight-v1.json', 24)]


def read(path): return json.loads((ROOT / path).read_bytes())
def write(path, value): Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def controls(env):
    native.cloud_environment(env)  # Refuse local execution before file reads.
    if env.get('CARGO_TARGET_DIR') != str(TARGET):
        raise ValueError('Separate cloud build target required')
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != env.get('GITHUB_SHA'):
        raise ValueError('Exact checked-out source commit required')
    request = read(REQUEST)
    if (request.get('schema') != 'osw.south-java-catalog-engine-request.v1'
            or request.get('execution_permitted') is not True
            or request.get('native_build_permitted') is not True or request.get('wasm_build_permitted') is not True
            or type(request.get('max_cloud_jobs')) is not int or request['max_cloud_jobs'] != 1
            or type(request.get('max_heavy_local_jobs')) is not int or request['max_heavy_local_jobs'] != 0):
        raise ValueError('Single matching-catalog cloud build is disabled')
    for key in ['browser_automation_permitted', 'scientific_source_processing_permitted',
                'installed_assets_change_permitted', 'main_merge_permitted']:
        if request.get(key) is not False: raise ValueError('Forbidden build permission: ' + key)
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']:
        raise ValueError('Changed build preflight')
    for path, expected in read(PREFLIGHT)['input_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed build source: ' + path)
    for path, count in FREEZES:
        pins = read(path)['input_sha256']
        if len(pins) != count: raise ValueError('Changed preserved source inventory')
        for name, expected in pins.items():
            if digest(ROOT / name) != expected: raise ValueError('Changed preserved source: ' + name)
    for path in [native.REQUEST, 'research/south-java-saved-wasm-request-v1.json',
                 'research/south-java-model-delivery-request-v1.json', saved.REQUEST]:
        if read(path)['execution_permitted'] is not False:
            raise ValueError('Earlier computation/browser request must be disabled')
    phase = read('research/current-gap-delivery-phase.json')
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain')
    inventory = read(INVENTORY)
    if (len(inventory['rust_source_sha256']) != 98 or len(inventory['compile_time_data_sha256']) != 144
            or len(inventory['excluded_test_only_data_references']) != 6):
        raise ValueError('Changed compiled input inventory')
    for path, expected in inventory['rust_source_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed current runtime source: ' + path)
    return inventory


def data_inputs(inventory):
    # These include the saved catalog: check only after exact artifact restoration.
    for path, expected in inventory['compile_time_data_sha256'].items():
        actual = digest(ROOT / path)
        if actual != expected:
            raise ValueError('Compile input differs: ' + path + '; expected=' + expected + '; actual=' + actual)


def restore(inventory):
    if shutil.disk_usage(ROOT).free < 3221225472:
        raise ValueError('At least3GiB free cloud disk required')
    available = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines()
                     if line.startswith('MemAvailable:'))
    if available < 6442450944:
        raise ValueError('At least6GiB available cloud memory required before restoration')
    OUTPUT.mkdir(parents=True, exist_ok=False)
    saved.OUTPUT.mkdir(parents=True, exist_ok=False)
    proof = saved.restore()  # Exact ZIP/parts/data/source/baseline-binary custody.
    data_inputs(inventory)
    parent_raw = (ROOT / MANIFEST).read_bytes()
    expected = read(saved.RESULT)['generated_sha256'][MANIFEST]
    if native.digest(parent_raw) != expected: raise ValueError('Unexpected restored parent engine manifest')
    (OUTPUT / 'parent-engine-manifest.json').write_bytes(parent_raw)
    write(OUTPUT / 'restored.json', {'source_commit': os.environ['GITHUB_SHA'], 'custody': proof,
          'parent_manifest_sha256': expected, 'rust_cargo_sources_verified': 98,
          'data_reference_bytes_verified': 144, 'scientific_source_processing': False})


def capture(command, target, limit):
    """Stream large initialization metadata; retain bounded native diagnostics."""
    errors = target.with_suffix('.stderr')
    with target.open('xb') as output, errors.open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=output, stderr=stderr)
        try: code = process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(); raise ValueError('Native metadata timed out')
    length = target.stat().st_size
    if code or not 0 < length <= limit or errors.stat().st_size > 32768:
        with errors.open('rb') as stream: detail = stream.read(1200).decode(errors='replace')
        raise ValueError('Native metadata exit=' + str(code) + ', bytes=' + str(length) + ', limit=' + str(limit) + ': ' + detail)


def stream_payloads():
    packet = read('almanac/query-data.json')
    main = OUTPUT / 'main.json'
    logical = hashlib.sha256()
    with main.open('xb') as destination:
        for part in descriptors(packet):
            with (ROOT / 'almanac' / part['path']).open('rb') as source:
                for chunk in iter(lambda: source.read(1048576), b''):
                    destination.write(chunk); logical.update(chunk)
    if main.stat().st_size != packet['logical_byte_length'] or logical.hexdigest() != packet['logical_sha256']:
        raise ValueError('Saved main payload changed')
    catalog = read(engine.CATALOG)
    if catalog['bundle_bytes'] > 536870912: raise ValueError('Source corpus exceeded reviewed budget')
    index = OUTPUT / 'index.json'
    hashed = hashlib.sha256()
    with gzip.open(ROOT / 'almanac/index-data.json.gz', 'rb') as source, index.open('xb') as destination:
        for chunk in iter(lambda: source.read(1048576), b''):
            destination.write(chunk); hashed.update(chunk)
            if destination.tell() > catalog['bundle_bytes']: raise ValueError('Source corpus exceeded declared bytes')
    if index.stat().st_size != catalog['bundle_bytes'] or hashed.hexdigest() != catalog['bundle_sha256']:
        raise ValueError('Source corpus changed')
    return main, index


def query(cli, payload, request, index=False):
    command = [str(cli)] + (['--index'] if index else []) + [str(payload), '-']
    result = subprocess.run(command, input=json.dumps(request).encode(), cwd=ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    limit = 2097152 if index else 131072
    if result.returncode or len(result.stdout) > limit or len(result.stderr) > 32768:
        raise ValueError('Native query exit=' + str(result.returncode) + ': ' + result.stderr.decode(errors='replace')[:1200])
    value = json.loads(result.stdout)
    if value.get('ok') is not True: raise ValueError('Native query refused')
    return value


def original_source_matches(response, raw):
    reconstructed = {row['source_key']: row['record'] for row in response['rows']}
    return (response['source_sha256'] == native.digest(raw)
            and native.fingerprint(reconstructed) == native.fingerprint(json.loads(raw)))


def parity(mode, cli, wasm, payload, wasm_sha):
    metadata = OUTPUT / (mode + '-metadata.json')
    capture([str(cli)] + (['--index'] if mode == 'index' else []) + [str(payload)],
            metadata, payload.stat().st_size + 2097152)
    fixtures = {'payload_sha256': digest(payload), 'queries': []}
    if mode == 'main':
        checks = read('research/south-java-model-layer-cloud-result-v3.json')['native_query_checks']
        for check in checks:
            request = {'collection': check['collection'], 'filters': check['filters'], 'sort': {'field': 'id'}, 'limit': 100}
            response = query(cli, payload, request)
            if response['total'] != check['total'] or [r['id'] for r in response['rows']] != check['row_ids']:
                raise ValueError('Main record inventory differs from the verified candidate')
            fixtures['queries'].append({'request': request, 'expected': response})
    else:
        from south_java_model_delivery_v1 import DOCUMENTS
        for path in sorted(DOCUMENTS):
            request = {'document': path, 'pointer': '', 'limit': 500, 'offset': 0}
            response = query(cli, payload, request, index=True)
            raw = (ROOT / path).read_bytes()
            if not original_source_matches(response, raw):
                raise ValueError('Indexed source differs from exact checked document: ' + path)
            fixtures['queries'].append({'request': request, 'expected': response})
        wrong = OUTPUT / 'wrong-index.json'
        wrong.write_text('{"schema":"osw.almanac-index-bundle.v1","documents":{}}')
        refused = subprocess.run([str(cli), '--index', str(wrong)], cwd=ROOT,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        if refused.returncode != 2 or b'Changed index bundle or compiled catalog' not in refused.stderr:
            raise ValueError('Native compiled-catalog guard did not reject mismatched corpus')
    fixture_path = OUTPUT / (mode + '-fixtures.json')
    write(fixture_path, fixtures)
    if fixture_path.stat().st_size > 6291456: raise ValueError('Parity fixture budget exceeded')
    out = OUTPUT / (mode + '-parity.json')
    result = subprocess.run(['node', '--max-old-space-size=1536', 'analysis/check_south_java_compiled_catalog_v1.mjs',
        mode, str(wasm), str(payload), str(fixture_path), str(metadata), str(out), wasm_sha], cwd=ROOT,
        env=dict(os.environ, OSW_SOUTH_JAVA_COMPILED_CATALOG='1'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)
    if result.returncode: raise ValueError('Compiled catalog ' + mode + ' parity failed: ' + result.stderr.decode(errors='replace')[:1200])
    return json.loads(out.read_bytes())


def finish(inventory):
    restored = json.loads((OUTPUT / 'restored.json').read_bytes())
    if restored['source_commit'] != os.environ['GITHUB_SHA']: raise ValueError('Restoration belongs to another source')
    data_inputs(inventory)
    if digest(ROOT / MANIFEST) != restored['parent_manifest_sha256']: raise ValueError('Parent engine manifest changed during compilation')
    saved.custody.verify(ROOT, read(saved.RESULT))
    wasm = TARGET / 'wasm32-unknown-unknown/release/osw_query.wasm'
    cli = TARGET / 'debug/osw-query-cli'
    if not cli.is_file() or not 8 < wasm.stat().st_size <= 64000000: raise ValueError('Missing or oversized compiled output')
    with wasm.open('rb') as stream:
        if stream.read(8) != b'\x00asm\x01\x00\x00\x00': raise ValueError('Unexpected compiled binary format')
    dependency_proof = engine.dependencies(wasm.with_suffix('.d').read_text(), ROOT, inventory)
    wasm_sha = digest(wasm)
    main, index = stream_payloads()
    main_result = parity('main', cli, wasm, main, wasm_sha)
    index_result = parity('index', cli, wasm, index, wasm_sha)
    compiler = subprocess.check_output(['rustc', '+1.95.0', '--version'], text=True).strip()
    parent = json.loads((OUTPUT / 'parent-engine-manifest.json').read_bytes())
    updated = engine.overlay(parent, inventory, read(SCOPE), wasm_sha256=wasm_sha, compiler=compiler,
        parent_manifest_sha256=restored['parent_manifest_sha256'], dependency_proof=dependency_proof)
    artifact = OUTPUT / 'artifact/almanac'; artifact.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(wasm, artifact / 'query-engine.wasm')
    write(artifact / 'query-engine.manifest.json', updated)
    receipt = {'schema': 'osw.south-java-catalog-engine-result.v1', 'status': 'PASS',
        'source_commit': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'restoration': restored, 'compiler': compiler, 'wasm_sha256': wasm_sha, 'wasm_bytes': wasm.stat().st_size,
        'engine_manifest_sha256': digest(artifact / 'query-engine.manifest.json'),
        'native_cli_sha256': digest(cli), 'main_query_responses_equal': len(main_result['checks']),
        'source_query_responses_equal': len(index_result['checks']), 'native_and_wasm_mismatched_corpus_refused': True,
        'pinned_rust_cargo_source_count': 98, 'pinned_data_reference_count': 144,
        'dependency_proof': dependency_proof, 'wasm_rebuilt': True, 'browser_verified': False,
        'compiler_dependency_record_sha256': digest(wasm.with_suffix('.d')),
        'native_cargo_arguments': ['+1.95.0', 'build', '--offline', '--locked', '--manifest-path',
                                  'rust/osw-query/Cargo.toml', '--bin', 'osw-query-cli'],
        'wasm_cargo_arguments': ['+1.95.0', 'rustc', '--offline', '--locked', '--release', '--target',
                                'wasm32-unknown-unknown', '--lib', '--crate-type', 'cdylib',
                                '--manifest-path', 'rust/osw-query/Cargo.toml'],
        'working_branch_installed': False, 'scientific_source_processing': False, 'new_physical_dimensions_admitted': 0}
    write(OUTPUT / 'result.json', receipt)
    print(json.dumps({'status': 'PASS', 'main_queries': 11, 'source_queries': 3, 'wasm_bytes': wasm.stat().st_size}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight-only', action='store_true'); mode.add_argument('--restore', action='store_true'); mode.add_argument('--finish', action='store_true')
    args = parser.parse_args()
    inventory = controls(dict(os.environ))
    if args.preflight_only: print('Matching-catalog source preflight passed'); return
    try:
        if args.restore: restore(inventory)
        else: finish(inventory)
    except Exception as error:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        write(OUTPUT / 'failure.json', {'status': 'FAIL', 'source_commit': os.environ['GITHUB_SHA'],
            'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
            'error': (type(error).__name__ + ': ' + str(error))[:1500], 'working_branch_installed': False})
        raise


if __name__ == '__main__': main()
