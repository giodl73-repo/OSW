"""Metadata-only projection of reviewed coastal quantities; no new dimensions.

Copies source statements without distance calculation, observation extraction,
or source refresh. The committed contract is required before applying real data.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import quote
from build_ocean_motion_claims import review_fingerprint

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'analysis/indian_coastal_dimension_context_v1.py'
TESTS = 'analysis/test_indian_coastal_dimension_context_v1.py'
FILE = 'research/indian-coastal-dimension-context-query-contract-v1.json'
PROTOCOL = 'plans/indian-coastal-dimension-context-batch-v1.md'
ROLE_REVIEW = 'signals/roles/check/indian-coastal-dimension-context-v1-roles-check-2026-10-24.md'
FACTS = ('research/eacc-painter-2020-regional-reach-source-facts-v1.json',
         'research/south-java-sprintall-2010-confinement-source-facts-v1.json')
SUPPLEMENT = ('research/indian-coastal-dimension-source-batch-v1.json',
              'research/source-data/painter-eacc-2020/acquisition.json',
              'research/source-data/sprintall-sjc-2010/acquisition-metadata-v1.json')
EACC, SJC = 'current:east-african-coastal', 'current:south-java'
REACH = 'regional-reach:east-african-coastal:painter-2020-connection'
CONFINEMENT = 'cross-shore-context:south-java:sprintall-2010-ombai-confinement'
EACC_SOURCE = 'source:painter-eacc-2020-regional-reach'
SJC_SOURCE = 'source:sprintall-sjc-2010-ombai-confinement'
METHOD = 'source:indian-coastal-dimension-context-v1'
VERSION = 'indian-coastal-dimension-context-v1'
OWNER_FIELDS = {'current_regional_reaches': ('regional_reach_ids', 'reported_regional_reaches'),
                'current_cross_shore_context': ('cross_shore_context_ids', 'cross_shore_context')}


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def pin(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def fingerprint(value):
    # Same canonical object convention as the established identity adapters.
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def validate_facts(reach, confinement):
    if (reach.get('schema') != 'osw.reported-regional-reach-source-facts.v1' or reach.get('entity_id') != EACC
            or reach.get('quantity') != 'source_reported_approximate_regional_connection_distance'
            or not positive(reach.get('reported_distance_km')) or reach.get('approximate') is not True):
        raise ValueError('Changed EACC regional source quantity')
    for field in ['whole_current_length_km', 'annual_length_range_km', 'source_numeric_length_uncertainty_km',
                  'exact_observation_dates', 'fixed_depth_layer_m', 'longitude_coordinates']:
        if reach.get(field) is not None:raise ValueError('Regional reach promoted beyond source support')
    for field in ['whole_current_rank_eligible', 'seasonal_geometry_eligible', 'working_dataset_admitted',
                  'source_gate_coordinates_extracted', 'geodesic_path_computed']:
        if reach.get(field) is not False:raise ValueError('Regional reach admission or geometry invented')
    if (confinement.get('schema') != 'osw.current-coastal-confinement-source-facts.v1'
            or confinement.get('entity_id') != SJC or confinement.get('quantity') != 'sst_associated_coastal_confinement_scale'):
        raise ValueError('Changed SJC source quantity')
    bounds = confinement.get('reported_approximate_extent_range_km')
    if not isinstance(bounds, list) or len(bounds) != 2 or not all(map(positive, bounds)) or bounds[0] >= bounds[1]:
        raise ValueError('Invalid source confinement range')
    for field in ['paired_current_width_km', 'fixed_velocity_layer_m', 'annual_width_range_km',
                  'numeric_measurement_uncertainty_km', 'calendar_months_assigned_to_this_number']:
        if confinement.get(field) is not None:raise ValueError('Confinement promoted to width, layer, calendar or error')
    for field in ['full_current_width_inference_eligible', 'whole_current_rank_eligible',
                  'seasonal_current_geometry_eligible', 'working_dataset_admitted']:
        if confinement.get(field) is not False:raise ValueError('Confinement promoted to physical coverage')
    for facts in [reach, confinement]:
        source = facts.get('source', {})
        digest = source.get('original_sha256', '')
        if (len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)
                or not source.get('url') or not source.get('doi') or source.get('full_paper_visual_review') is not False):
            raise ValueError('Missing or overstated original-source identity/review scope')


def project(reach, confinement):
    """Copy the two reviewed quantities into their distinct existing collections."""
    validate_facts(reach, confinement)
    distance = reach['reported_distance_km']
    r = {'id': REACH, 'entity_id': EACC, 'current_id': 'east-african-coastal',
         'schema': 'osw.source-reported-regional-connection.v1',
         'status': 'source_reported_approximate_regional_connection_not_measured_axis',
         'constraint': {'quantity': reach['quantity'], 'reported_value_km': distance, 'unit': 'km',
                        'relation': 'source_reported_approximate_value', 'display': f'About {distance:g} km · regional connection',
                        'reported_uncertainty_km': None, 'whole_current_length_km': None,
                        'physical_length_lower_bound_km': None, 'physical_width_km': None,
                        'annual_or_seasonal_range': None, 'current_geometry': None, 'state_intersections': None,
                        'rank_eligible': False, 'study_window': None, 'vertical_support': 'Not specified for this regional distance.'},
         'scope_note': reach['regional_context'] + '. ' + reach['interpretation'],
         'source': {'source_title': reach['source']['title'], 'authors': [reach['source']['author']]},
         'source_id': EACC_SOURCE, 'source_locator': reach['source']['locator'],
         'source_file': FACTS[0], 'record_role': 'reported_regional_connection_not_whole_current_length',
         'whole_current_length_admitted': False, 'physical_width_admitted': False,
         'annual_or_seasonal_range_admitted': False, 'current_geometry_admitted': False,
         'state_intersections_admitted': False, 'rank_eligible': False, 'new_calculation_performed': False}
    c = {'id': CONFINEMENT, 'entity_id': SJC, 'quantity': confinement['quantity'],
         'record_role': 'reported_sst_associated_confinement_not_paired_velocity_width',
         'reported_range_km': copy.deepcopy(confinement['reported_approximate_extent_range_km']),
         'reported_value_km': None, 'reference': confinement['reference_boundary'],
         'source_precision': 'Approximate source-described confinement range',
         'range_meaning': confinement['range_meaning'], 'geographic_scope': confinement['region'],
         'time_support_note': ('Source season: ' + confinement['season_label'] + '. Supporting velocity records: '
                               + ', '.join(map(str, confinement['velocity_observation_years']))
                               + '. SST climatology: ' + confinement['sst_climatology_period_as_reported'] + '.'),
         'proxy_note': 'SST-front position is a proxy; no paired velocity-current boundary is established.',
         'source_id': SJC_SOURCE, 'source_locator': '; '.join(confinement['source']['locators']),
         'source_file': FACTS[1], 'canonical_width_admitted': False,
         'paired_current_width_km': None, 'fixed_depth_layer_m': None,
         'annual_width_range_km': None, 'uncertainty_interval': False, 'width_interval': False,
         'geographic_width_geometry': None, 'ranking_eligible': False,
         'physical_seasonal_playback_eligible': False}
    sources = []
    for facts, sid in [(reach, EACC_SOURCE), (confinement, SJC_SOURCE)]:
        source = facts['source']
        sources.append({'id': sid, 'kind': 'article', 'label': source['title'], 'title': source['title'],
                        'url': source['url'], 'doi': source['doi'], 'publication_year': source['year'],
                        'original_sha256': source['original_sha256'], 'original_bytes': source['original_bytes'],
                        'authors': source.get('authors') or [source['author']],
                        'license_or_rights': source.get('license') or source.get('rights_statement'),
                        'original_asset_redistributed_by_this_batch': False,
                        'source_kind': 'source_scoped_publication_context_not_independent_observation',
                        'independent_observations_added': 0,
                        'review_scope': 'Selected source pages visually checked; no full-paper visual review.'})
    sources.append({'id': METHOD, 'kind': 'method', 'label': 'Indian coastal source-context projection v1',
                    'url': '../' + PROTOCOL, 'path': PROTOCOL,
                    'source_kind': 'metadata_projection_no_new_physical_calculation',
                    'independent_observations_added': 0})
    claims = []
    for collection, row, quantity, value in [
        ('current_regional_reaches', r, r['constraint']['quantity'], {'reported_value_km': distance}),
        ('current_cross_shore_context', c, c['quantity'], {'reported_range_km': c['reported_range_km']})]:
        claim = {'id': 'claim:' + row['id'], 'subject_id': row['entity_id'], 'object_id': None,
                 'predicate': quantity, 'value': copy.deepcopy(value), 'unit': 'km',
                 'target_collection': collection, 'target_id': row['id'],
                 'source_id': row['source_id'], 'source_locator': row['source_locator'],
                 'source_locator_status': 'specific', 'method_source_id': METHOD, 'method': PROTOCOL,
                 'evidence_class': 'reviewed_source_context_not_physical_dimension_admission',
                 'assertion_status': 'reported_source_context', 'scope': row.get('scope_note', row.get('geographic_scope')),
                 'observation_time': None, 'observation_window': None, 'source_date': None,
                 'review_status': 'not_individually_reviewed', 'reviewer': None, 'review_date': None,
                 'review_note': 'Internal source/scope checks; no independent scientific approval.'}
        claim['review_fingerprint'] = review_fingerprint(claim)
        claims.append(claim)
        row['claim_id'] = claim['id'];row['method_source_id'] = METHOD
    return {'current_regional_reaches': [r], 'current_cross_shore_context': [c],
            'sources': sources, 'claims': claims}


def query_link(collection, record_id, label):
    request = {'collection': collection, 'filters': [{'field': 'id', 'op': 'eq', 'value': record_id}], 'limit': 1}
    return {'label': label, 'url': 'query.html?q=' + quote(json.dumps(request, separators=(',', ':')), safe='')}


def validate_additions(additions):
    reach = additions['current_regional_reaches'][0]
    cross = additions['current_cross_shore_context'][0]
    constraint = reach.get('constraint', {})
    for row in [reach, cross]:
        for field in ['length_km', 'width_km', 'whole_current_width_km', 'geometry', 'state_intersections', 'annual_dimension_range_km']:
            if field in row and row[field] is not None:raise ValueError('Physical dimension added to a context row')
    if (reach.get('entity_id') != EACC or reach.get('source_id') != EACC_SOURCE
            or reach.get('source_file') != FACTS[0]
            or constraint.get('quantity') != 'source_reported_approximate_regional_connection_distance'
            or not positive(constraint.get('reported_value_km')) or constraint.get('unit') != 'km'):
        raise ValueError('Changed regional connection quantity or owner')
    for field in ['reported_uncertainty_km', 'whole_current_length_km', 'physical_length_lower_bound_km',
                  'physical_width_km', 'annual_or_seasonal_range', 'current_geometry', 'state_intersections', 'study_window']:
        if field not in constraint or constraint[field] is not None:raise ValueError('Reach promoted into a physical dimension')
    if constraint.get('rank_eligible') is not False:raise ValueError('Regional reach cannot be ranked')
    for field in ['whole_current_length_admitted', 'physical_width_admitted', 'annual_or_seasonal_range_admitted',
                  'current_geometry_admitted', 'state_intersections_admitted', 'rank_eligible', 'new_calculation_performed']:
        if reach.get(field) is not False:raise ValueError('Reach admission flags changed')
    bounds = cross.get('reported_range_km')
    if (cross.get('entity_id') != SJC or cross.get('source_id') != SJC_SOURCE or cross.get('source_file') != FACTS[1]
            or cross.get('quantity') != 'sst_associated_coastal_confinement_scale'
            or not isinstance(bounds, list) or len(bounds) != 2 or not all(map(positive, bounds)) or bounds[0] >= bounds[1]):
        raise ValueError('Changed SST-associated confinement quantity or owner')
    for field in ['paired_current_width_km', 'fixed_depth_layer_m', 'annual_width_range_km', 'geographic_width_geometry', 'reported_value_km']:
        if field not in cross or cross[field] is not None:raise ValueError('Confinement promoted to a physical width')
    for field in ['canonical_width_admitted', 'uncertainty_interval', 'width_interval', 'ranking_eligible', 'physical_seasonal_playback_eligible']:
        if cross.get(field) is not False:raise ValueError('Confinement admission flags changed')
    for row, claim, collection, entity, value, predicate in [
        (reach, additions['claims'][0], 'current_regional_reaches', EACC, {'reported_value_km': constraint['reported_value_km']}, constraint['quantity']),
        (cross, additions['claims'][1], 'current_cross_shore_context', SJC, {'reported_range_km': bounds}, cross['quantity'])]:
        if (row.get('method_source_id') != METHOD or row.get('claim_id') != claim['id']
                or claim.get('subject_id') != entity or claim.get('target_id') != row['id']
                or claim.get('target_collection') != collection or claim.get('source_id') != row['source_id']
                or claim.get('predicate') != predicate or claim.get('value') != value or claim.get('unit') != 'km'
                or claim.get('method_source_id') != METHOD or claim.get('review_fingerprint') != review_fingerprint(claim)
                or claim.get('review_status') != 'not_individually_reviewed'
                or any(claim.get(field) is not None for field in ['reviewer', 'review_date', 'observation_time', 'observation_window', 'source_date'])):
            raise ValueError('Source-context claim/provenance changed')


def prepare(collections, contract):
    """Stage only two context owners and seven rows; never mutate the parent."""
    if (contract.get('schema') != 'osw.indian-coastal-dimension-context.query-contract.v1'
            or contract.get('version') != VERSION or contract.get('canonical_delivery_verified') is not False):
        raise ValueError('Unsupported context contract')
    additions = contract['additions']
    expected = {'current_regional_reaches': [REACH], 'current_cross_shore_context': [CONFINEMENT],
                'sources': [EACC_SOURCE, SJC_SOURCE, METHOD], 'claims': ['claim:' + REACH, 'claim:' + CONFINEMENT]}
    if set(additions) != set(expected):raise ValueError('Context contract attempted a physical collection')
    for collection, ids in expected.items():
        rows = additions[collection]
        prior = collections.get(collection, [])
        if (not isinstance(rows, list) or [r['id'] for r in rows] != ids or not isinstance(prior, list)
                or len({r['id'] for r in prior}) != len(prior) or set(ids) & {r['id'] for r in prior}):
            raise ValueError('Duplicate or altered source-context rows')
    validate_additions(additions)
    owners = {}
    registry = {row['id'] for row in collections.get('sources', [])}
    for entity in [EACC, SJC]:
        matches = [o for o in collections.get('objects', []) if o['id'] == entity]
        entities = [e for e in collections.get('entities', []) if e['id'] == entity]
        if len(matches) != 1 or len(entities) != 1:raise ValueError('Missing or duplicate accepted context owner')
        owner = matches[0];refs = owner.get('source_ids')
        if (owner.get('type') != 'named_current' or not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs)
                or len(set(refs)) != len(refs) or set(refs) - registry
                or type(owner.get('linked_source_count')) is not int or owner['linked_source_count'] != len(refs)):
            raise ValueError('Invalid original owner provenance')
        if (not isinstance(owner.get('capabilities', {}), dict) or not isinstance(owner.get('section_fingerprints', {}), dict)
                or not isinstance(owner.get('evidence_links', []), list)):
            raise ValueError('Invalid original owner context containers')
        owners[entity] = copy.deepcopy(owner)
    stage = dict(collections)
    for collection, rows in additions.items():stage[collection] = [*collections.get(collection, []), *copy.deepcopy(rows)]
    registry = {row['id'] for row in stage['sources']}
    for collection, (field, capability) in OWNER_FIELDS.items():
        for row in additions[collection]:
            entity = row['entity_id'];owner = owners.get(entity)
            if owner is None or row['source_id'] not in registry or row['method_source_id'] != METHOD:
                raise ValueError('Context ownership or provenance changed')
            before = owner.get(field, [])
            old_ids = [r['id'] for r in collections.get(collection, []) if r.get('entity_id') == entity]
            if before != old_ids or owner.get('capabilities', {}).get(capability, 0) != len(old_ids):
                raise ValueError('Original context ownership/count changed')
            owner[field] = before + [row['id']]
            owner.setdefault('capabilities', {})[capability] = len(owner[field])
            owner['source_ids'] = sorted(set(owner['source_ids']) | {row['source_id'], METHOD})
            owner['linked_source_count'] = len(owner['source_ids'])
            label = 'Query the source-reported regional connection' if collection == 'current_regional_reaches' else 'Query the SST-associated confinement context'
            owner.setdefault('evidence_links', []).append(query_link(collection, row['id'], label))
    for entity, owner in owners.items():
        source_index = {s['id']: s for s in stage['sources']}
        group = [source_index[ref] for ref in owner['source_ids']]
        owner.setdefault('section_fingerprints', {})['sources'] = fingerprint(group)
        own = [r for name in OWNER_FIELDS for r in stage.get(name, []) if r.get('entity_id') == entity]
        owner['section_fingerprints']['coastal_dimension_context'] = fingerprint(own)
        contexts = [r for name in ['current_direction_calendars', 'current_direction_descriptions',
                                  'current_reported_width_evidence', 'current_cross_shore_context', 'current_regime_context']
                    for r in stage.get(name, []) if r.get('entity_id') == entity]
        owner['section_fingerprints']['source_context'] = fingerprint(contexts)
        claims = [r for r in stage.get('claims', []) if entity in (r.get('subject_id'), r.get('object_id'))]
        owner['recorded_claims'] = len(claims)
        owner['claim_review_counts'] = {status: sum((r.get('review_status') or 'unspecified') == status for r in claims)
                                        for status in sorted({r.get('review_status') or 'unspecified' for r in claims})}
        owner['section_fingerprints']['claims'] = fingerprint(claims)
        owner['fingerprint'] = fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    stage['objects'] = [owners.get(row['id'], row) for row in collections['objects']]
    return stage, {'schema': 'osw.indian-coastal-dimension-context.stage-receipt.v1',
                   'status': 'staged_source_context_not_published', 'canonical_delivery_verified': False,
                   'new_rows': 7, 'changed_owner_ids': [EACC, SJC],
                   'new_paired_widths': 0, 'new_ranked_lengths': 0, 'new_raw_observations': 0,
                   'new_annual_ranges': 0, 'new_current_geometry_or_state_joins': 0}


def validate_custody(documents, receipts):
    """Match reviewed identities to existing receipts without reopening PDFs."""
    if len(documents) != 2 or len(receipts) != 2:
        raise ValueError('Both source identities and custody receipts are required')
    for facts, receipt, url_key in zip(documents, receipts, ['source_url', 'url']):
        source = facts['source']
        if (source.get('url') != receipt.get(url_key)
                or source.get('original_sha256') != receipt.get('sha256')
                or type(source.get('original_bytes')) is not int
                or type(receipt.get('bytes')) is not int
                or source['original_bytes'] <= 0
                or source['original_bytes'] != receipt['bytes']):
            raise ValueError('Reviewed source identity differs from original acquisition receipt')
    if (receipts[0].get('doi') != documents[0]['source']['doi']
            or receipts[1].get('http_status') != 200
            or receipts[1].get('original_pdf_committed') is not False):
        raise ValueError('Original-source receipt scope changed')


def build_contract():
    """Build a prospective metadata contract; this does not apply it to a dataset."""
    documents = [json.loads((ROOT / name).read_bytes()) for name in FACTS]
    receipts = [json.loads((ROOT / name).read_bytes()) for name in SUPPLEMENT[1:]]
    validate_custody(documents, receipts)
    rows = project(*documents)
    dependencies = [OPERATOR, TESTS, PROTOCOL, ROLE_REVIEW, *FACTS, *SUPPLEMENT,
                    'analysis/build_ocean_motion_claims.py']
    for collection in OWNER_FIELDS:
        for row in rows[collection]:row['source_file_sha256'] = pin(row['source_file'])
    return {'schema': 'osw.indian-coastal-dimension-context.query-contract.v1', 'version': VERSION,
            'status': 'prepared_source_context_not_delivered', 'canonical_delivery_verified': False,
            'input_sha256': {name: pin(name) for name in dependencies},
            'source_documents': sorted([*FACTS, *SUPPLEMENT, FILE]),
            'additions': rows, 'new_independent_observations': 0, 'new_paired_widths': 0,
            'new_ranked_lengths': 0, 'new_current_geometry_or_state_joins': 0}


def evidence():
    """Actual data application requires exact committed contract and inputs."""
    import subprocess
    raw = (ROOT / FILE).read_bytes()
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', 'HEAD:' + FILE], cwd=ROOT) != raw:
        raise ValueError('Coastal context contract must be committed before data application')
    document = json.loads(raw)
    for path, expected in document['input_sha256'].items():
        if pin(path) != expected:raise ValueError('Changed source-context contract input: ' + path)
        if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', 'HEAD:' + path], cwd=ROOT) != (ROOT / path).read_bytes():
            raise ValueError('Source-context input differs from committed bytes: ' + path)
    if encoded(build_contract()) != raw:raise ValueError('Coastal context contract differs from reviewed source projection')
    return document, hashlib.sha256(raw).hexdigest()
