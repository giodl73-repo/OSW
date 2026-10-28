"""Prepare additive width and dated-flow metadata against a bounded audited parent."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import check_madagascar_dimensions_parent_v1 as parent
import ponsoni_emc_2016_dimensions_v1 as source

ROOT=Path(__file__).resolve().parents[1]
PARENT=parent.LOGICAL
OWNER='current:southern-east-madagascar'
CURRENT='southern-east-madagascar'
COLLECTION='current_reported_flow_events'
SOURCE_ID='source:ponsoni-emc-2016-inatex'
KEY='published_madagascar_dimensions_v1'
FILE='research/madagascar-dimensions-query-contract-v1.json'
MODULE='analysis/madagascar_dimensions_query_v1.py'
PROTOCOL='plans/madagascar-dimensions-query-contract-v1.md'
SELECTED='research/madagascar-dimensions-parent-run-v1/selected-records.json'
REVIEW='research/madagascar-dimensions-parent-execution-review-v1.json'

def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def fingerprint(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def query_url(collection):
    query={'collection':collection,'filters':[{'field':'current_id','op':'eq','value':CURRENT}],'limit':100}
    if collection==COLLECTION:query['sort']={'field':'date','direction':'asc'}
    return 'query.html?q='+quote(json.dumps(query,separators=(',',':')))+'#query-chart-section'

def build_contract():
    review=read(REVIEW);selected=read(SELECTED);result=read('research/madagascar-dimensions-parent-run-v1/result.json')
    request=read(parent.REQUEST)
    facts,width=source.build()
    if (review['status']!='PASS_SOURCE_BOUND_PARENT_SELECTION_REQUEST_DISABLED' or not review['request_disabled']
        or request['execute'] is not False or request['cloud_parent_packet_read_permitted'] is not False
        or sha(parent.REQUEST)!=review['disabled_request_sha256'] or result['logical_sha256']!=PARENT
        or sha(SELECTED)!=result['selected_records_sha256'] or result['publication_resolutions']['ponsoni_2016']['status']!='MISSING'
        or selected['candidate_width_id_matches'] or read(source.FACTS)!=facts or read(source.PREPARED)!=width):
        raise ValueError('Exact reviewed source and audited installed parent required')
    if 'reported_flow_event_ids' in selected['owner'] or COLLECTION in result['collection_counts']:
        raise ValueError('Existing flow event schema requires reconciliation')
    width=copy.deepcopy(width)
    width.update(schema='osw.scoped-width-evidence.v1',status='source_reported_regional_study_summary',
        name='Southern East Madagascar Current',source_id=SOURCE_ID,source_ids=[SOURCE_ID],
        source_file=source.FACTS,source_file_sha256=sha(source.FACTS),source_pointer='/width_summary',
        source_citation='Ponsoni, Aguiar-González, Ridderinkhof and Maas (2016), JPO46,1045–1065, doi:10.1175/JPO-D-15-0154.1.',
        phase_kind='published_regional_mooring_study_summary',phase_label='INATEX study2010–2013',
        calendar_months=None,is_annual_mean=False,is_climatology=False,remote_duplicate_and_join_check_pending=False)
    events=[]
    for i,event in enumerate(facts['event_index']):
        row=copy.deepcopy(event)
        row.update(entity_id=OWNER,current_id=CURRENT,source_id=SOURCE_ID,source_ids=[SOURCE_ID],
            source_file=source.FACTS,source_file_sha256=sha(source.FACTS),source_pointer=f'/event_index/{i}',
            source_url=facts['source']['url'],source_doi=facts['source']['doi'],
            label=f'Madagascar / {event["date"]} / {event["description"]}',
            status='source_reported_selected_flow_event',geometry=None,
            annual_width_range_km=None,uncertainty_km=None,independent_new_observation=False,
            inferred_eddy_id=None,source_figure_digitized=False)
        events.append(row)
    citation={'id':SOURCE_ID,'kind':'publication','title':facts['source']['title'],
        'label':facts['source']['title'],'authors':facts['source']['authors'],'year':2016,
        'doi':facts['source']['doi'],'url':facts['source']['url'],
        'preferred_citation':width['source_citation'],'source_facts_file':source.FACTS,'source_facts_sha256':sha(source.FACTS),
        'access_scope':'Twelve selected pages visually reviewed from the original public institutional PDF; no original redistributed.',
        'provider_asset_redistributed':False,'used_in_collections':['objects','widths',COLLECTION],
        'scope_note':'Regional study-summary width and selected dated flow examples; no seasonal dimensional series or new raw observations.'}
    owner=copy.deepcopy(selected['owner'])
    owner['width_ids'].append(width['id'])
    owner['capabilities']['scoped_width']+=1
    owner['reported_flow_event_ids']=[r['id'] for r in events]
    owner['capabilities']['reported_flow_events']=len(events)
    owner['source_ids']=sorted(set(owner['source_ids'])|{SOURCE_ID});owner['linked_source_count']=len(owner['source_ids'])
    owner['section_fingerprints']['measurements']=fingerprint({'prior_fingerprint':selected['owner']['section_fingerprints']['measurements'],'added_width':width})
    owner['section_fingerprints']['reported_flow_events']=fingerprint(events)
    owner['section_fingerprints']['sources']=fingerprint({'prior_fingerprint':selected['owner']['section_fingerprints']['sources'],'added_source':citation})
    owner['evidence_links'] += [{'label':'Compare regional width summaries with separate study periods','url':query_url('widths')},
                               {'label':'Browse eight dated flow examples (not a seasonal cycle)','url':query_url(COLLECTION)}]
    owner['fingerprint']=fingerprint({k:v for k,v in owner.items() if k!='fingerprint'})
    before=selected['historical_dashboard_entry'][0];after=copy.deepcopy(before)
    for key in ['width_ids','reported_flow_event_ids','capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','evidence_links']:
        after[key]=copy.deepcopy(owner[key])
    pins=[source.FACTS,source.PREPARED,source.PROTOCOL,'analysis/ponsoni_emc_2016_dimensions_v1.py',MODULE,PROTOCOL,
        SELECTED,REVIEW,'research/madagascar-dimensions-parent-run-v1/result.json',
        'research/madagascar-dimensions-parent-run-v1/run-receipt.json','research/ponsoni-emc-2016-dimension-preparation-review-v1.json']
    return {'schema':'osw.madagascar-dimensions-query-contract.v1','status':'PREPARED_NOT_COMPILED_OR_INSTALLED',
        'parent_logical_sha256':PARENT,'prior_records':selected,'parent_collection_counts':result['collection_counts'],
        'width_record':width,'event_collection':COLLECTION,'event_records':events,'new_source':citation,'final_owner':owner,
        'dashboard_before':before,'dashboard_after':after,'input_sha256':{p:sha(p) for p in pins},
        'new_width_records':1,'new_flow_event_references':8,'new_publication_sources':1,'new_length_records':0,
        'new_width_samples':0,'new_independent_observations':0,'new_physical_footprints':0,
        'expected_totals':{'widths':177,'sources':216,'owners_with_scoped_width_capability':89},
        'width_query_after_installation':query_url('widths'),'flow_query_after_installation':query_url(COLLECTION)}

def marker(contract):
    return {'schema':'osw.madagascar-dimensions-runtime-receipt.v1','parent_logical_sha256':PARENT,
        'contract_file':FILE,'contract_sha256':fingerprint(contract),'width_records_added':1,
        'flow_event_references_added':8,'publication_sources_added':1,'new_width_samples':0,'new_independent_observations':0}

def prepare(collections,manifest,contract,*,parent_logical_sha256):
    if contract!=build_contract() or parent_logical_sha256!=PARENT or KEY in manifest or COLLECTION in collections:
        raise ValueError('Exact unapplied contract and parent required')
    prior=contract['prior_records']
    for name in ['sources','objects','entities','widths','reference_routes']:
        if not isinstance(collections.get(name),list) or len(collections[name])!=contract['parent_collection_counts'][name]:
            raise ValueError('Parent inventory differs: '+name)
    for name,key in [('objects','owner'),('entities','entity')]:
        if [r for r in collections[name] if r.get('id')==OWNER]!=[prior[key]]:raise ValueError('Changed audited owner/entity')
    for name in ['widths','reference_routes']:
        if [r for r in collections[name] if r.get('current_id')==CURRENT]!=prior[name]:raise ValueError('Changed prior regional evidence')
    sources=collections['sources'];matched,resolutions=parent.publications(sources)
    if matched['ponsoni_2016'] or resolutions['ponsoni_2016']['status']!='MISSING' or any(r['id']==SOURCE_ID for r in sources):
        raise ValueError('Publication already present; reconcile')
    if matched['nauw_2008']!=prior['publications']['nauw_2008']:raise ValueError('Changed prior publication')
    by_id={r['id']:r for r in sources}
    if any(by_id.get(r['id'])!=r for r in prior['owner_sources']):raise ValueError('Changed owner source')
    if any(r.get('id')==contract['width_record']['id'] for r in collections['widths']):raise ValueError('Existing width ID')
    after=dict(collections)
    after['sources']=[*sources,copy.deepcopy(contract['new_source'])]
    after['objects']=[copy.deepcopy(contract['final_owner']) if r['id']==OWNER else r for r in collections['objects']]
    after['widths']=[*collections['widths'],copy.deepcopy(contract['width_record'])]
    after[COLLECTION]=copy.deepcopy(contract['event_records'])
    updated=dict(manifest);updated['input_sha256']=dict(manifest.get('input_sha256',{}))
    updated['input_sha256'].update(contract['input_sha256']);updated['input_sha256'][FILE]=fingerprint(contract)
    updated[KEY]=marker(contract)
    collections.clear();collections.update(after);manifest.clear();manifest.update(updated)

if __name__=='__main__':
    path=ROOT/FILE
    if path.exists():raise ValueError('Use a new contract version')
    path.write_bytes(encoded(build_contract()))
    print('Frozen one-width/eight-event/one-source contract; runtime and installation remain pending.')
