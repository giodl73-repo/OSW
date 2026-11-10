"""Offline local depth proxies in the provider's declared native U/V basis."""
import datetime,hashlib,json,math,os,signal,socket,time
from pathlib import Path
import netCDF4
from acquire_a20_gulf_stream_cast_headers_v1 import write_json
from sample_a20_gulf_stream_depth_brackets_v1 import clean,coarse_indices,CUTOFFS,number_count
from sample_a20_gulf_stream_core_direction_depths_v2 import sample_aligned

ROOT=Path(__file__).resolve().parents[1]
OP='research/i06s-native-frame-depth-operator-v2.json'
FOLDER='research/source-data/i06s-agulhas-native-casts-v1'

def native_frame(samples,initial):
    point=min((p for p in samples if p['native_index'] in initial),key=lambda p:(abs(p['depth_m']-100),p['native_index']))
    u,v=point['u_m_s'],point['v_m_s']
    speed=math.hypot(u,v) if u is not None and v is not None else None
    qualified=speed is not None and speed>.05
    return {'reference_native_index':point['native_index'],'reference_depth_m':point['depth_m'],
        'reference_native_u_m_s':u,'reference_native_v_m_s':v,'reference_speed_m_s':speed,
        'qualified':qualified,'native_uv_unit_vector':[u/speed,v/speed] if qualified else None,
        'independent_geographic_direction_or_current_axis_verified':False}

def qualify(station,header):
    a=header['global_attributes'];v=header['variables']
    if a.get('GEN_LADCP_station')!=int(station) or a.get('GEN_Software_orig')!='LDEO LADCP software: Version IX_14beta2':
        raise ValueError('Exact retained source identity/version required, not equivalence to another solver')
    for k,units in [('z','Meters'),('u','m/s'),('v','m/s'),('uerr','m/s')]:
        if v[k]['dimensions']!=['z'] or v[k]['attributes'].get('units')!=units or v[k]['shape']!=v['z']['shape']:
            raise ValueError('Explicit provider metre and m/s common-axis labels required')
    if not 2<=v['z']['shape'][0]<=1000:raise ValueError('Bounded native axis required')
    for k,units in [('lat','Degree North'),('lon','Degree East')]:
        if v[k]['shape']!=[1] or v[k]['attributes'].get('units')!=units:raise ValueError('Retained length-one geocode layout')
    if v['date']['shape']!=[6] or v['date']['attributes'].get('units')!='Y M D H M S':raise ValueError('Retained date layout')

