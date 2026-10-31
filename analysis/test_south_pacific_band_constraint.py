"""Source pin and assumption guards for the prepared South Pacific record."""
import copy
import json

import pytest
from pypdf import PdfReader

import check_south_pacific_band_constraint as source


def test_complete_original_source_and_monthly_constraint():
    audit = source.load()
    paper = source.ROOT/audit['source_document_file']
    reader = PdfReader(paper, strict=True)
    assert len(reader.pages) == 15
    assert len(reader.pages[5].get_text() if hasattr(reader.pages[5],'get_text') else reader.pages[5].extract_text()) < 20
    row = source.record()
    assert row['observed_month'] == '1990-03' and row['time_precision'] == 'month'
    assert row['observed_period'] is None
    assert row['approximate_width_km'] is None and row['width_range_km'] is None
    assert row['reported_width_constraint']['operator'] == 'lt'
    assert row['reported_width_constraint']['reference_scale_km'] == 200
    assert row['original_regional_context']['relative_geostrophic_reference']['value_kg_m3'] == 36.75


@pytest.mark.parametrize('key,value', [
    ('approximate_width_km',200),('approximate_width_km',100),
    ('width_range_km',[0,200]),('width_range_km',[100,200]),
    ('current_id','antarctic-circumpolar'),('current_id','south-atlantic'),
    ('observed_month','1995-01'),('observed_month','1990-03-01'),
    ('observed_period',{'start':'1990-03-01','end':'1990-03-31'}),
    ('fixed_layer_bounds_m',[0,1000]),('calendar_months',[3]),
    ('uncertainty_km',10),('annual_width_range_km',[100,200]),
    ('seasonal_playback_eligible',True),('width_rank_eligible',True),
    ('whole_current_representative',True),
])
def test_scope_or_numeric_promotion_rejects(key,value):
    row = source.record();row[key] = value
    with pytest.raises(ValueError):source.validate_row(row)


@pytest.mark.parametrize('kind', ['qualifier','reference','cutoff','front_edges','illustrative_width'])
def test_coherent_nested_assumption_changes_reject(kind):
    row = source.record()
    if kind == 'qualifier': row['reported_width_constraint']['operator']='lte'
    elif kind == 'reference': row['original_regional_context']['relative_geostrophic_reference']['value_kg_m3']=45.82
    elif kind == 'cutoff': row['original_regional_context']['source_velocity_context']['velocities_are_width_cutoffs']=True
    elif kind == 'front_edges': row['original_regional_context']['front_bracket_is_width_edges']=True
    elif kind == 'illustrative_width': row['original_regional_context']['illustrative_transport_width_is_observation']=True
    with pytest.raises(ValueError):source.validate_row(row)


def test_deleted_duplicate_and_rebound_audit_reject():
    good={'measurements':[source.record()]};source.validate_inventory(good)
    for rows in [[],[source.record(),source.record()]]:
        with pytest.raises(ValueError):source.validate_inventory({'measurements':rows})
    changed=copy.deepcopy(source.load());changed['measurement']['reported_width_constraint']['reference_scale_km']=100
    with pytest.raises(ValueError):source.validate_row(source.record(),changed)


def test_graphic_is_independent_and_has_qualifier_without_width_bar():
    svg=source.figure()
    for text in ['&lt;200 km','March 1990','sigma2 = 36.75','1800-1840','Upper 1,000 m','&gt;500 km','not digitized']:
        assert text in svg,text
    assert '<polyline' not in svg and '<polygon' not in svg
