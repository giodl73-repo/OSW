"""Exact-parent additive published-width admission, independent of ocean fields."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
FILE='research/richardson-walsh-1986-characteristic-velocity-query-contract-v1.json'
PREPARED='research/richardson-walsh-1986-characteristic-velocity-admission-prepared-v1.json'
AUDIT='research/richardson-walsh-1986-characteristic-velocity-parent-run-v1/result.json'
KEY='published_characteristic_velocities_v1'
PARENT='404de2dee8ca4fc4968f24a23f892b336bd5392d8b44a3556206a8944e2b2e3a'
COLLECTION='current_characteristic_velocities'
OWNERS=tuple('current:'+v for v in ['caribbean','guiana','north-brazil','brazil','guinea','atlantic-north-equatorial','atlantic-north-equatorial-countercurrent','atlantic-south-equatorial'])
FAMILIES=('current:north-equatorial','current:south-equatorial')

def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def owns(row,owner):return row.get('entity_id')==owner or row.get('current_id')==owner.removeprefix('current:')
def query_url(owner):
    request={'collection':COLLECTION,'filters':[{'field':'current_id','op':'eq','value':owner.removeprefix('current:')}],'limit':100}
    return 'query.html?q='+quote(json.dumps(request,separators=(',',':')))+'#query-chart-section'

def build_contract():
    prep=read(PREPARED);audit=read(AUDIT)
    selected_path='research/richardson-walsh-1986-characteristic-velocity-parent-run-v1/selected-records.json'
    selected=read(selected_path);request=read('research/richardson-walsh-1986-characteristic-velocity-parent-request-v1.json')
    if (prep['audit_sha256']!=sha(AUDIT) or prep['selected_parent_sha256']!=sha(selected_path)
        or audit['logical_sha256']!=PARENT or audit['publication_resolutions']['richardson_walsh_1986']['status']!='MISSING'
        or request['execute'] is not False or request['cloud_parent_packet_read_permitted'] is not False
        or request['completed_run_id']!=40996133038 or selected['candidate_record_id_matches']
        or selected['publication_linked_measurement_records']):raise ValueError('Exact completed parent review required')
    records=copy.deepcopy(prep['new_records']);source=copy.deepcopy(prep['new_source_record'])
    if len(records)!=10 or len({r['id'] for r in records})!=10 or {r['entity_id'] for r in records}!=set(OWNERS):raise ValueError('Ten unique summaries across eight exact owners required')
    from richardson_walsh_1986_characteristic_velocities_v1 import prepare as scientific
    checked=scientific(read('research/richardson-walsh-1986-characteristic-velocity-source-facts-v1.json'))['records']
    for row,expected in zip(records,checked):
        allowed=set(expected)|{'source_id','source_ids','source_file_sha256','figure','potential_observation_overlap_note'}
        if set(row)!=allowed or any(row.get(k)!=v for k,v in expected.items()):raise ValueError('Scientific quantity, operator or source scope changed')
    prior={owner:{'objects':[r['object']],'entities':[r['entity']],'widths':r['widths']} for owner,r in selected['identities'].items()}
    final={}
    for owner in OWNERS:
        old=prior[owner]['objects'][0];value=copy.deepcopy(old)
        additions=[r for r in records if owns(r,owner)]
        value['characteristic_velocity_ids']=[r['id'] for r in additions]
        value['capabilities']['characteristic_velocity']=len(additions)
        value['source_ids']=sorted(set(old['source_ids'])|{source['id']})
        value['linked_source_count']=len(value['source_ids'])
        if additions:value['section_fingerprints']['measurements']=digest({'prior_fingerprint':old['section_fingerprints']['measurements'],'added_characteristic_velocities':additions})
        value['section_fingerprints']['sources']=digest({'prior_fingerprint':old['section_fingerprints']['sources'],'added_source':source})
        value['evidence_links']=[*old['evidence_links'],{'label':'Characteristic velocity summaries and original source','url':query_url(owner)}]
        value['fingerprint']=digest({k:v for k,v in value.items() if k!='fingerprint'})
        final[owner]=value
    source_rows={r['id']:r for v in selected['identities'].values() for r in v['owner_sources']}
    inputs=[PREPARED,AUDIT,selected_path,'research/richardson-walsh-1986-characteristic-velocity-parent-execution-review-v1.json',
        'research/richardson-walsh-1986-characteristic-velocity-parent-request-v1.json',
        'research/richardson-walsh-1986-characteristic-velocity-source-facts-v1.json',
        'analysis/richardson_walsh_1986_characteristic_velocities_v1.py',
        'analysis/characteristic_velocities_query_v1.py','figures/richardson-walsh-1986-characteristic-velocities-v1.svg']
    return {'schema':'osw.characteristic-velocities-query-contract.v1','parent_logical_sha256':PARENT,
        'parent_collection_counts':audit['collection_counts'],'prior_source_inventory':list(source_rows.values()),
        'prior_source_inventory_scope':'owner_and_family_linked_sources_only_all_other_rows_preserved',
        'prior_owners':prior,'final_objects':final,'records':records,'new_source':source,
        'citation_owner_ids':list(OWNERS),'families':list(FAMILIES),'collection':COLLECTION,
        'input_sha256':{p:sha(p) for p in inputs},'records_added':10,'sources_added':1,
        'collections_added':1,'width_samples_added':0,'lengths_added':0,'widths_added':0,
        'annual_ranges_added':0,'physical_geometries_added':0,'independent_observations_added':0,'installed':False}


def marker(contract,pin):
    return {'schema':'osw.characteristic-velocities-runtime.v1','parent_logical_sha256':PARENT,
        'contract_file':FILE,'contract_sha256':pin,'collection':COLLECTION,'records_added':10,
        'sources_added':1,'collections_added':1,'lengths_added':0,'widths_added':0,
        'annual_ranges_added':0,'physical_geometries_added':0,'independent_observations_added':0}


def apply_verified(collections,manifest,contract,*,parent_logical_sha256,contract_sha256):
    if parent_logical_sha256!=PARENT or contract['parent_logical_sha256']!=PARENT or KEY in manifest:
        raise ValueError('Exact unapplied parent required')
    counts=contract['parent_collection_counts']
    if set(collections)!=set(counts) or any(not isinstance(collections[n],list) or len(collections[n])!=c for n,c in counts.items()):
        raise ValueError('Complete parent collection counts required')
    for row in contract['prior_source_inventory']:
        if [r for r in collections['sources'] if r.get('id')==row['id']]!=[row]:raise ValueError('Prior owner source changed')
    for owner,prior in contract['prior_owners'].items():
        for name in ('objects','entities'):
            if [r for r in collections[name] if r.get('id')==owner]!=prior[name]:raise ValueError('Owner/family identity changed')
        if [r for r in collections['widths'] if owns(r,owner)]!=prior['widths']:raise ValueError('Prior widths changed')
    if COLLECTION in collections:raise ValueError('Characteristic collection already present')
    additions=contract['records'];new_ids={r['id'] for r in additions}|{contract['new_source']['id']}
    if any(r.get('id') in new_ids for rows in collections.values() for r in rows):raise ValueError('New ID collision')
    pins={**contract['input_sha256'],FILE:contract_sha256}
    if any(p in manifest.get('input_sha256',{}) and manifest['input_sha256'][p]!=h for p,h in pins.items()):
        raise ValueError('Historical input pin would change')
    after=dict(collections)
    after['sources']=[*collections['sources'],copy.deepcopy(contract['new_source'])]
    after[COLLECTION]=copy.deepcopy(additions)
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
    print('Frozen ten characteristic summaries, one publication and eight object projections; delivery pending.')
