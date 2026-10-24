"""Verify matching cloud artifacts and commit generated data to the working branch.

No local download, build or whole-packet JSON parse. Publication runs only in
the dependent cloud job after the source, native/WASM and browser matrix gates.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from check_current_gap_parent_rehearsal import PARENT_SHA, INSTALLED_PROOF
from current_gap_candidate_metadata import VERSION, encoded
from query_packet import descriptors

BRANCH = 'codex/current-measurement-gaps'
ROOT = Path(__file__).resolve().parents[1]
GENERATED = {
    'almanac/query-data.json', 'almanac/query-engine.wasm', 'almanac/query-engine.manifest.json',
    'almanac/index-catalog.json', 'almanac/index-sources.json', 'almanac/index-data.json.gz',
    'research/ocean-motion-dashboard.json', INSTALLED_PROOF,
}
REQUIRED_JOBS = ('regional-reach-source-replay', 'front-level-atlas', 'scientific-reproduction',
                 'front-temperature-conformance', 'netcdf-fixture')
CARDS = ['west-india-coastal', 'east-india-coastal', 'east-african-coastal', 'south-java', 'brazil']


def allowed_output(path):
    return path in GENERATED or re.fullmatch(r'almanac/query-parts/\d{6}-[0-9a-f]{64}\.bin', path) is not None


def verify_changed_paths(changed, packet):
    eligible = GENERATED | {'almanac/' + part['path'] for part in descriptors(packet)}
    if not changed or any(not allowed_output(path) or path not in eligible for path in changed):
        raise ValueError('Delivery would change a source, historical part or unexpected file')


def local_path(root, relative):
    if '\\' in relative or ':' in relative or any(p in ('', '.', '..') for p in relative.split('/')):
        raise ValueError('Invalid delivery input path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Delivery input missing or outside checkout: ' + relative)
    return path


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def verify(root, source, browser, run, jobs, expected_sha):
    """Small metadata plus streaming file checks; no physical-source mutation."""
    if run['head_sha'] != expected_sha or run['head_branch'] != BRANCH or run['event'] != 'push':
        raise ValueError('Cloud delivery source revision or branch mismatch')
    if jobs.get('total_count') != len(jobs.get('jobs', [])):
        raise ValueError('Incomplete cloud job inventory')
    for name in REQUIRED_JOBS:
        matches = [job for job in jobs['jobs'] if job['name'] == name]
        if len(matches) != 1 or matches[0]['status'] != 'completed' or matches[0]['conclusion'] != 'success':
            raise ValueError('Required cloud gate has not passed: ' + name)
    if source['status'] != 'PASS' or source['candidate']['named_currents'] != 106:
        raise ValueError('Wrong or failed source candidate')
    for field in ('all_prior_nonobject_rows_exact', 'prior_physical_object_fields_and_capabilities_exact'):
        if source['preservation'].get(field) is not True:
            raise ValueError('Original physical data preservation not verified')
    if (browser.get('status') != 'PASS' or browser.get('named_currents') != 106
            or browser.get('native_wasm_object_views_equal') != CARDS):
        raise ValueError('Complete current-card parity not verified')
    for field in ('keyboard_evidence_query', 'dashboard_all_106_currents', 'dashboard_alias_native_wasm_parity'):
        if browser.get(field) is not True:
            raise ValueError('Missing current browser check: ' + field)
    if (browser.get('phone_horizontal_overflow') is not False or browser.get('errors') != []
            or browser.get('original_downloads') != [] or browser.get('source_context_coverage_modes_verified') != 4):
        raise ValueError('Current UI coverage or source-access checks failed')
    for field, expected in {'source_scoped_widths':3,'qualitative_calendar_months':24,
                            'scoped_t24_width_records':1,'raw_width_samples_added':0,
                            'annual_width_ranges_added':0}.items():
        if browser.get(field) != expected:
            raise ValueError('Current browser changed dimension scope: ' + field)
    engine = json.loads(local_path(root, 'almanac/query-engine.manifest.json').read_bytes())
    if (engine.get('schema') != 'osw.query-engine-manifest.v1'
            or engine.get('engine') != 'rust-osw-query-v1' or engine.get('abi_version') != 1):
        raise ValueError('Unsupported engine manifest')
    pins = engine['sha256']
    for path in GENERATED - {INSTALLED_PROOF, 'almanac/query-engine.manifest.json'}:
        if path not in pins:
            raise ValueError('Engine omitted generated input: ' + path)
    for path, expected in pins.items():
        if digest(local_path(root, path)) != expected:
            raise ValueError('Engine/source/data mismatch: ' + path)
    packet = json.loads(local_path(root, 'almanac/query-data.json').read_bytes())
    logical, logical_bytes = hashlib.sha256(), 0
    for part in descriptors(packet):
        path = 'almanac/' + part['path']
        if pins.get(path) != part['sha256']:
            raise ValueError('Engine omitted or changed candidate part')
        file = local_path(root, path)
        if file.stat().st_size != part['byte_length']:
            raise ValueError('Candidate part length mismatch')
        with file.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                logical.update(block)
                logical_bytes += len(block)
    if (logical.hexdigest() != packet['logical_sha256'] or logical_bytes != packet['logical_byte_length']
            or source['candidate']['logical_sha256'] != packet['logical_sha256']
            or browser.get('bundle_sha256') != packet['logical_sha256']):
        raise ValueError('Candidate, engine and actual browser packet mismatch')
    dashboard = json.loads(local_path(root, 'research/ocean-motion-dashboard.json').read_bytes())
    if dashboard['counts'] != {'named_current':106,'named_eddy':136,'operational_eddy_detection':4}:
        raise ValueError('Unexpected installed dashboard inventory')
    # The broad offline gate is reported even when unavailable originals block
    # it. This is a working-data commit, not a merge or scientific release.
    return {'schema':'osw.current-gap-installed-delivery.v1','status':'verified_cloud_delivery',
        'cohort_version':VERSION,'source_commit':expected_sha,'run_id':run['id'],
        'run_url':run['html_url'],'parent_logical_sha256':PARENT_SHA,
        'packet_logical_sha256':packet['logical_sha256'],'native_verified':True,'browser_verified':True,
        'working_dataset_delivery_verified':True,'scientific_release_published':False,
        'candidate':source['candidate'],'preservation':source['preservation'],
        'browser':browser,'job_results':[{k:job[k] for k in ('name','status','conclusion')}
                                      for job in jobs['jobs']],
        'published_paths_scope':'Generated query/index/dashboard/engine files and this receipt only.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--audit-dir', type=Path)
    args = parser.parse_args()
    if (not args.publish or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REF') != 'refs/heads/' + BRANCH or args.audit_dir is None):
        parser.error('Explicit publication in the dependent working-branch cloud job required')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    git = ['git','-c','core.fsmonitor=false','-c','maintenance.auto=false','-c','gc.auto=0']
    def output(*command):
        return subprocess.check_output([*git,*command],cwd=ROOT,text=True).strip()
    expected = os.environ['GITHUB_SHA']
    if output('rev-parse','HEAD') != expected:
        raise ValueError('Checkout moved since validation')
    def check_remote():
        if output('ls-remote','origin','refs/heads/' + BRANCH).split()[0] != expected:
            raise ValueError('Working branch advanced; refusing stale generated commit')
    check_remote()
    load = lambda name: json.loads((args.audit_dir / name).read_bytes())
    run = load('run.json')
    if run['id'] != int(os.environ['GITHUB_RUN_ID']):
        raise ValueError('Delivery audit belongs to another workflow run')
    proof = verify(ROOT, load('source/result.json'), load('browser/result.json'),
                   run, load('jobs.json'), expected)
    proof['installed_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT / INSTALLED_PROOF).write_bytes(encoded(proof))
    changed = set(output('diff','--name-only','HEAD').splitlines())
    changed.update(output('ls-files','--others','--exclude-standard').splitlines())
    verify_changed_paths(changed, json.loads((ROOT / 'almanac/query-data.json').read_bytes()))
    subprocess.run([*git,'add','--',*sorted(changed)],cwd=ROOT,check=True)
    if output('diff','--cached','--name-only','--diff-filter=D'):
        raise ValueError('Delivery must retain all historical files')
    subprocess.run([*git,'-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,check=True)
    subprocess.run([*git,'-c','user.name=github-actions[bot]',
        '-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m',
        f'Deliver verified106-current working dataset from run{proof["run_id"]}'],cwd=ROOT,check=True)
    check_remote()
    subprocess.run([*git,'-c','pack.threads=1','-c','pack.windowMemory=64m',
        '-c','http.version=HTTP/1.1','-c','http.postBuffer=134217728','push','origin',
        'HEAD:refs/heads/' + BRANCH],cwd=ROOT,check=True)
    print('Published verified generated working data to ' + BRANCH)


if __name__ == '__main__':
    main()
