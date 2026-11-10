"""Known analytic profiles only; no original model arrays or source access."""
from copy import deepcopy
import math

import pytest

import coastal_reference_extent_v1 as extent


def coastal(scale=2,decay_km=40,boundary_peak=False,step=5):
    offsets=list(range(-step if boundary_peak else -2*step,125,step))
    rows=[]
    for s in offsets:
        status='missing_paired_corner' if s< (0 if boundary_peak else -step) else 'ok'
        q=None if status!='ok' else .95 if s<0 else math.exp(-s/decay_km)
        rows.append({'s_km':s,'q_m_s':q,'status':status})
    return {'case_id':'m01:offset0:step5','source':{'fixture':'known_seaward_exponential_decay'},
        'legacy_regional_gate':{'status':'seed_refinement_missing_search_endpoint',
            'all_five_local_axis_checks_pass':False,'all_five_half_peak_spans_resolved':False},
        'frame':extent.FRAME,'coordinate':extent.COORDINATE,
        'normal_sample_step_km':step,
        'q_representation_bound_m_s':0.,'offset_representation_bound_km':0.,
        'rows':rows,'segments':[{'supported':a['status']==b['status']=='ok','native_cell_scale_km':scale}
            for a,b in zip(rows,rows[1:])],
        'peak':{'index':next(i for i,r in enumerate(rows) if r['s_km']==0),
            'unique_verified':True,'local_support_verified':True,'source_fingerprint':'synthetic:exponential',
            'support_kind':'one_sided_boundary_candidate' if boundary_peak else 'interior_unique_candidate'}}


def detached():
    profile=coastal()
    profile['rows']=[{'s_km':s,'q_m_s':math.exp(-(s/40)**2),'status':'ok'} for s in range(-100,105,5)]
    profile['segments']=[{'supported':True,'native_cell_scale_km':2} for _ in profile['rows'][:-1]]
    profile['peak']['index']=20
    return profile


def metric(result,quantity,fraction=.5):
    variant=next(row for row in result['variants'] if row['fraction']==fraction)
    return next(row for row in variant['metrics'] if row['quantity']==quantity)


def assert_contains(bounds,truth):
    assert bounds[0]<=truth<=bounds[1]


def shore(bounds,connected=False):
    return {'kind':'geographic_shoreline','status':'declared_shore_reference',
        'offset_bracket_km':bounds,'source_fingerprint':'synthetic:known_shore',
        'geometry_reviewed':True,'inshore_flow_connectivity_verified':connected}


@pytest.mark.parametrize('fraction',[.4,.5,.6])
def test_known_coastal_decay_has_one_edge_and_a_separate_supported_domain_extent(fraction):
    p=coastal();result=extent.analyse(p)
    expected=-40*math.log(fraction)
    half=metric(result,'core_to_positive_normal_threshold_extent',fraction)
    assert_contains(half['extent_bracket_km'],expected)
    domain=metric(result,'finite_paired_support_to_positive_threshold_extent',fraction)
    assert_contains(domain['extent_bracket_km'],expected+7.5)
    assert domain['source_scale_gate_passed']
    assert metric(result,'local_two_sided_threshold_span',fraction)['extent_bracket_km'] is None
    assert domain['reference']['is_physical_shoreline'] is False
    assert domain['whole_current_width_km'] is None


def test_boundary_candidate_at_known_shore_is_not_silently_doubled():
    p=coastal(boundary_peak=True)
    result=extent.analyse(p,shore([0,0],connected=True))
    known=40*math.log(2)
    answer=metric(result,'shore_reference_to_positive_threshold_extent')
    assert_contains(answer['extent_bracket_km'],known)
    assert answer['extent_bracket_km'][1]<2*known
    assert answer['reference']['model_support_reaches_entire_shore_interval']
    assert result['peak_support_kind']=='one_sided_boundary_candidate'
    assert metric(result,'local_two_sided_threshold_span')['extent_bracket_km'] is None


def test_detached_gaussian_has_known_two_sided_span():
    p=detached();result=extent.analyse(p)
    width=2*40*math.sqrt(math.log(2))
    answer=metric(result,'local_two_sided_threshold_span')
    assert_contains(answer['extent_bracket_km'],width)
    assert answer['source_scale_gate_passed']
    assert metric(result,'finite_paired_support_to_positive_threshold_extent')['extent_bracket_km'] is None


