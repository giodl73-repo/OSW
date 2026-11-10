"""Cloud-only bounded salinity checks at the five frozen NCC reach-bound columns."""
import copy,hashlib,json,time
from datetime import datetime,timezone
from pathlib import Path
import netCDF4
import numpy as np
from ncc_core_salinity_diagnostic_v1 import diagnose

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/ncc-original-core-salinity-operator-v1.json'
OUT=Path('ncc-original-core-salinity-v1')


def clean(a):return [None if not np.isfinite(v) else float(v) for v in a]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()


class SalinityReads:
    def __init__(self,path,sleep=time.sleep):
        self.path=Path(path);self.sleep=sleep;self.requests=[];self.requested=0;self.returned=0;self.retry_reserved=0;self.save()
    def receipt(self):
        return {'schema':'osw.ncc-bounded-salinity-reads.v1','planned_successful_scalar_values':600,'additional_retry_scalar_values_reserved':self.retry_reserved,'actual_requested_scalar_values':self.requested,'successfully_returned_scalar_values':self.returned,'maximum_requested_scalar_values':1800,'conservative_all_target_plus_retries_bytes':8*(600+self.retry_reserved),'maximum_decoded_bytes':7000000,'maximum_attempts_per_target':3,'requests':self.requests,'wire_bytes_instrumented':False,'source_wire_hash_claimed':False}
    def save(self):self.path.write_bytes(encode(self.receipt()))
    def read(self,var,it,iy,ix):
        for attempt in range(1,4):
            if attempt>1:self.retry_reserved+=120
            if self.requested+120>1800 or 8*(600+self.retry_reserved)>7000000:raise ValueError('Frozen scalar/byte budget exceeded before read')
            entry={'variable':var.name,'source_time_index':it,'latitude_index':iy,'longitude_indices_inclusive':[ix-1,ix+1],'depth_indices_inclusive':[0,39],'attempt':attempt,'requested_scalar_values':120};self.requested+=120
            try:a=np.ma.filled(var[it,:,iy:iy+1,ix-1:ix+2],np.nan)[:,0,:]
            except RuntimeError as error:
                retry='NetCDF: I/O failure' in str(error);entry['status']='provider_io_failure' if retry else 'non_transport_error_not_retried';self.requests.append(entry);self.save()
                if not retry or attempt==3:raise
                self.sleep([2,5][attempt-1]);continue
            if a.shape!=(40,3):entry['status']='shape_mismatch_not_retried';self.requests.append(entry);self.save();raise ValueError('Exact40level3profile patch required')
            self.returned+=120;entry.update(status='success',actual_decoded_array_bytes=int(a.nbytes));self.requests.append(entry);self.save();return a


def load_targets(root,op):
    reader=lambda f:(root/f).read_bytes();report=json.loads(reader(op['original_audit_report_file']));targets=[]
    for si,study in enumerate(report['studies']):
        for ri,r in enumerate(study['records']):
            if r['entity_id']!='current:norwegian-coastal' or not r['reach_eligible']:continue
            raw=reader(r['source_section_file'])
            if digest(raw)!=r['source_section_sha256']:raise ValueError('Original velocity section changed')
            section=json.loads(raw);column=section['columns'][r['selected_column_index']]
            if section['entity_id']!=r['entity_id'] or section['source_time_index']!=section['retrieved_hyperslab']['time_index'] or section['snapshot_time_utc']!=r['snapshot_time_utc'] or column['sampled_lon_lat']!=r['sampled_lon_lat'] or section['diagnosis']['selected_column_index']!=r['selected_column_index'] or section['diagnosis']['selected_column_threshold_layers'][1]!=r['primary_layer'] or r['component_bearing_degrees_true']!=0 or r['primary_threshold_m_s']!=.1 or r['core_search_depth_interval_m']!=[0,100] or r['selection_depth_interval_m']!=[0,100] or r['surface_component_gate_m_s'] is not None:raise ValueError('Exact original selection,core,scope and snapshot required')
            targets.append({'source_audit_pointer':'/studies/'+str(si)+'/records/'+str(ri),'original_audit_record':copy.deepcopy(r),'section':section,'column':column})
    if [t['source_audit_pointer'] for t in targets]!=op['original_audit_pointers'] or len(targets)!=5:raise ValueError('All and only five original NCC bounds required')
    return targets


