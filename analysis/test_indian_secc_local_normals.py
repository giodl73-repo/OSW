"""Analytical normals and a straight synthetic jet precede actual-field admission."""
import json
import math
import numpy as np
import pytest
from indian_secc_local_normals import (Field,GEOD,normal_point,profile,peak_audit,spans,
                                       section,advance,case,ROOT,SOURCE,REPORT,verify,encoded)


def jet():
    y=np.array([-10.,-7.,-5.,-3.,0.,2.]);x=np.array([70.,75.,80.,85.,90.])
    u=np.tile(np.maximum(.2*(1-abs(y+5)/2),-.1)[:,None],(1,len(x)))
    return Field(x,y,u,np.zeros_like(u))


@pytest.mark.parametrize('angle',[0,35,90,170])
@pytest.mark.parametrize('offset',[-500,500])
def test_transport_keeps_tangent_perpendicular_to_normal(angle,offset):
    origin=(80,-5);point,tangent=normal_point(origin,angle,offset)
    back=GEOD.inv(*point,*origin)[0]
    increasing_normal=back+180 if offset>0 else back
    assert abs(math.cos(math.radians(tangent-increasing_normal)))<1e-12
    assert abs(GEOD.inv(*origin,*point)[2]/1000-abs(offset))<1e-8


def test_eastward_normal_sign_and_center():
    south,tangent=normal_point((80,-5),90,100);north,_=normal_point((80,-5),90,-100)
    assert south[1]<-5<north[1] and abs(south[0]-80)<1e-10 and tangent==90
    assert normal_point((80,-5),90,0)==((80,-5),90)


def test_analytic_half_peak_span_of_straight_jet():
    field=jet();data=profile(field,(80,-5),5);peak=peak_audit(data)
    assert peak['status']=='supported_local_peak' and peak['peak_offset_km']==0
    nominal=spans(field,data,peak)[1]
    expected=GEOD.inv(80,-6,80,-4)[2]/1000
    assert nominal['status']=='paired_sampled_edges'
    assert abs(nominal['span_km']-expected)<.005
    assert nominal['bracket_span_km'][0]<=expected<=nominal['bracket_span_km'][1]
    assert nominal['resolution_review_required'] # finer sampling does not improve this coarse synthetic grid
    assert max(abs(e['evaluated_component_residual_m_s']) for e in nominal['edges'].values())<1e-6


def test_five_stations_follow_straight_jet_without_creating_current_admission():
    field=jet();anchor={'section_id':'indian-secc-80p333e','longitude':80.,'selected_peak_latitude':-5.}
    result=case(field,anchor,0,5,1)
    assert result['all_five_local_axis_checks_pass']
    assert [s['station_arc_parameter_km'] for s in result['stations']]==[-100,-50,0,50,100]
    assert all(s['local_candidate_axis_check'] for s in result['stations'])
    assert len(result['paths'])==4 and all(p['status']=='target_station_reached' for p in result['paths'])


def test_rk4_station_uses_requested_arc_parameter_and_retains_geometry():
    result,end=advance(jet(),(80,-5),1)
    assert result['status']=='target_station_reached' and result['arc_parameter_km']==50
    assert abs(result['geodesic_chord_sum_km']-50)<.001 and end[0]>80 and end[1]==-5
    assert len(result['vertices_lon_lat'])>2


def test_missing_corner_stops_profile_without_zero_or_gap_bridge():
    field=jet();field.v[1,2]=np.nan
    data=profile(field,(80,-5),5)
    positive=[x for x in data['rows'] if x['s']>0]
    assert len(positive)==1 and positive[0]['q'] is None
    assert positive[0]['status']=='missing_paired_corner'
    assert not any(c['status']=='paired_sampled_edges' for c in spans(field,data,peak_audit(data)))


def test_numerical_peak_ties_are_not_arbitrarily_selected():
    rows=[{'s':s,'q':.1,'velocity':(.1,0),'tangent':90} for s in range(-40,41,10)]
    rows[4]['q']=.2;rows[5]['q']=.2-5e-11
    data={'rows':rows};peak=peak_audit(data)
    assert peak['status']=='numerically_tied_peak' and peak['index'] is None
    rows[5]['q']=.2-1e-8
    assert peak_audit(data)['status']=='supported_local_peak'


def test_flat_uniform_field_cannot_pass_axis_check():
    field=Field([70,80,90],[-10,-5,0,2],np.full((4,3),.2),np.zeros((4,3)))
    result=section(field,(80,-5),5,0)
    assert not result['local_candidate_axis_check']
    assert result['peak']['status']=='numerically_tied_peak'
    assert all(c['span_km'] is None for c in result['threshold_cases'])


def test_weak_seed_remains_failed_not_zero_width():
    field=Field([70,80,90],[-10,-5,0,2],np.full((4,3),.001),np.zeros((4,3)))
    anchor={'section_id':'indian-secc-80p333e','longitude':80.,'selected_peak_latitude':-5.}
    result=case(field,anchor,0,5,1)
    assert result['status']=='weak_or_non_eastward_seed' and not result['stations']


@pytest.fixture(scope='module')
def actual():
    d,_=verify()
    assert encoded(d)==(ROOT/REPORT).read_bytes()
    return d,json.loads((ROOT/SOURCE).read_bytes())


def test_actual_attempts_include_failures_and_no_robust_axis_admission(actual):
    d,_=actual
    assert len(d['cases'])==144 and len(d['case_summaries'])==144 and len(d['step_comparisons'])==72
    assert d['counts']['sampled_stations']==120 and d['counts']['central_paired_half_peak_sections']==36
    assert sum(c['all_five_local_axis_checks_pass'] for c in d['cases'])==1
    assert not any(c['both_five_station_checks_pass'] for c in d['step_comparisons'])
    assert d['whole_current_width_km'] is d['whole_current_length_km'] is None
    for key in ['current_association_verified','physical_current_axis_admitted','physical_state_join_eligible',
                'length_rank_eligible','width_rank_eligible','method_sensitivity_is_measurement_uncertainty']:
        assert d[key] is False
    for c in d['cases']:
        if c['all_five_local_axis_checks_pass']:
            assert c['primary_seed'] and len(c['stations'])==5 and all(s['local_candidate_axis_check'] for s in c['stations'])
        if not c['primary_seed']:assert len(c['stations'])<=1 and not c['all_five_local_axis_checks_pass']


def test_actual_interpolated_components_match_independent_source_weights(actual):
    d,source=actual;checked=0
    xs=source['longitude_degrees_east'];order=sorted(range(len(source['latitude_degrees_north'])),key=lambda y:source['latitude_degrees_north'][y])
    ys=[source['latitude_degrees_north'][y] for y in order]
    for c in d['cases']:
        frame=source['months'][c['month']-1]
        for station in c['stations']:
            for row in station['samples'][::11]:
                offset,x,y,u,v,q,yi,xi,status=row
                if status!='ok':assert q is None;continue
                a=(x-xs[xi])/(xs[xi+1]-xs[xi]);b=(y-ys[yi])/(ys[yi+1]-ys[yi])
                def interpolate(key):
                    values=frame[key]
                    low=values[order[yi]][xi]*(1-a)+values[order[yi]][xi+1]*a
                    high=values[order[yi+1]][xi]*(1-a)+values[order[yi+1]][xi+1]*a
                    return low*(1-b)+high*b
                assert abs(u-interpolate('eastward_m_s'))<1e-8
                assert abs(v-interpolate('northward_m_s'))<1e-8
                checked+=1
    assert checked>1000
