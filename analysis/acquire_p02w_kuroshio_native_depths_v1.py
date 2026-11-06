"""One-shot new LADCP case using frozen bounded header and cutoff kernels."""
import copy,csv,hashlib,io,json,math,os,signal,socket,time,urllib.request
from pathlib import Path
import netCDF4
from acquire_a20_gulf_stream_cast_headers_v1 import acquire,NoRedirect,write_json
from inspect_retained_a20_gulf_stream_headers_v2 import inspect
from sample_a20_gulf_stream_depth_brackets_v1 import clean,coarse_indices,CUTOFFS,csv_bytes
from sample_a20_gulf_stream_core_direction_depths_v2 import fixed_frame,sample_aligned

ROOT=Path(__file__).resolve().parents[1]
OP='research/p02w-kuroshio-native-depth-operator-v1.json'
IDS=['00601','00701','00801']


def validate_operator(op):
    if [t['cast_id'] for t in op['targets']]!=IDS or op['thresholds_m_s']!=CUTOFFS:
        raise ValueError('Exact prospective three-cast matrix and cutoffs required')
    expected={'maximum_provider_operations':3,'maximum_response_bytes':600000,'maximum_per_response_bytes':200000,
        'maximum_case_seconds':180,'maximum_metadata_numeric_values':10000,'maximum_native_scalars':250000,
        'maximum_native_bytes':7000000,'maximum_selected_levels_per_cast':40,'maximum_native_profiles':3,
        'maximum_depth_axis_values_per_cast':1000}
    if any(op[k]!=v for k,v in expected.items()):raise ValueError('Whole new-source case caps, never per-file resets')
    for t in op['targets']:
        if t['url']!='https://currents.soest.hawaii.edu/go-ship/ladcp/downloads/2022_P02W/'+t['cast_id']+'.nc':
            raise ValueError('No host/file substitution or guessed retry alternatives')
    if any(op['eligibility'].values()):raise ValueError('Candidate measurement, not canonical physical bottom')


def qualify_header(target,h):
    attrs=h['global_attributes'];variables=h['variables']
    if attrs.get('GEN_Software_orig')!='LDEO LADCP software: Version IX_14':
        raise ValueError('Qualified documented LDEOIX14 semantics required; preserve raw if version differs')
    if attrs.get('GEN_LADCP_station') not in [int(target['cast_id']),int(target['cast_id'][:3])]:
        raise ValueError('Provider label/source station linkage unresolved')
    if not str(attrs.get('datetime','')).startswith('2022-05-05'):
        raise ValueError('Exact provider listed cast date required')
    for name,units in [('z','Meters'),('u','m/s'),('v','m/s'),('uerr','m/s')]:
        v=variables[name]
        if v['dimensions']!=['z'] or len(v['shape'])!=1 or not 2<=v['shape'][0]<=1000 or v['attributes'].get('units')!=units:
            raise ValueError('Bounded same native metre grid and component units required')
    if any(variables[k]['shape']!=variables['z']['shape'] for k in ['u','v','uerr']):
        raise ValueError('Shared native velocity/depth axis required')
    for name,units in [('lat','degrees_north'),('lon','degrees_east')]:
        if variables[name]['shape']!=[] or variables[name]['attributes'].get('units')!=units:raise ValueError('Scalar native geocodes required')


def no_frame_cases():
    return [{'threshold_m_s':t,'status':'NO_QUALIFYING_FIXED_NEAREST100M_DIRECTION','lower_depth_m':None,
        'lower_depth_native_bracket_m':None,'first_native_downcrossing_below_core_verified':False,
        'physical_current_bottom_established':False,'physical_thickness_m':None,'annual_range_m':None,'volume_eligible':False} for t in CUTOFFS]


