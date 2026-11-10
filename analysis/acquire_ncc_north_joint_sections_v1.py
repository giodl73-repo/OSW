"""Cloud-only northward NCC extension with one joint three-field reservation."""
import hashlib,json,time
from collections import Counter
from contextlib import ExitStack
from datetime import datetime,timezone
from pathlib import Path
import netCDF4
import numpy as np
from latitude_depth_section_geometry_v1 import preflight as geometry,columns_from_arrays
from interval_depth_diagnostic_v1 import diagnose,INTERIOR
from ncc_core_salinity_diagnostic_v1 import diagnose as fresh_diagnose
from sample_eac_hycom_route_depth_v1 import clean,canonical_hash

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/ncc-north-joint-sections-operator-v1.json'
OWNER='current:norwegian-coastal'
SECTIONS=[{'id':'section-61p5n','entity_id':OWNER,'fixed_axis':'latitude','latitude_degrees_north':61.5,'longitude_gate_degrees_east':[3,7]},{'id':'section-62p25n','entity_id':OWNER,'fixed_axis':'latitude','latitude_degrees_north':62.25,'longitude_gate_degrees_east':[3.5,8.5]}]
STAMPS=['2022-'+m+'-15T00:00:00Z' for m in ['03','06','09','12']]
UV='https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/uv3z/2022'
TS='https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/ts3z/2022'
FIELDS={'water_u':('m/s','eastward_sea_water_velocity'),'water_v':('m/s','northward_sea_water_velocity'),'salinity':('psu','sea_water_salinity')}


