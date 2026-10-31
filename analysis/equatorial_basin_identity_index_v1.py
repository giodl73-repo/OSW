"""Cloud-only lossless source-index extension for basin identity evidence."""
import copy
import gzip
import hashlib
import json
import os
from current_gap_index_extension import extend
import equatorial_basin_identity_query_v2 as query

PARENT_CATALOG_SHA = 'd3a90b894f39c550894897603dff86293c820286071a85f17a40f517b2bf53f1'
KEY = 'equatorial_basin_identity_index_v1'
DOCUMENTS = sorted([query.FILE, query.FACTS, query.PLANNING])
INDEX = {'almanac/index-catalog.json', 'almanac/index-data.json.gz', 'almanac/index-sources.json'}
sha = lambda raw: hashlib.sha256(raw).hexdigest()
encode = lambda value: (json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()


def verify_audit(audit):
    if (audit.get('added_source_paths') != DOCUMENTS
            or audit.get('replaced_source_paths') != []
            or audit.get('original_sources_verified') != 636
            or audit.get('original_source_strings_preserved') != 636
            or audit.get('scientific_source_documents_replaced') != 0):
        raise ValueError('Preserve all636 historical strings and append exactly three identity documents')


def source_index(catalog_raw, compressed, registry_raw):
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('OSW_EQUATORIAL_BASIN_IDENTITY_DELIVERY_V1') != '1'):
        raise ValueError('Explicit cloud basin identity delivery required before index access')
    if sha(catalog_raw) != PARENT_CATALOG_SHA:
        raise ValueError('Exact installed source catalog required')
    catalog = json.loads(catalog_raw)
    if sha(compressed) != catalog['compressed_sha256'] or len(compressed) != catalog['compressed_bytes']:
        raise ValueError('Compressed source index differs')
    raw = gzip.decompress(compressed)
    if sha(raw) != catalog['bundle_sha256'] or len(raw) != catalog['bundle_bytes']:
        raise ValueError('Logical source index differs')
    contract = query.build_contract()
    if query.encoded(contract) != (query.ROOT / query.FILE).read_bytes():
        raise ValueError('Frozen basin identity contract differs')
    added = {path: (query.ROOT / path).read_bytes() for path in DOCUMENTS}
    updated, corpus, registry, audit = extend(catalog, json.loads(raw), json.loads(registry_raw), added)
    verify_audit(audit)
    body = encode(corpus)
    packed = gzip.compress(body, compresslevel=9, mtime=0)
    registry_raw = encode(registry)
    updated.update(bundle_sha256=sha(body), bundle_bytes=len(body), compressed_sha256=sha(packed), compressed_bytes=len(packed))
    updated['input_sha256'] = {**updated.get('input_sha256', {}), **{p: sha(b) for p, b in added.items()},
                               'almanac/index-sources.json': sha(registry_raw)}
    return {'almanac/index-catalog.json': encode(updated), 'almanac/index-data.json.gz': packed,
            'almanac/index-sources.json': registry_raw}, audit


def attach(bundle, generated, audit):
    if set(generated) != INDEX or KEY in bundle['manifest'] or query.KEY not in bundle['manifest']:
        raise ValueError('Exact unapplied basin identity source-index extension required')
    verify_audit(audit)
    contract = query.build_contract()
    if (bundle['collections'].get('current_basin_memberships') != contract['additions']['current_basin_memberships']
            or json.loads(generated['almanac/index-catalog.json'])['source_count'] != 639):
        raise ValueError('Five exact memberships and639 source documents required')
    result = dict(bundle)
    result['manifest'] = copy.deepcopy(bundle['manifest'])
    result['manifest']['input_sha256'].update({p: sha(raw) for p, raw in generated.items()})
    result['manifest'][KEY] = copy.deepcopy(audit)
    return result
