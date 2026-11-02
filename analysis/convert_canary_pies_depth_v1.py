"""Convert published reversal pressures, retaining their native scope and units."""
import hashlib
import json
from pathlib import Path
import gsw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/canary-pies-native-depth-source-facts-v1.json'
OPERATOR = 'research/canary-pies-pressure-conversion-operator-v1.json'
OUTPUT = 'research/canary-pies-converted-depths-v1.json'
EXPECTED = [
    ('canary-pies-2025-cc-mean-velocity-reversal-pressure', 810, ['C', 'E'], 'all_times_time_mean'),
    ('canary-pies-2025-lp-mean-velocity-reversal-pressure', 480, ['A', 'B'], 'all_times_time_mean'),
    ('canary-pies-2025-lp-southward-only-velocity-reversal-pressure', 690, ['A', 'B'], 'source_southward_component_selection_excluding_recirculation'),
]


def latitude(label):
    degrees, minutes = map(float, label.split())
    if not (0 <= degrees < 90 and 0 <= minutes < 60):
        raise ValueError('Invalid nominal latitude')
    return degrees + minutes / 60


def build(root=ROOT):
    source = json.loads((root/SOURCE).read_bytes())
    operator = json.loads((root/OPERATOR).read_bytes())
    if gsw.__version__ != operator['gsw_version']:
        raise ValueError('Unpinned GSW version')
    if operator['assumed_dynamic_height_m2_s2'] != 0 or operator['assumed_sea_surface_geopotential_m2_s2'] != 0:
        raise ValueError('Unreviewed geopotential correction')
    if operator['latitude_rule'] != 'arithmetic_mean_of_nominal_endpoint_latitudes':
        raise ValueError('Unreviewed section latitude rule')
    if len(source['references']) != 3:
        raise ValueError('Expected three independently scoped source descriptors')
    records = []
    for row, (ref, pressure, endpoints, condition) in zip(source['references'], EXPECTED):
        if (row['id'], row['approximate_value'], row['pies_endpoints'], row['averaging_condition']) != (ref, pressure, endpoints, condition):
            raise ValueError('Changed source pressure, region or averaging condition')
        if row['unit'] != 'dbar' or row['metric'] != 'reported_mean_geostrophic_velocity_sign_reversal_pressure':
            raise ValueError('Invalid native pressure quantity')
        lats = [latitude(source['nominal_sites'][site]['latitude_degrees_minutes_north']) for site in endpoints]
        lat = sum(lats)/2
        depth = -float(gsw.z_from_p(pressure, lat, 0, 0))
        endpoint_depths = sorted(-float(gsw.z_from_p(pressure, p, 0, 0)) for p in lats)
        records.append({
            'id': ref.replace('-pressure', '-converted-depth'), 'native_reference_id': ref,
            'entity_id': row['entity_id'], 'branch_scope': row['branch_scope'],
            'averaging_condition': condition, 'source_pressure_dbar': pressure,
            'pressure_interpretation': 'assumed_oceanographic_sea_pressure_as_used_for_published_vertical_coordinate',
            'atmospheric_pressure_subtracted_dbar': 0,
            'nominal_endpoint_latitudes_degrees_north': [round(p, 9) for p in lats],
            'conversion_latitude_degrees_north': round(lat, 9),
            'computed_depth_m': round(depth, 6), 'display_approximate_depth_m': int(10*round(depth/10)),
            'endpoint_latitude_sensitivity_depths_m': [round(v, 6) for v in endpoint_depths],
            'sensitivity_is_uncertainty_interval': False,
            'metric': 'converted_mean_section_velocity_reversal_depth', 'unit': 'm',
            'vertical_datum': 'local_sea_surface_positive_down',
            'physical_depth_uncertainty_m': None, 'seasonal_depth_range_m': None,
            'physical_thickness_m': None, 'volume_eligible': False,
            'reference_route_projection_eligible': False,
        })
    paths = [SOURCE, OPERATOR, 'analysis/convert_canary_pies_depth_v1.py']
    return {
        'schema': 'osw.canary-pies-converted-depths.v1',
        'status': 'APPROXIMATE_STANDARD_OCEAN_PRESSURE_CONVERSION_NOT_NEW_BOUNDARY_OBSERVATIONS',
        'input_sha256': {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
        'gsw_version': gsw.__version__, 'records': records,
        'computed_precision_is_physical_accuracy': False,
        'new_independent_observations': 0, 'new_seasonal_depth_series': 0,
        'whole_route_depth_profiles': 0, 'volume_estimates': 0,
        'full_goal_complete': False,
    }


if __name__ == '__main__':
    output = ROOT/OUTPUT
    output.write_bytes((json.dumps(build(), indent=2, ensure_ascii=False)+'\n').encode('utf8'))
