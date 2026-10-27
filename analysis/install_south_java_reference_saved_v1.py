"""Cloud-only installation of the single exact reviewed South Java artifact.
No builds, packet/index decoding, original-field processing, browser or local sync.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

import south_java_reference_git_transport_v1 as transport

ROOT = Path(__file__).resolve().parents[1]
REPO = 'repos/giodl73-repo/OSW'
BRANCH = 'codex/current-measurement-gaps'
REQUEST = 'research/south-java-reference-installation-request-v1.json'
PREFLIGHT = 'research/south-java-reference-installation-preflight-v1.json'
PROOF = 'research/south-java-reference-installed-v1.json'
SAVED = 'research/south-java-reference-installation-saved-engine-manifest-v1.json'
FULL = 'research/south-java-reference-full-delivery-result-v4.json'
EXECUTION = 'research/south-java-reference-full-delivery-execution-review-v4.json'
REVIEW = 'research/south-java-reference-full-delivery-visual-review-v4.json'
BROWSER = 'research/south-java-reference-full-delivery-browser-v4.json'
INVENTORY = 'research/south-java-reference-full-delivery-compile-inventory-v4.json'
MANIFEST = 'almanac/query-engine.manifest.json'
OUT = ROOT / '.pytest_cache/south-java-reference-installation-v1'
PARENT_MANIFEST = 'a36845e583cf89ba49a1c75612da627f6d78bebacdc15fdf02574985d51d00fa'
LOGICAL = '233c156bf1e044e7378d5bb739633da59eadb28125d40fc3254dd503e2bc1a32'
FINAL_MANIFEST = 'e5ccd930ffeb1086821144fbe6c2ffcd3b94781750368b91465d7e83702daf34'
SOURCE = '542b94b390b84c0620f561938f053177203eb779'
BINARY = '33fa5177803cca74fb0cc8d50ee6f2171c45ea9e20fc47c656063d8e822522cd'


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


def verify_request(request):
    expected = {'schema': 'osw.south-java-reference-installation-request.v1',
        'execution_permitted': True, 'working_branch_installation_permitted': True,
        'cloud_git_object_transport_permitted': True, 'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}
    for key, value in expected.items():
        assert type(request.get(key)) is type(value) and request[key] == value, key
    for key in ['native_build_permitted', 'wasm_build_permitted', 'browser_automation_permitted',
                'scientific_source_processing_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        assert request.get(key) is False, key


def verify_results(full, execution, review, browser):
    assert full['status'] == execution['status'] == review['status'] == browser['status'] == 'PASS'
    assert full['source_commit'] == execution['source_commit'] == SOURCE
    assert str(full['run_id']) == str(execution['run_id']) == str(review['run_id']) == '40579934300'
    assert str(full['run_attempt']) == str(execution['run_attempt']) == str(review['run_attempt']) == '2'
    expected_tests = {'indian_coastal_context::tests': 8, 'current_gap_admissions::tests': 7,
        'south_java_reference::tests': 5, 'pacific_secc_reference::tests': 5, 'planning::tests': 6,
        'nwasc_reference_route::tests': 4, 'madagascar_coastal_curve::tests': 4}
    assert full['rust_test_counts'] == expected_tests and execution['rust_tests_passed'] == 39
    assert execution['python_tests_passed'] == 21
    assert full['browser_verified'] is browser['browser_verified'] is True
    assert full['main_query_comparisons'] == 20 and full['source_query_comparisons'] == 9
    assert full['presentation_api_comparisons'] == 2
    assert review['screenshots'] == browser['screenshots'] and len(review['screenshots']) == 7
    assert len({r['path'] for r in review['screenshots']}) == 7
    assert not browser['page_errors'] and not browser['original_downloads'] and not browser['missing_assets']
    assert full['logical_sha256'] == execution['logical_sha256'] == LOGICAL
    assert full['logical_bytes'] == execution['logical_bytes'] == 190512457
    assert full['wasm_sha256'] == execution['wasm_sha256'] == BINARY
    assert full['new_physical_dimensions'] == execution['new_physical_dimensions'] == 0
    assert full['working_branch_installed'] is execution['working_branch_installed'] is review['installed'] is False
    hashes = full['generated_sha256']
    assert len(hashes) == 20 and hashes[MANIFEST] == execution['engine_manifest_sha256'] == FINAL_MANIFEST
    assert hashes['almanac/query-engine.wasm'] == BINARY
    assert sum(p.startswith('almanac/query-parts/') for p in hashes) == 12
    assert all(not PurePosixPath(p).is_absolute() and '..' not in PurePosixPath(p).parts
        and '\\' not in p and re.fullmatch('[0-9a-f]{64}', h) for p, h in hashes.items())
    item = execution['candidate_artifact']
    assert item['id'] == 12770296976 and item['bytes'] == 97006910
    assert item['sha256'] == '0d3ffa561c6f2c3a2688b7ce82e6bb814ebe41c628be94232121a6ce1f508efd'
    return dict(hashes)


def file_sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def controls():
    # Refuse locally before reading a request, descriptor, full packet or index.
    assert os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('RUNNER_OS') == 'Linux'
    assert os.environ.get('GITHUB_EVENT_NAME') == 'push'
    assert os.environ.get('GITHUB_REPOSITORY') == 'giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        assert os.environ.get(key) == '1', key
    source = os.environ['GITHUB_SHA']
    assert transport.git('rev-parse', 'HEAD') == branch_head() == source
    request = read(REQUEST)
    verify_request(request)
    assert file_sha(ROOT / PREFLIGHT) == request['preflight_sha256']
    preflight = read(PREFLIGHT)
    for path, digest in preflight['input_sha256'].items():
        assert file_sha(ROOT / path) == digest, path
    phase = read('research/current-gap-delivery-phase.json')
    assert phase['phase'] == 'source-review-only-v1' and phase['heavy_work_permitted'] is False
    assert phase['max_heavy_local_jobs'] == 0 and phase['max_heavy_cloud_jobs'] == 1
    for path in preflight['disabled_requests']:
        value = read(path)
        assert value.get('execute', value.get('execution_permitted')) is False, path
    hashes = verify_results(read(FULL), read(EXECUTION), read(REVIEW), read(BROWSER))
    for name, count in [('main', 20), ('index', 9), ('snapshots', 2)]:
        parity = read('research/south-java-reference-full-delivery-' + name + '-parity-v4.json')
        assert parity['status'] == 'PASS' and len(parity['checks']) == count
        assert parity['initialization_metadata_equal'] is True
        assert all(row['entire_response_equal'] is True for row in parity['checks'])
        assert parity['wasm_sha256'] == BINARY
        if name == 'index':
            assert parity['mismatched_corpus_refused'] is True
        else:
            assert parity['payload_sha256'] == LOGICAL
    assert not (ROOT / PROOF).exists() and not (ROOT / SAVED).exists()
    assert file_sha(ROOT / MANIFEST) == PARENT_MANIFEST
    for path, identity in preflight['parent_files'].items():
        assert (ROOT / path).stat().st_size == identity['bytes'] and file_sha(ROOT / path) == identity['sha256'], path
    return source, request, preflight, hashes


def verify_candidate(target, old_manifest, full, hashes):
    final = json.loads((target / MANIFEST).read_bytes())
    assert file_sha(target / MANIFEST) == FINAL_MANIFEST
    for key in old_manifest:
        if key not in {'sha256', 'rustc'}:
            assert final[key] == old_manifest[key], key
    receipt = final['south_java_reference_engine_delivery_v4']
    assert receipt['source_commit'] == SOURCE and receipt['logical_sha256'] == LOGICAL
    assert receipt['matching_binary_sha256'] == BINARY and receipt['new_physical_dimensions'] == 0
    for path, digest in hashes.items():
        assert file_sha(target / path) == digest, path
        if path != MANIFEST:
            assert final['sha256'][path] == digest, path
    inventory = read(INVENTORY)
    for path, digest in {**inventory['rust_source_sha256'], **inventory['compile_time_data_sha256']}.items():
        actual = target / path if path in hashes else ROOT / path
        assert file_sha(actual) == digest and final['sha256'][path] == digest, path
    packet = json.loads((target / 'almanac/query-data.json').read_bytes())
    assert packet['logical_sha256'] == LOGICAL and packet['logical_byte_length'] == 190512457
    parts = packet['parts']
    assert len(parts) == 12 and sum(p['byte_length'] for p in parts) == 190512457
    assert {'almanac/' + p['path'] for p in parts} == {p for p in hashes if p.startswith('almanac/query-parts/')}
    for part in parts:
        path = 'almanac/' + part['path']
        assert hashes[path] == part['sha256'] and (target / path).stat().st_size == part['byte_length']
    assert full['logical_sha256'] == packet['logical_sha256']
    return final


def install(source, request, preflight, hashes):
    main = api(REPO + '/git/ref/heads/main')['object']['sha']
    protected = set(preflight['input_sha256']) | set(preflight['parent_files']) | set(preflight['disabled_requests'])
    protected -= set(hashes) | {REQUEST, PROOF, SAVED}
    before = objects(source, protected)
    assert all(before.values())
    execution = read(EXECUTION)
    item = {**execution['candidate_artifact'], 'run_id': execution['run_id'],
            'run_attempt': execution['run_attempt'], 'source_commit': execution['source_commit']}
    target = OUT / 'candidate'
    extract_verified(artifact(item, 'candidate.zip'), hashes, target)
    verify_candidate(target, read(MANIFEST), read(FULL), hashes)
    files, entries = {}, []
    bodies = [(p, target / p) for p in sorted(hashes)] + [(SAVED, target / MANIFEST)]
    for path, origin in bodies:
        raw = origin.read_bytes()
        identity = transport.store(raw)
        assert identity == oid(raw)
        files[path] = {'sha256': sha(raw), 'bytes': len(raw), 'git_blob_oid': identity}
        entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': identity})
        del raw
    proof = {'schema': 'osw.south-java-reference-installed.v1', 'status': 'EXACT_REVIEWED_ARTIFACT_INSTALLED',
        'installation_transport': 'cloud_git_nonforce_single_ref_v1', 'installation_control_commit': source,
        'installation_run_id': os.environ['GITHUB_RUN_ID'], 'installation_run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'files': dict(files), 'logical_sha256': LOGICAL, 'logical_bytes': 190512457,
        'engine_manifest_sha256': FINAL_MANIFEST, 'wasm_sha256': BINARY, 'candidate_artifact': item,
        'visual_review_sha256': file_sha(ROOT / REVIEW), 'coverage': read(FULL)['candidate_structural_coverage'],
        'new_physical_dimensions': 0, 'new_ranked_whole_current_lengths': 0,
        'browser_verified': True, 'visual_review_complete': True, 'local_preview_synchronized': False,
        'main_merged': False, 'full_goal_complete': False}
    request.update(execution_permitted=False, working_branch_installation_permitted=False,
        cloud_git_object_transport_permitted=False, status='DISABLED_IN_EXACT_ARTIFACT_INSTALLATION_COMMIT')
    for path, raw in [(PROOF, encode(proof)), (REQUEST, encode(request))]:
        identity = transport.store(raw)
        assert identity == oid(raw)
        files[path] = {'sha256': sha(raw), 'bytes': len(raw), 'git_blob_oid': identity}
        entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': identity})
    commit = transport.candidate(source, entries, OUT / 'installation.index')
    checked = transport.objects(commit, files)
    assert checked == {p: {'oid': r['git_blob_oid'], 'byteSize': r['bytes']} for p, r in files.items()}
    assert transport.objects(commit, protected) == before
    assert branch_head() == source and api(REPO + '/git/ref/heads/main')['object']['sha'] == main
    transport.publish(commit, BRANCH)
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
        print('Exact saved South Java installation preflight passed')
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
