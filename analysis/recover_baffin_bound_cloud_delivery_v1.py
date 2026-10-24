"""Publish the already validated Baffin cohort after exact formatter replay.

Cloud only. The original verifier and all its engine/source/data hashes remain
unchanged. No native build, source calculation or browser rerun is performed.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BRANCH = 'codex/current-measurement-gaps'
SOURCE_RUN = 40088222914
SOURCE_COMMIT = '4fcdc388de1fdc7458e77829e08bc89197608fd3'
PACKET = '045d6fd80b871ba7a9863154f390d7c84a450f4b3e960b3f5f4e27b8d6a009b0'
WORKFLOW = '.github/workflows/recover-baffin-bound-working-data-v1.yml'
PHASE = 'research/current-gap-delivery-phase.json'
REQUEST = 'research/baffin-working-data-recovery-request-v1.json'
BUILD = 'analysis/build_rust_query_engine.py'
CONTROLLERS = ['.github/workflows/baffin-bound-candidate.yml', '.github/workflows/davidson-width-candidate.yml']
CONTROL_FILES = {WORKFLOW: 'A', REQUEST: 'A', PHASE: 'M', BUILD: 'M',
                 'analysis/recover_baffin_bound_cloud_delivery_v1.py': 'A',
                 'analysis/test_baffin_bound_delivery_recovery_v1.py': 'A',
                 **{path: 'M' for path in CONTROLLERS}}
GIT = ['git', '-c', 'core.fsmonitor=false', '-c', 'maintenance.auto=0', '-c', 'gc.auto=0']


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify_control_delta(changes):
    if changes != CONTROL_FILES:
        raise ValueError('Recovery permits exactly the declared operational control changes')


def verify_request(request):
    required = {'schema': 'osw.baffin-working-data-recovery-request.v1',
                'source_run_id': SOURCE_RUN, 'source_commit': SOURCE_COMMIT,
                'packet_logical_sha256': PACKET, 'native_rebuild_requested': False,
                'browser_rerun_requested': False, 'scientific_source_recomputation_requested': False,
                'scientific_release_published': False, 'main_merged': False}
    if (set(request) != set(required) | {'reason'} or not isinstance(request.get('reason'), str)
            or not request['reason'] or any(request.get(key) != value for key, value in required.items())):
        raise ValueError('Changed source run, packet or recovery scope')


def verify_source_run(run, jobs):
    if (run.get('id') != SOURCE_RUN or run.get('head_sha') != SOURCE_COMMIT
            or run.get('status') != 'completed' or run.get('conclusion') != 'failure'):
        raise ValueError('Wrong completed source run')
    rows = jobs.get('jobs', [])
    if jobs.get('total_count') != len(rows) or len({row['name'] for row in rows}) != len(rows):
        raise ValueError('Incomplete original jobs')
    expected = {'select-delivery-phase': 'success', 'baffin-candidate-and-views': 'success',
                'publish-baffin-working-data': 'failure'}
    if {row['name']: row.get('conclusion') for row in rows} != expected or any(row.get('status') != 'completed' for row in rows):
        raise ValueError('Original complete validation must succeed; only publication may fail')
    heavy = next(row for row in rows if row['name'] == 'baffin-candidate-and-views')
    names = {step['name'].split(':', 1)[0] for step in heavy['steps'] if step['name'].startswith('Source matrix ')}
    if names != {f'Source matrix {i:02d}/14' for i in range(1, 15)}:
        raise ValueError('All fourteen original source gates are required')
    if any(step.get('conclusion') != 'success' for step in heavy['steps']):
        raise ValueError('Original sequential steps did not all succeed')
    publisher = next(row for row in rows if row['name'] == 'publish-baffin-working-data')
    failed = [step['name'] for step in publisher['steps'] if step.get('conclusion') == 'failure']
    if failed != ['Verify all artifact bindings and publish generated working data']:
        raise ValueError('Different publication failure')


def verify_formatted_paths(paths, pins):
    if ('rust/osw-query/src/lib.rs' not in paths or any(
            not path.startswith('rust/osw-query/src/') or not path.endswith('.rs') or path not in pins
            for path in paths)):
        raise ValueError('Only pinned compiled Rust source formatting may be installed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if (not args.publish or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'
            or os.environ.get('GITHUB_REF') != 'refs/heads/' + BRANCH):
        parser.error('Explicit working-branch cloud recovery required')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    def git(*commands, cwd=ROOT, binary=False):
        raw = subprocess.check_output([*GIT, *commands], cwd=cwd)
        return raw if binary else raw.decode().strip()
    control = os.environ['GITHUB_SHA']
    if git('rev-parse', 'HEAD') != control:
        raise ValueError('Recovery checkout moved')
    subprocess.run([*GIT, 'merge-base', '--is-ancestor', SOURCE_COMMIT, control], cwd=ROOT, check=True)
    rows = git('diff', '--name-status', '--no-renames', SOURCE_COMMIT, control).splitlines()
    changes = {path: status for status, path in (row.split('\t', 1) for row in rows)}
    if len(changes) != len(rows):
        raise ValueError('Duplicate control delta')
    verify_control_delta(changes)
    old = lambda name: git('show', SOURCE_COMMIT + ':' + name, binary=True)
    for name in CONTROLLERS:
        before = old(name)
        needle = b"('davidson', 'baffin-bound-v1', 'osnap-wg-source-inventory-v1')"
        replacement = b"('davidson', 'baffin-bound-v1', 'baffin-bound-recovery-v1', 'osnap-wg-source-inventory-v1')"
        if before.count(needle) != 1 or (ROOT / name).read_bytes() != before.replace(needle, replacement):
            raise ValueError('Controller may only recognize the explicit recovery phase')
    before = old(BUILD)
    needle = b"['cargo','fmt','--manifest-path',MANIFEST]"
    if before.count(needle) != 1 or (ROOT / BUILD).read_bytes() != before.replace(needle, b"['cargo','fmt','--manifest-path',MANIFEST,'--','--check']"):
        raise ValueError('Build change may only require committed formatting')
    phase = json.loads(old(PHASE))
    phase.update(phase='baffin-bound-recovery-v1', workflow=WORKFLOW)
    if json.loads((ROOT / PHASE).read_bytes()) != phase:
        raise ValueError('Unexpected recovery phase or parent')
    verify_request(json.loads((ROOT / REQUEST).read_bytes()))
    def check_remote():
        if git('ls-remote', 'origin', 'refs/heads/' + BRANCH).split()[0] != control:
            raise ValueError('Working branch advanced; stale recovery refused')
    check_remote()
    folder = ROOT / '.pytest_cache/baffin-recovery'
    source_root = folder / 'source-checkout'
    if git('rev-parse', 'HEAD', cwd=source_root) != SOURCE_COMMIT:
        raise ValueError('Wrong isolated source checkout')
    load = lambda name: json.loads((folder / 'audit' / name).read_bytes())
    run, jobs = load('run.json'), load('jobs.json')
    verify_source_run(run, jobs)
    sys.path.insert(0, str(source_root / 'analysis'))
    import prepare_baffin_bound_delivery as original
    if original.ROOT != source_root:
        raise ValueError('Original verifier was not imported from its exact source revision')
    packet = json.loads((source_root / 'almanac/query-data.json').read_bytes())
    if packet['logical_sha256'] != PACKET:
        raise ValueError('Different saved candidate')
    initial = set(git('diff', '--name-only', 'HEAD', cwd=source_root).splitlines())
    initial.update(git('ls-files', '--others', '--exclude-standard', cwd=source_root).splitlines())
    original.verify_changed_paths(initial, packet)
    # This is the same formatter transformation run before the successful build.
    # It performs no Rust compilation and computes no source-data measurements.
    subprocess.run(['rustup', 'run', '1.95.0', 'cargo', 'fmt', '--manifest-path', 'rust/osw-query/Cargo.toml'],
                   cwd=source_root, check=True)
    pins = json.loads((source_root / 'almanac/query-engine.manifest.json').read_bytes())['sha256']
    formatted = set(git('diff', '--name-only', 'HEAD', '--', 'rust/osw-query/src', cwd=source_root).splitlines())
    verify_formatted_paths(formatted, pins)
    for name in formatted:
        if (sha(source_root / name) != pins[name]
                or (ROOT / name).read_bytes() != git('show', 'HEAD:' + name, cwd=source_root, binary=True)):
            raise ValueError('Formatted compiled source or original control input changed: ' + name)
    proof = original.verify(source_root, load('source/result.json'), load('browser/result.json'),
                            load('prior-davidson/result.json'), load('prior-cards/result.json'), run, jobs, SOURCE_COMMIT)
    proof.update(installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 publication_control_commit=control, recovery_workflow_run_id=int(os.environ['GITHUB_RUN_ID']),
                 recovery_source_run_id=SOURCE_RUN, original_run_conclusion='failure',
                 original_validation_job_conclusion='success', original_publication_job_conclusion='failure',
                 recovery_reason='Exact pinned formatter replay aligns published Rust bytes with the successful compiled cohort; original verifier unchanged.',
                 intervening_operational_paths=sorted(changes), formatted_rust_source_sha256={name: pins[name] for name in sorted(formatted)},
                 original_verifier_sha256=sha(source_root / 'analysis/prepare_baffin_bound_delivery.py'),
                 recovery_native_build_performed=False, recovery_browser_rerun_performed=False,
                 scientific_sources_recomputed=False)
    files = original.GENERATED - {original.INSTALLED_PROOF}
    files |= {'almanac/' + part['path'] for part in original.descriptors(packet)}
    for name in sorted(files | formatted):
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original.local_path(source_root, name), target)
    (ROOT / original.INSTALLED_PROOF).write_bytes(original.metadata.encoded(proof))
    changed = set(git('diff', '--name-only', 'HEAD').splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').splitlines())
    original.verify_changed_paths(changed - formatted, packet)
    if not changed <= files | formatted | {original.INSTALLED_PROOF}:
        raise ValueError('Unexpected recovery publication path')
    for name in formatted:
        if sha(ROOT / name) != pins[name]:
            raise ValueError('Installed formatted source changed')
    subprocess.run([*GIT, 'add', '--', *sorted(changed)], cwd=ROOT, check=True)
    if git('diff', '--cached', '--name-only', '--diff-filter=D'):
        raise ValueError('Historical deletion refused')
    subprocess.run([*GIT, '-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    check_remote()
    subprocess.run([*GIT, '-c', 'user.name=github-actions[bot]',
                    '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                    'commit', '-m', f'Recover verified Baffin data and exact compiled Rust formatting from run{SOURCE_RUN}'], cwd=ROOT, check=True)
    check_remote()
    subprocess.run([*GIT, '-c', 'push.negotiate=true', '-c', 'pack.threads=1', '-c', 'pack.windowMemory=64m',
                    '-c', 'http.version=HTTP/1.1', '-c', 'http.postBuffer=134217728',
                    'push', 'origin', 'HEAD:refs/heads/' + BRANCH], cwd=ROOT, check=True)
    result = {'status': 'VERIFIED_RECOVERY_PUBLISHED', 'source_run_id': SOURCE_RUN,
              'source_commit': SOURCE_COMMIT, 'publication_control_commit': control,
              'packet_logical_sha256': PACKET, 'installed_commit': git('rev-parse', 'HEAD'),
              'formatted_rust_source_sha256': proof['formatted_rust_source_sha256'],
              'native_build_performed': False, 'browser_rerun_performed': False,
              'scientific_sources_recomputed': False, 'main_merged': False}
    (folder / 'recovery-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
