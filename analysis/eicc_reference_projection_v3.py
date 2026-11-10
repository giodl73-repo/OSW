"""Source-bound EICC revision and inline atlas cards; no installed datasets loaded."""
import copy
import json
import xml.etree.ElementTree as ET

import eicc_reference_delivery_v1 as delivery
import eicc_reference_query_v1 as context

IDENTITY = 'research/indian-current-identity-query-contract-v1.json'
PLANNING = 'research/indian-current-reference-route-planning-v1.json'
MODULE = 'analysis/eicc_reference_projection_v3.py'


def source(path):
    raw = (context.ROOT / path).read_bytes()
    return raw, json.loads(raw)


def original_decision():
    return next(row for row in source(IDENTITY)[1]['additions']['route_decisions'] if row['entity_id'] == context.TARGET)


def atlas_reports(contract):
    figure = ET.fromstring((context.ROOT / context.FIGURE).read_bytes())
    viewbox = [float(n) for n in figure.attrib['viewBox'].split()]
    features = {feature['candidate_id']: feature for feature in contract['owner_map_features']}
    result = {}
    for row in contract['collections'][context.ROUTES]:
        report = copy.deepcopy(row)
        report.update(
            schema='osw.current-reference-path-input.v1',
            rendering_role='derived_inline_source_reference_card_not_additional_observation',
            source_candidate_file=context.CANDIDATE, source_candidate_pointer=row['source_pointer'],
            reported_approximate_reference_path_km=row['approximate_reference_path_km'],
            coordinates_lon_lat=copy.deepcopy(features[row['id']]['geometry']['coordinates']),
            figure_aspect_ratio=viewbox[2] / viewbox[3], map_view_box=viewbox,
            scenario_range_km=copy.deepcopy(row['public_editorial_probe_span_km']),
            coordinate_selection='Saved nominal WGS84 reference connection through three approximate source anchors. The source datum is unspecified. Display sampling does not reconstruct an observed current axis.',
            scenario_rule='Nine retained combinations of minus10,zero,plus10km leg bend probes per coordinate convention. Their span is editorial geometry sensitivity, not measurement uncertainty or an annual range.',
            source_citation='Gangopadhyay et al. (2013), Geophysical Research Letters, doi:10.1002/grl.50412',
            source_reference_anchors=[{'id': chr(65 + i), 'source_notation': f'{lon:g} degrees E, {lat:g} degrees N'}
                                      for i, (lon, lat) in enumerate(row['coordinates_lon_lat'])],
            state_scope_note='No physical OSW state intersections are admitted. These editorial reference connections are navigation evidence only.',
            nasa_movie_context=[], recommended_nasa_tile_id=None,
            method='Use the saved zero-offset shortest WGS84 geodesic connection and retained bend cases. The590km and630km conventions remain separate, unranked regional references.',
            map_land_check='All18 declared cases clear both retained coastline masks in their checked representations. These checks do not establish a physical axis, width or navigational clearance.',
            remaining_gates=['Recover continuous source axes and defensible endpoints.',
                             'Resolve source coordinate conventions without treating them as physical extrema.',
                             'Establish independent width, seasonal range and uncertainty evidence.'])
        result[row['id']] = report
    return result


