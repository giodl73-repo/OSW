"""Selective classic-NetCDF extraction from retained ACT bytes; no provider replay."""
import csv,ftplib,hashlib,io,json,math,signal,socket,time,urllib.request
from pathlib import Path
import collect_act2011_observed_pair_v1 as frozen
ROOT=Path(__file__).resolve().parents[1]
OP='research/act2011-retained-pair-operator-v2.json'
DATA='research/source-data/act2011-observed-pair-v1'


def no_network(*a,**k):raise RuntimeError('Retained ACT decoder forbids every provider connection')


def layout(ds):
    import numpy as np
    if ds.data_model not in ['NETCDF3_CLASSIC','NETCDF3_64BIT_OFFSET','NETCDF3_64BIT_DATA']:raise ValueError('Only uncompressed classic NetCDF scalar selection is eligible for this bounded read plan')
    t=frozen.choose(ds,'time');u=frozen.choose(ds,'u');v=frozen.choose(ds,'v');z=frozen.choose(ds,'depth')
    lat=frozen.choose(ds,'latitude');lon=frozen.choose(ds,'longitude')
    if t.ndim!=1 or not 1<=t.size<=50000 or lat.size!=1 or lon.size!=1:raise ValueError('Scoped50000time-axis and scalar provider-coordinate bounds required')
    td=t.dimensions[0];calendar=str(getattr(t,'calendar','standard')).lower()
    if calendar not in ['standard','gregorian','proleptic_gregorian']:raise ValueError('NativeGregoriancalendar required')
    for var in [t,u,v,z,lat,lon]:
        if np.dtype(var.dtype).kind not in 'iuf' or any(d!=td and len(ds.dimensions[d])!=1 for d in var.dimensions):raise ValueError('Primitive singleton-point variables only')
    depth_cf=str(getattr(z,'units','')).lower() in ['m','meter','meters','metre','metres'] and str(getattr(z,'positive','')).lower()=='down' and str(getattr(z,'standard_name',''))=='depth' and str(getattr(z,'axis','Z')).upper()=='Z'
    if not depth_cf:raise ValueError('Consistent native CF metre/depth/positiveDown coordinate required')
    frame='eastward' in str(getattr(u,'long_name','')).lower() and 'northward' in str(getattr(v,'long_name','')).lower()
    return {'time':t,'u':u,'v':v,'depth':z,'latitude':lat,'longitude':lon,'time_dim':td,'calendar':calendar,
      'u_factor':frozen.factor(getattr(u,'units','')),'v_factor':frozen.factor(getattr(v,'units','')),
      'provider_depth_reference_supported':False,'CF_depth_coordinate_supported':True,
      'provider_east_north_frame_supported':bool(frame),'ancillary_QC_mapping_pending':bool(getattr(u,'ancillary_variables','') or getattr(v,'ancillary_variables',''))}


def independent_pair(depth,south,q):
    if len(depth)!=2 or any(v is None for v in depth+south):return None
    a,b=sorted(zip(depth,south));z0,u0=a;z1,u1=b
    if z0<0 or z1<=z0 or z1-z0>500 or u0<=q or u1>q:return None
    return z0+(q-u0)*(z1-z0)/(u1-u0)


def eq(actual,expected):
    if (actual is None)!=(expected is None) or actual is not None and not math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-9):raise ValueError('Independent native record/scenario verification mismatch')


def independent_record(ds,m,row):
    import netCDF4,numpy as np
    if row['time_index'] is None:return
    i=row['time_index'];td=m['time_dim']
    actual=float(m['time'][i]);date=netCDF4.num2date(actual,m['time'].units,calendar=m['calendar'])
    if date.isoformat()+'Z'!=row['source_time_label_utc']:raise ValueError('Original native label/index mismatch')
    for role,key in [('u','eastward_m_s'),('v','northward_m_s'),('depth','depth_m')]:
        var=m[role];index=tuple(i if d==td else 0 for d in var.dimensions);value=var[index] if var.dimensions else var[...]
        value=None if np.ma.is_masked(value) else float(value)
        if value is not None and not math.isfinite(value):value=None
        if role in ['u','v'] and value is not None:value*=.01 if str(var.units).strip().lower().startswith('cm') else 1.
        eq(row[key],value)
    for role,k in [('longitude',0),('latitude',1)]:
        var=m[role];value=float(var[tuple(0 for d in var.dimensions)] if var.dimensions else var[...])
        if row['source_coordinate'] is None:raise ValueError('Both finite provider scalar coordinates required')
        eq(row['source_coordinate'][k],value)


