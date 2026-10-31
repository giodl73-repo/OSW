"""Cloud-only extension of the lossless index by one active source document."""
import copy
import gzip
import hashlib
import json
import os
from current_gap_index_extension import extend
import azcc_onken_query_v1 as query

PARENT_CATALOG_SHA='7eaa28ecd76077967ac8060d79c0007e8729b6690d02472e503c11321bf5c7c8'
KEY='azcc_onken_index_v1'
INDEX={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def verify_audit(audit):
    if (audit.get('added_source_paths')!=[query.FACTS] or audit.get('replaced_source_paths')!=[]
        or audit.get('original_sources_verified')!=635 or audit.get('original_source_strings_preserved')!=635
        or audit.get('scientific_source_documents_replaced')!=0):
        raise ValueError('All635 historical source strings must be preserved exactly')

def source_index(catalog_raw,compressed,registry_raw):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
        or os.environ.get('OSW_AZCC_ONKEN_DELIVERY_V1')!='1'):
        raise ValueError('Explicit cloud AzCC delivery required before index access')
    if sha(catalog_raw)!=PARENT_CATALOG_SHA:raise ValueError('Exact installed source catalog required')
    catalog=json.loads(catalog_raw)
    if sha(compressed)!=catalog['compressed_sha256'] or len(compressed)!=catalog['compressed_bytes']:raise ValueError('Compressed index differs')
    raw=gzip.decompress(compressed)
    if sha(raw)!=catalog['bundle_sha256'] or len(raw)!=catalog['bundle_bytes']:raise ValueError('Logical index differs')
    source=(query.ROOT/query.FACTS).read_bytes()
    updated,corpus,registry,audit=extend(catalog,json.loads(raw),json.loads(registry_raw),{query.FACTS:source})
    verify_audit(audit)
    body=encode(corpus);packed=gzip.compress(body,compresslevel=9,mtime=0);registry_raw=encode(registry)
    updated.update(bundle_sha256=sha(body),bundle_bytes=len(body),compressed_sha256=sha(packed),compressed_bytes=len(packed))
    updated['input_sha256']={**updated.get('input_sha256',{}),query.FACTS:sha(source),'almanac/index-sources.json':sha(registry_raw)}
    return {'almanac/index-catalog.json':encode(updated),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_raw},audit

def attach(bundle,generated,audit):
    if set(generated)!=INDEX or KEY in bundle['manifest'] or query.KEY not in bundle['manifest']:
        raise ValueError('Exact unapplied AzCC source-index extension required')
    verify_audit(audit)
    contract=query.build_contract()
    if ([r for r in bundle['collections'].get('widths',[]) if r.get('id')==query.WIDTH_ID]!=[contract['width_record']]
            or json.loads(generated['almanac/index-catalog.json'])['source_count']!=636):
        raise ValueError('Exact cited regional width and636 indexed documents required')
    result=dict(bundle);result['manifest']=dict(bundle['manifest'])
    result['manifest']['input_sha256']=dict(bundle['manifest']['input_sha256'])
    result['manifest']['input_sha256'].update({p:sha(raw) for p,raw in generated.items()})
    result['manifest'][KEY]=copy.deepcopy(audit)
    return result
