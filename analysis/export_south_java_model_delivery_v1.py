"""Cloud-only saved candidate export; no installation or scientific extraction."""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import check_south_java_model_layer_cloud_v1 as native
import south_java_model_delivery_v1 as delivery
from check_south_java_saved_wasm_v1 import write_native_metadata

ROOT = native.ROOT
OUTPUT = ROOT / '.pytest_cache/south-java-model-delivery-v1'
PREFLIGHT = 'research/south-java-model-delivery-preflight-v1.json'
REQUEST = 'research/south-java-model-delivery-request-v1.json'
MANIFEST = 'almanac/query-engine.manifest.json'


def controls(env):
    native.cloud_environment(env)
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip() != env.get('GITHUB_SHA'):
        raise ValueError('Exact cloud source checkout required')
    request = json.loads((ROOT / REQUEST).read_bytes())
    if (request.get('schema') != 'osw.south-java-model-delivery-request.v1'
            or request.get('execution_permitted') is not True
            or request.get('cloud_derived_artifact_permitted') is not True
            or type(request.get('max_cloud_jobs')) is not int or request['max_cloud_jobs'] != 1
            or type(request.get('max_heavy_local_jobs')) is not int or request['max_heavy_local_jobs'] != 0):
        raise ValueError('Single cloud saved-candidate export is disabled')
    for key in ['installed_assets_change_permitted', 'scientific_source_processing_permitted',
                'wasm_build_permitted', 'browser_automation_permitted', 'main_merge_permitted']:
        if request.get(key) is not False:
            raise ValueError('Forbidden export permission: ' + key)
    raw = (ROOT / PREFLIGHT).read_bytes()
    if delivery.sha(raw) != request['preflight_sha256']:
        raise ValueError('Changed delivery preflight')
    pref = json.loads(raw)
    for path, expected in pref['input_sha256'].items():
        if delivery.sha((ROOT / path).read_bytes()) != expected:
            raise ValueError('Changed delivery source: ' + path)
    for path, count in [('research/eacc-coastal-reference-extent-preflight-v1.json', 83),
                        ('research/current-local-extent-query-check-preflight-v2.json', 23),
                        ('research/current-local-extent-ui-preflight-v1.json', 20),
                        (native.PREFLIGHT, 26), ('research/south-java-saved-wasm-preflight-v1.json', 12)]:
        pins = json.loads((ROOT / path).read_bytes())['input_sha256']
        if len(pins) != count:
            raise ValueError('Changed preserved source inventory')
        for name, expected in pins.items():
            if delivery.sha((ROOT / name).read_bytes()) != expected:
                raise ValueError('Changed preserved source: ' + name)
    for path in [native.REQUEST, 'research/south-java-saved-wasm-request-v1.json']:
        if json.loads((ROOT / path).read_bytes())['execution_permitted'] is not False:
            raise ValueError('Prior compatibility request must be disabled')
    phase = json.loads((ROOT / 'research/current-gap-delivery-phase.json').read_bytes())
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain')
    if delivery.sha((ROOT / MANIFEST).read_bytes()) != '2d07f5c5d83f1e610c2dccd07790f184d1aa6d8497d2eedca3ce5f4418e36609':
        raise ValueError('Installed engine manifest identity changed')
    return pref


def parity(cli, candidate, native_checks):
    fixtures = {'candidate_sha256': delivery.sha(candidate.read_bytes()), 'queries': []}
    for check in native_checks:
        query = {'collection': check['collection'], 'filters': check['filters'], 'sort': {'field': 'id'}, 'limit': 100}
        response = native.decode_native_result(subprocess.run([str(cli), str(candidate), '-'],
            input=json.dumps(query).encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180, cwd=ROOT))
        if response['total'] != check['total'] or [row['id'] for row in response['rows']] != check['row_ids']:
            raise ValueError('Final exported candidate differs from verified record inventory')
        fixtures['queries'].append({'query': query, 'expected': response})
    fixture_path = OUTPUT / 'query-fixtures.json'
    fixture_path.write_bytes(delivery.encoded(fixtures))
    if fixture_path.stat().st_size > 1572864:
        raise ValueError('Query fixture budget exceeded')
    metadata_path = OUTPUT / 'native-metadata.json'
    write_native_metadata(cli, candidate, metadata_path, candidate.stat().st_size + 2097152)
    del fixtures, response
    gc.collect()
    result = subprocess.run(['node', '--max-old-space-size=1536', 'analysis/check_south_java_saved_wasm_v1.mjs',
        str(candidate), str(ROOT / delivery.WASM), str(fixture_path), str(OUTPUT / 'parity.json'),
        delivery.WASM_SHA, str(metadata_path)], cwd=ROOT, env=dict(os.environ, OSW_SOUTH_JAVA_SAVED_WASM='1'),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)
    if result.returncode != 0:
        raise ValueError('Final candidate saved-WASM parity failed: ' + result.stderr.decode(errors='replace')[:1200])
    return json.loads((OUTPUT / 'parity.json').read_bytes())


