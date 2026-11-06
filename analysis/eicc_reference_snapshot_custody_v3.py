"""Compare complete parent/child presentation APIs without rewriting source data."""
import eicc_reference_delivery_v1 as delivery


def verify(parent, candidate, expected_catalog, dashboard_text, candidate_logical_sha):
    if (parent.get('ok') is not True or candidate.get('ok') is not True
            or parent.get('bundle_sha256') != delivery.PARENT_LOGICAL_SHA
            or candidate.get('bundle_sha256') != candidate_logical_sha
            or set(parent) != set(candidate)
            or delivery.encoded(candidate.get('working_reference_routes')) != delivery.encoded(expected_catalog)):
        raise ValueError('Complete atlas/seasonal snapshot identity or catalog differs')
    changed = {'bundle_sha256', 'working_reference_routes', 'sources_json'}
    for key in set(parent) - changed:
        if delivery.encoded(parent[key]) != delivery.encoded(candidate[key]):
            raise ValueError('Unrelated presentation API field changed: ' + key)
    old_sources, new_sources = parent['sources_json'], candidate['sources_json']
    if set(old_sources) != set(new_sources): raise ValueError('Historical presentation source inventory changed')
    for path, original in old_sources.items():
        expected = dashboard_text if path == delivery.DASHBOARD else original
        if delivery.encoded(new_sources[path]) != delivery.encoded(expected):
            raise ValueError('Historical presentation source bytes changed: ' + path)
    return {'status': 'PASS', 'complete_catalog_matches_source_projection': True,
            'unrelated_presentation_fields_preserved': len(set(parent) - changed),
            'original_source_documents_preserved': len(old_sources) - int(delivery.DASHBOARD in old_sources),
            'dashboard_source_replaced': delivery.DASHBOARD in old_sources}
