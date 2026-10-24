"""Small publication fixtures; no large assets, browser, Git mutation or network."""
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import pytest
import prepare_current_gap_cloud_delivery as delivery
from query_packet import write_packet


@pytest.fixture
def candidate(tmp_path):
    (tmp_path / 'almanac').mkdir()
    packet = write_packet(tmp_path / 'almanac/query-data.json',
        b'{"schema":"osw.query-bundle.v1","collections":{}}\n')
    for path in delivery.GENERATED - {delivery.INSTALLED_PROOF,'almanac/query-data.json',
                                      'almanac/query-engine.manifest.json'}:
        target = tmp_path / path; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(b'fixture')
    (tmp_path / 'research/ocean-motion-dashboard.json').write_text(json.dumps({'counts':{
        'named_current':106,'named_eddy':136,'operational_eddy_detection':4}}),encoding='utf-8')
    paths = sorted(delivery.GENERATED - {delivery.INSTALLED_PROOF,'almanac/query-engine.manifest.json'})
    paths += ['almanac/' + part['path'] for part in packet['parts']]
    pins = {path:delivery.digest(tmp_path / path) for path in paths}
    engine = {'schema':'osw.query-engine-manifest.v1','engine':'rust-osw-query-v1',
              'abi_version':1,'sha256':pins}
    (tmp_path / 'almanac/query-engine.manifest.json').write_text(json.dumps(engine),encoding='utf-8')
    source = {'status':'PASS','candidate':{'named_currents':106,'logical_sha256':packet['logical_sha256']},
              'preservation':{'all_prior_nonobject_rows_exact':True,
                              'prior_physical_object_fields_and_capabilities_exact':True}}
    browser = {'status':'PASS','named_currents':106,'native_wasm_object_views_equal':delivery.CARDS,
        'keyboard_evidence_query':True,'dashboard_all_106_currents':True,
        'dashboard_alias_native_wasm_parity':True,'phone_horizontal_overflow':False,
        'source_context_coverage_modes_verified':4,'errors':[],'original_downloads':[],
        'bundle_sha256':packet['logical_sha256'],'source_scoped_widths':3,
        'qualitative_calendar_months':24,'scoped_t24_width_records':1,
        'raw_width_samples_added':0,'annual_width_ranges_added':0}
    run = {'id':123,'head_sha':'a'*40,'head_branch':delivery.BRANCH,'event':'push','html_url':'https://example.invalid/run/123'}
    jobs = {'total_count':len(delivery.REQUIRED_JOBS)+1,'jobs':[
        {'name':name,'status':'completed','conclusion':'success'} for name in delivery.REQUIRED_JOBS] + [
        {'name':'offline','status':'completed','conclusion':'failure'}]}
    return [tmp_path,source,browser,run,jobs,'a'*40]


def test_matching_delivery_retains_offline_failure_and_adds_no_release_claim(candidate):
    before = copy.deepcopy(candidate[1:])
    proof = delivery.verify(*candidate)
    assert candidate[1:] == before
    assert proof['status'] == 'verified_cloud_delivery'
    assert proof['native_verified'] and proof['browser_verified']
    assert proof['scientific_release_published'] is False
    assert proof['job_results'][-1]['conclusion'] == 'failure'
    assert not (candidate[0] / delivery.INSTALLED_PROOF).exists()


@pytest.mark.parametrize('mutation',['branch','revision','gate','incomplete-jobs','browser',
                                     'packet-binding','annual-range','source-preservation','asset'])
def test_wrong_artifacts_or_missing_gates_cannot_be_published(candidate,mutation):
    if mutation=='branch': candidate[3]['head_branch']='main'
    if mutation=='revision': candidate[3]['head_sha']='b'*40
    if mutation=='gate': candidate[4]['jobs'][1]['conclusion']='failure'
    if mutation=='incomplete-jobs': candidate[4]['jobs'].pop()
    if mutation=='browser': candidate[2]['status']='FAIL'
    if mutation=='packet-binding': candidate[2]['bundle_sha256']='wrong'
    if mutation=='annual-range': candidate[2]['annual_width_ranges_added']=1
    if mutation=='source-preservation': candidate[1]['preservation']['all_prior_nonobject_rows_exact']=False
    if mutation=='asset': (candidate[0] / 'almanac/query-engine.wasm').write_bytes(b'changed')
    with pytest.raises(ValueError): delivery.verify(*candidate)
    assert not (candidate[0] / delivery.INSTALLED_PROOF).exists()


def test_publication_write_scope_excludes_originals_and_source_code():
    assert delivery.allowed_output('almanac/query-data.json')
    assert delivery.allowed_output('almanac/query-parts/000000-'+'a'*64+'.bin')
    for path in ['research/source-data/original.pdf','rust/osw-query/src/lib.rs',
                 'research/ocean-current-width-inventory.json','../almanac/query-data.json']:
        assert not delivery.allowed_output(path)


def test_unreferenced_historical_parts_cannot_be_changed(candidate):
    packet=json.loads((candidate[0] / 'almanac/query-data.json').read_bytes())
    current='almanac/'+packet['parts'][0]['path']
    delivery.verify_changed_paths({current,delivery.INSTALLED_PROOF},packet)
    with pytest.raises(ValueError):
        delivery.verify_changed_paths({'almanac/query-parts/000000-'+'0'*64+'.bin'},packet)


def test_publish_cannot_start_on_the_local_machine(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    monkeypatch.setattr('sys.argv',['prepare_current_gap_cloud_delivery.py','--publish','--audit-dir','missing'])
    with pytest.raises(SystemExit) as error: delivery.main()
    assert error.value.code==2


def test_current_filter_retains_all_four_object_types():
    class Options(HTMLParser):
        def __init__(self):
            super().__init__(); self.active=False; self.values=[]
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='select': self.active=attrs.get('id')=='dashboard-type'
            if tag=='option' and self.active: self.values.append(attrs.get('value'))
        def handle_endtag(self,tag):
            if tag=='select': self.active=False
    parser=Options()
    parser.feed((Path(__file__).resolve().parents[1] / 'almanac/dashboard.html').read_text(encoding='utf-8'))
    assert parser.values==['all','named_current','named_eddy','operational_eddy_detection']
