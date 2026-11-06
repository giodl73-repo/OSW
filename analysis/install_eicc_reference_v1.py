"""Cloud-only installation of the exact saved and visually reviewed EICC files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import eicc_reference_delivery_v7 as delivery
import eicc_saved_installation_v1 as rules
import install_south_java_model_v1 as prior
from query_packet import descriptors
from south_java_model_browser_custody_v1 import members

ROOT = prior.ROOT
REQUEST = rules.REQUEST
WORKFLOW = rules.WORKFLOW
PROOF = rules.PROOF
PREFLIGHT = 'research/eicc-reference-installation-preflight-v1.json'
REVIEW = 'research/eicc-reference-installation-visual-review-v1.json'
DELIVERY_PREFLIGHT = 'research/eicc-reference-delivery-preflight-v7.json'
PARENT_PROOF = 'research/loop-published-metrics-installed-v1.json'
INVENTORY = 'research/south-java-compiled-catalog-build-inputs-v1.json'
OUTPUT = ROOT / '.pytest_cache/eicc-reference-installation-v1'


def read(path):
    return json.loads((ROOT / path).read_bytes())


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


def proofs():
    values = {name: read(rules.PROOF_DIR + name + '.json') for name in
              ['result', 'engine', 'browser', 'browser-phase-custody', 'main-parity', 'index-parity',
               'snapshots-parity', 'snapshot-preservation', 'prepared']}
    review = read(REVIEW)
    rules.verify_proofs(review, values['result'], values['engine'], values['browser'],
                        values['browser-phase-custody'],
                        {mode: values[name + '-parity'] for mode, name in
                         [('main', 'main'), ('index', 'index'), ('snapshots', 'snapshots')]},
                        values['snapshot-preservation'])
    for path, row in review['retained_proof_files'].items():
        assert path.startswith(rules.PROOF_DIR)
        assert (ROOT / path).stat().st_size == row['bytes'] and prior.digest(ROOT / path) == row['sha256'], path
    assert prior.digest(ROOT / review['functional_result_file']) == review['functional_result_sha256']
    return review, values


def controls(env):
    prior.native.cloud_environment(env)  # Before request, source or artifact reads.
    if env.get('GITHUB_EVENT_NAME') != 'push' or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('Exact low-priority working-branch push required')
    source = prior.git('rev-parse', 'HEAD')
    assert source == env['GITHUB_SHA'] and not prior.git('status', '--porcelain', '--untracked-files=all')
    prior.remote_guard(source)
    request = read(REQUEST)
    rules.verify_request(request)
    assert prior.digest(ROOT / PREFLIGHT) == request['preflight_sha256']
    preflight = read(PREFLIGHT)
    for path, pin in preflight['input_sha256'].items():
        assert prior.digest(ROOT / path) == pin, path
    parent_proof = read(PARENT_PROOF)
    relocations = read(delivery.SCOPE)['historical_source_relocations']
    for path, count in preflight['preserve_inventories'].items():
        pins = read(path)['input_sha256']
        assert len(pins) == count, path
        for name, expected in pins.items():
            if name == 'almanac/loop-published-metrics.html':
                old = parent_proof['presentation_overlay']
                assert old['original_page_sha256'] == expected
                assert prior.digest(ROOT / old['original_page_archive_path']) == expected
                assert prior.digest(ROOT / name) == parent_proof['files'][name]['sha256']
            elif prior.digest(ROOT / name) != expected:
                found = [r for r in relocations if r['inventory'] == path and r['historical_path'] == name
                         and r['historical_sha256'] == expected]
                assert len(found) == 1, (path, name)
                assert prior.digest(ROOT / found[0]['archive_path']) == expected
                assert prior.digest(ROOT / name) == found[0]['candidate_sha256']
    assert len(preflight['disabled_requests']) == 24
    for path in preflight['disabled_requests']:
        assert read(path)['execution_permitted'] is False, path
    phase = read('research/current-gap-delivery-phase.json')
    assert phase['phase'] == 'source-review-only-v1' and phase['heavy_work_permitted'] is False
    for path, row in parent_proof['files'].items():
        assert prior.digest(ROOT / path) == row['sha256'] and (ROOT / path).stat().st_size == row['bytes'], path
    parent = read(delivery.MANIFEST)
    assert prior.digest(ROOT / delivery.MANIFEST) == delivery.PARENT_MANIFEST_SHA
    packet = read('almanac/query-data.json')
    assert packet['logical_sha256'] == delivery.PARENT_LOGICAL_SHA and packet['logical_byte_length'] == delivery.PARENT_LOGICAL_BYTES
    inventory = read(INVENTORY)
    checked = delivery.compile_inventory(inventory, parent, parent['sha256'][delivery.CATALOG],
                                         delivery.PARENT_LOGICAL_SHA, read(delivery.SCOPE))
    for path, pin in {**checked['rust_source_sha256'], **checked['compile_time_data_sha256']}.items():
        assert prior.digest(ROOT / path) == pin, path
    assert not (ROOT / PROOF).exists()
    proofs()
    return source, request, inventory, parent


def archive(row, filename):
    metadata = prior.browser.api('actions/artifacts/' + str(row['id']))
    assert metadata['expired'] is False and metadata['name'] == row['name']
    assert metadata['size_in_bytes'] == row['bytes'] and metadata['digest'] == 'sha256:' + row['sha256']
    assert metadata['workflow_run']['id'] == rules.CASE[0] and metadata['workflow_run']['head_sha'] == rules.CASE[3]
    path = OUTPUT / filename
    with path.open('xb') as stream:
        subprocess.run(['gh', 'api', 'repos/giodl73-repo/OSW/actions/artifacts/' + str(row['id']) + '/zip'],
                       stdout=stream, check=True, timeout=600)
    assert path.stat().st_size == row['bytes'] and prior.digest(path) == row['sha256']
    return path


def verify_saved_review(review):
    rid, attempt, _, _ = rules.CASE
    prior.verify_case(prior.browser.api(f'actions/runs/{rid}/attempts/{attempt}'),
                      prior.browser.api(f'actions/runs/{rid}/attempts/{attempt}/jobs'), rules.CASE)
    path = archive(review['evidence_artifact'], 'reviewed-evidence.zip')
    copies = {Path(name).name: name for name in review['retained_proof_files']}
    assert len(copies) == 14
    with zipfile.ZipFile(path) as saved:
        members(saved.infolist(), sorted(copies) + [r['path'] for r in review['screenshots']])
        for name, copy in copies.items():
            assert saved.read(name) == (ROOT / copy).read_bytes(), name
        for row in review['screenshots']:
            raw = saved.read(row['path'])
            assert len(raw) == row['bytes'] and rules.sha(raw) == row['sha256'], row['path']


def restore_and_verify(review, values, inventory, parent):
    result, engine = values['result'], values['engine']
    paths = rules.generated_paths(result)
    path = archive(review['candidate_artifact'], 'saved-candidate.zip')
    with zipfile.ZipFile(path) as saved:
        for info in members(saved.infolist(), sorted(paths)):
            target = ROOT / info.filename
            assert not target.is_symlink() and target.resolve().is_relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            with saved.open(info) as src, target.open('wb') as dst:
                shutil.copyfileobj(src, dst, length=1048576)
            assert target.stat().st_size == info.file_size
            assert prior.digest(target) == result['generated_sha256'][info.filename], info.filename
    packet = read('almanac/query-data.json')
    assert packet['logical_sha256'] == result['logical_sha256'] and packet['logical_byte_length'] == result['logical_bytes']
    logical, total = hashlib.sha256(), 0
    for part in descriptors(packet):
        path = ROOT / 'almanac' / part['path']
        assert path.stat().st_size == part['byte_length'] and prior.digest(path) == part['sha256']
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1048576), b''):
                logical.update(chunk)
                total += len(chunk)
    assert total == result['logical_bytes'] and logical.hexdigest() == result['logical_sha256']
    with (ROOT / delivery.WASM).open('rb') as stream:
        assert stream.read(8) == b'\x00asm\x01\x00\x00\x00'
    assert (ROOT / delivery.WASM).stat().st_size == engine['wasm_bytes']
    source_pins = {**read(DELIVERY_PREFLIGHT)['input_sha256'], DELIVERY_PREFLIGHT: prior.digest(ROOT / DELIVERY_PREFLIGHT)}
    replacement_paths = delivery.GENERATED | delivery.DOCUMENTS | set(source_pins) | {'almanac/' + p['path'] for p in descriptors(packet)}
    replacements = {p: prior.digest(ROOT / p) for p in replacement_paths}
    expected = delivery.engine_manifest(parent, inventory, values['prepared']['compile_inventory'],
        replacements, source_pins, packet, read(delivery.SCOPE), wasm_sha=engine['wasm_sha256'],
        compiler=engine['compiler'], parent_manifest_sha=delivery.PARENT_MANIFEST_SHA,
        source_commit=rules.CASE[3], dependency_proof=engine['dependency_proof'])
    manifest = read(delivery.MANIFEST)
    assert delivery.encoded(manifest) == delivery.encoded(expected)
    assert manifest['loop_published_metrics_presentation_revision_v1'] == parent['loop_published_metrics_presentation_revision_v1']
    custody = delivery.browser_phase_custody(engine, manifest, packet,
        {p: prior.digest(ROOT / p) for p in paths}, manifest_sha=prior.digest(ROOT / delivery.MANIFEST),
        source_commit=rules.CASE[3])
    assert custody == values['browser-phase-custody']
    return paths


def install(source, request, inventory, parent):
    prior.native.cloud_environment(dict(os.environ))
    main = prior.browser.api('git/ref/heads/main')['object']['sha']
    review, values = proofs()
    verify_saved_review(review)
    paths = restore_and_verify(review, values, inventory, parent)
    files = {p: prior.file_identity(p) for p in sorted(paths)}
    proof = {'schema': 'osw.eicc-reference-installed.v1', 'status': 'EXACT_REVIEWED_ARTIFACTS_INSTALLED',
        'installation_control_commit': source, 'installation_run_id': os.environ['GITHUB_RUN_ID'],
        'installation_run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'data_execution': rules.CASE,
        'logical_sha256': values['result']['logical_sha256'], 'logical_bytes': values['result']['logical_bytes'],
        'engine_manifest_sha256': values['engine']['engine_manifest_sha256'], 'wasm_sha256': values['engine']['wasm_sha256'],
        'files': files, 'review_sha256': prior.digest(ROOT / REVIEW), 'candidate_artifact': review['candidate_artifact'],
        'parent_installed_proof_sha256': prior.digest(ROOT / PARENT_PROOF),
        'named_currents': 106, 'scoped_width_records': 172, 'reference_route_rows': 80, 'reference_route_owners': 73,
        'new_reference_routes': 2, 'new_sampling_reference_points': 7, 'new_spectral_scale_records': 6, 'new_sources': 3,
        'new_physical_dimensions_admitted': 0, 'new_ranked_lengths': 0, 'new_named_eddies': 0, 'new_state_intersections': 0,
        'browser_verified': True, 'visual_review_complete': True, 'scientific_release_approved': False,
        'main_merged': False, 'local_preview_synchronized': False, 'full_goal_complete': False,
        'installed_commit_location': 'Cloud result.json binds this proof blob to the installed commit.'}
    (ROOT / PROOF).write_bytes(encode(proof))
    request['execution_permitted'] = False
    request['working_branch_installation_permitted'] = False
    request['status'] = 'DISABLED_IN_EXACT_SAVED_ARTIFACT_INSTALLATION_COMMIT'
    (ROOT / REQUEST).write_bytes(encode(request))
    allowed = paths | {PROOF, REQUEST}
    prior.git('add', '--', *sorted(allowed))
    changed = set(prior.git('diff', '--cached', '--name-only').splitlines())
    assert rules.FIXED | {PROOF, REQUEST} <= changed <= allowed
    for p, row in files.items():
        assert prior.git('rev-parse', ':' + p) == row['git_blob_oid'], p
    assert not prior.git('diff', '--name-only')
    prior.remote_guard(source)
    prior.git('-c', 'core.hooksPath=/dev/null', '-c', 'user.name=OSW data delivery',
              '-c', 'user.email=actions@users.noreply.github.com', 'commit', '-m',
              'Install reviewed EICC regional reference routes and published source support')
    installed = prior.git('rev-parse', 'HEAD')
    assert prior.git('rev-parse', 'HEAD^') == source
    prior.remote_guard(source)
    prior.git('push', 'origin', 'HEAD:refs/heads/' + prior.BRANCH)
    prior.remote_guard(installed)
    files.update({p: prior.file_identity(p) for p in [PROOF, REQUEST]})
    remote = prior.remote_files(installed, list(files))
    for p, row in files.items():
        assert remote[p] == {'__typename': 'Blob', 'oid': row['git_blob_oid'], 'byteSize': row['bytes']}, p
    assert prior.browser.api('git/ref/heads/main')['object']['sha'] == main
    receipt = {'schema': 'osw.eicc-reference-installation-result.v1', 'status': 'PASS',
        'installed_commit': installed, 'control_commit': source, 'run_id': os.environ['GITHUB_RUN_ID'],
        'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'remote_verified_files': files,
        'logical_sha256': values['result']['logical_sha256'], 'working_branch_installed': True,
        'request_disabled_in_installed_commit': True, 'main_unchanged': True,
        'local_preview_synchronized': False, 'new_physical_dimensions_admitted': 0, 'full_goal_complete': False}
    (OUTPUT / 'result.json').write_bytes(encode(receipt))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-install', action='store_true', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    source, request, inventory, parent = controls(dict(os.environ))
    if args.preflight_only:
        print('Exact saved EICC installation preflight passed')
        return
    OUTPUT.mkdir(parents=True, exist_ok=False)
    try:
        install(source, request, inventory, parent)
    except Exception as error:
        (OUTPUT / 'failure.json').write_bytes(encode({'status': 'FAIL', 'control_commit': source,
            'error': (type(error).__name__ + ': ' + str(error))[:2500],
            'instruction': 'Inspect authoritative branch before retry: push may already have succeeded.'}))
        raise


if __name__ == '__main__':
    main()
