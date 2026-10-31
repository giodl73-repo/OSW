"""Cloud browser review of saved data with its verified matching engine."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import check_south_java_catalog_engine_cloud_v1 as build
import check_south_java_model_browser_v1 as browser
import check_south_java_model_layer_cloud_v1 as native
import south_java_compiled_browser_custody_v1 as compiled
from south_java_model_browser_custody_v1 import digest, members

ROOT = native.ROOT
OUTPUT = ROOT / '.pytest_cache/south-java-compiled-browser-v1'
REQUEST = 'research/south-java-compiled-browser-request-v1.json'
PREFLIGHT = 'research/south-java-compiled-browser-preflight-v1.json'
REVIEW = 'research/south-java-catalog-engine-execution-review-v1.json'
RESULT = 'research/south-java-catalog-engine-result-v1.json'


def read(path): return json.loads((ROOT / path).read_bytes())
def write(path, value): Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def controls(env):
    native.cloud_environment(env)
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != env.get('GITHUB_SHA'): raise ValueError('Exact source checkout required')
    request = read(REQUEST)
    if (request.get('schema') != 'osw.south-java-compiled-browser-request.v1'
            or request.get('execution_permitted') is not True
            or request.get('browser_automation_permitted') is not True
            or type(request.get('max_cloud_jobs')) is not int or request['max_cloud_jobs'] != 1
            or type(request.get('max_heavy_local_jobs')) is not int or request['max_heavy_local_jobs'] != 0):
        raise ValueError('Single compiled-engine browser review is disabled')
    for key in ['native_build_permitted', 'wasm_build_permitted', 'local_browser_permitted',
                'scientific_source_processing_permitted', 'installed_assets_change_permitted', 'main_merge_permitted']:
        if request.get(key) is not False: raise ValueError('Forbidden browser permission: ' + key)
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']: raise ValueError('Changed browser preflight')
    for path, expected in read(PREFLIGHT)['input_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed browser input: ' + path)
    for path, count in [*build.FREEZES, (build.PREFLIGHT, 21)]:
        pins = read(path)['input_sha256']
        if len(pins) != count: raise ValueError('Changed preserved input inventory')
        for name, expected in pins.items():
            if digest(ROOT / name) != expected: raise ValueError('Changed preserved source: ' + name)
    for path in [native.REQUEST, 'research/south-java-saved-wasm-request-v1.json',
                 'research/south-java-model-delivery-request-v1.json', browser.REQUEST, build.REQUEST]:
        if read(path)['execution_permitted'] is not False:
            raise ValueError('Earlier compute/export/browser request must be disabled')
    phase = read('research/current-gap-delivery-phase.json')
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain')
    inventory = read(build.INVENTORY)
    for path, expected in inventory['rust_source_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed compiled runtime source: ' + path)
    return inventory


def apply_engine(inventory):
    # The unchanged function validates old-binary custody before the overlay.
    browser.OUTPUT.mkdir(parents=True, exist_ok=False)
    baseline = browser.restore()
    build.data_inputs(inventory)
    parent_raw = (ROOT / build.MANIFEST).read_bytes()
    review, result = read(REVIEW), read(RESULT)
    run = browser.api('actions/runs/' + str(review['run_id']))
    if (run['status'] != 'completed' or run['conclusion'] != 'success'
            or run['run_attempt'] != review['run_attempt'] or run['head_sha'] != review['executed_source_commit']
            or result['source_commit'] != review['executed_source_commit']):
        raise ValueError('Verified matching-engine run identity changed')
    artifact = review['engine_artifact']
    metadata = browser.api('actions/artifacts/' + str(artifact['id']))
    if (metadata['expired'] or metadata['workflow_run']['id'] != review['run_id']
            or metadata['size_in_bytes'] != artifact['bytes']
            or metadata['digest'] != 'sha256:' + artifact['sha256']):
        raise ValueError('Compiled engine artifact metadata changed')
    archive = OUTPUT / 'compiled-engine.zip'
    with archive.open('xb') as stream:
        subprocess.run(['gh', 'api', 'repos/giodl73-repo/OSW/actions/artifacts/' + str(artifact['id']) + '/zip'],
                       stdout=stream, check=True, timeout=300)
    if archive.stat().st_size != artifact['bytes'] or digest(archive) != artifact['sha256']:
        raise ValueError('Full compiled engine ZIP hash/size differs')
    staging = OUTPUT / 'overlay'
    with zipfile.ZipFile(archive) as saved:
        infos = saved.infolist()
        names = [info.filename for info in infos if not info.is_dir()]
        if set(names) != set(artifact['expected_paths']):
            raise ValueError('Unexpected compiled engine archive paths: ' + repr(names))
        for info in members(infos, artifact['expected_paths']):
            target = staging / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with saved.open(info) as source, target.open('xb') as destination:
                shutil.copyfileobj(source, destination, length=1048576)
            if target.stat().st_size != info.file_size: raise ValueError('Incomplete compiled overlay member')
    wasm = staging / 'almanac/query-engine.wasm'
    manifest = staging / build.MANIFEST
    if manifest.stat().st_size > 1048576: raise ValueError('Unexpected compiled manifest size')
    proof = compiled.verify(parent_raw, manifest.read_bytes(), digest(wasm), wasm.stat().st_size,
                            result, inventory, read(build.SCOPE))
    for path in artifact['expected_paths']:
        target = ROOT / path
        if target.is_symlink() or not target.resolve().is_relative_to(ROOT): raise ValueError('Unsafe overlay destination')
        shutil.copyfile(staging / path, target)
    generated = read(browser.RESULT)
    for path, expected in generated['generated_sha256'].items():
        if path != build.MANIFEST and digest(ROOT / path) != expected:
            raise ValueError('Saved generated data changed during engine overlay: ' + path)
    build.data_inputs(inventory)
    if digest(ROOT / build.MANIFEST) != result['engine_manifest_sha256'] or digest(ROOT / 'almanac/query-engine.wasm') != result['wasm_sha256']:
        raise ValueError('Applied engine overlay differs from verified build')
    return {'baseline_generated_custody': baseline, 'compiled_engine_overlay': proof,
            'logical_sha256': generated['logical_sha256'], 'active_wasm_sha256': result['wasm_sha256'],
            'compiled_engine_source_run_id': review['run_id'], 'compiled_engine_source_run_attempt': review['run_attempt'],
            'compiled_engine_artifact_id': artifact['id'], 'full_compiled_archive_sha256': artifact['sha256'],
            'compiled_runtime_source_count_verified': 98, 'compiled_data_reference_bytes_verified': 144,
            'working_branch_installed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-browser', action='store_true'); parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    if not args.cloud_browser: parser.error('Explicit cloud browser review required; no artifact opened')
    inventory = controls(dict(os.environ))
    if args.preflight_only: print('Compiled browser source preflight passed'); return
    OUTPUT.mkdir(parents=True, exist_ok=False)
    try:
        proof = apply_engine(inventory)
        write(OUTPUT / 'custody.json', proof)
        browser.run_browser(proof)
        # Driver writes only to its historical output folder; copy compact receipts
        # and PNGs into this stage's evidence folder without changing the driver.
    except Exception as error:
        write(OUTPUT / 'failure.json', {'status': 'FAIL', 'source_commit': os.environ['GITHUB_SHA'],
              'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
              'error': (type(error).__name__ + ': ' + str(error))[:1500], 'working_branch_installed': False})
        raise
    finally:
        if browser.OUTPUT.exists():
            for source in browser.OUTPUT.iterdir():
                if source.name == 'result.json' or source.suffix == '.png':
                    shutil.copyfile(source, OUTPUT / source.name)


if __name__ == '__main__': main()
