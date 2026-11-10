"""Cloud-only installation of the single exact reviewed Azores section artifact.
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

import verified_artifact_git_transport_v1 as transport

ROOT = Path(__file__).resolve().parents[1]
REPO = 'repos/giodl73-repo/OSW'
BRANCH = 'codex/current-measurement-gaps'
REQUEST = 'research/azores-2009-section-installation-request-v1.json'
PREFLIGHT = 'research/azores-2009-section-installation-preflight-v1.json'
PROOF = 'research/azores-2009-section-installed-v1.json'
SAVED = 'research/azores-2009-section-installation-saved-engine-manifest-v1.json'
FULL = 'research/azores-2009-section-engine-evidence-v1.json'
EXECUTION = 'research/azores-2009-section-delivery-execution-review-v1.json'
REVIEW = 'research/azores-2009-section-runtime-visual-review-v1.json'
BROWSER = 'research/azores-2009-section-browser-resume-browser-v1.json'
INVENTORY = 'research/azores-2009-section-compile-inventory-v1.json'
MANIFEST = 'almanac/query-engine.manifest.json'
OUT = ROOT / '.pytest_cache/azores-2009-section-installation-v1'
PARENT_MANIFEST = 'e5ccd930ffeb1086821144fbe6c2ffcd3b94781750368b91465d7e83702daf34'
LOGICAL = '9d35ca1c8cebee0f48e49dd66bb83321b506fa43260f1dd5db4b1e06102293da'
FINAL_MANIFEST = 'dd85f3264d13539b3219b17c5dd30ab675494b46e53653b3c12fe6f3a3856546'
SOURCE = '14ff443664e3a3e329555c7cf41e00cfa7c522da'
BINARY = '2c25aad90ef489b9129d004b5efb5ff1309fd58ac08b33e7af16d897fe970ef5'


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
    from resume_azores_2009_section_browser_v1 import verify_saved_metadata
    meta = api(REPO + '/actions/artifacts/' + str(row['id']))
    original = REPO + f"/actions/runs/{row['run_id']}/attempts/{row['run_attempt']}"
    verify_saved_metadata(api(original), api(original + '/jobs')['jobs'], meta, read(FULL))
    browser_run=api(REPO + '/actions/runs/40595305912/attempts/1')
    assert browser_run['status']=='completed' and browser_run['conclusion']=='success'
    assert browser_run['head_sha']=='1ad8980034415c6805c7957a9a3148d1f573ebe2'
    path = OUT / filename
    with path.open('xb') as stream:
        subprocess.run(['gh', 'api', REPO + f"/actions/artifacts/{row['id']}/zip"], stdout=stream, check=True, timeout=600)
    assert path.stat().st_size == row['bytes'] and file_sha(path) == row['sha256']
    return path



def verify_request(request):
    expected = {'schema': 'osw.azores-2009-section-installation-request.v1',
        'execution_permitted': True, 'working_branch_installation_permitted': True,
        'cloud_git_object_transport_permitted': True, 'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}
    for key, value in expected.items():
        assert type(request.get(key)) is type(value) and request[key] == value, key
    for key in ['native_build_permitted', 'wasm_build_permitted', 'browser_automation_permitted',
                'scientific_source_processing_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        assert request.get(key) is False, key


def verify_results(full, execution, review, browser):
    assert full['status']=='PASS' and full['stage']=='engine_verified' and full['source_commit']==SOURCE
    assert execution['status']=='ENGINE_AND_SAVED_CANDIDATE_BROWSER_VERIFIED_VISUAL_REVIEW_PASS_NOT_INSTALLED'
    assert execution['engine_run']['id']==40591687892 and execution['engine_run']['overall_result']=='failure'
    assert execution['engine_run']['engine_phase_result']=='success'
    assert execution['browser_follow_up']['id']==40595305912 and execution['browser_follow_up']['overall_result']=='success'
    assert sum(full['rust_test_counts'].values())==42
    assert full['main_query_comparisons']==26 and full['source_query_comparisons']==12 and full['presentation_api_comparisons']==2
    assert full['logical_sha256']==execution['logical_sha256']==LOGICAL and full['logical_bytes']==190487048
    assert full['wasm_sha256']==execution['wasm_sha256']==BINARY
    assert execution['verification']['original_scientific_collections_changed']==0 and execution['new_measurements']==0
    assert review['status']=='PASS_ACTUAL_DESKTOP_MOBILE_IMAGES_INDIVIDUALLY_INSPECTED' and review['image_count']==15
    assert review['browser_run_id']==40595305912 and review['source_date_conflict_resolved'] is False
    assert browser['status']=='PASS' and browser['real_browser_executed'] is True
    assert not browser['page_errors'] and not browser['missing_assets'] and not browser['original_science_downloads']
    actual=[{k:r[k] for k in ['path','bytes','sha256']} for r in browser['screenshots']]
    reviewed=[{k:r[k] for k in ['path','bytes','sha256']} for r in review['images']]
    assert actual==reviewed and len(actual)==len({r['path'] for r in actual})==15
    assert all(r['individually_inspected'] is True for r in review['images'])
    assert all(r['geometry']['clipped_axes']==[] for r in browser['screenshots'])
    assert all(doc['working_branch_installed'] is False for doc in [full,execution,review])
    hashes=full['generated_sha256']
    assert len(hashes)==18 and hashes[MANIFEST]==FINAL_MANIFEST and hashes['almanac/query-engine.wasm']==BINARY
    assert sum(path.startswith('almanac/query-parts/') for path in hashes)==12
    assert all(not PurePosixPath(path).is_absolute() and '..' not in PurePosixPath(path).parts and '\\' not in path
               and re.fullmatch('[0-9a-f]{64}',digest) for path,digest in hashes.items())
    item=execution['saved_candidate_artifact']
    assert item['id']==12773519030 and item['bytes']==96189974
    assert item['sha256']=='ab4b1f97f4c9b8b26483382125e85981de82deb81d8aafd86500fd0ee0127515'
    return dict(hashes)


def verify_browser_result(result):
    assert result['status']=='PASS' and result['browser_verified'] is True
    assert result['engine_source_commit']==SOURCE
    assert result['browser_source_commit']=='1ad8980034415c6805c7957a9a3148d1f573ebe2'
    assert result['original_engine_run_id']==40591687892 and result['saved_candidate_artifact_id']==12773519030
    assert str(result['run_id'])=='40595305912' and str(result['run_attempt'])=='1'
    assert result['logical_sha256']==LOGICAL and result['wasm_sha256']==BINARY
    assert result['saved_candidate_files_verified']==18 and result['native_builds']==result['wasm_builds']==0
    assert result['new_physical_dimensions']==0 and result['working_branch_installed'] is False



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
    verify_browser_result(read('research/azores-2009-section-browser-resume-result-v1.json'))
    for name, count in [('main', 26), ('index', 12), ('snapshots', 2)]:
        parity = read('research/azores-2009-section-' + name + '-parity-v1.json')
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
    receipt = final['azores_2009_section_engine_delivery_v1']
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
    assert packet['logical_sha256'] == LOGICAL and packet['logical_byte_length'] == 190487048
    parts = packet['parts']
    assert len(parts) == 12 and sum(p['byte_length'] for p in parts) == 190487048
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
    item = dict(execution['saved_candidate_artifact'])
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
    proof = {'schema': 'osw.azores-2009-section-installed.v1', 'status': 'EXACT_REVIEWED_ARTIFACT_INSTALLED',
        'installation_transport': 'cloud_git_nonforce_single_ref_v1', 'installation_control_commit': source,
        'installation_run_id': os.environ['GITHUB_RUN_ID'], 'installation_run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'files': dict(files), 'logical_sha256': LOGICAL, 'logical_bytes': 190487048,
        'engine_manifest_sha256': FINAL_MANIFEST, 'wasm_sha256': BINARY, 'candidate_artifact': item,
        'visual_review_sha256': file_sha(ROOT / REVIEW),
        'engine_run_id':40591687892,'browser_run_id':40595305912,'browser_source_commit':'1ad8980034415c6805c7957a9a3148d1f573ebe2', 'coverage': read('research/current-measurement-coverage-checkpoint-v4.json')['counts'],
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
        print('Exact saved Azores section installation preflight passed')
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
