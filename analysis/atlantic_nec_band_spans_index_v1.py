"""Append four source documents while preserving all 660 indexed originals."""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
from current_gap_index_extension import extend
import atlantic_nec_band_spans_query_v1 as query

ROOT=query.ROOT
KEY='published_atlantic_nec_band_spans_index_v1'
DOCUMENTS=sorted([query.FILE,query.PREPARED,'research/atlantic-nec-stramma-2005-source-facts-v2.json',
                  'research/atlantic-nec-stramma-2005-preparation-review-v2.json'])
INDEX={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
        or os.environ.get('OSW_ATLANTIC_NEC_BANDS_DELIVERY_V1')!='1'):
        raise ValueError('Scoped cloud index registration only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')

def verify_audit(audit):
    expected={'original_sources_verified':660,'original_source_strings_preserved':660,
        'replaced_source_paths':[],'added_source_paths':DOCUMENTS,'scientific_source_documents_replaced':0}
    if audit!=expected:raise ValueError('All 660 originals and exactly four new documents required')

def source_index(catalog_raw,compressed,registry_raw):
    controls()
    parent=query.read('research/dimoune-2023-width-installation-saved-engine-manifest-v1.json')['sha256']
    for path,raw in [('almanac/index-catalog.json',catalog_raw),('almanac/index-data.json.gz',compressed),('almanac/index-sources.json',registry_raw)]:
        if sha(raw)!=parent[path]:raise ValueError('Exact installed source index required: '+path)
    catalog=json.loads(catalog_raw)
    if sha(compressed)!=catalog['compressed_sha256'] or len(compressed)!=catalog['compressed_bytes']:raise ValueError('Compressed index descriptor differs')
    raw=gzip.decompress(compressed)
    if sha(raw)!=catalog['bundle_sha256'] or len(raw)!=catalog['bundle_bytes']:raise ValueError('Logical index descriptor differs')
    additions={path:(ROOT/path).read_bytes() for path in DOCUMENTS}
    next_catalog,corpus,registry,audit=extend(catalog,json.loads(raw),json.loads(registry_raw),additions);verify_audit(audit)
    body=encode(corpus);packed=gzip.compress(body,compresslevel=9,mtime=0);registry_bytes=encode(registry)
    next_catalog.update(bundle_sha256=sha(body),bundle_bytes=len(body),compressed_sha256=sha(packed),compressed_bytes=len(packed))
    next_catalog['input_sha256']={**next_catalog.get('input_sha256',{}),**{p:sha(b) for p,b in additions.items()},'almanac/index-sources.json':sha(registry_bytes)}
    return {'almanac/index-catalog.json':encode(next_catalog),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_bytes},audit

def attach(bundle,generated,audit,contract):
    verify_audit(audit)
    if set(generated)!=INDEX or KEY in bundle['manifest']:raise ValueError('Exact unapplied index extension required')
    if bundle['manifest'].get(query.KEY)!=query.marker(contract,sha((ROOT/query.FILE).read_bytes())):raise ValueError('Complete width admission required')
    catalog=json.loads(generated['almanac/index-catalog.json']);registry=json.loads(generated['almanac/index-sources.json'])
    paths=[r['path'] for r in catalog['documents']]
    if len(paths)!=len(set(paths)) or len(paths)!=664 or catalog['source_count']!=664 or not set(DOCUMENTS)<=set(paths):raise ValueError('Exact 664-document catalog required')
    if len(registry['documents'])!=len(set(registry['documents'])) or not set(registry['documents'])<=set(paths):raise ValueError('Invalid source registry')
    for row in catalog['documents']:
        if row['path'] in DOCUMENTS:
            raw=(ROOT/row['path']).read_bytes()
            if row['source_sha256']!=sha(raw) or row['source_bytes']!=len(raw):raise ValueError('Changed new source descriptor')
    if catalog['compressed_sha256']!=sha(generated['almanac/index-data.json.gz']) or catalog['compressed_bytes']!=len(generated['almanac/index-data.json.gz']) or catalog['input_sha256']['almanac/index-sources.json']!=sha(generated['almanac/index-sources.json']):raise ValueError('Generated index binding differs')
    result=dict(bundle);result['manifest']=copy.deepcopy(bundle['manifest']);pins={p:sha(raw) for p,raw in generated.items()}
    result['manifest']['input_sha256'].update(pins)
    result['manifest'][KEY]={'schema':'osw.atlantic-nec-band-spans-source-registration.v1',**audit,'source_count':664,
        'generated_sha256':pins,'added_document_sha256':{p:sha((ROOT/p).read_bytes()) for p in DOCUMENTS}}
    return result