def encode(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()


class JointReads:
    def __init__(self,planned,path,sleep=time.sleep):
        if type(planned)!=int or planned<=0 or 2*planned>250000 or 24*planned>7000000:raise ValueError('All velocity pairs and salinity first reads must fit joint caps')
        self.planned=planned;self.path=Path(path);self.sleep=sleep;self.extra=0;self.actual=0;self.returned=0;self.requests=[];self.successes=set();self.save()
    def receipt(self):return {'schema':'osw.ncc-joint-three-field-read-ledger.v1','planned_velocity_cell_pairs':self.planned,'planned_salinity_scalars':self.planned,'planned_first_attempt_scalar_values':3*self.planned,'additional_retry_scalar_values_reserved':self.extra,'joint_reserved_native_cell_units':2*self.planned+self.extra,'conservative_joint_decoded_bytes':24*self.planned+8*self.extra,'actual_requested_scalar_values':self.actual,'successful_returned_scalar_values':self.returned,'maximum_joint_native_cell_units':250000,'maximum_decoded_bytes':7000000,'maximum_attempts_per_target':3,'requests':self.requests,'wire_hash_claimed':False}
    def save(self):self.path.write_bytes(encode(self.receipt()))
    def read(self,var,it,iy,x0,x1):
        n=x1-x0+1;values=40*n;key=(var.name,it,iy,x0,x1)
        if var.name not in FIELDS or any(type(v)!=int or v<0 for v in [it,iy,x0,x1]) or not 3<=n<=150 or values>20000:raise ValueError('Declared bounded native field patch required')
        if key in self.successes:raise ValueError('Successful field patch cannot be replayed')
        if self.actual+values>3*self.planned+self.extra:raise ValueError('No unreserved first reads')
        for attempt in range(1,4):
            entry={'variable':var.name,'time_index':it,'latitude_index':iy,'longitude_indices_inclusive':[x0,x1],'depth_indices_inclusive':[0,39],'attempt':attempt,'requested_scalar_values':values}
            if attempt>1:
                if 2*self.planned+self.extra+values>250000 or 24*self.planned+8*(self.extra+values)>7000000:raise ValueError('Retry cannot consume reserved future first reads')
                self.extra+=values
            self.actual+=values
            try:a=np.ma.filled(var[it,:,iy:iy+1,x0:x1+1],np.nan)[:,0,:]
            except RuntimeError as error:
                retry='NetCDF: I/O failure' in str(error);entry['status']='provider_io_failure' if retry else 'non_transport_error_not_retried';self.requests.append(entry);self.save()
                if not retry or attempt==3:raise
                self.sleep([2,5][attempt-1]);continue
            if a.shape!=(40,n):entry['status']='shape_mismatch_not_retried';self.requests.append(entry);self.save();raise ValueError('Exact native shape required')
            finite=a[np.isfinite(a)]
            if a.nbytes>8*values or (np.any((finite<0)|(finite>50)) if var.name=='salinity' else np.any(abs(finite)>10)):entry['status']='source_scaling_or_size_invalid_not_retried';self.requests.append(entry);self.save();raise ValueError('Source scale and decoded byte cap required')
            self.returned+=values;self.successes.add(key);entry.update(status='success',decoded_array_bytes=int(a.nbytes));self.requests.append(entry);self.save();return a


def validate_operator(op):
    if op['sections']!=SECTIONS or op['snapshot_times_utc']!=STAMPS or op['opendap_dataset']!=UV or op['salinity_opendap_dataset']!=TS or op['component_bearing_degrees_true']!=0 or op['primary_threshold_m_s']!=.1 or op['thresholds_m_s']!=[.05,.1,.2] or op['practical_salinity_exclusive_upper_threshold']!=35 or op['selection_depth_interval_m']!=[0,100] or op['core_search_depth_interval_m']!=[0,100] or op['surface_component_gate_m_s'] is not None or any(op['eligibility'].values()):raise ValueError('Exact declared domain and frozen source-specific rules required')
    if op['maximum_total_cell_pairs']!=250000 or op['maximum_total_decoded_velocity_bytes']!=7000000 or op['maximum_nearest_latitude_distance_km']!=5:raise ValueError('Unchanged native/decoded and axis caps required')


def preflight(uv,ts,op):
    validate_operator(op);axes={}
    for name in ['depth','lat','lon']:
        a=np.asarray(uv[name][:],dtype=float);b=np.asarray(ts[name][:],dtype=float)
        if a.ndim!=1 or not len(a) or not np.all(np.isfinite(a)) or np.any(np.diff(a)<=0) or not np.array_equal(a,b):raise ValueError('Exactly corresponding increasing native axes required before fields')
        axes[name]=a
    z=axes['depth']
    if len(z)!=40 or z[0]!=0 or z[-1]!=5000 or not np.any(z==100):raise ValueError('Exact forty-level depth support and native100m required')
    for ds in [uv,ts]:
        if ds['depth'].units!='m' or ds['depth'].positive!='down' or ds['lat'].units!='degrees_north' or ds['lon'].units!='degrees_east' or ds.getncattr('field_type')!='instantaneous':raise ValueError('Native coordinate units and instantaneous fields required')
    for name,(unit,standard) in FIELDS.items():
        var=(ts if name=='salinity' else uv)[name]
        if var.dimensions!=('time','depth','lat','lon') or var.units!=unit or var.standard_name!=standard:raise ValueError('Native source field units/frame/dimensions required')
    plans,planned=geometry(axes['lat'],axes['lon'],op)
    if 2*planned>250000 or 24*planned>7000000 or 100*planned+165536>=2400000:raise ValueError('Complete three-field cohort must fit unchanged caps before fields')
    for plan in plans:
        if not 3<=len(plan['longitude_indices'])<=150:raise ValueError('Bounded native profiles required')
    times={name:np.asarray(ds['time'][:],dtype=float) for name,ds in [('uv',uv),('ts',ts)]};timeplan=[]
    for stamp in STAMPS:
        indices=[]
        for name,ds in [('uv',uv),('ts',ts)]:
            calendar=getattr(ds['time'],'calendar','gregorian');numeric=netCDF4.date2num(datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ'),ds['time'].units,calendar=calendar);hits=np.flatnonzero(times[name]==numeric)
            if len(hits)!=1:raise ValueError('Exact unique snapshot required in both datasets')
            it=int(hits[0]);returned=netCDF4.num2date(times[name][it],ds['time'].units,calendar=calendar).strftime('%Y-%m-%dT%H:%M:%SZ')
            if returned!=stamp:raise ValueError('Exact returned snapshot required')
            indices.append(it)
        if indices[0]!=indices[1]:raise ValueError('Paired original time indices required')
        timeplan.append((stamp,indices[0]))
    return axes,plans,planned,timeplan


def classify(z,columns,salt,diagnosis):
    if diagnosis['horizontal_selection_status']!=INTERIOR:return {'status':'original_horizontal_axis_unresolved','original_horizontal_selection_status':diagnosis['horizontal_selection_status'],'original_selected_column_index':diagnosis['selected_column_index'],'core_reselected':False,'physical_current_bottom_established':False}
    selected=diagnosis['selected_column_index'];core=diagnosis['selected_column_threshold_layers'][1].get('core_index')
    if core is None:return {'status':'original_primary_core_unresolved','core_reselected':False,'physical_current_bottom_established':False}
    return fresh_diagnose(z,columns[selected]['signed_reference_component_m_s'],salt[selected],core)


def collect(root=ROOT,out=Path('ncc-north-joint-sections-v1'),factory=netCDF4.Dataset):
    op=json.loads((root/OPERATOR).read_bytes());validate_operator(op)
    for file,pin in op['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Frozen input changed: '+file)
    out=Path(out);out.mkdir(exist_ok=True);pieces=[];total=0;records=[]
    with ExitStack() as stack:
        uv=stack.enter_context(factory(UV));ts=stack.enter_context(factory(TS));axes,plans,planned,timeplan=preflight(uv,ts,op);reads=JointReads(planned,out/'transport-ledger.json');z=clean(axes['depth'])
        metadata={'velocity_global':{k:str(uv.getncattr(k)) for k in uv.ncattrs()},'salinity_global':{k:str(ts.getncattr(k)) for k in ts.ncattrs()},'variables':{name:{k:str((ts if name=='salinity' else uv)[name].getncattr(k)) for k in (ts if name=='salinity' else uv)[name].ncattrs()} for name in FIELDS}}
        for stamp,it in timeplan:
            for plan in plans:
                ix=plan['longitude_indices'];iy=int(plan['latitude_index']);args=(it,iy,int(ix[0]),int(ix[-1]));u=reads.read(uv['water_u'],*args);v=reads.read(uv['water_v'],*args);s=reads.read(ts['salinity'],*args)
                columns=columns_from_arrays(u,v,axes['lon'],float(axes['lat'][iy]),iy,ix,0);salt=[clean(s[:,i]) for i in range(len(ix))];diagnosis=diagnose(z,[c['signed_reference_component_m_s'] for c in columns],op);fresh=classify(z,columns,salt,diagnosis)
                report={'schema':'osw.ncc-north-joint-native-section.v1','entity_id':OWNER,'operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'section_definition':plan['definition'],'snapshot_time_utc':stamp,'source_returned_timestamp_utc':stamp,'source_time_index':it,'velocity_dataset':UV,'salinity_dataset':TS,'source_metadata':metadata,'depth_levels_m':z,'native_latitude_index':iy,'native_latitude_degrees_north':float(axes['lat'][iy]),'nearest_latitude_distance_km':plan['nearest_latitude_distance_km'],'native_longitude_indices_inclusive':[int(ix[0]),int(ix[-1])],'columns':columns,'practical_salinity_columns':salt,'decoded_columns_sha256':canonical_hash(columns),'decoded_salinity_sha256':canonical_hash(salt),'diagnosis':diagnosis,'fresh_component_classification':fresh,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'native_coordinates_exactly_paired':True,'core_reselected_after_salinity':False,'physical_current_bottom_established':False,'physical_thickness_m':None,'volume_m3':None,'annual_extrema_established':False,'full_goal_complete':False,'wire_hash_claimed':False}
                name=stamp[:10]+'-'+plan['definition']['id']+'.json';raw=encode(report);total+=len(raw)
                if len(raw)>=2500000 or total>=2200000:raise ValueError('Fixed source publication caps exceeded;no admission')
                (out/name).write_bytes(raw);piece={'file':name,'bytes':len(raw),'sha256':digest(raw)};pieces.append(piece);records.append({'section_id':plan['definition']['id'],'snapshot_time_utc':stamp,'profile':piece,'horizontal_selection_status':diagnosis['horizontal_selection_status'],'fresh_component_classification':fresh});print(json.dumps({'file':name,'profiles':len(columns),'axis_status':diagnosis['horizontal_selection_status'],'fresh_status':fresh['status']}),flush=True)
    if len(records)!=8 or reads.returned!=3*planned or len(reads.successes)!=24:raise ValueError('All8cases and24unique successful field patches required')
    summary={'schema':'osw.ncc-north-joint-source-report.v1','status':'ALL8JOINT_NATIVE_SECTIONS_RETRIEVED','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'profiles':pieces,'records':records,'counts':{'new_sections':8,'native_velocity_profiles':planned//40,'classification_status_counts':dict(Counter(r['fresh_component_classification']['status'] for r in records))},'transport':reads.receipt(),'transport_ledger_sha256':digest((out/'transport-ledger.json').read_bytes()),'all_targets_preflighted_before_fields':True,'new_reference_inventory_rows_admitted':0,'physical_current_bottom_established':False,'runtime_changed':False,'full_goal_complete':False}
    raw=encode(summary)
    if total+len(raw)+(out/'transport-ledger.json').stat().st_size>=2400000:raise ValueError('Fixed complete source batch cap exceeded')
    (out/'source-report.json').write_bytes(raw);print(json.dumps(summary['counts']))


if __name__=='__main__':collect()
