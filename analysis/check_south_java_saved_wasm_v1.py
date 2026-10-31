"""One cloud stage: reproduce the verified candidate, test the saved WASM ABI."""
import argparse
import gc
import json
import os
from pathlib import Path
import subprocess

import check_south_java_model_layer_cloud_v1 as native

ROOT = native.ROOT
REQUEST = 'research/south-java-saved-wasm-request-v1.json'
PREFLIGHT = 'research/south-java-saved-wasm-preflight-v1.json'
OUTPUT = ROOT / '.pytest_cache/south-java-saved-wasm-v1'
PRIOR = 'research/south-java-model-layer-cloud-result-v3.json'


def controls(env):
    native.cloud_environment(env)  # Refuses before opening files on a local host.
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != env.get('GITHUB_SHA'):
        raise ValueError('Exact source checkout required')
    request = json.loads((ROOT / REQUEST).read_bytes())
    if (request.get('execution_permitted') is not True
            or request.get('schema') != 'osw.south-java-saved-wasm-request.v1'
            or type(request.get('max_cloud_jobs')) is not int
            or type(request.get('max_heavy_local_jobs')) is not int
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0):
        raise ValueError('Saved-engine compatibility stage is disabled')
    for name in ['installed_assets_change_permitted', 'source_processing_permitted',
                 'wasm_build_permitted', 'browser_automation_permitted', 'main_merge_permitted']:
        if request.get(name) is not False:
            raise ValueError('Forbidden stage permission: ' + name)
    raw = (ROOT / PREFLIGHT).read_bytes()
    if native.digest(raw) != request['preflight_sha256']:
        raise ValueError('Changed stage preflight')
    pref = json.loads(raw)
    for path, expected in pref['input_sha256'].items():
        if native.digest((ROOT / path).read_bytes()) != expected:
            raise ValueError('Changed stage input: ' + path)
    engine_manifest = (ROOT / 'almanac/query-engine.manifest.json').read_bytes()
    if (native.digest(engine_manifest) != pref['saved_engine_manifest_sha256']
            or json.loads(engine_manifest)['sha256']['almanac/query-engine.wasm'] != pref['saved_wasm_sha256']):
        raise ValueError('Changed installed engine identity')
    old_pref = json.loads((ROOT / native.PREFLIGHT).read_bytes())
    freezes = [(old_pref['input_sha256'], 26)]
    for path, count in [('research/eacc-coastal-reference-extent-preflight-v1.json', 83),
                        ('research/current-local-extent-query-check-preflight-v2.json', 23),
                        ('research/current-local-extent-ui-preflight-v1.json', 20)]:
        freezes.append((json.loads((ROOT / path).read_bytes())['input_sha256'], count))
    for pins, count in freezes:
        if len(pins) != count:
            raise ValueError('Changed prior freeze count')
        for path, expected in pins.items():
            if native.digest((ROOT / path).read_bytes()) != expected:
                raise ValueError('Changed preserved input: ' + path)
    phase = json.loads((ROOT / 'research/current-gap-delivery-phase.json').read_bytes())
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source processing must remain held')
    if json.loads((ROOT / native.REQUEST).read_bytes())['execution_permitted'] is not False:
        raise ValueError('Earlier compatibility stage must be disabled')
    prior = json.loads((ROOT / PRIOR).read_bytes())
    if (prior['status'] != 'PASS' or prior['run_id'] != '40146583480'
            or prior['run_attempt'] != '1' or len(prior['native_query_checks']) != 11
            or prior['new_physical_dimensions_admitted'] != 0):
        raise ValueError('Verified native result required')
    return old_pref, prior


