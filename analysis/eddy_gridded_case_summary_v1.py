"""Validate small retained contour diagnostics; no ocean fields or geometry loaded."""
import math

METHOD = 'gridded_adt_named_source_case_v1'
METRICS = {
    'area': ('osw_gridded_adt_contour_area', 'area_km2', 'km2', 5000),
    'equivalent_diameter': ('osw_gridded_adt_area_equivalent_diameter', 'area_equivalent_diameter_km', 'km', 25),
    'east_west': ('osw_gridded_adt_east_west_bounding_arc', 'east_west_bounding_arc_km_at_midlatitude', 'km', 25),
    'north_south': ('osw_gridded_adt_north_south_bounding_arc', 'north_south_bounding_arc_km', 'km', 25),
}


def summarize(report, component):
    assert report['schema'] == 'osw.eddy-gridded-named-case-comparison.v1'
    assert report['status'] == 'PASS_QUALIFIED_SOURCE_CASE_REFERENCE'
    case = report['case']
    assert case['owner_id'] == 'eddy:horizon:loop-60-primary' and case['source_name'] == 'Kraken'
    assert case['date'] == '2013-03-31' and case['registry_initial_separation'] == '2013-04-08'
    assert case['source_map_pixels_reviewed'] and case['comparison_pixels_reviewed']
    assert all(case[k] is False for k in ['physical_crosswalk_verified', 'other_kraken_values_inherited', 'physical_footprint_admitted', 'rights_screened_release_eligible'])
    cloud = report['cloud_review']['result']
    assert cloud['status'] == 'PASS_EXPLORATORY_CONTOUR_PILOT_NO_ADMISSION'
    assert cloud['source']['sha256'] == '526fb93bbb0880a4c6ab9390527cef8ecc4706c7c08d0a075ccfd02de922b527'
    day = next(d for d in cloud['days'] if d['date'] == case['date'])
    assert len(day['scenarios']) == 6
    assert {(s['mean_method'], s['level_m']) for s in day['scenarios']} == {(m, v) for m in ['finite_gridpoint_arithmetic', 'cos_latitude_weighted'] for v in [.15, .17, .19]}
    selected = []
    for scenario in day['scenarios']:
        hits = [c for c in scenario['candidates'] if c['review_control_point_hits'][case['control_key']] == [True] * 9]
        assert len(hits) == 1, 'Each scenario needs a unique common control-point match'
        c = hits[0]
        assert c['vertices'] >= 4 and c['area_km2'] > 4000
        assert math.isclose(c['area_equivalent_diameter_km'], 2 * math.sqrt(c['area_km2'] / math.pi), rel_tol=1e-12)
        w, s, e, n = c['bbox_degrees']; assert -99 < w < e < -79 and 17 < s < n < 32
        assert math.isclose(c['north_south_bounding_arc_km'], 6371 * math.radians(n - s), rel_tol=1e-12)
        selected.append(c)
        if scenario['mean_method'] == 'finite_gridpoint_arithmetic' and scenario['level_m'] == .17:
            nominal_candidate = c
    metric, key, unit, increment = METRICS[component]
    values = [c[key] for c in selected]
    assert all(math.isfinite(v) and v > 0 for v in values)
    nominal = nominal_candidate[key]
    return {'metric': metric, 'unit': unit, 'component': component,
            'nominal_audit_value': nominal, 'scenario_values': values,
            'unrounded_extrema': [min(values), max(values)], 'round_outward_to': increment,
            'range_value': [math.floor(min(values) / increment) * increment, math.ceil(max(values) / increment) * increment],
            'scenarios': 6, 'range_is_method_sensitivity_only': True}