def test_inshore_model_boundary_outside_detached_core_does_not_become_current_edge():
    p=detached();p['rows'][0].update(status='missing_paired_corner',q_m_s=None)
    p['segments'][0]['supported']=False
    result=extent.analyse(p,shore([-100,-95]))
    assert metric(result,'local_two_sided_threshold_span')['extent_bracket_km'] is not None
    for name in ('finite_paired_support_to_positive_threshold_extent','shore_reference_to_positive_threshold_extent'):
        answer=metric(result,name)
        assert answer['extent_bracket_km'] is None
        assert answer['status']=='reference_not_connected_to_sampled_threshold_core'


def test_shore_position_interval_and_model_gap_remain_conditional():
    p=coastal(); result=extent.analyse(p,shore([-15,-10]))
    answer=metric(result,'shore_reference_to_positive_threshold_extent')
    assert_contains(answer['extent_bracket_km'],40*math.log(2)+12.5)
    assert answer['status']=='conditional_shore_to_edge_extent_with_unresolved_inshore_strip'
    assert answer['reference']['inshore_model_gap_bracket_km']==[5,10]
    assert not answer['inshore_connection_verified'] and answer['whole_current_width_km'] is None


def test_long_unknown_inshore_strip_cannot_inflate_native_scale_support():
    p=coastal(scale=10);result=extent.analyse(p,shore([-1000,-1000],connected=True))
    answer=metric(result,'shore_reference_to_positive_threshold_extent')
    assert answer['extent_bracket_km'][0]>1000
    assert answer['supported_path_lower_bound_km']<40
    assert not answer['source_scale_gate_passed']
    assert not answer['reference']['model_support_reaches_entire_shore_interval']
    assert answer['status']=='conditional_shore_to_edge_extent_with_unresolved_inshore_strip'


def test_shore_reference_cannot_choose_a_later_supported_start():
    p=coastal();r=shore([-15,-10]);r['supported_start_index']=p['peak']['index']
    with pytest.raises(ValueError,match='favorable later'):extent.analyse(p,r)


@pytest.mark.parametrize('change',['sample','segment'])
def test_missing_offshore_support_never_gets_bridged(change):
    p=coastal();i=next(i for i,row in enumerate(p['rows']) if row['s_km']==20)
    if change=='sample':p['rows'][i].update(status='missing_paired_corner',q_m_s=0.)
    else:p['segments'][i-1]['supported']=False
    result=extent.analyse(p)
    assert metric(result,'core_to_positive_normal_threshold_extent')['extent_bracket_km'] is None
    assert metric(result,'finite_paired_support_to_positive_threshold_extent')['extent_bracket_km'] is None


def test_source_crop_cannot_supply_a_model_coastal_reference():
    p=coastal();p['rows'][0]['status']='outside_source'
    result=extent.analyse(p)
    answer=metric(result,'finite_paired_support_to_positive_threshold_extent')
    assert answer['status']=='source_crop_is_not_inshore_reference'
    assert answer['extent_bracket_km'] is None
    assert metric(result,'core_to_positive_normal_threshold_extent')['extent_bracket_km'] is not None


def test_profile_limit_before_crossing_remains_unresolved():
    p=coastal();p['rows']=p['rows'][:7];p['segments']=p['segments'][:6]
    answer=metric(extent.analyse(p),'core_to_positive_normal_threshold_extent')
    assert answer['status']=='sample_limit_without_crossing' and answer['extent_bracket_km'] is None


def test_competing_rise_before_crossing_stays_unresolved():
    p=coastal()
    for row in p['rows']:
        if row['s_km']==15:row['q_m_s']=.95
    answer=metric(extent.analyse(p),'core_to_positive_normal_threshold_extent')
    assert answer['status']=='possible_competing_rise_before_crossing'
    assert answer['extent_bracket_km'] is None


def test_first_connected_crossing_does_not_merge_a_later_second_core():
    p=coastal()
    for row in p['rows']:
        if row['s_km']>=70:row['q_m_s']=.9
    answer=metric(extent.analyse(p),'core_to_positive_normal_threshold_extent')
    assert_contains(answer['extent_bracket_km'],40*math.log(2))


def test_stored_precision_ambiguity_expands_the_sampling_bracket():
    p=coastal();p['q_representation_bound_m_s']=.001
    for row in p['rows']:
        if row['status']=='ok' and row['s_km']>=0:row['q_m_s']=max(0,1-.02*row['s_km'])
    p['offset_representation_bound_km']=.1
    edge=extent.crossing(p,.5,1)
    assert_contains(edge['offset_bracket_km'],25)
    assert edge['offset_bracket_km'][0]<25<edge['offset_bracket_km'][1]
    assert edge['ambiguous_sample_indices']


