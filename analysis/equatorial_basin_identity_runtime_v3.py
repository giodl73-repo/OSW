"""Independent preservation model for the basin identity cloud candidate.

This module accepts supplied objects; it never opens the installed packet/index.
"""
import copy
import hashlib
import json
import re
from urllib.parse import quote
import equatorial_basin_identity_query_v3 as query
import equatorial_basin_identity_index_v2 as index

PROJECTION = 'equatorial_basin_identity_projection_v3'
SCENE_SCOPE = ('These editorial basin qualifications separate measurement targets. Family relationships do not establish '
               'physical connections, shared dimensions or observed current geometry.')
DIMENSION_STATUS = 'Lengths, widths, observation dates and annual ranges remain unmeasured by this identity admission.'
SCOPE = 'research/equatorial-basin-runtime-scope-v3.json'
PARENT_MANIFEST = 'c13a6295deac9c7a1897fc7539dc84099d6a0a6af30aa40499f40c660d2d431c'
PARENT_WASM = '28ca1a4704101c9a5406b1ce9a6a126081e581de9043474ed099949db108d428'


def scopes():
    scope = query.read(SCOPE)
    if query.sha(scope['parent_engine_manifest_file']) != PARENT_MANIFEST:
        raise ValueError('Installed source receipt differs')
    for path, row in scope['runtime_source_changes'].items():
        if query.sha(path) != row['candidate_sha256'] or query.sha(row['archive_path']) != row['historical_sha256']:
            raise ValueError('Changed runtime source or history: ' + path)
    for path, pin in {**scope['added_source_sha256'], **scope['source_dependencies_sha256'],
                      **scope['candidate_rust_source_sha256']}.items():
        if query.sha(path) != pin:
            raise ValueError('Changed frozen source: ' + path)
    return scope


def contract():
    value = query.build_contract()
    if query.encoded(value) != (query.ROOT / query.FILE).read_bytes():
        raise ValueError('Frozen identity contract differs')
    return value


def marker(c):
    return {'contract_file': query.FILE, 'contract_sha256': query.sha(query.FILE),
            'parent_logical_sha256': query.PARENT, 'new_identity_ids': c['expected_entity_ids'],
            'accepted_current_identities': 111, 'new_measurements': 0,
            'new_publication_sources': 0, 'physical_geometry_added': False}


def verify_collections(parent, child):
    c = contract()
    if set(child) != set(parent) or any(child[k] != parent[k] for k in parent if k not in {'collections', 'manifest'}):
        raise ValueError('Historical packet envelope changed')
    old, new = parent['collections'], child['collections']
    if {k: len(v) for k, v in old.items()} != c['prior_collection_counts']:
        raise ValueError('Exact parent collection inventory required')
    if set(new) != set(old) | set(c['additions']):
        raise ValueError('Unexpected collection inventory')
    for name in new:
        if new[name] != old.get(name, []) + c['additions'].get(name, []):
            raise ValueError('Historical rows/order or declared additions differ: ' + name)
    before, after = parent['manifest'], child['manifest']
    if set(after) != set(before) | {query.KEY, index.KEY}:
        raise ValueError('Unexpected manifest namespace')
    if any(after[k] != v for k, v in before.items() if k not in {'input_sha256', 'taxonomy'}):
        raise ValueError('Historical manifest changed')
    if after['taxonomy'] != query.taxonomy_projection(before,c):
        raise ValueError('Taxonomy changed outside exact node/link counts')
    if after[query.KEY] != marker(c):
        raise ValueError('Identity admission receipt differs')
    index.verify_audit(after[index.KEY])
    oldpins, newpins = before['input_sha256'], after['input_sha256']
    added = {**c['input_sha256'], query.FILE: query.sha(query.FILE)}
    if set(newpins) != set(oldpins) | set(added) | index.INDEX:
        raise ValueError('Input pin inventory differs')
    if any(newpins[p] != pin for p, pin in oldpins.items() if p not in index.INDEX):
        raise ValueError('Historical scientific input rebound')
    if any(newpins.get(p) != pin for p, pin in added.items()):
        raise ValueError('New source binding differs')
    if any(not isinstance(newpins.get(p), str) or not re.fullmatch('[0-9a-f]{64}', newpins[p]) for p in index.INDEX):
        raise ValueError('Missing candidate index hash')


def dashboard_document(original):
    c = contract()
    doc = copy.deepcopy(original)
    if len(doc['entries']) != 246 or doc['counts']['named_current'] != 106 or PROJECTION in doc:
        raise ValueError('Exact preceding dashboard required')
    if any(row['id'] in c['expected_entity_ids'] for row in doc['entries']):
        raise ValueError('Repeated identity dashboard extension')
    pending = doc['proposed_current_additions']
    if type(pending) is not int or pending < 5:
        raise ValueError('Invalid preceding proposal count')
    doc['entries'].extend(copy.deepcopy(c['additions']['objects']))
    doc['counts']['named_current'] = 111
    doc['proposed_current_additions'] -= 5
    doc['snapshot_fingerprint'] = hashlib.sha256(('osw.equatorial-basin-identities.v3\n' +
        original['snapshot_fingerprint'] + '\n' + query.sha(query.FILE) + '\n').encode()).hexdigest()
    doc[PROJECTION] = {'contract_file': query.FILE, 'contract_sha256': query.sha(query.FILE),
                       'new_identities': 5, 'new_measurements': 0}
    return doc


