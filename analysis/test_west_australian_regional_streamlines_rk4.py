"""Independent constant-bearing benchmarks and all-case numerical refinement."""
import json
import math

import numpy as np
import pytest

from west_australian_regional_streamlines_rk4 import ROOT, REPORT, Field, GEOD, build, encoded, trace


@pytest.mark.parametrize('step',[5,10,20])
def test_constant_bearing_known_length(step):
    field=Field([60,80,100,116],[-36,-32,-28],np.full((3,4),.05),np.full((3,4),.1))
    backward,a=trace(field,(90,-32),-1,step);forward,b=trace(field,(90,-32),1,step)
    assert backward['status']==forward['status']=='matching_gate_reached'
    expected=GEOD.inv(90,-36,90,-28)[2]/1000/math.cos(math.atan(.5))
    assert abs(a+b-expected)<.001
    assert backward['final_boundary_snap_km']<=.001 and forward['final_boundary_snap_km']<=.001
    assert backward['maximum_estimated_local_error_km']<=.01 and forward['maximum_estimated_local_error_km']<=.01


def test_stage_masks_and_weak_speed_cannot_be_crossed():
    u=np.zeros((3,4));v=np.full_like(u,.1);u[2,1]=np.nan
    field=Field([60,80,100,116],[-36,-32,-28],u,v)
    row,distance=trace(field,(90,-32),1,10)
    assert row['status']=='missing_paired_corner' and distance==0
    field=Field([60,80,100,116],[-36,-32,-28],np.zeros((3,4)),np.full((3,4),.001))
    row,distance=trace(field,(90,-32),1,10)
    assert row['status']=='weak_stage_speed_guard' and distance==0


def test_all_cases_preserve_baseline_and_source_scope():
    document=json.loads((ROOT/REPORT).read_bytes())
    assert encoded(build())==(ROOT/REPORT).read_bytes()
    assert len(document['cases'])==len({r['id'] for r in document['cases']})==117
    assert len(document['step_comparisons'])==39
    original=json.loads((ROOT/document['euler_baseline_file']).read_bytes())
    lookup={r['id']:r for r in original['cases']}
    for row in document['cases']:
        old=lookup[row['euler_case_id']]
        assert all(row[key]==old[key] for key in ['field_id','month','step_km','native_seed_offset','primary','seed_lon_lat'])
        assert row['euler_status']==old['status'] and row['euler_conditional_length_km']==old['conditional_regional_path_length_km']
        resolved=row['status']=='both_regional_gates_reached'
        assert (row['conditional_regional_path_length_km'] is not None)==resolved
        if resolved:
            assert row['backward']['vertices_lon_lat'][-1][1]==-36
            assert row['forward']['vertices_lon_lat'][-1][1]==-28
        for key in ['backward','forward']:
            leg=row[key]
            if leg is None:continue
            assert leg['maximum_estimated_local_error_km']<=.01
            assert leg['final_boundary_snap_km']<=.001
            coordinates=leg['vertices_lon_lat']
            assert all(60<=p[0]<=116 and -36<=p[1]<=-28 for p in coordinates)
            computed=sum(GEOD.inv(*a,*b)[2]/1000 for a,b in zip(coordinates,coordinates[1:]))
            assert abs(computed-leg['traced_distance_km'])<=(len(coordinates)-1)*.000004+.000000501
    assert document['whole_current_length_km'] is None and document['current_association_verified'] is False
    assert document['length_rank_eligible'] is False and document['physical_state_join_eligible'] is False