@pytest.mark.parametrize('decay_km',[15,40,70])
@pytest.mark.parametrize('step',[5,10])
def test_quantized_analytic_crossings_are_enclosed_across_scales_and_cadences(decay_km,step):
    p=coastal(decay_km=decay_km,step=step)
    p['q_representation_bound_m_s']=5.000001e-9
    p['offset_representation_bound_km']=5.000001e-7
    for row in p['rows']:
        if row['status']=='ok':row['q_m_s']=round(row['q_m_s'],8)
    result=extent.analyse(p)
    for fraction in extent.FRACTIONS:
        truth=-decay_km*math.log(fraction)
        answer=metric(result,'core_to_positive_normal_threshold_extent',fraction)
        assert_contains(answer['positive_edge']['offset_bracket_km'],truth)
        if answer['extent_bracket_km'] is None:
            # A crossing inside the first sampling interval cannot establish
            # an entirely positive distance bracket under offset guards.
            assert truth<step
            assert answer['status']=='overlapping_or_reversed_boundary_brackets'
        else:assert_contains(answer['extent_bracket_km'],truth)
        assert_contains(metric(result,'finite_paired_support_to_positive_threshold_extent',fraction)['extent_bracket_km'],truth+1.5*step)


@pytest.mark.parametrize('where',['transition','offshore','unknown'])
def test_native_scale_covers_both_brackets_and_supported_path(where):
    p=coastal()
    i=0 if where=='transition' else next(i for i,r in enumerate(p['rows'][:-1]) if r['s_km']==25)
    p['segments'][i]['native_cell_scale_km']=None if where=='unknown' else 50
    answer=metric(extent.analyse(p),'finite_paired_support_to_positive_threshold_extent')
    assert answer['extent_bracket_km'] is not None and not answer['source_scale_gate_passed']
    assert answer['status']=='unknown_native_scale' if where=='unknown' else answer['status']=='insufficient_native_scale_support'


def test_unknown_scale_after_the_crossing_does_not_change_the_local_bracket():
    p=coastal();p['segments'][-1]['native_cell_scale_km']=None
    assert metric(extent.analyse(p),'finite_paired_support_to_positive_threshold_extent')['source_scale_gate_passed']


def test_conditional_shore_coverage_and_unknown_scale_are_both_retained():
    p=coastal();p['segments'][p['peak']['index']]['native_cell_scale_km']=None
    answer=metric(extent.analyse(p,shore([-15,-10])),'shore_reference_to_positive_threshold_extent')
    assert answer['conditional_on_inshore_flow_assumption']
    assert answer['resolution_status']=='unknown_native_scale' and not answer['source_scale_gate_passed']


def test_no_shore_reference_uses_the_same_unresolved_metric_schema():
    result=extent.analyse(coastal())
    assert set(metric(result,'shore_reference_to_positive_threshold_extent'))==set(metric(result,'core_to_positive_normal_threshold_extent'))


def test_rotation_with_unequal_earth_components_preserves_known_scalar_geometry():
    p=coastal(); angle=math.radians(37)
    for row in p['rows']:
        if row['status']!='ok':continue
        q=row['q_m_s'];u=q*math.sin(angle);v=q*math.cos(angle)
        assert not math.isclose(u,v)
        row['q_m_s']=u*math.sin(angle)+v*math.cos(angle)
    assert_contains(metric(extent.analyse(p),'core_to_positive_normal_threshold_extent')['extent_bracket_km'],40*math.log(2))
    p['frame']='meridional_velocity_without_projection'
    with pytest.raises(ValueError,match='frame'):extent.analyse(p)


@pytest.mark.parametrize('origin,bearing', [((40,-9),37),((170,65),25),((-179,70),89)])
def test_curved_wgs84_normal_and_longitude_seam_preserve_extent_bounds(origin,bearing):
    from pyproj import Geod
    geod=Geod(ellps='WGS84');p=coastal()
    def at(s):
        lon,lat,back=geod.fwd(*origin,(bearing+90) if s>=0 else (bearing+270),abs(s)*1000)
        tangent=((back+180) if s>0 else back)-90 if s else bearing
        return (lon,lat),tangent
    for row in p['rows']:
        if row['status']!='ok':continue
        _,tangent=at(row['s_km']);angle=math.radians(tangent)
        q=row['q_m_s'];u=q*math.sin(angle);v=q*math.cos(angle)
        row['q_m_s']=u*math.sin(angle)+v*math.cos(angle)
    coast,_=at(-7.5);edge,_=at(40*math.log(2))
    geodesic_extent=geod.inv(*coast,*edge)[2]/1000
    assert math.isclose(geodesic_extent,7.5+40*math.log(2),rel_tol=0,abs_tol=1e-7)
    answer=metric(extent.analyse(p),'finite_paired_support_to_positive_threshold_extent')
    assert_contains(answer['extent_bracket_km'],geodesic_extent)


