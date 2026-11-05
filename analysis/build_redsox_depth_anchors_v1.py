"""Build regional conditional depth anchors from frozen, audited observations."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/redsox-depth-anchors-operator-v1.json'
FACTS = 'research/redsox-observed-depth-reference-source-facts-v1.json'
OUTPUT = 'research/redsox-conditional-depth-anchors-v1.geojson'
OWNER = 'current:red-sea-saline-overflow'


def encoded(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


def anchor(row):
    if row['entity_id'] != OWNER or row['lower_status'] != 'censored_at_native_velocity_sampling_end':
        raise ValueError('Original owner and sampling censor required')
    for key in ['surface_connection_established', 'physical_current_bottom_established',
                'physical_cast_identity_independently_verified', 'sample_level_synchronization_verified',
                'source_reference_quality_independently_verified', 'tidal_correction_applied',
                'volume_eligible', 'annual_extrema_established', 'reference_route_projection_eligible']:
        if row[key] is not False:
            raise ValueError('No physical, identity, temporal or route promotion')
    if row['physical_layer_thickness_m'] is not None or row['volume_m3'] is not None:
        raise ValueError('No physical thickness or volume')
    top = row['upper_crossing_context']
    upper = top['boundary_depth_m']
    core = row['core_depth_m']
    last = row['supported_penetration_lower_bound_m']
    if (top['status'] != 'first_adjacent_union_joint_predicate_crossing'
            or not top['fine_union_bracket_m'][0] <= upper <= top['fine_union_bracket_m'][1]
            or not upper < core <= last or row['supported_penetration_lower_bound_exclusive'] is not False
            or row['native_union_path_from_core_to_sampling_end_verified'] is not True
            or row['all_native_hydrographic_knots_retained'] is not True):
        raise ValueError('Resolved joint upper crossing, unchanged core and inclusive censored support required')
    lon, lat = row['position_lon_lat']
    if not -180 <= lon <= 180 or not -90 <= lat <= 90:
        raise ValueError('Source longitude/latitude required')
    properties = copy.deepcopy(row)
    properties.update({
        'evidence_class': 'conditional_processed_profile_depth_anchor',
        'source_observations_added': 0,
        'new_primary_measurements': 0,
        'depth_unit': 'm',
        'depth_positive_direction': 'down',
        'conditional_upper_crossing_depth_m': upper,
        'conditional_lower_boundary_depth_m': None,
        'minimum_connected_vertical_support_m': last - upper,
        'minimum_connected_vertical_support_kind': 'inclusive_lower_bound_on_reconstructed_joint_component_salinity_support_extent',
        'minimum_support_is_physical_current_thickness': False,
        'minimum_support_is_uncertainty_or_annual_range': False,
        'upper_crossing_is_physical_flow_top': False,
        'vertical_support_rule': 'signed_component_gt_0.2_m_s_and_practical_salinity_ge_38_on_frozen_native_union_reconstruction',
        'support_reaches_native_sampling_end': True,
        'comparison_group_interpolation_performed': False,
        'between_anchor_interpolation_performed': False,
        'geographic_axis_established': False,
        'paired_width_reference_id': None,
        'horizontal_area_m2': None,
        'geojson_geometry_role': 'provider_reported_station_position_only',
    })
    return {'type': 'Feature', 'id': row['source_case_id'],
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]}, 'properties': properties}


def build(root=ROOT):
    op = json.loads((root / OPERATOR).read_bytes())
    for path, digest in op['input_sha256'].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen input changed: ' + path)
    facts = json.loads((root / FACTS).read_bytes())
    review = json.loads((root / op['validated_source_review_file']).read_bytes())
    if review['tests_passed'] != 24 or review['source_run'] != 41955057852:
        raise ValueError('Validated source admission review required')
    for path in [FACTS, *facts['source_report_pins']]:
        if review['input_sha256'][path] != op['input_sha256'][path]:
            raise ValueError('Source review binding changed')
    if facts['source_profile_cases'] != 4 or facts['original_selected_profile_cases'] != 17:
        raise ValueError('Four supported anchors from original seventeen cases required')
    features = [anchor(row) for row in facts['records']]
    if len({f['id'] for f in features}) != 4 or [r['station'] for r in facts['records']] != [8, 9, 73, 62]:
        raise ValueError('Original unique supported cases required')
    return {'type': 'FeatureCollection', 'schema': 'osw.redsox-conditional-depth-anchors.v1',
            'name': 'REDSOX winter regional conditional depth anchors',
            'entity_id': OWNER, 'features': features,
            'source_facts_file': FACTS, 'input_sha256': op['input_sha256'],
            'counts': {'regional_point_anchors': 4, 'source_component_groups': 2,
                       'new_primary_measurements': 0, 'continuous_route_profiles': 0,
                       'physical_thickness_estimates': 0, 'volume_estimates': 0},
            'interpretation': [
                'Four previously audited processed source profiles, not new independent observations.',
                'Minimum vertical support subtracts resolved joint upper crossing from deepest connected native sample. It is a lower bound on the reconstructed conditional support extent, not physical current thickness.',
                'Upper crossing is not physical flow top; last sample is not seabed or current bottom. No zero-to-bottom layer or symmetric core is assumed.',
                'Provider positions locate anchors. No geographic axis, between-station interpolation, common cast clock, seasonal range or annual envelope is supplied.',
                'Keep the fixed southward and section-normal component groups separate. Source reference quality, physical cast identity, synchronization and water-mass identity remain unverified.',
                'Native precision and numerical crossing brackets are not uncertainty. Existing 818 reference rows and all old projections remain unchanged.',
            ],
            'whole_current_profile': False, 'runtime_changed': False,
            'query_ui_integration_performed': False, 'full_goal_complete': False}


if __name__ == '__main__':
    result = build()
    out = ROOT / 'redsox-depth-anchors-v1'
    out.mkdir(exist_ok=True)
    raw = encoded(result)
    if len(raw) > 2400000:
        raise ValueError('Scientific output cap exceeded')
    (out / 'anchors.geojson').write_bytes(raw)
    print(json.dumps(result['counts']))
