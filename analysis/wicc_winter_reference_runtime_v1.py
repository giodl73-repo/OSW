"""Exact runtime adapter; small source fixtures only until an explicit cloud caller."""
import copy
import hashlib
import json
import wicc_winter_reference_query_v1 as query
import published_wicc_review_width_v1 as width

ROOT = query.ROOT
FILE = 'research/wicc-winter-reference-runtime-contract-v1.json'
KEY = 'wicc_winter_reference_delivery_v1'
PLANNING = 'research/indian-current-reference-route-planning-v1.json'
MODULE = 'analysis/wicc_winter_reference_runtime_v1.py'
PROTOCOL = 'plans/wicc-winter-reference-runtime-protocol-v1.md'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def final_owner(source):
    owner = copy.deepcopy(source['prior_records']['owner'])
    owner['route_ids'] = [query.ROUTE]
    owner['capabilities']['reference_route'] = 1
    owner['map_features'].append(copy.deepcopy(source['owner_map_feature']))
    owner['source_ids'] = sorted(set(owner['source_ids']) | set(source['route']['source_ids']))
    owner['linked_source_count'] = len(owner['source_ids'])
    owner['route_url'] = query.atlas_url()
    owner['section_fingerprints']['wicc_winter_regional_reference'] = query.fingerprint(source['route'])
    owner['fingerprint'] = query.fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    return owner


def final_decision(source):
    prior = source['prior_records']['planning_decision']
    decision = copy.deepcopy(prior)
    decision['prior_route_decision'] = copy.deepcopy(prior)
    decision.update(route_ids=[query.ROUTE], candidate_count=1,
                    construction_status='regional_editorial_reference_abstract_supported',
                    source_catalog_file=query.CANDIDATE, source_catalog_sha256=source['route']['source_file_sha256'],
                    source_id=source['route']['source_id'], source_ids=copy.deepcopy(source['route']['source_ids']),
                    source_url=source['route']['source_url'],
                    next_action='Recover whole-current endpoints and compatible physical axes; this abstract-supported regional reference does not establish seasonal dimensions or uncertainty.')
    decision['source_decision'].update(candidate_ids=[query.ROUTE],
                                      reference_path_decision=decision['construction_status'],
                                      name_source_url=decision['source_url'], next_action=decision['next_action'])
    return decision


def build_contract():
    source = query.build_contract()
    raw = (ROOT / query.CONTRACT).read_bytes()
    if raw != query.encoded(source):
        raise ValueError('Exact frozen query contract required')
    planning = (ROOT / PLANNING).read_bytes()
    prior = source['prior_records']['planning_decision']
    plans = [r for r in json.loads(planning)['entries'] if r['current_id'] == query.CURRENT]
    if plans != [prior['source_decision']] or prior['source_catalog_sha256'] != sha(planning):
        raise ValueError('Audited planning source differs')
    owner = final_owner(source)
    selected = source['prior_records']
    marker = selected['manifest_bindings'][width.KEY]
    historical = selected['historical_dashboard_entry'][0]
    projected = width.dashboard_row(historical, marker['prior_dashboard_fingerprint'], marker['prior_measurements_fingerprint'])
    dashboard_after = copy.deepcopy(projected)
    for key in ['route_ids', 'capabilities', 'map_features', 'source_ids', 'linked_source_count',
                'route_url', 'section_fingerprints', 'fingerprint']:
        dashboard_after[key] = copy.deepcopy(owner[key])
    return {'schema': 'osw.wicc-winter-reference-runtime-contract.v1', 'status': 'PREPARED_NOT_COMPILED_OR_INSTALLED',
            'parent_logical_sha256': query.PARENT, 'query_contract': source,
            'final_owner': owner, 'final_decision': final_decision(source),
            'dashboard_before': projected, 'dashboard_after': dashboard_after,
            'original_planning_source': plans[0],
            'input_sha256': {**source['input_sha256'], query.CONTRACT: sha(raw), PLANNING: sha(planning),
                             MODULE: sha((ROOT / MODULE).read_bytes()), PROTOCOL: sha((ROOT / PROTOCOL).read_bytes())}}


