"""Lossless source-index extension for the verified regional speed collection.

The cloud caller supplies the exact installed compressed index. No CLI opens
the full packet or index locally. Historical source strings remain unchanged.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path
from current_gap_index_extension import extend
import published_current_speed_statistics_v1 as speed

ROOT = Path(__file__).resolve().parents[1]
PARENT_CATALOG_SHA = '2e19fdd112512f8ab7cc72f3691da9204440ccd39964be1f8be820a631101f15'
KEY = 'published_current_speed_source_index_v1'
INDEX = {'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()


def _extend_verified_index(catalog, compressed, registry, source):
    if digest(compressed) != catalog['compressed_sha256'] or len(compressed) != catalog['compressed_bytes']:
        raise ValueError('Compressed source index identity differs')
    raw = gzip.decompress(compressed)
    if digest(raw) != catalog['bundle_sha256'] or len(raw) != catalog['bundle_bytes']:
        raise ValueError('Logical source index identity differs')
    updated, corpus, next_registry, audit = extend(catalog,json.loads(raw),registry,{speed.SOURCE:source})
    if (audit['replaced_source_paths'] or audit['added_source_paths'] != [speed.SOURCE]
            or audit['original_source_strings_preserved'] != catalog['source_count']):
        raise ValueError('Only one new reviewed source document may be added')
    body = encode(corpus)
    packed = gzip.compress(body,compresslevel=9,mtime=0)
    registry_raw = encode(next_registry)
    updated.update(bundle_sha256=digest(body),bundle_bytes=len(body),
                   compressed_sha256=digest(packed),compressed_bytes=len(packed))
    updated['input_sha256'] = {**updated.get('input_sha256',{}),
        speed.SOURCE:digest(source),'almanac/index-sources.json':digest(registry_raw)}
    return {'almanac/index-catalog.json':encode(updated),
            'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_raw},audit


def source_index(catalog_raw, compressed, registry_raw):
    if digest(catalog_raw) != PARENT_CATALOG_SHA:
        raise ValueError('Exact installed source catalog required')
    source = (ROOT / speed.SOURCE).read_bytes()
    speed.validate_source(json.loads(source))
    return _extend_verified_index(json.loads(catalog_raw),compressed,json.loads(registry_raw),source)


def attach(bundle, generated, audit):
    if set(generated) != INDEX or KEY in bundle['manifest']:
        raise ValueError('Exact new source-index artifacts required, once')
    if (audit['added_source_paths'] != [speed.SOURCE] or audit['replaced_source_paths']
            or audit['original_sources_verified'] != 627
            or audit['original_source_strings_preserved'] != 627):
        raise ValueError('All627 installed source strings must survive')
    rows = bundle['collections'].get(speed.COLLECTION)
    if rows != speed.records():
        raise ValueError('Verified regional speed rows changed before index extension')
    catalog = json.loads(generated['almanac/index-catalog.json'])
    if catalog['source_count'] != 628:
        raise ValueError('Unexpected source document count')
    manifest = copy.deepcopy(bundle['manifest'])
    manifest['input_sha256'].update({p:digest(raw) for p,raw in generated.items()})
    manifest[KEY] = copy.deepcopy(audit)
    result = dict(bundle)
    result['manifest'] = manifest
    return result
