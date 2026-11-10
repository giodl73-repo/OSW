"""Cloud-only browser follow-up on the exact already-verified saved engine.

No native/WASM build, scientific processing, branch installation or local sync.
The original failed run's successful engine phase is preserved as evidence;
this run can establish browser behavior only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from install_south_java_reference_saved_v1 import extract_verified
import azores_2009_section_engine_v1 as engine

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/azores-2009-section-browser-resume-v1'
REQUEST = 'research/azores-2009-section-browser-resume-request-v1.json'
PREFLIGHT = 'research/azores-2009-section-browser-resume-preflight-v1.json'
ORIGINAL_PREFLIGHT = 'research/azores-2009-section-delivery-preflight-v1.json'
ORIGINAL_REQUEST = 'research/azores-2009-section-delivery-request-v1.json'
EVIDENCE = 'research/azores-2009-section-engine-evidence-v1.json'
WORKFLOW = '.github/workflows/azores-2009-section-browser-resume-v1.yml'
REPO = 'repos/giodl73-repo/OSW'
SOURCE = '14ff443664e3a3e329555c7cf41e00cfa7c522da'
RUN = 40591687892
ATTEMPT = 1
ARTIFACT = 12773519030
ARCHIVE_BYTES = 96189974
ARCHIVE_SHA = 'ab4b1f97f4c9b8b26483382125e85981de82deb81d8aafd86500fd0ee0127515'
LOGICAL = '9d35ca1c8cebee0f48e49dd66bb83321b506fa43260f1dd5db4b1e06102293da'
WASM = '2c25aad90ef489b9129d004b5efb5ff1309fd58ac08b33e7af16d897fe970ef5'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', REPO + '/' + path], timeout=55))


def controls(clean):
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'
            or os.environ.get('OSW_AZORES_SECTION_BROWSER_RESUME_V1') != '1'):
        raise ValueError('Exact cloud working-branch browser-resume push required')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One cloud CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS', 'RUST_TEST_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1':
            raise ValueError('One worker required: ' + key)
    request = read(REQUEST)
    if (request.get('schema') != 'osw.azores-2009-section-browser-resume-request.v1'
            or request.get('execute') is not True or request.get('workflow') != WORKFLOW
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0):
        raise ValueError('Browser-only request disabled or changed')
    for key in ['browser_permitted', 'cloud_candidate_restore_permitted']:
        if request.get(key) is not True:
            raise ValueError('Browser-resume phase not authorized: ' + key)
    for key in ['native_build_permitted', 'wasm_build_permitted', 'scientific_source_processing_permitted',
                'working_branch_installation_permitted', 'main_merge_permitted', 'local_bulk_sync_permitted']:
        if request.get(key) is not False:
            raise ValueError('Unrelated permission enabled: ' + key)
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']:
        raise ValueError('Changed frozen browser-resume preflight')
    preflight = read(PREFLIGHT)
    original = read(ORIGINAL_PREFLIGHT)
    for path, expected in {**original['input_sha256'], **preflight['input_sha256']}.items():
        if digest(ROOT / path) != expected:
            raise ValueError('Original engine source or observer changed: ' + path)
    for path in original['disabled_requests'] + [ORIGINAL_REQUEST]:
        item = read(path)
        if item.get('execute', item.get('execution_permitted')) is not False:
            raise ValueError('Another execution request is enabled: ' + path)
    phase = read('research/current-gap-delivery-phase.json')
    if phase.get('phase') != 'source-review-only-v1' or phase.get('heavy_work_permitted') is not False:
        raise ValueError('Global scientific processing must remain disabled')
    if clean:
        for path, expected in original['parent_file_sha256'].items():
            if digest(ROOT / path) != expected:
                raise ValueError('Installed parent changed before saved-candidate restore')
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != os.environ.get('GITHUB_SHA') or head != api('git/ref/heads/codex/current-measurement-gaps')['object']['sha']:
        raise ValueError('Exact current working-branch checkout required')
    if clean and subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean source checkout required')
    return head


def verify_saved_metadata(run, jobs, artifact, evidence):
    if (run.get('status') != 'completed' or run.get('conclusion') != 'failure'
            or run.get('head_sha') != SOURCE or run.get('run_attempt') != ATTEMPT
            or artifact.get('expired') is not False or artifact.get('id') != ARTIFACT
            or artifact.get('size_in_bytes') != ARCHIVE_BYTES
            or artifact.get('digest') != 'sha256:' + ARCHIVE_SHA
            or artifact.get('workflow_run', {}).get('id') != RUN
            or artifact['workflow_run'].get('head_sha') != SOURCE):
        raise ValueError('Exact terminal run and saved artifact required')
    matching = [job for job in jobs if job.get('name') == 'full-delivery']
    if len(matching) != 1:
        raise ValueError('Missing original full-delivery job')
    steps = {step['name']: step['conclusion'] for step in matching[0]['steps']}
    if (steps.get('Verify parent preservation and matching native/WASM queries and complete snapshots') != 'success'
            or steps.get('Verify direct atlas/query/card links and actual desktop/mobile rendering') != 'failure'):
        raise ValueError('Original successful engine phase and failed browser phase required')
    if (evidence.get('status') != 'PASS' or evidence.get('stage') != 'engine_verified'
            or evidence.get('source_commit') != SOURCE or evidence.get('logical_sha256') != LOGICAL
            or evidence.get('wasm_sha256') != WASM or evidence.get('main_query_comparisons') != 26
            or evidence.get('source_query_comparisons') != 12 or evidence.get('presentation_api_comparisons') != 2
            or sum(evidence.get('rust_test_counts', {}).values()) != 42
            or len(evidence.get('generated_sha256', {})) != 18):
        raise ValueError('Saved successful matching-engine evidence differs')


def verify_restored(evidence):
    for path, expected in evidence['generated_sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Saved candidate bytes changed: ' + path)
    manifest = read(engine.MANIFEST)
    if (manifest[engine.KEY]['source_commit'] != SOURCE
            or manifest[engine.KEY]['logical_sha256'] != LOGICAL
            or manifest[engine.KEY]['matching_binary_sha256'] != WASM):
        raise ValueError('Saved matching binary/data manifest differs')


def restore():
    head = controls(clean=True)
    if OUTPUT.exists():
        raise ValueError('Refuse to overwrite a prior browser resume')
    OUTPUT.mkdir(parents=True)
    evidence = read(EVIDENCE)
    attempt_path = 'actions/runs/' + str(RUN) + '/attempts/' + str(ATTEMPT)
    verify_saved_metadata(api(attempt_path), api(attempt_path + '/jobs')['jobs'],
                          api('actions/artifacts/' + str(ARTIFACT)), evidence)
    archive = OUTPUT / 'saved-candidate.zip'
    with archive.open('xb') as stream:
        subprocess.run(['gh', 'api', REPO + '/actions/artifacts/' + str(ARTIFACT) + '/zip'],
                       stdout=stream, check=True, timeout=600)
    if archive.stat().st_size != ARCHIVE_BYTES or digest(archive) != ARCHIVE_SHA:
        raise ValueError('Changed saved artifact archive')
    extract_verified(archive, evidence['generated_sha256'], ROOT)
    verify_restored(evidence)
    for path, expected in read(ORIGINAL_PREFLIGHT)['parent_file_sha256'].items():
        if path not in evidence['generated_sha256'] and digest(ROOT / path) != expected:
            raise ValueError('Restore changed an unrelated installed artifact')
    write(OUTPUT / 'restored.json', {'status': 'PASS', 'browser_source_commit': head,
        'engine_source_commit': SOURCE, 'saved_candidate_artifact_id': ARTIFACT,
        'saved_candidate_files_verified': 18, 'native_builds': 0, 'wasm_builds': 0,
        'logical_sha256': LOGICAL, 'wasm_sha256': WASM, 'working_branch_installed': False})


def browser():
    head = controls(clean=False)
    restored = read(OUTPUT / 'restored.json')
    if restored.get('status') != 'PASS' or restored.get('browser_source_commit') != head:
        raise ValueError('Exact saved-candidate restore required before browser')
    evidence = read(EVIDENCE)
    verify_restored(evidence)
    from check_azores_2009_section_browser_v2 import browser_review
    review = browser_review(ROOT, OUTPUT)
    write(OUTPUT / 'browser.json', review)
    verify_restored(evidence)
    write(OUTPUT / 'result.json', {'schema': 'osw.azores-2009-section-browser-resume-result.v1',
        'status': 'PASS', 'engine_source_commit': SOURCE, 'browser_source_commit': head,
        'original_engine_run_id': RUN, 'saved_candidate_artifact_id': ARTIFACT,
        'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'logical_sha256': LOGICAL, 'wasm_sha256': WASM,
        'saved_candidate_files_verified': 18, 'native_builds': 0, 'wasm_builds': 0,
        'browser_verified': True, 'visual_review_complete': False,
        'new_physical_dimensions': 0, 'working_branch_installed': False,
        'main_merged': False, 'full_goal_complete': False})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'restore', 'browser'])
    args = parser.parse_args()
    try:
        if args.action == 'preflight':
            controls(clean=True)
        elif args.action == 'restore':
            restore()
        else:
            browser()
    except Exception as error:
        if os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true':
            write(OUTPUT / (args.action + '-failure.json'), {'status': 'FAIL', 'stage': args.action,
                'source_commit': os.environ.get('GITHUB_SHA'), 'error': str(error)[:4000], 'installed': False})
        raise
