"""Exact-parent additive published-width admission, independent of ocean fields."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
FILE='research/dimoune-2023-width-query-contract-v1.json'
PREPARED='research/dimoune-2023-section-width-admission-prepared-v1.json'
AUDIT='research/dimoune-2023-width-parent-run-v1/audit.json'
KEY='published_dimoune_2023_section_widths_v1'
PARENT='dc671a2af236089e37c02489e0cba6bea52e81298879abf0ea809f8d9552a936'
OWNERS=('current:north-brazil','current:guiana','current:atlantic-north-equatorial-countercurrent','current:atlantic-south-equatorial')

def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def owns(row,owner):return row.get('entity_id')==owner or row.get('current_id')==owner.removeprefix('current:')
def query_url(owner):
    request={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':owner.removeprefix('current:')}],'limit':100}
    return 'query.html?q='+quote(json.dumps(request,separators=(',',':')))+'#query-chart-section'

def build_contract():
    prep=read(PREPARED);audit=read(AUDIT);review=read('research/dimoune-2023-width-parent-execution-review-v1.json')
    request=read('research/dimoune-2023-width-parent-request-v1.json')
    if (prep['exact_parent_audit_sha256']!=sha(AUDIT) or review['audit_sha256']!=sha(AUDIT)
        or audit['parent_logical_sha256']!=PARENT or audit['publication_resolution']!='MISSING'
        or request['execute'] is not False or request['cloud_parent_packet_read_permitted'] is not False
        or request['completed_run_id']!=40925528451):raise ValueError('Exact completed parent review required')
    widths=copy.deepcopy(prep['new_width_records']);source=copy.deepcopy(prep['new_source_record'])
    source.update(kind='publication',year=2023,used_in_collections=['objects','widths'],
        source_facts_file='research/dimoune-2023-section-width-records-prepared-v1.json',
        source_facts_sha256=sha('research/dimoune-2023-section-width-records-prepared-v1.json'))
    if len(widths)!=6 or len({r['id'] for r in widths})!=6:raise ValueError('Six unique widths required')
    final={}
    for owner in OWNERS:
        old=audit['owners'][owner]['objects'][0];value=copy.deepcopy(old)
        additions=[r for r in widths if owns(r,owner)]
        value['width_ids']=[*old['width_ids'],*[r['id'] for r in additions]]
        value['capabilities']['scoped_width']+=len(additions)
        value['source_ids']=sorted(set(old['source_ids'])|{source['id']})
        value['linked_source_count']=len(value['source_ids'])
        if additions:value['section_fingerprints']['measurements']=digest({'prior_fingerprint':old['section_fingerprints']['measurements'],'added_widths':additions})
        value['section_fingerprints']['sources']=digest({'prior_fingerprint':old['section_fingerprints']['sources'],'added_source':source})
        value['evidence_links']=[*old['evidence_links'],{'label':'Published mean section widths and original source','url':query_url(owner)}]
        value['fingerprint']=digest({k:v for k,v in value.items() if k!='fingerprint'})
        final[owner]=value
    inputs=[PREPARED,AUDIT,'research/dimoune-2023-width-parent-execution-review-v1.json',
        'research/dimoune-2023-width-parent-request-v1.json','research/dimoune-2023-section-width-records-prepared-v1.json',
        'analysis/dimoune_2023_width_query_v1.py','plans/dimoune-2023-width-delivery-v1.md',
        'figures/dimoune-2023-section-widths-source-review-v1.svg']
    return {'schema':'osw.dimoune-2023-width-query-contract.v1','parent_logical_sha256':PARENT,
        'parent_collection_counts':audit['collection_counts'],'prior_source_inventory':audit['source_inventory'],
        'prior_owners':audit['owners'],'final_objects':final,'width_records':widths,'new_source':source,
        'citation_owner_ids':list(OWNERS),'family':'current:south-equatorial',
        'input_sha256':{p:sha(p) for p in inputs},'width_records_added':6,'sources_added':1,
        'width_samples_added':0,'lengths_added':0,'annual_ranges_added':0,'physical_geometries_added':0,
        'independent_observations_added':0,'installed':False}

def marker(contract,pin):
    return {'schema':'osw.dimoune-2023-width-runtime.v1','parent_logical_sha256':PARENT,
        'contract_file':FILE,'contract_sha256':pin,'width_records_added':6,'sources_added':1,
        'width_samples_added':0,'lengths_added':0,'annual_ranges_added':0,'physical_geometries_added':0,
        'independent_observations_added':0}

def apply_verified(collections,manifest,contract,*,parent_logical_sha256,contract_sha256):
    if parent_logical_sha256!=PARENT or contract['parent_logical_sha256']!=PARENT or KEY in manifest:
        raise ValueError('Exact unapplied parent required')
    counts=contract['parent_collection_counts']
    if set(collections)!=set(counts) or any(not isinstance(collections[n],list) or len(collections[n])!=c for n,c in counts.items()):
        raise ValueError('Complete parent collection counts required')
    if collections['sources']!=contract['prior_source_inventory']:raise ValueError('Prior source inventory changed')
    for owner,prior in contract['prior_owners'].items():
        for name in ('objects','entities'):
            if [r for r in collections[name] if r.get('id')==owner]!=prior[name]:raise ValueError('Owner/family identity changed')
        if [r for r in collections['widths'] if owns(r,owner)]!=prior['widths']:raise ValueError('Prior widths changed')
    additions=contract['width_records'];new_ids={r['id'] for r in additions}|{contract['new_source']['id']}
    if any(r.get('id') in new_ids for rows in collections.values() for r in rows):raise ValueError('New ID collision')
    pins={**contract['input_sha256'],FILE:contract_sha256}
    if any(p in manifest.get('input_sha256',{}) and manifest['input_sha256'][p]!=h for p,h in pins.items()):
        raise ValueError('Historical input pin would change')
    after=dict(collections)
    after['sources']=[*collections['sources'],copy.deepcopy(contract['new_source'])]
    after['widths']=[*collections['widths'],*copy.deepcopy(additions)]
    after['objects']=[copy.deepcopy(contract['final_objects'].get(r['id'],r)) for r in collections['objects']]
    updated=copy.deepcopy(manifest);updated['input_sha256']={**manifest.get('input_sha256',{}),**pins}
    updated[KEY]=marker(contract,contract_sha256)
    return after,updated

def prepare(collections,manifest,contract,*,parent_logical_sha256):
    expected=build_contract();raw=encoded(expected)
    if encoded(contract)!=raw or (ROOT/FILE).read_bytes()!=raw:raise ValueError('Exact frozen contract required')
    return apply_verified(collections,manifest,contract,parent_logical_sha256=parent_logical_sha256,
                          contract_sha256=hashlib.sha256(raw).hexdigest())

if __name__=='__main__':
    target=ROOT/FILE
    if target.exists():raise ValueError('Use a new contract version')
    target.write_bytes(encoded(build_contract()))
    print('Frozen six regional widths, one publication and four object projections; delivery pending.')