def catalogue_document(original):
    c = contract()
    doc = copy.deepcopy(original)
    new_plans = [row['source_decision'] for row in c['additions']['route_decisions']]
    if PROJECTION in doc or any(p['current_id'] == r['current_id'] for p in new_plans for r in doc['remaining_current_decisions']):
        raise ValueError('Repeated identity route planning extension')
    doc['remaining_current_decisions'].extend(copy.deepcopy(new_plans))
    strategies = [r for r in doc['planning_taxonomy']['strategies'] if r['id'] == 'source_axis_definition_required']
    if len(strategies) != 1:
        raise ValueError('One source-axis strategy required')
    for key in ['current_count', 'unbuilt_count']:
        strategies[0][key] += 5
    for key in ['accepted_current_names', 'currents_without_any_reference_card',
                'currents_without_route_candidates', 'currents_without_published_ranked_estimate']:
        doc['counts'][key] += 5
    doc['counts']['route_decision_records'] = len(doc['remaining_current_decisions'])
    doc['effective_accepted_current_count'] = doc['counts']['accepted_current_names']
    doc[PROJECTION] = {'contract_file': query.FILE, 'contract_sha256': query.sha(query.FILE),
                       'new_route_plans': 5, 'new_routes': 0}
    return doc


def membership_scene(selected, owner=None):
    if not selected:
        return None
    c = contract()
    members = []
    for row in selected:
        if row not in c['additions']['current_basin_memberships']:
            raise ValueError('Unknown membership')
        entity = next(e for e in c['additions']['entities'] if e['id'] == row['entity_id'])
        family = c['prior_family_records'][row['family_entity_id']]['entities'][0]
        members.append({'membership_record': copy.deepcopy(row), 'entity_id': entity['id'], 'label': entity['label'],
                        'object_url': entity['almanac_url'], 'family_entity_id': family['id'], 'family_label': family['label'],
                        'family_url': 'object.html?id=' + quote(family['id'], safe='')})
    return {'kind': 'equatorial_basin_identity_context', 'title': 'Basin-specific current identities', 'members': members,
            'selected_entity_id': owner, 'source_file': query.FILE, 'source_pointer': '/additions/current_basin_memberships',
            'source_url': 'https://www.tidesandcurrents.noaa.gov/glossary.html', 'figure': query.FIGURE,
            'scope': SCENE_SCOPE, 'dimension_status': DIMENSION_STATUS}


def scenes():
    c = contract()
    memberships = c['additions']['current_basin_memberships']
    result = {}
    for owner in c['expected_entity_ids'] + sorted(c['prior_family_records']):
        member = next((r for r in memberships if r['entity_id'] == owner), None)
        family = member['family_entity_id'] if member else owner
        result[owner] = membership_scene([r for r in memberships if r['family_entity_id'] == family], owner)
    return result


def decisions():
    return [{'current_id': r['proposal_id'], 'name': r['entity']['label'], 'measurement_ids': [],
             'status': 'identity_admitted_width_not_admitted', 'whole_current_width_km': None,
             'annual_width_range_km': None, 'admission_id': r['id']}
            for r in contract()['additions']['current_identity_admissions']]


def empty_plan(current):
    # Installed current_measurements derives these five empty plans before add_plans.
    return {'current_id': current, 'phases': [], 'can_play': False, 'eligible_indices': [],
            'range_note': 'Annual width range and measurement uncertainty: not available. A single dated section does not establish a seasonal cycle.',
            'playback_scope': 'Recorded comparable states only; no annual extrema or interpolated boundaries inferred.'}


def verify_snapshot(name, old, new):
    if name not in {'dashboard', 'atlas', 'seasons'}:
        raise ValueError('Unknown API snapshot')
    if not isinstance(new.get('bundle_sha256'), str) or not re.fullmatch('[0-9a-f]{64}', new['bundle_sha256']):
        raise ValueError('Missing candidate bundle identity')
    expected = copy.deepcopy(old)
    expected['bundle_sha256'] = new['bundle_sha256']
    if name == 'dashboard':
        if json.loads(new['snapshot_json']) != dashboard_document(json.loads(old['snapshot_json'])):
            raise ValueError('Complete dashboard projection differs')
        expected['snapshot_json'] = new['snapshot_json']
    else:
        if any(k in old for k in ['basin_identity_scenes', 'basin_identity_contract', 'basin_identity_planning']):
            raise ValueError('Repeated snapshot extension')
        expected['basin_identity_scenes'] = scenes()
        expected['basin_identity_contract'] = contract()
        expected['basin_identity_planning'] = query.read(query.PLANNING)
        expected['admitted_current_decisions'] += decisions()
        expected['working_reference_routes'] = catalogue_document(old['working_reference_routes'])
        if name == 'atlas':
            path = 'research/ocean-motion-dashboard.json'
            if json.loads(new['sources_json'][path]) != dashboard_document(json.loads(old['sources_json'][path])):
                raise ValueError('Atlas dashboard projection differs')
            expected['sources_json'][path] = new['sources_json'][path]
        else:
            for row in decisions():
                if row['current_id'] in expected['phase_plans']:
                    raise ValueError('Preexisting basin seasonal plan')
                expected['phase_plans'][row['current_id']] = empty_plan(row['current_id'])
    if expected != new:
        raise ValueError('Complete ' + name + ' changed outside declared identity projections')
