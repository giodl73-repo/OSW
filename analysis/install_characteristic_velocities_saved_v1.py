"""Install exact reviewed tropical Atlantic characteristic velocity artifacts in one guarded cloud job.

No science processing, native/WASM build, browser work or local bulk sync.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import zipfile

import characteristic_velocities_installation_contract_v1 as contract
import verified_artifact_git_transport_v1 as transport

ROOT = Path(__file__).resolve().parents[1]
BRANCH = 'codex/current-measurement-gaps'
REPO = 'repos/giodl73-repo/OSW'
REQUEST = 'research/richardson-walsh-1986-characteristic-velocity-installation-request-v1.json'
PREFLIGHT = 'research/richardson-walsh-1986-characteristic-velocity-installation-preflight-v1.json'
WORKFLOW = '.github/workflows/install-richardson-walsh-1986-characteristic-velocity-saved-v1.yml'
PROOF = 'research/richardson-walsh-1986-characteristic-velocity-installed-v1.json'
SAVED = 'research/richardson-walsh-1986-characteristic-velocity-installation-saved-engine-manifest-v1.json'
ENGINE = 'research/richardson-walsh-1986-characteristic-velocity-delivery-run-v2/'
BROWSER = 'research/richardson-walsh-1986-characteristic-velocity-browser-run-v2/'
VISUAL = 'research/richardson-walsh-1986-characteristic-velocity-browser-visual-review-v2.json'
EXECUTION = 'research/richardson-walsh-1986-characteristic-velocity-complete-execution-review-v1.json'
OUT = ROOT / '.pytest_cache/richardson-walsh-1986-characteristic-velocity-installation-v1'
require = contract.require


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], timeout=55))


def head(branch):
    line = transport.git('ls-remote', 'origin', 'refs/heads/' + branch)
    fields = line.split()
    require(len(fields) == 2 and fields[1] == 'refs/heads/' + branch, 'Missing remote branch')
    return fields[0]


def verify_request(request):
    expected = {'schema': 'osw.characteristic-velocities-installation-request.v1',
                'workflow': WORKFLOW, 'execution_permitted': True,
                'working_branch_installation_permitted': True,
                'cloud_git_object_transport_permitted': True,
                'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}
    for key, value in expected.items():
        require(type(request.get(key)) is type(value) and request[key] == value, 'Invalid request: ' + key)
    for key in ('native_build_permitted', 'wasm_build_permitted', 'browser_automation_permitted',
                'scientific_source_processing_permitted', 'source_field_processing_permitted',
                'local_bulk_sync_permitted', 'main_merge_permitted'):
        require(request.get(key) is False, 'Forbidden permission: ' + key)


def evidence():
    final_raw = (ROOT / (ENGINE + 'engine-manifest.json')).read_bytes()
    require(sha(final_raw) == contract.FINAL_MANIFEST, 'Reviewed manifest bytes differ')
    files = contract.verify_evidence(read(ENGINE + 'result.json'),
        {k: read(ENGINE + 'compare-' + k + '.json') for k in ('main', 'index')},
        read(BROWSER + 'result.json'), read(BROWSER + 'browser.json'), read(VISUAL),
        json.loads(final_raw), len(final_raw))
    execution = read(EXECUTION)
    require(execution['status'] == 'PASS_ENGINE_SOURCE_INDEX_BROWSER_AND_INDIVIDUAL_VISUAL_REVIEW_INSTALLATION_PENDING', 'Execution review missing')
    require(execution['visual_review_sha256'] == file_sha(ROOT / VISUAL), 'Visual review differs')
    for path, pin in execution['retained_evidence_sha256'].items():
        require(file_sha(ROOT / path) == pin, 'Retained evidence differs: ' + path)
    return files, final_raw


def controls():
    # Refuse before reading installed artifacts or making network requests.
    require(os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true'
            and os.environ.get('RUNNER_OS') == 'Linux'
            and os.environ.get('OSW_CHARACTERISTIC_VELOCITIES_INSTALL_V1') == '1', 'Cloud-only installation')
    require(os.environ.get('GITHUB_EVENT_NAME') == 'push'
            and os.environ.get('GITHUB_REPOSITORY') == 'giodl73-repo/OSW'
            and os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH, 'Wrong event or ref')
    require(len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15, 'One low-priority CPU required')
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        require(os.environ.get(key) == '1', 'Worker limit required')
    source = os.environ['GITHUB_SHA']
    require(transport.git('rev-parse', 'HEAD') == head(BRANCH) == source, 'Parent moved')
    require(head('main') == contract.MAIN and not transport.git('status', '--porcelain'), 'Main changed or checkout dirty')
    request = read(REQUEST)
    verify_request(request)
    require(file_sha(ROOT / PREFLIGHT) == request['preflight_sha256'], 'Preflight differs')
    preflight = read(PREFLIGHT)
    for path, pin in preflight['input_sha256'].items():
        require(file_sha(ROOT / path) == pin, 'Source differs: ' + path)
    for path, row in preflight['parent_files'].items():
        require((ROOT / path).stat().st_size == row['bytes'] and file_sha(ROOT / path) == row['sha256'], 'Installed parent differs: ' + path)
    for path in preflight['disabled_requests']:
        value = read(path)
        require(value.get('execute', value.get('execution_permitted')) is False, 'Another request enabled: ' + path)
    phase = read('research/current-gap-delivery-phase.json')
    require(phase['heavy_work_permitted'] is False and phase['max_heavy_local_jobs'] == 0
            and phase['max_heavy_cloud_jobs'] == 1, 'Broad phase must remain disabled')
    require(not (ROOT / PROOF).exists() and not (ROOT / SAVED).exists(), 'Already installed')
    files, final_raw = evidence()
    return source, request, preflight, files, final_raw


def verify_artifacts():
    for run, attempt, source in ((contract.ENGINE_RUN, 1, contract.ENGINE_SOURCE),
                                 (contract.BROWSER_RUN, 1, contract.BROWSER_SOURCE)):
        value = api(REPO + f'/actions/runs/{run}/attempts/{attempt}')
        require(value['status'] == 'completed' and value['conclusion'] == 'success'
                and value['head_sha'] == source, 'Verified run custody differs')
    for desc, run, source in ((contract.ENGINE_ARTIFACT, contract.ENGINE_RUN, contract.ENGINE_SOURCE),
                              (contract.BROWSER_ARTIFACT, contract.BROWSER_RUN, contract.BROWSER_SOURCE)):
        value = api(REPO + '/actions/artifacts/' + str(desc['id']))
        require(value['workflow_run']['id'] == run and value['workflow_run']['head_sha'] == source
                and value['expired'] is False and value['size_in_bytes'] == desc['bytes']
                and value['digest'] == 'sha256:' + desc['sha256'], 'Artifact custody differs')


def extract_exact(archive, target, files):
    """Reject unlisted, duplicate, unsafe, oversized or changed archive members."""
    require(not target.exists(), 'Extraction target already exists')
    with zipfile.ZipFile(archive) as saved:
        rows = saved.infolist()
        require(len(rows) == len(files) and {r.filename for r in rows} == set(files), 'Archive members differ')
        require(sum(r.file_size for r in rows) < 512 * 1024 * 1024, 'Archive exceeds bound')
        for row in rows:
            path = PurePosixPath(row.filename)
            mode = row.external_attr >> 16
            require(not path.is_absolute() and '..' not in path.parts and '\\' not in row.filename
                    and str(path) == row.filename and not row.is_dir()
                    and stat.S_IFMT(mode) in (0, stat.S_IFREG), 'Unsafe archive path or type')
            require(row.file_size == files[row.filename]['bytes'] and row.file_size < 100 * 1024 * 1024, 'Wrong member size')
        for row in rows:
            destination = target / row.filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            with saved.open(row) as stream, destination.open('xb') as output:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    output.write(block)
            require(file_sha(destination) == files[row.filename]['sha256'], 'Wrong member hash')


def verify_packet(target, files, final):
    for path, row in files.items():
        require((target / path).stat().st_size == row['bytes'] and file_sha(target / path) == row['sha256'], 'Final artifact differs: ' + path)
    # The cumulative ledger also retains historical control/source hashes.
    # Check the actual compiled dependency closure and all runtime UI assets.
    inventory = read(ENGINE + 'compile-inventory.json')
    for group, count in (('rust_source_sha256', 117), ('compile_time_data_sha256', 171)):
        require(len(inventory[group]) == count, 'Compiled inventory differs')
        for path, pin in inventory[group].items():
            require(final['sha256'][path] == pin and file_sha((target if path in files else ROOT) / path) == pin,
                    'Compiled input differs: ' + path)
    dependencies = read(ENGINE + 'dependency-proof.json')['production_dependencies']
    require(len(dependencies) == 280, 'Production dependency closure differs')
    active = set(dependencies) | {p for p in final['sha256']
        if p.startswith('almanac/') and Path(p).suffix in ('.js', '.css', '.html')}
    for path in active:
        require(file_sha((target if path in files else ROOT) / path) == final['sha256'][path], 'Active manifest input differs: ' + path)
    phase_path = 'research/current-gap-delivery-phase.json'
    operational = final['indian_sec_regional_model_lengths_engine_v1']['delivery_source_provenance_v2']['operational_inputs'][phase_path]
    require(final['sha256'][phase_path] == operational['parent_sha256']
            and file_sha(ROOT / phase_path) == operational['current_sha256'], 'Operational provenance differs')
    catalog = json.loads((target / 'almanac/index-catalog.json').read_bytes())
    require(catalog['source_count'] == 668 and catalog['bundle_sha256'] == read(ENGINE + 'compare-index.json')['payload_sha256'], 'Indexed source metadata differs')
    descriptor = json.loads((target / 'almanac/query-data.json').read_bytes())
    require(descriptor['logical_sha256'] == contract.LOGICAL
            and descriptor['logical_byte_length'] == contract.LOGICAL_BYTES, 'Logical descriptor differs')
    parts = descriptor['parts']
    require(len(parts) == 12 and [r['index'] for r in parts] == list(range(12)), 'Part inventory differs')
    require({'almanac/' + r['path'] for r in parts} == {p for p in files if p.startswith('almanac/query-parts/')}, 'Part paths differ')
    logical = hashlib.sha256()
    total = 0
    for row in parts:
        path = target / 'almanac' / row['path']
        require(path.stat().st_size == row['byte_length'] and file_sha(path) == row['sha256'], 'Part metadata differs')
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                logical.update(block)
                total += len(block)
    require(total == contract.LOGICAL_BYTES and logical.hexdigest() == contract.LOGICAL, 'Complete logical bytes differ')


def leaves(commit):
    result = {}
    for line in transport.git('ls-tree', '-r', '--long', '-z', commit).split('\0'):
        if not line:
            continue
        metadata, path = line.split('\t', 1)
        mode, kind, oid, size = metadata.split()
        result[path] = {'mode': mode, 'type': kind, 'sha': oid, 'bytes': None if size == '-' else int(size)}
    return result


def install():
    source, request, preflight, files, final_raw = controls()
    verify_artifacts()
    OUT.mkdir(parents=True, exist_ok=False)
    archive = OUT / 'engine.zip'
    with archive.open('xb') as output:
        subprocess.run(['gh', 'api', REPO + f"/actions/artifacts/{contract.ENGINE_ARTIFACT['id']}/zip"], stdout=output, check=True, timeout=600)
    require(archive.stat().st_size == contract.ENGINE_ARTIFACT['bytes']
            and file_sha(archive) == contract.ENGINE_ARTIFACT['sha256'], 'Archive bytes differ')
    target = OUT / 'unpacked'
    original_files = read(ENGINE + 'result.json')['generated_files']
    extract_exact(archive, target, original_files)
    (target / 'almanac/query-engine.manifest.json').write_bytes(final_raw)
    verify_packet(target, files, json.loads(final_raw))
    before = leaves(source)
    entries, installed = [], {}

    def add(path, raw):
        oid = transport.store(raw)
        expected = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(oid == expected, 'Git blob identity differs')
        entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': oid})
        installed[path] = {'sha256': sha(raw), 'bytes': len(raw), 'git_blob_oid': oid}

    for path in files:
        add(path, (target / path).read_bytes())
    add(SAVED, final_raw)
    proof = {'schema': 'osw.richardson-walsh-1986-characteristic-velocity-installed.v1', 'status': 'VERIFIED_ARTIFACTS_READY_FOR_ATOMIC_WORKING_BRANCH_INSTALLATION',
        'installation_control_commit': source, 'engine_source': contract.ENGINE_SOURCE,
        'engine_run': contract.ENGINE_RUN, 'engine_artifact': contract.ENGINE_ARTIFACT,
        'browser_source': contract.BROWSER_SOURCE, 'browser_run': contract.BROWSER_RUN,
        'browser_artifact': contract.BROWSER_ARTIFACT, 'logical_sha256': contract.LOGICAL,
        'wasm_sha256': contract.BINARY, 'manifest_sha256': contract.FINAL_MANIFEST,
        'files': dict(installed), 'query_contract_file': contract.QUERY_CONTRACT,
        'source_index_documents': 668, 'publication_source_collection_rows': 228,
        'scoped_width_records': 187, 'owners_with_scoped_width_capability': 92,
        'widths_added': 0, 'characteristic_velocity_records_added': 10,
        'characteristic_velocity_records': 10, 'owners_with_characteristic_velocity': 8, 'publication_sources_added': 1, 'reported_whole_current_lengths_added': 0,
        'width_samples_added': 0, 'annual_ranges_added': 0, 'physical_state_joins_added': 0,
        'independent_observations_added': 0, 'native_or_wasm_rebuild': False,
        'main_updated': False, 'local_bulk_sync': False, 'full_goal_complete': False}
    add(PROOF, encode(proof))
    disabled = dict(request, execution_permitted=False, working_branch_installation_permitted=False, cloud_git_object_transport_permitted=False, completed_by_run=os.environ['GITHUB_RUN_ID'],
                    completed_by_attempt=os.environ['GITHUB_RUN_ATTEMPT'])
    add(REQUEST, encode(disabled))
    require(len(entries) == 21, 'Installation scope differs')
    candidate = transport.candidate(source, entries, str(OUT / 'git-index'))
    after = leaves(candidate)
    selected = set(installed)
    require(set(after) == set(before) | selected, 'Tree paths changed unexpectedly')
    for path, row in before.items():
        if path not in selected:
            require(after[path] == row, 'Protected tree changed: ' + path)
    for path, row in installed.items():
        require(after[path] == {'mode': '100644', 'type': 'blob', 'sha': row['git_blob_oid'], 'bytes': row['bytes']}, 'Candidate file differs')
    require(head(BRANCH) == source and head('main') == contract.MAIN, 'Remote parent moved')
    transport.publish(candidate, BRANCH)
    require(head(BRANCH) == candidate and head('main') == contract.MAIN, 'Published ref differs')
    result = dict(proof, status='PASS_INSTALLED_REVIEWED_WORKING_BRANCH_ARTIFACTS',
                  installed_commit=candidate, files=installed,
                  protected_paths_preserved=len(set(before) - selected), installed=True,
                  request_disabled=True, main_unchanged=True)
    (OUT / 'result.json').write_bytes(encode(result))
    print(json.dumps({k: result[k] for k in ('status', 'installed_commit', 'main_unchanged', 'full_goal_complete')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-install', action='store_true', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    try:
        if args.preflight_only:
            controls()
            verify_artifacts()
            print('PASS_EXACT_PARENT_EVIDENCE_AND_CUSTODY_PREFLIGHT')
        else:
            install()
    except Exception as error:
        # Keep failure evidence compact. Never print packet/index/source payloads.
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            OUT.mkdir(parents=True, exist_ok=True)
            (OUT / 'failure.json').write_bytes(encode({'status': 'FAIL', 'error_type': type(error).__name__,
                'message': str(error)[:1200], 'installed': False, 'main_updated': False}))
        raise
