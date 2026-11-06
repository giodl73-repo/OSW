"""Tiny constructed fields and retained-profile fixtures; no original ocean data."""
from copy import deepcopy
import math

import pytest

import eacc_coastal_reference_extent_adapter_v1 as adapter
from indian_secc_local_normals import profile,peak_audit,packed_peak,packed_row,sample
from west_australian_regional_streamlines import Field,GEOD


SOURCE={'diagnostic_sha256':'d'*64,'monthly_fields_sha256':'f'*64,'fixture':'synthetic_only'}


def source_fixture(angle=0):
    x=[round(39.6+.1*i,8) for i in range(21)]
    y=[round(-9.5+.1*i,8) for i in range(11)]
    theta=math.radians(angle)
    magnitude=[math.exp(-((lon-40)/.4)**2) for lon in x]
    u=[[None if xi==0 else speed*math.sin(theta) for xi,speed in enumerate(magnitude)] for _ in y]
    v=[[None if xi==0 else speed*math.cos(theta) for xi,speed in enumerate(magnitude)] for _ in y]
    field=Field(x,y,u,v)
    cases=[]
    for month in range(1,13):
        for offset in (-1,0,1):
            for step in (5,10):
                origin=(40.,y[5+offset]);data=profile(field,origin,step);peak=peak_audit(data)
                assert peak['usable_for_thresholds'] and peak['status'] in ('missing_search_endpoint','supported_local_peak')
                status=('seed_refinement_missing_search_endpoint' if peak['status']=='missing_search_endpoint'
                    else 'candidate_diagnostic_unresolved' if offset==0 else 'seed_sensitivity_section_only')
                cases.append({'id':f'm{month:02d}:offset{offset}:step{step}','month':month,
                    'native_latitude_offset':offset,'normal_sample_step_km':step,
                    'status':status,'current_association_verified':False,
                    'all_five_local_axis_checks_pass':False,'all_five_half_peak_spans_resolved':False,
                    'seed':{'status':'supported_northward_seed','origin_lon_lat':list(origin)},
                    'initial_refinement':{'peak':packed_peak(peak),'samples':[packed_row(row) for row in data['rows']]}})
    diagnostic={'schema':adapter.SOURCE_SCHEMA,'current_association_verified':False,'cases':cases}
    fields={'schema':adapter.FIELDS_SCHEMA,'source_model_year':2013,'provider_depth_m':15,
        'longitude_degrees_east':x,'latitude_degrees_north':y,
        'months':[{'month':month,'eastward_m_s':deepcopy(u),'northward_m_s':deepcopy(v)} for month in range(1,13)]}
    return diagnostic,fields,field


@pytest.fixture(scope='module')
def fixture():
    return source_fixture()


def test_all72_saved_profiles_adapt_without_reselecting_or_mutating(fixture):
    diagnostic,fields,_=fixture
    before=(deepcopy(diagnostic),deepcopy(fields))
    result=adapter.analyse_saved_case(diagnostic,fields,SOURCE)
    assert (diagnostic,fields)==before and result['case_count']==72
    assert result['new_current_measurements_admitted']==0 and not result['old_producer_rerun']
    for original,calculated in zip(diagnostic['cases'],result['cases']):
        assert calculated['source_status']==original['status']
        assert calculated['legacy_regional_gate']['status']==original['status']
        assert calculated['legacy_regional_gate']['all_five_half_peak_spans_resolved'] is False
        assert calculated['adapter_audit']['frame_and_support_verified']
        assert not calculated['adapter_audit']['anchor_or_peak_reselected']
        assert len(calculated['variants'])==3 and all(len(v['metrics'])==4 for v in calculated['variants'])


def test_retained_q_values_and_quantization_bounds_are_used(fixture):
    diagnostic,_,field=fixture
    original=diagnostic['cases'][0]
    adapted=adapter.adapt_case(original,field,SOURCE)['profile']
    assert [r['q_m_s'] for r in adapted['rows']]==[r[5] for r in original['initial_refinement']['samples']]
    assert adapted['peak']['index']==original['initial_refinement']['peak']['index']
    assert adapted['q_representation_bound_m_s']==adapter.Q_BOUND
    assert adapted['offset_representation_bound_km']==adapter.OFFSET_BOUND_KM


@pytest.mark.parametrize('angle',[-37,37])
def test_unequal_rotated_earth_components_and_geodesic_normals_verify(angle):
    diagnostic,_,field=source_fixture(angle)
    case=diagnostic['cases'][0]
    data,audit=adapter.verify_retained_profile(case,field)
    assert data is not None and audit['frame_and_support_verified']
    assert math.isclose(audit['seed_bearing_degrees_true'],angle%360,abs_tol=1e-10)
    center=next(row for row in case['initial_refinement']['samples'] if row[0]==0)
    assert not math.isclose(center[3],center[4])
    bad=deepcopy(case)
    row=next(row for row in bad['initial_refinement']['samples'] if row[0]==5)
    row[5]=row[4] # V is not projected q when the tangent is rotated.
    with pytest.raises(ValueError,match='projected q'):adapter.verify_retained_profile(bad,field)


