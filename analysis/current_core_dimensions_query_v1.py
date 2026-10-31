"""Add one regional reach and one cited width to the exact audited parent."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import current_core_gap_followup_prepare_v1 as science

ROOT=Path(__file__).resolve().parents[1]
FILE='research/current-core-dimensions-query-contract-v1.json'
PREPARED=science.PREPARED
AUDIT=science.PARENT+'/result.json'
KEY='published_current_core_dimensions_v1'
PARENT=science.LOGICAL
REACHES='current_regional_reaches'
OWNERS=('current:red-sea-saline-overflow','current:indian-south-equatorial')

def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def owns(row,owner):return row.get('entity_id')==owner or row.get('current_id')==owner.removeprefix('current:')
def query_url(owner,collection):
    request={'collection':collection,'filters':[{'field':'current_id','op':'eq','value':owner.removeprefix('current:')}],'limit':100}
    return 'query.html?q='+quote(json.dumps(request,separators=(',',':')))+'#query-chart-section'

def build_contract():
    prep=read(PREPARED)
    if prep!=science.prepare():raise ValueError('Exact source-scoped scientific preparation required')
    audit=read(AUDIT);selected=read(science.PARENT+'/selected-records.json')
    request=read('research/current-core-gap-followup-parent-request-v1.json')
    if request['execute'] is not False or request['cloud_parent_packet_read_permitted'] is not False or request['completed_run_id']!=41039800756:raise ValueError('Completed disabled parent audit required')
    reaches=copy.deepcopy(prep['regional_length_records']);widths=copy.deepcopy(prep['width_claim_records'])
    for row in reaches+widths:
        row.update(source_ids=[row['source_id']],source_file_sha256=sha(row['source_file']),figure=science.FIGURE)
    reaches[0].update(phase_label='Northern Channel summer plume | 2001 campaign',
        source_evidence_kind='published_original_reviewed_regional_plume_reach',
        source_quality_note='Source-reported nonsynoptic summer extent; exact occupation dates and paired endpoint coordinates unknown.')
    widths[0].update(phase_label='Upstream Indian SEC | literature-cited estimate',
        range_interpretation='Approximate regional width cited in a 2008 report, not a new measurement. Original methods, dates, numerical error and annual range remain unknown.',
        vertical_scope='Width sampling layer: Unknown. The nearby current-depth description is not the width layer.',
        source_quality_note='New et al. (2007) is a provisional attribution; the report bibliography omits that work and its full original has not been reviewed.')
    sources=copy.deepcopy(prep['publication_records'])
    for row in sources:row.update(source_facts_file=science.PETERS if row['id']==science.PETERS_SOURCE else science.ASCLME,source_facts_sha256=sha(science.PETERS if row['id']==science.PETERS_SOURCE else science.ASCLME))
    prior={};final={}
    for owner in OWNERS:
        evidence=selected['identities'][owner]
        if evidence['widths'] or REACHES in evidence['linked_inventory']:raise ValueError('Reconcile prior owner dimensions before append')
        prior[owner]={'objects':[evidence['object']],'entities':[evidence['entity']],'widths':[],'current_regional_reaches':[]}
        old=evidence['object'];value=copy.deepcopy(old)
        added_widths=[r for r in widths if owns(r,owner)];added_reaches=[r for r in reaches if owns(r,owner)]
        ids={r['source_id'] for r in added_widths+added_reaches}
        if added_widths:
            value['width_ids']+= [r['id'] for r in added_widths];value['capabilities']['scoped_width']+=len(added_widths)
        if added_reaches:
            value['regional_reach_ids']=[*old.get('regional_reach_ids',[]),*[r['id'] for r in added_reaches]]
            value['capabilities']['reported_regional_reaches']=old['capabilities'].get('reported_regional_reaches',0)+len(added_reaches)
        value['source_ids']=sorted(set(old['source_ids'])|ids);value['linked_source_count']=len(value['source_ids'])
        value['section_fingerprints']['measurements']=digest({'prior_fingerprint':old['section_fingerprints']['measurements'],'added_widths':added_widths,'added_reaches':added_reaches})
        value['section_fingerprints']['sources']=digest({'prior_fingerprint':old['section_fingerprints']['sources'],'added_sources':[r for r in sources if r['id'] in ids]})
        collection=REACHES if added_reaches else 'widths'
        value['evidence_links']=[*old['evidence_links'],{'label':'Reported summer plume reach and source limits' if added_reaches else 'Cited upstream width and attribution limits','url':query_url(owner,collection)}]
        value['fingerprint']=digest({k:v for k,v in value.items() if k!='fingerprint'});final[owner]=value
    source_rows={r['id']:r for owner in OWNERS for r in selected['identities'][owner]['owner_sources']}
    inputs=[PREPARED,AUDIT,science.PARENT+'/selected-records.json',science.PARENT+'/run-receipt.json',
        'research/current-core-gap-followup-parent-execution-review-v1.json','research/current-core-gap-followup-parent-request-v1.json',
        science.PETERS,science.ASCLME,science.NILSEN,science.FIGURE,'analysis/current_core_gap_followup_prepare_v1.py','analysis/current_core_dimensions_query_v1.py']
    return {'schema':'osw.current-core-dimensions-query-contract.v1','parent_logical_sha256':PARENT,
        'parent_collection_counts':audit['collection_counts'],'prior_source_inventory':list(source_rows.values()),
        'prior_owners':prior,'final_objects':final,'width_records':widths,'reach_records':reaches,'new_sources':sources,
        'citation_owner_ids':list(OWNERS),'input_sha256':{p:sha(p) for p in inputs},
        'width_records_added':1,'regional_reaches_added':1,'sources_added':2,'whole_current_lengths_added':0,
        'annual_ranges_added':0,'physical_geometries_added':0,'independent_observations_added':0,'installed':False}

def marker(contract,pin):
    return {'schema':'osw.current-core-dimensions-runtime.v1','parent_logical_sha256':PARENT,'contract_file':FILE,'contract_sha256':pin,
        'width_records_added':1,'regional_reaches_added':1,'sources_added':2,'whole_current_lengths_added':0,
        'annual_ranges_added':0,'physical_geometries_added':0,'independent_observations_added':0}

def apply_verified(collections,manifest,contract,*,parent_logical_sha256,contract_sha256):
    if parent_logical_sha256!=PARENT or contract['parent_logical_sha256']!=PARENT or KEY in manifest:raise ValueError('Exact unapplied parent required')
    counts=contract['parent_collection_counts']
    if set(collections)!=set(counts) or any(not isinstance(collections[n],list) or len(collections[n])!=c for n,c in counts.items()):raise ValueError('Complete parent collection counts required')
    for row in contract['prior_source_inventory']:
        if [r for r in collections['sources'] if r.get('id')==row['id']]!=[row]:raise ValueError('Prior source changed')
    for owner,prior in contract['prior_owners'].items():
        for name in ('objects','entities'):
            if [r for r in collections[name] if r.get('id')==owner]!=prior[name]:raise ValueError('Prior identity changed')
        for name in ('widths',REACHES):
            if [r for r in collections[name] if owns(r,owner)]!=prior[name]:raise ValueError('Prior scoped dimension changed')
    new_ids={r['id'] for key in ['width_records','reach_records','new_sources'] for r in contract[key]}
    if len(new_ids)!=4 or any(r.get('id') in new_ids for rows in collections.values() for r in rows):raise ValueError('Candidate ID collision')
    pins={**contract['input_sha256'],FILE:contract_sha256}
    if any(p in manifest.get('input_sha256',{}) and manifest['input_sha256'][p]!=h for p,h in pins.items()):raise ValueError('Historical input pin would change')
    after=dict(collections)
    for name,key in [('sources','new_sources'),('widths','width_records'),(REACHES,'reach_records')]:after[name]=[*collections[name],*copy.deepcopy(contract[key])]
    after['objects']=[copy.deepcopy(contract['final_objects'].get(r['id'],r)) for r in collections['objects']]
    updated=copy.deepcopy(manifest);updated['input_sha256']={**manifest.get('input_sha256',{}),**pins};updated[KEY]=marker(contract,contract_sha256)
    return after,updated

def prepare(collections,manifest,contract,*,parent_logical_sha256):
    expected=build_contract();raw=encoded(expected)
    if encoded(contract)!=raw or (ROOT/FILE).read_bytes()!=raw:raise ValueError('Exact frozen contract required')
    return apply_verified(collections,manifest,contract,parent_logical_sha256=parent_logical_sha256,contract_sha256=hashlib.sha256(raw).hexdigest())

if __name__=='__main__':
    target=ROOT/FILE
    if target.exists():raise ValueError('Use a new contract version')
    target.write_bytes(encoded(build_contract()));print('Frozen one scoped reach, one cited width, two publications and two owner projections.')
