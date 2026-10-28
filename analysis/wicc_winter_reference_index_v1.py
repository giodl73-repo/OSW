"""Cloud-only one-document source-index extension; preserve all prior source text."""
import copy
import gzip
import hashlib
import json
import os
from current_gap_index_extension import extend
import wicc_winter_reference_query_v1 as query
import wicc_winter_reference_runtime_v1 as runtime

PARENT_CATALOG_SHA='4d72b7841ffacb1617f678934bb793d38f71763e2091adc36208c88d5f46cf5a'
KEY='wicc_winter_reference_index_v1'
INDEX={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()


def source_index(catalog_raw, compressed, registry_raw):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Explicit working-branch cloud caller required before index access')
    if sha(catalog_raw)!=PARENT_CATALOG_SHA:
        raise ValueError('Exact installed source catalog required')
    catalog=json.loads(catalog_raw)
    if sha(compressed)!=catalog['compressed_sha256'] or len(compressed)!=catalog['compressed_bytes']:
        raise ValueError('Compressed index differs')
    raw=gzip.decompress(compressed)
    if sha(raw)!=catalog['bundle_sha256'] or len(raw)!=catalog['bundle_bytes']:
        raise ValueError('Logical source index differs')
    source=(query.ROOT/query.CANDIDATE).read_bytes()
    updated,corpus,registry,audit=extend(catalog,json.loads(raw),json.loads(registry_raw),{query.CANDIDATE:source})
    if (audit['added_source_paths']!=[query.CANDIDATE] or audit['replaced_source_paths']
            or audit['original_sources_verified']!=632 or audit['original_source_strings_preserved']!=632):
        raise ValueError('Preserve all632 indexed source strings exactly')
    body=encode(corpus);packed=gzip.compress(body,compresslevel=9,mtime=0);registry_raw=encode(registry)
    updated.update(bundle_sha256=sha(body),bundle_bytes=len(body),compressed_sha256=sha(packed),compressed_bytes=len(packed))
    updated['input_sha256']={**updated.get('input_sha256',{}),query.CANDIDATE:sha(source),'almanac/index-sources.json':sha(registry_raw)}
    return {'almanac/index-catalog.json':encode(updated),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_raw},audit


def attach(bundle,generated,audit):
    if set(generated)!=INDEX or KEY in bundle['manifest'] or runtime.KEY not in bundle['manifest']:
        raise ValueError('Exact new route/index extension required once')
    if (audit.get('added_source_paths')!=[query.CANDIDATE] or audit.get('replaced_source_paths')!=[]
            or audit.get('original_sources_verified')!=632 or audit.get('original_source_strings_preserved')!=632):
        raise ValueError('Historical source custody differs')
    rows=[r for r in bundle['collections']['reference_routes'] if r.get('current_id')==query.CURRENT]
    if rows!=[query.build_contract()['route']] or json.loads(generated['almanac/index-catalog.json'])['source_count']!=633:
        raise ValueError('Exact regional route and633 source documents required')
    result=dict(bundle);result['manifest']=copy.deepcopy(bundle['manifest'])
    result['manifest']['input_sha256'].update({p:sha(raw) for p,raw in generated.items()})
    result['manifest'][KEY]=copy.deepcopy(audit)
    return result
