"""Prepare an atomic four-identity extension for the next coherent atlas build."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import unicodedata
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REVIEW = 'research/indian-coastal-current-identity-review-v1.json'
REVIEW_SHA = '809b77e2328106d7504e4b251530e74dff5c8d62929a6277c4938356400503ff'
FILE = 'research/indian-current-identity-query-contract-v1.json'
PLANNING = 'research/indian-current-reference-route-planning-v1.json'
PRIMARY = 'source:indian-coastal-identities-vinayachandran-2021'
VARIANTS = 'source:indian-coastal-spellings-madkaiker-2024'
EXPECTED = (
    'current:west-india-coastal', 'current:east-india-coastal',
    'current:east-african-coastal', 'current:south-java',
)
EMPTY_CAPABILITIES = (
    'dated_diagnostics', 'flow_network', 'geometry', 'observed_velocity',
    'passage_transport', 'radius_evidence', 'reference_route', 'reported_length',
    'scope_notes', 'scoped_width', 'source_connectivity', 'time_samples', 'width_samples',
)


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


def pin(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def normalized(label):
    return ' '.join(unicodedata.normalize('NFKC', label).casefold().split())


def query_url(collection, identity):
    request = {'collection': collection, 'filters': [{'field': 'id', 'op': 'eq', 'value': identity}], 'limit': 1}
    return 'query.html?q=' + quote(json.dumps(request, separators=(',', ':')), safe='')


def build_contract():
    if pin(REVIEW) != REVIEW_SHA:
        raise ValueError('Frozen identity review differs; new review/version required')
    review = json.loads((ROOT / REVIEW).read_bytes())
    if pin(review['candidate_file']) != review['candidate_sha256'] or pin(review['protocol_file']) != review['protocol_sha256']:
        raise ValueError('Frozen identity support differs')
    if pin(review['source_original_file']) != review['source_original_sha256']:
        raise ValueError('Named-current original differs')
    if (ROOT / review['source_original_file']).stat().st_size != review['source_original_bytes']:
        raise ValueError('Named-current original size differs')
    if tuple(row['proposed_entity_id'] for row in review['decisions']) != EXPECTED:
        raise ValueError('Prepared identity scope changed')
    planning = json.loads((ROOT / PLANNING).read_bytes())
    if planning['source_review_file'] != REVIEW or planning['source_review_sha256'] != REVIEW_SHA:
        raise ValueError('Route gap worklist review differs')
    plans = {row['current_id']: row for row in planning['entries']}
    if len(plans) != 4 or set(plans) != {value.removeprefix('current:') for value in EXPECTED}:
        raise ValueError('Incomplete prepared route-gap inventory')
    paths = {
        REVIEW, PLANNING, review['candidate_file'], review['protocol_file'],
        review['source_original_file'], 'analysis/indian_current_identity_query.py',
        'research/source-data/vinayachandran-indian-upwelling-2021/acquisition.json',
    }
    additions = {key: [] for key in ('entities', 'names', 'sources', 'length_assessments', 'current_identity_admissions', 'objects', 'route_decisions')}
    additions['sources'] = [
        {'id': PRIMARY, 'kind': 'external', 'label': review['source_title'],
         'title': review['source_title'], 'doi': review['source_doi'],
         'url': 'https://bg.copernicus.org/articles/18/5967/2021/',
         'source_kind': review['source_kind'], 'access_scope': review['source_access_mode'],
         'original_file': review['source_original_file'], 'original_sha256': review['source_original_sha256'],
         'document_identity_sha256': review['source_original_sha256'],
         'original_bytes': review['source_original_bytes'], 'provider_asset_redistributed': True,
         'license': 'CC-BY-4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
         'rights_policy_url': review['protocol_file'],
         'metadata_note': 'Scoped identity reference to a retained published review, not a new independent document or observation.'},
        {'id': VARIANTS, 'kind': 'external', 'label': review['additional_qualitative_source']['title'],
         'title': review['additional_qualitative_source']['title'],
         'doi': review['additional_qualitative_source']['doi'], 'url': review['additional_qualitative_source']['url'],
         'access_scope': review['additional_qualitative_source']['access_mode'],
         'source_locator': review['additional_qualitative_source']['locator'],
         'provider_asset_redistributed': False, 'original_sha256': None,
         'rights_policy_url': review['protocol_file'],
         'metadata_note': 'Linked, attributed spelling and identity context from publisher HTML; its transport integration domain is not a current width.'},
    ]
    for decision in review['decisions']:
        identity = decision['proposed_entity_id']
        slug = identity.removeprefix('current:')
        admission_id = 'current_admission:' + slug
        refs = [PRIMARY] + ([VARIANTS] if decision['name_variants'] else [])
        entity = {
            'id': identity, 'label': decision['preferred_name'], **decision['proposed_facets'],
            'identity_level': decision['identity_level'], 'source_id': PRIMARY,
            'source_record_id': slug, 'source_kind': review['source_kind'],
            'identity_scope_note': decision['source_geographic_description'] + '. ' + decision['source_qualitative_flow_support'],
            'source_locator': decision['source_definition_locator'],
            'identity_admission_id': admission_id, 'catalogue_version': '0.2.0-draft-indian-coastal',
            'almanac_url': 'object.html?id=' + quote(identity, safe=''),
        }
        additions['entities'].append(entity)
        plan = plans[slug]
        if (plan['name'] != entity['label'] or plan['existing_scope'] != entity['identity_scope_note']
                or plan['candidate_ids'] != [] or plan['geometry'] is not None
                or plan['published_length_rank_eligible'] is not False or plan['rank_eligible'] is not False
                or plan['naming_source_is_route_geometry_evidence'] is not False
                or plan['reference_path_decision'] != 'not_constructed_source_axis_and_endpoints_unresolved'):
            raise ValueError('Route gap worklist promoted geography or dimensions')
        names = [(decision['preferred_name'], 'preferred', PRIMARY, True),
                 (decision['abbreviation'], 'abbreviation', PRIMARY, False)]
        names.extend((row['label'], 'spelling', VARIANTS, False) for row in decision['name_variants'])
        for label, role, source, preferred in names:
            additions['names'].append({'id': f'name:{identity}:{role}', 'entity_id': identity,
                'label': label, 'preferred': preferred, 'name_role': role, 'source_id': source})
        additions['length_assessments'].append({
            'id': 'length_assessment:' + slug, 'entity_id': identity, 'source_id': PRIMARY,
            'source_locator': decision['source_definition_locator'], 'evidence_status': 'identity_only_dimensions_not_admitted',
            'rank_eligible': False, 'published_length_km': None, 'published_rank': None,
            'lower_bound_km': None, 'proposed_system_length_km': None,
            'scope': 'Separately named current; identity admission supplies no length, width, observed axis or annual envelope.',
        })
        additions['current_identity_admissions'].append({
            'id': admission_id, 'entity_id': identity, 'proposal_id': slug,
            'entity': copy.deepcopy(entity), 'route_planning_decision': copy.deepcopy(plan),
            'status': 'editorial_identity_admitted_measurements_separately_gated',
            'source_id': PRIMARY, 'source_ids': refs, 'source_review_file': REVIEW,
            'source_review_sha256': REVIEW_SHA, 'source_locator': decision['source_definition_locator'],
            'distinguished_from': copy.deepcopy(decision['distinguished_from']),
            'classification_basis': decision['facet_method'],
            'source_qualitative_flow_support': decision['source_qualitative_flow_support'],
            'canonical_measurements_admitted': False, 'external_scientific_review_claimed': False,
            'rank_eligible': False, 'physical_edges_admitted': False, 'seasonal_playback_eligible': False,
            'geometry': None, 'annual_width_range_km': None, 'annual_length_range_km': None,
        })
        owner = {key: copy.deepcopy(entity[key]) for key in ('id', 'label', 'type', 'basin', 'setting', 'time_behavior', 'identity_level', 'source_kind')}
        owner.update(
            identity_scope_note=entity['identity_scope_note'], vertical_setting=entity['vertical_setting'],
            source_ids=sorted(refs), linked_source_count=len(refs),
            capabilities={key: 0 for key in EMPTY_CAPABILITIES},
            dashboard_search=entity['label'] + ' ' + entity['basin'],
            search_aliases=[label for label, _, _, _ in names if label != entity['label']],
            object_url=entity['almanac_url'], route_url=None,
            season_url='seasons.html?current=' + quote(slug, safe=''),
            published_length_km=None, latest_observation_date=None, recorded_claims=0,
            nasa_links=0, claim_review_counts={},
            evidence_links=[{'label': 'Query the separate identity and scope', 'url': query_url('current_identity_admissions', admission_id)},
                            {'label': 'Read the naming source', 'url': query_url('sources', PRIMARY)}],
        )
        for field in ('connections', 'current_section_ids', 'diagnostic_ids', 'map_features', 'measurement_ids',
                      'route_decision_ids', 'route_ids', 'scope_notes', 'series', 'state_codes', 'state_evidence',
                      'velocity_sample_ids', 'width_ids', 'width_sample_ids'):
            owner[field] = []
        route_id = 'route-decision:' + slug
        owner['route_decision_ids'] = [route_id]
        owner['evidence_links'].append({'label': 'Query the unresolved reference-route work', 'url': query_url('route_decisions', route_id)})
        additions['route_decisions'].append({
            'id': route_id, 'entity_id': identity, 'current_id': slug, 'label': plan['name'],
            'strategy_id': plan['route_strategy_id'], 'strategy_label': plan['route_strategy_label'],
            'construction_status': plan['reference_path_decision'], 'candidate_count': 0, 'route_ids': [],
            'next_action': plan['next_action'], 'scope': plan['existing_scope'], 'status': plan['planning_status'],
            'rank_eligible': False, 'source_url': plan['name_source_url'], 'source_id': PRIMARY,
            'source_decision': copy.deepcopy(plan), 'source_catalog_file': PLANNING,
            'source_catalog_sha256': pin(PLANNING), 'scope_reviews': [],
        })
        groups = {
            'identity': entity,
            'sources': [row for row in additions['sources'] if row['id'] in refs],
            'claims': [], 'measurements': [[], [], None],
            'routes_geometry': [[], [], [], []], 'media': [],
            'time_evidence': [[], None, None, None],
        }
        owner['section_fingerprints'] = {key: fingerprint(value) for key, value in groups.items()}
        owner['fingerprint'] = fingerprint(owner)
        additions['objects'].append(owner)
    return {
        'schema': 'osw.indian-current-identity.query-contract.v1',
        'status': 'prepared_extension_not_yet_in_canonical_bundle',
        'canonical_delivery_verified': False, 'proposed_entity_ids': list(EXPECTED),
        'unresolved_candidate': copy.deepcopy(review['unresolved_candidate']),
        'input_sha256': {path: pin(path) for path in sorted(paths)},
        'additions': additions,
        'next_gate': 'Integrate entities before taxonomy/dashboard/seasonal inventory, then project the qualified evidence and complete native/WASM/UI parity in one coherent build.',
    }


def evidence():
    document = build_contract()
    if encoded(document) != (ROOT / FILE).read_bytes():
        raise ValueError('Stale prepared Indian identity query contract')
    return document, {**document['input_sha256'], FILE: pin(FILE)}


def append(collections, document):
    """Apply an already source-verified contract atomically, preserving older rows.

    The caller obtains document through evidence() first. The saved contract
    must still match. Applying to a rehearsal does not publish the bundle.
    """
    if encoded(document) != (ROOT / FILE).read_bytes():
        raise ValueError('Unverified Indian identity query contract')
    rows = document['additions']
    existing_entities = collections.get('entities', [])
    entity_ids = {row['id'] for row in existing_entities}
    for admission in rows['current_identity_admissions']:
        if any(item['entity_id'] not in entity_ids for item in admission['distinguished_from']):
            raise ValueError('Missing distinguished existing current identity')
    old_names = {}
    for row in [*existing_entities, *collections.get('names', [])]:
        if row.get('label'):
            old_names.setdefault(normalized(row['label']), set()).add(row.get('entity_id', row['id']))
    for row in rows['names']:
        if normalized(row['label']) in old_names:
            raise ValueError('Existing name requires explicit identity reconciliation: ' + row['label'])
    for name, additions in rows.items():
        existing = collections.get(name, [])
        if not isinstance(existing, list):
            raise ValueError('Collection is not a record list: ' + name)
        ids = [row['id'] for row in existing]
        extra_ids = [row['id'] for row in additions]
        if len(ids) != len(set(ids)) or len(extra_ids) != len(set(extra_ids)) or set(ids) & set(extra_ids):
            raise ValueError('Identity extension collision in ' + name)
    registry = {row['id'] for row in collections.get('sources', [])} | {row['id'] for row in rows['sources']}
    for name, additions in rows.items():
        for row in additions:
            refs = row.get('source_ids', []) + ([row['source_id']] if row.get('source_id') else [])
            if set(refs) - registry:
                raise ValueError('Unresolved identity source reference in ' + name)
    # No mutation occurs until every collision, ownership and source check passes.
    for name, additions in rows.items():
        collections.setdefault(name, []).extend(copy.deepcopy(additions))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'check'))
    action = parser.parse_args().action
    if action == 'build':
        (ROOT / FILE).write_bytes(encoded(build_contract()))
    else:
        evidence()
    print('PASS prepared four-current identity query contract ' + action)


if __name__ == '__main__':
    main()
