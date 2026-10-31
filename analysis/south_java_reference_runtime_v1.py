"""Bind the South Java source append to native validation and atlas projection."""
import copy
import hashlib
import json

import south_java_reference_query_v1 as query

ROOT = query.ROOT
FILE = 'research/south-java-reference-runtime-contract-v1.json'
MODULE = 'analysis/south_java_reference_runtime_v1.py'
PROTOCOL = 'plans/south-java-reference-runtime-protocol-v1.md'
KEY = 'south_java_reference_delivery_v1'
PLANNING = 'research/indian-current-reference-route-planning-v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':'))


def build_contract():
    source = query.build_contract()
    source_raw = (ROOT / query.FILE).read_bytes()
    if source_raw != query.encoded(source):
        raise ValueError('Exact frozen South Java query contract required')
    planning_raw = (ROOT / PLANNING).read_bytes()
    plans = [r for r in json.loads(planning_raw)['entries'] if r['current_id'] == query.CURRENT]
    prior = source['prior_decision']
    if (plans != [prior['source_decision']] or prior['source_catalog_file'] != PLANNING
            or prior['source_catalog_sha256'] != sha(planning_raw)):
        raise ValueError('Exact audited South Java planning source required')
    report = json.loads((ROOT / query.CANDIDATE).read_bytes())
    report.update(status='reviewed_editorial_regional_reference_connection_pending_installation',
        rendering_role='derived_inline_editorial_reach_card_not_additional_observation',
        source_candidate_file=query.CANDIDATE, source_candidate_sha256=query.PINS[query.CANDIDATE],
        geography_review_file=query.REVIEW, geography_review_sha256=query.PINS[query.REVIEW],
        figure=query.FIGURE, compact_figure_file=query.COMPACT,
        physical_current_axis_admitted=False, physical_state_join_eligible=False,
        whole_current_length_km=None, annual_length_range_km=None,
        state_scope_note='AUSW and SUND are editorial drawing overlaps; physical current passage is unassessed.',
        remaining_gates=['Verify this exact reference in native/WASM queries and atlas cards.',
            'Recover compatible physical axes, alongflow endpoints, widths and seasonal dimensions.'])
    return {'schema': 'osw.south-java-reference-runtime-contract.v1', 'status': 'PREPARED_NOT_COMPILED_OR_INSTALLED',
        'owner_id': query.TARGET, 'parent_logical_sha256': query.PARENT,
        'original_planning_file': PLANNING, 'original_planning_sha256': sha(planning_raw),
        'original_planning_source': plans[0], 'query_contract_file': query.FILE,
        'query_contract_sha256': sha(source_raw), 'query_contract': source, 'atlas_report': report,
        'input_sha256': {**source['input_sha256'], query.FILE: sha(source_raw), PLANNING: sha(planning_raw),
            MODULE: sha((ROOT / MODULE).read_bytes()), PROTOCOL: sha((ROOT / PROTOCOL).read_bytes())}}


def prepare(collections, manifest, contract, *, parent_logical_sha256):
    if query.encoded(contract) != query.encoded(build_contract()):
        raise ValueError('Changed South Java runtime source contract')
    if (parent_logical_sha256 != query.PARENT or KEY in manifest
            or manifest.get('input_sha256', {}).get(PLANNING) != contract['original_planning_sha256']):
        raise ValueError('Exact unapplied parent and original planning receipt required')
    # The query append clones only its selected records and replaces four lists.
    # Sharing untouched scientific collections avoids another large-table copy.
    after = dict(collections)
    result = query.append(after, contract['query_contract'], parent_logical_sha256=parent_logical_sha256)
    owner = next(r for r in after['objects'] if r['id'] == query.TARGET)
    route = next(r for r in after['reference_routes'] if r['id'] == query.ROUTE)
    receipt = {'schema': 'osw.south-java-reference-runtime-receipt.v1',
        'parent_logical_sha256': query.PARENT, 'contract_file': FILE,
        'contract_sha256': sha(query.encoded(contract)),
        'prior_owner': copy.deepcopy(contract['query_contract']['prior_owner']),
        'prior_entity': copy.deepcopy(contract['query_contract']['prior_entity']),
        'prior_decision': copy.deepcopy(contract['query_contract']['prior_decision']),
        'publication_sources': copy.deepcopy(contract['query_contract']['existing_publications']),
        'owner_fingerprint_json': compact({k: v for k, v in owner.items() if k != 'fingerprint'}),
        'section_fingerprint_json': compact(route), 'new_physical_dimensions': 0, 'installed': False}
    updated = copy.deepcopy(manifest)
    updated[KEY] = receipt
    updated['input_sha256'].update(contract['input_sha256'])
    updated['input_sha256'][FILE] = receipt['contract_sha256']
    collections.update(after)
    manifest.update(updated)
    return result


def catalog_projection(catalog, collections, contract):
    if query.encoded(contract) != query.encoded(build_contract()):
        raise ValueError('Changed runtime catalogue contract')
    if any(r['current_id'] == query.CURRENT for r in catalog['candidates']):
        raise ValueError('South Java atlas reference already present')
    indices = [i for i, r in enumerate(catalog['remaining_current_decisions']) if r['current_id'] == query.CURRENT]
    if len(indices) != 1 or catalog['remaining_current_decisions'][indices[0]] != contract['original_planning_source']:
        raise ValueError('Original South Java atlas planning source required')
    matches = [r for r in collections['reference_routes'] if r['id'] == query.ROUTE]
    decisions = [r for r in collections['route_decisions'] if r['entity_id'] == query.TARGET]
    if matches != [contract['query_contract']['route']] or len(decisions) != 1:
        raise ValueError('Exact prepared reference and decision required')
    result = copy.deepcopy(catalog)
    entry = copy.deepcopy(matches[0])
    entry.update(candidate_file=query.CANDIDATE, candidate_sha256=query.PINS[query.CANDIDATE],
        route_extent_kind='Java-Bali editorial study reach', scenario_range_km=entry['public_editorial_probe_span_km'],
        nominal_atlas_state_crossings=[], state_intersection_status='unassessed_no_physical_join_admitted',
        remaining_gates=contract['atlas_report']['remaining_gates'], report_inline=copy.deepcopy(contract['atlas_report']))
    result['candidates'].append(entry)
    result['remaining_current_decisions'][indices[0]] = copy.deepcopy(decisions[0]['source_decision'])
    for key, delta in [('route_candidates', 1), ('currents_with_route_candidates', 1),
                      ('currents_without_route_candidates', -1), ('currents_without_any_reference_card', -1)]:
        value = result['counts'][key]
        if type(value) is not int or value + delta < 0:
            raise ValueError('Invalid atlas counter: ' + key)
        result['counts'][key] = value + delta
    strategies = [r for r in result['planning_taxonomy']['strategies'] if r['id'] == decisions[0]['strategy_id']]
    if len(strategies) != 1 or type(strategies[0]['unbuilt_count']) is not int or strategies[0]['unbuilt_count'] <= 0:
        raise ValueError('Invalid original planning strategy count')
    strategies[0]['unbuilt_count'] -= 1
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = query.encoded(build_contract())
    if args.action == 'build':
        (ROOT / FILE).write_bytes(raw)
    elif (ROOT / FILE).read_bytes() != raw:
        raise ValueError('Changed source-bound runtime contract')
    print(json.dumps({'status': 'PASS', 'compiled': False, 'installed': False}))
