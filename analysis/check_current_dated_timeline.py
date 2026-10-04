"""Verify dated geometry against pinned fields, trace receipts and map joins."""
import json
import math
from pathlib import Path
from shapely.geometry import LineString
from build_current_dated_timeline import ROOT, AUDIT, OUTPUT, digest
from build_cartographic_current_state_join import PROVINCES, load_states, project
from build_gulf_stream_geostrophic_path import load_field, trace
from build_gulf_stream_navo_state_snapshot import geographic_line_length_km

def validate(document):
    if document['status'] != 'research_only_not_canonical_or_ranked' or document['annual_extrema_eligible'] is not False or document['annual_length_range_km'] is not None or document['annual_width_range_km'] is not None:
        raise ValueError('Unsupported admission or annual inference')
    if document['current_id'] != 'gulf-stream-system' or document['geometry_role'] != 'frozen_field_diagnostic_streamline_not_current_axis_or_parcel_track':
        raise ValueError('Identity or geometry meaning changed')
    if document['audit_file'] not in ['research/gulf-stream-geostrophic-repeat-20260918-20260927.json','research/gulf-stream-2025-monthly-sample-receipts.json']:
        raise ValueError('Unsupported acquisition manifest')
    audit_path = ROOT / document['audit_file']
    for key,path in [('audit_sha256',audit_path),('generator_sha256',ROOT/'analysis/build_current_dated_timeline.py'),('trace_algorithm_sha256',ROOT/'analysis/build_gulf_stream_geostrophic_path.py'),('state_map_sha256',PROVINCES)]:
        if document[key] != digest(path):
            raise ValueError('Changed algorithm or source map')
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    if audit.get('sampling_year') == 2025 and audit['dates'] != [f'2025-{month:02d}-15' for month in range(1,13)]:
        raise ValueError('Incomplete annual sampling')
    if [row['date'] for row in document['frames']] != audit['dates']:
        raise ValueError('Missing, duplicated or reordered date')
    states = load_states()
    for frame, observation in zip(document['frames'],audit['observations']):
        path = ROOT/observation['source_subset']
        if frame['source_subset'] != observation['source_subset'] or frame['source_subset_sha256'] != digest(path) or digest(path) != observation['source_subset_sha256'] or frame['figure_sha256'] != digest(ROOT/frame['figure']):
            raise ValueError('Changed frame or source bytes')
        source = json.loads(path.read_text(encoding='utf-8'))
        for field in ['source_url','source_response_sha256','source_algorithm','source_product_status']:
            if frame[field] != source[field]:
                raise ValueError('Frame source mismatch')
        if frame['time_start'] != source['source_time_start'] or frame['time_end_exclusive'] != source['source_time_end_exclusive'] or frame['width_km'] is not None or frame['positional_uncertainty_km'] is not None:
            raise ValueError('Invented time or uncertainty')
        result = trace(source,load_field(source),36.875,10)
        if frame['coordinates_lon_lat'] != result['coordinates_lon_lat'] or frame['diagnostic_length_km'] != result['segment_length_km'] or frame['stop_reason'] != result['stop_reason'] or frame['reaches_downstream_gate'] != (result['stop_reason']=='downstream_longitude_gate'):
            raise ValueError('Geometry, length or stop mismatch')
        sensitivity = frame['diagnostic_sensitivity']
        if sensitivity['range_kind'] != 'finite_seed_and_step_sensitivity_of_gate_reaching_diagnostics' or sensitivity['is_confidence_interval'] is not False or sensitivity['is_width_estimate'] is not False or sensitivity['scenario_grid'] != {'seed_latitudes':[36.625,36.875,37.125], 'steps_km':[5,10,20]}:
            raise ValueError('Unsupported diagnostic range meaning')
        expected_scenarios = []
        fields = load_field(source)
        for latitude in [36.625,36.875,37.125]:
            for step in [5,10,20]:
                scenario = trace(source, fields, latitude, step)
                expected_scenarios.append({'seed_latitude':latitude,'step_km':step,'diagnostic_length_km':scenario['segment_length_km'],'stop_reason':scenario['stop_reason'],'last_lon_lat':scenario['last_lon_lat'],'reaches_downstream_gate':scenario['stop_reason']=='downstream_longitude_gate'})
        successful = [r['diagnostic_length_km'] for r in expected_scenarios if r['reaches_downstream_gate']]
        expected_span = [math.floor(min(successful)/10)*10, math.ceil(max(successful)/10)*10] if successful else None
        if sensitivity['scenarios'] != expected_scenarios or sensitivity['gate_reaching_count'] != len(successful) or sensitivity['rounded_successful_scenario_span_km'] != expected_span:
            raise ValueError('Missing, altered or incorrectly aggregated sensitivity scenarios')
        line = LineString([project(*p) for p in result['coordinates_lon_lat']])
        expected = []
        for code,shape in sorted(states.items()):
            intersection = line.intersection(shape)
            if intersection.length > 0:
                expected.append({'state_code':code,'predicate':'dated_geostrophic_streamline_segment_intersection','intersection_length_km':round(geographic_line_length_km(intersection),1)})
        if frame['state_relations'] != expected:
            raise ValueError('Incorrect dated diagnostic state intersection')

if __name__ == '__main__':
    for path in [OUTPUT, OUTPUT.parent / 'ocean-current-dated-timeline-2025.json']:
        document = json.loads(path.read_text(encoding='utf-8'))
        validate(document)
        print(f"OK: {path.name}; {len(document['frames'])} pinned geometries and state joins; stops retained; no annual extrema")