def main():
    def stopped(*a):raise SystemExit('Stopped offline I06S diagnostic, no replay')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    start=float(os.environ['OSW_I06S_NATIVE_PHASE_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic test/producer clock')
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline retained bytes only'))
    op=json.loads((ROOT/OP).read_bytes())
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
    old=json.loads((ROOT/FOLDER/'journal.json').read_bytes())
    headers=json.loads((ROOT/FOLDER/'headers.json').read_bytes())
    if len(old['operations'])!=3 or old['native_array_values_decoded']!=0 or old['case_operation_cap']!=3:
        raise ValueError('Exact original complete custody, no extra source/profile allowance')
    if [r['station'] for r in headers['headers']]!=['046','047','048']:raise ValueError('Three original profiles required')
    metadata=old['metadata_numeric_attribute_values']+number_count(op)+number_count(old)+number_count(headers)
    if metadata>10000:raise ValueError('All prior attributes and repeated typed JSON decodes charged')
    out=ROOT/'i06s-native-frame-depths-v2';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.i06s-native-frame-ledger.v2','prior_case_time_charge_seconds':old['case_time_charge_seconds'],
        'case_time_charge_seconds':old['case_time_charge_seconds'],'case_time_cap_seconds':180,
        'provider_operations_used':3,'provider_operations_remaining':0,'response_bytes':old['case_response_bytes'],
        'numeric_metadata_values_including_reconstruction':metadata,'native_array_values_decoded':0,
        'native_scalar_reservations':[],'native_selected_level_counts':{s:0 for s in ['046','047','048']},
        'new_canonical_depth_references':0}
    write_json(out/'ledger.json',ledger)
    def charge(kind,count):
        if metadata+ledger['native_array_values_decoded']+count>250000:raise ValueError('Original scalar cap before native slice')
        ledger['native_array_values_decoded']+=count
        ledger['native_scalar_reservations'].append({'kind':kind,'count':count,'status':'reserved_before_native_slice'})
        write_json(out/'ledger.json',ledger)
    signal.alarm(max(1,min(60,int(180-old['case_time_charge_seconds']-(time.monotonic()-start)))))
    try:
        profiles=[]
        targets={t['station']:t for t in op['targets']}
        for row in headers['headers']:
            station=row['station'];h=row['header'];qualify(station,h)
            p=ROOT/FOLDER/row['raw_file']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=row['raw_sha256']:raise ValueError('Exact original native file required')
            seen=set()
            with netCDF4.Dataset(p) as d:
                charge(station+':z_axis',len(d['z']));z=[clean(v) for v in d['z'][:]]
                initial=coarse_indices(z)
                charge(station+':lon_lat_date',8)
                lon,lat=clean(d['lon'][0]),clean(d['lat'][0]);date=[int(v) for v in d['date'][:]]
                stamp=datetime.datetime(*date).isoformat()+'Z'
                if date[:3]!=[2019,5,9] or lon is None or lat is None:raise ValueError('Native source date/geocode unresolved')
                if any(abs(a-b)>.02 for a,b in zip([lon,lat],targets[station]['provider_listed_lon_lat'])):
                    raise ValueError('Native geocode differs from rounded primary provider table; no relocation')
                def read_point(i):
                    if i in seen or len(seen)>=40:raise ValueError('Cached unique native40level union required')
                    seen.add(i);ledger['native_selected_level_counts'][station]=len(seen)
                    charge(station+':u_v_uerr_index_'+str(i),3)
                    return {k+'_m_s':clean(d[k][i]) for k in ['u','v','uerr']}
                inherited=[{'native_index':i,'depth_m':z[i],**read_point(i)} for i in initial]
                frame=native_frame(inherited,initial)
                if frame['qualified']:
                    sampled=sample_aligned(z,inherited,read_point,frame['native_uv_unit_vector'])
                else:
                    sampled={'selected_native_samples':inherited,'selected_native_indices':initial,'selected_native_levels':len(inherited),
                        'coarse_native_indices':initial,'threshold_cases':[{'threshold_m_s':t,'status':'NO_QUALIFYING_FIXED_NATIVE_UV_FRAME',
                        'lower_depth_m':None,'lower_depth_native_bracket_m':None,'physical_current_bottom_established':False} for t in CUTOFFS]}
                if sampled['selected_native_levels']!=len(seen):raise ValueError('Unique cache accounting required')
            profiles.append({'station':station,'entity_context':'current:agulhas','source_file':str(Path(FOLDER)/p.name),
                'source_sha256':row['raw_sha256'],'cast_datetime_utc':stamp,'source_lon_lat':[lon,lat],
                'source_timestamp_role':'provider_nominal_profile_date_not_per_depth_instant','native_axis_domain_m':[z[0],z[-1]],
                'native_axis_count':len(z),'native_component_frame':frame,
                'component_metric':'signed_component_along_fixed_nearest100m_vector_in_provider_declared_native_uv_basis',
                'current_membership_basis':'regional_Agulhas_candidate_not_independently_validated_current_axis',
                'source_processing_software':'LDEO LADCP software: Version IX_14beta2',
                'source_processing_warnings':h['global_attributes'].get('warnings'),
                'source_QC_status':'provider_processed_profile_primary_cruise_initial_QC_described_final_QC_not_verified',
                'exact_solver_equivalence_verified':False,'independent_geographic_component_orientation_verified':False,
                'source_uerr_is_SE_or_depth_CI':False,'physical_state_join_eligible':False,'volume_eligible':False,
                'physical_thickness_m':None,'seasonal_range_m':None,**sampled})
        counts={'source_cast_profiles':len(profiles),'cutoff_contexts':sum(len(p['threshold_cases']) for p in profiles),
            'qualified_native_reference_frames':sum(p['native_component_frame']['qualified'] for p in profiles),
            'adjacent_local_crossings':sum(c['lower_depth_m'] is not None for p in profiles for c in p['threshold_cases']),
            'selected_native_levels':sum(p['selected_native_levels'] for p in profiles),
            'case_metadata_numeric_values':metadata,'native_array_values_decoded':ledger['native_array_values_decoded'],
            'case_scalar_bound':metadata+ledger['native_array_values_decoded'],'new_canonical_depth_references':0}
        report={'schema':'osw.i06s-native-frame-depths.v2','status':'CONDITIONAL_PROVIDER_NATIVE_UV_LOCAL_DEPTH_DIAGNOSTICS',
            'operator_file':OP,'input_sha256':op['input_sha256'],'profiles':profiles,'counts':counts,
            'exact_solver_equivalence_verified':False,'source_final_QC_verified':False,'current_axis_verified':False,
            'global_first_crossing_verified':False,'physical_current_bottom_established':False,
            'whole_route_physical_depth_profile_established':False,'volume_m3':None,'runtime_changed':False,'full_goal_complete':False}
        write_json(out/'depths.json',report)
        if sum(p.stat().st_size for p in out.iterdir())>2400000:raise ValueError('Whole scientific output chunk cap')
        print(json.dumps(counts))
        for p in profiles:print(json.dumps({'station':p['station'],'threshold_cases':p['threshold_cases']}))
    finally:
        signal.alarm(0);ledger['case_time_charge_seconds']=old['case_time_charge_seconds']+time.monotonic()-start
        write_json(out/'ledger.json',ledger)
        if ledger['case_time_charge_seconds']>180:raise TimeoutError('Original source case time cannot reset')

if __name__=='__main__':main()
