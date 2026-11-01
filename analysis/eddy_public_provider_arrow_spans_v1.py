"""Source circulation-arrow spans; publication context never supplies observation dates."""
import itertools
from eddy_map_spans_v1 import span_interval

METHOD = 'source_public_cardone_circulation_arrow_spans_v1'


def summarize(report, component):
    assert report['schema'] == 'osw.eddy-cardone-provider-arrow-source-review.v1'
    assert report['status'] == 'PASS_QUALIFIED_PROVIDER_CIRCULATION_ARROW_EXTENT'
    c = report['case']
    assert c['owner_id'] == 'eddy:horizon:loop-78-primary' and c['source_name'] == 'Cardone'
    assert c['observation_date'] is None and c['publication_context_date'] == '2024-05-27'
    assert c['source_date_is_observation_date'] is False
    assert c['source_raster']['width'] == 1988 and c['source_raster']['height'] == 1530
    assert c['source_ink_max_rgb_channel'] == 75
    assert c['axes'] == {'longitude': [[673, -92], [892, -90], [1111, -88]],
                         'latitude': [[334, 28], [554, 26], [774, 24]]}
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
    assert [r['axis_coordinate_pixel'] for r in readings] == [694, 1008, 430, 681]
    for r in readings:
        assert r['selected_ink_pixels'] >= 10 and len(r['selected_ink_pixels_sha256']) == 64
        axis = 0 if r['direction'] in ['west', 'east'] else 1
        assert all(p[axis] == r['axis_coordinate_pixel'] for p in r['extreme_ink_pixels'])
    assert c['outline']['bbox_xyxy'] == [694, 430, 1008, 681]
    assert report['original']['bytes'] == 835456
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
    return {'method': METHOD, 'component': component, 'source_case_name': 'Cardone',
            'range_km': [min(s['range_km'][0] for s in scenarios), max(s['range_km'][1] for s in scenarios)],
            'nominal_audit_span_km': nominal['audit_span_km'],
            'audit_reading_extrema_km': [min(s['audit_reading_interval_km'][0] for s in scenarios),
                                       max(s['audit_reading_interval_km'][1] for s in scenarios)],
            'axis_shift_scenarios': 64, 'reading_allowance_native_pixels': 6,
            'axis_allowance_native_pixels': 2, 'round_outward_km': 25,
            'range_is_reading_only': True, 'physical_uncertainty_quantified': False,
            'observation_date': None, 'publication_context_date': '2024-05-27',
            'publication_date_is_observation_date': False,
            'closed_boundary_inferred': False, 'whole_physical_eddy_extent_inferred': False}
