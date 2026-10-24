import json
import numpy as np
import pytest
import build_redsox_lower_nc_section as section


def test_layer_integral_preserves_actual_vertical_coordinates_and_units():
    rows=[[h,1000-h,.01*h,-.02*h] for h in range(80,-1,-10)]
    actual=section.velocity_layer(rows,[20,60])
    assert actual['u_m_s']==pytest.approx(.4)
    assert actual['southward_m_s']==pytest.approx(.8)
    assert actual['source_depth_at_knots_m']==pytest.approx([980,970,960,950,940])
    assert actual['original_samples_in_layer']==5


def test_missing_support_is_not_filled_or_extrapolated():
    with pytest.raises(ValueError,match='outside observed'):
        section.velocity_layer([[h,1000-h,1,-1] for h in range(100,19,-10)],[10,50])
    with pytest.raises(ValueError,match='Missing sample'):
        section.interpolate_complete([0,10,20,30],[1,np.nan,2,3],[5,25])
    with pytest.raises(ValueError,match='maximum'):
        section.interpolate_complete([0,25,40],[1,2,3],[5,30],max_gap=20)


def profiles(values):
    return [{'id':str(i),'position_lon_lat':[44+i/100,12],
        'primary_available':v is not None,
        'layer':{'southward_m_s':v,'u_m_s':0,'v_m_s':-v,'speed_of_mean_vector_m_s':abs(v)} if v is not None else None,
        'hydrography':{'layer_mean_salinity_psu':39}} for i,v in enumerate(values)]


def test_missing_beyond_crossings_preserves_strict_result_and_separate_local_followup():
    source=profiles([None,0,.6,0,None])
    assert section.section_span(source,.5)['span_km'] is None
    result=section.section_span(source,.5,local_supported=True)
    assert result['span_km']==pytest.approx(section.GEOD.inv(44.015,12,44.025,12)[2]/1000)
    assert result['global_peak_search_complete'] is False
    assert result['unavailable_profile_ids']==['0','4']
    assert {result['left_edge']['inner_profile_id'],result['left_edge']['outer_profile_id'],result['right_edge']['inner_profile_id'],result['right_edge']['outer_profile_id']}=={'1','2','3'}


def test_missing_before_crossing_and_open_edges_remain_unknown():
    assert section.section_span(profiles([0,None,.6,0,0]),.5,local_supported=True)['span_km'] is None
    assert section.section_span(profiles([.6,.4,.3]),.5)['span_km'] is None
    assert section.section_span(profiles([0,.1,0]),.5)['status']=='peak_below_predeclared_component_floor'


def test_equal_peaks_select_western_core_without_bridging_valley():
    result=section.section_span(profiles([0,.6,.2,.6,0]),.5)
    assert result['peak_profile_id']=='1'
    assert result['right_edge']['outer_profile_id']=='2'


def test_pressure_conversion_matches_official_teos10_example_not_pressure_as_metres():
    depth=-section.gsw.z_from_p(600,4)
    assert depth==pytest.approx(595.8253480356214,abs=1e-8)
    assert depth!=pytest.approx(600,abs=1)


@pytest.fixture(scope='module')
def calculated():return section.build()


def test_frozen_originals_reproduce_saved_diagnostic_with_numerical_tolerance(calculated):
    saved=json.loads(section.RESULT.read_bytes())
    def same(a,b):
        assert type(a) is type(b)
        if isinstance(a,dict):
            assert a.keys()==b.keys()
            for key in a:same(a[key],b[key])
        elif isinstance(a,list):
            assert len(a)==len(b)
            for x,y in zip(a,b):same(x,y)
        elif isinstance(a,float):assert a==pytest.approx(b,rel=1e-10,abs=1e-11)
        else:assert a==b
    same(calculated,saved)
    assert not calculated['new_width_record_admitted'] and not calculated['current_association_verified']
    assert not calculated['fully_blinded_before_any_selected_velocity_exposure']
    assert calculated['annual_width_range_km'] is None


def test_layer_choice_quality_and_threshold_nulls_are_preserved(calculated):
    cases={(c['campaign'],tuple(c['height_layer_m'])):c for c in calculated['cases']}
    primary=cases['RSX1',(20,60)]
    assert primary['primary']['span_km'] is None
    assert primary['supported_local_core_diagnostics'][0]['span_km'] is None
    assert primary['conditional_diagnostics'][0]['span_km']==pytest.approx(7.325376291189)
    layer=cases['RSX1',(40,80)];actual=layer['supported_local_core_diagnostics'][0]
    assert actual['span_km']==pytest.approx(6.034865010454052)
    assert actual['peak_saline_speed_screen'] and actual['fewer_than4_spacings']
    ids={actual[side][which] for side in ['left_edge','right_edge'] for which in ['inner_profile_id','outer_profile_id']}
    assert ids=={'rsx1-007-hr','rsx1-008-hr','rsx1-009-hr'}
    assert layer['supported_local_core_diagnostics'][3]['fraction']==.4
    assert layer['supported_local_core_diagnostics'][3]['span_km'] is None
    assert layer['supported_local_core_diagnostics'][6]['span_km']==pytest.approx(4.827892369228013)
    for key in [('RSX1',(10,50)),('RSX2',(20,60)),('RSX2',(10,50)),('RSX2',(40,80))]:
        assert all(d['span_km'] is None for d in cases[key]['supported_local_core_diagnostics'])


def test_summer_source_height_failure_is_not_relabelled_zero_flow(calculated):
    case=next(c for c in calculated['cases'] if c['campaign']=='RSX2' and c['height_layer_m']==[20,60])
    cast=next(p for p in case['profiles'] if p['id']=='rsx2-034-hr')
    assert cast['layer'] is None and cast['primary_available'] is False
    assert cast['source_height_range_m'][0]>80 and not cast['source_height_axis_monotonic']
