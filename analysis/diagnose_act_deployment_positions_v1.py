"""Offline cloud diagnostic of a specific coordinate hypothesis; never repairs data."""
import hashlib
import json
import signal
import socket
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = 'research/act2010-primary-deployment-position-context-v1.json'
POINTS = 'research/act2011-native-point-observations-v2.json'
GEOMETRY = 'research/source-data/act2011-source-geometry-v1/qualification.json'


def south_position(row):
    deg, minutes = row['latitude_south_degrees'], row['latitude_minutes']
    if not (isinstance(deg, int) and 0 <= deg < 90 and 0 <= minutes < 60):
        raise ValueError('Valid explicitly southern degrees/minutes required')
    lon_deg, lon_minutes = row['longitude_east_degrees'], row['longitude_minutes']
    if not (isinstance(lon_deg, int) and 0 <= lon_deg < 180 and 0 <= lon_minutes < 60):
        raise ValueError('Valid explicitly eastern degrees/minutes required')
    return [lon_deg + lon_minutes / 60, -(deg + minutes / 60)]


def compare(row, archive):
    correct = south_position(row)
    wrong = -row['latitude_south_degrees'] + row['latitude_minutes'] / 60
    tolerance = 0.0001  # Degree comparison tolerance, NOT physical accuracy.
    return {
        'document_survey_position_lon_lat_degrees': correct,
        'archive_position_lon_lat_degrees': list(archive),
        'signed_degree_plus_positive_minutes_hypothesis_latitude': wrong,
        'hypothesis_minus_archive_latitude_degrees': wrong - archive[1],
        'comparison_tolerance_degrees': tolerance,
        'longitude_matches_within_comparison_tolerance': abs(correct[0] - archive[0]) <= tolerance,
        'latitude_hypothesis_matches_within_comparison_tolerance': abs(wrong - archive[1]) <= tolerance,
        'coordinate_correction_applied': False,
        'geographic_assignment_eligible': False,
        'physical_state_join_eligible': False,
        'route_projection_eligible': False,
        'width_join_eligible': False,
        'physical_bottom_m': None,
        'physical_thickness_m': None,
        'volume_m3': None,
    }


def numeric_count(value):
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return 1
    if isinstance(value, list):
        return sum(map(numeric_count, value))
    if isinstance(value, dict):
        return sum(map(numeric_count, value.values()))
    return 0


def build():
    raw = {p: (ROOT / p).read_bytes() for p in [CONTEXT, POINTS, GEOMETRY]}
    if sum(map(len, raw.values())) > 100000:
        raise ValueError('Bounded retained metadata packet exceeded')
    parsed = {p: json.loads(v) for p, v in raw.items()}
    typed = sum(map(numeric_count, parsed.values()))
    if typed > 5000:
        raise ValueError('Typed metadata budget exceeded')
    context = parsed[CONTEXT]
    if context['original_pdf_byte_custody'] or context['B']['native_serial_number_match_verified']:
        raise ValueError('Do not upgrade indexed-text evidence or unverified serial linkage')
    b_rows = parsed[POINTS]['instrument_observations']
    points = [r['source_coordinate'] for group in b_rows for r in group]
    if len(points) != 6 or any(p != points[0] for p in points):
        raise ValueError('Original six consistent-coordinate outcomes required')
    b = compare(context['B'], points[0])
    # An explicitly unassigned retained location-list row; no instrument identity claim.
    d = compare(context['D'], [27.8633003234863, -33.9793014526367])
    return {
        'schema': 'osw.act-deployment-position-diagnostic.v1',
        'status': 'PRIMARY_INDEXED_SURVEY_POSITION_CANDIDATE_NOT_A_COORDINATE_REPAIR',
        'input_sha256': {p: hashlib.sha256(v).hexdigest() for p, v in raw.items()},
        'source_url': context['source_url'],
        'original_pdf_byte_custody': False,
        'B': b,
        'D_unassigned_longitude_control': d,
        'D_instrument_row_assignment_verified': False,
        'B_native_serial_number_match_verified': False,
        'six_native_point_records_modified': False,
        'new_native_profiles_selected': 0,
        'new_native_ocean_values_decoded': 0,
        'new_provider_operations': 0,
        'case_operations_used_unchanged': 13,
        'case_operations_cap_unchanged': 18,
        'case_time_charge_seconds_unchanged': 55.03573454399998,
        'case_time_cap_seconds_unchanged': 210,
        'case_native_scalar_bound_unchanged': 85175,
        'retained_metadata_numeric_values': typed,
        'retained_metadata_bytes': sum(map(len, raw.values())),
        'new_depth_references_admitted': 0,
        'physical_or_seasonal_depth_range_admitted': False,
        'full_goal_complete': False,
        'interpretation': [
            'A matching longitude control cannot prove a shared conversion error at B.',
            'The documentary survey position remains separate and provisional because only indexed primary text is available.',
            'An exact automated repair requires independent instrument identity, coordinate provenance and original-document verification.',
            'No repeated provider requests, new geometry intersections or physical current-bottom estimates.'
        ]
    }


def main():
    def stopped(signum, frame):
        raise SystemExit('Diagnostic stopped; do not replay automatically')
    signal.signal(signal.SIGTERM, stopped)
    signal.signal(signal.SIGALRM, stopped)
    signal.alarm(45)
    socket.socket = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('Offline only'))
    output = ROOT / 'act-deployment-position-diagnostic-v1'
    output.mkdir(exist_ok=False)
    report = build()
    (output / 'diagnostic.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps({'status': report['status'], 'B': report['B'], 'D': report['D_unassigned_longitude_control']}))


if __name__ == '__main__':
    main()
