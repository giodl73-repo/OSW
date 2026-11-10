"""Regional fitted Gulf Stream decay-depth profiles, with explicit geometry assumptions."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/current-depth-route-projection-operator-v11.json'
OUTPUT = 'research/current-depth-route-projections-v11.json'
CSV = 'research/current-depth-route-projections-v11.csv'
GEOD = Geod(ellps='WGS84')


def group_profiles(descriptors, section_ids):
    expected = {(kind, month, section) for kind, month in [('mean', None)] + [('annual_cycle', m) for m in range(1, 13)] for section in section_ids}
    grouped = {}
    for row in descriptors:
        key = row['source_product_kind'], row['calendar_month_phase'], row['section_id']
        if key not in expected or key in grouped:
            raise ValueError('Unexpected or duplicate section/phase profile')
        grouped[key] = row
    if set(grouped) != expected:
        raise ValueError('All five original sections and all thirteen source fit cases required')
    return [[grouped[kind, month, section] for section in section_ids]
            for kind, month in [('mean', None)] + [('annual_cycle', m) for m in range(1, 13)]]


def anchor_eligible(anchor):
    depth = anchor['source_computed_depth_descriptor_m']
    return (isinstance(depth, (float, int)) and math.isfinite(depth) and depth >= 0
            and anchor['source_lower_status'] == 'adjacent_isotach_crossing'
            and anchor['source_horizontal_selection_status'] == 'interior_fitted_section_maximum_not_independently_validated_axis')


def descriptor_at_distance(anchors, distance):
    if not math.isfinite(distance):
        raise ValueError('Finite reference distance required')
    if not all(a['distance_km'] < b['distance_km'] for a, b in zip(anchors, anchors[1:])):
        raise ValueError('Strictly ascending original anchor distances required')
    for a in anchors:
        if abs(distance - a['distance_km']) < 1e-8:
            return (a['source_computed_depth_descriptor_m'], [a], 'source_fitted_section_decay_depth') if anchor_eligible(a) else (None, [a], 'unknown_at_unresolved_or_edge_anchor')
    for a, b in zip(anchors, anchors[1:]):
        if a['distance_km'] < distance < b['distance_km']:
            if not anchor_eligible(a) or not anchor_eligible(b):
                return None, [a, b], 'unknown_between_unresolved_or_edge_anchors'
            fraction = (distance - a['distance_km']) / (b['distance_km'] - a['distance_km'])
            return (a['source_computed_depth_descriptor_m'] + fraction * (b['source_computed_depth_descriptor_m'] - a['source_computed_depth_descriptor_m']),
                    [a, b], 'assumed_linear_between_fitted_section_depths')
    return None, [], 'unknown_outside_reference_connector'


def geometry(points):
    distances = [0.]
    bearings = []
    for a, b in zip(points, points[1:]):
        bearing, _, metres = GEOD.inv(*a, *b)
        if not math.isfinite(metres) or metres <= 0:
            raise ValueError('Distinct finite source anchor coordinates required')
        distances.append(distances[-1] + metres / 1000)
        bearings.append(bearing)
    return [round(v, 6) for v in distances], bearings


def coordinate_at_distance(anchors, bearings, distance):
    for a in anchors:
        if abs(distance - a['distance_km']) < 1e-8:
            return list(a['source_lon_lat'])
    for i, (a, b) in enumerate(zip(anchors, anchors[1:])):
        if a['distance_km'] < distance < b['distance_km']:
            lon, lat, _ = GEOD.fwd(*a['source_lon_lat'], bearings[i], (distance - a['distance_km']) * 1000)
            return [round(lon, 6), round(lat, 6)]
    return None


def project_case(rows, op):
    anchors = []
    for row in rows:
        half = row['half_sampled_core_component_decay']
        if half is None or half.get('relative_sampled_core_fraction') != .5:
            raise ValueError('A separately typed half-sampled-core source diagnosis is required')
        anchors.append({'section_id': row['section_id'], 'source_lon_lat': row['selected_lon_lat'],
                        'source_computed_depth_descriptor_m': half['lower_depth_m'],
                        'source_native_bracketing_depths_m': half.get('lower_bracket_m'),
                        'source_lower_status': half['lower_status'],
                        'source_horizontal_selection_status': row['horizontal_selection_status'],
                        'locked_reference_direction_at100m_degrees': row['locked_reference_direction_at100m_degrees'],
                        'source_file': row['source_file'], 'source_sha256': row['source_sha256'],
                        'source_pointer': row['source_pointer'],
                        'source_profile_ref': row['source_file'] + '#' + row['source_pointer'],
                        'source_product_kind': row['source_product_kind'],
                        'calendar_month_phase': row['calendar_month_phase'],
                        'actual_provider_phase_timestamp_utc': row['actual_provider_phase_timestamp_utc'],
                        'nominal_phase_calendar_date': row['nominal_phase_calendar_date']})
    if len({(a['source_product_kind'], a['calendar_month_phase'], a['actual_provider_phase_timestamp_utc'], a['nominal_phase_calendar_date']) for a in anchors}) != 1:
        raise ValueError('Section fits must share the exact source phase context')
    distances, bearings = geometry([a['source_lon_lat'] for a in anchors])
    for a, distance in zip(anchors, distances):
        a['distance_km'] = distance
    sample_distances = set(distances) | {i * 50. for i in range(1, math.floor(distances[-1] / 50) + 1)}
    samples = []
    for distance in sorted(sample_distances):
        value, used, status = descriptor_at_distance(anchors, distance)
        samples.append({'distance_along_reference_route_km': distance,
                        'nominal_reference_connector_lon_lat': coordinate_at_distance(anchors, bearings, distance),
                        'computed_depth_descriptor_m': round(value, 6) if value is not None else None,
                        'projected_depth_descriptor_m': int(10 * round(value / 10)) if value is not None else None,
                        'status': status, 'source_reference_ids': [],
                        'source_profile_refs': [a['source_profile_ref'] for a in used],
                        'source_section_ids': [a['section_id'] for a in used],
                        'depth_uncertainty_m': None, 'physical_thickness_m': None, 'volume_eligible': False})
    segments = [{'section_ids': [a['section_id'], b['section_id']],
                 'reference_distance_interval_km': [a['distance_km'], b['distance_km']],
                 'projection_status': 'conditional_linear_reference_connector' if anchor_eligible(a) and anchor_eligible(b) else 'gap_no_projection',
                 'physical_current_continuity_established': False}
                for a, b in zip(anchors, anchors[1:])]
    month = anchors[0]['calendar_month_phase']
    tag = 'mean' if month is None else f'phase-{month:02d}'
    return {'id': 'gulf-stream-spray2023-half-core-' + tag + '-connector-v1',
            'entity_id': 'current:gulf-stream', 'status': 'REGIONAL_FITTED_DECAY_DEPTH_REFERENCE_CONNECTOR',
            'metric': 'projected_relative_core_component_decay_depth_descriptor',
            'vertical_datum': 'local_sea_surface_positive_down',
            'coordinate_kind': 'WGS84_cumulative_fitted_section_core_connector_distance',
            'geometry_role': 'source_fitted_section_core_connector_not_observed_current_axis',
            'route_id': 'gulf-stream-spray2023-five-section-' + tag + '-connector', 'route_file': None,
            'reference_connector_length_km': distances[-1], 'whole_current_length_replaced': False,
            'source_reference_ids': [], 'source_profile_refs': [a['source_profile_ref'] for a in anchors],
            'anchors': anchors, 'segments': segments, 'samples': samples,
            'source_product_kind': anchors[0]['source_product_kind'],
            'calendar_months': None if month is None else [month], 'calendar_month_phase': month,
            'phase_label': 'time mean' if month is None else f'fitted annual-cycle phase {month:02d}-15',
            'actual_provider_phase_timestamp_utc': anchors[0]['actual_provider_phase_timestamp_utc'],
            'nominal_phase_calendar_date': anchors[0]['nominal_phase_calendar_date'],
            'source_time_basis': 'Published2015-07-16 through2023-05-30 fitted glider mean/two-harmonic annual cycle; phase timestamps are not instantaneous observations or monthly means.',
            'common_fit_observation_period': op['common_fit_observation_period'],
            'common_record_period': None, 'simultaneous_record_period_established': False,
            'source_component_reference_frame': 'signed_projection_onto_each_selected_column_mean_direction_at100m_locked_with_depth',
            'relative_core_fraction': .5, 'model_product': None,
            'descriptor_display_rounding_m': 10,
            'derived_geometry_serialization_decimals': 6,
            'serialization_decimals_are_physical_accuracy': False,
            'interpolation_assumption': op['interpolation_assumption'],
            'physical_thickness_m': None, 'uncertainty_m': None, 'annual_range_m': None,
            'whole_current_representative': False, 'eligibility': copy.deepcopy(op['eligibility']),
            'full_goal_complete': False}


def validate_source_rows(facts, chunks):
    for row in facts['descriptors']:
        if row['source_file'] not in chunks:
            raise ValueError('Unregistered source section file')
        source = chunks[row['source_file']]
        if source['entity_context'] != 'current:gulf-stream' or source['section_definition']['id'] != row['section_id']:
            raise ValueError('Source regional current identity changed')
        index = int(row['source_pointer'].split('/')[-1])
        if row['source_pointer'] != '/records/' + str(index):
            raise ValueError('Source record pointer changed')
        raw = source['records'][index]
        profile = raw['selected_profile']
        for key in ['source_product_kind', 'calendar_month_phase', 'actual_provider_phase_timestamp_utc', 'nominal_phase_calendar_date', 'horizontal_selection_status']:
            if row[key] != raw[key]:
                raise ValueError('Source phase/selection context changed')
        if (row['selected_lon_lat'] != profile['source_lon_lat']
                or row['half_sampled_core_component_decay'] != profile['half_sampled_core_component_decay']
                or row['locked_reference_direction_at100m_degrees'] != profile['locked_reference_direction_at100m_degrees']):
            raise ValueError('Source depth, position or locked frame changed')


def phase_spans(projections, section_ids):
    result = []
    for section in section_ids:
        anchors = [a for p in projections if p['source_product_kind'] == 'annual_cycle'
                   for a in p['anchors'] if a['section_id'] == section and anchor_eligible(a)]
        values = [a['source_computed_depth_descriptor_m'] for a in anchors]
        result.append({'section_id': section, 'fitted_phase_samples': len(values),
                       'sampled_fitted_phase_depth_span_m': [min(values), max(values)] if values else None,
                       'all12_prescribed_phases_supported': len(values) == 12,
                       'actual_annual_extrema_established': False, 'confidence_interval': False,
                       'interpretation': 'Span among twelve fitted day15 phase samples, excluding the mean; neither observed annual extrema nor physical uncertainty.'})
    return result


def build(root=ROOT):
    read = lambda p: json.loads((root / p).read_bytes())
    op = read(OPERATOR)
    for path, pin in op['input_sha256'].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != pin:
            raise ValueError('Frozen profile input changed: ' + path)
    if any(op['eligibility'].values()):
        raise ValueError('No whole-current physical promotion is authorized')
    prior = read(op['previous_projection_file'])
    depth = read(op['depth_register_file'])
    facts = read(op['source_facts_file'])
    chunks = {path: read(path) for path in op['section_files']}
    validate_source_rows(facts, chunks)
    groups = group_profiles(facts['descriptors'], op['section_ids'])
    additions = [project_case(rows, op) for rows in groups]
    projections = copy.deepcopy(prior['projections']) + additions
    records = []
    for raw in depth['records']:
        row = copy.deepcopy(next(r for r in prior['records'] if r['entity_id'] == raw['entity_id']))
        row['depth_reference_ids'] = list(raw['depth_reference_ids'])
        row['projection_ids'] = [p['id'] for p in projections if p['entity_id'] == row['entity_id']]
        row['projection_status'] = 'regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected'
        records.append(row)
    owners = sum(bool(r['projection_ids']) for r in records)
    pins = dict(op['input_sha256'], **{OPERATOR: hashlib.sha256((root / OPERATOR).read_bytes()).hexdigest()})
    return {'schema': 'osw.current-depth-route-projections.v11',
            'status': 'REGIONAL_GULF_STREAM_FITTED_MEAN_AND12_PHASE_DECAY_DEPTH_CONNECTORS',
            'generator_file': 'analysis/build_current_depth_route_projections_v11.py',
            'generator_sha256': hashlib.sha256((root / 'analysis/build_current_depth_route_projections_v11.py').read_bytes()).hexdigest(),
            'input_sha256': pins, 'previous_twelve_projection_records_preserved': projections[:12] == prior['projections'],
            'counts': {'catalog_identities': len(records), 'identities_with_regional_projection_scenarios': owners,
                       'identities_not_yet_projected': len(records) - owners, 'regional_projection_scenarios': len(projections),
                       'source_anchor_references': prior['counts']['source_anchor_references'],
                       'new_fitted_source_profile_anchors': 65, 'new_fitted_profile_connectors': 13,
                       'new_conditional_adjacent_segments': sum(s['projection_status'] != 'gap_no_projection' for p in additions for s in p['segments']),
                       'new_depth_measurements': 0, 'whole_route_physical_depth_profiles': 0, 'volume_estimates': 0,
                       'regional_reference_geometry_volume_scenarios': prior['counts']['regional_reference_geometry_volume_scenarios']},
            'interpretation': op['interpretation'], 'regional_volume_scenario_file': prior['regional_volume_scenario_file'],
            'fitted_phase_depth_sample_spans': phase_spans(additions, op['section_ids']),
            'records': records, 'projections': projections, 'runtime_changed': False,
            'query_ui_integration_performed': False, 'full_goal_complete': False}


def csv_bytes(document, root=ROOT):
    op = json.loads((root / OPERATOR).read_bytes())
    reader = csv.DictReader(io.StringIO((root / op['previous_projection_csv']).read_text(encoding='utf8')))
    columns = list(reader.fieldnames)
    rows = list(reader)
    columns += [k for k in ['computed_depth_descriptor_m', 'source_profile_refs', 'source_section_ids',
        'source_component_reference_frame', 'relative_core_fraction', 'common_fit_observation_period',
        'actual_provider_phase_timestamp_utc', 'nominal_phase_calendar_date', 'interpolation_assumption'] if k not in columns]
    for p in document['projections'][12:]:
        for sample in p['samples']:
            row = {k: v for k, v in sample.items() if k in columns}
            row.update({k: p.get(k) for k in ['entity_id', 'route_id', 'geometry_role', 'coordinate_kind', 'metric',
                'vertical_datum', 'phase_label', 'calendar_months', 'source_time_basis', 'source_component_reference_frame',
                'relative_core_fraction', 'common_fit_observation_period', 'actual_provider_phase_timestamp_utc',
                'nominal_phase_calendar_date', 'interpolation_assumption']})
            row.update(projection_id=p['id'], longitude=sample['nominal_reference_connector_lon_lat'][0],
                       latitude=sample['nominal_reference_connector_lon_lat'][1])
            for key, value in list(row.items()):
                if isinstance(value, (list, dict)):
                    row[key] = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
            rows.append(row)
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')


def main():
    result = build()
    out = Path('current-depth-route-projections-v11')
    out.mkdir(exist_ok=True)
    (out / 'projections.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf8')
    (out / 'projections.csv').write_bytes(csv_bytes(result))
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
