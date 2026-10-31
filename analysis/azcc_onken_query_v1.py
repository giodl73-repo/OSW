"""Prepare one dependent regional width against an exactly audited installed parent."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import check_azcc_onken_parent_v1 as parent

ROOT=Path(__file__).resolve().parents[1]
PARENT=parent.LOGICAL
OWNER='current:azores-countercurrent'
CURRENT='azores-countercurrent'
SOURCE_ID='source:onken-azcc-1993'
WIDTH_ID='azores-countercurrent-onken1993-cited-regional-width'
KEY='published_azcc_onken_width_v1'
FILE='research/azcc-onken-query-contract-v1.json'
MODULE='analysis/azcc_onken_query_v1.py'
PROTOCOL='plans/azcc-onken-query-contract-v1.md'
FACTS='research/onken-azcc-1993-source-facts-v1.json'
SELECTED='research/azcc-onken-parent-run-v1/selected-records.json'
REVIEW='research/azcc-onken-parent-execution-review-v1.json'


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def fingerprint(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def query_url():
    return 'query.html?q='+quote(json.dumps({'collection':'widths','filters':[{'field':'current_id','op':'eq','value':CURRENT}],'limit':100},separators=(',',':')))+'#query-chart-section'


def build_contract():
    review=read(REVIEW);selected=read(SELECTED);result=read('research/azcc-onken-parent-run-v1/result.json')
    request=read(parent.REQUEST);facts=read(FACTS);source_review=read('research/onken-azcc-1993-preparation-review-v1.json')
    if (review['status']!='PASS_DISTINCT_DEPENDENT_WIDTH_SOURCE_IDENTITY_MISSING' or not review['request_disabled']
        or request['execute'] is not False or request['cloud_parent_packet_read_permitted'] is not False
        or request['completed_run_id']!=40751937917 or result['logical_sha256']!=PARENT
        or sha(SELECTED)!=result['selected_records_sha256'] or sha(SELECTED)!=review['selected_records_sha256']
        or result['publication_resolutions']['onken_1993']['status']!='MISSING'
        or selected['publications']['onken_1993'] or selected['candidate_width_id_matches']
        or source_review['source_facts_sha256']!=sha(FACTS) or not source_review['compact_figure_individually_reviewed']):
        raise ValueError('Exact reviewed source and audited parent required')
    summary=facts['cited_width_summary']
    if (summary['approximate_width_km']!=200 or summary['admitted'] is not False
        or summary['cited_originals_reviewed_here'] is not False or facts['whole_current_length_km'] is not None
        or facts['longitudinal_evidence_support']['current_endpoints_diagnosed'] is not False):
        raise ValueError('Dependent historical regional width scope required')
    width={'schema':'osw.scoped-width-evidence.v1','id':WIDTH_ID,'current_id':CURRENT,'entity_id':OWNER,
        'name':'Azores Countercurrent','status':'source_reported_cited_regional_summary',
        'measurement_type':'published_cited_historical_regional_width','approximate_width_km':200,
        'width_metric':'author_interpreted_historical_regional_width','width_range_km':None,
        'range_interpretation':'One approximate cited regional summary, not seasonal variability or numerical uncertainty. Keep the distinct110km2009 section separate.',
        'geographic_scope':'Western North Atlantic historical sections near50W,45W and41W, discussed as westward flow in the38-40N band. These are not paired width-edge coordinates.',
        'layer':'Fixed width-sampling layer unknown. The paper compares several distinct depth and pressure supports; upper1000dbar comparison context is not a uniform current thickness.',
        'boundary_rule':None,'edge_operator':None,'paired_edge_coordinates':None,'section_geometry':None,
        'observed_period':None,'sampling_dates':None,'calendar_months':None,
        'phase_kind':'historical_regional_section_interpretation','phase_label':'Historical sections reviewed by Onken (1993)',
        'source_id':SOURCE_ID,'source_ids':[SOURCE_ID],'source_file':FACTS,'source_file_sha256':sha(FACTS),
        'source_pointer':'/cited_width_summary','source_url':facts['original_url'],'source_doi':facts['doi'],
        'source_citation':facts['citation'],'source_locator':summary['locator'],
        'source_evidence_kind':'dependent_author_interpretation_of_cited_sections',
        'source_quality_note':'Worthington1962/1976 originals remain unreviewed. Onken states the sections were obtained in different years; dates and a reproducible edge operator remain unresolved.',
        'extraction_method':'Transcribe the author-reported approximate200km summary; no figure coordinates, axes or edges digitized.',
        'source_retrieved_date':'2026-10-28','annual_width_range_km':None,'numerical_width_uncertainty_km':None,
        'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,
        'seasonal_playback_eligible':False,'is_annual_mean':False,'is_climatology':False,
        'independent_new_observation':False,'source_figure_digitized':False,
        'cited_originals':summary['cited_originals'],'cited_originals_reviewed':False}
    citation={'id':SOURCE_ID,'kind':'publication','title':'The Azores Countercurrent','label':'The Azores Countercurrent',
        'authors':['Reiner Onken'],'year':1993,'doi':facts['doi'],'url':facts['original_url'],
        'preferred_citation':facts['citation'],'source_facts_file':FACTS,'source_facts_sha256':sha(FACTS),
        'access_scope':'All nine original pages visually reviewed from public GEOMAR PDF; original not redistributed.',
        'provider_asset_redistributed':False,'used_in_collections':['objects','widths'],
        'scope_note':'Dependent historical regional width interpretation; longitude evidence support is not a physical current length.'}
    old=selected['owner'];owner=copy.deepcopy(old)
    owner['width_ids'].append(WIDTH_ID);owner['capabilities']['scoped_width']+=1
    owner['source_ids']=sorted(set(owner['source_ids'])|{SOURCE_ID});owner['linked_source_count']=len(owner['source_ids'])
    owner['section_fingerprints']['measurements']=fingerprint({'prior_fingerprint':old['section_fingerprints']['measurements'],'added_width':width})
    owner['section_fingerprints']['sources']=fingerprint({'prior_fingerprint':old['section_fingerprints']['sources'],'added_source':citation})
    owner['evidence_links'] += [{'label':'Compare separately scoped historical and2009 width evidence','url':query_url()},
        {'label':'Historical source locations and cited regional width','url':'../figures/onken-azcc-1993-evidence-compact-v1.svg'}]
    owner['fingerprint']=fingerprint({k:v for k,v in owner.items() if k!='fingerprint'})
    before=selected['historical_dashboard_entry'][0];after=copy.deepcopy(before)
    for key in ['width_ids','capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','evidence_links']:
        after[key]=copy.deepcopy(owner[key])
    pins=[FACTS,MODULE,PROTOCOL,SELECTED,REVIEW,parent.REQUEST,'research/azcc-onken-parent-run-v1/result.json',
        'research/azcc-onken-parent-run-v1/run-receipt.json','research/onken-azcc-1993-preparation-review-v1.json',
        'plans/onken-azcc-1993-evidence-protocol-v1.md','figures/onken-azcc-1993-evidence-compact-v1.svg']
    return {'schema':'osw.azcc-onken-query-contract.v1','status':'PREPARED_NOT_COMPILED_OR_INSTALLED',
        'parent_logical_sha256':PARENT,'prior_records':selected,'parent_collection_counts':result['collection_counts'],
        'width_record':width,'new_source':citation,'final_owner':owner,'dashboard_before':before,'dashboard_after':after,
        'input_sha256':{p:sha(p) for p in pins},'new_width_records':1,'new_publication_sources':1,'new_length_records':0,
        'new_width_samples':0,'new_independent_observations':0,'new_physical_footprints':0,
        'expected_totals':{'widths':178,'sources':217,'owners_with_scoped_width_capability':89},
        'width_query_after_installation':query_url()}


def marker(contract):
    return {'schema':'osw.azcc-onken-runtime-receipt.v1','parent_logical_sha256':PARENT,'contract_file':FILE,
        'contract_sha256':fingerprint(contract),'width_records_added':1,'publication_sources_added':1,
        'new_width_samples':0,'new_independent_observations':0,'new_length_records':0}


def prepare(collections,manifest,contract,*,parent_logical_sha256):
    if contract!=build_contract() or parent_logical_sha256!=PARENT or KEY in manifest:
        raise ValueError('Exact unapplied contract and parent required')
    prior=contract['prior_records']
    for name in ['sources','objects','entities','widths','reference_routes']:
        rows=collections.get(name)
        if not isinstance(rows,list) or len(rows)!=contract['parent_collection_counts'][name]:raise ValueError('Parent inventory differs: '+name)
        ids=[r.get('id') for r in rows]
        if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):raise ValueError('Unique row IDs required: '+name)
    for name,key in [('objects','owner'),('entities','entity')]:
        if [r for r in collections[name] if r.get('id')==OWNER]!=[prior[key]]:raise ValueError('Changed audited owner/entity')
    for name in ['widths','reference_routes']:
        if [r for r in collections[name] if r.get('current_id')==CURRENT]!=prior[name]:raise ValueError('Changed prior regional evidence')
    sources=collections['sources'];matched,resolutions=parent.publications(sources)
    if matched['onken_1993'] or resolutions['onken_1993']['status']!='MISSING' or any(r['id']==SOURCE_ID for r in sources):
        raise ValueError('Publication already present; reconcile')
    by_id={r['id']:r for r in sources}
    if any(by_id.get(r['id'])!=r for r in prior['owner_sources']):raise ValueError('Changed owner source')
    if any(r.get('id')==WIDTH_ID for r in collections['widths']):raise ValueError('Existing width ID')
    for path,pin in {**contract['input_sha256'],FILE:fingerprint(contract)}.items():
        if path in manifest.get('input_sha256',{}) and manifest['input_sha256'][path]!=pin:
            raise ValueError('Historical input pin would change: '+path)
    after=dict(collections)
    after['sources']=[*sources,copy.deepcopy(contract['new_source'])]
    after['objects']=[copy.deepcopy(contract['final_owner']) if r['id']==OWNER else r for r in collections['objects']]
    after['widths']=[*collections['widths'],copy.deepcopy(contract['width_record'])]
    updated=dict(manifest);updated['input_sha256']=dict(manifest.get('input_sha256',{}))
    updated['input_sha256'].update(contract['input_sha256']);updated['input_sha256'][FILE]=fingerprint(contract)
    updated[KEY]=marker(contract)
    collections.clear();collections.update(after);manifest.clear();manifest.update(updated)


if __name__=='__main__':
    path=ROOT/FILE
    if path.exists():raise ValueError('Use a new contract version')
    path.write_bytes(encoded(build_contract()))
    print('Frozen one dependent width/one source contract; runtime and installation pending.')
