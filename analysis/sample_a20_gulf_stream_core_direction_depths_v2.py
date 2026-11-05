"""Locked local100m-direction LADCP sampling, sharing the original40level union."""
import copy,csv,hashlib,io,json,math,os,signal,socket,time
from pathlib import Path
import netCDF4
from sample_a20_gulf_stream_depth_brackets_v1 import finite,clean,number_count,coarse_indices,CUTOFFS
ROOT=Path(__file__).resolve().parents[1]
OP='research/a20-gulf-stream-core-direction-depth-operator-v2.json'
SOURCE='research/a20-gulf-stream-native-depth-brackets-v1.json'


def fixed_frame(profile):
    samples={p['native_index']:p for p in profile['selected_native_samples']}
    original=[samples[i] for i in profile['coarse_native_indices']]
    point=min(original,key=lambda p:(abs(p['depth_m']-100),p['native_index']))
    u,v=point['u_m_s'],point['v_m_s']
    speed=math.hypot(u,v) if u is not None and v is not None else None
    qualified=speed is not None and speed>.05
    return {'reference_native_index':point['native_index'],'reference_depth_m':point['depth_m'],
      'reference_eastward_u_m_s':u,'reference_northward_v_m_s':v,'reference_speed_m_s':speed,
      'qualified':qualified,'east_north_unit_vector':[u/speed,v/speed] if qualified else None,
      'reference_direction_is_independently_validated_current_axis':False}


def sample_aligned(z, inherited, read_point, direction):
    if len(direction)!=2 or not all(finite(v) for v in direction) or not math.isclose(math.hypot(*direction),1.,abs_tol=1e-12):
        raise ValueError('Fixed finite east/north unit vector required')
    initial = coarse_indices(z)
    if len(inherited)>40 or len({p['native_index'] for p in inherited})!=len(inherited):
        raise ValueError('Cumulative inherited40level union required')
    def project(p):
        return None if p['u_m_s'] is None or p['v_m_s'] is None else p['u_m_s']*direction[0]+p['v_m_s']*direction[1]
    cache={}
    for p in inherited:
        i=p['native_index']
        if z[i]!=p['depth_m']:raise ValueError('Exact original depth/index linkage')
        cache[i]={**copy.deepcopy(p),'native_u_m_s':p['u_m_s'],'u_m_s':project(p)}
    def get(i):
        if i not in cache:
            if len(cache) >= 40: raise ValueError('Whole-profile40level cap reached before native slice')
            point = read_point(i)
            if set(point) != {'u_m_s', 'v_m_s', 'uerr_m_s'} or any(v is not None and not finite(v) for v in point.values()):
                raise ValueError('Finite-or-explicit-missing native components required')
            cache[i] = {'native_index': i, 'depth_m': z[i], **point, 'native_u_m_s':point['u_m_s'], 'u_m_s':project(point)}
        return cache[i]
    for i in initial: get(i)
    upper = [i for i in initial if z[i] <= 200 and get(i)['u_m_s'] is not None]
    core = max(upper, key=lambda i: get(i)['u_m_s']) if upper else None
    states = []
    for cutoff in CUTOFFS:
        state = {'threshold_m_s': cutoff, 'sampled_upper200m_core_index': core,
                 'coarse_bracket_indices': None, 'refined_bracket_indices': None,
                 'lower_depth_m': None, 'lower_depth_native_bracket_m': None,
                 'status': 'NO_QUALIFYING_SAMPLED_UPPER200M_CORE',
                 'first_native_downcrossing_below_core_verified': False,
                 'continuous_connection_from_core_verified': False,
                 'skipped_native_levels_may_hide_earlier_reversal': True,
                 'physical_current_bottom_established': False,
                 'physical_thickness_m': None, 'annual_range_m': None,
                 'depth_confidence_interval_m': None, 'volume_eligible': False}
        if core is not None and get(core)['u_m_s'] > cutoff:
            state['status'] = 'RIGHT_CENSORED_ON_SAMPLED_COARSE_PATH'
            left = core
            for right in [i for i in initial if i > core]:
                value = get(right)['u_m_s']
                if value is None:
                    state.update(status='CENSORED_AT_MISSING_COARSE_SAMPLE', last_positive_sample_depth_m=z[left])
                    break
                if value <= cutoff:
                    state.update(status='REFINEMENT_PENDING', coarse_bracket_indices=[left, right],
                                 refined_bracket_indices=[left, right])
                    break
                left = right
            else:
                state['last_positive_sample_depth_m'] = z[left]
        states.append(state)
    # Deterministic ascending-cutoff round robin shares the same40level cache.
    while any(s['status'] == 'REFINEMENT_PENDING' for s in states):
        progressed = False
        for state in states:
            if state['status'] != 'REFINEMENT_PENDING': continue
            left, right = state['refined_bracket_indices']
            if right - left == 1:
                a, b = get(left)['u_m_s'], get(right)['u_m_s']
                if not a > state['threshold_m_s'] >= b: raise ValueError('Opposite-sign finite endpoint invariant')
                depth = z[left] + (state['threshold_m_s'] - a) * (z[right] - z[left]) / (b - a)
                state.update(status='ADJACENT_NATIVE_CROSSING_WITHIN_FIRST_COARSE_DESCENDING_BRACKET',
                             lower_depth_m=depth, lower_depth_native_bracket_m=[z[left], z[right]])
                progressed = True
                continue
            mid = (left + right) // 2
            if mid not in cache and len(cache) == 40:
                state['status'] = 'UNRESOLVED_REFINEMENT_LEVEL_BUDGET'
                continue
            value = get(mid)['u_m_s']; progressed = True
            if value is None:
                state.update(status='CENSORED_AT_MISSING_REFINEMENT_SAMPLE', missing_refinement_native_index=mid)
            elif value > state['threshold_m_s']:
                state['refined_bracket_indices'][0] = mid
            else:
                state['refined_bracket_indices'][1] = mid
        if not progressed: break
    for state in states:
        if state['refined_bracket_indices'] is not None:
            state['remaining_endpoint_depth_bracket_m'] = [z[i] for i in state['refined_bracket_indices']]
        state['local_crossing_is_first_crossing_of_entire_native_profile'] = False
        state['linear_interpolation_used_only_between_adjacent_finite_native_endpoints'] = state['lower_depth_m'] is not None
    return {'coarse_native_indices': initial, 'sampled_upper200m_core_index': core,
            'selected_native_indices': sorted(cache), 'selected_native_levels': len(cache),
            'selected_native_samples': [{**{k:v for k,v in cache[i].items() if k!='native_u_m_s'},'aligned_component_m_s':cache[i]['u_m_s'],'u_m_s':cache[i]['native_u_m_s']} for i in sorted(cache)], 'threshold_cases': states,
            'source_upper200m_core_fully_sampled': False, 'entire_native_velocity_profile_read': False,
            'independent_current_axis_verified': False, 'physical_current_bottom_established': False,
            'seasonal_playback_eligible': False, 'reference_route_projection_eligible': False}


