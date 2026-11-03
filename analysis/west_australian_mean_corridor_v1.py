"""Cloud-only qualified provider-mean corridor; no observed current-axis claim."""
import base64,hashlib,json,math
from pathlib import Path
from bounded_hycom_http_ranges_v1 import BoundedHttpRanges,validate_plan
from pacific_neuc_mean_sections_v1 import decode_component
from interval_depth_diagnostic_v1 import diagnose
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/west-australian-mean-corridor-operator-v1.json'


def encoded(value):
    return (json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode()


def plan_sections(axes,header,op,prior):
    z,lat,lon=[axes[k] for k in ['depth','lat','lon']]
    if op['component_bearing_degrees_true']!=0 or op['regional_inventory_promotion_authorized'] or len(axes['time'])!=1 or not math.isfinite(axes['time'][0]):raise ValueError('North-component qualified single-mean diagnostic required')
    if len(z)!=40 or z[0]!=0 or z[-1]!=5000 or any(type(x) not in [int,float] or not math.isfinite(x) for a in [z,lat,lon] for x in a) or any(b<=a for axis in [z,lat,lon] for a,b in zip(axis,axis[1:])):raise ValueError('Finite increasing full native axes required')
    dims={d['name']:d['declared_length'] for d in header['dimensions']}
    if header['format']!='CDF2' or header['record_count']!=1 or tuple(map(len,[z,lat,lon]))!=(dims['depth'],dims['lat'],dims['lon']):raise ValueError('Verified single-record CDF2 shape required')
    if any(x not in z for x in op['selection_depth_interval_m']):raise ValueError('Native selection endpoints required')
    if (prior['source_url'],prior['source_bytes'],prior['source_last_modified'])!=(header['source_object_url'],header['source_content_length'],header['source_last_modified']):raise ValueError('Prior range custody source identity changed')
    old=[tuple(r) for row in prior['requests'] if row['status']=='success' for r in row['ranges']]
    low,high=op['longitude_gate_deg_e'];ix=[i for i,x in enumerate(lon) if low<=x<=high]
    if not 3<=len(ix)<=op['maximum_profiles_per_section'] or ix!=list(range(ix[0],ix[-1]+1)):raise ValueError('Bounded complete native longitude gate required')
    variables={v['name']:v for v in header['variables']};sections=[];used=set()
    if variables['depth']['attributes']['units']['values']!='m' or variables['depth']['attributes']['positive']['values']!='down':raise ValueError('Metre depths positive downward required')
    for target in op['section_latitudes_deg_n']:
        iy=min(range(len(lat)),key=lambda i:abs(lat[i]-target));distance=abs(lat[iy]-target)*111.1950802335329
        if iy in used or distance>op['maximum_axis_distance_km']:raise ValueError('Unique native latitude within5km required')
        used.add(iy);components={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            v=variables[name];a=v['attributes']
            if v['dimension_names']!=['time','depth','lat','lon'] or v['nc_type']!=3 or v['external_element_bytes']!=2 or v['vsize']!=len(z)*len(lat)*len(lon)*2 or v['begin']<header['header_bytes'] or v['begin']+v['vsize']>header['source_content_length']:raise ValueError('Exact signedshort single-record storage required')
            if a['standard_name']['values']!=standard or a['units']['values']!='m/s' or a['_FillValue']['values']!=[-30000] or a['missing_value']['values']!=[-30000] or a['scale_factor']['values']!=[0.0010000000474974513] or a['add_offset']['values']!=[0.0]:raise ValueError('Frozen geographic CF component packing required')
            ranges=[(v['begin']+2*((iz*len(lat)+iy)*len(lon)+ix[0]),len(ix)*2) for iz in range(len(z))]
            components[name]={'variable_begin':v['begin'],'scale_factor':a['scale_factor']['values'][0],'add_offset':0.,'missing_packed':-30000,'ranges':ranges}
        sections.append({'requested_latitude_deg_n':target,'sampled_latitude_deg_n':lat[iy],'native_latitude_index':iy,'nearest_axis_distance_km':distance,'native_longitude_indices':ix,'native_longitudes_deg_e':[lon[i] for i in ix],'components':components})
    ranges=[r for s in sections for c in s['components'].values() for r in c['ranges']];validate_plan(ranges,1000000)
    if any(s<old_s+old_n and old_s<s+n for s,n in ranges for old_s,old_n in old):raise ValueError('Previously successful field range replay forbidden')
    pairs=len(sections)*len(ix)*len(z);requested=sum(n for _,n in ranges)
    if pairs>op['maximum_total_cell_pairs'] or pairs*16>op['maximum_total_decoded_bytes'] or len(ix)*len(z)>op['maximum_cell_pairs_per_section']:raise ValueError('Shared fixed ocean-field budgets exceeded')
    if len(ranges)>op['maximum_http_requests'] or requested>op['maximum_requested_bytes'] or max(n for _,n in ranges)>op['maximum_response_body_bytes'] or len(ranges)*op['maximum_response_body_bytes']>op['maximum_total_response_body_bytes']:raise ValueError('Complete single-request plan/future body reservation exceeded')
    return sections,{'sections':len(sections),'native_profiles':len(sections)*len(ix),'native_levels':len(z),'cell_pairs':pairs,'conservative_decoded_float64_component_bytes':pairs*16,'packed_component_bytes':requested,'planned_http_requests':len(ranges),'previous_successful_ranges_replayed':0}


def corridor_diagnosis(z,columns,op):
    result=diagnose(z,columns,op);ready=[i for i,r in enumerate(result['candidate_scores']) if r['eligible']];groups=[]
    for i in ready:
        if not groups or i!=groups[-1][-1]+1:groups.append([])
        groups[-1].append(i)
    result.update(qualifying_column_indices=ready,qualifying_component_groups=[{'column_indices':g,'touches_sample_domain_edge':g[0]==0 or g[-1]==len(columns)-1,'is_named_current_or_physical_width':False} for g in groups],
                  all_qualifying_column_layers=[{'column_index':i,'layers':[connected_layer(z,columns[i],t,op['core_search_depth_interval_m']) for t in op['thresholds_m_s']]} for i in ready],
                  selected_column_role='representative_interval_maximum_not_independently_validated_current_axis',
                  physical_current_axis_validated=False,physical_current_depth_m=None,physical_current_thickness_m=None,regional_inventory_promotion_authorized=False)
    return result


def mean_context(op,axes):
    return {'temporal_operator_class':op['temporal_operator_class'],'nominal_provider_period':op['nominal_provider_period'],'snapshot_time_utc':None,'source_time_coordinate':axes['time'],'time_coordinate_is_averaging_interval':False,'actual_averaging_coverage_verified':False,'averaging_weights_verified':False,'fixed_depth_Eulerian_mean_equivalence_verified':False,'seasonal_mean_or_annual_extrema_established':False}


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen WAC input changed: '+f)
    header=json.loads((ROOT/op['header_file']).read_bytes());axes=json.loads((ROOT/op['coordinates_file']).read_bytes())['coordinate_arrays'];prior=json.loads((ROOT/op['prior_custody_ledger']).read_bytes())
    sections,counts=plan_sections(axes,header,op,prior);allowed=[r for s in sections for c in s['components'].values() for r in c['ranges']]
    reader=BoundedHttpRanges(header['source_object_url'],header['source_content_length'],header['source_last_modified'],allowed,op['maximum_http_requests'],op['maximum_requested_bytes'],op['maximum_response_body_bytes'],op['maximum_total_response_body_bytes'])
    out=Path('west-australian-mean-corridor-v1');out.mkdir(exist_ok=True);checkpoints=out/'completed-ranges';checkpoints.mkdir(exist_ok=True);files=[];diagnostics=[]
    try:
        for si,s in enumerate(sections):
            data={};components={}
            for name,packing in s['components'].items():
                parts=[]
                for start,n in packing['ranges']:
                    raw=reader.read([(start,n)])[start,n];parts.append(raw);i=len(reader.rows)-1
                    (checkpoints/('request-%03d.json'%i)).write_bytes(encoded({'schema':'osw.wac-completed-single-range.v1','request_index':i,'source_url':reader.url,'source_last_modified':reader.modified,'start':start,'length':n,'sha256':hashlib.sha256(raw).hexdigest(),'raw_base64':base64.b64encode(raw).decode()}))
                    (out/'transport-ledger.json').write_bytes(encoded(reader.receipt()))
                raw=b''.join(parts);data[name]=decode_component(raw,len(axes['depth']),len(s['native_longitude_indices']),packing)
                components[name]={'packing':{k:v for k,v in packing.items() if k!='ranges'},'packed_order':'depth-major then native longitude','packed_shape':[len(axes['depth']),len(s['native_longitude_indices'])],'packed_base64':base64.b64encode(raw).decode(),'packed_sha256':hashlib.sha256(raw).hexdigest()}
            columns=[{'profile_index':j,'native_longitude_index':ix,'sampled_lon_lat':[s['native_longitudes_deg_e'][j],s['sampled_latitude_deg_n']],'eastward_velocity_m_s':data['water_u'][j],'northward_velocity_m_s':data['water_v'][j],'signed_reference_component_m_s':data['water_v'][j]} for j,ix in enumerate(s['native_longitude_indices'])]
            diagnosis=corridor_diagnosis(axes['depth'],[c['signed_reference_component_m_s'] for c in columns],op)
            section={'schema':'osw.west-australian-qualified-mean-section.v1','entity_id':op['entity_id'],'section_index':si,'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'source_mean_context':mean_context(op,axes),**{k:v for k,v in s.items() if k!='components'},'depth_levels_m':axes['depth'],'component_bearing_degrees_true':0,'columns':columns,'components':components,'diagnosis':diagnosis,'current_identity_validated':False,'physical_current_depth_m':None,'runtime_changed':False,'full_goal_complete':False}
            name='section-%02d.json'%si;raw=encoded(section)
            if len(raw)>=2500000:raise ValueError('Fixed source-file publication ceiling exceeded')
            (out/name).write_bytes(raw);files.append({'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'section_index':si})
            diagnostics.append({'section_index':si,'selected_column_index':diagnosis['selected_column_index'],'horizontal_selection_status':diagnosis['horizontal_selection_status'],'qualifying_columns':len(diagnosis['qualifying_column_indices']),'qualifying_groups':len(diagnosis['qualifying_component_groups']),'selected_column_threshold_layers':diagnosis['selected_column_threshold_layers']})
            print(json.dumps(diagnostics[-1]),flush=True)
        result={'schema':'osw.west-australian-qualified-mean-corridor.v1','status':'QUALIFIED_PROVIDER_MEAN_CORRIDOR_CURRENT_IDENTITY_UNVALIDATED','entity_id':op['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'source_object_url':reader.url,'source_content_length':reader.length,'source_last_modified':reader.modified,'source_mean_context':mean_context(op,axes),'counts':counts,'source_files':files,'section_diagnostics':diagnostics,'ocean_velocity_values_read':True,'regional_inventory_promotion_authorized':False,'new_physical_depth_measurements':0,'runtime_changed':False,'full_goal_complete':False}
        (out/'manifest.json').write_bytes(encoded(result));print(json.dumps({'counts':counts,'new_physical_depth_measurements':0,'regional_inventory_promotion_authorized':False}))
    finally:
        (out/'transport-ledger.json').write_bytes(encoded(reader.receipt()))


if __name__=='__main__':main()
