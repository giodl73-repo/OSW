"""Verify one cloud-tested Davidson candidate and publish working data only."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

import davidson_wallace_width_admission as admission
import davidson_width_candidate_metadata as metadata
from prepare_current_gap_cloud_delivery import BRANCH, digest, local_path
from query_packet import descriptors

ROOT = Path(__file__).resolve().parents[1]
INSTALLED_PROOF = metadata.INSTALLED_PROOF
WORKFLOW = '.github/workflows/davidson-width-candidate.yml'
REQUIRED_JOB = 'davidson-candidate-and-views'
GENERATED = {
    'almanac/query-data.json','almanac/query-engine.wasm','almanac/query-engine.manifest.json',
    'almanac/index-catalog.json','almanac/index-sources.json','almanac/index-data.json.gz',
    metadata.DASHBOARD,INSTALLED_PROOF,
}
REQUIRED_INPUTS = {
    admission.FILE, metadata.PARENT_PACKET, admission.REPORT, admission.FIGURE, admission.PROOF,
    'rust/osw-query/src/davidson_reported_width.rs','rust/osw-query/src/object_view.rs',
    'almanac/current-source-evidence-ui.js','analysis/test_davidson_reported_width_browser.py',
    'analysis/export_davidson_width_candidate.py','analysis/davidson_width_candidate_metadata.py',
    'analysis/prepare_davidson_width_delivery.py','analysis/test_davidson_width_delivery.py',WORKFLOW,
}


def verify_changed_paths(changed, packet):
    allowed = GENERATED | {'almanac/' + part['path'] for part in descriptors(packet)}
    if not changed or not set(changed) <= allowed:
        raise ValueError('Only referenced candidate parts and generated delivery files may change')


def verify(root, source, browser, prior_cards, run, jobs, expected_sha):
    if (run.get('head_sha') != expected_sha or run.get('head_branch') != BRANCH
            or run.get('event') != 'push' or run.get('path') != WORKFLOW):
        raise ValueError('Wrong source revision, branch or workflow')
    if jobs.get('total_count') != len(jobs.get('jobs', [])):
        raise ValueError('Incomplete cloud job inventory')
    matches = [job for job in jobs['jobs'] if job['name'] == REQUIRED_JOB]
    if (len(matches) != 1 or matches[0]['status'] != 'completed'
            or matches[0]['conclusion'] != 'success'):
        raise ValueError('Sequential candidate, native/WASM and browser gate did not pass')
    if (source.get('schema') != 'osw.davidson-width-candidate.v1' or source.get('status') != 'PASS'
            or source.get('parent_logical_sha256') != metadata.PARENT_SHA
            or source.get('published') is not False):
        raise ValueError('Wrong or unsuccessful source candidate')
    added = source['admission']['added_rows']
    if (added not in ({'sources':3,'widths':1,'claims':1,'current_measurement_admissions':1},
                     {'sources':2,'widths':1,'claims':1,'current_measurement_admissions':1})
            or source['candidate']['rows'] != metadata.PARENT_ROWS + sum(added.values())
            or source['candidate']['objects'] != metadata.PARENT_OBJECTS
            or source['candidate']['named_currents'] != 106 or source['candidate']['widths'] != 172):
        raise ValueError('Unexpected admitted records or inventory')
    preserved = source['admission']['preservation']
    for key in ['all_prior_nonobject_rows_exact',
                'physical_fields_and_capabilities_preserved_except_scoped_width_count']:
        if preserved.get(key) is not True:raise ValueError('Missing prior-data preservation: ' + key)
    if (preserved.get('unchanged_objects_verified') != 245
            or preserved.get('prior_rows_verified') != metadata.PARENT_ROWS - metadata.PARENT_OBJECTS
            or source['admission'].get('complete_parent_packet_verified') is not True
            or any(source['admission'].get(key) != 0 for key in
                   ['raw_samples_added','annual_ranges_added','geometry_or_state_joins_added'])):
        raise ValueError('Physical or prior-data scope changed')
    index = source['index_extension']
    if (not isinstance(index.get('original_sources_verified'),int)
            or index['original_sources_verified'] < 572
            or index.get('original_source_strings_preserved') != index['original_sources_verified'] - 1
            or index.get('replaced_source_paths') != [metadata.DASHBOARD]
            or index.get('scientific_source_documents_replaced') != 0
            or source.get('source_originals_redistributed') is not False
            or source.get('scientific_release_published') is not False):
        raise ValueError('Historical source index or redistribution scope changed')
    if browser.get('status') != 'PASS':raise ValueError('Davidson browser gate failed')
    for key in ['native_wasm_card_equal','historical_width_preserved',
                'source_caption_browser_visible','keyboard_width_query','source_link_focusable']:
        if browser.get(key) is not True:raise ValueError('Missing Davidson browser evidence: ' + key)
    if (browser.get('phone_horizontal_overflow') is not False or browser.get('errors') != []
            or browser.get('original_downloads') != []
            or browser.get('source_scalar_sha256') != admission.FROZEN_OUTPUTS[admission.FIGURE]):
        raise ValueError('Davidson rendering/source scope failed')
    # The preceding cohort stays covered by actual card/dashboard checks.
    if (prior_cards.get('status') != 'PASS' or prior_cards.get('named_currents') != 106
            or prior_cards.get('native_wasm_object_views_equal') !=
                ['west-india-coastal','east-india-coastal','east-african-coastal','south-java','brazil']):
        raise ValueError('Missing preceding current-card parity')
    for key in ['keyboard_evidence_query','dashboard_all_106_currents','dashboard_alias_native_wasm_parity']:
        if prior_cards.get(key) is not True:raise ValueError('Missing preceding UI coverage: ' + key)
    for key,value in {'phone_horizontal_overflow':False,'errors':[],'original_downloads':[],
                      'source_scoped_widths':3,'qualitative_calendar_months':24,
                      'scoped_t24_width_records':1,'raw_width_samples_added':0,
                      'annual_width_ranges_added':0,'source_context_coverage_modes_verified':4}.items():
        if prior_cards.get(key) != value:raise ValueError('Preceding cohort scope changed: ' + key)
    engine = json.loads(local_path(root,'almanac/query-engine.manifest.json').read_bytes())
    if (engine.get('schema') != 'osw.query-engine-manifest.v1'
            or engine.get('engine') != 'rust-osw-query-v1' or engine.get('abi_version') != 1):
        raise ValueError('Unsupported engine manifest')
    pins = engine['sha256']
    required = (GENERATED - {INSTALLED_PROOF,'almanac/query-engine.manifest.json'}) | REQUIRED_INPUTS
    if not required <= set(pins):raise ValueError('Engine omitted a delivery/source input')
    contract = json.loads(local_path(root, admission.FILE).read_bytes())
    for path,expected in contract['input_sha256'].items():
        if pins.get(path) != expected:raise ValueError('Engine/source contract disagreement: ' + path)
    for path,expected in pins.items():
        if digest(local_path(root,path)) != expected:raise ValueError('Engine/source/data mismatch: ' + path)
    packet = json.loads(local_path(root,'almanac/query-data.json').read_bytes())
    logical, length = hashlib.sha256(), 0
    for part in descriptors(packet):
        path = 'almanac/' + part['path']
        file = local_path(root,path)
        if pins.get(path) != part['sha256'] or file.stat().st_size != part['byte_length']:
            raise ValueError('Engine omitted or changed a candidate part')
        with file.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):
                logical.update(block); length += len(block)
    sha = packet['logical_sha256']
    if (logical.hexdigest() != sha or length != packet['logical_byte_length']
            or source['candidate']['logical_sha256'] != sha
            or source['candidate']['logical_bytes'] != length
            or browser.get('bundle_sha256') != sha or prior_cards.get('bundle_sha256') != sha):
        raise ValueError('Source, engine, transport and actual browsers disagree')
    dashboard = json.loads(local_path(root,metadata.DASHBOARD).read_bytes())
    if dashboard['counts'] != {'named_current':106,'named_eddy':136,'operational_eddy_detection':4}:
        raise ValueError('Changed dashboard inventory')
    return {'schema':'osw.davidson-width-installed-delivery.v1','status':'verified_cloud_delivery',
            'cohort_version':metadata.VERSION,'source_commit':expected_sha,'run_id':run['id'],
            'run_url':run['html_url'],'parent_logical_sha256':metadata.PARENT_SHA,
            'packet_logical_sha256':sha,'candidate':source['candidate'],
            'admission_contract_sha256':digest(local_path(root,admission.FILE)),
            'generated_sha256':{path:digest(local_path(root,path)) for path in GENERATED - {INSTALLED_PROOF}},
            'native_verified':True,'browser_verified':True,'working_dataset_delivery_verified':True,
            'preservation':preserved,'browser':browser,'preceding_current_cards':prior_cards,
            'full_offline_regression':'Separate unresolved gate; Rotschi original HTTP 403 in run40053831110.',
            'scientific_release_published':False,'main_merged':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    parser.add_argument('--audit-dir',type=Path)
    args = parser.parse_args()
    if (not args.publish or args.audit_dir is None or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'
            or os.environ.get('GITHUB_REF') != 'refs/heads/' + BRANCH):
        parser.error('Explicit publication in the dependent working-branch cloud job required')
    if hasattr(os,'sched_getaffinity'):
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))}); os.nice(5)
    git = ['git','-c','core.fsmonitor=false','-c','maintenance.auto=false','-c','gc.auto=0']
    def output(*command):return subprocess.check_output([*git,*command],cwd=ROOT,text=True).strip()
    expected = os.environ['GITHUB_SHA']
    if output('rev-parse','HEAD') != expected:raise ValueError('Checkout moved after validation')
    def check_remote():
        if output('ls-remote','origin','refs/heads/' + BRANCH).split()[0] != expected:
            raise ValueError('Working branch advanced; stale publication refused')
    check_remote()
    load = lambda name:json.loads((args.audit_dir / name).read_bytes())
    run = load('run.json')
    if run['id'] != int(os.environ['GITHUB_RUN_ID']):raise ValueError('Different workflow run')
    proof = verify(ROOT,load('source/result.json'),load('browser/result.json'),
                   load('prior-cards/result.json'),run,load('jobs.json'),expected)
    proof['installed_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT / INSTALLED_PROOF).write_bytes(metadata.encoded(proof))
    changed = set(output('diff','--name-only','HEAD').splitlines())
    changed.update(output('ls-files','--others','--exclude-standard').splitlines())
    verify_changed_paths(changed,json.loads((ROOT / 'almanac/query-data.json').read_bytes()))
    subprocess.run([*git,'add','--',*sorted(changed)],cwd=ROOT,check=True)
    if output('diff','--cached','--name-only','--diff-filter=D'):
        raise ValueError('No historical files may be deleted')
    subprocess.run([*git,'-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,check=True)
    subprocess.run([*git,'-c','user.name=github-actions[bot]',
                    '-c','user.email=41898282+github-actions[bot]@users.noreply.github.com',
                    'commit','-m',f'Deliver scoped Davidson working width from run{run["id"]}'],cwd=ROOT,check=True)
    check_remote()
    subprocess.run([*git,'-c','pack.threads=1','-c','pack.windowMemory=64m',
                    '-c','http.version=HTTP/1.1','-c','http.postBuffer=134217728',
                    'push','origin','HEAD:refs/heads/' + BRANCH],cwd=ROOT,check=True)


if __name__ == '__main__':main()