def marker(contract):
    return {'schema': 'osw.wicc-winter-reference-runtime-receipt.v1', 'parent_logical_sha256': query.PARENT,
            'contract_file': FILE, 'contract_sha256': sha(query.encoded(contract)),
            'new_editorial_routes': 1, 'new_publication_citations': 2,
            'new_internal_sources': 1, 'new_physical_dimensions': 0}


def prepare(collections, manifest, contract, *, parent_logical_sha256):
    if contract != build_contract() or parent_logical_sha256 != query.PARENT or KEY in manifest:
        raise ValueError('Exact unapplied runtime contract and parent required')
    if manifest.get('input_sha256', {}).get(PLANNING) != contract['input_sha256'][PLANNING]:
        raise ValueError('Original planning receipt required')
    names = ['sources', 'reference_routes', 'objects', 'entities', 'route_decisions', 'widths']
    # Do not deep-copy large scientific tables outside the affected lists.
    small = {name: collections[name] for name in names}
    after = query.append(small, contract['query_contract'], parent_logical_sha256=parent_logical_sha256)
    decision = next(r for r in after['route_decisions'] if r.get('entity_id') == query.OWNER)
    decision['source_decision']['name_source_url'] = decision['source_url']
    if decision != contract['final_decision'] or next(r for r in after['objects'] if r['id'] == query.OWNER) != contract['final_owner']:
        raise ValueError('Runtime projection differs from frozen expected records')
    updated = copy.deepcopy(manifest)
    updated[KEY] = marker(contract)
    updated['input_sha256'].update(contract['input_sha256'])
    updated['input_sha256'][FILE] = updated[KEY]['contract_sha256']
    for name in ['sources', 'reference_routes', 'objects', 'route_decisions']:
        collections[name] = after[name]
    manifest.clear()
    manifest.update(updated)


def catalog_projection(catalog, contract):
    if contract != build_contract():
        raise ValueError('Changed runtime contract')
    if any(r['current_id'] == query.CURRENT for r in catalog['candidates']):
        raise ValueError('WICC card already present')
    indices = [i for i, r in enumerate(catalog['remaining_current_decisions']) if r['current_id'] == query.CURRENT]
    if len(indices) != 1 or catalog['remaining_current_decisions'][indices[0]] != contract['original_planning_source']:
        raise ValueError('Exact original WICC planning card required')
    result = copy.deepcopy(catalog)
    entry = copy.deepcopy(contract['query_contract']['route'])
    entry.update(report_inline=copy.deepcopy(contract['query_contract']['atlas_report']),
                 nominal_atlas_state_crossings=[], state_intersection_status='editorial_navigation_only_no_physical_join',
                 remaining_gates=contract['query_contract']['atlas_report']['remaining_gates'])
    result['candidates'].append(entry)
    result['remaining_current_decisions'][indices[0]] = copy.deepcopy(contract['final_decision']['source_decision'])
    for key, delta in [('route_candidates', 1), ('currents_with_route_candidates', 1),
                       ('currents_without_route_candidates', -1), ('currents_without_any_reference_card', -1)]:
        if type(result['counts'][key]) is not int or result['counts'][key] + delta < 0:
            raise ValueError('Invalid route coverage counter')
        result['counts'][key] += delta
    strategies = [r for r in result['planning_taxonomy']['strategies'] if r['id'] == contract['final_decision']['strategy_id']]
    if len(strategies) != 1 or type(strategies[0]['unbuilt_count']) is not int or strategies[0]['unbuilt_count'] < 1:
        raise ValueError('Invalid route strategy counter')
    strategies[0]['unbuilt_count'] -= 1
    return result


if __name__ == '__main__':
    target = ROOT / FILE
    assert not target.exists(), 'Executed runtime contracts are frozen'
    target.write_bytes(query.encoded(build_contract()))
    print('Prepared WICC runtime contract; compilation and installation pending')
