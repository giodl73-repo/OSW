"""Cloud-only exact CDF2 mean-field sections; no whole-current depth claim."""
import base64,hashlib,json,math,struct
from pathlib import Path
from bounded_hycom_http_ranges_v1 import BoundedHttpRanges
from interval_depth_diagnostic_v1 import diagnose,INTERIOR

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/pacific-neuc-mean-sections-operator-v1.json'


def dumps(value):
    return (json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode()


def section_plan(axes,header,op):
    z=axes['depth'];lat=axes['lat'];lon=axes['lon']
    if len(z)!=40 or any(not math.isfinite(x) for axis in [z,lat,lon] for x in axis) or any(b<=a for axis in [z,lat,lon] for a,b in zip(axis,axis[1:])):
        raise ValueError('Forty-level increasing finite native axes required')
    dims={d['name']:d['declared_length'] for d in header['dimensions']}
    if header['format']!='CDF2' or header['record_count']!=1 or (len(z),len(lat),len(lon))!=(dims['depth'],dims['lat'],dims['lon']):raise ValueError('Verified single-record dimensions required')
    if any(x not in z for x in op['selection_depth_interval_m']):raise ValueError('Native selection endpoints required')
    low,high=op['latitude_gate_deg_n'];iy=[i for i,x in enumerate(lat) if low<=x<=high]
    if not 3<=len(iy)<=op['maximum_profiles_per_section'] or iy!=list(range(iy[0],iy[-1]+1)):raise ValueError('Complete bounded native latitude gate required')
    variables={v['name']:v for v in header['variables']};sections=[];used=set()
    for target in op['section_longitudes_deg_e']:
        ix=min(range(len(lon)),key=lambda i:abs(lon[i]-target));distance=abs(lon[ix]-target)*111.1950802335329*math.cos(math.radians((low+high)/2))
        if ix in used or distance>op['maximum_axis_distance_km']:raise ValueError('Unique native longitude within tolerance required')
        used.add(ix);components={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            v=variables[name];attrs=v['attributes']
            if v['dimension_names']!=['time','depth','lat','lon'] or v['nc_type']!=3 or v['external_element_bytes']!=2 or v['vsize']!=len(z)*len(lat)*len(lon)*2 or v['begin']+v['vsize']>header['source_content_length']:raise ValueError('Exact packed single-record component storage required')
            if attrs['standard_name']['values']!=standard or attrs['units']['values']!='m/s' or attrs['_FillValue']['values']!=[-30000] or attrs['missing_value']['values']!=[-30000] or attrs['scale_factor']['values']!=[0.0010000000474974513] or attrs['add_offset']['values']!=[0.0]:raise ValueError('Frozen CF packing/frame required')
            ranges=[(v['begin']+2*((iz*len(lat)+j)*len(lon)+ix),2) for iz in range(len(z)) for j in iy]
            components[name]={'ranges':ranges,'variable_begin':v['begin'],'scale_factor':attrs['scale_factor']['values'][0],'add_offset':0.,'missing_packed':-30000}
        sections.append({'requested_longitude_deg_e':target,'sampled_longitude_deg_e':lon[ix],'native_longitude_index':ix,'nearest_axis_distance_km':distance,'native_latitude_indices':iy,'native_latitudes_deg_n':[lat[j] for j in iy],'components':components})
    pairs=len(sections)*len(iy)*len(z);decoded=pairs*2*4
    if pairs>op['maximum_total_cell_pairs'] or decoded>op['maximum_total_decoded_bytes'] or len(iy)*len(z)>op['maximum_cell_pairs_per_section']:raise ValueError('Shared fixed ocean field budgets exceeded')
    return sections,{'sections':len(sections),'native_profiles':len(sections)*len(iy),'native_levels':len(z),'cell_pairs':pairs,'decoded_float32_component_bytes':decoded,'packed_component_bytes':pairs*4}


def decode_component(raw,levels,profiles,packing):
    if len(raw)!=levels*profiles*2:raise ValueError('Exact packed component shape required')
    packed=struct.unpack('>'+str(levels*profiles)+'h',raw)
    values=[None if x==packing['missing_packed'] else x*packing['scale_factor']+packing['add_offset'] for x in packed]
    return [[values[iz*profiles+j] for iz in range(levels)] for j in range(profiles)]


def section_diagnostic(z,profiles,latitudes,op):
    result=diagnose(z,profiles,op);selected=result['selected_column_index'];layers=result['selected_column_threshold_layers']
    primary=next((x for x in layers if x['threshold_m_s']==op['primary_threshold_m_s']),None)
    low,high=op['independent_southern_jet_latitude_context_deg_n']
    result.update(selected_latitude_deg_n=latitudes[selected] if selected is not None else None,
                  selected_node_in_independent_latitude_context=selected is not None and low<=latitudes[selected]<=high,
                  primary_layer_detached_from_surface=primary is not None and primary['upper_status']=='adjacent_isotach_crossing' and primary['upper_depth_m']>0,
                  horizontal_interior_selection=result['horizontal_selection_status']==INTERIOR,
                  model_axis_independently_validated=False,current_identity_validated=False,
                  physical_current_depth_m=None,physical_current_thickness_m=None,
                  regional_inventory_promotion_authorized=False)
    return result


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen input changed: '+f)
    axes_source=json.loads((ROOT/op['coordinates_file']).read_bytes());axes=axes_source['coordinate_arrays']
    header=json.loads((ROOT/op['header_file']).read_bytes());sections,counts=section_plan(axes,header,op)
    allowed=[r for s in sections for c in s['components'].values() for r in c['ranges']]
    reader=BoundedHttpRanges(header['source_object_url'],header['source_content_length'],header['source_last_modified'],allowed,op['maximum_http_requests'],op['maximum_requested_bytes'],op['maximum_response_body_bytes'],op['maximum_total_response_body_bytes'])
    out=Path('pacific-neuc-mean-sections-v1');out.mkdir(exist_ok=True);checkpoints=out/'completed-ranges';checkpoints.mkdir(exist_ok=True)
    names=[];diagnostics=[]
    try:
        for si,s in enumerate(sections):
            component_data={}
            for name,p in s['components'].items():
                parts={};ranges=p['ranges']
                for first in range(0,len(ranges),op['maximum_ranges_per_request']):
                    batch=ranges[first:first+op['maximum_ranges_per_request']];values=reader.read(batch)
                    checkpoint={'schema':'osw.neuc-completed-ranges.v1','request_index':len(reader.rows)-1,'source_url':reader.url,'source_last_modified':reader.modified,'parts':[{'start':start,'length':n,'raw_base64':base64.b64encode(values[start,n]).decode()} for start,n in batch]}
                    (checkpoints/('request-%03d.json'%(len(reader.rows)-1))).write_bytes(dumps(checkpoint))
                    parts.update(values)
                    (out/'transport-ledger.json').write_bytes(dumps(reader.receipt()))
                raw=b''.join(parts[r] for r in ranges);profiles=decode_component(raw,len(axes['depth']),len(s['native_latitude_indices']),p)
                component_data[name]={'packing':{k:v for k,v in p.items() if k!='ranges'},'packed_order':'depth-major then ascending native latitude at one native longitude','packed_shape':[len(axes['depth']),len(s['native_latitude_indices'])],'packed_base64':base64.b64encode(raw).decode(),'packed_sha256':hashlib.sha256(raw).hexdigest(),'profiles_m_s':profiles}
            section={'schema':'osw.pacific-neuc-mean-section.v1','section_index':si,**{k:v for k,v in s.items() if k!='components'},'depth_levels_m':axes['depth'],'components':component_data,'diagnostic':section_diagnostic(axes['depth'],component_data['water_u']['profiles_m_s'],s['native_latitudes_deg_n'],op),'current_identity_validated':False,'physical_current_depth_m':None}
            name='section-%02d.json'%si;raw=dumps(section);(out/name).write_bytes(raw);names.append({'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});diagnostics.append({'section_index':si,**section['diagnostic']})
        result={'schema':'osw.pacific-neuc-mean-sections.v1','status':'QUALIFIED_PROVIDER_MEAN_DIAGNOSTIC_IDENTITY_NOT_VALIDATED','entity_id':op['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'source_object_url':header['source_object_url'],'source_content_length':header['source_content_length'],'source_last_modified':header['source_last_modified'],'nominal_provider_period':op['nominal_provider_period'],'temporal_operator_class':op['temporal_operator_class'],'time_coordinate_is_averaging_interval':False,'averaging_semantics_validated':False,'provider_regional_bias_assessed':False,'counts':counts,'source_files':names,'section_diagnostics':diagnostics,'ocean_velocity_values_read':True,'new_physical_depth_measurements':0,'current_identity_validated':False,'regional_inventory_promotion_authorized':False,'runtime_changed':False,'full_goal_complete':False}
        (out/'manifest.json').write_bytes(dumps(result));print(json.dumps({'counts':counts,'section_selection_statuses':[d['horizontal_selection_status'] for d in diagnostics],'new_physical_depth_measurements':0,'inventory_promotion_authorized':False}))
    finally:
        (out/'transport-ledger.json').write_bytes(dumps(reader.receipt()))


if __name__=='__main__':main()
