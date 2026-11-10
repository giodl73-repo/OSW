"""Lossless one-document index extension for the review-cited WICC width."""
import copy
import gzip
import hashlib
import json
from current_gap_index_extension import extend
import published_wicc_review_width_v1 as core

PARENT_CATALOG_SHA='5836aa50cbd91ee14791fcbeeaf3ce5e6b0ac5eb43e77e6efdf20fd06d94a413'
KEY='published_wicc_review_width_index_v1'
INDEX={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def source_index(catalog_raw,compressed,registry_raw):
    if sha(catalog_raw)!=PARENT_CATALOG_SHA:raise ValueError('Exact installed source catalog required')
    catalog=json.loads(catalog_raw)
    if sha(compressed)!=catalog['compressed_sha256'] or len(compressed)!=catalog['compressed_bytes']:raise ValueError('Compressed index differs')
    raw=gzip.decompress(compressed)
    if sha(raw)!=catalog['bundle_sha256'] or len(raw)!=catalog['bundle_bytes']:raise ValueError('Logical index differs')
    source=(core.ROOT/core.SOURCE).read_bytes()
    updated,corpus,registry,audit=extend(catalog,json.loads(raw),json.loads(registry_raw),{core.SOURCE:source})
    if audit['replaced_source_paths'] or audit['added_source_paths']!=[core.SOURCE] or audit['original_source_strings_preserved']!=630:raise ValueError('All630 historical source strings must survive')
    body=encode(corpus);packed=gzip.compress(body,compresslevel=9,mtime=0);registry_raw=encode(registry)
    updated.update(bundle_sha256=sha(body),bundle_bytes=len(body),compressed_sha256=sha(packed),compressed_bytes=len(packed))
    updated['input_sha256']={**updated.get('input_sha256',{}),core.SOURCE:sha(source),'almanac/index-sources.json':sha(registry_raw)}
    return {'almanac/index-catalog.json':encode(updated),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_raw},audit

def attach(bundle,generated,audit):
    if set(generated)!=INDEX or KEY in bundle['manifest']:raise ValueError('Exact new index artifacts required once')
    if audit['added_source_paths']!=[core.SOURCE] or audit['replaced_source_paths'] or audit['original_sources_verified']!=630 or audit['original_source_strings_preserved']!=630:raise ValueError('Historical corpus custody differs')
    rows=[r for r in bundle['collections']['widths'] if 'review_width_context' in r]
    if rows!=[core.record()] or json.loads(generated['almanac/index-catalog.json'])['source_count']!=631:raise ValueError('Review width rows or source count differ')
    result=dict(bundle);result['manifest']=copy.deepcopy(bundle['manifest'])
    result['manifest']['input_sha256'].update({p:sha(raw) for p,raw in generated.items()});result['manifest'][KEY]=copy.deepcopy(audit)
    return result