def extract(raws):
    if len(raws)!=2:raise ValueError('Exactly retained two-instrument cohort required')
    import netCDF4
    datasets=[]
    try:
        for raw in raws:datasets.append(netCDF4.Dataset('retained',memory=raw))
        headers=[frozen.header(ds) for ds in datasets];metas=[layout(ds) for ds in datasets]
        # One full TIME axis/file plus conservatively two reads of six selected scalar roles/date/file.
        time_values=sum(m['time'].size for m in metas);bound=time_values+len(raws)*len(frozen.DATES)*6*2
        if bound>110000 or bound+2000>238000 or (bound+2000)*8>7000000:raise ValueError('Shared native scalar/byte budget cannot reset or count full unselected velocity arrays as decoded')
        samples=[frozen.observations(ds,m) for ds,m in zip(datasets,metas)]
        for ds,m,rows in zip(datasets,metas,samples):
            for r in rows:independent_record(ds,m,r)
        profiles=[];contexts_checked=0;csvrows=[]
        for i,label in enumerate(frozen.DATES):
            rows=[s[i] for s in samples];coords=[r.get('source_coordinate') for r in rows]
            same=all(c is not None for c in coords) and all(abs(a-b)<=1e-4 for a,b in zip(coords[0],coords[1]))
            same_label=bool(getattr(datasets[0],'mooring_name','')) and str(getattr(datasets[0],'mooring_name',''))==str(getattr(datasets[1],'mooring_name',''))
            supported=same and same_label and all(m['provider_east_north_frame_supported'] and m['CF_depth_coordinate_supported'] and not m['ancillary_QC_mapping_pending'] for m in metas)
            profile={'requested_time_utc':label,'samples':rows,'provider_same_site_coordinate_supported':bool(same),
              'provider_same_mooring_label_supported':bool(same_label),'provider_CF_depth_coordinate_supported':all(m['CF_depth_coordinate_supported'] for m in metas),
              'independent_sea_surface_or_gauge_datum_verified':False,'physical_current_identity_independently_verified':False,
              'actual_current_axis_verified':False,'native_coordinate_threshold_contexts':[],
              'physical_current_bottom_m':None,'physical_thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'volume_m3':None,
              'reference_inventory_admission_performed':False}
            if supported:
                z=[r['depth_m'] for r in rows];s=[-r['northward_m_s'] if r['northward_m_s'] is not None else None for r in rows]
                for q in [.05,.1,.2]:
                    result=frozen.pair_diagnostic(z,s,q);expected=independent_pair(z,s,q)
                    eq(result['lower_isotach_scenario_m'],expected)
                    result['lower_native_depth_coordinate_isotach_scenario_m']=result.pop('lower_isotach_scenario_m')
                    result['coordinate_interpretation']='provider_CF_depth_below_surface_positive_down_not_independently_verified_gauge_datum'
                    profile['native_coordinate_threshold_contexts'].append(result);contexts_checked+=1
            else:profile['status']='unresolved_site_component_QC_or_coordinate_support'
            profiles.append(profile)
            for k,row in enumerate(rows):
                csvrows.append({'instrument':str(datasets[k].getncattr('id')),'mooring':str(getattr(datasets[k],'mooring_name','')),
                  'requested_time_utc':label,'source_time_label_utc':row.get('source_time_label_utc'),'source_time_index':row['time_index'],
                  'native_depth_coordinate_m':row['depth_m'],'provider_nominal_instrument_depth_label':str(getattr(datasets[k],'instrument_depth','')),
                  'eastward_m_s':row['eastward_m_s'],'northward_m_s':row['northward_m_s'],
                  'provider_longitude':row['source_coordinate'][0] if row['source_coordinate'] else None,
                  'provider_latitude':row['source_coordinate'][1] if row['source_coordinate'] else None,
                  'source_status':row['source_status'],'source_raw_file':DATA+'/instrument-0'+str(k+1)+'.raw',
                  'source_raw_sha256':frozen.sha(raws[k]),'source_sampling_interval_label':str(getattr(datasets[k],'sampling_interval','')),
                  'provider_averaging_interval_independently_resolved':False,'sample_QC_independently_verified':False,
                  'source_depth_coordinate_definition':'provider_CF_depth_metres_positiveDown_surface_datum_not_independently_verified','native_depth_coordinate_is_current_bottom':False,'physical_thickness_m':None,'volume_m3':None})
        return {'schema':'osw.act2011-retained-pair-observations.v2','entity_id':'current:agulhas','native_headers':headers,
          'instrument_observations':samples,'profiles':profiles,'independent_threshold_contexts_verified':contexts_checked,
          'native_time_axis_scalars_loaded':time_values,'conservative_native_scalar_touch_bound':bound,
          'conservative_case_scalar_bound_including_prior_metadata':bound+2000,
          'data_model_by_instrument':[ds.data_model for ds in datasets],
          'native_observation_outcomes':len(csvrows),'valid_native_velocity_observation_outcomes':sum(r['eastward_m_s'] is not None and r['northward_m_s'] is not None for r in csvrows),
          'new_depth_references_admitted':0,'native_coordinate_scenarios_are_physical_current_bottom':False,
          'runtime_changed':False,'full_goal_complete':False},csvrows
    finally:
        for ds in datasets:ds.close()


