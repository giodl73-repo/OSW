"""Append diagnostic source documents to the exact verified index, cloud only."""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path

from current_gap_index_extension import extend
import pacific_nec_product_axis_query_v1 as query
import pacific_nec_product_axis_records_v1 as records
from pacific_nec_product_axis_delivery_contract_v1 import admission_marker

ROOT=Path(__file__).resolve().parents[1]
KEY='pacific_nec_surface_product_axis_index_v1'
RULES='research/pacific-nec-product-axis-measurement-rules-v1.json'
DOCUMENTS=sorted([query.FILE,query.CORE,query.SAMPLING,query.ACQUISITION,RULES,
    'research/pacific-nec-monthly-dimensions-source-review-v1.json',
    'research/pacific-nec-monthly-dimensions-run-v1/download.json'])
INDEX={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}
PARENT_SHA={'almanac/index-catalog.json':'f70a37404f5b5f76ebc41a4e98d62de826983531aca01a9513eac5e84245b992',
    'almanac/index-data.json.gz':'9f781605197ffc83e6e426323827e7258add7b3db757347a3a940359500b0c78',
    'almanac/index-sources.json':'27a7e92891e45e026135ecd6af85c395e4797eb4ec776ce1fe1793859fd2f80f'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_PACIFIC_NEC_PRODUCT_DELIVERY_V1')!='1'):
        raise ValueError('Scoped cloud product-axis source registration required before index access')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required: '+key)

def verify_audit(audit):
    expected={'original_sources_verified':649,'original_source_strings_preserved':649,'replaced_source_paths':[],
        'added_source_paths':DOCUMENTS,'scientific_source_documents_replaced':0}
    if audit!=expected:raise ValueError('All 649 historical source strings and exactly seven new documents required')

def source_index(catalog_raw,compressed,registry_raw):
    controls()
    for path,raw in [('almanac/index-catalog.json',catalog_raw),('almanac/index-data.json.gz',compressed),('almanac/index-sources.json',registry_raw)]:
        if sha(raw)!=PARENT_SHA[path]:raise ValueError('Exact installed source-index files required: '+path)
    catalog=json.loads(catalog_raw)
    if sha(compressed)!=catalog['compressed_sha256'] or len(compressed)!=catalog['compressed_bytes']:raise ValueError('Compressed index descriptor differs')
    raw=gzip.decompress(compressed)
    if sha(raw)!=catalog['bundle_sha256'] or len(raw)!=catalog['bundle_bytes']:raise ValueError('Logical source index differs')
    contract=query.build_contract()
    if records.encoded(contract)!=(ROOT/query.FILE).read_bytes():raise ValueError('Frozen diagnostic contract changed')
    additions={path:(ROOT/path).read_bytes() for path in DOCUMENTS}
    next_catalog,corpus,registry,audit=extend(catalog,json.loads(raw),json.loads(registry_raw),additions);verify_audit(audit)
    body=encode(corpus);packed=gzip.compress(body,compresslevel=9,mtime=0);registry_bytes=encode(registry)
    next_catalog.update(bundle_sha256=sha(body),bundle_bytes=len(body),compressed_sha256=sha(packed),compressed_bytes=len(packed))
    next_catalog['input_sha256']={**next_catalog.get('input_sha256',{}),**{p:sha(b) for p,b in additions.items()},'almanac/index-sources.json':sha(registry_bytes)}
    return {'almanac/index-catalog.json':encode(next_catalog),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_bytes},audit

def attach(bundle,generated,audit,contract):
    verify_audit(audit)
    if set(generated)!=INDEX or KEY in bundle['manifest']:raise ValueError('Exact unapplied generated source index required')
    marker=bundle['manifest'].get(records.KEY,{})
    if records.encoded(marker)!=records.encoded(admission_marker(contract)) or marker['contract_sha256']!=sha((ROOT/query.FILE).read_bytes()):raise ValueError('Complete diagnostic admission required')
    for name,rows in contract['collections_added'].items():
        if records.encoded(bundle['collections'].get(name))!=records.encoded(rows):raise ValueError('Incomplete diagnostic rows: '+name)
    catalog=json.loads(generated['almanac/index-catalog.json']);registry=json.loads(generated['almanac/index-sources.json']);paths=[r['path'] for r in catalog['documents']]
    if catalog['source_count']!=656 or len(paths)!=656 or len(set(paths))!=656 or not set(DOCUMENTS)<=set(paths):raise ValueError('Exact 656-document catalog required')
    if registry.get('schema')!='osw.almanac-index-sources.v1' or len(registry['documents'])!=len(set(registry['documents'])) or not set(registry['documents'])<=set(paths) or not set(DOCUMENTS)<=set(registry['documents']):raise ValueError('Invalid generated source registry')
    for row in catalog['documents']:
        if row['path'] in DOCUMENTS:
            raw=(ROOT/row['path']).read_bytes()
            if row['source_sha256']!=sha(raw) or row['source_bytes']!=len(raw):raise ValueError('Changed new source descriptor')
    if catalog['compressed_sha256']!=sha(generated['almanac/index-data.json.gz']) or catalog['compressed_bytes']!=len(generated['almanac/index-data.json.gz']) or catalog['input_sha256']['almanac/index-sources.json']!=sha(generated['almanac/index-sources.json']):raise ValueError('Generated index binding differs')
    result=dict(bundle);result['manifest']=copy.deepcopy(bundle['manifest']);pins={p:sha(raw) for p,raw in generated.items()}
    result['manifest']['input_sha256'].update(pins)
    result['manifest'][KEY]={'schema':'osw.pacific-nec-product-axis-source-registration.v1',**copy.deepcopy(audit),'source_count':656,
        'generated_sha256':pins,'added_document_sha256':{p:sha((ROOT/p).read_bytes()) for p in DOCUMENTS}}
    return result
