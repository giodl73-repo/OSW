"""Verify one complete cloud Baffin cohort before publishing generated working data."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

import baffin_bound_admission as admission
import baffin_bound_owner_projection as owner
import baffin_bound_candidate_metadata as metadata
from prepare_current_gap_cloud_delivery import BRANCH, digest, local_path
from query_packet import descriptors

ROOT = Path(__file__).resolve().parents[1]
INSTALLED_PROOF = 'research/baffin-bound-installed-delivery-v1.json'
WORKFLOW = '.github/workflows/baffin-bound-candidate.yml'
PHASE = 'research/current-gap-delivery-phase.json'
REQUIRED_JOB = 'baffin-candidate-and-views'
GENERATED = {'almanac/query-data.json','almanac/query-engine.wasm','almanac/query-engine.manifest.json',
             'almanac/index-catalog.json','almanac/index-sources.json','almanac/index-data.json.gz',
             metadata.DASHBOARD,INSTALLED_PROOF}
REQUIRED_INPUTS = {
    admission.FILE,owner.FILE,owner.PARENT,admission.REPORT,admission.FIGURE,admission.PROOF,
    metadata.PARENT_PROOF,WORKFLOW,PHASE,
    'rust/osw-query/src/baffin_latitude_bound.rs','rust/osw-query/src/object_view.rs',
    'rust/osw-query/src/length_assessment_overlays.rs','almanac/current-source-evidence-ui.js',
    'analysis/test_baffin_bound_browser.py','analysis/test_baffin_bound_browser_policy.py',
    'analysis/baffin_bound_admission.py','analysis/baffin_bound_owner_projection.py',
    'analysis/baffin_bound_candidate_metadata.py','analysis/export_baffin_bound_candidate.py',
    'analysis/prepare_baffin_bound_delivery.py','analysis/test_baffin_bound_delivery.py',
}


def verify_changed_paths(changed, packet):
    allowed = GENERATED | {'almanac/'+part['path'] for part in descriptors(packet)}
    if not changed or not set(changed) <= allowed:
        raise ValueError('Only generated files and referenced candidate parts may change')


def verify(root, source, browser, prior_davidson, prior_cards, run, jobs, expected_sha):
    if (run.get('head_sha') != expected_sha or run.get('head_branch') != BRANCH
            or run.get('event') != 'push' or run.get('path') != WORKFLOW):
        raise ValueError('Wrong Baffin source revision, branch or workflow')
    if jobs.get('total_count') != len(jobs.get('jobs',[])):
        raise ValueError('Incomplete job inventory')
    matches = [j for j in jobs['jobs'] if j['name'] == REQUIRED_JOB]
    if len(matches) != 1 or matches[0]['status'] != 'completed' or matches[0]['conclusion'] != 'success':
        raise ValueError('Complete sequential native/WASM/browser job must pass')
    phase = json.loads(local_path(root,PHASE).read_bytes())
    if (phase.get('phase') != 'baffin-bound-v1' or phase.get('workflow') != WORKFLOW
            or phase.get('required_parent_installed_receipt') != metadata.PARENT_PROOF):
        raise ValueError('Wrong declared delivery phase or parent')
    parent = json.loads(local_path(root,metadata.PARENT_PROOF).read_bytes())
    if (parent.get('schema') != 'osw.davidson-width-installed-delivery.v1'
            or parent.get('status') != 'verified_cloud_delivery'
            or parent.get('cohort_version') != 'davidson-wallace-line67-v1'
            or any(parent.get(k) is not True for k in ('native_verified','browser_verified','working_dataset_delivery_verified'))):
        raise ValueError('Missing verified preceding Davidson delivery')
    prior_inventory = parent['candidate']
    if (prior_inventory.get('objects') != 246 or prior_inventory.get('named_currents') != 106
            or prior_inventory.get('widths') != 172 or prior_inventory.get('rows') not in (108529,108530)
            or parent.get('packet_logical_sha256') == owner.parent()['parent_logical_sha256']
            or parent['browser'].get('status') != 'PASS' or parent['preceding_current_cards'].get('status') != 'PASS'):
        raise ValueError('Changed preceding cohort inventory or browser evidence')
    if (source.get('schema') != 'osw.baffin-bound-candidate.v1' or source.get('status') != 'PASS'
            or source.get('published') is not False
            or source.get('parent_logical_sha256') != parent['packet_logical_sha256']
            or source.get('parent_installed_run_id') != parent['run_id']):
        raise ValueError('Unsuccessful or unrelated Baffin source candidate')
    candidate = source['candidate']
    if (candidate['rows'] != prior_inventory['rows']+14 or candidate['objects'] != 246
            or candidate['named_currents'] != 106 or candidate['widths'] != 172
            or candidate['editorial_bound_scenarios'] != 9):
        raise ValueError('Changed Baffin candidate inventory')
    audit = source['admission']
    preserved = audit['preservation']
    for key in ('owner_projection_verified','complete_parent_packet_verified','physical_fields_and_capabilities_preserved'):
        if audit.get(key) is not True:raise ValueError('Missing candidate proof: '+key)
    for key in ('all_other_prior_nonobject_rows_exact','physical_fields_and_capabilities_preserved','qualified_published_length_ranks_preserved'):
        if preserved.get(key) is not True:raise ValueError('Missing preservation proof: '+key)
    if (audit.get('appended_rows') != 14 or audit.get('replaced_length_assessments') != 1
            or audit.get('physical_samples_added') != 0 or audit.get('seasonal_ranges_added') != 0
            or preserved.get('length_assessments_replaced') != 1
            or preserved.get('prior_nonobject_rows_verified') != prior_inventory['rows']-247
            or preserved.get('unchanged_objects_verified') != 245):
        raise ValueError('Unexpected evidence replacement or physical scope')
    index = source['index_extension']
    count = index.get('original_sources_verified')
    if (type(count) is not int or count < 572
            or index.get('original_source_strings_preserved') != count-1
            or index.get('replaced_source_paths') != [metadata.DASHBOARD]
            or index.get('scientific_source_documents_replaced') != 0
            or source.get('source_originals_redistributed') is not False
            or source.get('scientific_release_published') is not False):
        raise ValueError('Historical source index or redistribution scope changed')
    if browser.get('status') != 'PASS':raise ValueError('Baffin browser gate failed')
    for key in ('native_wasm_card_equal','complete_nine_scenario_table','scenario_rows_are_editorial_not_observations',
                'parent_width_ids_preserved','parent_owner_physical_fields_preserved',
                'historical_naming_scope_visible','keyboard_scenario_query',
                'global_map_current_selection_verified','atlas_evidence_links_verified','keyboard_atlas_scenario_query'):
        if browser.get(key) is not True:raise ValueError('Missing Baffin browser evidence: '+key)
    for key, value in {'record_parity_queries':10,'qualified_length_ranks_preserved':13,
                       'phone_viewports_verified':[320,390],'phone_horizontal_overflow':False,
                       'errors':[],'original_downloads':[],
                       'source_scalar_sha256':admission.OUTPUTS[admission.FIGURE]}.items():
        if browser.get(key) != value:raise ValueError('Changed Baffin browser scope: '+key)
    # Re-run the predecessor's actual cards on this same new data/engine cohort.
    strip_sha = lambda record:{k:v for k,v in record.items() if k != 'bundle_sha256'}
    if (strip_sha(prior_davidson) != strip_sha(parent['browser'])
            or strip_sha(prior_cards) != strip_sha(parent['preceding_current_cards'])):
        raise ValueError('Preceding current cards or dashboard behavior changed')
    for key in ('native_wasm_card_equal','historical_width_preserved','source_caption_browser_visible',
                'keyboard_width_query','source_link_focusable'):
        if prior_davidson.get(key) is not True:raise ValueError('Missing preceding Davidson browser evidence')
    for record in (prior_davidson,prior_cards):
        if record.get('phone_horizontal_overflow') is not False or record.get('errors') != [] or record.get('original_downloads') != []:
            raise ValueError('Preceding browser source/rendering scope changed')
    if prior_davidson.get('source_scalar_sha256') != '48ad6871e4839d9c21809ea2322eac7d8d7081fec2786c0f7877e3af3dc75d67':
        raise ValueError('Preceding Davidson scalar source changed')
    if (prior_cards.get('named_currents') != 106
            or prior_cards.get('native_wasm_object_views_equal') !=
                ['west-india-coastal','east-india-coastal','east-african-coastal','south-java','brazil']):
        raise ValueError('Missing preceding five-current parity')
    for key in ('keyboard_evidence_query','dashboard_all_106_currents','dashboard_alias_native_wasm_parity'):
        if prior_cards.get(key) is not True:raise ValueError('Missing preceding dashboard evidence')
    for key,value in {'source_scoped_widths':3,'qualitative_calendar_months':24,'scoped_t24_width_records':1,
                      'raw_width_samples_added':0,'annual_width_ranges_added':0,'source_context_coverage_modes_verified':4}.items():
        if prior_cards.get(key) != value:raise ValueError('Preceding current data scope changed')
    engine = json.loads(local_path(root,'almanac/query-engine.manifest.json').read_bytes())
    if (engine.get('schema') != 'osw.query-engine-manifest.v1'
            or engine.get('engine') != 'rust-osw-query-v1' or engine.get('abi_version') != 1):
        raise ValueError('Unsupported engine manifest')
    pins = engine['sha256']
    contract = json.loads(local_path(root,admission.FILE).read_bytes())
    required = (GENERATED-{INSTALLED_PROOF,'almanac/query-engine.manifest.json'}) | REQUIRED_INPUTS | set(contract['input_sha256'])
    if not required <= pins.keys():raise ValueError('Engine omitted a required source/delivery pin')
    for path, sha in {**contract['input_sha256'],**admission.OUTPUTS}.items():
        if pins.get(path) != sha:raise ValueError('Engine/frozen source disagreement: '+path)
    for path, sha in pins.items():
        if digest(local_path(root,path)) != sha:raise ValueError('Engine/source/data mismatch: '+path)
    packet = json.loads(local_path(root,'almanac/query-data.json').read_bytes())
    logical, size = hashlib.sha256(), 0
    for part in descriptors(packet):
        path = 'almanac/'+part['path']; file = local_path(root,path)
        if pins.get(path) != part['sha256'] or file.stat().st_size != part['byte_length']:
            raise ValueError('Changed or unpinned packet part')
        with file.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):
                logical.update(block);size += len(block)
    sha = packet['logical_sha256']
    if (logical.hexdigest() != sha or size != packet['logical_byte_length']
            or candidate['logical_sha256'] != sha or candidate['logical_bytes'] != size
            or any(record.get('bundle_sha256') != sha for record in (browser,prior_davidson,prior_cards))):
        raise ValueError('Source/engine/transport/browser cohorts disagree')
    dashboard = json.loads(local_path(root,metadata.DASHBOARD).read_bytes())
    if dashboard['counts'] != {'named_current':106,'named_eddy':136,'operational_eddy_detection':4}:
        raise ValueError('Changed dashboard inventory')
    transition = json.loads(local_path(root,owner.FILE).read_bytes())
    if [row for row in dashboard['entries'] if row['id'] == admission.ENTITY] != [transition['owner']]:
        raise ValueError('Dashboard lost the exact Baffin owner projection')
    return {'schema':'osw.baffin-bound-installed-delivery.v1','status':'verified_cloud_delivery',
            'cohort_version':metadata.VERSION,'source_commit':expected_sha,'run_id':run['id'],'run_url':run['html_url'],
            'parent_logical_sha256':parent['packet_logical_sha256'],'parent_installed_run_id':parent['run_id'],
            'packet_logical_sha256':sha,'candidate':candidate,'admission_contract_sha256':digest(local_path(root,admission.FILE)),
            'generated_sha256':{path:digest(local_path(root,path)) for path in GENERATED-{INSTALLED_PROOF}},
            'native_verified':True,'browser_verified':True,'working_dataset_delivery_verified':True,
            'preservation':preserved,'browser':browser,'preceding_davidson':prior_davidson,'preceding_current_cards':prior_cards,
            'full_offline_regression':'Separate unresolved Rotschi1972 original HTTP403 gate from run40053831110.',
            'scientific_release_published':False,'main_merged':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true');parser.add_argument('--audit-dir',type=Path)
    args = parser.parse_args()
    if (not args.publish or args.audit_dir is None or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push' or os.environ.get('GITHUB_REF') != 'refs/heads/'+BRANCH):
        parser.error('Explicit dependent working-branch cloud publication required')
    if hasattr(os,'sched_getaffinity'):
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});os.nice(5)
    git = ['git','-c','core.fsmonitor=false','-c','maintenance.auto=0','-c','gc.auto=0']
    def output(*args):return subprocess.check_output([*git,*args],cwd=ROOT,text=True).strip()
    expected = os.environ['GITHUB_SHA']
    if output('rev-parse','HEAD') != expected:raise ValueError('Checkout moved after validation')
    def check_remote():
        if output('ls-remote','origin','refs/heads/'+BRANCH).split()[0] != expected:
            raise ValueError('Working branch advanced; stale publication refused')
    check_remote()
    load = lambda path:json.loads((args.audit_dir/path).read_bytes())
    run = load('run.json')
    if run['id'] != int(os.environ['GITHUB_RUN_ID']):raise ValueError('Different workflow run')
    proof = verify(ROOT,load('source/result.json'),load('browser/result.json'),load('prior-davidson/result.json'),
                   load('prior-cards/result.json'),run,load('jobs.json'),expected)
    proof['installed_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT/INSTALLED_PROOF).write_bytes(metadata.encoded(proof))
    changed = set(output('diff','--name-only','HEAD').splitlines())
    changed.update(output('ls-files','--others','--exclude-standard').splitlines())
    verify_changed_paths(changed,json.loads((ROOT/'almanac/query-data.json').read_bytes()))
    subprocess.run([*git,'add','--',*sorted(changed)],cwd=ROOT,check=True)
    if output('diff','--cached','--name-only','--diff-filter=D'):raise ValueError('Historical deletion refused')
    subprocess.run([*git,'-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,check=True)
    subprocess.run([*git,'-c','user.name=github-actions[bot]',
                    '-c','user.email=41898282+github-actions[bot]@users.noreply.github.com',
                    'commit','-m',f'Deliver Baffin conditional geographic bound from run{run["id"]}'],cwd=ROOT,check=True)
    check_remote()
    subprocess.run([*git,'-c','push.negotiate=true','-c','pack.threads=1','-c','pack.windowMemory=64m',
                    '-c','http.version=HTTP/1.1','-c','http.postBuffer=134217728',
                    'push','origin','HEAD:refs/heads/'+BRANCH],cwd=ROOT,check=True)


if __name__ == '__main__':main()