def preflight(ds,targets):
    z=np.asarray(ds['depth'][:],dtype=float);lats=np.asarray(ds['lat'][:],dtype=float);lons=np.asarray(ds['lon'][:],dtype=float);times=np.asarray(ds['time'][:],dtype=float)
    if z.shape!=(40,) or z[0]!=0 or z[-1]!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down' or not np.all(np.isfinite(z)) or np.any(np.diff(z)<=0) or ds['lat'].units!='degrees_north' or ds['lon'].units!='degrees_east':raise ValueError('Expected original native axes and positive-down depths')
    if any(a.ndim!=1 or not np.all(np.isfinite(a)) or np.any(np.diff(a)<=0) for a in [lats,lons,times]):raise ValueError('Finite strictly increasing coordinate/time axes required')
    attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
    var=ds['salinity']
    if attrs.get('field_type')!='instantaneous' or var.dimensions!=('time','depth','lat','lon') or var.units not in ['psu','PSU'] or var.standard_name!='sea_water_salinity':raise ValueError('Instantaneous practical-salinity variable metadata required')
    plans=[]
    for target in targets:
        s=target['section'];c=target['column'];r=target['original_audit_record'];iy=c['global_latitude_index'];ix=c['global_longitude_index'];it=s['source_time_index']
        if not np.array_equal(z,np.asarray(s['depth_levels_m'])) or not 0<=iy<len(lats) or not 1<=ix<len(lons)-1 or not 0<=it<len(times) or float(lats[iy])!=c['native_source_latitude_degrees_north'] or float(lons[ix])!=c['native_source_longitude_degrees_east']:raise ValueError('Exact native velocity/salinity node and depth axis required')
        for offset in [-1,0,1]:
            neighbor=s['columns'][r['selected_column_index']+offset]
            if neighbor['global_longitude_index']!=ix+offset or neighbor['global_latitude_index']!=iy or neighbor['native_source_longitude_degrees_east']!=float(lons[ix+offset]):raise ValueError('Exact original three-column neighbor stencil required')
        calendar=getattr(ds['time'],'calendar','gregorian');stamp=netCDF4.num2date(times[it],ds['time'].units,calendar=calendar).strftime('%Y-%m-%dT%H:%M:%SZ');numeric=netCDF4.date2num(datetime.strptime(r['snapshot_time_utc'],'%Y-%m-%dT%H:%M:%SZ'),ds['time'].units,calendar=calendar)
        if stamp!=r['snapshot_time_utc'] or np.count_nonzero(times==numeric)!=1 or times[it]!=numeric:raise ValueError('Exact original time index and timestamp required;no nearest date')
        plans.append({'it':it,'iy':iy,'ix':ix,'stamp':stamp,'depths':clean(z),'longitudes':clean(lons[ix-1:ix+2]),'latitude':float(lats[iy])})
    return plans,attrs,{k:str(var.getncattr(k)) for k in var.ncattrs()}


