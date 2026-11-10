"""Cloud-only mixed-axis interval sections using one frozen shared read budget."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import netCDF4
import numpy as np
from mixed_interval_section_geometry_v1 import preflight,profile_count,read_arguments,columns_from_arrays,retained_geometry,validate_retained
from bounded_hycom_mixed_reads_v1 import BoundedMixedReads
from interval_depth_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import clean,canonical_hash
from sample_eac_hycom_route_depth_v2 import check_budget

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/antarctic-coastal-bellingshausen-interval-depth-sections-operator-v1.json'
OUT=Path('antarctic-coastal-bellingshausen-interval-depth-sections-v1')


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for path,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen input changed: '+path)
    if any(op['eligibility'].values()) or any(c.get('temperature_gate') is not None or c['surface_component_gate_m_s'] is not None or c['core_search_depth_interval_m']!=c['selection_depth_interval_m'] for c in op['currents'].values()):raise ValueError('Equal interval windows,no surface/thermal gate and no physical promotion required')
    OUT.mkdir(exist_ok=True);manifest=[];pairs_used=0;bytes_used=0
    with netCDF4.Dataset(op['opendap_dataset']) as ds:
        z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:]);times=np.asarray(ds['time'][:])
        if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down':raise ValueError('Expected40positive-down metre levels0-5000m')
        if not np.all(np.isfinite(z)) or np.any(np.diff(z)<=0) or not all(np.any(z==endpoint) for c in op['currents'].values() for endpoint in c['selection_depth_interval_m']):raise ValueError('Finite increasing depth axis with every native interval endpoint required')
        if ds['lat'].units!='degrees_north' or ds['lon'].units!='degrees_east':raise ValueError('Native geographic coordinates required')
        attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
        if attrs.get('field_type')!='instantaneous':raise ValueError('Instantaneous source required')
        variable_attrs={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            var=ds[name]
            if var.dimensions!=('time','depth','lat','lon') or var.units!='m/s' or var.standard_name!=standard:raise ValueError('Unexpected source component dimensions/units/frame')
            variable_attrs[name]={k:str(var.getncattr(k)) for k in var.ncattrs()}
        plans,planned_pairs=preflight(lats,lons,op)
        time_plan=[]
        for stamp in op['snapshot_times_utc']:
            target=datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ');numeric=netCDF4.date2num(target,ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian'))
            hits=np.flatnonzero(times==numeric)
            if len(hits)!=1:raise ValueError('Exact requested snapshot absent or duplicated')
            it=int(hits[0]);returned=netCDF4.num2date(times[it],ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
            if returned!=stamp:raise ValueError('Returned snapshot changed')
            time_plan.append((stamp,it,returned))
        reads=BoundedMixedReads(planned_pairs,op,OUT/'transport-ledger.json')
        for stamp,it,returned in time_plan:
            for plan in plans:
                definition=plan['definition'];config={**op,**op['currents'][definition['entity_id']]};n=profile_count(plan)
                pairs=check_budget((40,n,1),pairs_used,op['maximum_total_cell_pairs'])
                if bytes_used+pairs*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Actual running decoded byte cap exceeded before retrieval')
                read=getattr(reads,'read_'+definition['fixed_axis']);arguments=read_arguments(plan)
                u=read(ds['water_u'],it,*arguments);v=read(ds['water_v'],it,*arguments)
                if u.shape!=(40,n) or v.shape!=u.shape:raise ValueError('Unexpected source depth/profile hyperslab shape')
                pairs_used+=pairs;bytes_used+=u.nbytes+v.nbytes
                if bytes_used>op['maximum_total_decoded_velocity_bytes'] or np.any(abs(u[np.isfinite(u)])>10) or np.any(abs(v[np.isfinite(v)])>10):raise ValueError('Source byte cap/scaling changed')
                columns=columns_from_arrays(u,v,lats,lons,plan,config['component_bearing_degrees_true'])
                result=diagnose(clean(z),[r['signed_reference_component_m_s'] for r in columns],config)
                section={'schema':'osw.mixed-interval-depth-section.v1','status':'EXPLORATORY_NATIVE_SECTION_MODEL_AXIS_PROXY',
                    'entity_id':definition['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),
                    'input_sha256':op['input_sha256'],'section_definition':definition,'source_section_geometry':definition['fixed_axis'],
                    'snapshot_time_utc':stamp,'source_returned_timestamp_utc':returned,'source_time_index':it,
                    'source_tau_hours_since_analysis':float(ds['tau'][it]) if 'tau' in ds.variables else None,
                    'component_bearing_degrees_true':config['component_bearing_degrees_true'],'depth_levels_m':clean(z),'columns':columns,
                    'decoded_columns_sha256':canonical_hash(columns),'diagnosis':result,'native100m_temperature_degrees_celsius':None,'temperature_source':None,
                    'source_product':op['source_product'],'opendap_dataset':op['opendap_dataset'],'source_global_attributes':attrs,'source_variable_attributes':variable_attrs,
                    'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'raw_HTTP_payload_bytes_instrumented':False,'source_subset_wire_byte_hash_claimed':False,
                    'geographic_gate_independently_validates_current_identity':False,'section_is_flow_normal':False,'water_mass_classification_performed':False,
                    'width_or_volume_join_performed':False,'uncertainty_m':None,'eligibility':op['eligibility'],'full_goal_complete':False,
                    **retained_geometry(plan,lats,lons,it)}
                validate_retained(section,config)
                filename=stamp[:10]+'-'+definition['entity_id'].split(':')[1]+'-'+definition['id']+'.json'
                raw=(json.dumps(section,indent=2,allow_nan=False)+'\n').encode('utf8')
                if len(raw)>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
                (OUT/filename).write_bytes(raw)
                manifest.append({'file':filename,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'section_id':definition['id'],'snapshot_time_utc':stamp,
                    'entity_id':definition['entity_id'],'source_section_geometry':definition['fixed_axis'],'native_columns':len(columns),
                    'selected_column_index':result['selected_column_index'],'horizontal_selection_status':result['horizontal_selection_status'],
                    'selected_column_threshold_layers':result['selected_column_threshold_layers']})
                print(json.dumps({'file':filename,'profiles':len(columns),'selected':result['selected_column_index'],'status':result['horizontal_selection_status']}),flush=True)
    if pairs_used!=planned_pairs or reads.returned_values!=2*planned_pairs:raise ValueError('Actual field count differs from complete joint preflight')
    (OUT/'manifest.json').write_text(json.dumps({'schema':'osw.mixed-interval-depth-sections-manifest.v1','operator_file':OPERATOR,
        'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'sections':manifest,
        'preflight_velocity_cell_pairs':planned_pairs,'decoded_velocity_cell_pairs':pairs_used,'decoded_velocity_array_bytes':bytes_used,
        'transport_ledger_file':'transport-ledger.json','transport_ledger_sha256':reads.digest(),'transport':reads.receipt(),
        'decoded_temperature_scalars':0,'decoded_temperature_array_bytes':0,'full_goal_complete':False},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'completed_sections':len(manifest),'native_profiles':sum(r['native_columns'] for r in manifest),'cell_pairs':pairs_used,'decoded_bytes':bytes_used}))


if __name__=='__main__':main()
