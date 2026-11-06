"""Bounded original ACT instrument acquisition and typed three-date observations."""
import copy,ftplib,hashlib,json,math,os,re,signal,time
from datetime import datetime,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/act2011-observed-pair-operator-v1.json'
INDEX='research/act2010-retained-instrument-manifest-index-v1.json'
PRIOR='research/source-data/act2010-version-metadata-v2/journal.json'
HOST='ftp-oceans.ncei.noaa.gov'
BASE='/nodc/archive/arc0085/0140939/1.1/'
DATES=['2011-06-14T12:00:00Z','2011-06-15T12:00:00Z','2011-06-16T12:00:00Z']
PATHS=['NODC-Readme.txt','data/0-data/ACT_cm_timeseries_2010-2013_netcdf/M3960201.nc','data/0-data/ACT_cm_timeseries_2010-2013_netcdf/M3960301.nc']


def encoded(x):return (json.dumps(x,indent=2,allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def atomic(path,obj):
    temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('wb') as f:f.write(encoded(obj));f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
def alarm(signum,frame):
    if signum!=signal.SIGALRM:raise SystemExit('Producer terminated; no further operation')
    raise TimeoutError('Absolute source operation deadline')


def targets(index):
    found={e['manifest_path']:e for e in index['entries']}
    out=[]
    for i,path in enumerate(PATHS):
        e=found[path]
        if not e['regular_file'] or e['native_file_downloaded'] or e['ftp_url']!='ftp://'+HOST+BASE+path:raise ValueError('Only exact unattempted provider-manifest targets required')
        out.append({'target_id':['readme','instrument-01','instrument-02'][i],'path':BASE+path,
                    'provider_size_bytes':e['provider_size_bytes'],'provider_asserted_sha256':e['provider_asserted_sha256']})
    if sum(t['provider_size_bytes']+1 for t in out)>1700000:raise ValueError('Whole field-phase body reserve exceeded before download')
    return out


def reserve(j,folder,key,command,path,cap):
    if len(j['operations'])>=18 or len(j['operations'])-6>=4:raise ValueError('Original18operation case and4operation field-phase caps cannot reset')
    if any(r['target_id']==key or (r['command'],r['path'])==(command,path) for r in j['operations']):raise ValueError('No exact source target/archived response replay')
    if j['field_phase_body_bytes']+cap+1>1700000:raise ValueError('Aggregate field body cap exceeded')
    row={'target_id':key,'command':command,'path':path,'attempts':1,'cap_bytes':cap,'bytes_received':0,'status':'reserved_before_remote_operation'}
    j['operations'].append(row);atomic(folder/'journal.json',j);return row


def acquire(client,folder,j,target,deadline):
    if time.monotonic()+26>deadline:raise TimeoutError('Too little original-case time remains for new operation')
    row=reserve(j,folder,target['target_id'],'RETR',target['path'],target['provider_size_bytes'])
    path=folder/(target['target_id']+'.raw');size=0
    signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
    try:
        with path.open('xb') as f:
            def callback(block):
                nonlocal size
                part=block[:max(0,target['provider_size_bytes']+1-size)]
                f.write(part);f.flush();os.fsync(f.fileno());size+=len(part);row['bytes_received']=size
                if size>target['provider_size_bytes']:raise ValueError('Exact manifest size cap exceeded')
            client.retrbinary('RETR '+target['path'],callback,blocksize=16384)
        raw=path.read_bytes();row.update(raw_file=path.name,sha256=sha(raw))
        if size!=target['provider_size_bytes'] or sha(raw)!=target['provider_asserted_sha256']:raise ValueError('Original provider manifest size/SHA256 mismatch; no parse/retry')
        row.update(status='provider_hash_verified_archived_before_parse',provider_asserted_sha256=target['provider_asserted_sha256'])
        return raw
    except BaseException as error:
        row.update(status='failed_or_interrupted_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
        if path.exists():row.update(raw_file=path.name,sha256=sha(path.read_bytes()))
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);j['field_phase_body_bytes']+=size;j['total_body_bytes']+=size;atomic(folder/'journal.json',j)


def documentation_gate(raw):
    if len(raw)>10000:raise ValueError('Exact bounded original archive README required')
    text=raw.decode('utf8',errors='strict')
    deny=[r'not for public release',r'access (?:is )?restricted',r'do not (?:redistribute|download)',r'confidential',r'not authorized']
    if any(re.search(p,text,re.I) for p in deny):raise ValueError('Provider document restricts acquisition; no fields or alternate access')
    return {'basis':'Primarycatalog explicitly publishes originalanonymousFTPdistribution andCC0; conflicting non-public catalog label retained as metadata inconsistency, not an authentication denial. OriginalREADME reviewed for explicit restrictions before field transfer.',
            'provider_README_sha256':sha(raw),'explicit_restrictive_statement_detected':False,
            'catalog_label_discrepancy_not_erased':True,'no_access_control_bypassed':True,
            'scientific_schema_or_reference_eligibility_inferred':False}


def header(ds):
    if len(ds.variables)>64:raise ValueError('Bounded point-instrument header required')
    return {'dimensions':{k:len(v) for k,v in ds.dimensions.items()},
      'attributes':{k:str(ds.getncattr(k))[:2048] for k in ds.ncattrs()},
      'variables':{name:{'dtype':str(v.dtype),'dimensions':list(v.dimensions),'shape':list(v.shape),
       'attributes':{k:str(v.getncattr(k))[:2048] for k in v.ncattrs()}} for name,v in ds.variables.items()}}


def choose(ds,role):
    aliases={'time':['time','juld'],'u':['u','ucur','eastward_velocity','uvel'],'v':['v','vcur','northward_velocity','vvel'],'depth':['depth','deph','instrument_depth','z'],
             'latitude':['latitude','lat'],'longitude':['longitude','lon']}
    standard={'time':['time'],'u':['eastward_sea_water_velocity'],'v':['northward_sea_water_velocity'],'depth':['depth'],'latitude':['latitude'],'longitude':['longitude']}
    candidates=[name for name,v in ds.variables.items() if name.lower() in aliases[role] or str(getattr(v,'standard_name','')).lower() in standard[role]]
    if len(candidates)!=1:raise ValueError('One unambiguous native '+role+' variable required; retained header available')
    return ds[candidates[0]]


def factor(units):
    u=' '.join(str(units).lower().split())
    if u in ['m/s','m s-1','m s^-1','meters per second','metres per second']:return 1.
    if u in ['cm/s','cm s-1','cm s^-1','centimeters per second','centimetres per second']:return .01
    raise ValueError('Explicit native velocity units required')


def scalar(v,index,time_dim):
    import numpy as np
    key=tuple(index if d==time_dim else 0 for d in v.dimensions)
    value=v[key] if v.dimensions else v[...]
    if np.ma.is_masked(value):return None
    x=float(value)
    return x if math.isfinite(x) else None


def coordinate(ds,role,index,time_dim):
    for name in [role,role.upper(),role[:3],role[:3].upper(),'nominal_'+role]:
        if name in ds.ncattrs():
            try:return float(ds.getncattr(name))
            except (ValueError,TypeError):pass
    try:return scalar(choose(ds,role),index,time_dim)
    except ValueError:return None


def layout(ds):
    import numpy as np
    t=choose(ds,'time');u=choose(ds,'u');v=choose(ds,'v');z=choose(ds,'depth')
    if t.ndim!=1 or not 1<=t.size<=40000:raise ValueError('One bounded native time axis required')
    td=t.dimensions[0];calendar=str(getattr(t,'calendar','standard')).lower()
    if calendar not in ['standard','gregorian','proleptic_gregorian']:raise ValueError('Unambiguous Gregorian UTC calendar required')
    for var in [t,u,v,z]:
        if np.dtype(var.dtype).kind not in 'iuf' or any(d!=td and len(ds.dimensions[d])!=1 for d in var.dimensions):raise ValueError('Bounded primitive scalar point-instrument records required, not an unbounded ADCP field')
        if var is not t and var.dimensions.count(td)>1:raise ValueError('One time dimension per point variable')
    f_u=factor(getattr(u,'units',''));f_v=factor(getattr(v,'units',''))
    if str(getattr(z,'units','')).lower() not in ['m','meter','meters','metre','metres']:raise ValueError('Native metre depth required; no pressure/seabed conversion')
    ref=' '.join(str(getattr(z,k,'')) for k in ['reference_datum','reference','long_name','comment','description']).lower()
    depth_supported=str(getattr(z,'positive','')).lower()=='down' and any(k in ref for k in ['sea surface','sea_surface','sea level','sea_level'])
    names=[str(getattr(var,'standard_name',''))+' '+str(getattr(var,'long_name','')) for var in [u,v]]
    frame=('eastward_sea_water_velocity' in names[0] or 'east' in names[0].lower() or 'zonal' in names[0].lower()) and ('northward_sea_water_velocity' in names[1] or 'north' in names[1].lower() or 'meridional' in names[1].lower())
    qc_pending=bool(getattr(u,'ancillary_variables','') or getattr(v,'ancillary_variables',''))
    reserve=sum(max(1,var.size) for var in [t,u,v,z])+1000
    return {'time':t,'u':u,'v':v,'depth':z,'time_dim':td,'calendar':calendar,'u_factor':f_u,'v_factor':f_v,
       'native_scalar_reserve':reserve,'provider_depth_reference_supported':bool(depth_supported),
       'provider_east_north_frame_supported':bool(frame),'ancillary_QC_mapping_pending':qc_pending}


def observations(ds,meta):
    import netCDF4,numpy as np
    t=meta['time'];values=t[:];td=meta['time_dim'];units=getattr(t,'units','')
    result=[]
    for label in DATES:
        date=datetime.fromisoformat(label.replace('Z','+00:00')).replace(tzinfo=None)
        wanted=float(netCDF4.date2num(date,units,calendar=meta['calendar']))
        eps=abs(float(netCDF4.date2num(date+timedelta(seconds=1),units,calendar=meta['calendar']))-wanted)
        valid=np.ma.filled(np.isfinite(values)&(abs(values-wanted)<=eps),False)
        matches=np.flatnonzero(valid)
        if len(matches)>1:raise ValueError('Duplicate exact native timestamp; no nearest/best selection')
        if not len(matches):
            result.append({'requested_time_utc':label,'source_status':'no_exact_native_timestamp','time_index':None,'depth_m':None,'eastward_m_s':None,'northward_m_s':None,'source_coordinate':None});continue
        i=int(matches[0]);actual=netCDF4.num2date(float(values[i]),units,calendar=meta['calendar'])
        u=scalar(meta['u'],i,td);v=scalar(meta['v'],i,td);depth=scalar(meta['depth'],i,td)
        lat=coordinate(ds,'latitude',i,td);lon=coordinate(ds,'longitude',i,td)
        if lat is not None and not -90<=lat<=90:raise ValueError('Native latitude outside valid domain')
        if lon is not None and not -180<=lon<=360:raise ValueError('Native longitude outside valid domain')
        result.append({'requested_time_utc':label,'source_time_label_utc':actual.isoformat()+'Z','time_index':i,'source_status':'native_values_returned',
          'depth_m':depth,'eastward_m_s':u*meta['u_factor'] if u is not None else None,'northward_m_s':v*meta['v_factor'] if v is not None else None,
          'source_coordinate':[lon,lat] if lat is not None and lon is not None else None,
          'position_role':'provider_point_coordinate_not_independently_located_current_axis',
          'provider_averaging_interval_independently_resolved':False,'individual_QC_independently_verified':False,
          'CF_mask_scale_and_valid_range_applied':True})
    return result


def pair_diagnostic(depth,south,threshold):
    out={'threshold_m_s':threshold,'lower_isotach_scenario_m':None,'interpolation_bracket_m':None,
         'physical_current_bottom_m':None,'physical_thickness_m':None,'uncertainty_m':None,'volume_m3':None}
    if len(depth)!=2 or any(z is None for z in depth) or any(v is None for v in south):return out|{'status':'unresolved_missing_original_pair'}
    (z0,u0),(z1,u1)=sorted(zip(depth,south))
    if z0<0 or z1<=z0:return out|{'status':'unresolved_depth_geometry'}
    if z1-z0>500:return out|{'status':'censored_at_predeclared_500m_sample_gap'}
    if u0<=threshold:return out|{'status':'no_qualifying_upper_poleward_sample'}
    if u1>threshold:return out|{'status':'deeper_sample_still_above_threshold_unknown_bottom','deeper_observed_sample_depth_m':z1}
    crossing=(z0*(u1-threshold)+z1*(threshold-u0))/(u1-u0)
    return out|{'status':'conditional_two_sample_component_isotach_scenario','lower_isotach_scenario_m':crossing,
                'interpolation_bracket_m':[z0,z1],'piecewise_linear_no_hidden_reversals_assumed':True}


def decode(raws,report):
    import netCDF4
    datasets=[]
    try:
        for raw in raws:datasets.append(netCDF4.Dataset('source',memory=raw))
        report['native_headers']=[header(ds) for ds in datasets]
        layouts=[layout(ds) for ds in datasets]
        reserve=sum(m['native_scalar_reserve'] for m in layouts)
        report['conservative_native_scalar_reserve']=reserve
        if reserve>236000 or (reserve+2000)*8>7000000:raise ValueError('Whole-cohort native scalar/byte reserve exceeded before any arrays')
        samples=[observations(ds,m) for ds,m in zip(datasets,layouts)]
        report['instrument_observations']=samples
        report['native_decode_completed']=True
        for i,label in enumerate(DATES):
            pair=[s[i] for s in samples];coords=[p.get('source_coordinate') for p in pair]
            same=all(c is not None for c in coords) and all(abs(a-b)<=1e-4 for a,b in zip(coords[0],coords[1]))
            supported=same and all(m['provider_depth_reference_supported'] and m['provider_east_north_frame_supported'] and not m['ancillary_QC_mapping_pending'] for m in layouts)
            profile={'requested_time_utc':label,'same_provider_site_coordinate_supported':bool(same),
               'provider_depth_and_frame_supported':bool(supported),'samples':pair,
               'physical_current_identity_independently_verified':False,'actual_current_axis_verified':False,
               'physical_thickness_m':None,'annual_range_m':None,'volume_m3':None,
               'threshold_contexts':[],'reference_inventory_admission_performed':False}
            if supported:
                depth=[p['depth_m'] for p in pair];south=[-p['northward_m_s'] if p['northward_m_s'] is not None else None for p in pair]
                profile['threshold_contexts']=[pair_diagnostic(depth,south,q) for q in [.05,.1,.2]]
            else:profile['status']='unresolved_source_geometry_frame_depth_or_QC_support'
            report['profiles'].append(profile)
    finally:
        for ds in datasets:ds.close()


def collect(folder,client,prior,plan,deadline):
    folder.mkdir(exist_ok=False);started=time.monotonic();j=copy.deepcopy(prior)
    j.update(schema='osw.act2011-observed-pair-source-journal.v1',prior_receipt_source_directory='research/source-data/act2010-version-metadata-v2',
       prior_operation_count=6,prior_journal_file=PRIOR,metadata_stage_operations_used_unchanged=6,metadata_stage_cap_unchanged=6,
       field_phase_body_bytes=0,field_phase_body_cap=1700000,field_phase_operation_cap=4,
       prior_case_time_charge_seconds=51.622283097,producer_finalized_before_artifact_upload=False)
    report={'schema':'osw.act2011-observed-pair.v1','entity_id':'current:agulhas','source_accession':'0140939',
      'requested_times_utc':DATES,'profiles':[],'native_headers':[],'instrument_observations':[],
      'native_decode_completed':False,'new_depth_references_admitted':0,'physical_depth_or_volume_established':False,
      'runtime_changed':False,'full_goal_complete':False}
    failed=False
    try:
        row=reserve(j,folder,'pair-session-01','CONNECT_LOGIN_ANONYMOUS',BASE+'data/0-data/ACT_cm_timeseries_2010-2013_netcdf/',0)
        signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
        try:client.connect(HOST,21,timeout=25);client.login('anonymous','anonymous@');row['status']='explicit_field_phase_session_opened'
        except BaseException as error:row.update(status='failed_no_reconnect',error_type=type(error).__name__,error_summary=str(error)[:240]);raise
        finally:signal.setitimer(signal.ITIMER_REAL,0);atomic(folder/'journal.json',j)
        doc=acquire(client,folder,j,plan[0],deadline);report['documentation_review']=documentation_gate(doc)
        raws=[acquire(client,folder,j,t,deadline) for t in plan[1:]]
        if time.monotonic()>=deadline:raise TimeoutError('Original-case deadline exhausted before decode')
        signal.setitimer(signal.ITIMER_REAL,max(.1,deadline-time.monotonic()))
        decode(raws,report)
        report['status']='source_pair_acquired_and_typed_no_reference_admission'
    except BaseException as error:
        failed=True;report.update(status='partial_or_unsupported_source_retained_no_retry',error_type=type(error).__name__,error_summary=str(error)[:300])
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);client.close()
        j['producer_finalized_before_artifact_upload']=True;j['unused_independent_case_remote_operations']=18-len(j['operations'])
        j['field_phase_elapsed_seconds']=time.monotonic()-started;j['case_time_charge_seconds']=51.622283097+j['field_phase_elapsed_seconds']
        atomic(folder/'journal.json',j);atomic(folder/'profiles.json',report)
        if j['operations'][:6]!=prior['operations']:raise ValueError('Exact prior source receipts must remain unchanged')
        if sum(p.stat().st_size for p in folder.iterdir())>=2400000:raise ValueError('Scientific output chunk exceeds original cap')
        print(json.dumps({'status':report['status'],'aggregate_case_operations_reserved':len(j['operations']),
          'field_phase_body_bytes':j['field_phase_body_bytes'],'native_decode_completed':report['native_decode_completed'],
          'profiles_retained':len(report['profiles']),'native_scalar_reserve':report.get('conservative_native_scalar_reserve'),
          'error_summary':report.get('error_summary'),'new_depth_references_admitted':0}),flush=True)
    return report,j,failed


def main():
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if sha((ROOT/f).read_bytes())!=h:raise ValueError('Pinned native field input changed:'+f)
    if op['aggregate_case_operations_cap']!=18 or op['prior_operations_charged']!=6 or op['remaining_case_seconds']!=158 or op['maximum_field_phase_operations']!=4:raise ValueError('Case/stage/time budgets cannot reset')
    prior=json.loads((ROOT/PRIOR).read_bytes())
    if len(prior['operations'])!=6 or prior['total_body_bytes']!=73839 or prior['case_time_charge_seconds']!=51.622283097:raise ValueError('Exact prior source custody/time charge required')
    plan=targets(json.loads((ROOT/INDEX).read_bytes()))
    if plan!=op['targets']:raise ValueError('Exactly declared before-values instrument/README targets required')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,alarm)
    _,_,failed=collect(ROOT/'act2011-observed-pair-v1',ftplib.FTP(),prior,plan,time.monotonic()+158)
    if failed:raise SystemExit(1)

if __name__=='__main__':main()
