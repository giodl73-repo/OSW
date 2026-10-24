"""Refine every baseline source-field case; retain numerical failures and comparisons."""
import json
import math
from collections import Counter

import west_australian_regional_streamlines as baseline
from west_australian_regional_streamlines import ROOT, Field, GEOD, readback, digest

PROTOCOL='plans/west-australian-regional-streamline-rk4-protocol-v2.md'
OPERATOR='analysis/west_australian_regional_streamlines_rk4.py'
REPORT='research/west-australian-regional-streamlines-rk4.json'
TOLERANCE_KM=.01
MIN_STEP_KM=.1


class StageFailure(Exception):
    def __init__(self,reason):self.reason=reason


def rate(field,point,direction):
    if field.cell(*point) is None:raise StageFailure('outside_source')
    velocity=field.sample(*point)
    if velocity is None:raise StageFailure('missing_paired_corner')
    if math.hypot(*velocity)<.005:raise StageFailure('weak_stage_speed_guard')
    # Evaluate the angular derivative directly; subtracting an advanced
    # longitude/latitude from the original state would lose small increments.
    phi=math.radians(point[1]);e2=(1/298.257223563)*(2-1/298.257223563)
    denominator=1-e2*math.sin(phi)**2
    prime=6378137/math.sqrt(denominator);meridional=6378137*(1-e2)/denominator**1.5
    speed=math.hypot(*velocity)
    return (math.degrees(direction*1000*velocity[0]/speed/(prime*math.cos(phi))),
            math.degrees(direction*1000*velocity[1]/speed/meridional))


def rk4(field,point,direction,step):
    k1=rate(field,point,direction)
    p2=tuple(point[i]+step*k1[i]/2 for i in range(2));k2=rate(field,p2,direction)
    p3=tuple(point[i]+step*k2[i]/2 for i in range(2));k3=rate(field,p3,direction)
    p4=tuple(point[i]+step*k3[i] for i in range(2));k4=rate(field,p4,direction)
    end=tuple(point[i]+step*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6 for i in range(2))
    rate(field,end,direction)
    points=[point,p2,p3,p4,end]
    low=tuple(min(p[i] for p in points) for i in range(2));high=tuple(max(p[i] for p in points) for i in range(2))
    if not field.supported_rectangle(low,high):raise StageFailure('unsupported_stage_rectangle')
    return end


def trial(field,point,direction,step):
    coarse=rk4(field,point,direction,step)
    middle=rk4(field,point,direction,step/2)
    fine=rk4(field,middle,direction,step/2)
    error=GEOD.inv(*coarse,*fine)[2]/1000/15
    if error>TOLERANCE_KM:raise StageFailure('local_error_guard')
    return middle,fine,error


def nearest_side(point,bounds):
    west,east,south,north=bounds
    candidates=[('west',(west,point[1])),('east',(east,point[1])),('south',(point[0],south)),('north',(point[0],north))]
    return min(((GEOD.inv(*point,*p)[2]/1000,side,p) for side,p in candidates),key=lambda row:row[0])


def trace(field,seed,direction,step_km,limit_km=10000,return_after_km=300):
    point=tuple(seed);vertices=[point];distance=0.;step=float(step_km);rejected=0;accepted_trials=0;max_error=0.;snap=0.
    target='north' if direction==1 else 'south';stop=None;last_velocity=None;exit_side=None;last_rejection=None
    def append(candidate):
        nonlocal point,distance,last_velocity,stop
        if not field.supported_rectangle(point,candidate):stop='unsupported_final_rectangle';return False
        velocity=field.sample(*candidate)
        if velocity is None or math.hypot(*velocity)<.005:stop='weak_or_missing_endpoint';return False
        last_velocity=velocity
        length=GEOD.inv(*point,*candidate)[2]/1000
        if length<1e-10:return True
        if distance+length>limit_km:stop='next_step_exceeds_distance_limit';return False
        vertices.append(candidate);point=candidate;distance+=length;last_velocity=velocity
        if distance>=return_after_km and GEOD.inv(*seed,*point)[2]/1000<=max(20,2*step_km):stop='seed_return_guard';return False
        return True
    for _ in range(300000):
        try:
            middle,end,error=trial(field,point,direction,step)
        except StageFailure as failure:
            rejected+=1;last_rejection=failure.reason
            if step>MIN_STEP_KM+1e-12:step=max(MIN_STEP_KM,step/2);continue
            if failure.reason!='outside_source':stop=failure.reason;break
            low=0.;high=step;best=None
            for _ in range(40):
                length=(low+high)/2
                try:proposal=trial(field,point,direction,length)
                except StageFailure:high=length
                else:low=length;best=proposal
            if best is not None:
                middle,end,error=best
                if not append(middle) or not append(end):break
                accepted_trials+=1;max_error=max(max_error,error)
            gap,side,endpoint=nearest_side(point,field.bounds)
            if gap>.001:stop='boundary_minimum_step_guard';break
            if not append(endpoint):break
            snap=gap;exit_side=side
            stop='matching_gate_reached' if side==target and last_velocity[1]>0 else 'gate_velocity_not_northward' if side==target else 'viewport_'+side+'_exit'
            break
        if not append(middle) or not append(end):break
        accepted_trials+=1;max_error=max(max_error,error)
        if error<TOLERANCE_KM/32:step=min(float(step_km),step*2)
    if stop is None:stop='iteration_limit_guard'
    return {'status':stop,'target_gate':target,'traced_distance_km':readback(distance,6),
            'vertices_lon_lat':[[readback(x,8),readback(y,8)] for x,y in vertices],
            'accepted_segments':len(vertices)-1,'accepted_trials':accepted_trials,'rejected_trials':rejected,
            'last_trial_rejection':last_rejection,'maximum_estimated_local_error_km':readback(max_error,6),
            'final_boundary_snap_km':readback(snap,6),'reached_viewport_side':exit_side,
            'matching_gate_original_northward_positive':bool(last_velocity[1]>0) if stop=='matching_gate_reached' else None,
            'last_accepted_velocity_m_s':None if last_velocity is None else [readback(v,8) for v in last_velocity]},distance


