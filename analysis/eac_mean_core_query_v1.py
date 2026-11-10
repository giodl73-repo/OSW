"""Bounded source contract for regional mean-model sections; no installed reads."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import check_eac_mean_core_parent_v1 as parent
import eac_kerry_2020_mean_core_v2 as facts

ROOT=Path(__file__).resolve().parents[1]
PARENT=parent.LOGICAL
OWNER='current:east-australian'
CURRENT='east-australian'
COLLECTION='current_mean_core_sections'
SOURCE_ID='source:eac-kerry-2020-mean-core'
FILE='research/eac-mean-core-query-contract-v1.json'
KEY='published_eac_mean_core_sections_v1'
MODULE='analysis/eac_mean_core_query_v1.py'
PROTOCOL='plans/eac-mean-core-query-contract-v1.md'
SELECTED='research/eac-mean-core-parent-run-v1/selected-records.json'
REVIEW='research/eac-mean-core-parent-execution-review-v1.json'

def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def fingerprint(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def query_url():
    q={'collection':COLLECTION,'filters':[{'field':'current_id','op':'eq','value':CURRENT}],
       'sort':{'field':'latitude_degrees_north','direction':'desc'},'limit':100}
    return 'query.html?q='+quote(json.dumps(q,separators=(',',':')))+'#query-chart-section'

def build_contract():
    review=read(REVIEW);selected=read(SELECTED);result=read('research/eac-mean-core-parent-run-v1/result.json')
    doc=read(facts.FACTS)
    if (review['status']!='PASS_SOURCE_BOUND_PARENT_SELECTION_REQUEST_DISABLED' or review['request_disabled'] is not True
        or result['logical_sha256']!=PARENT or sha(SELECTED)!=result['selected_records_sha256']
        or result['publication_resolutions']['kerry_2020']['status']!='MISSING'
        or doc!=facts.build()):raise ValueError('Exact audited parent and prepared source facts required')
    if selected['owner'].get('mean_core_section_ids') is not None:raise ValueError('Existing core-section join needs reconciliation')
    rows=[]
    for i,source in enumerate(doc['records']):
        row=copy.deepcopy(source)
        row.update(entity_id=OWNER,current_id=CURRENT,
            label=f'EAC system / {source["place"]} / {abs(source["latitude_degrees_north"]):g} S / mean model core',
            association_kind='source_defined_regional_system_context',
            parent_attribution_status='source_components_retained_no_uniform_parent_dimension_inheritance',
            source_id=SOURCE_ID,source_ids=[SOURCE_ID],source_file=facts.FACTS,source_file_sha256=sha(facts.FACTS),
            source_pointer=f'/records/{i}',source_doi=doc['source']['doi'],
            source_url=doc['source']['url'],status='source_reported_model_mean_core_geometry',
            fixed_depth_width_km=None,paired_edge_width_km=None,uniform_current_thickness_m=None,
            new_width_record_admitted=False,new_length_record_admitted=False,rank_eligible=False)
        rows.append(row)
    citation={'id':SOURCE_ID,'kind':'publication','title':parent.PAPERS['kerry_2020']['title'],
        'doi':'10.1029/2019JC015227','year':2020,'url':doc['source']['url'],
        'access_scope':'institutional_original_selected_pages_visually_reviewed',
        'source_original_sha256':doc['source']['original_sha256'],
        'rights_status':'Copyright2020 American Geophysical Union; original/page images not redistributed.',
        'used_in_collections':[COLLECTION,'objects']}
    owner=copy.deepcopy(selected['owner'])
    owner['mean_core_section_ids']=[r['id'] for r in rows]
    owner['capabilities']['reported_model_core_sections']=len(rows)
    owner['source_ids']=sorted(set(owner['source_ids'])|{SOURCE_ID});owner['linked_source_count']=len(owner['source_ids'])
    owner['section_fingerprints']['mean_model_core_sections']=fingerprint(rows)
    owner['section_fingerprints']['sources']=fingerprint({'prior_fingerprint':selected['owner']['section_fingerprints']['sources'],'added_source':citation})
    link={'label':'Compare five published mean-model core sections: offshore extent, depth and area','url':query_url()}
    owner['evidence_links'].append(link)
    owner['fingerprint']=fingerprint({k:v for k,v in owner.items() if k!='fingerprint'})
    before=selected['historical_dashboard_entry'][0];after=copy.deepcopy(before)
    for key in ['capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','mean_core_section_ids','evidence_links']:
        after[key]=copy.deepcopy(owner[key])
    pins=[facts.FACTS,facts.FILE,'analysis/eac_kerry_2020_mean_core_v1.py',facts.base.INPUT,facts.base.PROTOCOL,
          MODULE,PROTOCOL,SELECTED,REVIEW,'research/eac-mean-core-parent-run-v1/result.json',
          'research/eac-mean-core-parent-run-v1/run-receipt.json','research/eac-kerry-2020-mean-core-preparation-review-v1.json']
    return {'schema':'osw.eac-mean-core-query-contract.v1','status':'PREPARED_NOT_COMPILED_OR_INSTALLED',
        'parent_logical_sha256':PARENT,'prior_records':selected,'parent_collection_counts':result['collection_counts'],
        'collection':COLLECTION,'records':rows,'new_source':citation,'final_owner':owner,
        'dashboard_before':before,'dashboard_after':after,'query_url_after_installation':query_url(),
        'input_sha256':{p:sha(p) for p in pins},'new_reported_model_section_records':5,'new_publication_sources':1,
        'new_width_records':0,'new_length_records':0,'new_independent_observations':0,'new_physical_footprints':0}

def marker(contract):
    return {'schema':'osw.eac-mean-core-runtime-receipt.v1','parent_logical_sha256':PARENT,
        'contract_file':FILE,'contract_sha256':fingerprint(contract),'records_added':5,'publication_sources_added':1,
        'new_width_records':0,'new_length_records':0,'new_independent_observations':0}

def prepare(collections,manifest,contract,*,parent_logical_sha256):
    if contract!=build_contract() or parent_logical_sha256!=PARENT or KEY in manifest or COLLECTION in collections:
        raise ValueError('Exact unapplied contract and installed parent required')
    prior=contract['prior_records']
    for name in ['sources','objects','entities','widths','reference_routes']:
        rows=collections.get(name)
        if not isinstance(rows,list) or len(rows)!=contract['parent_collection_counts'][name]:raise ValueError('Parent inventory differs: '+name)
    for name,key in [('objects','owner'),('entities','entity')]:
        if [r for r in collections[name] if r.get('id')==OWNER]!=[prior[key]]:raise ValueError('Audited owner/entity differs')
    for name in ['widths','reference_routes']:
        if [r for r in collections[name] if r.get('current_id')==CURRENT]!=prior[name]:raise ValueError('Prior EAC evidence differs: '+name)
    sources=collections['sources'];matched,resolutions=parent.publications(sources)
    if matched['kerry_2020'] or resolutions['kerry_2020']['status']!='MISSING' or any(r['id']==SOURCE_ID for r in sources):
        raise ValueError('Publication already present; reconcile before appending')
    by_id={r['id']:r for r in sources}
    for source in prior['owner_sources']:
        if by_id.get(source['id'])!=source:raise ValueError('Prior EAC source differs')
    after=dict(collections)
    after['sources']=[*sources,copy.deepcopy(contract['new_source'])]
    after['objects']=[copy.deepcopy(contract['final_owner']) if r['id']==OWNER else r for r in collections['objects']]
    after[COLLECTION]=copy.deepcopy(contract['records'])
    updated=dict(manifest);updated['input_sha256']=dict(manifest.get('input_sha256',{}))
    updated['input_sha256'].update(contract['input_sha256']);updated['input_sha256'][FILE]=fingerprint(contract)
    updated[KEY]=marker(contract)
    collections.clear();collections.update(after);manifest.clear();manifest.update(updated)

if __name__=='__main__':
    target=ROOT/FILE
    if target.exists():raise ValueError('Contracts are frozen; use a new version')
    target.write_bytes(encoded(build_contract()));print('Prepared five-row source-bound query contract; Rust/UI integration and installation pending')
