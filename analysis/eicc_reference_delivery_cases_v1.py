"""Declared main-store queries and independent semantic checks for cloud delivery."""
import eicc_reference_query_v1 as context

MAIN_CASE_COUNT = 24
INDEX_CASE_COUNT = 25


def request(collection, field, value, *, extra=(), limit=100):
    return {'collection': collection, 'filters': [{'field': field, 'op': 'eq', 'value': value}, *extra],
            'sort': {'field': 'id', 'direction': 'asc'}, 'limit': limit}


def main_cases(expected):
    routes, points, scales = (expected[n] for n in [context.ROUTES, context.POINTS, context.SCALES])
    route_query = lambda: request(context.ROUTES, 'current_id', context.CURRENT)
    cases = [(route_query(), routes)]
    cases += [(request(context.ROUTES, 'id', row['id'], limit=1), [row]) for row in routes]
    cases += [(request(context.POINTS, 'entity_id', context.TARGET), points),
              (request(context.POINTS, 'id', points[-1]['id']), [points[-1]]),
              (request(context.POINTS, 'is_strict_eicc_path_reference', False), [points[-1]]),
              (request(context.POINTS, 'geometry', None), points),
              (request(context.SCALES, 'entity_id', context.TARGET), scales),
              (request(context.SCALES, 'paired_current_width_km', None), scales),
              (request(context.SCALES, 'paired_current_width_km', 0), [])]
    cases += [(request('sources', 'id', row['id']), [row]) for row in expected['sources']]
    cases += [(request('objects', 'id', context.TARGET), [expected['owner']]),
              (request('route_decisions', 'entity_id', context.TARGET), [expected['decision']]),
              ({'collection': 'objects', 'record_type': 'named_current', 'limit': 1}, 106),
              ({'collection': 'widths', 'limit': 1}, 172),
              (request('current_reported_contour_length_summaries', 'entity_id', 'current:loop'), expected['loop_summaries']),
              (request('current_reported_separation_events', 'entity_id', 'current:loop'), expected['loop_events']),
              ({'collection': 'current_model_depth_context', 'sort': {'field': 'id'}, 'limit': 100}, expected['legacy_depths']),
              (request(context.ROUTES, 'current_id', context.CURRENT,
                       extra=[{'field': 'rank_eligible', 'op': 'eq', 'value': True}]), []),
              (request(context.SCALES, 'geometry', None), scales),
              (request(context.POINTS, 'current_thickness_m', None), points),
              (request(context.ROUTES, 'current_id', context.CURRENT,
                       extra=[{'field': 'annual_length_range_km', 'op': 'eq', 'value': None}]), routes)]
    if len(cases) != MAIN_CASE_COUNT:
        raise ValueError('Declared main-query scope changed')
    return cases


def verify_response(query, expected, response):
    if response.get('ok') is not True:
        raise ValueError('Query did not succeed')
    if type(expected) is int:
        if response.get('total') != expected or len(response['rows']) != 1:
            raise ValueError('Historical inventory query differs')
        return
    rows = sorted(expected, key=lambda r: r['id'])
    if response.get('total') != len(rows) or context.encoded(response['rows']) != context.encoded(rows):
        raise ValueError('Complete query rows differ from prepared source projection')
    name = query['collection']
    if name in [context.POINTS, context.SCALES]:
        if response.get('map_scene') is not None or response.get('chart_scene') is not None:
            raise ValueError('Source diagnostics gained an inferred geographic or temporal scene')
    if name == context.ROUTES:
        scene = response.get('map_scene')
        if (not isinstance(scene, dict) or scene.get('inspection_collection') != context.ROUTES
                or scene.get('matching_objects') != len(rows) or scene.get('mapped_objects') != len(rows)
                or scene.get('unmapped_objects') != 0 or scene.get('omitted_features') != []
                or len(scene.get('features', [])) != len(rows)
                or sorted(f['entity_id'] for f in scene['features']) != sorted(r['id'] for r in rows)
                or any(f['role'] != 'editorial_reference_route' or not f['primitive'].get('d')
                       for f in scene['features'])):
            raise ValueError('Reference map selection does not match the selected route IDs')