def test_native_scale_includes_every_cell_in_both_boundary_footprints():
    x=[39.8,39.9,40.3,40.4];y=[-9.01,-9.,-8.99]
    field=Field(x,y,[[0]*4 for _ in y],[[1]*4 for _ in y])
    geometry=adapter.NativeGeometry(field)
    scale=geometry.segment_scale((39.85,-9.005),(40.35,-8.995))
    expected=GEOD.inv(39.9,-8.99,40.3,-8.99)[2]/1000
    assert math.isclose(scale,expected,rel_tol=0,abs_tol=1e-9)
    assert scale>3*geometry.cell_scale(0,0)
    assert set(geometry.cache)=={(yi,xi) for yi in (0,1) for xi in (0,1,2)}
    assert geometry.segment_scale((39.7,-9),(40,-9)) is None


@pytest.mark.parametrize('change',['coordinate','eastward','northward','q','cell','status','step','peak_index','peak_q','seed'])
def test_mixed_or_corrupted_retained_records_are_rejected(fixture,change):
    diagnostic,_,field=fixture;case=deepcopy(diagnostic['cases'][0])
    row=next(row for row in case['initial_refinement']['samples'] if row[0]==5)
    if change=='coordinate':row[1]+=.001
    if change=='eastward':row[3]+=.001
    if change=='northward':row[4]+=.001
    if change=='q':row[5]+=.001
    if change=='cell':row[7]+=1
    if change=='status':row[-1]='missing_paired_corner';row[3:6]=[None,None,None]
    if change=='step':case['normal_sample_step_km']=10
    if change=='peak_index':case['initial_refinement']['peak']['index']+=1
    if change=='peak_q':case['initial_refinement']['peak']['peak_projected_m_s']+=.001
    if change=='seed':case['seed']['origin_lon_lat'][0]+=.1
    with pytest.raises(ValueError):adapter.verify_retained_profile(case,field)


def test_zero_fill_of_an_original_missing_sample_is_rejected(fixture):
    diagnostic,_,field=fixture;case=deepcopy(diagnostic['cases'][0])
    row=next(row for row in case['initial_refinement']['samples'] if row[-1]!='ok')
    row[3:6]=[0,0,0]
    with pytest.raises(ValueError,match='filled'):adapter.verify_retained_profile(case,field)


def test_profile_cannot_continue_after_first_unsupported_sample(fixture):
    diagnostic,_,field=fixture;case=deepcopy(diagnostic['cases'][0])
    rows=case['initial_refinement']['samples'];first=rows[0]
    origin=tuple(case['seed']['origin_lon_lat']);bearing=0.
    extra=packed_row(sample(field,origin,bearing,first[0]-case['normal_sample_step_km']))
    rows.insert(0,extra)
    with pytest.raises(ValueError,match='continues beyond'):adapter.verify_retained_profile(case,field)


def test_unusable_original_peak_is_retained_as_missing_not_reselected(fixture):
    diagnostic,fields,_=deepcopy(fixture)
    diagnostic['cases'][0]['initial_refinement']['peak']['usable_for_thresholds']=False
    result=adapter.analyse_saved_case(diagnostic,fields,SOURCE)
    assert result['case_count']==72 and result['cases'][0]['status']=='missing_supported_profile'
    assert result['cases'][0]['adapter_audit']['status']=='original_initial_peak_not_usable'
    assert all(m['extent_bracket_km'] is None for v in result['cases'][0]['variants'] for m in v['metrics'])


@pytest.mark.parametrize('change',['month','depth','year','axis','missing_case','duplicate_case','case_id','association'])
def test_source_identity_order_and_original_case_inventory_are_strict(fixture,change):
    diagnostic,fields,_=deepcopy(fixture)
    if change=='month':fields['months'][0]['month']=2
    if change=='depth':fields['provider_depth_m']=20
    if change=='year':fields['source_model_year']=2014
    if change=='axis':fields['latitude_degrees_north'].reverse()
    if change=='missing_case':diagnostic['cases'].pop()
    if change=='duplicate_case':diagnostic['cases'][-1]=deepcopy(diagnostic['cases'][0])
    if change=='case_id':diagnostic['cases'][0]['id']='made-up'
    if change=='association':diagnostic['current_association_verified']=True
    with pytest.raises(ValueError):adapter.adapt_cases(diagnostic,fields,SOURCE)