def build():
    op=json.loads((ROOT/OP).read_bytes())
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
    raw=(ROOT/SOURCE).read_bytes()
    if len(raw)>400000:raise ValueError('Bounded retained scalar packet')
    old=json.loads(raw);typed=number_count(old)
    if old['counts']['case_scalar_bound_including_one_actual_test_and_producer']!=8137 or typed>2500:raise ValueError('Original native phase and bounded metadata required')
    metadata_bound=4023+2*typed
    if metadata_bound>10000:raise ValueError('Cumulative original metadata cap cannot reset')
    profiles=[];axis_values=0;new_field_values=0
    for previous in old['profiles']:
        path=ROOT/previous['source_file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=previous['source_sha256']:raise ValueError('Original native custody required')
        frame=fixed_frame(previous)
        if not frame['qualified']:
            result={'status':'NO_QUALIFYING_FIXED_NEAREST100M_DIRECTION','selected_native_samples':copy.deepcopy(previous['selected_native_samples']),
                    'selected_native_indices':copy.deepcopy(previous['selected_native_indices']),
                    'selected_native_levels':previous['selected_native_levels'],'threshold_cases':[
                        {'threshold_m_s':t,'status':'NO_QUALIFYING_FIXED_NEAREST100M_DIRECTION','lower_depth_m':None,
                         'lower_depth_native_bracket_m':None,'first_native_downcrossing_below_core_verified':False,
                         'physical_current_bottom_established':False,'physical_thickness_m':None,'annual_range_m':None,'volume_eligible':False} for t in CUTOFFS]}
        else:
            with netCDF4.Dataset(path) as d:
                if d['z'].getncattr('units')!='Meters' or len(d['z'])>1000:raise ValueError('Original native axis guard')
                for k in ['u','v','uerr']:
                    if d[k].dimensions!=('z',) or d[k].getncattr('units')!='m/s':raise ValueError('Native component units/shapes')
                values=d['z'][:];axis_values+=int(values.size);z=[clean(v) for v in values]
                if coarse_indices(z)!=previous['coarse_native_indices']:raise ValueError('No initial-grid or inherited-node reselection')
                def read(i):
                    nonlocal new_field_values
                    new_field_values+=3
                    return {k+'_m_s':clean(d[k][i]) for k in ['u','v','uerr']}
                result=sample_aligned(z,previous['selected_native_samples'],read,frame['east_north_unit_vector'])
            result['status']='FIXED_NEAREST100M_DIRECTION_LOCAL_NATIVE_CROSSING_DIAGNOSTICS'
        profiles.append({'station':previous['station'],'entity_context':'current:gulf-stream',
            'source_file':previous['source_file'],'source_sha256':previous['source_sha256'],
            'cast_datetime_utc':previous['cast_datetime_utc'],'source_lon_lat':copy.deepcopy(previous['source_lon_lat']),
            'fixed_reference_frame':frame,'inherited_native_level_count':previous['selected_native_levels'],
            'component_metric':'signed_horizontal_component_along_fixed_native_nearest100m_velocity_direction',
            'source_uerr_is_depth_confidence_interval':False,**result})
    if [p['station'] for p in profiles]!=['014','015','016']:raise ValueError('Same3profiles,not3newindependentprofiles')
    cumulative=8137+2*typed+2*(axis_values+new_field_values)
    if cumulative>250000 or sum(p['selected_native_levels'] for p in profiles)>120:raise ValueError('Original cumulative native caps')
    return {'schema':'osw.a20-gulf-stream-core-direction-depths.v2',
        'status':'FIXED_LOCAL100M_DIRECTION_COMPONENT_CROSSINGS_WITH_SHARED_NATIVE_LEVEL_UNION',
        'operator_file':OP,'input_sha256':op['input_sha256'],'source_file':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),
        'profiles':profiles,'counts':{'source_cast_profiles':3,'new_independent_cast_profiles':0,'threshold_contexts':9,
            'qualified_fixed_reference_frames':sum(p['fixed_reference_frame']['qualified'] for p in profiles),
            'cumulative_selected_native_levels':sum(p['selected_native_levels'] for p in profiles),
            'adjacent_local_crossings':sum(c['lower_depth_m'] is not None for p in profiles for c in p['threshold_cases']),
            'new_native_axis_values_one_pass':axis_values,'new_selected_native_field_values_one_pass':new_field_values,
            'typed_source_packet_numbers_per_pass':typed,'case_metadata_touch_bound':metadata_bound,
            'case_scalar_bound_including_prior_phases_one_actual_test_and_producer':cumulative,
            'provider_requests':0,'new_canonical_depth_references':0},
        'prior_case_time_charge_seconds':old['cumulative_case_time_charge_seconds'],
        'original_case_operations_used':3,'original_case_operations_remaining':0,'original_case_response_bytes':425028,
        'source_full_velocity_arrays_read':False,'first_native_crossing_verified':False,'continuous_core_connection_verified':False,
        'frame_is_source_fitted100m_mean_downstream_direction':False,'seasonal_extrema_established':False,
        'whole_route_physical_depth_profile_established':False,'physical_thickness_m':None,'volume_m3':None,
        'runtime_changed':False,'full_goal_complete':False}


