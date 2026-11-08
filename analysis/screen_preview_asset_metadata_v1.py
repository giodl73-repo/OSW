"""Check UI asset custody and splice identity metadata; numerical evidence stays opaque."""
import base64
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import time
import zipfile

from compiled_depth_catalog_query_guard_v3 import DescriptorQuery

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'almanac/preview-data-candidate-v1'
OUT = ROOT / '.pytest_cache/preview-asset-metadata-v1'
STRINGS = re.compile(rb'"(?:[^"\\]|\\.)*"')
ALLOWED_STATE_KINDS = {'editorial_coastal_reference_curve', 'shared_regional_gateway',
                       'reported_center_point', 'source_geography_locator', 'source_reported_position',
                       'dated_ssh_contour_proxy'}
HELD_URLS = {'https://www.horizonmarine.com/loop-current-eddies',
             'https://www.ncei.noaa.gov/jag/navy/data/satellite_analysis/nafreddy.zip',
             'https://ocean.weather.gov/gulf_stream_text.php',
             'https://coastwatch.noaa.gov/data/pub0015/coastwatch/rads/sla/2026/rads_global_nrt_sla_20260925_20260926_001.nc'}
FORBIDDEN_KEYS = {'raw_record', 'raw_text', 'source_text', 'source_text_excerpt', 'source_quote',
                  'geometry', 'coordinates', 'native_values', 'registry_separation_date', 'registry_date',
                  'registry_row_index', 'registry_column', 'raw_profiles', 'raw_profile'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf8')


def object_span(raw):
    """Locate one JSON object's byte frame, skipping quoted text without decoding quantities."""
    match = re.search(rb'"object"\s*:\s*\{', raw)
    if not match:
        raise ValueError('Missing identity metadata object')
    start = match.end() - 1
    depth = 0
    quoted = escaped = False
    for offset in range(start, len(raw)):
        c = raw[offset]
        if quoted:
            if escaped:
                escaped = False
            elif c == 92:
                escaped = True
            elif c == 34:
                quoted = False
        elif c == 34:
            quoted = True
        elif c == 123:
            depth += 1
        elif c == 125:
            depth -= 1
            if depth == 0:
                return start, offset + 1
    raise ValueError('Unclosed identity metadata object')


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    started = time.monotonic()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('Carried metadata screening deadline')))
    signal.alarm(50)
    # These are administrative manifests/decisions; never load the admitted measurement catalogs.
    build_raw = (SOURCE / 'build.json').read_bytes()
    build = json.loads(build_raw)
    review_manifest = json.loads((ROOT / 'almanac/preview-review-v1/manifest.json').read_bytes())
    assert review_manifest['candidate_build_sha256'] == sha(build_raw)
    decisions = json.loads((ROOT / 'almanac/preview-review-v1/source-use.json').read_bytes())
    existing = json.loads((ROOT / 'research/public-preview-source-use-decisions-v1.json').read_bytes())
    allowed_urls = {r['url'] for r in decisions['entries']} | {r['url'] for r in existing['entries'] if r.get('url')}
    save = lambda doc: (OUT / 'query-ledger.json').write_bytes(encode(doc))
    query = DescriptorQuery(save, prior_numeric=247336, prior_bytes=29547419)
    files = {}
    receipts = []
    denied_keys = Counter()
    unknown_urls = set()
    held_urls = set()
    removed_states = Counter()
    all_keys = set()
    changed_records = []
    protected = []

    def audit_strings(raw):
        for token in STRINGS.finditer(raw):
            pos = token.end()
            while pos < len(raw) and raw[pos] in b' \t\r\n':
                pos += 1
            if pos == len(raw) or raw[pos] != 58:
                continue
            key = json.loads(token.group())  # JSON key metadata only, never numerical values.
            all_keys.add(key)
            if key in FORBIDDEN_KEYS:
                denied_keys[key] += 1
            pos += 1
            while pos < len(raw) and raw[pos] in b' \t\r\n':
                pos += 1
            if key.endswith('url') and pos < len(raw) and raw[pos] == 34:
                value_token = STRINGS.match(raw, pos)
                if value_token:
                    url = json.loads(value_token.group())  # One bibliographic URL string.
                    if url in HELD_URLS or 'MUNSTER_v1_eddyident_' in url or ('arcgis.com' in url and '/FeatureServer/' in url):
                        held_urls.add(url)
                    elif url.startswith(('http://', 'https://')) and url not in allowed_urls:
                        unknown_urls.add(url)

    with query.decoding():
        for receipt in build['files']:
            path = receipt['path']
            raw = (SOURCE / path).read_bytes()
            assert len(raw) == receipt['bytes'] and sha(raw) == receipt['sha256']
            # The projected index is copied as opaque, previously checked Rust output.
            # It has no state-association metadata and requires no numerical re-decoding.
            if path == 'index.json':
                result = raw
            else:
                envelope = json.loads(raw)
                assert envelope['schema'] == 'osw.preview-json-envelope.v1' and envelope['encoding'] == 'gzip+base64'
                decoded = gzip.decompress(base64.b64decode(envelope['payload'], validate=True))
                assert len(decoded) == envelope['decoded_bytes'] < 2_500_000 and sha(decoded) == envelope['decoded_sha256']
                # Intentionally do not JSON-decode the scientific record. Evidence bytes
                # outside its identity metadata are copied and checked byte for byte.
                audit_strings(decoded)
                if path.startswith('records/'):
                    start, end = object_span(decoded)
                    metadata = json.loads(decoded[start:end])
                    assert set(metadata) <= {'id', 'label', 'type', 'basin', 'identity_level',
                                             'identity_scope_note', 'scope_notes', 'state_codes',
                                             'state_evidence', 'source_ids'}
                    states = metadata.get('state_evidence', [])
                    allowed = []
                    for state in states:
                        if state['kind'] in ALLOWED_STATE_KINDS:
                            allowed.append(state)
                        else:
                            removed_states[state['kind']] += 1
                    if len(allowed) != len(states):
                        metadata['state_evidence'] = allowed
                        metadata['state_codes'] = sorted({r['state_code'] for r in allowed})
                        replacement = encode(metadata)
                        changed = decoded[:start] + replacement + decoded[end:]
                        assert changed[:start] == decoded[:start] and changed[start + len(replacement):] == decoded[end:]
                        protected.append({'path': path, 'evidence_bytes_sha256': sha(decoded[:start] + decoded[end:]),
                                          'evidence_bytes_unchanged': True})
                        decoded = changed
                        changed_records.append(path)
                        result = encode({'schema': envelope['schema'], 'encoding': envelope['encoding'],
                                         'decoded_bytes': len(decoded), 'decoded_sha256': sha(decoded),
                                         'payload': base64.b64encode(gzip.compress(decoded, mtime=0)).decode('ascii')})
                    else:
                        protected.append({'path': path, 'evidence_bytes_sha256': sha(decoded[:start] + decoded[end:]),
                                          'evidence_bytes_unchanged': True})
                        result = raw
                else:
                    result = raw
            files[path] = result
            receipts.append({'path': path, 'bytes': len(result), 'sha256': sha(result)})
    status = ('PASS_ASSET_METADATA_SCREEN_ONLY' if not denied_keys and not held_urls and not unknown_urls
              else 'ASSET_METADATA_RECONCILIATION_REQUIRED')
    report = {'schema': 'osw.preview-asset-metadata.v1', 'status': status, 'source_commit': os.environ['GITHUB_SHA'],
              'input_build_sha256': sha(build_raw), 'input_projection_source': build['source_commit'],
              'counts_from_pinned_build': {k: build[k] for k in ['counts', 'depth_reference_count', 'depth_reference_units', 'eddy_reference_count', 'eddy_size_reference_count']},
              'removed_state_associations_by_kind': dict(removed_states), 'changed_records': changed_records,
              'forbidden_field_names': dict(denied_keys), 'held_source_urls': sorted(held_urls),
              'unreviewed_source_urls': sorted(unknown_urls), 'inspected_key_names': sorted(all_keys),
              'evidence_byte_protection': protected, 'files': receipts,
              'scientific_numerical_values_decoded_or_recalculated': False, 'new_provider_requests': 0,
              'index_projection_bytes_unchanged': True, 'prior_active_seconds': 4.535214145,
              'active_seconds': time.monotonic() - started, 'publication_approved': False,
              'interpretation': 'Metadata/asset screen only. Numerical evidence remains opaque and unchanged. Unknown observed-center and provider-polygon state assertions are withheld. Counts are carried from the verified input build, not recalculated scientific claims.'}
    report['cumulative_active_seconds'] = report['prior_active_seconds'] + report['active_seconds']
    assert report['cumulative_active_seconds'] < 59
    report_raw = encode(report)
    assert sum(map(len, files.values())) + len(report_raw) + (OUT / 'query-ledger.json').stat().st_size < 2_400_000
    (OUT / 'result.json').write_bytes(report_raw)
    with zipfile.ZipFile(OUT / 'package.zip', 'w') as archive:
        for path, raw in sorted(files.items()):
            info = zipfile.ZipInfo(path, date_time=(2026, 11, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw)
    signal.alarm(0)
    print(json.dumps({'status': status, 'changed_identity_metadata_records': len(changed_records),
                      'withheld_state_kinds': dict(removed_states), 'unreviewed_urls': len(unknown_urls),
                      'forbidden_keys': dict(denied_keys), 'active_seconds': report['active_seconds']}))
    if status != 'PASS_ASSET_METADATA_SCREEN_ONLY':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
