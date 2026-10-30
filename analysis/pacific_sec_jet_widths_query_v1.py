"""Exact-parent additive published-width admission, independent of ocean fields."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
FILE='research/pacific-sec-gourdeau-2008-query-contract-v1.json'
PREPARED='research/pacific-sec-gourdeau-2008-admission-prepared-v1.json'
AUDIT='research/pacific-sec-gourdeau-2008-parent-run-v1/result.json'
KEY='published_pacific_sec_jet_widths_v1'
PARENT='d21ade39ba095192df3f4c6adef702d0d5f68570ea736f455eaf84980d9800ea'
OWNERS=('current:pacific-south-equatorial',)
FAMILY='current:south-equatorial'

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
    selected_path='research/pacific-sec-gourdeau-2008-parent-run-v1/selected-records.json'
    selected=read(selected_path);request=read('research/pacific-sec-gourdeau-2008-parent-request-v1.json')
    if (prep['exact_parent_audit_sha256']!=sha(AUDIT) or prep['selected_parent_sha256']!=sha(selected_path)
        or audit['logical_sha256']!=PARENT or audit['publication_resolutions']['gourdeau_2008']['status']!='MISSING'
        or request['execute'] is not False or request['cloud_parent_packet_read_permitted'] is not False
        or request['completed_run_id']!=41020672610 or selected['candidate_record_id_matches']
        or selected['publication_linked_measurement_records']):raise ValueError('Exact completed parent review required')
    widths=copy.deepcopy(prep['width_records']);source=copy.deepcopy(prep['source_record'])
    import pacific_sec_gourdeau_2008_widths_v1 as science
    expected=science.prepare()['width_records']
    if source['id']!='source:gourdeau-2008-coral-sea-jets' or source['doi']!='10.1175/2007JPO3780.1' or source['source_facts_sha256']!=sha(science.FACTS) or source['source_pdf_sha256']!=science.PDF_SHA:
        raise ValueError('Reviewed primary publication required')
    for row in expected:
        row.update(source_id=source['id'],source_ids=[source['id']],source_file_sha256=sha(science.FACTS),figure=science.FIGURE,
            phase_label=row['component_label']+' | July-October 2005 campaign',source_evidence_kind='published_glider_campaign_component_width',
            vertical_scope=row['layer_note'],range_interpretation='Reported width of this regional jet; the two jet widths are not seasonal bounds or uncertainty.',
            source_quality_note='Nonsynoptic campaign; individual crossing dates and exact numerical edge threshold unspecified.')
    if widths!=expected or selected['candidate_related_source_records'] or selected['candidate_related_width_records']:
        raise ValueError('Exact two component widths and reconciled source scope required')
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
        value['evidence_links']=[*old['evidence_links'],{'label':'Published regional jet widths and original source','url':query_url(owner)}]
        value['fingerprint']=digest({k:v for k,v in value.items() if k!='fingerprint'})
        final[owner]=value
    source_rows={r['id']:r for v in selected['identities'].values() for r in v['owner_sources']}
    inputs=[PREPARED,AUDIT,selected_path,'research/pacific-sec-gourdeau-2008-parent-execution-review-v1.json',
        'research/pacific-sec-gourdeau-2008-parent-request-v1.json','research/pacific-sec-gourdeau-2008-width-source-facts-v1.json',
        'analysis/pacific_sec_jet_widths_query_v1.py','figures/pacific-sec-gourdeau-2008-regional-widths-v1.svg',
        'analysis/pacific_sec_gourdeau_2008_widths_v1.py','research/pacific-sec-gourdeau-2008-widths-prepared-v1.json',
        'research/pacific-sec-gourdeau-2008-width-preparation-review-v1.json']
    return {'schema':'osw.pacific-sec-jet-widths-query-contract.v1','parent_logical_sha256':PARENT,
        'parent_collection_counts':audit['collection_counts'],'prior_source_inventory':list(source_rows.values()),
        'prior_source_inventory_scope':'owner_and_family_linked_sources_only_all_other_rows_preserved',
        'prior_owners':prior,'final_objects':final,'width_records':widths,'new_source':source,
        'citation_owner_ids':list(OWNERS),'family':FAMILY,'input_sha256':{p:sha(p) for p in inputs},
        'width_records_added':2,'sources_added':1,'width_samples_added':0,'lengths_added':0,
        'annual_ranges_added':0,'physical_geometries_added':0,'independent_observations_added':0,'installed':False}


def marker(contract,pin):
    return {'schema':'osw.pacific-sec-jet-widths-runtime.v1','parent_logical_sha256':PARENT,
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
    print('Frozen two reported component widths, one publication and one object projection; delivery pending.')
