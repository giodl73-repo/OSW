"""Versioned identity-JSON transport; frozen v1 native-array method unchanged."""
import argparse
import copy
import gzip
import hashlib
import json

from angola_nansen_native_sections import (
    ROOT, REPORT as LEGACY_REPORT, calculate as native_calculate,
    encoded, reserve,
)

REPORT = 'research/angola-nansen-native-sections-v2.json'
PREFLIGHT = 'research/angola-nansen-native-sections-preflight-v2.json'
PROTOCOL = 'plans/angola-nansen-portable-transport-protocol-v2.md'
OPERATOR = 'analysis/angola_nansen_portable_sections_v2.py'
TEST = 'analysis/test_angola_nansen_portable_sections_v2.py'
MIRRORS = 'research/angola-nansen-query-source-manifest-v1.json'
DIAGNOSTIC = 'research/angola-nansen-native-v1-linux-transport-diagnostic.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonicalize(retained, rebuilt, products, mirrors, read):
    """Require full native equality; isolate only legacy compression receipts."""
    a, b = copy.deepcopy(retained), copy.deepcopy(rebuilt)
    for report in (a, b):
        for section in report['sections']:
            del section['field_sha256']
            del section['field_bytes']
    if a != b:
        raise ValueError('Native report differs beyond compressed hash and size')
    old_paths = [s['field_file'] for s in retained['sections']]
    if len(set(old_paths)) != len(old_paths) or set(products) != set(old_paths):
        raise ValueError('Incomplete or duplicate native field inventory')
    mapping = {r['compressed_source_file']: r for r in mirrors}
    if len(mapping) != len(mirrors) or set(mapping) != set(old_paths):
        raise ValueError('Incomplete or duplicate canonical source mirrors')
    if len({r['source_file'] for r in mirrors}) != len(mirrors):
        raise ValueError('Canonical source files must be distinct')
    result = copy.deepcopy(rebuilt)
    custody = []
    for old, section in zip(retained['sections'], result['sections']):
        path = old['field_file']
        packed = read(path)
        if sha(packed) != old['field_sha256'] or len(packed) != old['field_bytes']:
            raise ValueError('Changed retained v1 compressed artifact')
        raw = gzip.decompress(products[path])
        mirror = mapping[path]
        if (sha(raw) != old['decoded_sha256'] or len(raw) != old['decoded_bytes']
                or gzip.decompress(packed) != raw):
            raise ValueError('Changed complete native decoded field')
        if (mirror['section_id'] != old['id']
                or mirror['compressed_source_sha256'] != old['field_sha256']
                or mirror['source_sha256'] != sha(raw)
                or mirror['source_bytes'] != len(raw)
                or read(mirror['source_file']) != raw):
            raise ValueError('Changed canonical identity-JSON source field')
        section.update(field_file=mirror['source_file'], field_sha256=sha(raw),
                       field_bytes=len(raw), field_encoding='identity-json')
        custody.append({k: old[k] for k in (
            'id', 'field_file', 'field_sha256', 'field_bytes',
            'decoded_sha256', 'decoded_bytes')})
    result.update(schema='osw.angola-nansen-native-sections.v2',
                  field_encoding='identity-json',
                  legacy_compressed_artifact_custody=custody,
                  native_decoded_fields_rebuilt_exactly=True,
                  legacy_compressed_reencoding_claimed=False)
    return result


def input_pins():
    paths = {LEGACY_REPORT, MIRRORS, DIAGNOSTIC, PROTOCOL, OPERATOR, TEST}
    legacy = json.loads((ROOT / LEGACY_REPORT).read_bytes())
    paths.update(legacy['input_sha256'])
    paths.update(s['field_file'] for s in legacy['sections'])
    mirrors = json.loads((ROOT / MIRRORS).read_bytes())
    paths.update(row['source_file'] for row in mirrors['documents'])
    return {path: sha((ROOT / path).read_bytes()) for path in sorted(paths)}


def declare():
    if (ROOT / PREFLIGHT).exists() or (ROOT / REPORT).exists():
        raise ValueError('Retain existing declaration/products; use a new version')
    declaration = {
        'schema': 'osw.angola-nansen-native-preflight.v2',
        'input_sha256': input_pins(),
        'actual_v2_compilation_performed': False,
        'prior_v1_arrays_and_compression_failure_inspected': True,
        'new_scientific_measurement_method': False,
        'physical_width_admitted': False,
    }
    (ROOT / PREFLIGHT).write_bytes(encoded(declaration))
    return declaration


def build():
    reserve()
    declaration = json.loads((ROOT / PREFLIGHT).read_bytes())
    if (declaration['input_sha256'] != input_pins()
            or declaration['actual_v2_compilation_performed'] is not False):
        raise ValueError('Changed prospective v2 transport inputs')
    retained = json.loads((ROOT / LEGACY_REPORT).read_bytes())
    rebuilt, products = native_calculate()
    mirrors = json.loads((ROOT / MIRRORS).read_bytes())
    result = canonicalize(retained, rebuilt, products, mirrors['documents'],
                          lambda path: (ROOT / path).read_bytes())
    result.update(
        legacy_report=LEGACY_REPORT,
        legacy_report_sha256=sha((ROOT / LEGACY_REPORT).read_bytes()),
        transport_protocol=PROTOCOL,
        supersession_reason='Compression-library-dependent v1 gzip reencoding; complete native JSON bytes unchanged.',
        input_sha256={**input_pins(), PREFLIGHT: sha((ROOT / PREFLIGHT).read_bytes())},
    )
    return result


def verify():
    result = build()
    if (ROOT / REPORT).read_bytes() != encoded(result):
        raise ValueError('Changed complete portable v2 source report')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['declare', 'build', 'check'])
    args = parser.parse_args()
    if args.action == 'declare':
        declare()
    elif args.action == 'check':
        verify()
    else:
        if (ROOT / REPORT).exists():
            raise ValueError('Retain existing scientific products; use check')
        (ROOT / REPORT).write_bytes(encoded(build()))
    print('Completed portable native-section action:', args.action)
