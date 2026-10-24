"""Cloud-only installation of one validated saved coastal context cohort."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import indian_coastal_card_presentation_v1 as presentation
import indian_coastal_delivery_receipts_v1 as delivery
import verify_indian_coastal_installation_v1 as verification

ROOT = Path(__file__).resolve().parents[1]
PROOF = 'research/indian-coastal-context-installed-delivery-v1.json'
COVERAGE = 'research/current-coverage-catalogue-snapshot-v1.json'
REQUEST = 'research/indian-coastal-context-installation-request-v1.json'
REVIEW = 'research/indian-coastal-context-card-visual-review-v2.json'
PHASE = 'research/current-gap-delivery-phase.json'
WORKFLOW = '.github/workflows/install-indian-coastal-context-v1.yml'
GENERATED = {PROOF, COVERAGE, PHASE, 'almanac/query-data.json', 'almanac/query-engine.wasm',
             'almanac/query-engine.manifest.json', 'almanac/index-catalog.json',
             'almanac/index-sources.json', 'almanac/index-data.json.gz', 'research/ocean-motion-dashboard.json'}
CONTROL_PATHS = {'.gitattributes', PHASE, REQUEST, REVIEW, WORKFLOW, presentation.UI,
    '.github/workflows/baffin-bound-candidate.yml', '.github/workflows/davidson-width-candidate.yml',
    '.github/workflows/indian-coastal-card-presentation-v1.yml',
    'rust/osw-query/src/indian_coastal_context.rs',
    'analysis/test_indian_coastal_context_browser.py',
    'analysis/indian_coastal_delivery_receipts_v1.py', 'analysis/test_indian_coastal_delivery_receipts_v1.py',
    'analysis/indian_coastal_card_presentation_v1.py', 'analysis/test_indian_coastal_card_presentation_v1.py',
    'analysis/check_indian_coastal_card_presentation_v1.py',
    'analysis/verify_indian_coastal_installation_v1.py', 'analysis/test_verify_indian_coastal_installation_v1.py',
    'analysis/install_indian_coastal_context_v1.py', 'analysis/test_install_indian_coastal_context_v1.py',
    'plans/indian-coastal-card-presentation-v1.md',
    'plans/indian-coastal-context-installation-v1.md',
    'signals/roles/check/indian-coastal-card-presentation-v1-roles-check-2026-10-24.md',
    'signals/roles/check/indian-coastal-context-installation-v1-roles-check-2026-10-24.md',
    'research/indian-coastal-context-candidate-export-execution-review-v1.json',
    'research/indian-coastal-context-full-validation-review-v1.json',
    'research/indian-coastal-context-card-visual-review-v1.json',
    'research/source-data/shetye-wicc-1991/author-copy-access-attempt-v1.json',
    'research/wicc-shetye-1991-author-copy-access-review-v1.json',
    'research/eacc-width-primary-source-followup-v1.json',
    'plans/eacc-regional-model-core-width-method-draft-v1.md'}
GIT = ['git', '-c', 'core.fsmonitor=false', '-c', 'maintenance.auto=0', '-c', 'gc.auto=0']


def sha(path):
    import hashlib
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):result.update(chunk)
    return result.hexdigest()


def verify_control_delta(compare, control):
    commits = compare.get('commits', [])
    files = compare.get('files', [])
    names = [row.get('filename') for row in files]
    if (compare.get('status') != 'ahead' or compare.get('base_commit', {}).get('sha') != delivery.SOURCE_COMMIT
            or compare.get('merge_base_commit', {}).get('sha') != delivery.SOURCE_COMMIT
            or not commits or commits[-1].get('sha') != control or compare.get('total_commits') != len(commits)
            or len(files) >= 300 or len(names) != len(set(names)) or not set(names) <= CONTROL_PATHS
            or any(row.get('status') not in ['added', 'modified'] for row in files)):
        raise ValueError('Only declared source-control additions/changes may intervene before installation')


def verify_request(request):
    fixed = {'schema': 'osw.indian-coastal-context.installation-request.v1',
             'source_run_id': delivery.SOURCE_RUN, 'source_commit': delivery.SOURCE_COMMIT,
             'packet_logical_sha256': delivery.PACKET, 'installation_workflow': WORKFLOW,
             'visual_review_file': REVIEW, 'native_rebuild': False, 'wasm_rebuild': False,
             'scientific_source_recomputation': False, 'main_merged': False, 'scientific_release_published': False}
    hashes = ['presentation_receipt_sha256', 'visual_review_sha256']
    if (any(request.get(key) != value for key, value in fixed.items())
            or type(request.get('presentation_run_id')) is not int or request['presentation_run_id'] <= 0
            or not isinstance(request.get('presentation_control_commit'), str)
            or len(request['presentation_control_commit']) != 40
            or any(not isinstance(request.get(key), str) or len(request[key]) != 64 for key in hashes)):
        raise ValueError('Exact original/presentation/visual-review installation request required')


def verify_outputs(changed, packet):
    from query_packet import descriptors
    allowed = GENERATED | {'almanac/' + row['path'] for row in descriptors(packet)}
    if not {PROOF, COVERAGE, PHASE} <= set(changed) or not set(changed) <= allowed:
        raise ValueError('Installation may only add verified generated files and reset the phase')


def verify_phase_controller(before, after):
    needle = b"'indian-coastal-context-v1'), phase"
    replacement = b"'indian-coastal-context-v1', 'indian-coastal-card-presentation-v1', 'indian-coastal-context-install-v1'), phase"
    if before.count(needle) != 1 or after != before.replace(needle, replacement):
        raise ValueError('Phase controllers may only recognize the two explicit follow-up phases')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--site', type=Path)
    parser.add_argument('--audit', type=Path)
    args = parser.parse_args()
    if (not args.publish or args.site is None or args.audit is None or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'
            or os.environ.get('GITHUB_REF') != 'refs/heads/' + delivery.BRANCH):
        parser.error('Explicit working-branch cloud installation required; no data or Git mutation attempted')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))});os.nice(5)
    if shutil.disk_usage(ROOT).free < 3 * 1024**3:raise ValueError('Need3GiB free for saved-cohort installation')
    def git(*commands, root=ROOT):
        return subprocess.check_output([*GIT, *commands], cwd=root).decode().strip()
    control = os.environ['GITHUB_SHA']
    if git('rev-parse', 'HEAD') != control or git('status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Clean exact installation control checkout required')
    def remote_guard():
        if git('ls-remote', 'origin', 'refs/heads/' + delivery.BRANCH).split()[0] != control:
            raise ValueError('Working branch advanced; stale installation refused')
    remote_guard()
    site, audit = args.site.resolve(), args.audit.resolve()
    if git('rev-parse', 'HEAD', root=site) != delivery.SOURCE_COMMIT:
        raise ValueError('Wrong saved source checkout')
    load = lambda name: json.loads((audit / name).read_bytes())
    verify_control_delta(load('control-compare.json'), control)
    request = json.loads((ROOT / REQUEST).read_bytes());verify_request(request)
    phase = json.loads((ROOT / PHASE).read_bytes())
    if phase.get('phase') != 'indian-coastal-context-install-v1' or phase.get('execution_workflow') != WORKFLOW:
        raise ValueError('Declared installation phase required')
    if (ROOT / PROOF).exists() or (ROOT / COVERAGE).exists():
        raise ValueError('Never replace an installed proof or historical coverage snapshot')
    delivery.verify_run(load('source-run.json'), load('source-jobs.json'))
    sys.path.insert(0, str(site / 'analysis'))
    import indian_coastal_dimension_context_v1 as context
    if context.ROOT != site:raise ValueError('Source contract helper came from wrong checkout')
    contract, contract_sha = context.evidence()
    for path, expected in contract['input_sha256'].items():
        if sha(ROOT / path) != expected:raise ValueError('Frozen coastal source changed in control tree: ' + path)
    frozen = json.loads((site / 'research/west-greenland-core-width-preflight-v1.json').read_bytes())['input_sha256']
    for path, expected in frozen.items():
        if sha(ROOT / path) != expected:raise ValueError('Prior scientific dependency changed: ' + path)
    hashes = {path: sha(site / path) for path in contract['source_documents']}
    source, browser, prior = load('source/result.json'), load('browser/result.json'), load('prior-cards/result.json')
    inherited = delivery.verify_receipts(source, browser, prior, hashes)
    parent_raw = (site / presentation.MANIFEST).read_bytes()
    parent_engine = json.loads(parent_raw)
    presentation.verify_files(site, parent_engine)
    for path in ['rust/osw-query/src/indian_coastal_context.rs', 'rust/osw-query/src/lib.rs']:
        if sha(ROOT / path) != parent_engine['sha256'][path]:
            raise ValueError('Control runtime differs from the actual compiled cohort: ' + path)
    for path in ['.github/workflows/baffin-bound-candidate.yml', '.github/workflows/davidson-width-candidate.yml']:
        verify_phase_controller((site / path).read_bytes(), (ROOT / path).read_bytes())
    folder = audit / 'presentation'
    receipt_raw = (folder / 'result.json').read_bytes();receipt = json.loads(receipt_raw)
    if (presentation.digest(receipt_raw) != request['presentation_receipt_sha256']
            or receipt.get('presentation_run_id') != request['presentation_run_id']
            or receipt.get('presentation_control_commit') != request['presentation_control_commit']):
        raise ValueError('Presentation artifact differs from requested exact review')
    verification.verify_presentation_run(load('presentation-run.json'), load('presentation-jobs.json'), receipt)
    ui_raw = (folder / 'overlay' / presentation.UI).read_bytes()
    overlay_raw = (folder / 'overlay' / presentation.MANIFEST).read_bytes()
    if ui_raw != (ROOT / presentation.UI).read_bytes():raise ValueError('Display changed since presentation check')
    verified_display = verification.verify_presentation_receipt(receipt, parent_raw, overlay_raw, ui_raw, hashes)
    review_raw = (ROOT / REVIEW).read_bytes()
    if presentation.digest(review_raw) != request['visual_review_sha256']:raise ValueError('Replacement visual review changed')
    review = json.loads(review_raw)
    screenshots = {row['path']: (folder / row['path']).read_bytes() for row in review['screenshots']}
    verification.verify_visual_review(review, receipt_raw, screenshots)
    coverage_raw = (folder / 'current-coverage-catalogue.json').read_bytes()
    verification.verify_coverage_snapshot(coverage_raw, receipt)
    (site / presentation.UI).write_bytes(ui_raw)
    (site / presentation.MANIFEST).write_bytes(overlay_raw)
    updated = json.loads(overlay_raw);presentation.verify_files(site, updated)
    packet = json.loads((site / 'almanac/query-data.json').read_bytes())
    verification.verify_transport(site, packet, updated['sha256'])
    from query_packet import descriptors
    files = GENERATED - {PROOF, COVERAGE, PHASE}
    files |= {'almanac/' + row['path'] for row in descriptors(packet)}
    for path in sorted(files):
        target = ROOT / path;target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(site / path, target)
    (ROOT / COVERAGE).write_bytes(coverage_raw)
    proof = {'schema': 'osw.indian-coastal-context.installed-delivery.v1', 'status': 'verified_cloud_delivery',
             'cohort_version': context.VERSION, 'source_run_id': delivery.SOURCE_RUN,
             'source_commit': delivery.SOURCE_COMMIT, 'presentation_run_id': request['presentation_run_id'],
             'presentation_control_commit': request['presentation_control_commit'], 'publication_control_commit': control,
             'packet_logical_sha256': delivery.PACKET, 'parent_logical_sha256': delivery.PARENT,
             'contract_sha256': contract_sha, 'candidate': source['candidate'],
             'preservation': inherited['preservation'], 'index_extension': source['index_extension'],
             'browser': browser, 'presentation': receipt, 'visual_review_sha256': request['visual_review_sha256'],
             'display_verification': verified_display, 'intervening_operational_paths': sorted(row['filename'] for row in load('control-compare.json')['files']),
             'generated_sha256': {path: sha(ROOT / path) for path in sorted(files | {COVERAGE})},
             'native_verified': True, 'browser_verified': True, 'working_dataset_delivery_verified': True,
             'new_paired_widths': 0, 'new_ranked_lengths': 0, 'native_rebuild': False, 'wasm_rebuild': False,
             'scientific_source_recomputation': False, 'scientific_release_published': False, 'main_merged': False,
             'full_offline_regression': 'Separate unresolved Rotschi1972 original HTTP403 gate; not claimed passed.',
             'installed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (ROOT / PROOF).write_bytes(presentation.encoded(proof))
    (ROOT / PHASE).write_bytes(presentation.encoded({'schema': 'osw.current-gap-delivery-phase.v1',
        'phase': 'source-review-only-v1', 'reason': 'Coastal context working packet installed; no new measured dimensions.',
        'completed_source_run_id': delivery.SOURCE_RUN, 'completed_presentation_run_id': request['presentation_run_id'],
        'installed_proof': PROOF, 'heavy_work_permitted': False, 'max_heavy_local_jobs': 0}))
    changed = set(git('diff', '--name-only', 'HEAD').splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').splitlines())
    verify_outputs(changed, packet)
    subprocess.run([*GIT, 'add', '--', *sorted(changed)], cwd=ROOT, check=True)
    if git('diff', '--cached', '--name-only', '--diff-filter=D'):raise ValueError('Historical deletion refused')
    subprocess.run([*GIT, '-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    remote_guard()
    subprocess.run([*GIT, '-c', 'user.name=github-actions[bot]',
        '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com', 'commit', '-m',
        'Install verified coastal source contexts and reviewed saved presentation'], cwd=ROOT, check=True)
    remote_guard()
    subprocess.run([*GIT, '-c', 'push.negotiate=true', '-c', 'pack.threads=1', '-c', 'pack.windowMemory=64m',
        '-c', 'http.version=HTTP/1.1', 'push', 'origin', 'HEAD:refs/heads/' + delivery.BRANCH], cwd=ROOT, check=True)
    result = {'status': 'VERIFIED_WORKING_DATA_INSTALLED', 'installed_commit': git('rev-parse', 'HEAD'),
              'packet_logical_sha256': delivery.PACKET, 'main_merged': False, 'scientific_release_published': False}
    (audit / 'installation-result.json').write_bytes(presentation.encoded(result));print(json.dumps(result))


if __name__ == '__main__':main()
