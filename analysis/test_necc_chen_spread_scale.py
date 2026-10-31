"""Keep the published model scale distinct from full widths and extrema."""
import copy,json
import pytest
import build_necc_chen_spread_scale as source


def test_reconstruct_published_states_and_operator_support():
    doc=source.build();assert doc==json.loads((source.ROOT/source.OUTPUT).read_bytes())
    assert [r['approximate_width_km'] for r in doc['measurements']]==[100,130]
    op=doc['operator']
    assert op['source_figure_8_width_axis_unit']=='degrees_latitude'
    assert op['osw_latitude_to_kilometre_conversion_applied'] is False
    assert op['velocity_weight_layer_m']==[0,150]
    assert op['source_latitude_integration_degrees_north']==[0,10]
    assert op['source_zonal_averaging_degrees_east']==[135,155]
    assert op['running_mean_months']==13
    assert 'abs(y-Y)' in op['scale'] and 'q*y' in op['axis']
    assert op['normalization_at_zero_eastward_transport']=='undefined_not_zero'


def test_model_states_are_not_edge_widths_or_exact_dated_extrema():
    rows=source.record_rows();source.validate_inventory({'measurements':rows})
    for row in rows:
        assert row['width_range_km'] is None and row['uncertainty_km'] is None
        assert row['observed_period'] is None and row['calendar_months'] is None
        assert row['section_geometry'] is None
        c=row['model_axis_spread_context'];assert c['model_analysis_period_years']==[1960,2014]
        for field in ['raw_model_fields_acquired','raw_width_series_extracted','exact_state_dates_extracted','author_estimator_reproduced','independent_observed_width_trend_verified','same_as_2013_140w_oscar_component_span','full_width_conversion_applied']:
            assert c[field] is False


@pytest.mark.parametrize('field,value',[
    ('approximate_width_km',200),('width_metric','full_width_at_half_maximum'),
    ('width_range_km',[100,130]),('annual_extrema_eligible',True),
    ('fixed_layer_bounds_m',[0,15]),('source_pointer','/measurements/1'),
    ('observed_period',{'start':'1960-01-01','end':'1960-01-01'}),
    ('current_id','north-equatorial-countercurrent'),
    ('section_geometry',{'type':'LineString','coordinates':[[145,0],[145,10]]}),
])
def test_reject_changed_value_meaning_or_invented_support(field,value):
    rows=source.record_rows();rows[0][field]=value
    with pytest.raises(ValueError,match='axis-distance scale'):source.validate_inventory({'measurements':rows})


@pytest.mark.parametrize('case',['missing','duplicate','speed_weight','standard_deviation','full_width_conversion','raw_model_claim'])
def test_reject_operator_and_coverage_promotions(case):
    rows=source.record_rows()
    if case=='missing':rows.pop()
    elif case=='duplicate':rows.append(copy.deepcopy(rows[0]))
    elif case=='speed_weight':rows[0]['model_axis_spread_context']['operator']['weight_is_vector_speed']=True
    elif case=='standard_deviation':rows[0]['model_axis_spread_context']['operator']['scale_is_rms_or_standard_deviation']=True
    elif case=='full_width_conversion':rows[0]['model_axis_spread_context']['full_width_conversion_applied']=True
    else:rows[0]['model_axis_spread_context']['raw_model_fields_acquired']=True
    with pytest.raises(ValueError,match='axis-distance scale'):source.validate_inventory({'measurements':rows})


def test_reject_changed_original_source_pin(monkeypatch):
    original=source.digest
    monkeypatch.setattr(source,'digest',lambda name:'0'*64 if name.endswith('journal-article.pdf') else original(name))
    with pytest.raises(ValueError,match='Changed reviewed model-scale input'):source.build()