def run(cli, pref, prior):
    OUTPUT.mkdir(exist_ok=False)
    # This unchanged, pinned implementation repeats only a metadata append, not science.
    native.run(cli, pref)
    report = json.loads((native.OUTPUT / 'result.json').read_bytes())
    for key in ['candidate_logical_sha256', 'candidate_logical_bytes', 'candidate_records',
                'native_query_checks', 'dashboard_projection']:
        if report[key] != prior[key]:
            raise ValueError('Candidate differs from verified native case: ' + key)
    candidate = native.OUTPUT / 'candidate.json'
    fixtures = {'candidate_sha256': prior['candidate_logical_sha256'], 'queries': []}
    # Metadata embeds the original manifest. Its budget follows the bound on the
    # exact candidate, plus 2MiB for metadata-only inventories; queries stay small.
    metadata_path = OUTPUT / 'native-metadata.json'
    metadata_budget = candidate.stat().st_size + 2097152
    write_native_metadata(cli, candidate, metadata_path, metadata_budget)
    for check in report['native_query_checks']:
        query = {'collection': check['collection'], 'filters': check['filters'],
                 'sort': {'field': 'id'}, 'limit': 100}
        result = subprocess.run([str(cli), str(candidate), '-'], input=json.dumps(query).encode(),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180, cwd=ROOT)
        response = native.decode_native_result(result)
        if response['total'] != check['total'] or [row['id'] for row in response['rows']] != check['row_ids']:
            raise ValueError('Native fixture differs from prior exact query')
        fixtures['queries'].append({'query': query, 'expected': response})
    fixture_path = OUTPUT / 'fixtures.json'
    fixture_path.write_text(json.dumps(fixtures, allow_nan=False) + '\n')
    if fixture_path.stat().st_size > 1572864:
        raise ValueError('Unexpected fixture size')
    del fixtures, response
    gc.collect()
    engine = ROOT / 'almanac/query-engine.wasm'
    manifest = json.loads((ROOT / 'almanac/query-engine.manifest.json').read_bytes())
    expected = manifest['sha256']['almanac/query-engine.wasm']
    env = dict(os.environ, OSW_SOUTH_JAVA_SAVED_WASM='1')
    result = subprocess.run(['node', '--max-old-space-size=1536', 'analysis/check_south_java_saved_wasm_v1.mjs',
                             str(candidate), str(engine), str(fixture_path), str(OUTPUT / 'result.json'),
                             expected, str(metadata_path)],
                            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)
    if result.returncode != 0:
        raise ValueError('Saved-engine check failed (exit ' + str(result.returncode) + '): '
                         + result.stderr.decode(errors='replace')[:1200])
    if len(result.stdout) > 32768 or len(result.stderr) > 32768:
        raise ValueError('Unexpected saved-engine diagnostic output size')
    print(result.stdout.decode())


def write_native_metadata(cli, candidate, target, budget):
    """Stream to a cloud-only file; never duplicate the manifest in fixtures."""
    stderr_path = target.with_suffix('.stderr')
    with target.open('xb') as output, stderr_path.open('xb') as errors:
        process = subprocess.Popen([str(cli), str(candidate)], cwd=ROOT,
                                   stdout=output, stderr=errors)
        try:
            # stdout is a regular file, so the child cannot block on a pipe.
            # Bound its growth while waiting, and retain exact size/status.
            import time
            deadline = time.monotonic() + 180
            while process.poll() is None:
                if target.stat().st_size > budget or stderr_path.stat().st_size > 32768:
                    process.kill(); process.wait()
                    raise ValueError('Native metadata export exceeded budget: '
                                     + str(target.stat().st_size) + '/' + str(budget) + ' bytes')
                if time.monotonic() > deadline:
                    process.kill(); process.wait()
                    raise ValueError('Native metadata export timed out; bytes=' + str(target.stat().st_size))
                time.sleep(0.2)
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
    length = target.stat().st_size
    if process.returncode != 0 or not 0 < length <= budget or stderr_path.stat().st_size > 32768:
        with stderr_path.open('rb') as stream:
            detail = stream.read(1200).decode(errors='replace')
        raise ValueError('Native metadata export exit=' + str(process.returncode)
                         + ', bytes=' + str(length) + ', budget=' + str(budget) + ': ' + detail)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-check', action='store_true')
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--cli', type=Path)
    args = parser.parse_args()
    if not args.cloud_check:
        parser.error('Explicit cloud stage required; no data opened')
    pref, prior = controls(dict(os.environ))
    if args.preflight_only:
        print('Saved-engine source preflight passed'); return
    if not args.cli:
        parser.error('Fresh native CLI required')
    cli = args.cli.resolve()
    if not cli.is_relative_to(ROOT / '.pytest_cache/south-java-model-layer-cloud-build-v1/target') or not cli.is_file():
        raise ValueError('Unexpected native executable')
    try:
        run(cli, pref, prior)
    except Exception as error:
        OUTPUT.mkdir(exist_ok=True)
        failure = {'schema': 'osw.south-java-saved-wasm-failure.v1', 'status': 'FAIL',
                   'source_commit': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
                   'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
                   'error': (type(error).__name__ + ': ' + str(error))[:1500],
                   'installed_assets_modified': False, 'wasm_rebuilt': False}
        (OUTPUT / 'failure.json').write_text(json.dumps(failure, indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
