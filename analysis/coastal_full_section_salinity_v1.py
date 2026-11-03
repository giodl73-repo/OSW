"""Exact full-section salinity acquisition and frozen-core conditional diagnostics."""
import copy,hashlib,json,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import netCDF4
import numpy as np
from interval_depth_diagnostic_v1 import diagnose as original_diagnose,INTERIOR
from ncc_core_salinity_diagnostic_v1 import diagnose as ncc_diagnose
from egcc_core_salinity_diagnostic_v1 import diagnose as egcc_diagnose

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/coastal-full-section-salinity-operator-v1.json'
OUT=Path('coastal-full-section-salinity-v1')
RULES={'current:norwegian-coastal':(0,35),'current:east-greenland-coastal':(225,34)}
DATASET='https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/ts3z/2022'


def encode(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def clean(values):return [None if not np.isfinite(v) else float(v) for v in values]


class SectionReads:
    def __init__(self,planned,path,sleep=time.sleep):
        self.planned=planned;self.path=Path(path);self.sleep=sleep;self.extra=0;self.requested=0;self.returned=0;self.requests=[]
        if type(planned)!=int or planned<=0 or 2*planned>250000 or 24*planned>7000000:raise ValueError('Retained velocity and all first salinity targets must fit original caps')
        self.save()
    def receipt(self):
        return {'schema':'osw.coastal-bounded-full-section-salinity-reads.v1','retained_velocity_cell_pairs_audited':self.planned,'planned_first_attempt_salinity_scalars':self.planned,'additional_retry_scalars_reserved':self.extra,'actual_requested_salinity_scalars':self.requested,'successful_returned_salinity_scalars':self.returned,'joint_retained_pairs_plus_reserved_salinity_scalars':2*self.planned+self.extra,'maximum_joint_native_cell_units':250000,'conservative_retained_velocity_and_reserved_salinity_bytes':24*self.planned+8*self.extra,'maximum_decoded_bytes':7000000,'maximum_attempts_per_target':3,'requests':self.requests,'wire_bytes_instrumented':False,'wire_hash_claimed':False}
    def save(self):self.path.write_bytes(encode(self.receipt()))
    def read(self,var,it,iy,x0,x1):
        n=x1-x0+1;values=40*n
        if any(type(v)!=int or v<0 for v in [it,iy,x0,x1]) or not 3<=n<=150 or values>20000:raise ValueError('Original profile/patch caps and nonnegative native indices required')
        for attempt in range(1,4):
            entry={'variable':var.name,'time_index':it,'latitude_index':iy,'longitude_indices_inclusive':[x0,x1],'depth_indices_inclusive':[0,39],'attempt':attempt,'requested_scalar_values':values}
            if attempt>1:
                if 2*self.planned+self.extra+values>250000 or 24*self.planned+8*(self.extra+values)>7000000:
                    entry.update(status='retry_denied_to_preserve_all_remaining_first_attempts',requested_scalar_values=0);self.requests.append(entry);self.save();raise ValueError('Retry denied before read by complete-target reservation')
                self.extra+=values
            if self.planned+self.requested+values>250000 or 16*self.planned+8*(self.requested+values)>7000000:raise ValueError('Actual joint native/byte cap exceeded before read')
            self.requested+=values
            try:a=np.ma.filled(var[it,:,iy:iy+1,x0:x1+1],np.nan)[:,0,:]
            except RuntimeError as error:
                retry='NetCDF: I/O failure' in str(error);entry['status']='provider_io_failure' if retry else 'non_transport_error_not_retried';self.requests.append(entry);self.save()
                if not retry or attempt==3:raise
                self.sleep([2,5][attempt-1]);continue
            if a.shape!=(40,n):entry.update(status='shape_mismatch_not_retried',observed_decoded_bytes=int(a.nbytes));self.requests.append(entry);self.save();raise ValueError('Exact requested native shape required')
            entry.update(status='success',decoded_array_bytes=int(a.nbytes));self.returned+=values;self.requests.append(entry);self.save();return a


def load_targets(root,op):
    targets=[];seen=set()
    if [s['entity_id'] for s in op['studies']]!=list(RULES):raise ValueError('Both declared owners in frozen study order required')
    for study in op['studies']:
        entity=study['entity_id'];manifest=json.loads((root/study['manifest_file']).read_bytes());sopraw=(root/study['source_operator_file']).read_bytes();sop=json.loads(sopraw);config={**sop,**sop['currents'][entity]};bearing,salt=RULES[entity]
        if manifest['operator_file']!=study['source_operator_file'] or manifest['operator_sha256']!=digest(sopraw) or config['component_bearing_degrees_true']!=bearing or config['primary_threshold_m_s']!=.1 or config['selection_depth_interval_m']!=[0,100] or config['core_search_depth_interval_m']!=[0,100] or config['surface_component_gate_m_s'] is not None or config['thresholds_m_s']!=[.05,.1,.2]:raise ValueError('Original owner-specific velocity definition required')
        own=[p for p in manifest['sections'] if p['entity_id']==entity];expected={(entity,stamp,s['id']) for stamp in sop['snapshot_times_utc'] for s in sop['sections'] if s['entity_id']==entity}
        if len(own)!=16:raise ValueError('All sixteen original sections per owner required')
        for piece in own:
            file=study['source_directory']+piece['file'];raw=(root/file).read_bytes()
            if digest(raw)!=piece['sha256'] or len(raw)!=piece['bytes']:raise ValueError('Exact original velocity section bytes required')
            s=json.loads(raw);key=(entity,s['snapshot_time_utc'],s['section_definition']['id'])
            if key in seen or s['entity_id']!=entity or s['operator_file']!=study['source_operator_file'] or s['operator_sha256']!=digest(sopraw) or s['source_section_geometry']!='latitude' or s['component_bearing_degrees_true']!=bearing:raise ValueError('Unique original owner,section and fixed frame required')
            seen.add(key)
            if original_diagnose(s['depth_levels_m'],[c['signed_reference_component_m_s'] for c in s['columns']],config)!=s['diagnosis']:raise ValueError('Original core/axis selection must reproduce unchanged')
            targets.append({'file':file,'sha256':piece['sha256'],'section':s,'salinity_threshold':salt})
        if {key for key in seen if key[0]==entity}!=expected:raise ValueError('Every original cut and quarterly snapshot required')
    if len(targets)!=32:raise ValueError('Complete32target cohort required')
    return targets


def preflight(ds,targets):
    z=np.asarray(ds['depth'][:],dtype=float);lat=np.asarray(ds['lat'][:],dtype=float);lon=np.asarray(ds['lon'][:],dtype=float);times=np.asarray(ds['time'][:],dtype=float)
    if z.shape!=(40,) or z[0]!=0 or z[-1]!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down' or ds['lat'].units!='degrees_north' or ds['lon'].units!='degrees_east' or any(a.ndim!=1 or not np.all(np.isfinite(a)) or np.any(np.diff(a)<=0) for a in [z,lat,lon,times]):raise ValueError('Original native geographic/depth/time axes required')
    attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()};var=ds['salinity']
    if attrs.get('field_type')!='instantaneous' or var.dimensions!=('time','depth','lat','lon') or var.units not in ['psu','PSU'] or var.standard_name!='sea_water_salinity':raise ValueError('Instantaneous native practical-salinity metadata required')
    plans=[];planned=0
    for target in targets:
        s=target['section'];columns=s['columns'];n=len(columns);slab=s['retrieved_hyperslab'];iy=slab['latitude_index'];x0,x1=slab['longitude_indices_inclusive'];it=s['source_time_index'];stamp=s['snapshot_time_utc']
        if not 3<=n<=150 or n*40>20000 or x1-x0+1!=n or not 0<=x0<=x1<len(lon) or not 0<=iy<len(lat) or not 0<=it<len(times) or slab['time_index']!=it or slab['depth_indices_inclusive']!=[0,39] or not np.array_equal(z,np.asarray(s['depth_levels_m'])):raise ValueError('Exact original full native section shape required')
        for j,c in enumerate(columns):
            if c['global_longitude_index']!=x0+j or c['global_latitude_index']!=iy or c['native_source_longitude_degrees_east']!=float(lon[x0+j]) or c['native_source_latitude_degrees_north']!=float(lat[iy]):raise ValueError('Every original native source column must match exactly')
        calendar=getattr(ds['time'],'calendar','gregorian');numeric=netCDF4.date2num(datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ'),ds['time'].units,calendar=calendar);returned=netCDF4.num2date(times[it],ds['time'].units,calendar=calendar).strftime('%Y-%m-%dT%H:%M:%SZ')
        if returned!=stamp or times[it]!=numeric or np.count_nonzero(times==numeric)!=1:raise ValueError('Exact original time index and timestamp required;no nearest date')
        plans.append({'it':it,'iy':iy,'x0':x0,'x1':x1,'native_depths_m':clean(z),'native_latitude_degrees_north':float(lat[iy]),'native_longitudes_degrees_east':clean(lon[x0:x1+1]),'timestamp_utc':returned});planned+=40*n
    estimated=32*planned+8192*len(targets)+524288
    if 2*planned>250000 or 24*planned>7000000 or estimated>=2400000:raise ValueError('Complete cohort must fit fixed joint native,decoded and source-batch caps before fields')
    return plans,planned,estimated,attrs,{k:str(var.getncattr(k)) for k in var.ncattrs()}


def check_controls(targets,payloads,controls):
    by_source={t['file']:payloads[i] for i,t in enumerate(targets) if i in payloads};results=[]
    for file,control in controls:
        source=control['original_audit_record']['source_section_file'];p=by_source.get(source);status='CONTROL_TARGET_NOT_RETRIEVED'
        if p is not None:
            start=control['native_longitude_indices_inclusive'][0]-p['native_longitude_indices_inclusive'][0];subset=p['practical_salinity_columns'][start:start+3]
            status='EXACT_RETAINED_CONTROL_MATCH' if start>=0 and subset==control['practical_salinity_columns'] and p['source_time_index']==control['source_time_index'] and p['native_latitude_index']==control['native_latitude_index'] and p['depth_levels_m']==control['depth_levels_m'] else 'RETAINED_CONTROL_MISMATCH_NO_REPAIR'
        results.append({'control_file':file,'original_velocity_source_file':source,'status':status})
    return len(results)==5 and all(r['status']=='EXACT_RETAINED_CONTROL_MATCH' for r in results),results


def classify(section,salinity_columns):
    original=section['diagnosis'];selected=original['selected_column_index'];entity=section['entity_id']
    if entity not in RULES:raise ValueError('Declared source-specific classifier required')
    if original['horizontal_selection_status']!=INTERIOR:return {'status':'original_horizontal_axis_unresolved','original_horizontal_selection_status':original['horizontal_selection_status'],'original_selected_column_index':selected,'core_reselected':False,'physical_current_bottom_established':False,'volume_eligible':False}
    layer=original['selected_column_threshold_layers'][1];core=layer.get('core_index')
    if core is None:return {'status':'original_primary_core_unresolved','core_reselected':False,'physical_current_bottom_established':False,'volume_eligible':False}
    diagnostic=ncc_diagnose if entity=='current:norwegian-coastal' else egcc_diagnose
    return diagnostic(section['depth_levels_m'],section['columns'][selected]['signed_reference_component_m_s'],salinity_columns[selected],core)


def collect(root=ROOT,out=OUT,dataset_factory=netCDF4.Dataset):
    read=lambda f:json.loads((root/f).read_bytes());op=read(OPERATOR)
    for file,pin in op['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Frozen full-cohort source input changed: '+file)
    if op['opendap_dataset']!=DATASET or op['classifiers']!={k:{'component_bearing_degrees_true':v[0],'practical_salinity_exclusive_upper_threshold':v[1],'velocity_threshold_m_s':.1} for k,v in RULES.items()} or any(op['eligibility'].values()):raise ValueError('Frozen source-specific rules and non-promotion required')
    targets=load_targets(root,op);controls=[(file,read(file)) for file in op['retained_control_files']]
    if len(controls)!=5 or len({file for file,c in controls})!=5 or len({c['original_audit_record']['source_section_file'] for file,c in controls})!=5 or any(c['original_audit_record']['entity_id']!='current:norwegian-coastal' for file,c in controls):raise ValueError('All five distinct original NCCcontrols required')
    out.mkdir(exist_ok=True);records=[{'entity_id':t['section']['entity_id'],'snapshot_time_utc':t['section']['snapshot_time_utc'],'section_id':t['section']['section_definition']['id'],'original_velocity_source_file':t['file'],'original_velocity_source_sha256':t['sha256'],'original_selected_column_index':t['section']['diagnosis']['selected_column_index'],'original_horizontal_selection_status':t['section']['diagnosis']['horizontal_selection_status'],'status':'PENDING','classification':None} for t in targets];payloads={};ds=None;reads=None
    report={'schema':'osw.coastal-full-section-salinity-source-report.v1','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'status':'PENDING','metadata_open_attempts':1,'records':records,'profiles':[],'new_reference_inventory_rows_admitted':0,'reference_inventory_updated':False,'model_projection_inventory_updated':False,'physical_current_bottom_established':False,'runtime_changed':False,'full_goal_complete':False}
    try:
        ds=dataset_factory(DATASET);plans,planned,estimated,attrs,varattrs=preflight(ds,targets);reads=SectionReads(planned,out/'transport-ledger.json');report.update(all_targets_preflighted_before_field_reads=True,original_velocity_diagnoses_reproduced=32,planned_salinity_scalars=planned,source_batch_preflight_estimated_bytes=estimated,source_global_attributes=attrs,source_variable_attributes=varattrs)
        for i,(target,plan) in enumerate(zip(targets,plans)):
            try:
                a=reads.read(ds['salinity'],plan['it'],plan['iy'],plan['x0'],plan['x1'])
                if np.any((a[np.isfinite(a)]<0)|(a[np.isfinite(a)]>50)):raise ValueError('Decoded practical salinity outside fixed sanity range')
                s=target['section'];payloads[i]={'schema':'osw.coastal-full-section-native-salinity.v1','entity_id':s['entity_id'],'original_velocity_source_file':target['file'],'original_velocity_source_sha256':target['sha256'],'source_diagnosis_pointer':'/diagnosis','opendap_dataset':DATASET,'source_time_index':plan['it'],'source_returned_timestamp_utc':plan['timestamp_utc'],'native_latitude_index':plan['iy'],'native_longitude_indices_inclusive':[plan['x0'],plan['x1']],'depth_levels_m':plan['native_depths_m'],'native_latitude_degrees_north':plan['native_latitude_degrees_north'],'native_longitudes_degrees_east':plan['native_longitudes_degrees_east'],'practical_salinity_columns':[clean(a[:,j]) for j in range(a.shape[1])],'original_selected_column_index':s['diagnosis']['selected_column_index'],'original_horizontal_selection_status':s['diagnosis']['horizontal_selection_status'],'original_primary_layer':copy.deepcopy(s['diagnosis']['selected_column_threshold_layers'][1]) if s['diagnosis']['selected_column_threshold_layers'] else None,'component_bearing_degrees_true':RULES[s['entity_id']][0],'practical_salinity_exclusive_upper_threshold':RULES[s['entity_id']][1],'velocity_threshold_m_s':.1,'classification':None,'decoded_salinity_array_bytes':int(a.nbytes),'wire_hash_claimed':False,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'published_coastal_front_foot_definition_reproduced':False,'physical_current_bottom_established':False,'runtime_changed':False,'full_goal_complete':False};records[i]['status']='FULL_NATIVE_SALINITY_SECTION_RETRIEVED'
            except (RuntimeError,ValueError,OSError) as error:records[i].update(status='SOURCE_TARGET_FAILED_NO_SUBSTITUTION',error_type=type(error).__name__,error_message=str(error)[:300])
    except (RuntimeError,ValueError,OSError) as error:
        report.update(status='SOURCE_OR_COHORT_PREFLIGHT_FAILED',error_type=type(error).__name__,error_message=str(error)[:300])
        for r in records:r['status']='NOT_READ_PREFLIGHT_FAILED'
    finally:
        if ds is not None:ds.close()
    controls_passed,control_results=check_controls(targets,payloads,controls);report.update(retained_controls=control_results,all_five_retained_controls_match=controls_passed)
    for i,payload in payloads.items():
        if controls_passed:payload['classification']=classify(targets[i]['section'],payload['practical_salinity_columns']);records[i]['classification']=payload['classification']
        else:records[i]['status']='RETRIEVED_BUT_CONTROL_GATE_NOT_SATISFIED_NO_CLASSIFICATION'
        raw=encode(payload);filename=Path(targets[i]['file']).name
        if len(raw)>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
        (out/filename).write_bytes(raw);piece={'file':filename,'sha256':digest(raw),'bytes':len(raw)};report['profiles'].append(piece);records[i]['profile']=piece
    if controls_passed:report['status']='ALL32SECTIONS_RETRIEVED_AND_CONTROLS_MATCH' if len(payloads)==32 else 'PARTIAL_SOURCE_WITH_CONTROLS_MATCHED'
    elif payloads:report['status']='RETAINED_CONTROL_GATE_NOT_SATISFIED'
    if reads is not None:report.update(transport=reads.receipt(),transport_ledger_sha256=digest((out/'transport-ledger.json').read_bytes()))
    report['classification_status_counts']=dict(Counter(r['classification']['status'] for r in records if r['classification'] is not None));report['new_velocity_scalar_requests']=0
    raw=encode(report)
    ledger_bytes=(out/'transport-ledger.json').stat().st_size if reads is not None else 0
    if len(raw)>=2500000 or sum(p['bytes'] for p in report['profiles'])+len(raw)+ledger_bytes>=2400000:raise ValueError('Fixed source-batch publication cap exceeded')
    (out/'source-report.json').write_bytes(raw);return report


def main():
    netCDF4.set_chunk_cache(1000000,1009,0.0);r=collect();print(json.dumps({k:r.get(k) for k in ['status','planned_salinity_scalars','all_five_retained_controls_match','classification_status_counts','transport']},allow_nan=False))


if __name__=='__main__':main()
