"""Install exact reviewed Loop artifacts and an explicit presentation overlay."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import install_south_java_model_v1 as prior
import loop_saved_installation_v1 as rules
from query_packet import descriptors
from south_java_model_browser_custody_v1 import members

ROOT = prior.ROOT
REQUEST = 'research/loop-published-metrics-installation-request-v1.json'
PREFLIGHT = 'research/loop-published-metrics-installation-preflight-v1.json'
REVIEW = 'research/loop-published-metrics-installation-visual-review-v1.json'
RESULT = 'research/loop-published-metrics-delivery-result-v2.json'
PROOF = 'research/loop-published-metrics-installed-v1.json'
OUTPUT = ROOT / '.pytest_cache/loop-published-metrics-installation-v1'
WORKFLOW = '.github/workflows/install-loop-published-metrics-v1.yml'
CASES = [(40161471991, 2, 121073896660, '127894a648b916770452f8456a0d40e5fad4b5e3'),
         (40341522081, 2, 121637528927, 'c2585606dec595d426b9ffb18e524c93345949f5')]


def read(path):
    return json.loads((ROOT / path).read_bytes())


def controls():
    prior.native.cloud_environment(dict(os.environ))  # Refuse local work before reading artifacts.
    assert os.environ['GITHUB_EVENT_NAME'] == 'push'
    source = prior.git('rev-parse', 'HEAD')
    assert source == os.environ['GITHUB_SHA']
    assert not prior.git('status', '--porcelain', '--untracked-files=all')
    prior.remote_guard(source)
    request = read(REQUEST)
    assert request['schema'] == 'osw.loop-published-metrics-installation-request.v1'
    assert request['execution_permitted'] is True and request['working_branch_installation_permitted'] is True
    assert request['installation_workflow'] == WORKFLOW
    assert type(request['max_cloud_jobs']) is int and request['max_cloud_jobs'] == 1
    assert type(request['max_heavy_local_jobs']) is int and request['max_heavy_local_jobs'] == 0
    for key in ['native_build_permitted', 'wasm_build_permitted', 'browser_automation_permitted',
                'scientific_source_processing_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        assert request[key] is False, key
    assert prior.digest(ROOT / PREFLIGHT) == request['preflight_sha256']
    preflight = read(PREFLIGHT)
    for path, sha in preflight['input_sha256'].items():
        assert prior.digest(ROOT / path) == sha, path
    for path in preflight['preserve_inventories']:
        for name, sha in read(path)['input_sha256'].items():
            assert prior.digest(ROOT / name) == sha, name
    for path in preflight['disabled_requests']:
        assert read(path)['execution_permitted'] is False, path
    assert read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False
    inventory = read('research/south-java-compiled-catalog-build-inputs-v1.json')
    for path, sha in inventory['rust_source_sha256'].items():
        assert prior.digest(ROOT / path) == sha, path
    parent = read('research/south-java-model-installed-v1.json')
    packet = read('almanac/query-data.json')
    assert packet['logical_sha256'] == parent['logical_sha256']
    for path in ['almanac/query-data.json', rules.WASM, rules.MANIFEST, 'almanac/index-catalog.json',
                 'almanac/index-sources.json', 'almanac/index-data.json.gz', 'research/ocean-motion-dashboard.json']:
        assert prior.digest(ROOT / path) == parent['files'][path]['sha256'], path
    for path in [PROOF, rules.ARCHIVED_PAGE, rules.ARCHIVED_MANIFEST]:
        assert not (ROOT / path).exists(), path
    return source, request, inventory


def archive(artifact_id, size, sha, run_id, filename):
    metadata = prior.browser.api('actions/artifacts/' + str(artifact_id))
    assert not metadata['expired'] and metadata['size_in_bytes'] == size
    assert metadata['digest'] == 'sha256:' + sha and metadata['workflow_run']['id'] == run_id
    path = OUTPUT / filename
    with path.open('xb') as stream:
        subprocess.run(['gh', 'api', 'repos/giodl73-repo/OSW/actions/artifacts/' + str(artifact_id) + '/zip'],
                       stdout=stream, check=True, timeout=600)
    assert path.stat().st_size == size and prior.digest(path) == sha
    return path


def validate_review():
    review = read(REVIEW)
    assert review['status'] == 'APPROVED_EXACT_WORKING_BRANCH_DATA_INSTALLATION'
    assert review['visual_review_complete'] is True and review['actual_screenshots_inspected'] == 2
    assert review['scientific_release_approved'] is False and review['main_merge_approved'] is False
    assert prior.digest(ROOT / RESULT) == review['data_result_sha256']
    result = read(RESULT)
    assert result['status'] == 'PASS' and result['source_commit'] == CASES[0][3]
    assert result['logical_sha256'] == review['logical_sha256']
    for identity in CASES:
        rid, attempt, _, _ = identity
        prior.verify_case(prior.browser.api(f'actions/runs/{rid}/attempts/{attempt}'),
                          prior.browser.api(f'actions/runs/{rid}/attempts/{attempt}/jobs'), identity)
    path = archive(review['evidence_artifact_id'], review['evidence_artifact_bytes'],
                   review['evidence_artifact_sha256'], CASES[1][0], 'phone-review.zip')
    with zipfile.ZipFile(path) as saved:
        members(saved.infolist(), ['result.json'] + [r['path'] for r in review['screenshots']])
        raw = saved.read('result.json')
        assert rules.sha(raw) == review['functional_result_sha256']
        assert raw == (ROOT / 'research/loop-presentation-browser-result-v1.json').read_bytes()
        browser = json.loads(raw)
        assert browser['status'] == 'PASS' and browser['source_commit'] == CASES[1][3]
        assert browser['screenshots'] == review['screenshots']
        assert browser['page_sha256'] == review['page_sha256']
        for row in review['screenshots']:
            raw = saved.read(row['path'])
            assert len(raw) == row['bytes'] and rules.sha(raw) == row['sha256']
    return review, result


def install(source, request, inventory):
    main = prior.browser.api('git/ref/heads/main')['object']['sha']
    review, result = validate_review()
    paths = rules.generated_paths(result)
    path = archive(review['candidate_artifact_id'], review['candidate_artifact_bytes'],
                   review['candidate_artifact_sha256'], CASES[0][0], 'saved-candidate.zip')
    original_page = (ROOT / rules.PAGE).read_bytes()
    with zipfile.ZipFile(path) as saved:
        infos = members(saved.infolist(), sorted(paths))
        for info in infos:
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
        file = ROOT / 'almanac' / part['path']
        assert file.stat().st_size == part['byte_length']
        with file.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1048576), b''):
                logical.update(chunk)
                total += len(chunk)
    assert total == result['logical_bytes'] and logical.hexdigest() == result['logical_sha256']
    saved_manifest = (ROOT / rules.MANIFEST).read_bytes()
    revision = read('research/loop-published-metrics-presentation-revision-v1.json')
    revised_page = (ROOT / revision['candidate_path']).read_bytes()
    assert rules.sha(revised_page) == review['page_sha256']
    manifest = rules.presentation_manifest(saved_manifest, original_page, revised_page, revision, inventory)
    (ROOT / rules.ARCHIVED_PAGE).write_bytes(original_page)
    (ROOT / rules.ARCHIVED_MANIFEST).write_bytes(saved_manifest)
    (ROOT / rules.PAGE).write_bytes(revised_page)
    (ROOT / rules.MANIFEST).write_bytes(rules.encode(manifest))
    assert prior.digest(ROOT / rules.WASM) == result['generated_sha256'][rules.WASM]
    assert manifest['sha256'][rules.WASM] == result['generated_sha256'][rules.WASM]
    installed_paths = paths | {rules.PAGE, rules.ARCHIVED_PAGE, rules.ARCHIVED_MANIFEST}
    files = {p: prior.file_identity(p) for p in sorted(installed_paths)}
    proof = {'schema': 'osw.loop-published-metrics-installed.v1', 'status': 'EXACT_REVIEWED_ARTIFACTS_INSTALLED',
             'installation_control_commit': source, 'installation_run_id': os.environ['GITHUB_RUN_ID'],
             'installation_run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
             'logical_sha256': result['logical_sha256'], 'files': files,
             'data_execution': CASES[0], 'presentation_execution': CASES[1],
             'review_sha256': prior.digest(ROOT / REVIEW),
             'candidate_artifact_id': review['candidate_artifact_id'],
             'saved_engine_manifest_sha256': rules.sha(saved_manifest),
             'installed_engine_manifest_sha256': prior.digest(ROOT / rules.MANIFEST),
             'presentation_overlay': manifest[rules.OVERLAY],
             'named_currents': 106, 'scoped_width_records': 172,
             'new_scalar_evidence_records': 14, 'new_sources': 2,
             'new_physical_dimensions_admitted': 0, 'new_named_eddies': 0, 'new_state_intersections': 0,
             'browser_verified': True, 'visual_review_complete': True,
             'scientific_release_approved': False, 'main_merged': False,
             'installed_commit_location': 'Cloud result.json binds this proof blob to the installed commit.'}
    (ROOT / PROOF).write_bytes(rules.encode(proof))
    request['execution_permitted'] = False
    request['working_branch_installation_permitted'] = False
    (ROOT / REQUEST).write_bytes(rules.encode(request))
    allowed = installed_paths | {PROOF, REQUEST}
    prior.git('add', '--', *sorted(allowed))
    changed = set(prior.git('diff', '--cached', '--name-only').splitlines())
    assert {PROOF, REQUEST, rules.PAGE, rules.ARCHIVED_PAGE, rules.ARCHIVED_MANIFEST,
            rules.MANIFEST, rules.WASM, 'almanac/query-data.json'} <= changed <= allowed
    for p, row in files.items():
        assert prior.git('rev-parse', ':' + p) == row['git_blob_oid'], p
    assert not prior.git('diff', '--name-only')
    prior.remote_guard(source)
    prior.git('-c', 'core.hooksPath=/dev/null', '-c', 'user.name=OSW data delivery',
              '-c', 'user.email=actions@users.noreply.github.com', 'commit', '-m',
              'Install reviewed Loop contour summaries, separation events and readable source page')
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
    receipt = {'schema': 'osw.loop-published-metrics-installation-result.v1', 'status': 'PASS',
               'installed_commit': installed, 'control_commit': source,
               'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
               'remote_verified_files': files, 'logical_sha256': result['logical_sha256'],
               'working_branch_installed': True, 'request_disabled_in_installed_commit': True,
               'main_unchanged': True, 'local_preview_synchronized': False,
               'new_physical_dimensions_admitted': 0, 'full_goal_complete': False}
    (OUTPUT / 'result.json').write_bytes(rules.encode(receipt))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-install', action='store_true', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    source, request, inventory = controls()
    if args.preflight_only:
        print('Exact saved Loop installation preflight passed')
    else:
        OUTPUT.mkdir(parents=True, exist_ok=False)
        try:
            install(source, request, inventory)
        except Exception as error:
            (OUTPUT / 'failure.json').write_bytes(rules.encode({'status': 'FAIL', 'control_commit': source,
                'error': (type(error).__name__ + ': ' + str(error))[:1500],
                'instruction': 'Inspect authoritative branch before retry: push may already have succeeded.'}))
            raise
