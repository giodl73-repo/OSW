"""Lossless cloud-only source registration for regional model-grid length evidence."""
import copy
import gzip
import hashlib
import json
import os
from current_gap_index_extension import extend
import chen_indian_sec_ridge_query_v2 as query

PARENT_CATALOG_SHA='37c952c060d812bdde797b11d76d3673829dd1459e50635974763f03e38c3243'
PARENT_COMPRESSED_SHA='f326263b163f8ab5d724d03a3822015a57589196349609dcfdafbba9e9ec118b'
PARENT_REGISTRY_SHA='d4be6973a0cac33809a0acbbab69ffe519316d5dbdefc36ec0b44b542ed6d91c'
KEY='indian_sec_model_grid_length_index_v1'
RULES='research/chen-indian-sec-length-measurement-rules-v1.json'
DOCUMENTS=sorted([query.FILE,query.science.FILE,query.science.PREFLIGHT,RULES,
    'research/source-data/chen-indian-sec-2022/model-provider-metadata-v1.json',
    'research/chen-indian-sec-coordinate-run-v1/coordinate-interpretation.json',
    'research/chen-indian-sec-candidate-run-v2/canonical-replay.json'])
INDEX={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def verify_audit(audit):
    expected={'original_sources_verified':642,'original_source_strings_preserved':642,
              'replaced_source_paths':[],'added_source_paths':DOCUMENTS,'scientific_source_documents_replaced':0}
    if audit!=expected:raise ValueError('Preserve all642 original source strings and append exactly seven declared documents')

def cloud_controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
        or os.environ.get('OSW_CHEN_INDIAN_SEC_INDEX_V1')!='1'):
        raise ValueError('Explicit cloud Indian SEC source registration required before index access')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required: '+key)

def source_index(catalog_raw,compressed,registry_raw):
    cloud_controls()
    if sha(catalog_raw)!=PARENT_CATALOG_SHA or sha(compressed)!=PARENT_COMPRESSED_SHA or sha(registry_raw)!=PARENT_REGISTRY_SHA:
        raise ValueError('Exact installed catalog, compressed corpus and registry required')
    catalog=json.loads(catalog_raw)
    if sha(compressed)!=catalog['compressed_sha256'] or len(compressed)!=catalog['compressed_bytes']:raise ValueError('Compressed source index differs')
    raw=gzip.decompress(compressed)
    if sha(raw)!=catalog['bundle_sha256'] or len(raw)!=catalog['bundle_bytes']:raise ValueError('Logical source index differs')
    query.validated_contract()
    added={path:(query.ROOT/path).read_bytes() for path in DOCUMENTS}
    updated,corpus,registry,audit=extend(catalog,json.loads(raw),json.loads(registry_raw),added)
    verify_audit(audit)
    body=encode(corpus);packed=gzip.compress(body,compresslevel=9,mtime=0);registry_bytes=encode(registry)
    updated.update(bundle_sha256=sha(body),bundle_bytes=len(body),compressed_sha256=sha(packed),compressed_bytes=len(packed))
    updated['input_sha256']={**updated.get('input_sha256',{}),**{p:sha(b) for p,b in added.items()},'almanac/index-sources.json':sha(registry_bytes)}
    return {'almanac/index-catalog.json':encode(updated),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_bytes},audit

def attach(bundle,generated,audit):
    """Register generated source hashes without changing any measurement row."""
    verify_audit(audit)
    if set(generated)!=INDEX or KEY in bundle['manifest']:raise ValueError('Exact unapplied index extension required')
    contract=query.build_contract()
    marker=bundle['manifest'].get(query.KEY,{})
    expected_marker={'schema':'osw.indian-sec-model-grid-length-runtime.v1','contract_file':query.FILE,
        'contract_sha256':query.CANONICAL[query.FILE],'parent_logical_sha256':query.PARENT,'series_added':1,
        'readings_added':75,'sensitivities_added':120,'qualified_model_grid_lengths':8,'withheld_readings':67,
        'reported_lengths_added':0,'reference_routes_added':0,'widths_added':0,'physical_state_joins_added':0}
    if marker!=expected_marker:
        raise ValueError('Complete canonical regional-length extension required')
    rows=bundle['collections']
    if {k:len(v) for k,v in rows.items()}!=contract['expected_totals']:raise ValueError('Exact complete candidate counts required')
    for name,expected,predicate in [
        (query.SERIES,[contract['series_record']],lambda r:r.get('id')==query.SERIES_ID),
        (query.READINGS,contract['reading_records'],lambda r:r.get('series_id')==query.SERIES_ID),
        (query.SENSITIVITIES,contract['sensitivity_records'],lambda r:r.get('series_id')==query.SERIES_ID),
        ('sources',contract['new_sources'],lambda r:r.get('id') in query.SOURCE_IDS),
        ('objects',[contract['final_owner']],lambda r:r.get('id')==query.ENTITY),
        ('length_assessments',[contract['final_length_assessment']],lambda r:r.get('entity_id')==query.ENTITY)]:
        if [r for r in rows[name] if predicate(r)]!=expected:raise ValueError('Complete candidate rows differ: '+name)
    catalog=json.loads(generated['almanac/index-catalog.json'])
    registry=json.loads(generated['almanac/index-sources.json'])
    if catalog.get('schema')!='osw.almanac-index-catalog.v1' or catalog.get('source_count')!=649 or len(catalog.get('documents',[]))!=649:
        raise ValueError('Exact649-document catalog required')
    paths=[r['path'] for r in catalog['documents']]
    if len(set(paths))!=649 or not set(DOCUMENTS)<=set(paths):raise ValueError('Duplicate or missing source descriptors')
    declared=registry.get('documents',[])
    if (registry.get('schema')!='osw.almanac-index-sources.v1' or len(declared)!=len(set(declared))
        or not set(declared)<=set(paths) or not set(DOCUMENTS)<=set(declared)):
        raise ValueError('Unique source registry must retain added documents within the catalog')
    for descriptor in catalog['documents']:
        p=descriptor['path']
        if p in DOCUMENTS:
            raw=(query.ROOT/p).read_bytes()
            if descriptor['source_sha256']!=sha(raw) or descriptor['source_bytes']!=len(raw):raise ValueError('Changed new document descriptor: '+p)
    if (catalog['compressed_sha256']!=sha(generated['almanac/index-data.json.gz'])
        or catalog['compressed_bytes']!=len(generated['almanac/index-data.json.gz'])
        or catalog['input_sha256']['almanac/index-sources.json']!=sha(generated['almanac/index-sources.json'])):
        raise ValueError('Generated source files do not match catalog')
    result=dict(bundle);result['manifest']=copy.deepcopy(bundle['manifest'])
    pins={p:sha(raw) for p,raw in generated.items()}
    result['manifest']['input_sha256'].update(pins)
    result['manifest'][KEY]={'schema':'osw.indian-sec-model-grid-length-source-registration.v1',**copy.deepcopy(audit),
        'source_count':649,'generated_sha256':pins,'added_document_sha256':{p:query.legacy.sha(p) for p in DOCUMENTS}}
    return result
