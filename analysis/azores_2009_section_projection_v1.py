"""Prepare a lossless, source-bound Azores section presentation for cloud delivery.

No full packet is loaded by this module's CLI. The delivery caller supplies an
already verified installed bundle in the cloud. Measurement collections and
all earlier manifest entries must survive unchanged.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = 'azores_2009_section_review_v1'
REVIEW = 'research/azores-2009-section-original-review-v1.json'
BINDINGS = 'research/azores-2009-section-record-bindings-v1.json'
VISUAL = 'research/azores-2009-section-card-visual-review-v1.json'
FIGURE = 'figures/azores-2009-section-card-v1.svg'
SOURCE_FIGURE = 'figures/azores-2009-section-context-v1.svg'
PARENT = '233c156bf1e044e7378d5bb739633da59eadb28125d40fc3254dd503e2bc1a32'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def documents():
    return {p: (ROOT / p).read_bytes() for p in [REVIEW, BINDINGS, VISUAL]}


def marker():
    if (ROOT / FIGURE).read_bytes() != card_svg():
        raise ValueError('Stale current-card section figure')
    return {'logical_parent_sha256': PARENT,
            'input_sha256': {p: sha((ROOT / p).read_bytes()) for p in [REVIEW, BINDINGS, VISUAL, FIGURE]},
            'measurement_records_added': 0, 'measurement_records_changed': 0}


def card_svg():
    raw = (ROOT / SOURCE_FIGURE).read_bytes()
    old = b'OSW independent locator. Source review prepared; runtime card integration pending.'
    if raw.count(old) != 1:
        raise ValueError('Changed reviewed source diagram footer')
    return raw.replace(old, b'OSW independent section locator. Original date conflict retained; one survey, not a seasonal cycle.')


def validate_rows(widths):
    binding = json.loads((ROOT / BINDINGS).read_bytes())
    if binding['logical_parent_sha256'] != PARENT:
        raise ValueError('Changed installed source parent')
    for expected in binding['records']:
        matches = [r for r in widths if r.get('id') == expected['id']]
        if matches != [expected]:
            raise ValueError('Missing, duplicated or changed existing Azores section')


def prepare(bundle, *, logical_parent_sha256):
    if logical_parent_sha256 != PARENT or bundle.get('schema') != 'osw.query-bundle.v1':
        raise ValueError('Exact installed logical parent required')
    validate_rows(bundle['collections'].get('widths', []))
    original = bundle['manifest']
    if KEY in original:
        raise ValueError('Section presentation already prepared')
    result = dict(bundle)
    result['manifest'] = manifest = copy.deepcopy(original)
    # Collections are preserved by identity; this transformation has no science delta.
    pins = marker()
    hashes = manifest.setdefault('input_sha256', {})
    for path, digest in pins['input_sha256'].items():
        if path in hashes and hashes[path] != digest:
            raise ValueError('Existing source pin would be overwritten')
        hashes[path] = digest
    manifest[KEY] = pins
    return result


def extend_source_index(catalog, corpus, registry):
    from current_gap_index_extension import extend
    return extend(catalog, corpus, registry, documents())


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()


def source_index(catalog, compressed, registry):
    if sha(compressed) != catalog['compressed_sha256'] or len(compressed) != catalog['compressed_bytes']:
        raise ValueError('Exact installed compressed index required')
    raw = gzip.decompress(compressed)
    if sha(raw) != catalog['bundle_sha256'] or len(raw) != catalog['bundle_bytes']:
        raise ValueError('Exact installed logical index required')
    updated, corpus, next_registry, audit = extend_source_index(catalog, json.loads(raw), registry)
    if audit['replaced_source_paths'] or set(audit['added_source_paths']) != set(documents()):
        raise ValueError('Unexpected historical source replacement or new source inventory')
    body = encode(corpus)
    packed = gzip.compress(body, compresslevel=9, mtime=0)
    registry_raw = encode(next_registry)
    updated.update(bundle_sha256=sha(body), bundle_bytes=len(body),
                   compressed_sha256=sha(packed), compressed_bytes=len(packed))
    updated['input_sha256'] = {**updated.get('input_sha256', {}),
        **{p: sha(b) for p, b in documents().items()}, 'almanac/index-sources.json': sha(registry_raw)}
    return {'almanac/index-catalog.json': encode(updated), 'almanac/index-data.json.gz': packed,
            'almanac/index-sources.json': registry_raw}, audit


def packet_manifest(manifest, generated, audit):
    expected = {'almanac/index-catalog.json', 'almanac/index-data.json.gz', 'almanac/index-sources.json'}
    if set(generated) != expected or manifest.get(KEY) != marker():
        raise ValueError('Exact prepared source-bound packet and index required')
    result = copy.deepcopy(manifest)
    result['input_sha256'].update({p: sha(raw) for p, raw in generated.items()})
    result['azores_2009_section_source_index_v1'] = copy.deepcopy(audit)
    return result
