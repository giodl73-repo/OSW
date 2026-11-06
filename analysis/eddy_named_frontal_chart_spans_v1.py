"""Qualified named frontal-analysis chart extents from retained manual landmarks."""
from eddy_map_spans_v1 import span_interval

METHOD = 'source_named_nelson_frontal_chart_spans_v1'


def summarize(report, component):
    assert report['schema'] == 'osw.eddy-nelson-frontal-chart-source-review.v1'
    assert report['status'] == 'PASS_QUALIFIED_NAMED_FRONTAL_CHART_EXTENT'
    c = report['case']
    assert c['owner_id'] == 'eddy:horizon:loop-11-primary' and c['source_name'] == 'Nelson'
    assert c['source_week'] == ['1989-08-26', '1989-09-01']
    assert c['source_report_separation_date'] == '1989-09-01'
    assert c['phase'] == 'source_separation_week_frontal_analysis'
    assert c['coordinate_system'] == 'original_embedded_raster_pixels'
    assert c['outline']['bbox_xyxy'] == [389, 183, 634, 477]
    raster = c['native_raster']
    assert (raster['xref'], raster['width'], raster['height']) == (1591, 1092, 898)
    assert c['landmark_definition'] == 'Visible outer Nelson frontal-analysis envelope including the source dashed western segment; inner drifter tracks and separate Loop Current continuation excluded.'
    assert c['source_line_style'] == 'mixed_solid_and_dashed_original_analysis'
    assert all(c[k] is False for k in [
        'closed_boundary_topology_verified', 'missing_segments_reconstructed',
        'whole_physical_eddy_extent_inferred', 'physical_crosswalk_verified',
        'physical_footprint_admitted', 'physical_state_join_eligible',
        'rights_screened_release_eligible', 'annual_extrema_inferred',
        'principal_width_inferred', 'diameter_inferred',
    ])
    assert report['original']['sha256'] == '9138b23ed8e702b7180018203ce2f1d57167046b93a1377a49272d7b037963fe'
    assert report['original']['bytes'] == 54579667 and report['original']['pages'] == 420
    assert all(report['source_verification'][k] is True for k in [
        'original_pdf_bytes_and_sha256_verified', 'native_raster_samples_verified',
        'published_axis_label_boxes_verified', 'source_table_week_verified',
    ])
    x0, y0, x1, y1 = raster['pdf_placement_xyxy']
    for key, ending, axis, scale, offset in [
        ('longitude', 'W', 0, 1092/(x1-x0), x0),
        ('latitude', 'N', 1, 898/(y1-y0), y0),
    ]:
        labels = [v for v in c['axis_label_boxes'] if v['text'].endswith(ending)]
        assert len(labels) == (10 if ending == 'W' else 7)
        expected = sorted([
            [((v['bbox'][axis]+v['bbox'][axis+2])/2-offset)*scale,
             (-1 if ending == 'W' else 1)*int(v['text'][:-2])]
            for v in labels
        ])
        assert c['axes'][key] == expected
    return {'method': METHOD, 'component': component, 'source_case_name': 'Nelson',
            'phase': c['phase'], 'source_week': c['source_week'],
            **span_interval(c, component),
            'reading_allowance_native_pixels': 6, 'round_outward_km': 25,
            'range_is_reading_only': True, 'physical_uncertainty_quantified': False,
            'closed_boundary_inferred': False, 'whole_physical_eddy_extent_inferred': False}
