"""Cloud-only contiguous-row acquisition preserving the four frozen diagnostics."""
import base64,hashlib,json
from pathlib import Path
from bounded_hycom_http_ranges_v1 import BoundedHttpRanges
from pacific_neuc_mean_sections_v1 import section_plan,decode_component,section_diagnostic,dumps,ROOT

OPERATOR='research/pacific-neuc-mean-rectangle-operator-v2.json'


def rectangle_plan(axes,header,op):
    sections,diagnostic_counts=section_plan(axes,header,op)
    ix0=min(s['native_longitude_index'] for s in sections);ix1=max(s['native_longitude_index'] for s in sections);width=ix1-ix0+1
    iy=sections[0]['native_latitude_indices'];ny=len(axes['lat']);nx=len(axes['lon']);nz=len(axes['depth']);patches=[]
    pairs=nz*len(iy)*width
    if pairs>op['maximum_total_cell_pairs'] or pairs*8>op['maximum_total_decoded_bytes'] or pairs*4>op['maximum_requested_bytes']:raise ValueError('Rectangle shared field/transport budget exceeded')
    for name in ['water_u','water_v']:
        begin=sections[0]['components'][name]['variable_begin']
        for z0 in range(0,nz,op['native_depth_levels_per_patch']):
            z1=min(nz,z0+op['native_depth_levels_per_patch']);count=(z1-z0)*len(iy)*width
            if count>op['maximum_cell_pairs_per_patch']:raise ValueError('Rectangle patch cell budget exceeded')
            ranges=[(begin+2*((iz*ny+j)*nx+ix0),width*2) for iz in range(z0,z1) for j in iy]
            patches.append({'component':name,'depth_start_index':z0,'depth_stop_index':z1,'cell_pairs':count,'ranges':ranges})
    batches=[]
    for pi,patch in enumerate(patches):
        rows=patch['ranges']
        if pi==0:batches.append(rows[:1]);rows=rows[1:]
        batches.extend(rows[i:i+op['maximum_ranges_per_request']] for i in range(0,len(rows),op['maximum_ranges_per_request']))
    if len(batches)>op['maximum_http_requests'] or len(batches)*op['maximum_response_body_bytes']>op['maximum_total_response_body_bytes']:raise ValueError('Whole-plan request/body reservations exceeded')
    return sections,patches,batches,{'native_longitude_start_index':ix0,'native_longitude_stop_index_inclusive':ix1,'native_longitudes_deg_e':axes['lon'][ix0:ix1+1],
      'native_latitude_indices':iy,'native_profiles_in_rectangle':width*len(iy),'native_levels':nz,'cell_pairs':pairs,'decoded_float32_component_bytes':pairs*8,'packed_component_bytes':pairs*4,'planned_http_requests':len(batches),'patches':len(patches),'diagnostic_subset_counts':diagnostic_counts}


