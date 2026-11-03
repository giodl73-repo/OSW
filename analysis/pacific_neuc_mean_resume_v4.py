"""Cloud-only residual five-row recovery importing every prior successful row."""
import base64,copy,hashlib,json,re
from pacific_neuc_mean_resume_v3 import import_custody,recovery_plan
from pathlib import Path
from bounded_hycom_http_ranges_v1 import BoundedHttpRanges
from pacific_neuc_mean_rectangle_v2 import rectangle_plan,extract_section_raw
from pacific_neuc_mean_sections_v1 import decode_component,section_diagnostic,dumps,ROOT

OPERATOR='research/pacific-neuc-mean-resume-operator-v4.json'


def restore_checkpoint_bundle(bundle,seed):
    if bundle['schema']!='osw.exact-utf8-artifact-member-bundle.v1':raise ValueError('Exact artifact-member envelope required')
    result=copy.deepcopy(seed);names=set()
    for member in bundle['members']:
        name=member['file'];raw=member['content_utf8'].encode('utf8')
        if name in names or not re.fullmatch(r'completed-ranges/request-[0-9]{3}\.json',name) or len(raw)!=member['bytes'] or hashlib.sha256(raw).hexdigest()!=member['sha256']:raise ValueError('Original checkpoint filename/bytes/hash changed')
        names.add(name);checkpoint=json.loads(raw)
        if any(checkpoint[k]!=seed[k] for k in ['schema','source_url','source_last_modified']) or checkpoint['request_index']!=int(name[-8:-5]):raise ValueError('Original checkpoint source/request identity changed')
        result['parts'].extend(checkpoint['parts'])
    return result


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen recovery input changed: '+f)
    old=json.loads((ROOT/op['geometry_operator_file']).read_bytes())
    axes=json.loads((ROOT/old['coordinates_file']).read_bytes())['coordinate_arrays'];header=json.loads((ROOT/old['header_file']).read_bytes())
    sections,patches,_,counts=rectangle_plan(axes,header,old);allowed=[r for patch in patches for r in patch['ranges']]
    checkpoint=restore_checkpoint_bundle(json.loads((ROOT/op['prior_checkpoint_bundle_file']).read_bytes()),json.loads((ROOT/op['prior_checkpoint_file']).read_bytes()))
    parts,rows,requested,body=import_custody([json.loads((ROOT/f).read_bytes()) for f in op['prior_ledger_files']],checkpoint,header)
    batches=recovery_plan(allowed,parts,rows,requested,body,op)
    reader=BoundedHttpRanges(header['source_object_url'],header['source_content_length'],header['source_last_modified'],allowed,op['maximum_http_requests'],op['maximum_requested_bytes'],op['maximum_response_body_bytes'],op['maximum_total_response_body_bytes'])
    reader.rows=rows;reader.requested_bytes=requested;reader.body_bytes=body;reader.completed=set(parts);reader.attempted=set(parts)
    out=Path('pacific-neuc-mean-resume-v4');out.mkdir(exist_ok=True);checkpoint=out/'completed-ranges';checkpoint.mkdir(exist_ok=True);files=[];diagnostics=[]
    counts={**counts,'legacy_geometry_planned_http_requests':counts['planned_http_requests'],'planned_http_requests':len(batches),'prior_http_requests':len(rows),'aggregate_planned_http_requests':len(rows)+len(batches),'imported_successful_ranges':len(parts)}
    print(json.dumps({'preflight_counts':counts,'prior_attempted_requested_bytes':requested,'prior_response_body_bytes':body}),flush=True)
    def save(name,value):
        raw=dumps(value);(out/name).write_bytes(raw);files.append({'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    save('imported-custody.json',{'schema':'osw.neuc-imported-custody.v1','input_sha256':{f:op['input_sha256'][f] for f in op['prior_ledger_files']+[op['prior_checkpoint_file'],op['prior_checkpoint_bundle_file']]},'successful_ranges':len(parts),'prior_http_requests':len(rows),'prior_attempted_requested_bytes':requested,'prior_response_body_bytes':body})
    try:
        for batch in batches:
            values=reader.read(batch);index=len(reader.rows)-1
            (checkpoint/('request-%03d.json'%index)).write_bytes(dumps({'schema':'osw.neuc-completed-ranges.v1','request_index':index,'source_url':reader.url,'source_last_modified':reader.modified,'parts':[{'start':s,'length':n,'raw_base64':base64.b64encode(values[s,n]).decode()} for s,n in batch]}))
            parts.update(values);(out/'transport-ledger.json').write_bytes(dumps(reader.receipt()))
            if index%25==3:print(json.dumps({'aggregate_requests':len(reader.rows),'completed_ranges':len(reader.completed),'body_bytes':reader.body_bytes}),flush=True)
        write_outputs(out,save,parts,sections,counts,axes,old,op,reader,files,diagnostics)
    finally:
        (out/'transport-ledger.json').write_bytes(dumps(reader.receipt()))


def write_outputs(out,save,parts,sections,counts,axes,geometry,op,reader,files,diagnostics):
    for name in ['water_u','water_v']:
        # Component order comes from the frozen exact geometry, never inferred from decoded values.
        _,patches,_,_=rectangle_plan(axes,json.loads((ROOT/geometry['header_file']).read_bytes()),geometry)
        ordered=[r for patch in patches if patch['component']==name for r in patch['ranges']];raw=b''.join(parts[r] for r in ordered)
        save('rectangle-'+name+'.json',{'schema':'osw.pacific-neuc-packed-rectangle.v2','component':name,'rectangle_counts':counts,'native_latitudes_deg_n':sections[0]['native_latitudes_deg_n'],'depth_levels_m':axes['depth'],'packing':{k:v for k,v in sections[0]['components'][name].items() if k!='ranges'},'packed_order':'ascending depth,latitude,longitude','packed_shape':[len(axes['depth']),len(counts['native_latitude_indices']),len(counts['native_longitudes_deg_e'])],'packed_base64':base64.b64encode(raw).decode(),'packed_sha256':hashlib.sha256(raw).hexdigest()})
    for si,s in enumerate(sections):
        components={}
        for name,packing in s['components'].items():
            raw=extract_section_raw(parts,s,counts,axes,name);components[name]={'packing':{k:v for k,v in packing.items() if k!='ranges'},'packed_order':'depth-major then ascending native latitude at one native longitude','packed_shape':[len(axes['depth']),len(s['native_latitude_indices'])],'packed_base64':base64.b64encode(raw).decode(),'packed_sha256':hashlib.sha256(raw).hexdigest(),'profiles_m_s':decode_component(raw,len(axes['depth']),len(s['native_latitude_indices']),packing)}
        diagnostic=section_diagnostic(axes['depth'],components['water_u']['profiles_m_s'],s['native_latitudes_deg_n'],geometry);diagnostics.append({'section_index':si,**diagnostic})
        save('section-%02d.json'%si,{'schema':'osw.pacific-neuc-mean-section.v1','section_index':si,**{k:v for k,v in s.items() if k!='components'},'depth_levels_m':axes['depth'],'components':components,'diagnostic':diagnostic,'snapshot_time_utc':None,'current_identity_validated':False,'physical_current_depth_m':None})
    save('manifest.json',{'schema':'osw.pacific-neuc-mean-resume.v4','status':'QUALIFIED_PROVIDER_MEAN_DIAGNOSTIC_IDENTITY_NOT_VALIDATED','entity_id':geometry['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'source_object_url':reader.url,'source_content_length':reader.length,'source_last_modified':reader.modified,'nominal_provider_period':geometry['nominal_provider_period'],'temporal_operator_class':geometry['temporal_operator_class'],'snapshot_time_utc':None,'counts':counts,'source_files':list(files),'section_diagnostics':diagnostics,'ocean_velocity_values_read':True,'averaging_semantics_validated':False,'provider_regional_bias_assessed':False,'current_identity_validated':False,'new_physical_depth_measurements':0,'regional_inventory_promotion_authorized':False,'runtime_changed':False,'full_goal_complete':False})
    print(json.dumps({'counts':counts,'section_selection_statuses':[d['horizontal_selection_status'] for d in diagnostics],'new_physical_depth_measurements':0,'inventory_promotion_authorized':False}),flush=True)


if __name__=='__main__':main()