def main():
    def stopped(*a):raise SystemExit('Stopped retained native direction producer')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline original casts only'))
    signal.alarm(60);start=float(os.environ['OSW_A20_DIRECTION_PHASE_START'])
    if not 0<=time.monotonic()-start<90:raise ValueError('Shared test/producer clock required')
    folder=ROOT/'a20-gulf-stream-core-direction-depths-v2';folder.mkdir(exist_ok=False)
    report=build();report['new_direction_phase_seconds']=time.monotonic()-start
    report['cumulative_case_time_charge_seconds']=report['prior_case_time_charge_seconds']+report['new_direction_phase_seconds']
    if report['cumulative_case_time_charge_seconds']>180:raise ValueError('Original case time cap')
    from sample_a20_gulf_stream_depth_brackets_v1 import csv_bytes
    raw=(json.dumps(report,indent=2,allow_nan=False)+'\n').encode();table=csv_bytes(report)
    if len(raw)+len(table)>2400000:raise ValueError('Fixed output chunk cap')
    (folder/'depths.json').write_bytes(raw);(folder/'depths.csv').write_bytes(table)
    print(json.dumps(report['counts']))
    for p in report['profiles']:
        print(json.dumps({'station':p['station'],'frame':p['fixed_reference_frame'],'selected_levels':p['selected_native_levels'],
            'thresholds':[{k:c.get(k) for k in ['threshold_m_s','status','lower_depth_m','lower_depth_native_bracket_m']} for c in p['threshold_cases']]}))


if __name__=='__main__':main()
