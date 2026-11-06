import copy
from pathlib import Path
import sys
import pytest
from pypdf import PdfReader

import check_south_atlantic_secondary_band as source


def test_complete_original_and_component_scope():
    audit=source.load();row=source.record();reader=PdfReader(source.ROOT/audit['source_document_file'],strict=True)
    assert len(reader.pages)==14
    assert len(reader.pages[8].extract_text())<20
    source.validate_inventory({'measurements':[row]})
    assert row['approximate_width_km']==200
    assert row['observed_month']=='1983-10' and row['time_precision']=='month'
    assert row['original_regional_context']['total_current_width_km'] is None
    assert row['original_regional_context']['secondary_core_width_km'] is None
    assert not row['whole_current_representative']


@pytest.mark.parametrize('key,value',[
    ('current_id','south-pacific'),('width_metric','whole_current_width'),
    ('approximate_width_km',222),('width_range_km',[100,300]),
    ('observed_month','1990-06'),('observed_period',{'start':'1983-10-01','end':'1983-10-31'}),
    ('time_precision','day'),('calendar_months',[10]),('fixed_layer_bounds_m',[0,1000]),
    ('uncertainty_km',8.3),('whole_current_representative',True),('full_width_inference_eligible',True),
    ('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('width_rank_eligible',True),
    ('section_geometry',{'type':'LineString','coordinates':[[1,-37],[1,-40]]}),
])
def test_unsupported_current_width_and_time_inferences_reject(key,value):
    row=source.record();row[key]=value
    with pytest.raises(ValueError):source.validate_row(row)


@pytest.mark.parametrize('kind',['reference','total','core','bracket','offset','layer','transport'])
def test_contextual_numbers_cannot_become_dimension_definitions(kind):
    row=source.record();context=row['original_regional_context']
    if kind=='reference':context['relative_geostrophic_reference']['value_kg_m3']=36.75
    if kind=='total':context['total_current_width_km']=200
    if kind=='core':context['secondary_core_width_km']=200
    if kind=='bracket':context['front_or_core_bracket_is_width_edges']=True
    if kind=='offset':context['core_offset_is_width']=True
    if kind=='layer':context['field_plot_context_is_uniform_width_layer']=True
    if kind=='transport':context['transport_context']['width_derived_from_transport']=True
    with pytest.raises(ValueError):source.validate_row(row)


def test_deleted_duplicated_or_forged_source_rejects():
    for rows in [[],[source.record(),source.record()]]:
        with pytest.raises(ValueError):source.validate_inventory({'measurements':rows})
    audit=copy.deepcopy(source.load());audit['measurement']['approximate_width_km']=222
    with pytest.raises(ValueError):source.validate_row(source.record(),audit)


def test_independent_statement_graphic_keeps_whole_width_unknown():
    svg=source.figure()
    for text in ['200 km','October 1983','southern component band','3470-3560','whole-current width unknown','curves and edge positions not digitized']:
        assert text in svg,text
    for shape in ['<polyline','<polygon','<circle','<path','<line']:
        assert shape not in svg
