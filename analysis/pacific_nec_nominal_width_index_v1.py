"""Cloud-only lossless source-index extension for the reviewed nominal width."""
import copy
import gzip
import hashlib
import json
import os
from current_gap_index_extension import extend
import pacific_nec_nominal_width_query_v1 as query

PARENT_CATALOG_SHA='5cab29c00b972f4a69e06e136dd0776103d9d29fc1678328ef7197e23b29f41c'
KEY='pacific_nec_nominal_width_index_v1'
DOCUMENTS=sorted([query.FILE,query.nominal.FACTS,query.nominal.FILE])
INDEX={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()


def verify_audit(audit):
    if (audit.get('added_source_paths')!=DOCUMENTS or audit.get('replaced_source_paths')!=[]
            or audit.get('original_sources_verified')!=639 or audit.get('original_source_strings_preserved')!=639
            or audit.get('scientific_source_documents_replaced')!=0):
        raise ValueError('Preserve all639 historical source strings and append exactly three width documents')


def source_index(catalog_raw,compressed,registry_raw):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
            or os.environ.get('OSW_PACIFIC_NEC_NOMINAL_WIDTH_DELIVERY_V1')!='1'):
        raise ValueError('Explicit cloud width delivery required before index access')
    if sha(catalog_raw)!=PARENT_CATALOG_SHA:raise ValueError('Exact installed source catalog required')
    catalog=json.loads(catalog_raw)
    if sha(compressed)!=catalog['compressed_sha256'] or len(compressed)!=catalog['compressed_bytes']:
        raise ValueError('Compressed source index differs')
    raw=gzip.decompress(compressed)
    if sha(raw)!=catalog['bundle_sha256'] or len(raw)!=catalog['bundle_bytes']:raise ValueError('Logical source index differs')
    contract=query.build_contract()
    if query.encoded(contract)!=(query.ROOT/query.FILE).read_bytes():raise ValueError('Frozen width contract differs')
    added={path:(query.ROOT/path).read_bytes() for path in DOCUMENTS}
    updated,corpus,registry,audit=extend(catalog,json.loads(raw),json.loads(registry_raw),added)
    verify_audit(audit)
    body=encode(corpus);packed=gzip.compress(body,compresslevel=9,mtime=0);registry_raw=encode(registry)
    updated.update(bundle_sha256=sha(body),bundle_bytes=len(body),compressed_sha256=sha(packed),compressed_bytes=len(packed))
    updated['input_sha256']={**updated.get('input_sha256',{}),**{p:sha(b) for p,b in added.items()},'almanac/index-sources.json':sha(registry_raw)}
    return {'almanac/index-catalog.json':encode(updated),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_raw},audit


def attach(bundle,generated,audit):
    if set(generated)!=INDEX or KEY in bundle['manifest'] or bundle['manifest'].get(query.KEY)!=query.marker(query.build_contract()):
        raise ValueError('Exact unapplied width source-index extension required')
    verify_audit(audit);contract=query.build_contract()
    if (len(bundle['collections'].get('sources',[]))!=219 or len(bundle['collections'].get('widths',[]))!=179
            or [r for r in bundle['collections']['widths'] if r.get('id')==query.WIDTH_ID]!=[contract['width_record']]
            or json.loads(generated['almanac/index-catalog.json'])['source_count']!=642):
        raise ValueError('Exact widths, publications and642 source documents required')
    result=dict(bundle);result['manifest']=copy.deepcopy(bundle['manifest'])
    result['manifest']['input_sha256'].update({p:sha(raw) for p,raw in generated.items()})
    result['manifest'][KEY]=copy.deepcopy(audit)
    return result
