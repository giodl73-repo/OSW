"""Prevent section bounds, cruise dates and transport error changing meaning."""
import copy

import pytest
from pyproj import Geod

import check_portugal_orca_section_span as source


def test_coordinate_conversion_and_source_event_are_reproducible():
    row = source.record()
    context = row['published_section_context']
    a, b = context['source_event']['reported_section_endpoints_lon_lat']
    assert row['section_geometry']['coordinates'] == [a, b]
    assert Geod(ellps='WGS84').inv(*b, *a)[2] / 1000 == pytest.approx(115.71427424571638)
    assert row['approximate_width_km'] == 116
    assert context['source_review']['raw_pdf_acquired'] is False
    assert context['source_review']['page_images_reviewed'] is False
    assert context['cruise_context']['is_exact_section_occupation'] is False
    source.validate_inventory({'measurements': [row]})


@pytest.mark.parametrize('change', [
    {'current_id': 'portugal-coastal'},
    {'width_metric': 'whole_current_width'},
    {'approximate_width_km': 144},
    {'observed_period': {'start': '2009-10-15', 'end': '2009-11-11'}},
    {'calendar_months': [10, 11], 'seasonal_playback_eligible': True},
    {'fixed_layer_bounds_m': [0, 1600]},
    {'uncertainty_km': 0.4},
    {'width_range_km': [115, 117], 'is_confidence_interval': True},
    {'width_rank_eligible': True, 'whole_current_representative': True},
    {'annual_extrema_eligible': True},
    {'full_width_inference_eligible': True},
])
def test_unsupported_width_layer_time_or_identity_promotions_reject(change):
    row = source.record()
    row.update(change)
    with pytest.raises(ValueError):
        source.validate_row(row)


@pytest.mark.parametrize('change', [
    {'distance_is_author_reported_km': True},
    {'source_coordinate_datum': 'WGS84'},
    {'transport_uncertainty_is_width_uncertainty': True},
    {'source_coordinate_uncertainty_degrees': 0.05},
    {'flow_normal_width_km': 116},
    {'whole_current_width_km': 116},
    {'source_review': {'raw_pdf_acquired': True, 'page_images_reviewed': True}},
])
def test_context_cannot_claim_unsupported_original_or_physical_support(change):
    row = source.record()
    row['published_section_context'].update(change)
    with pytest.raises(ValueError):
        source.validate_row(row)


def test_missing_duplicate_and_forged_audit_reject():
    for rows in [[], [source.record(), source.record()]]:
        with pytest.raises(ValueError):
            source.validate_inventory({'measurements': rows})
    audit = copy.deepcopy(source.load())
    audit['measurement']['approximate_width_km'] = 144
    with pytest.raises(ValueError):
        source.validate_row(source.record(), audit)