def collect(root=ROOT,out=OUT,dataset_factory=netCDF4.Dataset):
    op=json.loads((root/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if digest((root/f).read_bytes())!=pin:raise ValueError('Frozen salinity input changed: '+f)
    if op['practical_salinity_exclusive_upper_threshold']!=35 or op['velocity_threshold_m_s']!=.1 or any(op['eligibility'].values()) or op['opendap_dataset']!='https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/ts3z/2022':raise ValueError('Frozen source,classifier and non-promotion required')
    targets=load_targets(root,op);out.mkdir(exist_ok=True);reads=SalinityReads(out/'transport-ledger.json');records=[];pieces=[];ds=None
    report={'schema':'osw.ncc-original-core-salinity-source-report.v1','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'status':'PENDING','metadata_open_attempts':1,'records':records,'profiles':pieces,'new_reference_inventory_rows_admitted':0,'reference_inventory_updated':False,'physical_current_bottom_established':False,'full_goal_complete':False,'runtime_changed':False}
    try:
        ds=dataset_factory(op['opendap_dataset']);plans,attrs,varattrs=preflight(ds,targets);report.update(source_global_attributes=attrs,source_variable_attributes=varattrs,all_five_targets_preflighted_before_field_reads=True)
        for i,(target,plan) in enumerate(zip(targets,plans)):
            record={'source_audit_pointer':target['source_audit_pointer'],'original_audit_record':target['original_audit_record'],'status':'PENDING','classification':None};records.append(record)
            try:
                a=reads.read(ds['salinity'],plan['it'],plan['iy'],plan['ix'])
                if np.any((a[np.isfinite(a)]<0)|(a[np.isfinite(a)]>50)):raise ValueError('Decoded practical salinity outside frozen physical sanity range')
                columns=[clean(a[:,j]) for j in range(3)];record['classification']=diagnose(plan['depths'],target['column']['signed_reference_component_m_s'],columns[1],target['original_audit_record']['core_native_index']);record['status']='SALINITY_PROFILE_RETRIEVED_AND_CONDITIONAL_CORE_CLASSIFIED'
                profile={'schema':'osw.ncc-original-core-native-salinity-profile.v1','source_audit_pointer':target['source_audit_pointer'],'original_audit_record':target['original_audit_record'],'opendap_dataset':op['opendap_dataset'],'source_time_index':plan['it'],'source_returned_timestamp_utc':plan['stamp'],'native_latitude_index':plan['iy'],'native_longitude_indices_inclusive':[plan['ix']-1,plan['ix']+1],'depth_levels_m':plan['depths'],'native_latitude_degrees_north':plan['latitude'],'native_longitudes_degrees_east':plan['longitudes'],'practical_salinity_columns':columns,'selected_patch_column_index':1,'selected_original_component_m_s':target['column']['signed_reference_component_m_s'],'classification':record['classification'],'decoded_salinity_array_bytes':int(a.nbytes),'raw_wire_payload_hash_claimed':False,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'physical_current_bottom_established':False,'runtime_changed':False,'full_goal_complete':False};raw=encode(profile);name='target-'+str(i+1)+'.json'
                if len(raw)>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
                (out/name).write_bytes(raw);piece={'file':name,'sha256':digest(raw),'bytes':len(raw)};pieces.append(piece);record['profile']=piece
            except (RuntimeError,ValueError,OSError) as error:record.update(status='TARGET_SOURCE_OR_VALIDATION_FAILURE_NO_SUBSTITUTION',error_type=type(error).__name__,error_message=str(error)[:300])
        report['status']='ALL_FIVE_TARGETS_RETRIEVED' if len(pieces)==5 else 'PARTIAL_OR_FAILED_SOURCE_RETRIEVAL'
    except (RuntimeError,ValueError,OSError) as error:
        report.update(status='SOURCE_METADATA_OR_COLLLOCATION_PREFLIGHT_FAILED',error_type=type(error).__name__,error_message=str(error)[:300])
        records[:]=[{'source_audit_pointer':t['source_audit_pointer'],'original_audit_record':t['original_audit_record'],'status':'NOT_READ_PREFLIGHT_FAILED','classification':None} for t in targets]
    finally:
        if ds is not None:ds.close()
    report.update(transport=reads.receipt(),transport_ledger_sha256=digest((out/'transport-ledger.json').read_bytes()),new_salinity_scalar_requests=reads.requested,new_velocity_scalar_requests=0)
    raw=encode(report)
    if len(raw)>=2500000 or sum(p['bytes'] for p in pieces)+len(raw)+(out/'transport-ledger.json').stat().st_size>=2400000:raise ValueError('Frozen source-batch publication cap exceeded')
    (out/'source-report.json').write_bytes(raw);return report


def main():
    netCDF4.set_chunk_cache(1000000,1009,0.0);report=collect();print(json.dumps({'status':report['status'],'targets':len(report['records']),'profiles':len(report['profiles']),'transport':report['transport'],'classifications':[r['classification'] for r in report['records']]},allow_nan=False))


if __name__=='__main__':main()
