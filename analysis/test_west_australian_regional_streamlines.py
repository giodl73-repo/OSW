"""Known vector fields, barriers and independently checked polygonal distances."""
import json
import math

import numpy as np
import pytest

from west_australian_regional_streamlines import ROOT, REPORT, Field, GEOD, STEPS, OFFSETS, build, encoded, first_exit, trace


def constant(u=0.,v=.1):
    return Field([60,80,100,116],[-36,-32,-28],np.full((3,4),u),np.full((3,4),v))


@pytest.mark.parametrize('step',STEPS)
def test_uniform_northward_flow_has_known_meridional_length(step):
    field=constant();seed=(90,-32)
    backward,back=trace(field,seed,-1,step);forward,ahead=trace(field,seed,1,step)
    assert backward['status']==forward['status']=='matching_gate_reached'
    assert backward['vertices_lon_lat'][-1]==[90,-36]
    assert forward['vertices_lon_lat'][-1]==[90,-28]
    assert math.isclose(back+ahead,GEOD.inv(90,-36,90,-28)[2]/1000,abs_tol=1e-8)


def test_source_support_and_zero_weight_corners_cannot_be_bridged():
    u=np.ones((3,3));v=np.ones((3,3));u[0,2]=np.nan
    field=Field([0,1,2],[0,1,2],u,v)
    assert field.sample(.5,.5)==(1,1)
    assert field.supported_rectangle((.5,.5),(1.5,1.5)) is False
    u=np.ones((2,2));u[1,1]=np.nan
    assert Field([0,1],[0,1],u,np.ones_like(u)).sample(0,0) is None
    field=constant();field.u[2,1]=np.nan
    row,_=trace(field,(90,-32),1,10)
    assert row['status']=='missing_paired_corner'


def test_side_exit_opposite_gate_stagnation_and_limit_do_not_pass():
    east,_=trace(constant(u=.1,v=0),(115,-32),1,10)
    assert east['status']=='viewport_east_exit'
    south,_=trace(constant(v=-.1),(90,-32),1,10)
    assert south['status']=='viewport_south_exit'
    weak,distance=trace(constant(v=.001),(90,-32),1,10)
    assert weak['status']=='weak_speed_guard' and distance==0
    capped,distance=trace(constant(),(90,-32),1,20,limit_km=10)
    assert capped['status']=='next_step_exceeds_distance_limit' and distance==0
    point,side=first_exit((0,0),(2,2),(-1,1,-1,1))
    assert point==(1,1) and side=='east'


def test_rotational_field_returns_toward_its_seed():
    x=np.linspace(85,95,101);y=np.linspace(-36,-28,81);xx,yy=np.meshgrid(x,y)
    u=-(yy+32)*.1;v=(xx-90)*math.cos(math.radians(32))*.1
    result,_=trace(Field(x,y,u,v),(91,-32),1,5)
    assert result['status']=='seed_return_guard'
    assert 300 < result['traced_distance_km'] < 2000


def test_all_original_cases_and_independent_geometry():
    document=json.loads((ROOT/REPORT).read_bytes())
    assert encoded(build())==(ROOT/REPORT).read_bytes()
    cases=document['cases']
    assert len(cases)==len({r['id'] for r in cases})==117
    assert len(document['anchors'])==13
    for anchor in document['anchors']:
        rows=[r for r in cases if r['field_id']==anchor['field_id']]
        assert {(r['step_km'],r['native_seed_offset']) for r in rows}=={(s,o) for s in STEPS for o in OFFSETS}
        assert sum(r['primary'] for r in rows)==1
    assert document['counts']['status_counts']=={'both_regional_gates_reached':43,'unresolved_regional_gate_pair':74}
    assert {r['month'] for r in cases if r['primary'] and r['status']=='both_regional_gates_reached'}=={1,6,8,9}
    assert all(r['conditional_regional_path_length_km'] is None for r in cases if r['field_id']=='source-period-mean')
    for row in cases:
        both=row['status']=='both_regional_gates_reached'
        assert (row['conditional_regional_path_length_km'] is not None)==both
        if both:
            assert row['backward']['vertices_lon_lat'][-1][1]==-36
            assert row['forward']['vertices_lon_lat'][-1][1]==-28
            assert abs(row['conditional_regional_path_length_km']-sum(row[k]['traced_distance_km'] for k in ['backward','forward'])) <= 1.500001e-6
        for key in ['backward','forward']:
            leg=row[key]
            if leg is None: continue
            vertices=leg['vertices_lon_lat']
            assert all(60<=p[0]<=116 and -36<=p[1]<=-28 for p in vertices)
            assert leg['accepted_segments']==len(vertices)-1
            computed=sum(GEOD.inv(*a,*b)[2]/1000 for a,b in zip(vertices,vertices[1:]))
            # Triangle-inequality bound: <=2 mm per rounded endpoint, plus .5 mm scalar rounding.
            allowance=(len(vertices)-1)*.000004+.000000501
            assert abs(computed-leg['traced_distance_km'])<=allowance
    assert document['physical_current_axis_admitted'] is False
    assert document['length_rank_eligible'] is False and document['whole_current_length_km'] is None


@pytest.mark.parametrize('case',['shape','axis','infinity'])
def test_invalid_fields_rejected(case):
    if case=='shape':args=([0,1],[0,1],np.ones((2,3)),np.ones((2,3)))
    elif case=='axis':args=([0,0],[0,1],np.ones((2,2)),np.ones((2,2)))
    else:args=([0,1],[0,1],np.full((2,2),np.inf),np.ones((2,2)))
    with pytest.raises(ValueError): Field(*args)