def build():
    original=baseline.build()
    if baseline.encoded(original)!=(ROOT/baseline.REPORT).read_bytes():raise ValueError('Changed retained Euler baseline')
    source=json.loads((ROOT/original['source_monthly_file']).read_bytes())
    longitude=source['longitude_degrees_east'];latitude=source['latitude_degrees_north']
    mean=original['source_period_mean']
    fields={'source-period-mean':Field(longitude,latitude,mean['eastward_m_s'],mean['northward_m_s'])}
    fields.update({f'month-{r["month"]:02d}':Field(longitude,latitude,r['eastward_m_s'],r['northward_m_s']) for r in source['months']})
    cases=[]
    for old in original['cases']:
        row={k:old[k] for k in ['field_id','month','step_km','native_seed_offset','primary','seed_lon_lat']}
        row.update(id='rk4:'+old['id'],euler_case_id=old['id'],backward=None,forward=None,
                   conditional_regional_path_length_km=None,rounded_regional_path_length_km=None)
        if old['forward'] is None:row['status']=old['status']
        else:
            backward,back=trace(fields[row['field_id']],row['seed_lon_lat'],-1,row['step_km'])
            forward,ahead=trace(fields[row['field_id']],row['seed_lon_lat'],1,row['step_km'])
            row.update(backward=backward,forward=forward)
            if backward['status']==forward['status']=='matching_gate_reached':
                length=back+ahead
                row.update(status='both_regional_gates_reached',conditional_regional_path_length_km=readback(length,6),
                           rounded_regional_path_length_km=math.floor(length/10+.5)*10)
            else:row['status']='unresolved_regional_gate_pair'
        row['euler_status']=old['status'];row['euler_conditional_length_km']=old['conditional_regional_path_length_km']
        cases.append(row)
    comparisons=[]
    for anchor in original['anchors']:
        for offset in baseline.OFFSETS:
            rows=[r for r in cases if r['field_id']==anchor['field_id'] and r['native_seed_offset']==offset]
            values=[r['conditional_regional_path_length_km'] for r in rows]
            complete=all(value is not None for value in values)
            comparisons.append({'field_id':anchor['field_id'],'native_seed_offset':offset,
                'all_three_maximum_steps_reach_both_gates':complete,
                'relative_length_spread':readback((max(values)-min(values))/sorted(values)[1],8) if complete else None,
                'cases':[{'id':r['id'],'maximum_step_km':r['step_km'],'status':r['status'],
                          'conditional_length_km':r['conditional_regional_path_length_km']} for r in rows]})
    return {'schema':'osw.west-australian-regional-streamlines-rk4.v2',
        'status':'exploratory_refined_mean_field_paths_not_named_current_axes','method_display_name':'Adaptive RK4',
        'current_id':'west-australian','entity_id':'current:west-australian',
        'input_sha256':{**original['input_sha256'],baseline.REPORT:digest((ROOT/baseline.REPORT).read_bytes()),
                       PROTOCOL:digest((ROOT/PROTOCOL).read_bytes()),OPERATOR:digest((ROOT/OPERATOR).read_bytes())},
        'euler_baseline_file':baseline.REPORT,'source_monthly_file':original['source_monthly_file'],
        'anchors':original['anchors'],'cases':cases,'step_comparisons':comparisons,
        'counts':{'fields':13,'attempts':117,'status_counts':dict(sorted(Counter(c['status'] for c in cases).items())),
                  'primary_resolved_fields':sum(c['primary'] and c['status']=='both_regional_gates_reached' for c in cases),
                  'euler_resolved_pairs':sum(c['euler_status']=='both_regional_gates_reached' for c in cases),
                  'euler_matches_lost_on_refinement':sum(c['euler_status']=='both_regional_gates_reached' and c['status']!='both_regional_gates_reached' for c in cases),
                  'matches_gained_on_refinement':sum(c['euler_status']!='both_regional_gates_reached' and c['status']=='both_regional_gates_reached' for c in cases)},
        'tracing_convention':{**original['tracing_convention'],'method':'classical_RK4_step_doubling',
            'local_error_estimate_tolerance_km':TOLERANCE_KM,'minimum_trial_step_km':MIN_STEP_KM,'maximum_boundary_snap_km':.001,
            'local_error_is_source_uncertainty':False,'local_error_is_global_error_bound':False},
        'derived_readback_precision':original['derived_readback_precision'],'source_bounds':original['source_bounds'],'gates':original['gates'],
        'current_association_verified':False,'physical_current_axis_admitted':False,
        'whole_current_length_km':None,'whole_current_width_km':None,'annual_physical_length_range_km':None,
        'length_rank_eligible':False,'width_rank_eligible':False,'physical_state_join_eligible':False,
        'seed_return_guard_identifies_an_eddy':False,'partial_traced_distance_is_current_length':False,
        'comparison_figure':'figures/west-australian-regional-streamlines-rk4.svg',
        'path_figure':'figures/west-australian-regional-streamline-paths-rk4.svg'}


def encoded(document):return (json.dumps(document,separators=(',',':'),allow_nan=False)+'\n').encode()


if __name__=='__main__':
    document=build();(ROOT/REPORT).write_bytes(encoded(document));print(json.dumps(document['counts']),flush=True)
