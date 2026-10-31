"""Small publication fixtures: real source pins and deliberately tiny transport."""
import copy
import json
from pathlib import Path

import pytest
import prepare_baffin_bound_delivery as d
from query_packet import write_packet

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def cohort(tmp_path):
    contract = json.loads((ROOT/d.admission.FILE).read_bytes())
    required = d.REQUIRED_INPUTS | set(contract['input_sha256'])
    for path in required-{d.metadata.PARENT_PROOF}:
        target = tmp_path/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/path).read_bytes())
    previous = {
        'status':'PASS','bundle_sha256':'c'*64,'phone_horizontal_overflow':False,'errors':[],'original_downloads':[],
        'native_wasm_card_equal':True,'historical_width_preserved':True,'source_caption_browser_visible':True,
        'keyboard_width_query':True,'source_link_focusable':True,
        'source_scalar_sha256':'48ad6871e4839d9c21809ea2322eac7d8d7081fec2786c0f7877e3af3dc75d67',
    }
    cards = {
        'status':'PASS','bundle_sha256':'c'*64,'phone_horizontal_overflow':False,'errors':[],'original_downloads':[],
        'named_currents':106,'native_wasm_object_views_equal':['west-india-coastal','east-india-coastal','east-african-coastal','south-java','brazil'],
        'keyboard_evidence_query':True,'dashboard_all_106_currents':True,'dashboard_alias_native_wasm_parity':True,
        'source_scoped_widths':3,'qualitative_calendar_months':24,'scoped_t24_width_records':1,
        'raw_width_samples_added':0,'annual_width_ranges_added':0,'source_context_coverage_modes_verified':4,
    }
    parent = {'schema':'osw.davidson-width-installed-delivery.v1','status':'verified_cloud_delivery',
              'cohort_version':'davidson-wallace-line67-v1','run_id':100,
              'candidate':{'objects':246,'named_currents':106,'widths':172,'rows':108530},
              'packet_logical_sha256':'c'*64,'browser':previous,'preceding_current_cards':cards,
              'native_verified':True,'browser_verified':True,'working_dataset_delivery_verified':True}
    (tmp_path/d.metadata.PARENT_PROOF).write_bytes(d.metadata.encoded(parent))
    for path in d.GENERATED-{d.INSTALLED_PROOF,'almanac/query-data.json','almanac/query-engine.manifest.json',d.metadata.DASHBOARD}:
        target = tmp_path/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'fixture')
    transition = json.loads((ROOT/d.owner.FILE).read_bytes())
    (tmp_path/d.metadata.DASHBOARD).write_bytes(d.metadata.encoded({
        'counts':{'named_current':106,'named_eddy':136,'operational_eddy_detection':4},
        'entries':[transition['owner']]}))
    packet = write_packet(tmp_path/'almanac/query-data.json',b'{"schema":"osw.query-bundle.v1","collections":{}}\n')
    sha = packet['logical_sha256']
    current_previous = {**previous,'bundle_sha256':sha}
    current_cards = {**cards,'bundle_sha256':sha}
    browser = {
        'status':'PASS','bundle_sha256':sha,'native_wasm_card_equal':True,'record_parity_queries':10,
        'complete_nine_scenario_table':True,'scenario_rows_are_editorial_not_observations':True,
        'parent_width_ids_preserved':True,'parent_owner_physical_fields_preserved':True,
        'historical_naming_scope_visible':True,'qualified_length_ranks_preserved':13,
        'phone_viewports_verified':[320,390],'phone_horizontal_overflow':False,'keyboard_scenario_query':True,
        'global_map_current_selection_verified':True,'atlas_evidence_links_verified':True,'keyboard_atlas_scenario_query':True,
        'atlas_route_coverage_totals':{'accepted_current_names':106,'route_candidates':78,
            'currents_with_route_candidates':72,'currents_without_any_reference_card':34,'route_decision_records':95},
        'source_scalar_sha256':d.admission.OUTPUTS[d.admission.FIGURE],'errors':[],'original_downloads':[],
    }
    source = {
        'schema':'osw.baffin-bound-candidate.v1','status':'PASS','published':False,
        'parent_logical_sha256':'c'*64,'parent_installed_run_id':100,
        'candidate':{'logical_sha256':sha,'logical_bytes':packet['logical_byte_length'],
                     'objects':246,'rows':108544,'named_currents':106,'widths':172,'editorial_bound_scenarios':9},
        'admission':{'owner_projection_verified':True,'complete_parent_packet_verified':True,
                     'physical_fields_and_capabilities_preserved':True,'appended_rows':14,
                     'replaced_length_assessments':1,'physical_samples_added':0,'seasonal_ranges_added':0,
                     'preservation':{'all_other_prior_nonobject_rows_exact':True,
                                    'physical_fields_and_capabilities_preserved':True,
                                    'qualified_published_length_ranks_preserved':True,
                                    'length_assessments_replaced':1,'prior_nonobject_rows_verified':108283,
                                    'unchanged_objects_verified':245}},
        'index_extension':{'original_sources_verified':580,'original_source_strings_preserved':579,
                           'replaced_source_paths':[d.metadata.DASHBOARD],'scientific_source_documents_replaced':0},
        'source_originals_redistributed':False,'scientific_release_published':False,
    }
    pins = {path:d.digest(tmp_path/path) for path in required | (d.GENERATED-{d.INSTALLED_PROOF,'almanac/query-engine.manifest.json'})}
    pins.update({'almanac/'+part['path']:part['sha256'] for part in packet['parts']})
    (tmp_path/'almanac/query-engine.manifest.json').write_bytes(d.metadata.encoded({
        'schema':'osw.query-engine-manifest.v1','engine':'rust-osw-query-v1','abi_version':1,'sha256':pins}))
    run = {'head_sha':'b'*40,'head_branch':d.BRANCH,'event':'push','path':d.WORKFLOW,
           'id':200,'html_url':'https://example.invalid/run/200'}
    jobs = {'total_count':1,'jobs':[{'name':d.REQUIRED_JOB,'status':'completed','conclusion':'success'}]}
    return tmp_path,source,browser,current_previous,current_cards,run,jobs,'b'*40


