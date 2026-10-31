"""Install the exact saved, visually reviewed South Java cohort in one cloud job."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

import check_south_java_compiled_browser_v1 as restored
import check_south_java_catalog_engine_cloud_v1 as build
import check_south_java_model_browser_v1 as browser
import check_south_java_model_layer_cloud_v1 as native
from south_java_model_browser_custody_v1 import digest, members

ROOT = native.ROOT
REQUEST = 'research/south-java-model-installation-request-v1.json'
PREFLIGHT = 'research/south-java-model-installation-preflight-v1.json'
VISUAL = 'research/south-java-compiled-browser-visual-review-v1.json'
FUNCTIONAL = 'research/south-java-compiled-browser-result-v1.json'
PROOF = 'research/south-java-model-installed-v1.json'
OUTPUT = ROOT / '.pytest_cache/south-java-model-installation-v1'
BRANCH = 'codex/current-measurement-gaps'
WORKFLOW = '.github/workflows/install-south-java-model-v1.yml'
GIT = ['git', '-c', 'core.fsmonitor=false', '-c', 'maintenance.auto=0', '-c', 'gc.auto=0']
CASES = [(40150485982, 2, 121041034782, '4bc5025098656048e2def466448ab884888afe58'),
         (40154798060, 2, 121053851834, '3d6ba5188056099acff918e5262d8ad52a59e29a'),
         (40156327229, 1, 121058425650, '713c6234c6052bb55c46c87ac83def81b892734d')]


def read(path): return json.loads((ROOT / path).read_bytes())
def encode(value): return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
def git(*args): return subprocess.check_output([*GIT, *args], cwd=ROOT).decode().strip()


def verify_request(request):
    fixed = {'schema': 'osw.south-java-model-installation-request.v1',
             'execution_permitted': True, 'working_branch_installation_permitted': True,
             'installation_workflow': WORKFLOW, 'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}
    for key, expected in fixed.items():
        if type(request.get(key)) is not type(expected) or request[key] != expected:
            raise ValueError('Disabled or changed exact installation request: ' + key)
    for key in ['native_build_permitted', 'wasm_build_permitted', 'browser_automation_permitted',
                'scientific_source_processing_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False: raise ValueError('Forbidden installation permission: ' + key)


def verify_case(run, jobs, identity):
    rid, attempt, jid, source = identity
    if (run.get('id') != rid or run.get('run_attempt') != attempt or run.get('head_sha') != source
            or run.get('status') != 'completed' or run.get('conclusion') != 'success'):
        raise ValueError('Changed successful source run/attempt identity')
    found = [row for row in jobs.get('jobs', []) if row.get('id') == jid]
    if (len(found) != 1 or found[0].get('run_id') != rid or found[0].get('run_attempt') != attempt
            or found[0].get('head_sha') != source or found[0].get('status') != 'completed'
            or found[0].get('conclusion') != 'success'):
        raise ValueError('Changed successful source job identity')


def verify_visual(review, functional_raw, screenshots):
    result = json.loads(functional_raw)
    expected = {'status': 'APPROVED_EXACT_WORKING_BRANCH_DATA_INSTALLATION',
                'run_id': CASES[2][0], 'run_attempt': CASES[2][1], 'job_id': CASES[2][2],
                'source_commit': CASES[2][3], 'visual_review_complete': True,
                'actual_screenshots_inspected': 10, 'scientific_release_approved': False,
                'main_merge_approved': False, 'generated_artifact_id': 12582509417,
                'compiled_engine_artifact_id': 12583798914}
    if any(type(review.get(k)) is not type(v) or review[k] != v for k, v in expected.items()):
        raise ValueError('Exact completed visual installation review required')
    if (hashlib.sha256(functional_raw).hexdigest() != review['functional_result_sha256']
            or result.get('status') != 'PASS' or result.get('browser_verified') is not True
            or str(result.get('run_id')) != str(CASES[2][0]) or str(result.get('run_attempt')) != '1'
            or result.get('source_commit') != CASES[2][3]):
        raise ValueError('Final functional result differs from visual review')
    rows = review['screenshots']
    names = [row['path'] for row in rows]
    if (len(rows) != 10 or len(set(names)) != 10 or set(names) != set(screenshots)
            or rows != result['screenshots']):
        raise ValueError('Exact ten reviewed final screenshots required')
    for row in rows:
        raw = screenshots[row['path']]
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Reviewed screenshot bytes changed')
    custody = result['custody']
    if (review['logical_sha256'] != custody['logical_sha256']
            or review['wasm_sha256'] != custody['active_wasm_sha256']
            or review['engine_manifest_sha256'] != custody['compiled_engine_overlay']['compiled_manifest_sha256']):
        raise ValueError('Visual approval payload identity differs')
    return result


def generated_paths(result):
    paths = set(result['artifact_paths']) | {'almanac/query-engine.wasm'}
    fixed = {'almanac/query-data.json', 'almanac/query-engine.wasm', build.MANIFEST,
             'almanac/index-catalog.json', 'almanac/index-sources.json', 'almanac/index-data.json.gz',
             'research/ocean-motion-dashboard.json'}
    parts = paths - fixed
    import re
    if len(paths) != 19 or len(parts) != 12 or not fixed <= paths or any(
            re.fullmatch(r'almanac/query-parts/\d{6}-[0-9a-f]{64}\.bin', path) is None for path in parts):
        raise ValueError('Only exact nineteen saved generated paths may be published')
    return paths


def verify_changed(actual, allowed):
    # Existing content-addressed parts may already be identical; no unrelated change is allowed.
    if not {REQUEST, PROOF, 'almanac/query-data.json', build.MANIFEST, 'almanac/query-engine.wasm'} <= set(actual):
        raise ValueError('Required installation files are missing')
    if not set(actual) <= set(allowed): raise ValueError('Unrelated installation file change')


def controls(env):
    native.cloud_environment(env)  # Local refusal before even reading the request or packet.
    if env.get('GITHUB_EVENT_NAME') != 'push': raise ValueError('Exact working-branch push required')
    head = git('rev-parse', 'HEAD')
    if head != env.get('GITHUB_SHA') or git('status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Clean exact source checkout required')
    request = read(REQUEST); verify_request(request)
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']: raise ValueError('Changed installation preflight')
    for path, expected in read(PREFLIGHT)['input_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed installer source: ' + path)
    for path, count in [*build.FREEZES, (build.PREFLIGHT, 21), (restored.PREFLIGHT, 24)]:
        pins = read(path)['input_sha256']
        if len(pins) != count: raise ValueError('Changed preserved source inventory')
        for name, expected in pins.items():
            if digest(ROOT / name) != expected: raise ValueError('Changed preserved input: ' + name)
    for path in [native.REQUEST, 'research/south-java-saved-wasm-request-v1.json',
                 'research/south-java-model-delivery-request-v1.json', browser.REQUEST, build.REQUEST,
                 restored.REQUEST, 'research/current-local-extent-query-check-request-v2.json',
                 'research/current-local-extent-ui-request-v1.json']:
        if read(path)['execution_permitted'] is not False: raise ValueError('Earlier request must be disabled: ' + path)
    phase = read('research/current-gap-delivery-phase.json')
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain')
    inventory = read(build.INVENTORY)
    for path, expected in inventory['rust_source_sha256'].items():
        if digest(ROOT / path) != expected: raise ValueError('Changed compiled runtime: ' + path)
    packet = read('almanac/query-data.json')
    if packet['logical_sha256'] != native.PARENT_SHA or packet['logical_byte_length'] != native.PARENT_BYTES:
        raise ValueError('Original installed parent dataset required')
    if (ROOT / PROOF).exists(): raise ValueError('Do not overwrite installed proof')
    return head, request, inventory


def remote_guard(source):
    actual = browser.api('git/ref/heads/' + BRANCH)['object']['sha']
    if actual != source: raise ValueError('Working branch moved; installation refused')


def visual_archive():
    review = read(VISUAL)
    artifact = browser.api('actions/artifacts/' + str(review['evidence_artifact_id']))
    if (artifact['expired'] or artifact['workflow_run']['id'] != CASES[2][0]
            or artifact['digest'] != 'sha256:' + review['evidence_artifact_sha256']
            or artifact['size_in_bytes'] != 1015377):
        raise ValueError('Final browser archive metadata differs')
    archive = OUTPUT / 'browser-evidence.zip'
    with archive.open('xb') as stream:
        subprocess.run(['gh', 'api', 'repos/giodl73-repo/OSW/actions/artifacts/' + str(artifact['id']) + '/zip'],
                       stdout=stream, check=True, timeout=300)
    if archive.stat().st_size != artifact['size_in_bytes'] or digest(archive) != review['evidence_artifact_sha256']:
        raise ValueError('Full final browser ZIP differs')
    expected = ['result.json', 'custody.json'] + [row['path'] for row in review['screenshots']]
    with zipfile.ZipFile(archive) as saved:
        members(saved.infolist(), expected)
        raw = saved.read('result.json')
        if raw != (ROOT / FUNCTIONAL).read_bytes(): raise ValueError('Saved browser result differs')
        verify_visual(review, raw, {row['path']: saved.read(row['path']) for row in review['screenshots']})
    return review


def file_identity(path):
    target = ROOT / path
    if target.is_symlink() or not target.resolve().is_relative_to(ROOT): raise ValueError('Unsafe publication path')
    return {'sha256': digest(target), 'bytes': target.stat().st_size, 'git_blob_oid': git('hash-object', '--no-filters', path)}


def remote_files(commit, paths):
    fields = [f'p{i}:object(expression:{json.dumps(commit + ":" + path)})'
              '{__typename ... on Blob{oid byteSize}}' for i, path in enumerate(paths)]
    query = 'query{repository(owner:"giodl73-repo",name:"OSW"){' + ' '.join(fields) + '}}'
    raw = subprocess.check_output(['gh', 'api', 'graphql', '--input', '-'],
                                  input=json.dumps({'query': query}).encode())
    if len(raw) > 65536: raise ValueError('Unexpected remote verification response size')
    result = json.loads(raw)
    if result.get('errors'): raise ValueError('Remote installed file verification failed')
    return {path: result['data']['repository']['p' + str(i)] for i, path in enumerate(paths)}


def install(source, request, inventory):
    remote_guard(source)
    main = browser.api('git/ref/heads/main')['object']['sha']
    for rid, attempt, jid, sha in CASES:
        verify_case(browser.api('actions/runs/' + str(rid) + '/attempts/' + str(attempt)),
                    browser.api('actions/runs/' + str(rid) + '/attempts/' + str(attempt) + '/jobs'),
                    (rid, attempt, jid, sha))
    review = visual_archive()
    paths = generated_paths(read(browser.RESULT))
    restored.OUTPUT.mkdir(parents=True, exist_ok=False)
    custody = restored.apply_engine(inventory)  # Reuses exact two-artifact restoration and recomputed manifest overlay.
    if (custody['logical_sha256'] != review['logical_sha256']
            or custody['active_wasm_sha256'] != review['wasm_sha256']
            or digest(ROOT / build.MANIFEST) != review['engine_manifest_sha256']):
        raise ValueError('Restored candidate differs from approved visual review')
    files = {path: file_identity(path) for path in sorted(paths)}
    proof = {'schema': 'osw.south-java-model-installed.v1', 'status': 'EXACT_REVIEWED_ARTIFACTS_INSTALLED',
             'installation_control_commit': source, 'installation_run_id': os.environ['GITHUB_RUN_ID'],
             'installation_run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
             'parent_logical_sha256': native.PARENT_SHA, 'logical_sha256': review['logical_sha256'],
             'source_cases': [{'run_id': r, 'attempt': a, 'job_id': j, 'source_commit': s} for r, a, j, s in CASES],
             'functional_result_sha256': digest(ROOT / FUNCTIONAL), 'visual_review_sha256': digest(ROOT / VISUAL),
             'generated_artifact_id': review['generated_artifact_id'],
             'compiled_engine_artifact_id': review['compiled_engine_artifact_id'],
             'custody': custody, 'files': files, 'named_currents': 106, 'scoped_width_records': 172,
             'new_context_records': 5, 'new_provenance_entries': 2, 'new_physical_dimensions_admitted': 0,
             'browser_verified': True, 'visual_review_complete': True, 'scientific_release_approved': False,
             'main_merged': False,
             'installed_commit_location': 'Cloud installation artifact result.json binds this proof blob to the actual commit; no self-referential commit hash.'}
    (ROOT / PROOF).write_bytes(encode(proof))
    request['execution_permitted'] = False
    request['working_branch_installation_permitted'] = False
    (ROOT / REQUEST).write_bytes(encode(request))
    allowed = paths | {PROOF, REQUEST}
    # Include untracked new parts explicitly; never use git add -A on the workspace.
    git('add', '--', *sorted(allowed))
    changed = git('diff', '--cached', '--name-only').splitlines()
    verify_changed(changed, allowed)
    for path, row in files.items():
        if git('rev-parse', ':' + path) != row['git_blob_oid']:
            raise ValueError('Git filters changed saved publication bytes: ' + path)
    if git('diff', '--name-only'): raise ValueError('Unstaged tracked changes')
    remote_guard(source)
    git('-c', 'core.hooksPath=/dev/null', '-c', 'user.name=OSW data delivery',
        '-c', 'user.email=actions@users.noreply.github.com', 'commit', '-m',
        'Install reviewed South Java model context and matching saved query engine')
    installed = git('rev-parse', 'HEAD')
    if git('rev-parse', 'HEAD^') != source: raise ValueError('Unexpected installed commit parent')
    remote_guard(source)
    git('push', 'origin', 'HEAD:refs/heads/' + BRANCH)
    remote_guard(installed)
    commit = browser.api('git/commits/' + installed)
    if [p['sha'] for p in commit['parents']] != [source]: raise ValueError('Remote installed parent differs')
    installed_files = {**files, PROOF: file_identity(PROOF), REQUEST: file_identity(REQUEST)}
    objects = remote_files(installed, list(installed_files))
    for path, row in installed_files.items():
        actual = objects.get(path) or {}
        if actual.get('oid') != row['git_blob_oid'] or actual.get('byteSize') != row['bytes'] or actual.get('__typename') != 'Blob':
            raise ValueError('Remote installed bytes differ: ' + path)
    if browser.api('git/ref/heads/main')['object']['sha'] != main: raise ValueError('Main changed during installation')
    receipt = {'schema': 'osw.south-java-model-installation-result.v1', 'status': 'PASS',
               'installed_commit': installed, 'control_commit': source, 'remote_verified_files': installed_files,
               'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
               'logical_sha256': review['logical_sha256'], 'working_branch_installed': True,
               'request_disabled_in_installed_commit': True, 'main_unchanged': True,
               'local_preview_synchronized': False, 'new_physical_dimensions_admitted': 0, 'full_goal_complete': False}
    (OUTPUT / 'result.json').write_bytes(encode(receipt))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-install', action='store_true')
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    if not args.cloud_install: parser.error('Explicit cloud installation required; no file read or mutation')
    source, request, inventory = controls(dict(os.environ))
    remote_guard(source)
    if args.preflight_only: print('Exact saved installation source preflight passed'); return
    OUTPUT.mkdir(parents=True, exist_ok=False)
    try:
        install(source, request, inventory)
    except Exception as error:
        (OUTPUT / 'failure.json').write_bytes(encode({'status': 'FAIL', 'control_commit': source,
              'error': (type(error).__name__ + ': ' + str(error))[:1500],
              'instruction': 'Inspect authoritative branch and request before retry; a push may already have succeeded.'}))
        raise


if __name__ == '__main__': main()
