"""Source-relative PGW core-depth scenarios; no invented geographic axis."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/pgw-relative-core-depth-operator-v1.json'
FACTS = 'research/pgw-pous-2004-core-depth-regimes-source-facts-v1.json'
OWNER = 'current:persian-gulf-saline-overflow'


def finite_number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def depth_at(distance_km, endpoint_shoaling_m, assumed_r14_core_depth_m=None):
    """Evaluate an explicitly linear scenario on the approximate source path."""
    if not finite_number(distance_km) or not 0 <= distance_km <= 300:
        raise ValueError('Distance must lie in source-relative R14-to-R02 domain [0,300]km')
    if not finite_number(endpoint_shoaling_m) or not 0 < endpoint_shoaling_m < 30:
        raise ValueError('Positive endpoint shoaling must remain strictly below30m')
    if assumed_r14_core_depth_m is not None and (
            not finite_number(assumed_r14_core_depth_m) or assumed_r14_core_depth_m <= endpoint_shoaling_m):
        raise ValueError('Explicit positive depth datum must exceed endpoint shoaling')
    fraction = distance_km / 300
    change = -endpoint_shoaling_m * fraction
    return {'source_distance_from_R14_km': distance_km,
            'relative_core_depth_change_m': change,
            'assumed_r14_core_depth_m': assumed_r14_core_depth_m,
            'scenario_core_depth_m': None if assumed_r14_core_depth_m is None else assumed_r14_core_depth_m + change,
            'linear_scenario_depth_change_open_lower_bound_m': -30 * fraction,
            'linear_scenario_depth_change_open_upper_bound_m': 0,
            'bounds_exclusive': fraction != 0,
            'bounds_role': 'linear_family_only_not_observed_pointwise_limits',
            'distance_is_approximate_source_path_coordinate': True}


def build(root=ROOT):
    op = json.loads((root / OPERATOR).read_bytes())
    for path, pin in op['input_sha256'].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != pin:
            raise ValueError('Frozen input changed: ' + path)
    facts = json.loads((root / FACTS).read_bytes())
    review = json.loads((root / op['validated_source_review_file']).read_bytes())
    if (review['source_run'] != 41948713718 or review['tests_passed'] != 25
            or review['input_sha256'][FACTS] != op['input_sha256'][FACTS]):
        raise ValueError('Exact validated primary-source context required')
    context = facts['downstream_profile_context']['R14_to_R02']
    if (facts['entity_id'] != OWNER or context['reported_distance_approximately_km'] != 300
            or context['reported_core_shoaling_exclusive_upper_bound_m'] != 30
            or context['absolute_endpoint_depths_m'] is not None
            or context['bound_is_absolute_depth_or_annual_range'] is not False
            or facts['downstream_profile_context']['R12_excluded_by_authors'] is not True):
        raise ValueError('Original source-relative endpoint constraint and unresolved absolute depths required')
    if op['illustrative_endpoint_shoaling_m'] != [5, 15, 25] or op['illustrative_absolute_datum_m'] != 200:
        raise ValueError('Predeclared illustrative scenarios and optional assumed datum required')
    profiles = []
    for shoaling in op['illustrative_endpoint_shoaling_m']:
        profiles.append({'id': 'pgw-r14-r02-linear-shoaling-' + str(shoaling) + 'm-v1',
                         'endpoint_shoaling_m': shoaling,
                         'statistical_weight': None,
                         'relative_samples': [depth_at(x, shoaling) for x in range(0, 301, 50)],
                         'illustrative_absolute_samples': [depth_at(x, shoaling, op['illustrative_absolute_datum_m']) for x in range(0, 301, 50)]})
    return {'schema': 'osw.pgw-source-relative-core-depth-projection.v1', 'entity_id': OWNER,
            'status': 'SOURCE_CONSTRAINED_LINEAR_REGIONAL_SCENARIO_FAMILY',
            'source_url': facts['source_url'], 'doi': facts['doi'],
            'source_locator': 'Section3.2 paragraph15, R14-to-R02 net depth change; Section2/Table1 campaign context.',
            'source_facts_file': FACTS, 'input_sha256': op['input_sha256'],
            'campaign_window': facts['campaign_window'], 'exact_common_occupation_time': None,
            'coordinate': {'kind': 'source_relative_path_distance', 'origin_section': 'R14',
                           'end_section': 'R02', 'approximate_length_km': 300,
                           'geographic_geometry': None, 'length_uncertainty_km': None},
            'metric': 'salinity_maximum_core_depth_change', 'depth_positive_direction': 'down',
            'source_constraint': {'endpoint_shoaling_m_exclusive_interval': [0, 30],
                                  'absolute_endpoint_depths_m': None,
                                  'constraint_applies_to_net_endpoint_change_only': True},
            'assumptions': [
                'Linear change is an OSW scenario assumption. The source constrains net endpoint change, not monotonicity or intermediate depth excursions.',
                'Seven50km samples represent evaluation spacing of a continuous linear function, not station spacing or measurement resolution.',
                'Endpoint changes5/15/25m are illustrative choices inside the reported limit, not observations, quantiles, likelihoods or best estimates.',
                'The optional200m R14 datum is an explicit illustrative assumption motivated by the regional near200m core description; no measured R14 endpoint depth is available.',
                'The300km coordinate is approximate as reported; no mapped route, exact chainage or length uncertainty is recovered.',
                'Campaign sections were occupied on different dates. This is not an instantaneous, monthly, seasonal or annual profile.',
                'Salinity-core depth is not velocity-core depth, flow top, bottom or thickness. No centered layer, width/thickness join, area or stored volume is inferred.',
            ],
            'scenario_family_range_is_uncertainty': False, 'annual_range_m': None,
            'physical_layer_thickness_m': None, 'volume_m3': None,
            'physical_state_join_eligible': False, 'whole_current_profile': False,
            'old_projection_inventory_modified': False, 'new_primary_measurements': 0,
            'profiles': profiles, 'runtime_changed': False, 'full_goal_complete': False}


def csv_bytes(report):
    rows = [{'scenario_id': p['id'], 'endpoint_shoaling_m': p['endpoint_shoaling_m'],
             'datum_role': role, **row}
            for p in report['profiles']
            for role in ['relative_samples', 'illustrative_absolute_samples'] for row in p[role]]
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue().encode()


if __name__ == '__main__':
    result = build(); out = ROOT / 'pgw-relative-core-depth-v1'; out.mkdir(exist_ok=True)
    raw = (json.dumps(result, indent=2, allow_nan=False) + '\n').encode()
    tabular = csv_bytes(result)
    if len(raw) + len(tabular) > 2400000:
        raise ValueError('Scientific output budget exceeded')
    (out / 'profile.json').write_bytes(raw); (out / 'profile.csv').write_bytes(tabular)
    print(json.dumps({'regional_scenario_families': 1, 'illustrative_scenarios': 3,
                      'new_primary_measurements': 0, 'physical_volumes': 0}))
