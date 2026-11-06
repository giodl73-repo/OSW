"""Atomic source-checked packet patch; packet loading belongs to the cloud caller."""
import copy
import hashlib
import atlantic_nsec_reference_query_v1 as query


def marker(contract,pin):
    return {'schema':'osw.atlantic-nsec-reference-runtime.v1','parent_logical_sha256':query.PARENT,
        'contract_file':query.FILE,'contract_sha256':pin,'reference_routes_added':2,'sources_added':2,
        'reported_whole_current_lengths_added':0,'annual_ranges_added':0,
        'physical_geometries_added':0,'independent_observations_added':0}


def apply_verified(collections,manifest,contract,*,parent_logical_sha256,contract_sha256):
    if parent_logical_sha256!=query.PARENT or contract['parent_logical_sha256']!=query.PARENT or query.KEY in manifest:
        raise ValueError('Exact unapplied parent required')
    counts=contract['parent_collection_counts']
    if set(collections)!=set(counts) or any(not isinstance(collections[n],list) or len(collections[n])!=v for n,v in counts.items()):
        raise ValueError('Complete parent collection counts required')
    for name,field in [('objects','prior_owner'),('entities','prior_entity'),('route_decisions','prior_decision')]:
        field_id=contract[field]['id']
        if [r for r in collections[name] if r.get('id')==field_id]!=[contract[field]]:
            raise ValueError('Exact prior owner, identity or decision changed')
    for name,key in [('widths','prior_widths'),('length_assessments','prior_length_assessments')]:
        if [r for r in collections[name] if query.owns(r)]!=contract[key]:raise ValueError('Prior physical evidence changed')
    if any(query.owns(r) for r in collections['reference_routes']):raise ValueError('Prior reference routes need reconciliation')
    for row in contract['prior_owner_sources']:
        if [r for r in collections['sources'] if r.get('id')==row['id']]!=[row]:raise ValueError('Prior source changed')
    new_ids=[r['id'] for key in ['routes','new_sources'] for r in contract[key]]
    if len(new_ids)!=4 or len(set(new_ids))!=4 or any(r.get('id') in new_ids for records in collections.values() for r in records):
        raise ValueError('New record ID collision')
    pins={**contract['input_sha256'],query.FILE:contract_sha256}
    if any(p in manifest.get('input_sha256',{}) and manifest['input_sha256'][p]!=v for p,v in pins.items()):
        raise ValueError('Historical source pin would change')
    # Validate the entire patch before creating replacements; caller data is never mutated.
    after=dict(collections)
    after['reference_routes']=[*collections['reference_routes'],*copy.deepcopy(contract['routes'])]
    after['sources']=[*collections['sources'],*copy.deepcopy(contract['new_sources'])]
    for name,key in [('objects','final_owner'),('route_decisions','final_decision')]:
        expected=contract[key]
        after[name]=[copy.deepcopy(expected) if r['id']==expected['id'] else r for r in collections[name]]
    updated=copy.deepcopy(manifest);updated['input_sha256']={**manifest.get('input_sha256',{}),**pins}
    updated[query.KEY]=marker(contract,contract_sha256)
    return after,updated


def prepare(collections,manifest,contract,*,parent_logical_sha256):
    raw=query.encoded(query.build_contract())
    if query.encoded(contract)!=raw or (query.ROOT/query.FILE).read_bytes()!=raw:
        raise ValueError('Exact frozen source contract required')
    return apply_verified(collections,manifest,contract,parent_logical_sha256=parent_logical_sha256,
        contract_sha256=hashlib.sha256(raw).hexdigest())
