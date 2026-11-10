"""Project frozen, admitted descriptors into a separate preview candidate. No physics."""
import base64
from collections import Counter, defaultdict
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
from compiled_depth_catalog_view_v20 import load_inventory

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.pytest_cache/preview-data-projection-v1'
INPUT = 'almanac/display-data-v1/'
PRIOR_SECONDS = 2.536749197  # Includes a conservative two seconds for failed run 42526800644.
HELD_SOURCE_IDS = {'source:179111cb1095bbc9', 'source:80d0bf24c139328c',
                   'source:a45eadc81e6d9330', 'source:fda01be082655d33'}
HELD_URLS = {'https://www.horizonmarine.com/loop-current-eddies',
             'https://www.ncei.noaa.gov/jag/navy/data/satellite_analysis/nafreddy.zip',
             'https://ocean.weather.gov/gulf_stream_text.php',
             'https://coastwatch.noaa.gov/data/pub0015/coastwatch/rads/sla/2026/rads_global_nrt_sla_20260925_20260926_001.nc'}
MAP_ROLES = {'editorial_locator', 'editorial_reference_route', 'osw_editorial_reference_route',
             'shared_regional_gateway', 'source_geography_locator', 'approximate_reported_center'}
# These are copied source assets or original provider structures, not scope qualifiers.
EXCLUDED_KEYS = {'geometry', 'coordinates', 'projected', 'raw_record', 'raw_text', 'source_text',
                 'source_text_excerpt', 'source_quote', 'quote', 'excerpt', 'transcript',
                 'registry_context', 'registry_row_index', 'registry_column'}
