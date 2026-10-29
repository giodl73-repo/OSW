"""Source-bound additive admission of experimental Pacific NEC product diagnostics."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import pacific_nec_product_axis_records_v1 as data

ROOT=Path(__file__).resolve().parents[1]
FILE='research/pacific-nec-product-axis-query-contract-v1.json'
AUDIT='research/pacific-nec-product-axis-parent-run-v1/audit.json'
REVIEW='research/pacific-nec-product-axis-parent-execution-review-v1.json'
CORE='research/pacific-nec-connected-core-run-v1/diagnostic.json'
SAMPLING='research/pacific-nec-core-sampling-run-v1/diagnostic.json'
ACQUISITION='research/pacific-nec-monthly-dimensions-run-v1/acquisition.json'
PARENT='000ec593c4fd1eb597a0a7204824b5c8c8e19cd8e2683080095a46ec50609cb1'
SOURCE_IDS=['source:oscar2017-noaa-pifsc-archive','source:liu-zhou-pacific-nec-2020','source:osw-pacific-nec-connected-product-axis-v1']


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def read(path):return json.loads((ROOT/path).read_bytes())


def sources():
    acquisition=read(ACQUISITION)
    common={'used_in_collections':list(data.COLLECTIONS),'measurement_admission':'experimental_surface_product_operator_only',
            'source_facts_file':'research/pacific-nec-monthly-dimensions-source-review-v1.json',
            'source_facts_sha256':sha('research/pacific-nec-monthly-dimensions-source-review-v1.json')}
    return [
        {**common,'id':SOURCE_IDS[0],'kind':'dataset','label':'OSCAR2017.0 NOAA PIFSC archive mirror',
         'title':'OSCAR third-degree near-surface currents, version2017.0, NOAA PIFSC ERDDAP mirror',
         'url':'https://oceanwatch.pifsc.noaa.gov/erddap/info/yearly_336c_0b32_9cd3/index.html',
         'metadata_url':'https://oceanwatch.pifsc.noaa.gov/erddap/info/yearly_336c_0b32_9cd3/index.json',
         'provider':'Earth & Space Research; NOAA PIFSC ERDDAP mirror','dataset_id':'yearly_336c_0b32_9cd3',
         'version':'2017.0','doi':None,'nominal_depth_coordinate_m':15,'grid_spacing_degrees':1/3,
         'acquisition_file':ACQUISITION,'acquisition_sha256':sha(ACQUISITION),
         'acquired_product_files':copy.deepcopy(acquisition['files']),
         'scope_note':'Satellite-derived near-surface diagnostic product. The nominal15m coordinate is not a direct instrument section or depth-resolved current observation.',
         'license_locator':ACQUISITION+'#/license','citation_role':'direct_numerical_source_product'},
        {**common,'id':SOURCE_IDS[1],'kind':'paper','year':2020,'authors':['Xueqi Liu','Hui Zhou'],
         'label':'Liu and Zhou2020: Pacific NEC seasonal context',
         'title':'Seasonal Variations of the North Equatorial Current Across the Pacific Ocean',
         'doi':'10.1029/2019JC015895','url':'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019JC015895',
         'citation_role':'geographic_and_definition_context_only_not_numerical_measurement_source',
         'access_scope':'Publisher-indexed full-text methods/context inspected. Original figures were not acquired or digitized.',
         'scope_note':'The8–18N integration window and distinction between surface and depth-integrated axes provide context. The OSW OSCAR calculations do not reproduce this paper.'},
        {**common,'id':SOURCE_IDS[2],'kind':'internal','label':'OSW Pacific NEC connected product-axis diagnostic method',
         'title':'Window-constrained connected westward OSCAR paths and method sensitivity',
         'url':'../plans/pacific-nec-connected-core-protocol-v1.md','path':'plans/pacific-nec-connected-core-protocol-v1.md',
         'repository_path':'plans/pacific-nec-connected-core-protocol-v1.md',
         'additional_protocol_file':'plans/pacific-nec-core-window-sampling-protocol-v1.md',
         'citation_role':'OSW_numerical_operator_and_scope_definition',
         'scope_note':'Keep window contacts, failed scenarios, source sampling, representation effects and unresolved physical identity. Whole-current lengths, physical widths and annual envelopes are not admitted.'}]


def build_contract():
    review=read(REVIEW)
    if review['status']!='PASS_EXACT_PARENT_SOURCE_AND_COLLECTION_AUDIT':raise ValueError('Successful exact parent audit required')
    for path,pin in review['retained_evidence_sha256'].items():
        if sha(path)!=pin:raise ValueError('Retained parent evidence changed: '+path)
    audit=read(AUDIT)
    if audit['parent_logical_sha256']!=PARENT or audit['parent_logical_bytes']!=191109635:
        raise ValueError('Wrong audited parent')
    if audit['proposed_collections_absent']!=list(data.COLLECTIONS) or audit['proposed_namespace_absent']!=data.KEY:
        raise ValueError('Proposed namespace differs from audit')
    if any(row['status']!='MISSING' for row in audit['source_resolution']['resolutions'].values()):
        raise ValueError('Source aliases require renewed reconciliation')
    inputs=[AUDIT,REVIEW,CORE,SAMPLING,ACQUISITION,'analysis/pacific_nec_product_axis_records_v1.py',
        'analysis/pacific_nec_product_axis_query_v1.py','plans/pacific-nec-product-axis-query-delivery-v1.md',
        'plans/pacific-nec-connected-core-protocol-v1.md','plans/pacific-nec-core-window-sampling-protocol-v1.md',
        'research/pacific-nec-monthly-dimensions-source-review-v1.json',
        'research/pacific-nec-connected-core-render-visual-review-v2.json',
        'research/pacific-nec-core-sampling-execution-review-v1.json']
    pins={path:sha(path) for path in inputs}
    additions=data.records(read(CORE),read(SAMPLING),read(ACQUISITION),SOURCE_IDS,pins)
    for rows in additions.values():
        for row in rows:
            row.update(source_id=SOURCE_IDS[0],dataset_source_id=SOURCE_IDS[0],context_source_id=SOURCE_IDS[1],method_source_id=SOURCE_IDS[2])
    new_sources=sources()
    existing={r['id'] for r in audit['source_inventory']}
    if existing&set(SOURCE_IDS):raise ValueError('Source ID collision after audit')
    return {'schema':'osw.pacific-nec-product-axis-query-contract.v1',
        'admission':'experimental_reproducible_product_operator_diagnostics',
        'parent_logical_sha256':PARENT,'parent_logical_bytes':191109635,
        'parent_collection_counts':audit['collection_counts'],'prior_identity_rows':audit['identities'],
        'prior_source_inventory':audit['source_inventory'],'input_sha256':pins,
        'namespace':data.KEY,'owner':data.OWNER,'family':data.FAMILY,'prefixes':list(data.PREFIXES),
        'collections_added':additions,'new_sources':new_sources,
        'counts_added':{name:len(rows) for name,rows in additions.items()},
        'new_source_count':3,'reported_lengths_added':0,'reference_routes_added':0,'physical_widths_added':0,
        'physical_state_joins_added':0,'annual_physical_ranges_added':0,'independent_observations_added':0,
        'owner_and_family_rows_changed':False,'installed':False,'full_goal_complete':False}


def apply_verified(collections,manifest,contract,*,parent_logical_sha256,contract_sha256):
    """Pure mutation boundary, exercised separately with bounded parent fixtures."""
    if parent_logical_sha256!=contract['parent_logical_sha256'] or contract['namespace'] in manifest:
        raise ValueError('Exact unapplied parent required')
    counts=contract['parent_collection_counts']
    if set(collections)!=set(counts) or any(not isinstance(collections[name],list) or len(collections[name])!=count for name,count in counts.items()):
        raise ValueError('Complete parent collection set/counts differ')
    if any(name in collections for name in contract['collections_added']):raise ValueError('Diagnostic collection already exists')
    sources=collections['sources']
    if data.fingerprint(sources)!=data.fingerprint(contract['prior_source_inventory']):raise ValueError('Prior source inventory changed')
    for owner,expected in contract['prior_identity_rows'].items():
        for name in ('objects','entities'):
            selected=[r for r in collections[name] if r.get('id')==owner]
            if data.fingerprint(selected)!=data.fingerprint(expected[name]):raise ValueError('Owner/family identity changed: '+owner)
        for name,audited in expected.get('linked_records',{}).items():
            selected=[r for r in collections.get(name,[]) if r.get('entity_id')==owner
                or r.get('family_entity_id')==owner or r.get('current_id')==owner.removeprefix('current:')]
            if data.fingerprint(selected)!=data.fingerprint(audited):raise ValueError('Prior owner/family evidence changed: '+owner+'/'+name)
    new_ids={r['id'] for r in contract['new_sources']}
    if new_ids&{r['id'] for r in sources}:raise ValueError('New source ID already exists')
    if any(isinstance(r.get('id'),str) and r['id'].startswith(tuple(contract['prefixes'])) for rows in collections.values() for r in rows):
        raise ValueError('New record prefix already exists')
    pins={**contract['input_sha256'],FILE:contract_sha256}
    if any(path in manifest.get('input_sha256',{}) and manifest['input_sha256'][path]!=pin for path,pin in pins.items()):
        raise ValueError('Historical input pin would change')
    after=dict(collections)
    for name,rows in contract['collections_added'].items():after[name]=copy.deepcopy(rows)
    after['sources']=[*sources,*copy.deepcopy(contract['new_sources'])]
    updated=dict(manifest);updated['input_sha256']={**manifest.get('input_sha256',{}),**pins}
    updated[contract['namespace']]={'schema':'osw.pacific-nec-product-axis-runtime.v1',
        'contract_file':FILE,'contract_sha256':contract_sha256,'parent_logical_sha256':parent_logical_sha256,
        'collections_added':contract['counts_added'],'sources_added':len(contract['new_sources']),
        'admission':'experimental_product_operator_only','reported_lengths_added':0,'reference_routes_added':0,
        'physical_widths_added':0,'physical_state_joins_added':0,'annual_physical_ranges_added':0,
        'independent_observations_added':0}
    return after,updated


def prepare(collections,manifest,contract,*,parent_logical_sha256):
    expected=build_contract();raw=data.encoded(expected)
    if data.encoded(contract)!=raw or not (ROOT/FILE).exists() or (ROOT/FILE).read_bytes()!=raw:
        raise ValueError('Exact frozen contract required')
    return apply_verified(collections,manifest,contract,parent_logical_sha256=parent_logical_sha256,
                          contract_sha256=hashlib.sha256(raw).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-contract',action='store_true');args=parser.parse_args()
    contract=build_contract();raw=data.encoded(contract);target=ROOT/FILE
    if args.write_contract:
        if target.exists() and target.read_bytes()!=raw:raise ValueError('Frozen contract differs; use an explicit versioned revision')
        if not target.exists():target.write_bytes(raw)
    print(json.dumps({'status':'PREPARED_EXPERIMENTAL_DIAGNOSTIC_CONTRACT','records':contract['counts_added'],
        'sources_added':3,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'installed':False}))
