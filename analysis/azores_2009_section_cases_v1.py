"""Keep twenty prior cases and add six independent dated-section UI cases."""
import json
import south_java_reference_full_delivery_cases_v1 as legacy
import azores_2009_section_projection_v1 as p

MAIN_CASE_COUNT = 26
INDEX_CASE_COUNT = 12


def main_cases(collections):
    result = legacy.main_cases(collections)
    binding = json.loads((p.ROOT / p.BINDINGS).read_bytes())
    for row in binding['records']:
        for field, value in [('id', row['id']), ('current_id', row['current_id'])]:
            query = {'collection': 'widths', 'filters': [{'field': field, 'op': 'eq', 'value': value}],
                     'sort': {'field': 'id', 'direction': 'asc'}, 'limit': 100}
            rows = [r for r in collections['widths'] if r.get(field) == value]
            result.append((query, {'section_rows': rows}))
    url = binding['records'][0]['source_url']
    rows = [r for r in collections['widths'] if r.get('source_url') == url]
    if {r['id'] for r in rows} != {r['id'] for r in binding['records']}:
        raise ValueError('Exactly the two original dated sections required')
    for direction, offset in [('asc', 0), ('desc', 1)]:
        query = {'collection': 'widths', 'filters': [{'field': 'source_url', 'op': 'eq', 'value': url}],
                 'sort': {'field': 'id', 'direction': direction}, 'limit': 1, 'offset': offset}
        result.append((query, {'section_rows': rows}))
    if len(result) != MAIN_CASE_COUNT:
        raise ValueError('Declared complete query case count differs')
    return result


def verify_response(query, expected, response):
    if not isinstance(expected, dict) or 'section_rows' not in expected:
        legacy.verify_response(query, expected, response)
        return
    rows = sorted(expected['section_rows'], key=lambda r: r['id'], reverse=query['sort']['direction'] == 'desc')
    offset = query.get('offset', 0)
    selected = rows[offset:offset + query['limit']]
    if response.get('ok') is not True or response['total'] != len(rows) or response['rows'] != selected:
        raise ValueError('Dated section query rows, sort or pagination differ')
    scene = response.get('chart_scene')
    candidates = scene.get('scenes', [scene]) if isinstance(scene, dict) else []
    matches = [r for r in candidates if r.get('kind') == 'azores_2009_section_review']
    if len(matches) != 1:
        raise ValueError('Missing or duplicated original-section comparison scene')
    scene = matches[0]
    binding = json.loads((p.ROOT / p.BINDINGS).read_bytes())
    doc = json.loads((p.ROOT / p.REVIEW).read_bytes())
    expected_ids = sorted({r['id'] for r in rows} & {r['id'] for r in binding['records']})
    if (scene['records'] != binding['records'] or scene['matching_ids'] != expected_ids
            or scene['section_context'] != doc['shared_section_context']
            or scene['enrichments'] != doc['existing_measurement_enrichments']
            or scene['figure_file'] != p.FIGURE or scene['figure_sha256'] != p.sha((p.ROOT / p.FIGURE).read_bytes())):
        raise ValueError('Original-source section scene differs or invents support')


def index_cases():
    paths = sorted(set(legacy.index_cases()) | set(p.documents()))
    if len(paths) != INDEX_CASE_COUNT:
        raise ValueError('Complete source-index query scope differs')
    return paths
