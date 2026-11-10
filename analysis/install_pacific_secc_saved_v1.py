"""Install the two exact reviewed Pacific SECC artifacts in one branch transaction.

Cloud only. No build, ocean-field processing, browser, packet decoding or local sync.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'repos/giodl73-repo/OSW'
BRANCH = 'codex/current-measurement-gaps'
REQUEST = 'research/pacific-secc-installation-request-v1.json'
PREFLIGHT = 'research/pacific-secc-installation-preflight-v1.json'
PROOF = 'research/pacific-secc-installed-v1.json'
REVIEW = 'research/pacific-secc-compact-map-visual-review-v2.json'
FULL = 'research/pacific-secc-full-delivery-result-v1.json'
COMPACT = 'research/pacific-secc-compact-map-result-v2.json'
SAVED = 'research/pacific-secc-installation-saved-engine-manifest-v1.json'
MANIFEST = 'almanac/query-engine.manifest.json'
OUT = ROOT / '.pytest_cache/pacific-secc-installation-v1'
PARENT_MANIFEST = 'c9ccda691c287f560be53a8bd422a7c364fc9a8e5d2300d6f4868efb9daaf4e9'
LOGICAL = 'f0e046651b75c84da488c4e81204e410b18f37256e102c26a0ab2f70b5f69184'
FINAL_MANIFEST = 'a36845e583cf89ba49a1c75612da627f6d78bebacdc15fdf02574985d51d00fa'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def oid(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def api(path, body=None, method=None):
    args = ['gh', 'api', path, '-H', 'Cache-Control: no-cache']
    if method:
        args += ['--method', method]
    if body is not None:
        args += ['--input', '-']
    return json.loads(subprocess.run(args, input=encode(body) if body is not None else None,
        stdout=subprocess.PIPE, check=True, timeout=600).stdout)


def objects(commit, paths):
    result = {}
    paths = sorted(paths)
    for start in range(0, len(paths), 40):
        batch = paths[start:start + 40]
        fields = [f'p{i}:object(expression:{json.dumps(commit + ":" + p)})'
                  '{... on Blob{oid byteSize}}' for i, p in enumerate(batch)]
        response = api('graphql', {'query': 'query{repository(owner:"giodl73-repo",name:"OSW"){' + ' '.join(fields) + '}}'})
        assert not response.get('errors'), response.get('errors')
        result.update({p: response['data']['repository'][f'p{i}'] for i, p in enumerate(batch)})
    return result


def branch_head():
    return api(REPO + '/git/ref/heads/' + BRANCH)['object']['sha']


def verify_request(request):
    expected = {'schema': 'osw.pacific-secc-installation-request.v1', 'execution_permitted': True,
        'working_branch_installation_permitted': True, 'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}
    for key, value in expected.items():
        assert type(request.get(key)) is type(value) and request[key] == value, key
    for key in ['native_build_permitted', 'wasm_build_permitted', 'browser_automation_permitted',
                'scientific_source_processing_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        assert request.get(key) is False, key


def verify_results(full, compact, review, saved_raw):
    assert full['status'] == compact['status'] == review['status'] == 'PASS'
    assert full['source_commit'] == 'c16a0e71610e0137a94d1f213fe073aca404195a'
    assert compact['source_commit'] == review['source_commit'] == '7064a663f5dc94a99a1167a7f79cedac8506e7da'
    assert str(full['run_id']) == '40540897264' and str(full['run_attempt']) == '2'
    assert str(compact['run_id']) == '40550268723' and str(compact['run_attempt']) == '1'
    assert full['browser_verified'] is True and full['main_query_comparisons'] == 18
    assert full['source_query_comparisons'] == 10 and full['presentation_api_comparisons'] == 2
    assert full['rust_test_counts'] == {'pacific_secc_reference::tests': 5, 'planning::tests': 6,
        'nwasc_reference_route::tests': 4, 'madagascar_coastal_curve::tests': 4}
    assert review['actual_screenshots_inspected'] == 4 and review['visual_review_complete'] is True
    assert review['screenshots'] == compact['screenshots'] and len(compact['checks']) == 5
    assert review['working_branch_installation_approved'] is True
    assert full['logical_sha256'] == compact['logical_sha256'] == LOGICAL
    assert full['logical_bytes'] == 190476712 and full['new_physical_dimensions'] == 0
    assert len(full['generated_sha256']) == 20 and len(compact['generated_sha256']) == 4
    assert compact['generated_sha256'] == review['generated_sha256']
    assert compact['unchanged_scientific_candidate_paths'] == {
        p: h for p, h in full['generated_sha256'].items() if p not in compact['generated_sha256']}
    assert len(compact['unchanged_scientific_candidate_paths']) == 18
    hashes = {**full['generated_sha256'], **compact['generated_sha256']}
    assert len(hashes) == 22 and hashes[MANIFEST] == sha(saved_raw) == FINAL_MANIFEST
    assert all(not PurePosixPath(p).is_absolute() and '..' not in PurePosixPath(p).parts
               and '\\' not in p for p in hashes)
    return hashes


def extract_verified(archive, hashes, target):
    """Accept exact members, optionally beneath one shared packaging directory."""
    with zipfile.ZipFile(archive) as saved:
        infos = [i for i in saved.infolist() if not i.is_dir()]
        names = [i.filename for i in infos]
        assert len(names) == len(set(names)) == len(hashes), 'Duplicate or extra artifact members'
        assert all('\\' not in n and not PurePosixPath(n).is_absolute()
                   and '..' not in PurePosixPath(n).parts for n in names), 'Unsafe member path'
        prefix = ''
        if set(names) != set(hashes):
            prefixes = {n.split('/', 1)[0] for n in names}
            assert len(prefixes) == 1
            prefix = next(iter(prefixes)) + '/'
            assert {n[len(prefix):] for n in names} == set(hashes), 'Changed artifact inventory'
        assert sum(i.file_size for i in infos) < 350_000_000
        for info in infos:
            path = info.filename[len(prefix):]
            assert info.file_size <= 80_000_000 and not info.flag_bits & 1
            raw = saved.read(info)
            assert sha(raw) == hashes[path], path
            dest = target / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)


def controls():
    assert os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('RUNNER_OS') == 'Linux'
    assert os.environ.get('GITHUB_EVENT_NAME') == 'push'
    assert os.environ.get('GITHUB_REPOSITORY') == 'giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    source = os.environ['GITHUB_SHA']
    assert branch_head() == source
    request = read(REQUEST)
    verify_request(request)
    assert sha((ROOT / PREFLIGHT).read_bytes()) == request['preflight_sha256']
    preflight = read(PREFLIGHT)
    for p, h in preflight['input_sha256'].items():
        assert sha((ROOT / p).read_bytes()) == h, p
    phase = read('research/current-gap-delivery-phase.json')
    assert phase['phase'] == 'source-review-only-v1' and phase['heavy_work_permitted'] is False
    for path in preflight['disabled_requests']:
        value = read(path)
        assert value.get('execute', value.get('execution_permitted')) is False, path
    hashes = verify_results(read(FULL), read(COMPACT), read(REVIEW), (ROOT / SAVED).read_bytes())
    for name, count in [('main', 18), ('index', 10), ('snapshots', 2)]:
        parity = read('research/pacific-secc-full-delivery-' + name + '-parity-v1.json')
        assert parity['status'] == 'PASS' and len(parity['checks']) == count
        assert parity['initialization_metadata_equal'] is True
        assert all(row['entire_response_equal'] is True for row in parity['checks'])
        assert parity['wasm_sha256'] == hashes['almanac/query-engine.wasm']
        if name == 'index':
            assert parity['mismatched_corpus_refused'] is True
        else:
            assert parity['payload_sha256'] == LOGICAL
    assert not (ROOT / PROOF).exists()
    assert sha((ROOT / MANIFEST).read_bytes()) == PARENT_MANIFEST
    for p, identity in preflight['parent_files'].items():
        raw = (ROOT / p).read_bytes()
        assert sha(raw) == identity['sha256'] and len(raw) == identity['bytes'], p
    return source, request, preflight, hashes


def artifact(row, filename):
    meta = api(REPO + '/actions/artifacts/' + str(row['id']))
    assert meta['expired'] is False and meta['size_in_bytes'] == row['bytes']
    assert meta['digest'] == 'sha256:' + row['sha256']
    assert meta['workflow_run']['id'] == row['run_id']
    assert meta['workflow_run']['head_sha'] == row['source_commit']
    run = api(REPO + f"/actions/runs/{row['run_id']}/attempts/{row['run_attempt']}")
    assert run['status'] == 'completed' and run['conclusion'] == 'success'
    assert run['head_sha'] == row['source_commit']
    path = OUT / filename
    with path.open('xb') as stream:
        subprocess.run(['gh', 'api', REPO + f"/actions/artifacts/{row['id']}/zip"],
                       stdout=stream, check=True, timeout=600)
    assert path.stat().st_size == row['bytes'] and sha(path.read_bytes()) == row['sha256']
    return path


def install(source, request, preflight, hashes):
    main = api(REPO + '/git/ref/heads/main')['object']['sha']
    protected = set(preflight['input_sha256']) | set(preflight['parent_files']) | set(preflight['disabled_requests'])
    protected -= set(hashes) | {REQUEST, PROOF}
    before = objects(source, protected)
    assert all(before.values())
    old_manifest = read(MANIFEST)
    review = read(REVIEW)
    target = OUT / 'candidate'
    for key, filename, result in [('full_candidate_artifact', 'full.zip', read(FULL)),
                                  ('overlay_artifact', 'overlay.zip', read(COMPACT))]:
        extract_verified(artifact(review[key], filename), result['generated_sha256'], target)
    for p, h in hashes.items():
        assert sha((target / p).read_bytes()) == h, p
    final = json.loads((target / MANIFEST).read_bytes())
    assert (target / MANIFEST).read_bytes() == (ROOT / SAVED).read_bytes()
    assert final['eacc_regional_connection_presentation_v4'] == old_manifest['eacc_regional_connection_presentation_v4']
    for namespace in ['eicc_reference_spectral_delivery_v1', 'loop_published_metrics_delivery_v1',
                      'loop_published_metrics_presentation_revision_v1', 'south_java_compiled_catalog_engine_v1',
                      'south_java_model_delivery_v1']:
        assert final[namespace] == old_manifest[namespace], namespace
    packet = json.loads((target / 'almanac/query-data.json').read_bytes())
    assert packet['logical_sha256'] == LOGICAL and packet['logical_byte_length'] == 190476712
    files = {}
    entries = []
    existing = objects(source, hashes)
    for p in sorted(hashes):
        raw = (target / p).read_bytes()
        identity = oid(raw)
        if existing[p] != {'oid': identity, 'byteSize': len(raw)}:
            blob = api(REPO + '/git/blobs', {'content': base64.b64encode(raw).decode(), 'encoding': 'base64'})
            assert blob['sha'] == identity
        files[p] = {'sha256': sha(raw), 'bytes': len(raw), 'git_blob_oid': identity}
        entries.append({'path': p, 'mode': '100644', 'type': 'blob', 'sha': identity})
        del raw
    proof = {'schema': 'osw.pacific-secc-installed.v1', 'status': 'EXACT_REVIEWED_ARTIFACTS_INSTALLED',
        'installation_control_commit': source, 'installation_run_id': os.environ['GITHUB_RUN_ID'],
        'installation_run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'files': files,
        'logical_sha256': LOGICAL, 'logical_bytes': 190476712, 'engine_manifest_sha256': FINAL_MANIFEST,
        'visual_review_sha256': sha((ROOT / REVIEW).read_bytes()),
        'full_candidate_artifact': review['full_candidate_artifact'], 'overlay_artifact': review['overlay_artifact'],
        'coverage': read(FULL)['candidate_structural_coverage'], 'new_physical_dimensions': 0,
        'new_ranked_whole_current_lengths': 0, 'browser_verified': True, 'visual_review_complete': True,
        'local_preview_synchronized': False, 'main_merged': False, 'full_goal_complete': False}
    request.update(execution_permitted=False, working_branch_installation_permitted=False,
                   status='DISABLED_IN_EXACT_ARTIFACT_INSTALLATION_COMMIT')
    for p, raw in [(PROOF, encode(proof)), (REQUEST, encode(request))]:
        blob = api(REPO + '/git/blobs', {'content': base64.b64encode(raw).decode(), 'encoding': 'base64'})
        assert blob['sha'] == oid(raw)
        files[p] = {'sha256': sha(raw), 'bytes': len(raw), 'git_blob_oid': blob['sha']}
        entries.append({'path': p, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    parent = api(REPO + '/git/commits/' + source)
    tree = api(REPO + '/git/trees', {'base_tree': parent['tree']['sha'], 'tree': entries})
    commit = api(REPO + '/git/commits', {'message': 'Install reviewed Pacific SECC reference reach and readable atlas cards',
                                      'tree': tree['sha'], 'parents': [source]})['sha']
    checked = objects(commit, files)
    for p, row in files.items():
        assert checked[p] == {'oid': row['git_blob_oid'], 'byteSize': row['bytes']}, p
    assert objects(commit, protected) == before
    diff = api(REPO + '/compare/' + source + '...' + commit)
    assert diff['total_commits'] == 1
    assert {r['filename'] for r in diff['files']} <= set(files)
    assert all(r['status'] in ['added', 'modified'] for r in diff['files'])
    assert branch_head() == source
    assert api(REPO + '/git/ref/heads/main')['object']['sha'] == main
    api(REPO + '/git/refs/heads/' + BRANCH, {'sha': commit, 'force': False}, method='PATCH')
    assert branch_head() == commit and objects(commit, files) == checked
    assert api(REPO + '/git/ref/heads/main')['object']['sha'] == main
    (OUT / 'result.json').write_bytes(encode({'status': 'PASS', 'installed_commit': commit,
        'control_commit': source, 'files': files, 'protected_paths_preserved': len(protected),
        'request_disabled_in_installed_commit': True, 'working_branch_installed': True,
        'main_unchanged': True, 'local_preview_synchronized': False, 'full_goal_complete': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-install', action='store_true', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    source, request, preflight, hashes = controls()
    if args.preflight_only:
        print('Exact saved Pacific SECC installation preflight passed')
        return
    OUT.mkdir(parents=True, exist_ok=False)
    try:
        install(source, request, preflight, hashes)
    except Exception as error:
        (OUT / 'failure.json').write_bytes(encode({'status': 'FAIL', 'control_commit': source,
            'error': (type(error).__name__ + ': ' + str(error))[:2500],
            'instruction': 'Inspect authoritative branch: ref update may already have succeeded.'}))
        raise


if __name__ == '__main__':
    main()