def run(cli):
    from query_packet import write_packet
    if shutil.disk_usage(ROOT).free < 3221225472:
        raise ValueError('At least3GiB free cloud disk required')
    available = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines()
                     if line.startswith('MemAvailable:'))
    if available < 6442450944:
        raise ValueError('At least6GiB available cloud memory required before packet load')
    OUTPUT.mkdir(exist_ok=False)
    engine_raw = (ROOT / MANIFEST).read_bytes()
    parent_engine = json.loads(engine_raw)
    for path in delivery.GENERATED:
        expected = parent_engine['sha256'].get(path)
        with (ROOT / path).open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != expected:
            raise ValueError('Installed parent generated-file custody changed: ' + path)
    with (ROOT / delivery.WASM).open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != delivery.WASM_SHA:
            raise ValueError('Installed binary changed')
    native.run(cli, json.loads((ROOT / native.PREFLIGHT).read_bytes()))
    baseline_report = json.loads((native.OUTPUT / 'result.json').read_bytes())
    verified = json.loads((ROOT / 'research/south-java-saved-wasm-result-v3.json').read_bytes())
    if baseline_report['candidate_logical_sha256'] != verified['candidate_sha256']:
        raise ValueError('Verified baseline candidate changed')
    bundle = json.loads((native.OUTPUT / 'candidate.json').read_bytes())
    collection_hash = native.fingerprint(bundle['collections'])
    dashboard_raw = bundle['manifest']['dashboard_receipt']['source_json'].encode()
    documents = {path: (ROOT / path).read_bytes() for path in delivery.DOCUMENTS}
    generated, audit = delivery.source_index(json.loads((ROOT / 'almanac/index-catalog.json').read_bytes()),
        (ROOT / 'almanac/index-data.json.gz').read_bytes(),
        json.loads((ROOT / 'almanac/index-sources.json').read_bytes()), documents, dashboard_raw)
    bundle['manifest'] = delivery.packet_manifest(bundle['manifest'], generated, documents,
        verified_candidate_sha=verified['candidate_sha256'], index_audit=audit)
    if native.fingerprint(bundle['collections']) != collection_hash:
        raise ValueError('Scientific/context collections changed during generated-custody update')
    raw = delivery.encoded(bundle)
    del bundle
    gc.collect()
    if len(raw) > 210000000:
        raise ValueError('Final candidate byte budget exceeded')
    candidate = OUTPUT / 'final-candidate.json'
    candidate.write_bytes(raw)
    packet = write_packet(ROOT / 'almanac/query-data.json', raw)
    del raw
    gc.collect()
    for path, body in {**generated, delivery.DASHBOARD: dashboard_raw}.items():
        (ROOT / path).write_bytes(body)
    paths = delivery.GENERATED | delivery.UI | delivery.DOCUMENTS | {delivery.FIGURE}
    paths |= {'almanac/' + part['path'] for part in packet['parts']}
    replacements = {path: delivery.sha((ROOT / path).read_bytes()) for path in paths}
    updated_engine = delivery.engine_manifest(parent_engine, replacements, packet, source_commit=os.environ['GITHUB_SHA'])
    (ROOT / MANIFEST).write_bytes(delivery.encoded(updated_engine))
    del generated, dashboard_raw
    gc.collect()
    checks = parity(cli, candidate, baseline_report['native_query_checks'])
    result = {'schema': 'osw.south-java-model-delivery-candidate.v1', 'status': 'PASS',
        'source_commit': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
        'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'logical_sha256': packet['logical_sha256'],
        'logical_bytes': packet['logical_byte_length'], 'collections_sha256': collection_hash,
        'candidate_records': 108558, 'named_currents': 106, 'scoped_width_records': 172,
        'new_context_records': 5, 'new_provenance_entries': 2, 'index_audit': audit,
        'saved_wasm_sha256': delivery.WASM_SHA, 'native_wasm_queries_equal': len(checks['native_wasm_checks']),
        'initialization_metadata_equal': checks['initialization_metadata_equal'],
        'generated_sha256': {path: delivery.sha((ROOT / path).read_bytes()) for path in delivery.GENERATED | {MANIFEST}},
        'wasm_rebuilt': False, 'browser_verified': False, 'working_branch_installed': False,
        'scientific_source_processing': False, 'new_physical_dimensions_admitted': 0, 'main_merged': False}
    artifact = OUTPUT / 'artifact'
    artifact_paths = delivery.GENERATED | {MANIFEST} | {'almanac/' + part['path'] for part in packet['parts']}
    for path in sorted(artifact_paths):
        target = artifact / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)
    result['artifact_paths'] = sorted(artifact_paths)
    (OUTPUT / 'result.json').write_bytes(delivery.encoded(result))
    print(json.dumps({'status': result['status'], 'rows': result['candidate_records'],
                      'native_wasm_queries_equal': result['native_wasm_queries_equal']}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-export', action='store_true')
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--cli', type=Path)
    args = parser.parse_args()
    if not args.cloud_export:
        parser.error('Explicit cloud export required; no packet or index opened')
    controls(dict(os.environ))
    if args.preflight_only:
        print('Delivery source preflight passed'); return
    if not args.cli:
        parser.error('Native comparison CLI required')
    cli = args.cli.resolve()
    if not cli.is_relative_to(ROOT / '.pytest_cache/south-java-model-layer-cloud-build-v1/target') or not cli.is_file():
        raise ValueError('Unexpected comparison executable')
    try:
        run(cli)
    except Exception as error:
        OUTPUT.mkdir(exist_ok=True)
        (OUTPUT / 'failure.json').write_bytes(delivery.encoded({'status': 'FAIL',
            'source_commit': os.environ['GITHUB_SHA'], 'error': (type(error).__name__ + ': ' + str(error))[:1500],
            'working_branch_installed': False, 'scientific_source_processing': False}))
        raise


if __name__ == '__main__':
    main()
