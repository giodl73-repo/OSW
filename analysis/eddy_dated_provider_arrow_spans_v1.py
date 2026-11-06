"""Dated provider-chart arrow spans, not observed physical eddy boundaries."""
import itertools
from eddy_map_spans_v1 import span_interval

METHOD = 'source_public_feldman_dated_circulation_arrow_spans_v1'


def summarize(report, component):
    assert report['schema'] == 'osw.eddy-feldman-dated-provider-arrow-source-review.v1'
    assert report['status'] == 'PASS_QUALIFIED_PROVIDER_CIRCULATION_ARROW_EXTENT'
    c = report['case']
    assert c['owner_id'] == 'eddy:horizon:loop-81-primary' and c['source_name'] == 'Feldman'
    assert c['observation_date'] is None and c['source_map_date'] == '2026-01-06' and c['publication_context_date'] is None
    assert c['source_date_is_observation_date'] is False
    assert c['source_date_is_map_label'] is True and c['source_map_date_is_exact_observation_time'] is False
    assert c['source_trajectory_window_as_reported']=='4 d' and c['trajectory_window_is_exact_arrow_observation_support'] is False
    assert report['source_verification']['source_confidential_marking_visible'] is True and report['source_verification']['source_asset_republished'] is False
    assert c['source_raster']['width'] == 800 and c['source_raster']['height'] == 648
    assert c['source_ink_max_rgb_channel'] == 75
    assert c['axes'] == {'longitude': [[182, -94], [270, -92], [358, -90]],
                         'latitude': [[168, 28], [343, 24], [431, 22]]}
    assert c['axis_sensitivity_pixels'] == 2
    assert c['coordinate_interpolation'] == 'piecewise_linear_displayed_longitude_latitude'
    assert c['source_contour_level'] is None and c['source_contour_unit'] is None
    assert all(c[k] is False for k in [
        'physical_crosswalk_verified', 'physical_footprint_admitted',
        'physical_state_join_eligible', 'rights_screened_release_eligible',
        'closed_eddy_boundary_inferred', 'missing_segments_reconstructed',
        'annual_extrema_inferred', 'principal_width_inferred', 'diameter_inferred',
    ])
    readings = c['extremum_readings']
    assert [r['direction'] for r in readings] == ['west', 'east', 'north', 'south']
    assert [r['axis_coordinate_pixel'] for r in readings] == [210, 333, 230, 343]
    for r in readings:
        assert r['selected_ink_pixels'] >= 10 and len(r['selected_ink_pixels_sha256']) == 64
        axis = 0 if r['direction'] in ['west', 'east'] else 1
        assert all(p[axis] == r['axis_coordinate_pixel'] for p in r['extreme_ink_pixels'])
    assert c['outline']['bbox_xyxy'] == [210, 230, 333, 343]
    assert report['original']['bytes'] == 69949
    assert report['source_verification']['source_bytes_and_sha256_verified'] is True
    assert report['source_verification']['ink_extrema_recomputed'] is True
    assert report['source_verification']['actual_source_pixels_reviewed'] is True
    assert len(report['closed_ink_diagnostics']) == 2
    assert all(r['status'] == 'REJECTED' for r in report['closed_ink_diagnostics'])
    scenarios = []
    for shifts in itertools.product([-2, 2], repeat=6):
        axes = {key: [[p+shifts[i+offset], v] for i, (p, v) in enumerate(c['axes'][key])]
                for key, offset in [('longitude', 0), ('latitude', 3)]}
        scenarios.append(span_interval({**c, 'axes': axes}, component))
    nominal = span_interval(c, component)
    return {'method': METHOD, 'component': component, 'source_case_name': 'Feldman',
            'range_km': [min(s['range_km'][0] for s in scenarios), max(s['range_km'][1] for s in scenarios)],
            'nominal_audit_span_km': nominal['audit_span_km'],
            'audit_reading_extrema_km': [min(s['audit_reading_interval_km'][0] for s in scenarios),
                                       max(s['audit_reading_interval_km'][1] for s in scenarios)],
            'axis_shift_scenarios': 64, 'reading_allowance_native_pixels': 6,
            'axis_allowance_native_pixels': 2, 'round_outward_km': 25,
            'range_is_reading_only': True, 'physical_uncertainty_quantified': False,
            'observation_date': None, 'publication_context_date': None, 'source_map_date': '2026-01-06', 'source_map_date_is_exact_observation_time': False,
            'publication_date_is_observation_date': False,
            'closed_boundary_inferred': False, 'whole_physical_eddy_extent_inferred': False}
