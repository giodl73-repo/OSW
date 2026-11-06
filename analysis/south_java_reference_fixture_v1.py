"""Small synthetic peer records around the actual audited South Java metadata."""
import copy

import south_java_reference_runtime_v1 as runtime

query = runtime.query
FILE = 'research/south-java-reference-runtime-fixture-v1.json'


def unprepared():
    contract = runtime.build_contract()
    doc = contract['query_contract']
    sources = copy.deepcopy(doc['prior_owner_sources'])
    sources += [{'id': 'fixture:source:' + str(i)} for i in range(210 - len(sources))]
    routes = [{'id': 'fixture:route:' + str(i), 'current_id': 'fixture-peer-' + str(i % 74)} for i in range(81)]
    collections = {'sources': sources, 'objects': [copy.deepcopy(doc['prior_owner'])],
        'entities': [copy.deepcopy(doc['prior_entity'])], 'route_decisions': [copy.deepcopy(doc['prior_decision'])],
        'reference_routes': routes, 'widths': [{'id': 'fixture:width', 'payload': [10, 20]}],
        'width_samples': [{'id': 'fixture:width-sample', 'month': 7, 'payload': [30, 40]}]}
    manifest = {'input_sha256': {runtime.PLANNING: contract['original_planning_sha256']},
        'fixture_note': 'Synthetic peers and tables; not an installed bundle or independent scientific evidence.',
        'preserved_namespace': {'sentinel': 'unchanged'}}
    catalog = {'candidates': copy.deepcopy(routes), 'remaining_current_decisions': [copy.deepcopy(contract['original_planning_source'])],
        'counts': {'route_candidates': 81, 'currents_with_route_candidates': 74,
                   'currents_without_route_candidates': 21, 'currents_without_any_reference_card': 21},
        'planning_taxonomy': {'strategies': [{'id': doc['prior_decision']['strategy_id'], 'unbuilt_count': 8},
                                          {'id': 'fixture:other-strategy', 'unbuilt_count': 3}]}}
    return contract, collections, manifest, catalog


def build():
    contract, collections, manifest, catalog = unprepared()
    runtime.prepare(collections, manifest, contract, parent_logical_sha256=query.PARENT)
    manifest['fixture_catalogue'] = catalog
    manifest['fixture_expected_catalogue'] = runtime.catalog_projection(catalog, collections, contract)
    return {'schema': 'osw.query-bundle.v1', 'manifest': manifest, 'collections': collections}


if __name__ == '__main__':
    (runtime.ROOT / FILE).write_bytes(query.encoded(build()))
    print('Built synthetic runtime fixture; no installed packet or index read.')