def extract_section_raw(row_parts,section,rectangle,axes,name):
    ix0=rectangle['native_longitude_start_index'];ix1=rectangle['native_longitude_stop_index_inclusive'];width=ix1-ix0+1
    column=section['native_longitude_index']-ix0
    if not 0<=column<width:raise ValueError('Diagnostic longitude outside acquired rectangle')
    begin=section['components'][name]['variable_begin'];nx=len(axes['lon']);ny=len(axes['lat'])
    out=[]
    for iz in range(len(axes['depth'])):
        for iy in section['native_latitude_indices']:
            key=(begin+2*((iz*ny+iy)*nx+ix0),width*2);raw=row_parts[key]
            if len(raw)!=width*2:raise ValueError('Exact rectangle row custody required')
            out.append(raw[column*2:column*2+2])
    return b''.join(out)


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen rectangle input changed: '+f)
    axes=json.loads((ROOT/op['coordinates_file']).read_bytes())['coordinate_arrays'];header=json.loads((ROOT/op['header_file']).read_bytes())
    sections,patches,batches,counts=rectangle_plan(axes,header,op);allowed=[r for patch in patches for r in patch['ranges']]
    reader=BoundedHttpRanges(header['source_object_url'],header['source_content_length'],header['source_last_modified'],allowed,op['maximum_http_requests'],op['maximum_requested_bytes'],op['maximum_response_body_bytes'],op['maximum_total_response_body_bytes'])
    out=Path('pacific-neuc-mean-rectangle-v2');out.mkdir(exist_ok=True);checkpoint=out/'completed-ranges';checkpoint.mkdir(exist_ok=True);parts={};files=[];diagnostics=[]
    def save(name,value):
        raw=dumps(value);(out/name).write_bytes(raw);files.append({'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    try:
        for batch in batches:
            values=reader.read(batch);index=len(reader.rows)-1
            (checkpoint/('request-%03d.json'%index)).write_bytes(dumps({'schema':'osw.neuc-completed-ranges.v1','request_index':index,'source_url':reader.url,'source_last_modified':reader.modified,'parts':[{'start':s,'length':n,'raw_base64':base64.b64encode(values[s,n]).decode()} for s,n in batch]}))
            parts.update(values);(out/'transport-ledger.json').write_bytes(dumps(reader.receipt()))
        for name in ['water_u','water_v']:
            ordered=[r for patch in patches if patch['component']==name for r in patch['ranges']];raw=b''.join(parts[r] for r in ordered)
            save('rectangle-'+name+'.json',{'schema':'osw.pacific-neuc-packed-rectangle.v2','component':name,'rectangle_counts':counts,'native_latitudes_deg_n':sections[0]['native_latitudes_deg_n'],'depth_levels_m':axes['depth'],'packing':{k:v for k,v in sections[0]['components'][name].items() if k!='ranges'},'packed_order':'ascending depth,latitude,longitude','packed_shape':[len(axes['depth']),len(counts['native_latitude_indices']),len(counts['native_longitudes_deg_e'])],'packed_base64':base64.b64encode(raw).decode(),'packed_sha256':hashlib.sha256(raw).hexdigest()})
        for si,s in enumerate(sections):
            components={}
            for name,packing in s['components'].items():
                raw=extract_section_raw(parts,s,counts,axes,name);components[name]={'packing':{k:v for k,v in packing.items() if k!='ranges'},'packed_order':'depth-major then ascending native latitude at one native longitude','packed_shape':[len(axes['depth']),len(s['native_latitude_indices'])],'packed_base64':base64.b64encode(raw).decode(),'packed_sha256':hashlib.sha256(raw).hexdigest(),'profiles_m_s':decode_component(raw,len(axes['depth']),len(s['native_latitude_indices']),packing)}
            diagnostic=section_diagnostic(axes['depth'],components['water_u']['profiles_m_s'],s['native_latitudes_deg_n'],op);diagnostics.append({'section_index':si,**diagnostic})
            save('section-%02d.json'%si,{'schema':'osw.pacific-neuc-mean-section.v1','section_index':si,**{k:v for k,v in s.items() if k!='components'},'depth_levels_m':axes['depth'],'components':components,'diagnostic':diagnostic,'current_identity_validated':False,'physical_current_depth_m':None})
        save('manifest.json',{'schema':'osw.pacific-neuc-mean-rectangle.v2','status':'QUALIFIED_PROVIDER_MEAN_DIAGNOSTIC_IDENTITY_NOT_VALIDATED','entity_id':op['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'source_object_url':reader.url,'source_content_length':reader.length,'source_last_modified':reader.modified,'nominal_provider_period':op['nominal_provider_period'],'temporal_operator_class':op['temporal_operator_class'],'counts':counts,'source_files':list(files),'section_diagnostics':diagnostics,'ocean_velocity_values_read':True,'averaging_semantics_validated':False,'provider_regional_bias_assessed':False,'current_identity_validated':False,'new_physical_depth_measurements':0,'regional_inventory_promotion_authorized':False,'runtime_changed':False,'full_goal_complete':False})
        print(json.dumps({'counts':counts,'section_selection_statuses':[d['horizontal_selection_status'] for d in diagnostics],'new_physical_depth_measurements':0,'inventory_promotion_authorized':False}))
    finally:
        (out/'transport-ledger.json').write_bytes(dumps(reader.receipt()))


if __name__=='__main__':main()