def candidate(bundle, contract):
    identity_raw, identity = source(IDENTITY)
    planning_raw, planning = source(PLANNING)
    inputs = bundle['manifest'].get('input_sha256', {})
    if inputs.get(IDENTITY) != delivery.sha(identity_raw) or inputs.get(PLANNING) != delivery.sha(planning_raw):
        raise ValueError('Original admitted Indian-current source receipts differ')
    expected = next(row for row in identity['additions']['route_decisions'] if row['entity_id'] == context.TARGET)
    planning_entry = next(row for row in planning['entries'] if row['current_id'] == context.CURRENT)
    actual = [row for row in bundle['collections']['route_decisions'] if row['entity_id'] == context.TARGET]
    if (len(actual) != 1 or context.encoded(actual[0]) != context.encoded(expected)
            or expected['source_catalog_file'] != PLANNING
            or expected['source_catalog_sha256'] != delivery.sha(planning_raw)
            or context.encoded(expected['source_decision']) != context.encoded(planning_entry)):
        raise ValueError('Exact admitted EICC planning decision and source projection required')
    result, dashboard, audit = delivery.candidate(bundle, contract)
    decision = next(row for row in result['collections']['route_decisions'] if row['entity_id'] == context.TARGET)
    decision['source_decision']['name_source_url'] = decision['source_url']
    source_raw = (context.ROOT / context.CANDIDATE).read_bytes()
    if delivery.sha(source_raw) != contract['input_sha256'][context.CANDIDATE]:
        raise ValueError('Reviewed candidate source differs')
    query_raw = (context.ROOT / context.FILE).read_bytes()
    if query_raw != context.encoded(contract): raise ValueError('Exact saved query contract required')
    result['manifest'][delivery.RECEIPT]['planning_revision'] = {
        'schema': 'osw.eicc-source-reference-planning-revision.v2',
        'owner_id': context.TARGET, 'source_file': context.CANDIDATE,
        'source_sha256': delivery.sha(source_raw), 'source_json': source_raw.decode('utf-8'),
        'prior_decision_json': context.encoded(expected).decode('utf-8'),
        'query_contract_file': context.FILE, 'query_contract_sha256': delivery.sha(query_raw),
        'query_contract_json': query_raw.decode('utf-8'), 'atlas_reports': atlas_reports(contract)}
    audit.update(original_admission_planning_source=PLANNING, exact_compiled_prior_decision_verified=True,
                 planning_source_url_projection_consistent=True, inline_atlas_reports=2,
                 runtime_compatibility_verified=False)
    return result, dashboard, audit


def catalog_projection(catalog, revised_bundle):
    """Specify the complete atlas projection for the corresponding Rust adapter."""
    receipt = revised_bundle['manifest'][delivery.RECEIPT]['planning_revision']
    routes = json.loads(receipt['query_contract_json'])['collections'][context.ROUTES]
    if any(row['current_id'] == context.CURRENT for row in catalog['candidates']):
        raise ValueError('Partial or repeated EICC atlas projection')
    result = copy.deepcopy(catalog)
    for row in routes:
        report = receipt['atlas_reports'][row['id']]
        entry = copy.deepcopy(row)
        entry.update(candidate_file=context.CANDIDATE, candidate_sha256=row['source_file_sha256'],
                     route_extent_kind='regional source-anchor reference connection',
                     scenario_range_km=copy.deepcopy(row['public_editorial_probe_span_km']),
                     nominal_atlas_state_crossings=[], state_intersection_status='unassessed_no_physical_join_admitted',
                     remaining_gates=copy.deepcopy(report['remaining_gates']), report_inline=copy.deepcopy(report))
        result['candidates'].append(entry)
    decision = next(row for row in revised_bundle['collections']['route_decisions'] if row['entity_id'] == context.TARGET)
    matches = [row for row in result['remaining_current_decisions'] if row['current_id'] == context.CURRENT]
    if len(matches) != 1 or matches[0]['candidate_ids'] != []: raise ValueError('Original EICC catalog plan required')
    result['remaining_current_decisions'] = [copy.deepcopy(decision['source_decision']) if row['current_id'] == context.CURRENT else row
                                            for row in result['remaining_current_decisions']]
    counts = result['counts']
    counts['route_candidates'] += 2
    counts['currents_with_route_candidates'] += 1
    for key in ['currents_without_route_candidates', 'currents_without_any_reference_card']:
        if type(counts.get(key)) is not int or counts[key] < 1: raise ValueError('Invalid prior atlas count')
        counts[key] -= 1
    strategies = [s for s in result['planning_taxonomy']['strategies'] if s['id'] == decision['strategy_id']]
    if len(strategies) != 1 or strategies[0]['unbuilt_count'] < 1: raise ValueError('Original EICC strategy count required')
    strategies[0]['unbuilt_count'] -= 1
    return result
