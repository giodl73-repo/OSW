"""Project reviewed scalar contour summaries and separation days without geography."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/loop-manta-2023-published-metrics-v1.json'
PREPARATION = 'research/loop-published-metrics-preparation-v1.json'
PREPARATION_SHA = '32fbad60a78fdb0d4a4f4bb0f23800861c0b2458e1f12494a2410016d0108402'
PROTOCOL = 'plans/published-current-contour-event-query-protocol-v1.md'
FILE = 'research/loop-published-metrics-query-contract-v1.json'
MODULE = 'analysis/loop_published_metrics_query_v1.py'
TARGET = 'current:loop'
PAPER = 'source:manta-loop-2023'
METHOD = 'source:published-current-contour-event-query-v1'
SUMMARIES = 'current_reported_contour_length_summaries'
EVENTS = 'current_reported_separation_events'
OWNER_FIELDS = {SUMMARIES: ('reported_contour_length_summary_ids', 'reported_contour_length_summaries'),
                EVENTS: ('reported_separation_event_ids', 'reported_separation_events')}


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, indent=2) + '\n').encode()


def fingerprint(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def query_url(collection):
    query = {'collection': collection, 'filters': [{'field': 'entity_id', 'op': 'eq', 'value': TARGET}],
             'sort': {'field': 'date' if collection == EVENTS else 'id', 'direction': 'asc'}, 'limit': 100}
    return 'query.html?q=' + quote(json.dumps(query, separators=(',', ':')))


def source_query(pointer):
    return 'query.html?source-q=' + quote(json.dumps({'document': FACTS, 'pointer': pointer, 'limit': 100}, separators=(',', ':')))


def build_contract(root=ROOT):
    root = Path(root)
    raw = (root / PREPARATION).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PREPARATION_SHA:
        raise ValueError('Changed reviewed Loop source preparation')
    prepared = json.loads(raw)
    if (prepared['figure_png_actually_inspected'] is not True
            or prepared['final_png_matches_actually_inspected_png'] is not True
            or prepared['existing_scalar_statistics_restructured'] != 2
            or prepared['newly_structured_separation_events'] != 12
            or len(prepared['input_sha256']) != 5):
        raise ValueError('Complete reviewed source and visual evidence required')
    for name, expected in prepared['input_sha256'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Changed reviewed Loop source input: ' + name)
    facts = json.loads((root / FACTS).read_bytes())
    if facts['entity_id'] != TARGET or facts['source']['id'] != PAPER:
        raise ValueError('Reviewed Loop source identity changed')
    pins = {**prepared['input_sha256'], PREPARATION: PREPARATION_SHA}
    pins.update({path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in [PROTOCOL, MODULE]})
    common = {'entity_id': TARGET, 'related_current_id': TARGET,
              'source_id': PAPER, 'method_source_id': METHOD, 'source_ids': [PAPER, METHOD],
              'source_url': facts['source']['url'], 'source_file': FACTS, 'source_file_sha256': pins[FACTS],
              'figure_file': facts['delivery']['figure'], 'figure_sha256': pins[facts['delivery']['figure']],
              'evidence_page': facts['delivery']['page'], 'independent_observation_count': 0,
              'rank_eligible': False, 'physical_state_join_eligible': False,
              'geographic_seasonal_playback_eligible': False, 'nasa_identity_verified': False}
    collections = {SUMMARIES: [], EVENTS: [], 'sources': [
        {'id': PAPER, 'kind': 'external', 'title': facts['source']['title'], 'label': 'Manta et al. (2023) Loop Current',
         'doi': facts['source']['doi'], 'url': facts['source']['url'], 'publication_year': 2023,
         'access_scope': facts['source']['access'], 'original_asset_retained': False,
         'original_file_sha256': None, 'source_figures_digitized': False, 'provider_asset_redistributed': False},
        {'id': METHOD, 'kind': 'internal', 'title': 'Published contour statistics and separation-event query rules v1',
         'label': 'Published scalar extraction and event-definition limits', 'path': PROTOCOL,
         'url': '../' + PROTOCOL, 'provider_asset_redistributed': False}
    ]}
    method_labels = ['Demeaned 0.17 m contour', 'Maximum-velocity streamline']
    for index, original in enumerate(facts['length_summaries']):
        pointer = '/length_summaries/' + str(index)
        row = {**copy.deepcopy(common), **copy.deepcopy(original),
               'record_type': 'published_connected_contour_length_summary',
               'label': method_labels[index] + ' — 1993–2021 mean', 'value': original['mean_km'], 'unit': 'km',
               'scope': f"Temporal SD {original['temporal_standard_deviation_km']} km; not measurement error, annual extrema or a mean-axis length.",
               'source_product': copy.deepcopy(facts['source_product']),
               'source_pointer': pointer, 'source_query_url': source_query(pointer),
               'reported_period_start_year': 1993, 'reported_period_end_year': 2021,
               'exact_period_start': None, 'exact_period_end': None,
               'statistical_spread_kind': 'temporal_standard_deviation',
               'statistical_spread_is_uncertainty': False,
               'physical_width_km': None, 'geometry': None, 'sample_date': None}
        collections[SUMMARIES].append(row)
    definition = facts['event_definition']
    for index, original in enumerate(facts['separation_events']):
        pointer = '/separation_events/' + str(index)
        row = {**copy.deepcopy(common), **copy.deepcopy(original),
               'record_type': 'published_algorithm_final_separation_event',
               'label': 'Reported final separation — ' + original['date'], 'value': original['date'], 'unit': '',
               'scope': 'TOEddies final separation; listed overlap subset. Eddy identity, clock time, timezone and footprint unknown.',
               'source_pointer': pointer, 'source_query_url': source_query(pointer),
               'source_locator': definition['locator'], 'detector': definition['detector'],
               'event_type': definition['event_type'], 'event_definition': definition['meaning'],
               'date_precision': definition['date_precision'], 'clock_time': None, 'timezone': None,
               'subset_kind': 'published_mooring_overlap_event_list', 'listed_subset_count': 12,
               'reported_full_period_event_count': 48, 'complete_full_period_event_inventory': False,
               'is_initial_detachment_date': False, 'is_ring_birth_date': False,
               'is_direct_eddy_observation': False, 'physical_width_km': None,
               'latitude_degrees_north': None, 'longitude_degrees_east': None}
        collections[EVENTS].append(row)
    return {'schema': 'osw.published-current-contour-event-query.v1', 'version': 'loop-manta-2023-v1',
            'status': 'PREPARED_SCALAR_EVIDENCE_NOT_INSTALLED_PACKET', 'input_sha256': pins,
            'owner_id': TARGET, 'collections': collections,
            'manifest_fields': {'loop_published_contour_event_version': 'manta-2023-v1'},
            'counts': {'contour_length_summaries': 2, 'reported_final_separation_events': 12,
                       'publication_sources': 1, 'method_sources': 1},
            'example_queries': [
                {'collection': SUMMARIES, 'filters': [{'field': 'entity_id', 'op': 'eq', 'value': TARGET}],
                 'sort': {'field': 'mean_km', 'direction': 'asc'}, 'limit': 100},
                {'collection': EVENTS, 'filters': [{'field': 'entity_id', 'op': 'eq', 'value': TARGET}],
                 'sort': {'field': 'date', 'direction': 'asc'}, 'limit': 100},
                {'collection': EVENTS, 'filters': [{'field': 'date', 'op': 'contains', 'value': '2017-11'}],
                 'sort': {'field': 'date', 'direction': 'asc'}, 'limit': 100}
            ],
            'admission': {'new_current_identities': 0, 'new_eddy_identities': 0, 'ranked_lengths': 0,
                          'physical_widths': 0, 'annual_dimension_ranges': 0,
                          'state_intersections': 0, 'geographic_tracks': 0, 'independent_observations': 0}}


def checked_ids(rows, label):
    if not isinstance(rows, list) or any(not isinstance(r, dict) or not isinstance(r.get('id'), str) or not r['id'] for r in rows):
        raise ValueError('Invalid record list: ' + label)
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)): raise ValueError('Duplicate IDs: ' + label)
    return set(ids)


def normalized_doi(value):
    text = str(value).strip().lower()
    for prefix in ['https://doi.org/', 'http://doi.org/', 'https://dx.doi.org/', 'doi:']:
        if text.startswith(prefix): return text[len(prefix):].strip().rstrip('/')
    return text.rstrip('/')


def provenance(row, registry):
    refs = row.get('source_ids')
    if (not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs)
            or len(refs) != len(set(refs)) or set(refs) - registry):
        raise ValueError('Unresolved prior evidence provenance')
    if row.get('source_id') not in refs or row.get('method_source_id') not in refs:
        raise ValueError('Missing publication or method provenance')


def append(collections, document):
    """Validate before preparing replacements; update the caller only once."""
    if type(collections) is not dict or encoded(document) != encoded(build_contract()):
        raise ValueError('Changed reviewed contour/event query contract')
    objects, entities = collections.get('objects', []), collections.get('entities', [])
    checked_ids(objects, 'objects'); checked_ids(entities, 'entities')
    owners = [r for r in objects if r['id'] == TARGET]
    if (len(owners) != 1 or owners[0].get('type') != 'named_current'
            or sum(r['id'] == TARGET and r.get('type') == 'named_current' for r in entities) != 1):
        raise ValueError('Accepted Loop Current object/entity required')
    rows = document['collections']
    for name in OWNER_FIELDS:
        existing = checked_ids(collections.get(name, []), name)
        if existing & checked_ids(rows[name], 'new ' + name): raise ValueError('Contour/event collision: ' + name)
    old_sources = collections.get('sources', [])
    registry = checked_ids(old_sources, 'sources')
    by_id = {row['id']: row for row in old_sources}
    doi = normalized_doi(rows['sources'][0]['doi'])
    for row in old_sources:
        url = str(row.get('url', '')).lower()
        if (normalized_doi(row.get('doi', '')) == doi or doi in url) and row['id'] != PAPER:
            raise ValueError('Existing publication requires explicit source-registry reconciliation')
    new_sources = []
    for row in rows['sources']:
        if row['id'] in by_id:
            if encoded(row) != encoded(by_id[row['id']]): raise ValueError('Changed source-ID collision')
        else: new_sources.append(copy.deepcopy(row))
    owner = copy.deepcopy(owners[0])
    refs = owner.get('source_ids')
    if (not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs)
            or len(refs) != len(set(refs)) or set(refs) - registry
            or type(owner.get('linked_source_count')) is not int or owner['linked_source_count'] != len(refs)):
        raise ValueError('Invalid prior owner source references/count')
    if (not isinstance(owner.get('capabilities'), dict) or not isinstance(owner.get('evidence_links'), list)
            or not isinstance(owner.get('section_fingerprints'), dict)):
        raise ValueError('Invalid prior owner evidence containers')
    for name, (field, capability) in OWNER_FIELDS.items():
        prior = owner.get(field, [])
        if (not isinstance(prior, list) or any(not isinstance(ref, str) for ref in prior)
                or len(prior) != len(set(prior))): raise ValueError('Invalid prior contour/event owner references')
        available = {row['id']: row for row in collections.get(name, [])}
        for ref in prior:
            if ref not in available or available[ref].get('entity_id') != TARGET:
                raise ValueError('Unresolved prior contour/event owner reference')
            provenance(available[ref], registry)
        owned = {row['id'] for row in available.values() if row.get('entity_id') == TARGET}
        if owned != set(prior): raise ValueError('Prior owned contour/event rows are not all referenced')
        if (prior or capability in owner['capabilities']) and (type(owner['capabilities'].get(capability)) is not int
                or owner['capabilities'][capability] != len(prior)):
            raise ValueError('Prior contour/event capability/count mismatch')
        owner[field] = prior + [row['id'] for row in rows[name]]
        owner['capabilities'][capability] = len(owner[field])
        label = 'Query published contour-length summaries' if name == SUMMARIES else 'Query reported final-separation events'
        owner['evidence_links'].append({'label': label, 'url': query_url(name)})
    combined_registry = registry | {row['id'] for row in new_sources}
    for name in OWNER_FIELDS:
        for row in rows[name]: provenance(row, combined_registry)
    owner['source_ids'] = sorted(set(refs) | {PAPER, METHOD})
    owner['linked_source_count'] = len(owner['source_ids'])
    owner['evidence_links'].append({'label': 'Published Loop Current metrics and event timeline',
                                    'url': 'loop-published-metrics.html'})
    owner['section_fingerprints']['published_contour_events'] = fingerprint({name: rows[name] for name in OWNER_FIELDS})
    owner['fingerprint'] = fingerprint({key: value for key, value in owner.items() if key != 'fingerprint'})
    updates = {name: [*collections.get(name, []), *copy.deepcopy(rows[name])] for name in OWNER_FIELDS}
    updates['sources'] = [*old_sources, *new_sources]
    updates['objects'] = [owner if row['id'] == TARGET else row for row in objects]
    collections.update(updates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    document = build_contract()
    if args.action == 'build': (ROOT / FILE).write_bytes(encoded(document))
    elif (ROOT / FILE).read_bytes() != encoded(document): raise ValueError('Prepared contract differs from source projection')
    print(json.dumps({'status': 'PASS', 'action': args.action, 'counts': document['counts'], 'admission': document['admission']}))


if __name__ == '__main__': main()
