"""Publish an already verified run after an operational-only cache correction."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess

import prepare_current_gap_cloud_delivery as original

SOURCE_RUN = 40053831110
SOURCE_COMMIT = '6866981896abb5caffd29f9d46c6c76933d4c8ef'
ROOT = Path(__file__).resolve().parents[1]
CONTROL_FILES = {
    '.gitignore': 'M',
    '.github/workflows/recover-current-working-data.yml': 'A',
    'analysis/recover_current_gap_cloud_delivery.py': 'A',
    'analysis/test_current_gap_delivery_recovery.py': 'A',
}


def corrected_ignore(base):
    return base + (b'' if base.endswith(b'\n') else b'\n') + b'.pytest_cache/\n'


def verify_control_delta(changes, old_ignore, new_ignore):
    """No intervening runtime, source, data, UI, or historical-file changes."""
    if changes != CONTROL_FILES:
        raise ValueError('Recovery requires exactly the reviewed operational changes')
    if new_ignore != corrected_ignore(old_ignore):
        raise ValueError('Recovery may add only the missing cache exclusion')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--audit-dir', type=Path)
    args = parser.parse_args()
    if (not args.publish or args.audit_dir is None
            or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REF') != 'refs/heads/' + original.BRANCH
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'):
        parser.error('Explicit recovery in the dedicated working-branch cloud push job required')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    git = ['git','-c','core.fsmonitor=false','-c','maintenance.auto=0','-c','gc.auto=0']
    def output(*command):
        return subprocess.check_output([*git,*command],cwd=ROOT,text=True).strip()
    control = os.environ['GITHUB_SHA']
    if output('rev-parse','HEAD') != control:
        raise ValueError('Recovery checkout moved')
    subprocess.run([*git,'merge-base','--is-ancestor',SOURCE_COMMIT,control],cwd=ROOT,check=True)
    rows=output('diff','--name-status','--no-renames',SOURCE_COMMIT,control).splitlines()
    changes={path:status for status,path in (row.split('\t',1) for row in rows)}
    if len(changes)!=len(rows):raise ValueError('Duplicate operational paths')
    old_ignore=subprocess.check_output([*git,'show',SOURCE_COMMIT+':.gitignore'],cwd=ROOT)
    verify_control_delta(changes,old_ignore,(ROOT/'.gitignore').read_bytes())
    def check_remote():
        if output('ls-remote','origin','refs/heads/'+original.BRANCH).split()[0] != control:
            raise ValueError('Working branch advanced; refusing stale recovery')
    check_remote()
    load=lambda name:json.loads((args.audit_dir/name).read_bytes())
    run=load('run.json')
    if run['id']!=SOURCE_RUN or run['head_sha']!=SOURCE_COMMIT or run['status']!='completed':
        raise ValueError('Recovery source run is not the completed verified source revision')
    # Original gates, full streaming engine/source/data binding and actual
    # browser digest checks are reused unchanged. All bound runtime files in
    # this checkout must still match the tested artifacts exactly.
    proof=original.verify(ROOT,load('source/result.json'),load('browser/result.json'),
                          run,load('jobs.json'),SOURCE_COMMIT)
    proof.update(installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 publication_control_commit=control,recovery_workflow_run_id=int(os.environ['GITHUB_RUN_ID']),
                 recovery_source_run_id=SOURCE_RUN,
                 recovery_reason='Fresh publication checkout lacked the repository cache exclusion; source/runtime/data/UI unchanged.',
                 intervening_operational_paths=sorted(changes),
                 tested_runtime_inputs_unchanged=True)
    (ROOT/original.INSTALLED_PROOF).write_bytes(original.encoded(proof))
    changed=set(output('diff','--name-only','HEAD').splitlines())
    changed.update(output('ls-files','--others','--exclude-standard').splitlines())
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    original.verify_changed_paths(changed,packet)
    subprocess.run([*git,'add','--',*sorted(changed)],cwd=ROOT,check=True)
    if output('diff','--cached','--name-only','--diff-filter=D'):
        raise ValueError('Recovery must retain all historical files')
    subprocess.run([*git,'-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,check=True)
    subprocess.run([*git,'-c','user.name=github-actions[bot]',
        '-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m',
        f'Deliver verified106-current working data from run{SOURCE_RUN}'],cwd=ROOT,check=True)
    check_remote()
    subprocess.run([*git,'-c','pack.threads=1','-c','pack.windowMemory=64m',
        '-c','http.version=HTTP/1.1','-c','http.postBuffer=134217728','push','origin',
        'HEAD:refs/heads/'+original.BRANCH],cwd=ROOT,check=True)
    print('Published original verified candidate; no new science release or main merge.')


if __name__=='__main__':main()
