"""Cloud-only five-row recovery with imported successful-byte custody."""
import base64,copy,hashlib,json
from pathlib import Path
from bounded_hycom_http_ranges_v1 import BoundedHttpRanges
from pacific_neuc_mean_rectangle_v2 import rectangle_plan,extract_section_raw
from pacific_neuc_mean_sections_v1 import decode_component,section_diagnostic,dumps,ROOT

OPERATOR='research/pacific-neuc-mean-resume-operator-v3.json'


def import_custody(ledgers,checkpoint,header):
    rows=[];requested=0;body=0;expected={}
    for ledger in ledgers:
        if (ledger['source_url'],ledger['source_bytes'],ledger['source_last_modified'])!=(header['source_object_url'],header['source_content_length'],header['source_last_modified']):
            raise ValueError('Prior source identity changed')
        if ledger['automatic_retries']!=0:raise ValueError('Prior automatic retry forbidden')
        if sum(n for row in ledger['requests'] for _,n in row['ranges'])!=ledger['attempted_requested_bytes']:raise ValueError('Prior requested-byte custody mismatch')
        if sum(row.get('response_body_bytes',0) for row in ledger['requests'])!=ledger['response_body_bytes']:raise ValueError('Prior response-byte custody mismatch')
        completed=0
        for row in ledger['requests']:
            if row['status'] not in ['success','failed_no_replay']:raise ValueError('Only terminal attempts may be imported')
            if row['status']=='failed_no_replay' and row.get('response_body_bytes',0)!=0:raise ValueError('Recovery authorizes only zero-body prior failures')
            if row['status']=='success':
                keys={tuple(x) for x in row['ranges']};pins={(x['start'],x['length']):x['sha256'] for x in row['parts']}
                if keys!=set(pins) or len(keys)!=len(row['ranges']) or set(expected)&keys:raise ValueError('Prior duplicate or incomplete part custody')
                expected.update(pins);completed+=len(keys)
            rows.append(copy.deepcopy(row))
        if completed!=ledger['completed_ranges']:raise ValueError('Prior completed count mismatch')
        requested+=ledger['attempted_requested_bytes'];body+=ledger['response_body_bytes']
    if checkpoint['schema']!='osw.neuc-completed-ranges.v1' or checkpoint['source_url']!=header['source_object_url'] or checkpoint['source_last_modified']!=header['source_last_modified']:raise ValueError('Checkpoint source mismatch')
    parts={}
    for part in checkpoint['parts']:
        key=(part['start'],part['length']);raw=base64.b64decode(part['raw_base64'],validate=True)
        if key in parts or key not in expected or len(raw)!=key[1] or hashlib.sha256(raw).hexdigest()!=expected[key]:raise ValueError('Checkpoint bytes do not match successful ledger')
        parts[key]=raw
    if set(parts)!=set(expected):raise ValueError('Every successful prior range must be imported')
    return parts,rows,requested,body


def recovery_plan(allowed,parts,rows,requested,body,op):
    if len(allowed)!=len(set(allowed)) or not set(parts)<=set(allowed):raise ValueError('Exact unique rectangle and imported subset required')
    if op['maximum_ranges_per_request']!=5:raise ValueError('Predeclared five-range transport required')
    remaining=[r for r in allowed if r not in parts]
    batches=[remaining[i:i+5] for i in range(0,len(remaining),5)]
    if (len(rows)+len(batches)>op['maximum_http_requests'] or requested+sum(n for _,n in remaining)>op['maximum_requested_bytes'] or body+len(batches)*op['maximum_response_body_bytes']>op['maximum_total_response_body_bytes']):raise ValueError('Aggregate historical and future transport reservation exceeded')
    return batches


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen recovery input changed: '+f)
    old=json.loads((ROOT/op['geometry_operator_file']).read_bytes())
    axes=json.loads((ROOT/old['coordinates_file']).read_bytes())['coordinate_arrays'];header=json.loads((ROOT/old['header_file']).read_bytes())
    sections,patches,_,counts=rectangle_plan(axes,header,old);allowed=[r for patch in patches for r in patch['ranges']]
    parts,rows,requested,body=import_custody([json.loads((ROOT/f).read_bytes()) for f in op['prior_ledger_files']],json.loads((ROOT/op['prior_checkpoint_file']).read_bytes()),header)
    batches=recovery_plan(allowed,parts,rows,requested,body,op)
    reader=BoundedHttpRanges(header['source_object_url'],header['source_content_length'],header['source_last_modified'],allowed,op['maximum_http_requests'],op['maximum_requested_bytes'],op['maximum_response_body_bytes'],op['maximum_total_response_body_bytes'])
    reader.rows=rows;reader.requested_bytes=requested;reader.body_bytes=body;reader.completed=set(parts);reader.attempted=set(parts)
    out=Path('pacific-neuc-mean-resume-v3');out.mkdir(exist_ok=True);checkpoint=out/'completed-ranges';checkpoint.mkdir(exist_ok=True);files=[];diagnostics=[]
    counts={**counts,'legacy_geometry_planned_http_requests':counts['planned_http_requests'],'planned_http_requests':len(batches),'prior_http_requests':len(rows),'aggregate_planned_http_requests':len(rows)+len(batches),'imported_successful_ranges':len(parts)}
    print(json.dumps({'preflight_counts':counts,'prior_attempted_requested_bytes':requested,'prior_response_body_bytes':body}),flush=True)
    def save(name,value):
        raw=dumps(value);(out/name).write_bytes(raw);files.append({'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    save('imported-custody.json',{'schema':'osw.neuc-imported-custody.v1','input_sha256':{f:op['input_sha256'][f] for f in op['prior_ledger_files']+[op['prior_checkpoint_file']]},'successful_ranges':len(parts),'prior_http_requests':len(rows),'prior_attempted_requested_bytes':requested,'prior_response_body_bytes':body})
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
    save('manifest.json',{'schema':'osw.pacific-neuc-mean-resume.v3','status':'QUALIFIED_PROVIDER_MEAN_DIAGNOSTIC_IDENTITY_NOT_VALIDATED','entity_id':geometry['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'source_object_url':reader.url,'source_content_length':reader.length,'source_last_modified':reader.modified,'nominal_provider_period':geometry['nominal_provider_period'],'temporal_operator_class':geometry['temporal_operator_class'],'snapshot_time_utc':None,'counts':counts,'source_files':list(files),'section_diagnostics':diagnostics,'ocean_velocity_values_read':True,'averaging_semantics_validated':False,'provider_regional_bias_assessed':False,'current_identity_validated':False,'new_physical_depth_measurements':0,'regional_inventory_promotion_authorized':False,'runtime_changed':False,'full_goal_complete':False})
    print(json.dumps({'counts':counts,'section_selection_statuses':[d['horizontal_selection_status'] for d in diagnostics],'new_physical_depth_measurements':0,'inventory_promotion_authorized':False}),flush=True)


if __name__=='__main__':main()