def main():
    def stopped(*a):raise SystemExit('Stopped one-shot P02W case; retain journal and do not replay')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    start=float(os.environ['OSW_P02W_CASE_PHASE_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer case clock required')
    op=json.loads((ROOT/OP).read_bytes());validate_operator(op)
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen dependency changed:'+p)
    out=ROOT/'p02w-kuroshio-native-depths-v1';out.mkdir(exist_ok=False)
    journal={'schema':'osw.p02w-kuroshio-native-case-journal.v1','operations':[],
        'case_operation_cap':3,'case_response_byte_cap':600000,'case_response_bytes':0,
        'case_time_cap_seconds':180,'case_time_charge_seconds':0,
        'native_scalar_case_cap':250000,'native_byte_case_cap':7000000,'native_array_values_decoded':0,
        'native_scalar_reservations':[],'metadata_numeric_attribute_cap':10000,
        'native_selected_level_counts':{s:0 for s in IDS},'new_canonical_depth_references':0}
    write_json(out/'journal.json',journal)
    def charge_native(kind,count):
        if journal['native_array_values_decoded']+count>250000:raise ValueError('Aggregate native scalar cap before read')
        journal['native_array_values_decoded']+=count
        journal['native_scalar_reservations'].append({'kind':kind,'count':count,'status':'reserved_before_native_slice'})
        write_json(out/'journal.json',journal)
    try:
        opener=urllib.request.build_opener(NoRedirect());paths=[]
        for t in op['targets']:
            if time.monotonic()-start+30>180:raise TimeoutError('Original case time insufficient, no renewed request allowance')
            paths.append(acquire({'station':t['cast_id'],'url':t['url']},out,journal,opener))
        # All three raw native transfers closed and archived before any header/value interpretation.
        signal.alarm(max(1,min(90,int(180-(time.monotonic()-start)))))
        socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Native source acquisition closed; offline only'))
        metadata={'prior_failed_numeric_attribute_values':0,'reconstruction_numeric_attribute_touches':0,'new_numeric_attribute_values_touched':0}
        headers=[]
        for t,p in zip(op['targets'],paths):
            h=inspect(p,metadata)
            headers.append({'cast_id':t['cast_id'],'raw_file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'header':h})
        write_json(out/'headers.json',{'schema':'osw.p02w-kuroshio-native-headers.v1','headers':headers,
            'numeric_metadata_attribute_ledger':metadata,'native_variable_values_read':0})
        for t,row in zip(op['targets'],headers):qualify_header(t,row['header'])
        profiles=[]
        for t,p,row in zip(op['targets'],paths,headers):
            cast=t['cast_id'];seen=set()
            with netCDF4.Dataset(p) as d:
                count=len(d['z']);charge_native(cast+':z_axis',count)
                z=[clean(v) for v in d['z'][:]]
                charge_native(cast+':scalar_geocodes',2);lon,lat=clean(d['lon'][...]),clean(d['lat'][...])
                if lon is None or lat is None or abs(lon-t['provider_listed_lon_lat'][0])>.02 or abs(lat-t['provider_listed_lon_lat'][1])>.02:
                    raise ValueError('Native coordinate conflict with provider rounded display; no relocation')
                def read_point(i):
                    if i in seen:raise ValueError('Do not re-read cached native values')
                    if len(seen)>=40:raise ValueError('Original40level/cast union before read')
                    seen.add(i);journal['native_selected_level_counts'][cast]=len(seen)
                    charge_native(cast+':native_U_V_uerr_index_'+str(i),3)
                    return {k+'_m_s':clean(d[k][i]) for k in ['u','v','uerr']}
                initial=coarse_indices(z)
                inherited=[{'native_index':i,'depth_m':z[i],**read_point(i)} for i in initial]
                frame=fixed_frame({'selected_native_samples':inherited,'coarse_native_indices':initial})
                if frame['qualified']:
                    sample=sample_aligned(z,inherited,read_point,frame['east_north_unit_vector'])
                else:
                    sample={'selected_native_samples':inherited,'selected_native_indices':initial,
                        'selected_native_levels':len(inherited),'coarse_native_indices':initial,'threshold_cases':no_frame_cases(),
                        'physical_current_bottom_established':False,'reference_route_projection_eligible':False}
                if len(seen)!=sample['selected_native_levels']:raise ValueError('Exact unique native sampling cache required')
            profiles.append({'cast_id':cast,'station':cast,'entity_context':'current:kuroshio',
                'current_membership_basis':'regional_western_P02W_Kuroshio_survey_candidate_not_independent_axis_or_core_assignment',
                'source_QC_tier':'processed_provider_data_shipboard_initial_QC_described_final_post_cruise_assessment_unverified',
                'cast_datetime_utc':row['header']['global_attributes']['datetime'],
                'cast_timestamp_role':'provider_nominal_profile_datetime_not_per_depth_instant',
                'source_lon_lat':[lon,lat],'source_native_file':p.name,'source_native_sha256':row['sha256'],
                'native_axis_count':len(z),'native_axis_domain_m':[z[0],z[-1]],
                'fixed_reference_frame':frame,'reference_frame_temporal_support':'processed_cast_specific_not_climatological_or_mathematical_instant',
                'source_uerr_role':'provider_velocity_uncertainty_estimate_not_standard_error_or_depth_CI',
                'independent_current_axis_verified':False,'physical_state_join_eligible':False,
                'seasonal_playback_eligible':False,**sample})
        metadata_count=metadata['new_numeric_attribute_values_touched']
        total=metadata_count+journal['native_array_values_decoded']
        if metadata_count>10000 or total>250000 or journal['case_response_bytes']>600000:
            raise ValueError('All aggregate case limits must hold without resets')
        counts={'native_cast_profiles':3,'cutoff_contexts':9,
            'selected_native_levels':sum(p['selected_native_levels'] for p in profiles),
            'qualified_fixed_reference_frames':sum(p['fixed_reference_frame']['qualified'] for p in profiles),
            'local_adjacent_native_crossings':sum(c['lower_depth_m'] is not None for p in profiles for c in p['threshold_cases']),
            'native_array_scalar_reservations':journal['native_array_values_decoded'],
            'numeric_metadata_attributes':metadata_count,'case_scalar_bound_including_metadata':total,
            'provider_operations_used':len(journal['operations']),'provider_operations_remaining':0,
            'response_bytes':journal['case_response_bytes'],'new_canonical_depth_references':0}
        report={'schema':'osw.p02w-kuroshio-native-depths.v1','status':'THREE_REGIONAL_CANDIDATE_CASTS_WITH_LOCAL_DIRECTION_COMPONENT_DIAGNOSTICS',
            'operator_file':OP,'input_sha256':op['input_sha256'],'counts':counts,'profiles':profiles,
            'first_native_crossing_verified':False,'continuous_core_connection_verified':False,
            'source_final_post_cruise_QC_verified':False,'whole_route_physical_depth_profile_established':False,
            'physical_thickness_m':None,'annual_depth_range_m':None,'volume_m3':None,'runtime_changed':False,'full_goal_complete':False}
        raw=(json.dumps(report,indent=2,allow_nan=False)+'\n').encode();table=csv_bytes(report)
        if len(raw)+len(table)+sum(p.stat().st_size for p in out.iterdir())>2400000:
            raise ValueError('Whole artifact scientific output cap')
        (out/'depths.json').write_bytes(raw);(out/'depths.csv').write_bytes(table)
        journal['producer_status']=report['status'];journal['metadata_numeric_attribute_values']=metadata_count
        journal['case_scalar_bound_including_metadata']=total
        print(json.dumps(counts))
        for p in profiles:
            print(json.dumps({'cast_id':p['cast_id'],'frame':p['fixed_reference_frame'],'selected_levels':p['selected_native_levels'],
                'thresholds':[{k:c.get(k) for k in ['threshold_m_s','status','lower_depth_m','lower_depth_native_bracket_m']} for c in p['threshold_cases']]}))
    finally:
        signal.alarm(0);journal['case_time_charge_seconds']=time.monotonic()-start
        write_json(out/'journal.json',journal)
        if journal['case_time_charge_seconds']>180:raise TimeoutError('Original case time exceeded; no retry')


if __name__=='__main__':main()
