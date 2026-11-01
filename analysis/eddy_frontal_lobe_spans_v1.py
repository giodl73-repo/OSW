"""Small retained source-chart landmark spans; no reconstructed eddy boundary."""
from eddy_map_spans_v1 import span_interval

METHOD = 'source_hot_core_pre_detachment_frontal_lobe_spans_v1'


def summarize(report, component):
    assert report['schema'] == 'osw.eddy-hot-core-frontal-source-review.v1'
    assert report['status'] == 'PASS_QUALIFIED_PRE_DETACHMENT_LOBE_LANDMARK_REFERENCE'
    c = report['case']
    assert c['owner_id'] == 'eddy:horizon:loop-05-primary' and c['source_name'] == 'Hot Core'
    assert c['source_week'] == ['1986-01-10', '1986-01-17']
    assert c['source_report_separation_date'] == '1986-01-18'
    assert c['phase'] == 'source_chart_pre_detachment_frontal_lobe'
    assert c['native_raster']['width'] == 1098 and c['native_raster']['height'] == 906
    assert c['native_raster']['xref'] == 1544
    assert c['outline']['bbox_xyxy'] == [471, 211, 668, 491]
    assert c['coordinate_system'] == 'original_embedded_raster_pixels'
    assert c['landmark_definition'] == {
        'west': 'westernmost depicted Hot Core lobe front',
        'east': 'eastern lobe neck at the Loop Current junction; continuation excluded',
        'north': 'northernmost depicted Hot Core lobe front',
        'south': 'southernmost depicted Hot Core lobe front',
    }
    assert all(c[k] is False for k in [
        'closed_eddy_boundary_verified', 'missing_segments_reconstructed',
        'whole_eddy_extent_inferred', 'physical_crosswalk_verified',
        'physical_footprint_admitted', 'physical_state_join_eligible',
        'rights_screened_release_eligible', 'annual_extrema_inferred',
        'principal_width_inferred', 'diameter_inferred',
    ])
    assert report['original']['sha256'] == '9138b23ed8e702b7180018203ce2f1d57167046b93a1377a49272d7b037963fe'
    assert report['original']['bytes'] == 54579667 and report['original']['pages'] == 420
    assert report['source_verification']['original_pdf_bytes_and_sha256_verified'] is True
    assert report['source_verification']['native_raster_samples_verified'] is True
    assert report['source_verification']['published_axis_label_boxes_verified'] is True
    # Published tick-label centers are transformed through the actual image placement.
    x0, y0, x1, y1 = c['native_raster']['pdf_placement_xyxy']
    for key, ending, axis, scale, offset in [
        ('longitude', 'W', 0, 1098 / (x1-x0), x0),
        ('latitude', 'N', 1, 906 / (y1-y0), y0),
    ]:
        labels = [v for v in c['axis_label_boxes'] if v['text'].endswith(ending)]
        expected = sorted([
            [((v['bbox'][axis]+v['bbox'][axis+2])/2-offset)*scale,
             (-1 if ending == 'W' else 1)*int(v['text'][:-2])]
            for v in labels
        ])
        assert c['axes'][key] == expected
    result = span_interval(c, component)
    return {'method': METHOD, 'component': component,
            'source_case_name': 'Hot Core', 'phase': c['phase'],
            'source_week': c['source_week'], **result,
            'reading_allowance_native_pixels': 6, 'round_outward_km': 25,
            'range_is_reading_only': True, 'physical_uncertainty_quantified': False,
            'closed_boundary_inferred': False, 'whole_eddy_extent_inferred': False}
