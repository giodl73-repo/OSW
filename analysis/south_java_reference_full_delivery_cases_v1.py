"""Independent expected rows and finite complete-response coverage for cloud delivery."""
import copy

import south_java_reference_runtime_v1 as runtime
import south_java_reference_delivery_v1 as delivery
from eicc_reference_delivery_cases_v1 import request, verify_response

MAIN_CASE_COUNT = 20
INDEX_CASE_COUNT = 9


def main_cases(collections):
    q = runtime.query
    rows = collections
    select = lambda name, field, value: [r for r in rows[name] if r.get(field) == value]
    route = select('reference_routes', 'id', q.ROUTE)
    owner = select('objects', 'id', q.TARGET)
    decision = select('route_decisions', 'entity_id', q.TARGET)
    if len(route) != 1 or len(owner) != 1 or len(decision) != 1:
        raise ValueError('Complete selected South Java route/owner/planning rows required')
    cases = [
        (request('reference_routes', 'id', q.ROUTE, limit=1), route),
        (request('reference_routes', 'current_id', q.CURRENT), route),
        (request('objects', 'id', q.TARGET), owner),
        (request('route_decisions', 'entity_id', q.TARGET), decision),
        (request('sources', 'id', 'source:iskandar-south-java-ofes-2006'), select('sources', 'id', 'source:iskandar-south-java-ofes-2006')),
        (request('sources', 'id', q.METHOD), select('sources', 'id', q.METHOD)),
        ({'collection': 'objects', 'record_type': 'named_current', 'limit': 1}, 106),
        ({'collection': 'reference_routes', 'limit': 1}, 82),
        ({'collection': 'widths', 'limit': 1}, 172),
        (request('current_sampling_reference_points', 'entity_id', 'current:east-india-coastal'),
         select('current_sampling_reference_points', 'entity_id', 'current:east-india-coastal')),
        (request('reference_routes', 'current_id', 'east-india-coastal'),
         select('reference_routes', 'current_id', 'east-india-coastal')),
        (request('current_reported_contour_length_summaries', 'entity_id', 'current:loop'),
         select('current_reported_contour_length_summaries', 'entity_id', 'current:loop')),
        (request('current_reported_separation_events', 'entity_id', 'current:loop'),
         select('current_reported_separation_events', 'entity_id', 'current:loop')),
        ({'collection': 'current_model_depth_context', 'sort': {'field': 'id'}, 'limit': 100},
         rows['current_model_depth_context']),
        (request('current_regional_reaches', 'entity_id', 'current:east-african-coastal'),
         select('current_regional_reaches', 'entity_id', 'current:east-african-coastal')),
        (request('reference_routes', 'current_id', q.CURRENT,
            extra=[{'field': 'rank_eligible', 'op': 'eq', 'value': True}]), []),
        (request('reference_routes', 'current_id', q.CURRENT,
            extra=[{'field': 'annual_length_range_km', 'op': 'eq', 'value': None}]), route),
        (request('reference_routes', 'current_id', q.CURRENT,
            extra=[{'field': 'physical_state_join_eligible', 'op': 'eq', 'value': True}]), []),
        (request('sources', 'id', 'source:sprintall-sjc-2010-ombai-confinement'),
         select('sources', 'id', 'source:sprintall-sjc-2010-ombai-confinement')),
        (request('reference_routes', 'current_id', 'pacific-south-equatorial-countercurrent'),
         select('reference_routes', 'current_id', 'pacific-south-equatorial-countercurrent')),
    ]
    if (len(cases) != MAIN_CASE_COUNT or len(cases[9][1]) != 7 or len(cases[10][1]) != 2 or len(cases[11][1]) != 2
            or len(cases[12][1]) != 12 or len(cases[13][1]) != 3 or len(cases[14][1]) != 1
            or len(cases[18][1]) != 1 or len(cases[19][1]) != 1):
        raise ValueError('Declared current and retained evidence coverage differs')
    return copy.deepcopy(cases)


def index_cases():
    paths = sorted(delivery.DOCUMENTS) + ['research/loop-manta-2023-published-metrics-v1.json',
                                        'research/eicc-reference-query-contract-v1.json']
    if len(paths) != INDEX_CASE_COUNT or len(paths) != len(set(paths)):
        raise ValueError('Declared complete source-document query scope differs')
    return paths