def test_all_numeric_brackets_stay_distinct_from_physical_uncertainty_and_admission():
    p=coastal();before=deepcopy(p);result=extent.analyse(p)
    assert p==before and result['legacy_regional_gate']==before['legacy_regional_gate']
    assert not result['current_association_verified'] and not result['width_rank_eligible']
    for variant in result['variants']:
        for row in variant['metrics']:
            assert row['whole_current_width_km'] is row['physical_uncertainty_km'] is None
            assert not row['width_rank_eligible'] and not row['physical_state_join_eligible']
            assert not row['effective_resolution_verified'] and not row['is_confidence_interval']
    result['source']['fixture']='changed output'
    assert p==before
    assert result['physical_annual_minimum_width_km'] is result['physical_annual_maximum_width_km'] is None


@pytest.mark.parametrize('change',['duplicate_offset','nan','missing_segment','missing_scale_declaration',
    'unknown_frame','bad_bound','unsupported_peak_neighbor','missing_peak_provenance','wrong_peak'])
def test_invalid_contract_is_rejected(change):
    p=coastal()
    if change=='duplicate_offset':p['rows'][0]['s_km']=p['rows'][1]['s_km']
    if change=='nan':p['rows'][5]['q_m_s']=float('nan')
    if change=='missing_segment':p['segments'].pop()
    if change=='missing_scale_declaration':p['segments'][0].pop('native_cell_scale_km')
    if change=='unknown_frame':p['coordinate']='longitude_distance_in_degrees'
    if change=='bad_bound':p['q_representation_bound_m_s']=-1
    if change=='unsupported_peak_neighbor':p['segments'][p['peak']['index']]['supported']=False
    if change=='missing_peak_provenance':p['peak']['source_fingerprint']=''
    if change=='wrong_peak':p['rows'][p['peak']['index']+1]['q_m_s']=2
    with pytest.raises(ValueError):extent.analyse(p)


def cases():
    result=[]
    for month in range(1,13):
        for offset in (-1,0,1):
            for step in (5,10):
                p=coastal(step=step);p['case_id']=f'm{month:02d}:offset{offset}:step{step}'
                result.append({'id':p['case_id'],'month':month,'native_latitude_offset':offset,
                    'normal_sample_step_km':step,'source_status':'retained_synthetic_case',
                    'legacy_regional_gate':deepcopy(p['legacy_regional_gate']),'profile':p})
    return result


def test_all_twelve_months_and_unsupported_cases_are_preserved():
    data=cases();data[40]['profile']=None;data[40]['source_status']='synthetic_missing_profile'
    result=extent.analyse_cases(data)
    assert len(result['cases'])==72
    assert result['cases'][40]['status']=='missing_supported_profile'
    assert result['cases'][40]['source_status']=='synthetic_missing_profile'
    assert result['cases'][0]['source_status']==data[0]['source_status']
    assert result['cases'][40]['legacy_regional_gate']==data[40]['legacy_regional_gate']
    assert len(result['cases'][40]['variants'])==3
    assert all(len(v['metrics'])==4 and all(m['status']=='missing_supported_profile' for m in v['metrics'])
        for v in result['cases'][40]['variants'])
    assert result['physical_annual_width_range_km'] is None


@pytest.mark.parametrize('change',['drop','duplicate','wrong_id','legacy_gate_change','sampling_step_change'])
def test_case_identity_and_original_gate_cannot_be_rewritten(change):
    data=cases()
    if change=='drop':data.pop()
    if change=='duplicate':data[-1]=deepcopy(data[0])
    if change=='wrong_id':data[0]['id']='wrong'
    if change=='legacy_gate_change':data[0]['profile']['legacy_regional_gate']['status']='edited'
    if change=='sampling_step_change':data[0]['profile']['normal_sample_step_km']=10
    with pytest.raises(ValueError):extent.analyse_cases(data)