OBJECT_KEYS = {'id', 'label', 'type', 'basin', 'identity_level', 'identity_scope_note', 'scope_notes',
               'state_codes', 'state_evidence', 'source_ids'}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def clean(value):
    """Remove asset payloads and quotations, retaining scalar facts and all scope flags."""
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items() if k not in EXCLUDED_KEYS
                and not re.search(r'(?:quoted_passage|full_text|image_data|native_values|source_prose)', k)}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def refs(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith('source_id') and isinstance(child, str):
                yield child
            elif key.endswith('source_ids') and isinstance(child, list):
                yield from (v for v in child if isinstance(v, str))
            else:
                yield from refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs(child)


def urls(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and (key.endswith('url') or key in {'url', 'doi_url'}):
                yield child
            else:
                yield from urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from urls(child)


def held(value, extra_ids=()):
    return bool(set(refs(value)) & (HELD_SOURCE_IDS | set(extra_ids)) or set(urls(value)) & HELD_URLS)


def source_case_name(row):
    for key in ['independent_named_case', 'named_case_association', 'case_alias_association',
                'source_plot_estimate', 'source_map_estimate', 'model_context', 'detection_context']:
        context = row.get(key)
        if isinstance(context, dict):
            for field in ['source_case_name', 'source_name']:
                if isinstance(context.get(field), str) and context[field].strip():
                    return context[field]
    return None


def bibliographic_context(value):
    """Context registry is bibliography/method metadata, not a copy of source tables."""
    if not isinstance(value, dict):
        return {}
    keep = {'title', 'source_title', 'citation', 'source_citation', 'authors', 'author', 'year',
            'publication_year', 'doi', 'url', 'source_url', 'doi_url', 'source_locator',
            'source_publication', 'licence', 'license', 'source_licence', 'source_license',
            'interpretation', 'scope', 'scope_note', 'qualification', 'method_note'}
    out = {k: clean(v) for k, v in value.items() if k in keep
           or (k.endswith(('url', '_doi', '_citation')) and isinstance(v, str))}
    for key, child in value.items():
        if isinstance(child, dict) and key not in out:
            part = bibliographic_context(child)
            if part:
                out[key] = part
        elif isinstance(child, list) and key not in out:
            parts = [part for item in child if isinstance(item, dict) and (part := bibliographic_context(item))]
            if parts:
                out[key] = parts
    return out


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    started = time.monotonic()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('Carried source-use projection budget')))
    signal.alarm(53)
    save = lambda value: (OUT / 'query-ledger.json').write_bytes(encoded(value))
    query = DescriptorQuery(save, prior_numeric=132931, prior_bytes=15497827)
    read = query.reader(lambda path: (ROOT / path).read_bytes())
    files = {}
    receipts = []
    withheld = Counter()
    missing = defaultdict(set)
    source_uses = defaultdict(set)
    new_source_urls = defaultdict(set)
    metadata = {}

    def put(path, value, compress=False):
        decoded = encoded(value)
        if compress:
            raw = encoded({'schema': 'osw.preview-json-envelope.v1', 'encoding': 'gzip+base64',
                           'decoded_bytes': len(decoded), 'decoded_sha256': digest(decoded),
                           'payload': base64.b64encode(gzip.compress(decoded, mtime=0)).decode('ascii')})
        else:
            raw = decoded
        assert len(raw) < 2_400_000 and len(decoded) < 2_500_000
        assert path not in files
        files[path] = raw
        receipt = {'path': path, 'bytes': len(raw), 'sha256': digest(raw), 'decoded_bytes': len(decoded)}
        receipts.append(receipt)
        return receipt

    with query.decoding():
        build = json.loads(read(INPUT + 'build.json'))
        source_decisions = json.loads(read('research/public-preview-source-use-decisions-v1.json'))
        supplement = json.loads(read('research/public-preview-source-supplement-v1.json'))
        by_path = {r['path']: r for r in build['files']}

        def display(path):
            raw = read(INPUT + path)
            receipt = by_path[path]
            assert len(raw) == receipt['bytes'] and digest(raw) == receipt['sha256']
            return json.loads(raw)

        index = display('index.json')
        depth_manifest_raw = read('research/current-depth-reference-inventory-v57.json')
        assert digest(depth_manifest_raw) == '383b7df1880f008ea140e819b9a24a33963e21b589946876bd8cf77e691ed24b'
        depths = load_inventory(json.loads(depth_manifest_raw), read)
        assert len(depths['evidence']) == 941
        depth_by_owner = defaultdict(list)
        for row in depths['evidence']:
            depth_by_owner[row['entity_id']].append(row)
        contexts = {key: bibliographic_context(value) for key, value in depths['source_contexts'].items()}
        for context in contexts.values():
            for url in urls(context):
                new_source_urls[url].add('current_depth_context')
        put('depth-contexts.json', {'schema': 'osw.preview-depth-contexts.v1', 'contexts': contexts}, True)
        nasa_root = 'almanac/release/v0.1.0-rights-screened-preview/'
        nasa_tiles = json.loads(read(nasa_root + 'tiles.json'))
        nasa_state_relations = json.loads(read(nasa_root + 'tile_state_relations.json'))
        old_entities = json.loads(read(nasa_root + 'entities.json'))
        states = [{k: r[k] for k in ['id', 'type', 'label', 'state_code'] if k in r}
                  for r in old_entities if r.get('type') == 'osw_state']
        assert len(nasa_tiles) == 70 and states
        put('nasa-navigation.json', {'schema': 'osw.preview-nasa-navigation.v1', 'tiles': nasa_tiles,
                                    'tile_state_relations': nasa_state_relations, 'states': states,
                                    'interpretation': 'NASA modeled-motion navigation. Tile/state overlaps are display overlaps, not evidence that NASA identified a named current or eddy.'}, True)
        decisions = {r['id']: r for r in source_decisions['entries']}
        # Dataset rows retain bibliography only until the particular value use is reviewed.
        held_datasets = {key for key, row in decisions.items() if row['disposition'] == 'dataset_reuse_review_required'}
        supplement_sources = {s['id']: s for s in supplement['entries']}
        entries = []
        counts = Counter()
        joined_depth_count = 0
        emitted_depth_units = Counter()
        all_sources = dict(supplement_sources)
        for entry in index['entries']:
            record = display(entry['record']['path'])
            obj = record['object']
            if obj['type'] == 'operational_eddy_detection' or (
                    obj['type'] == 'named_eddy' and 'source:a45eadc81e6d9330' in obj.get('source_ids', [])):
                withheld['provider_identity_records'] += 1
                continue
            identifier = record['id']
            sources = {s['id']: clean(s) for s in record['sources'] if s['id'] not in HELD_SOURCE_IDS}
            sources.update({k: v for k, v in supplement_sources.items() if k in set(refs(record))})
            all_sources.update(sources)
            public = {'schema': 'osw.preview-record.v1', 'id': identifier,
                      'object': {k: clean(v) for k, v in obj.items() if k in OBJECT_KEYS},
                      'measurements': [], 'widths': [], 'reference_routes': [],
                      'depth_references': [], 'sources': []}
            public['object']['source_ids'] = [s for s in obj.get('source_ids', []) if s not in HELD_SOURCE_IDS]
            for field in ['measurements', 'widths', 'reference_routes']:
                for row in record[field]:
                    if held(row, held_datasets):
                        withheld[field] += 1
                        continue
                    public[field].append(clean(row))
            for row in depth_by_owner.get(identifier, []):
                if held(row):
                    withheld['depth_references'] += 1
                    continue
                public['depth_references'].append(clean(row))
                joined_depth_count += 1
                emitted_depth_units[row['unit']] += 1
                context_id = row.get('source_context_id')
                if context_id and context_id not in contexts:
                    missing[context_id].add(identifier)
                for url in urls(row):
                    new_source_urls[url].add('current_depth_reference')
            # Retain every required source row, including the missing-context supplement.
            for source_id in sorted(set(refs(public))):
                if source_id in sources:
                    public['sources'].append(sources[source_id])
                    source_uses[source_id].add(identifier)
                elif not any(source_id in set(refs(context)) for context in contexts.values()):
                    # Some admitted depth rows have their own bibliography or context.
                    relevant = [r for r in public['depth_references'] if source_id in set(refs(r))]
                    if not relevant or not all(r.get('source_context_id') in contexts or list(urls(r)) for r in relevant):
                        missing[source_id].add(identifier)
            public['source_context_ids'] = sorted({r['source_context_id'] for r in public['depth_references'] if r.get('source_context_id')})
            public['publication_scope'] = 'Candidate projection; selected facts only. No underlying source media or provider files.'
            geometry = [f for f in entry['display_features'] if f.get('role') in MAP_ROLES and not f.get('omitted_reason') and not held(f)]
            withheld['map_features'] += len(entry['display_features']) - len(geometry)
            receipt = put('records/' + digest(identifier.encode())[:24] + '.json', public, True)
            entries.append({k: entry[k] for k in ['id', 'label', 'type', 'basin', 'identity_level'] if k in entry} |
                           {'display_features': geometry, 'record': receipt,
                            'depth_reference_count': len(public['depth_references'])})
            counts[obj['type']] += 1
        assert counts['named_current'] == 111
        assert {r['id'] for r in entries if r['type'] == 'named_current'} == {r['id'] for r in index['entries'] if r['type'] == 'named_current'}
        assert joined_depth_count + withheld['depth_references'] == 941
        register_raw = read('research/eddy-measurement-register-v1.json')
        register = json.loads(register_raw)
        case_rows = []
        for row in register['evidence']:
            if row.get('evidence_role') == 'registry_source_reference' or held(row) or not row.get('source_url'):
                withheld['eddy_reference_rows'] += 1
                continue
            factual = clean(row)
            # This namespace describes a source reference, not the research registry owner.
            factual.pop('entity_id', None)
            original_id = factual.pop('id')
            public_id = 'source-reference:eddy:' + digest(original_id.encode())[:24]
            case_rows.append({'id': public_id, 'source_case_name': source_case_name(row),
                              'record_kind': 'source_scoped_evidence_reference_not_canonical_eddy',
                              'registry_identity_join_verified': False,
                              'original_reference_id_sha256': digest(original_id.encode()),
                              'reference': factual})
            new_source_urls[row['source_url']].add('eddy_factual_reference')
        # Chunk by bounded rows for lazy evidence browsing; not new scientific acquisition.
        case_receipts = []
        for offset in range(0, len(case_rows), 50):
            case_receipts.append(put(f'eddy-references/{offset // 50:03d}.json',
                                     {'schema': 'osw.preview-eddy-references.v1', 'references': case_rows[offset:offset + 50]}, True))
        put('index.json', {'schema': 'osw.preview-display-index.v1', 'entries': entries, 'counts': dict(counts),
                           'depth_reference_count': joined_depth_count, 'depth_reference_units': dict(emitted_depth_units),
                           'eddy_source_reference_count': len(case_rows), 'eddy_reference_parts': case_receipts,
                           'snapshot_is_live': False, 'not_a_count_of_distinct_physical_eddies': True})
        metadata = {'schema': 'osw.preview-data-projection.v1',
                    'status': 'CANDIDATE_REQUIRES_SOURCE_RECONCILIATION_AND_BUNDLE_REVIEW',
                    'source_commit': os.environ['GITHUB_SHA'], 'prior_active_seconds': PRIOR_SECONDS,
                    'input_display_build_sha256': digest((ROOT / INPUT / 'build.json').read_bytes()),
                    'depth_manifest_sha256': digest(depth_manifest_raw), 'eddy_register_sha256': digest(register_raw),
                    'counts': dict(counts), 'depth_reference_count': joined_depth_count,
                    'depth_reference_units': dict(emitted_depth_units),
                    'eddy_reference_count': len(case_rows),
                    'eddy_size_reference_count': sum(r['reference'].get('category') == 'size' for r in case_rows),
                    'withheld': dict(withheld), 'unresolved_required_sources': {k: sorted(v) for k, v in missing.items()},
                    'additional_factual_source_uses_to_review': [{'url': url, 'uses': sorted(uses)} for url, uses in sorted(new_source_urls.items())],
                    'depth_context_ids': sorted(contexts), 'depth_contexts_without_bibliographic_metadata': [k for k, v in contexts.items() if not v],
                    'state_association_source_review_required': True,
                    'nasa_navigation_tiles': len(nasa_tiles), 'osw_state_names': len(states),
                    'source_ids_used': sorted(source_uses), 'files': receipts,
                    'numeric_values_recalculated': False, 'native_provider_requests': 0,
                    'scientific_claim_review_granted': False, 'publication_approved': False,
                    'physical_current_volume_estimates': 0, 'whole_route_depth_profiles': 0}
    # The package is UTF-8 JSON only, compatible with the existing exact-tree publisher.
    total = sum(map(len, files.values()))
    assert total < 2_300_000, ('Encoded preview package output cap', total)
    metadata['encoded_package_bytes'] = total
    metadata['decoded_package_bytes'] = sum(r['decoded_bytes'] for r in receipts)
    metadata['active_seconds'] = time.monotonic() - started
    metadata['cumulative_active_seconds'] = PRIOR_SECONDS + metadata['active_seconds']
    assert metadata['cumulative_active_seconds'] < 59
    report = encoded(metadata)
    assert total + len(report) + (OUT / 'query-ledger.json').stat().st_size < 2_400_000
    (OUT / 'result.json').write_bytes(report)
    with zipfile.ZipFile(OUT / 'package.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, raw in sorted(files.items()):
            info = zipfile.ZipInfo(path, date_time=(2026, 11, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw)
    signal.alarm(0)
    print(json.dumps({'status': metadata['status'], 'counts': dict(counts), 'depth_references': joined_depth_count,
                      'eddy_references': len(case_rows), 'package_bytes': total,
                      'unresolved_sources': len(missing), 'active_seconds': metadata['active_seconds']}))


if __name__ == '__main__':
    main()