def source_transfer_count(journal):
    return sum(r.get('command')=='RETR' and r.get('path','').lower().endswith('.nc') and r.get('status')=='provider_hash_verified_archived_before_parse' for r in journal['operations'])


def build(root=ROOT):
    urllib.request.urlopen=no_network;urllib.request.build_opener=no_network;socket.create_connection=no_network;ftplib.FTP.connect=no_network
    started=time.monotonic();op=json.loads((root/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if frozen.sha((root/f).read_bytes())!=h:raise ValueError('Pinned retained native input changed:'+f)
    journal=json.loads((root/DATA/'journal.json').read_bytes());old=json.loads((root/DATA/'profiles.json').read_bytes())
    if len(journal['operations'])!=10 or old['native_decode_completed'] or old.get('instrument_observations') or old['error_summary']!='One bounded native time axis required':raise ValueError('Exact pre-array unsupported old decoder outcome required')
    if source_transfer_count(journal)!=2:raise ValueError('Actual source receipt ledger, not inherited zero headers, must prove two native transfers')
    plan=frozen.targets(json.loads((root/frozen.INDEX).read_bytes()))
    for target,receipt in zip(plan,journal['operations'][7:]):
        raw=(root/DATA/receipt['raw_file']).read_bytes()
        if receipt['path']!=target['path'] or receipt['status']!='provider_hash_verified_archived_before_parse' or frozen.sha(raw)!=target['provider_asserted_sha256'] or len(raw)!=target['provider_size_bytes']:raise ValueError('Every original provider response size/hash/receipt must reproduce')
    raws=[(root/DATA/name).read_bytes() for name in ['instrument-01.raw','instrument-02.raw']]
    result,rows=extract(raws)
    audit={'schema':'osw.act2011-retained-pair-audit.v2','status':'PASS_RETAINED_NATIVE_EXTRACTION_AND_INDEPENDENT_POINT_SCENARIO_CHECKS',
      'provider_requests':0,'original_native_instrument_transfers_verified':2,'original_native_files_verified':2,
      'legacy_metadata_zero_counters_not_global':True,'corrected_original_field_transfer_count':source_transfer_count(journal),'unrefreshed_inherited_field_request_header':journal.get('ocean_field_requests'),
      'aggregate_case_operations_used_unchanged':10,'aggregate_case_operations_cap_unchanged':18,
      'remaining_case_operations_unchanged':8,'metadata_discovery_operations_used_unchanged':6,
      'prior_decoded_native_arrays':0,'native_time_axis_scalars_loaded':result['native_time_axis_scalars_loaded'],
      'conservative_native_scalar_touch_bound':result['conservative_native_scalar_touch_bound'],
      'conservative_case_scalar_bound_including_prior_metadata':result['conservative_case_scalar_bound_including_prior_metadata'],
      'native_observation_outcomes':result['native_observation_outcomes'],'valid_native_velocity_observation_outcomes':result['valid_native_velocity_observation_outcomes'],
      'independent_threshold_contexts_verified':result['independent_threshold_contexts_verified'],
      'new_depth_references_admitted':0,'physical_current_depth_thickness_or_volume_established':False,
      'input_sha256':op['input_sha256'],'operator_sha256':frozen.sha((root/OP).read_bytes()),
      'case_time_charge_before_audit':journal['case_time_charge_seconds'],'case_time_charge_after_audit':journal['case_time_charge_seconds']+time.monotonic()-started,
      'runtime_changed':False,'full_goal_complete':False}
    if audit['case_time_charge_after_audit']>210:raise ValueError('Original aggregate source/consumer time cap exceeded')
    buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader()
    for r in rows:writer.writerow({k:'' if v is None else v for k,v in r.items()})
    pieces={'audit.json':frozen.encoded(audit),'observations.json':frozen.encoded(result),'observations.csv':buffer.getvalue().encode()}
    if sum(map(len,pieces.values()))>=2400000:raise ValueError('Scientific output chunk cap exceeded')
    return pieces

if __name__=='__main__':
    pieces=build();folder=ROOT/'act2011-retained-pair-v2';folder.mkdir(exist_ok=False)
    for name,raw in pieces.items():(folder/name).write_bytes(raw)
    audit=json.loads(pieces['audit.json']);print(json.dumps({k:v for k,v in audit.items() if k not in ['input_sha256']}),flush=True)