def test_complete_cohort_binding_accepts_only_working_delivery(cohort):
    proof = d.verify(*cohort)
    assert proof['status'] == 'verified_cloud_delivery'
    assert proof['parent_installed_run_id'] == 100
    assert proof['native_verified'] is proof['browser_verified'] is True
    assert proof['scientific_release_published'] is proof['main_merged'] is False


@pytest.mark.parametrize('change', ['revision','workflow','job','job-inventory','source','parent','inventory',
    'physical','preservation','index','browser','phone','queries','cohort','prior-davidson','prior-cards',
    'atlas-selection','atlas-links','atlas-keyboard','atlas-counts','atlas-plans'])
def test_coherent_delivery_is_required(cohort,change):
    root,source,browser,previous,cards,run,jobs,sha = cohort
    if change == 'revision': run['head_sha'] = 'a'*40
    if change == 'workflow': run['path'] = '.github/workflows/other.yml'
    if change == 'job': jobs['jobs'][0]['conclusion'] = 'failure'
    if change == 'job-inventory': jobs['total_count'] = 2
    if change == 'source': source['status'] = 'FAIL'
    if change == 'parent': source['parent_installed_run_id'] = 99
    if change == 'inventory': source['candidate']['rows'] += 1
    if change == 'physical': source['admission']['physical_samples_added'] = 1
    if change == 'preservation': source['admission']['preservation']['unchanged_objects_verified'] = 244
    if change == 'index': source['index_extension']['scientific_source_documents_replaced'] = 1
    if change == 'browser': browser['complete_nine_scenario_table'] = False
    if change == 'phone': browser['phone_viewports_verified'] = [390]
    if change == 'queries': browser['record_parity_queries'] = 8
    if change == 'cohort': browser['bundle_sha256'] = 'e'*64
    if change == 'prior-davidson': previous['historical_width_preserved'] = False
    if change == 'prior-cards': cards['source_scoped_widths'] = 1
    if change == 'atlas-selection': browser['global_map_current_selection_verified'] = False
    if change == 'atlas-links': browser['atlas_evidence_links_verified'] = False
    if change == 'atlas-keyboard': browser['keyboard_atlas_scenario_query'] = False
    if change == 'atlas-counts': browser['atlas_route_coverage_totals']['accepted_current_names'] = 102
    if change == 'atlas-plans': browser['atlas_route_coverage_totals']['route_decision_records'] = 91
    with pytest.raises(ValueError): d.verify(*cohort)


@pytest.mark.parametrize('change', ['source-pin','missing-pin','part','owner','parent-proof','phase'])
def test_file_or_engine_corruptions_reject(cohort,change):
    root,*_ = cohort
    engine_path = root/'almanac/query-engine.manifest.json'
    engine = json.loads(engine_path.read_bytes())
    if change == 'source-pin': engine['sha256'][d.admission.REPORT] = '0'*64
    if change == 'missing-pin': engine['sha256'].pop(d.PHASE)
    if change == 'part':
        packet = json.loads((root/'almanac/query-data.json').read_bytes())
        (root/'almanac'/packet['parts'][0]['path']).write_bytes(b'changed')
    if change == 'owner':
        path = root/d.metadata.DASHBOARD;dashboard = json.loads(path.read_bytes())
        dashboard['entries'][0]['capabilities']['reported_length'] = 1
        path.write_bytes(d.metadata.encoded(dashboard));engine['sha256'][d.metadata.DASHBOARD] = d.digest(path)
    if change == 'parent-proof':
        path = root/d.metadata.PARENT_PROOF;parent = json.loads(path.read_bytes());parent['browser_verified'] = False
        path.write_bytes(d.metadata.encoded(parent));engine['sha256'][d.metadata.PARENT_PROOF] = d.digest(path)
    if change == 'phase':
        path = root/d.PHASE;phase = json.loads(path.read_bytes());phase['phase'] = 'davidson'
        path.write_bytes(d.metadata.encoded(phase));engine['sha256'][d.PHASE] = d.digest(path)
    engine_path.write_bytes(d.metadata.encoded(engine))
    with pytest.raises(ValueError): d.verify(*cohort)


def test_changed_paths_exclude_scientific_sources_and_unreferenced_parts(cohort):
    packet = json.loads((cohort[0]/'almanac/query-data.json').read_bytes())
    d.verify_changed_paths({'almanac/query-data.json','almanac/'+packet['parts'][0]['path']},packet)
    for paths in [set(),{d.admission.REPORT},{'almanac/query-parts/unreferenced.bin'},{'secrets.txt'}]:
        with pytest.raises(ValueError):d.verify_changed_paths(paths,packet)


def test_local_publication_refuses_before_git_or_packet_access(monkeypatch):
    import sys
    monkeypatch.setattr(sys,'argv',['prepare_baffin_bound_delivery.py','--publish','--audit-dir','.pytest_cache/fake'])
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    def forbidden(*args,**kwargs):pytest.fail('Local publication accessed Git')
    monkeypatch.setattr(d.subprocess,'check_output',forbidden)
    with pytest.raises(SystemExit) as error:d.main()
    assert error.value.code == 2
