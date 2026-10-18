"""Retain native vector quality and ship-motion support before estimating widths."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from collections import Counter
import hashlib,json,math
import numpy as np
import xarray as xr
from pyproj import Geod
from build_p14n_native_metadata import verify as verify_metadata
from build_aleutian_p14n_vector_section import valid_values,layer_mean

ROOT=Path(__file__).resolve().parents[1]
BASE='research/source-data/jasadcp-p14n-1993-native/'
OUTPUT='research/aleutian-p14n-1993-native-vector-support.json'
PROTOCOL='plans/aleutian-p14n-native-field-audit-protocol-v1.md'
FROZEN_INPUTS={'research/source-data/jasadcp-p14n-1993-native/00016_short.nc': '5b81d211bbb7aadc60c065f7c66ace16572f79569d7642bc96436923785bc6f8', 'research/source-data/jasadcp-p14n-1993-native/00016_long.nc': 'bbd76e9d7322c54d8476f6ef545bcc10ebb0678c5e145c897554cbe13c82f746', 'research/source-data/jasadcp-p14n-1993-native/acquisition.json': 'be53aa8de06de0355ce4fa597a0a6250873f955ed863bdc408c883364c704bc1', 'analysis/acquire_p14n_native_products.py': 'da4018dc0d9dc7af1b7f55f74360f92516f1f4c00d063843109509976ec8948c', 'plans/aleutian-p14n-native-source-preflight-v1.md': 'a5c49bc002ccbf72dee754dcc3ff12dea24e8328e9e2b2daf38601613355fb3e', 'research/source-data/jasadcp-p14n-1993/gateway.html': 'e2ada40a24ef2674d7c3c243936648f0b8cc7fad56682fb95afdbe6367b89f2b', 'research/aleutian-p14n-1993-native-product-metadata.json': '6b5050ba8c1aeaf08667df95ad432c1ab5faa63b563b8161f40dbb3d3906c859', 'analysis/build_p14n_native_metadata.py': '6687b4f0a175b5a989969a950a548f9f99f74b3b7ff9cbf4843eb48f27bf71ab', 'plans/aleutian-p14n-native-field-audit-protocol-v1.md': '7ddc303a29fe29e68ed9a0a2d6715938812335d1eab510a3f31e4804e108a3b2', 'research/aleutian-p14n-1993-hydrography-correspondence.json': '6342f35f1a9f9affe71244eabd8e1dfe0bb7f46046bccf30eb564274cf202c04', 'analysis/build_aleutian_p14n_vector_section.py': '13609eb33036638035804d97d0d9d1956113c53724e54d667390e0ad62232118'}
GEOD=Geod(ellps='WGS84')
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
def stamp(value):return value.isoformat().replace('+00:00','Z')
def moment(value):return datetime.fromisoformat(value)
def distance(a,b):return GEOD.inv(a['longitude_degrees_east'],a['latitude_degrees_north'],b['longitude_degrees_east'],b['latitude_degrees_north'])[2]/1000
def require_units(source,expected):
    for name,units in expected.items():
        if source[name].attrs.get('units')!=units:raise ValueError('Changed native field units: '+name)

def supported_layer(depth,u,v,flags):
    depth=np.asarray(depth,float);u=np.asarray(u,float);v=np.asarray(v,float);flags=np.asarray(flags)
    if depth.shape!=u.shape or u.shape!=v.shape or flags.shape!=u.shape:raise ValueError('Unpaired native profile arrays')
    if not np.all(np.isfinite(depth)) or len(depth)<2 or np.any(np.diff(depth)<=0):
        return {'joint_valid_thickness_m':0.,'eastward_m_s':None,'northward_m_s':None,'depth_coordinates_acceptable':False}
    result=layer_mean(depth,np.where(flags==0,u,np.nan),np.where(flags==0,v,np.nan))
    return dict(result,depth_coordinates_acceptable=True)

def overlaps(start,end,events):
    if start is None:return []
    found=[]
    for event in events:
        seconds=(min(end,moment(event['end_utc']))-max(start,moment(event['begin_utc']))).total_seconds()
        if seconds>0:found.append({'ctd_identity':event['ctd_identity'],'nominal_overlap_seconds':seconds})
    return found

def runs(rows,cutoff):
    groups=[];current=[]
    for row in rows:
        eligible=row['ship_speed_m_s'] is not None and row['ship_speed_m_s']>=cutoff and row['layer_mean']['eastward_m_s'] is not None and row['ensemble_start_utc'] is not None
        previous=current[-1] if current else None
        gap=(moment(row['ensemble_end_utc'])-moment(previous['ensemble_end_utc'])).total_seconds() if previous else None
        adjacent=previous is None or (row['source_time_index']==previous['source_time_index']+1 and 0<gap<=450)
        if current and (not eligible or not adjacent):groups.append(current);current=[]
        if eligible:current.append(row)
    if current:groups.append(current)
    result=[]
    for group in groups:
        track=sum(distance(a,b) for a,b in zip(group,group[1:]))
        result.append({'source_time_indices':[r['source_time_index'] for r in group],'profile_count':len(group),
                       'first_ensemble_start_utc':group[0]['ensemble_start_utc'],'last_ensemble_end_utc':group[-1]['ensemble_end_utc'],
                       'observed_elapsed_hours':(moment(group[-1]['ensemble_end_utc'])-moment(group[0]['ensemble_start_utc'])).total_seconds()/3600,
                       'track_length_between_ensemble_end_positions_km':track,'endpoint_distance_km':distance(group[0],group[-1]),
                       'northward_steps':sum(b['latitude_degrees_north']>a['latitude_degrees_north'] for a,b in zip(group,group[1:])),
                       'ctd_event_overlapping_profiles':sum(bool(r['ctd_event_overlaps']) for r in group),'current_length_or_width':False})
    return {'ship_speed_cutoff_m_s':cutoff,'eligible_profiles':sum(r['profile_count'] for r in result),'run_count':len(result),'runs':result}

def build():
    if len(FROZEN_INPUTS)!=11:raise ValueError('Missing declared native field dependencies')
    for name,pin in FROZEN_INPUTS.items():
        if digest(name)!=pin:raise ValueError('Changed native field input: '+name)
    metadata=verify_metadata()
    hydro=json.loads((ROOT/'research/aleutian-p14n-1993-hydrography-correspondence.json').read_bytes())
    events=[]
    for cast in hydro['casts']:
        begins=[r for r in cast['source_summary_events'] if r['event_code']=='BE'];ends=[r for r in cast['source_summary_events'] if r['event_code']=='EN']
        if len(begins)!=1 or len(ends)!=1 or moment(begins[0]['time_utc'])>=moment(ends[0]['time_utc']):raise ValueError('Unresolved cast beginning/end metadata')
        events.append({'ctd_identity':cast['identity'],'begin_utc':begins[0]['time_utc'],'end_utc':ends[0]['time_utc'],'source_begin_line':begins[0]['source_line'],'source_end_line':ends[0]['source_line']})
    with xr.open_dataset(ROOT/(BASE+'00016_short.nc'),decode_cf=False,create_default_indexes=False) as short,xr.open_dataset(ROOT/(BASE+'00016_long.nc'),decode_cf=False,create_default_indexes=False) as long:
        require_units(short,{'depth':'meter','u':'meter second-1','v':'meter second-1','uship':'meter second-1','vship':'meter second-1'})
        require_units(long,{'CONFIG1_avg_interval':'s','u':'m/s','v':'m/s','ACCESS_U_ship_absolute':'m/s','ACCESS_V_ship_absolute':'m/s'})
        time=np.asarray(short.time.values,float)
        if not np.all(np.isfinite(time)) or np.any(np.diff(time)<=0):raise ValueError('Invalid or unordered native times')
        if not np.array_equal(time,np.asarray(long.time.values,float)):raise ValueError('Short/long time indices differ')
        epoch=datetime(1993,1,1,tzinfo=timezone.utc);times=[epoch+timedelta(days=float(t)) for t in time]
        lat,latvalid=valid_values(short.lat);lon,lonvalid=valid_values(short.lon)
        indices=[i for i,t in enumerate(times) if datetime(1993,7,7,tzinfo=timezone.utc)<=t<datetime(1993,7,19,tzinfo=timezone.utc) and latvalid[i] and lonvalid[i] and 40<=lat[i]<=48 and 178<=lon[i]%360<=180]
        if not indices:raise ValueError('No selected native profiles')
        def field(source,key):
            values,valid=valid_values(source[key].isel(time=indices));return np.where(valid,values,np.nan)
        u=field(short,'u');v=field(short,'v');depth=field(short,'depth');flags=field(short,'pflag')
        shipu=field(short,'uship');shipv=field(short,'vship');duration=field(long,'CONFIG1_avg_interval')
        lu=field(long,'u');lv=field(long,'v');lflags=field(long,'profile_flags');lsu=field(long,'ACCESS_U_ship_absolute');lsv=field(long,'ACCESS_V_ship_absolute')
        joint=np.isfinite(u)&np.isfinite(v);unflagged=flags==0
        compare=joint&unflagged&(lflags==0)&np.isfinite(lu)&np.isfinite(lv)&np.isfinite(lsu[:,None])&np.isfinite(lsv[:,None])
        du=np.abs(u-(lu+lsu[:,None]));dv=np.abs(v-(lv+lsv[:,None]))
        maxu=float(du[compare].max()) if compare.any() else None;maxv=float(dv[compare].max()) if compare.any() else None
        frame={'compared_joint_unflagged_cells':int(compare.sum()),'absolute_tolerance_m_s':1e-5,'maximum_eastward_difference_m_s':maxu,'maximum_northward_difference_m_s':maxv,'correspondence_within_tolerance':bool(compare.any() and maxu<=1e-5 and maxv<=1e-5),'short_ship_motion_added_again':False}
        rows=[]
        for local,index in enumerate(indices):
            end=times[index];seconds=float(duration[local]) if np.isfinite(duration[local]) else None
            start=end-timedelta(seconds=seconds) if seconds is not None and 0<seconds<=450 else None
            speed=math.hypot(shipu[local],shipv[local]) if np.isfinite(shipu[local]) and np.isfinite(shipv[local]) else None
            motion='unknown' if speed is None else 'slow' if speed<=.5 else 'underway_eligible' if speed>=2 else 'intermediate'
            layer=supported_layer(depth[local],u[local],v[local],flags[local])
            counts=Counter(int(f) if np.isfinite(f) and float(f).is_integer() else 'invalid' for f in flags[local])
            rows.append({'source_time_index':index,'raw_time_decimal_days_since1993':float(time[index]),'ensemble_end_utc':stamp(end),'nominal_ensemble_seconds':seconds,'ensemble_start_utc':stamp(start) if start else None,
                         'latitude_degrees_north':float(lat[index]),'longitude_degrees_east':float(lon[index]),'selection_longitude_modulo360':float(lon[index]%360),
                         'ship_eastward_m_s':float(shipu[local]) if np.isfinite(shipu[local]) else None,'ship_northward_m_s':float(shipv[local]) if np.isfinite(shipv[local]) else None,'ship_speed_m_s':speed,'ship_motion_class':motion,
                         'layer_mean':layer,'editing_flag_counts':{str(k):val for k,val in sorted(counts.items(),key=lambda item:str(item[0]))},
                         'joint_finite_cells':int(joint[local].sum()),'joint_finite_flagged_cells':int((joint[local]&~unflagged[local]).sum()),
                         'ctd_event_overlaps':overlaps(start,end,events)})
        flagcounts=Counter(int(f) if np.isfinite(f) and float(f).is_integer() else 'invalid' for f in flags.flat)
        selected_time_gaps=[(times[b]-times[a]).total_seconds() for a,b in zip(indices,indices[1:])]
        summary={'selected_native_profiles':len(rows),'retained_native_depth_cells':int(flags.size),'joint_finite_cells':int(joint.sum()),'joint_finite_unflagged_cells':int((joint&unflagged).sum()),'joint_finite_flagged_cells':int((joint&~unflagged).sum()),
                 'editing_flag_counts':{str(k):val for k,val in sorted(flagcounts.items(),key=lambda item:str(item[0]))},'short_long_flag_differences':int(np.count_nonzero(flags!=lflags)),
                 'supported_layer_means':sum(r['layer_mean']['eastward_m_s'] is not None for r in rows),'ship_motion_counts':dict(Counter(r['ship_motion_class'] for r in rows)),
                 'profiles_with_ctd_event_overlap':sum(bool(r['ctd_event_overlaps']) for r in rows),'underway_eligible_profiles_with_ctd_event_overlap':sum(r['ship_motion_class']=='underway_eligible' and bool(r['ctd_event_overlaps']) for r in rows),
                 'selected_adjacent_end_time_gap_seconds_min_max':[min(selected_time_gaps),max(selected_time_gaps)],'nominal_ensemble_seconds_counts':dict(Counter(str(r['nominal_ensemble_seconds']) for r in rows))}
    return {'schema':'osw.native-vector-support.v1','current_id':'aleutian','status':'observed_native_support_pending_underway_width_operator','input_sha256':dict(FROZEN_INPUTS),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'protocol_file':PROTOCOL,'source_metadata_file':'research/aleutian-p14n-1993-native-product-metadata.json','summary':summary,'frame_correspondence':frame,'ctd_event_intervals':events,'profiles':rows,'run_sensitivity':[runs(rows,c) for c in [1.,2.,3.]],
            'ocean_and_ship_velocity_arrays_inspected':True,'time_support':'UTC ensemble end; nominal start uses actual source CONFIG1_avg_interval seconds','layer_bounds_m':[100,300],'minimum_joint_layer_support_m':160,'depth_role':'nominal source bin centres, no sound-speed-profile correction',
            'osw_temporal_ocean_velocity_averaging_applied':False,'current_association_verified':False,'new_width_record_admitted':False,'whole_current_width_km':None,'annual_width_range_km':None,'physical_edge_geometry_admitted':False,'seasonal_playback_supported':False,
            'cautions':['Ship-motion classes are OSW threshold context, not verified activity or physical current identity. GPS uncertainty affects source ship motion and ocean velocity.',
            'Nominal CTD-event overlap is not same-depth simultaneity or a recovered CTD-wire interference flag. All positive overlaps retained.',
            'OSW applies no further temporal averaging to provider-processed native ensembles. Paper GPS-related uncertainty is0.47m/s at5minutes; no width error interval follows.',
            'Run track distance and duration describe sampling, not current dimensions. No station gap or unsupported mean is bridged.']}

def verify():
    report=build()
    if (ROOT/OUTPUT).read_bytes()!=encoded(report):raise ValueError('Stale native vector-support audit')
    return report

if __name__=='__main__':
    report=build();(ROOT/OUTPUT).write_bytes(encoded(report));print(json.dumps({'summary':report['summary'],'frame':report['frame_correspondence'],'runs':[{k:v for k,v in row.items() if k!='runs'} for row in report['run_sensitivity']]}))
