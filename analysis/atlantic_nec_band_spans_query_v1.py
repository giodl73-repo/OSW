"""Exact-parent additive published-width admission, independent of ocean fields."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
FILE='research/atlantic-nec-stramma-2005-query-contract-v1.json'
PREPARED='research/atlantic-nec-stramma-2005-admission-prepared-v1.json'
AUDIT='research/atlantic-nec-stramma-2005-parent-run-v1/result.json'
KEY='published_atlantic_nec_band_spans_v1'
PARENT='6bbbb4ddcc3f7eb73468a81305b03f30c593c8f004a15b3dd7ad95e312792bac'
OWNERS=('current:atlantic-north-equatorial',)
FAMILY='current:north-equatorial'

def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def owns(row,owner):return row.get('entity_id')==owner or row.get('current_id')==owner.removeprefix('current:')
def query_url(owner):
    request={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':owner.removeprefix('current:')}],'limit':100}
    return 'query.html?q='+quote(json.dumps(request,separators=(',',':')))+'#query-chart-section'

def build_contract():
    prep=read(PREPARED);audit=read(AUDIT)
    selected_path='research/atlantic-nec-stramma-2005-parent-run-v1/selected-records.json'
    selected=read(selected_path);request=read('research/atlantic-nec-stramma-2005-parent-request-v1.json')
    if (prep['exact_parent_audit_sha256']!=sha(AUDIT) or prep['selected_parent_sha256']!=sha(selected_path)
        or audit['logical_sha256']!=PARENT or audit['publication_resolutions']['stramma_2005']['status']!='MISSING'
        or request['execute'] is not False or request['cloud_parent_packet_read_permitted'] is not False
        or request['completed_run_id']!=40977162147 or selected['candidate_width_id_matches']
        or selected['publication_linked_width_records']):raise ValueError('Exact completed parent review required')
    widths=copy.deepcopy(prep['width_records']);source=copy.deepcopy(prep['source_record'])
    if len(widths)!=2 or len({r['id'] for r in widths})!=2:raise ValueError('Two unique regional spans required')
    for row,bounds,kind in zip(widths,([16,22],[14,20]),('published_shipboard_ADCP_band_extent','published_FLAME_model_band_extent')):
        if (row['source_reported_latitude_bounds_deg_north']!=bounds or row['source_evidence_kind']!=kind
            or row['approximate_width_km']!=700 or row['boundary_rule'] is not None
            or row['section_geometry'] is not None or row['annual_width_range_km'] is not None
            or row['numerical_width_uncertainty_km'] is not None or row['whole_current_representative'] is not False
            or row['seasonal_playback_eligible'] is not False or row['width_rank_eligible'] is not False):
            raise ValueError('Published regional band scope changed')
    prior={owner:{'objects':[r['object']],'entities':[r['entity']],'widths':r['widths']} for owner,r in selected['identities'].items()}
    final={}
    for owner in OWNERS:
        old=prior[owner]['objects'][0];value=copy.deepcopy(old)
        additions=[r for r in widths if owns(r,owner)]
        value['width_ids']=[*old['width_ids'],*[r['id'] for r in additions]]
        value['capabilities']['scoped_width']+=len(additions)
        value['source_ids']=sorted(set(old['source_ids'])|{source['id']})
        value['linked_source_count']=len(value['source_ids'])
        if additions:value['section_fingerprints']['measurements']=digest({'prior_fingerprint':old['section_fingerprints']['measurements'],'added_widths':additions})
        value['section_fingerprints']['sources']=digest({'prior_fingerprint':old['section_fingerprints']['sources'],'added_source':source})
        value['evidence_links']=[*old['evidence_links'],{'label':'Published regional band spans and original source','url':query_url(owner)}]
        value['fingerprint']=digest({k:v for k,v in value.items() if k!='fingerprint'})
        final[owner]=value
    source_rows={r['id']:r for v in selected['identities'].values() for r in v['owner_sources']}
    inputs=[PREPARED,AUDIT,selected_path,'research/atlantic-nec-stramma-2005-parent-execution-review-v1.json',
        'research/atlantic-nec-stramma-2005-parent-request-v1.json','research/atlantic-nec-stramma-2005-source-facts-v2.json',
        'analysis/atlantic_nec_band_spans_query_v1.py','figures/atlantic-nec-stramma-2005-band-spans-prepared-v2.svg']
    return {'schema':'osw.atlantic-nec-band-spans-query-contract.v1','parent_logical_sha256':PARENT,
        'parent_collection_counts':audit['collection_counts'],'prior_source_inventory':list(source_rows.values()),
        'prior_source_inventory_scope':'owner_and_family_linked_sources_only_all_other_rows_preserved',
        'prior_owners':prior,'final_objects':final,'width_records':widths,'new_source':source,
        'citation_owner_ids':list(OWNERS),'family':FAMILY,'input_sha256':{p:sha(p) for p in inputs},
        'width_records_added':2,'sources_added':1,'width_samples_added':0,'lengths_added':0,
        'annual_ranges_added':0,'physical_geometries_added':0,'independent_observations_added':0,'installed':False}


def marker(contract,pin):
    return {'schema':'osw.atlantic-nec-band-spans-runtime.v1','parent_logical_sha256':PARENT,
        'contract_file':FILE,'contract_sha256':pin,'width_records_added':2,'sources_added':1,
        'width_samples_added':0,'lengths_added':0,'annual_ranges_added':0,'physical_geometries_added':0,
        'independent_observations_added':0}

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
    print('Frozen two regional spans, one publication and one object projection; delivery pending.')
