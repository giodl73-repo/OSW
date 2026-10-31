"""Query semantics and the single106-to111 catalogue inventory migration."""
import equatorial_basin_identity_runtime_v1 as runtime
query = runtime.query


def adapt_legacy_cases(cases):
    result, changed = [], 0
    target = {'collection': 'objects', 'record_type': 'named_current', 'limit': 1}
    for request, expected in cases:
        if request == target:
            if type(expected) is not int or expected != 106:
                raise ValueError('Exact106-current legacy expectation required')
            expected = 111
            changed += 1
        result.append((request, expected))
    if changed != 1:
        raise ValueError('Exactly one historical named-current inventory case required')
    return result


def main_cases(collections):
    c = runtime.contract()
    cases = []

    def add(collection, field=None, value=None, **extra):
        filters = [] if field is None else [{'field': field, 'op': 'eq', 'value': value}]
        request = {'collection': collection, 'filters': filters, 'limit': 100, **extra}
        expected = [row for row in collections[collection]
                    if field is None or row.get(field) == value]
        cases.append((request, expected))

    add('current_basin_memberships')
    add('current_basin_memberships', limit=1, offset=2)
    add('current_basin_memberships', sort={'field': 'id', 'direction': 'desc'}, limit=2)
    for family in sorted(c['prior_family_records']):
        add('current_basin_memberships', 'family_entity_id', family)
    add('current_basin_memberships', 'entity_id', 'current:absent')
    for entity in c['expected_entity_ids']:
        add('current_basin_memberships', 'entity_id', entity)
        add('entities', 'id', entity)
        add('objects', 'id', entity)
        for name in ['names', 'length_assessments', 'current_identity_admissions']:
            add(name, 'entity_id', entity)
        slug = entity.removeprefix('current:')
        add('route_decisions', 'current_id', slug)
        add('widths', 'current_id', slug)
        add('reference_routes', 'current_id', slug)
    if len(cases) != 51:
        raise ValueError('Exact51-query basin identity inventory required')
    return cases


def verify(request, expected, response):
    sort = request.get('sort', {'field': 'id', 'direction': 'asc'})
    ordered = sorted(expected, key=lambda r: r[sort['field']], reverse=sort['direction'] == 'desc')
    start = request.get('offset', 0)
    if response.get('ok') is not True or response.get('total') != len(expected) or response.get('rows') != ordered[start:start + request['limit']]:
        raise ValueError('Basin identity query filtering/sorting/pagination differs')
    if request['collection'] == 'current_basin_memberships':
        #The chart represents all matches before result-row pagination.
        if response.get('chart_scene') != runtime.membership_scene(ordered):
            raise ValueError('Membership scene must retain only matching rows before pagination')
        if response.get('map_scene') is not None:
            raise ValueError('Membership relationships acquired unsupported map geometry')
    elif request['collection'] in {'widths', 'reference_routes'}:
        if expected or response.get('chart_scene') is not None:
            raise ValueError('Identity-only current acquired measurement or route evidence')
        if request['collection'] == 'widths':
            if response.get('map_scene') is not None:
                raise ValueError('Unmeasured width acquired map geometry')
        else:
            scene = response.get('map_scene')
            if (not isinstance(scene, dict) or scene.get('features') != []
                    or scene.get('matching_objects') != 0 or scene.get('mapped_objects') != 0
                    or scene.get('unmapped_objects') != 0 or scene.get('omitted_features') != []):
                raise ValueError('Empty reference-route map must have no mapped geometry')
    elif request['collection'] == 'objects':
        scene = response.get('map_scene')
        if (not isinstance(scene, dict) or scene.get('features') != []
                or scene.get('matching_objects') != len(expected) or scene.get('mapped_objects') != 0
                or scene.get('unmapped_objects') != len(expected) or scene.get('omitted_features') != []):
            raise ValueError('New current identity acquired unsupported map placement')
