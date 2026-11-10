"""Qualified NEUC meridional mean-field sections with detached-layer gates."""
import base64,copy,hashlib,json,math,re
from pathlib import Path
import pacific_neuc_mean_resume_v4 as source_method
from pacific_neuc_mean_resume_v3 import import_custody,recovery_plan
from pacific_neuc_mean_rectangle_v2 import rectangle_plan,extract_section_raw
from pacific_neuc_mean_sections_v1 import decode_component,section_diagnostic
from derive_eac_connected_layer_thickness_v1 import connected_layer
from build_current_depth_route_projections_v12 import GEOD,paired_anchor,project
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,assemble,load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v62.json'
GENERATOR='analysis/build_current_depth_route_projections_v62.py'
INVENTORY='research/current-depth-route-projection-inventory-v48.json'
ADDENDUM='research/current-depth-route-projection-addenda/pacific-neuc-qualified-mean-field-sections-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/pacific-neuc-qualified-mean-field-sections-v1.csv'
REPORT='research/pacific-neuc-mean-native-column-layers-v1.json'
FIELD_KIND='native_meridional_mean_field_section_not_along_current_axis'
METHOD='qualified_provider_mean_native_meridional_east300_1500_detached_southern_context0p02_v1'


def mean_context(geometry):
    return {'snapshot_time_utc':None,'snapshot_is_applicable':False,'nominal_provider_period':geometry['nominal_provider_period'],'temporal_operator_class':geometry['temporal_operator_class'],'actual_averaging_coverage_verified':False,'averaging_weights_verified':False,'fixed_depth_Eulerian_mean_equivalence_verified':False,'seasonal_mean_or_annual_extrema_established':False,'mean_is_mean_of_instantaneous_depths':False,'provider_regional_bias_assessed':False}


def audit_fields(manifest,sections,rectangles,ledger,sop,geometry,header,axes,prior_ledger,seed,bundle,imported,source_operator_sha):
    plans,patches,_,counts=rectangle_plan(axes,header,geometry);allowed=[r for patch in patches for r in patch['ranges']]
    checkpoint=source_method.restore_checkpoint_bundle(bundle,seed)
    oldparts,oldrows,oldrequested,oldbody=import_custody([prior_ledger],checkpoint,header)
    batches=recovery_plan(allowed,oldparts,oldrows,oldrequested,oldbody,sop)
    counts={**counts,'legacy_geometry_planned_http_requests':counts['planned_http_requests'],'planned_http_requests':len(batches),'prior_http_requests':len(oldrows),'aggregate_planned_http_requests':len(oldrows)+len(batches),'imported_successful_ranges':len(oldparts)}
    if manifest['schema']!='osw.pacific-neuc-mean-resume.v4' or manifest['counts']!=counts or manifest['operator_file']!=source_method.OPERATOR or manifest['operator_sha256']!=source_operator_sha or manifest['input_sha256']!=sop['input_sha256'] or manifest['entity_id']!=geometry['entity_id']:raise ValueError('Frozen mean manifest/operator/counts changed')
    if manifest['snapshot_time_utc'] is not None or manifest['nominal_provider_period']!=geometry['nominal_provider_period'] or manifest['temporal_operator_class']!=geometry['temporal_operator_class'] or any(manifest[k] for k in ['averaging_semantics_validated','provider_regional_bias_assessed','current_identity_validated','regional_inventory_promotion_authorized','runtime_changed','full_goal_complete']) or manifest['new_physical_depth_measurements']!=0:raise ValueError('Qualified mean cannot acquire time/physical claims')
    identity=(header['source_object_url'],header['source_content_length'],header['source_last_modified'])
    if (manifest['source_object_url'],manifest['source_content_length'],manifest['source_last_modified'])!=identity or (ledger['source_url'],ledger['source_bytes'],ledger['source_last_modified'])!=identity:raise ValueError('Exact mean source identity required')
    if ledger['automatic_retries']!=0 or ledger['allowed_ranges']!=len(allowed) or ledger['completed_ranges']!=len(allowed) or len(ledger['requests'])!=len(oldrows)+len(batches) or ledger['requests'][:len(oldrows)]!=oldrows:raise ValueError('Aggregate history and complete exact-row custody required')
    for key,opkey in [('maximum_requests','maximum_http_requests'),('maximum_requested_bytes','maximum_requested_bytes'),('maximum_response_body_bytes','maximum_response_body_bytes'),('maximum_total_response_body_bytes','maximum_total_response_body_bytes')]:
        if ledger[key]!=sop[opkey]:raise ValueError('Frozen aggregate transport ceiling changed')
    if ledger['attempted_requested_bytes']!=oldrequested+sum(n for b in batches for _,n in b) or ledger['response_body_bytes']!=sum(r.get('response_body_bytes',0) for r in ledger['requests']) or ledger['response_body_bytes']>sop['maximum_total_response_body_bytes']:raise ValueError('Aggregate bytes including failures must reconcile')
    expected_import={'schema':'osw.neuc-imported-custody.v1','input_sha256':{f:sop['input_sha256'][f] for f in sop['prior_ledger_files']+[sop['prior_checkpoint_file'],sop['prior_checkpoint_bundle_file']]},'successful_ranges':len(oldparts),'prior_http_requests':len(oldrows),'prior_attempted_requested_bytes':oldrequested,'prior_response_body_bytes':oldbody}
    if imported!=expected_import:raise ValueError('Imported custody changed')
    hashes={key:hashlib.sha256(raw).hexdigest() for key,raw in oldparts.items()}
    for batch,row in zip(batches,ledger['requests'][len(oldrows):]):
        if row['status']!='success' or row['ranges']!=[list(x) for x in sorted(batch)] or not sum(n for _,n in batch)<=row['response_body_bytes']<=sop['maximum_response_body_bytes'] or not re.fullmatch('[a-f0-9]{64}',row['response_body_sha256']):raise ValueError('Exact residual request order/body custody changed')
        if len(batch)>1 and (not row['content_type'].lower().startswith('multipart/byteranges;') or row['content_range'] is not None):raise ValueError('Exact multipart request required')
        if len(row['parts'])!=len(batch) or {(r['start'],r['length']) for r in row['parts']}!=set(batch):raise ValueError('All and only requested parts required')
        for part in row['parts']:
            key=(part['start'],part['length'])
            if key in hashes or not re.fullmatch('[a-f0-9]{64}',part['sha256']):raise ValueError('Successful replay or invalid part hash')
            hashes[key]=part['sha256']
    if set(hashes)!=set(allowed):raise ValueError('Every exact rectangle row required')
    rows={};fullbytes=0
    for name in ['water_u','water_v']:
        value=rectangles[name];packing=plans[0]['components'][name];raw=base64.b64decode(value['packed_base64'],validate=True)
        ordered=[r for patch in patches if patch['component']==name for r in patch['ranges']];width=len(counts['native_longitudes_deg_e']);ny=len(counts['native_latitude_indices']);nz=len(axes['depth'])
        if value['schema']!='osw.pacific-neuc-packed-rectangle.v2' or value['component']!=name or value['rectangle_counts']!=counts or value['native_latitudes_deg_n']!=plans[0]['native_latitudes_deg_n'] or value['depth_levels_m']!=axes['depth'] or value['packing']!={k:v for k,v in packing.items() if k!='ranges'} or value['packed_shape']!=[nz,ny,width] or value['packed_order']!='ascending depth,latitude,longitude' or len(raw)!=sum(n for _,n in ordered) or hashlib.sha256(raw).hexdigest()!=value['packed_sha256']:raise ValueError('Exact packed rectangle shape/coordinates/packing/hash required')
        offset=0
        for key in ordered:
            row=raw[offset:offset+key[1]];offset+=key[1]
            if hashlib.sha256(row).hexdigest()!=hashes[key] or (key in oldparts and row!=oldparts[key]):raise ValueError('Packed rectangle differs from acquired row custody')
            rows[key]=row
        decoded=decode_component(raw,nz,ny*width,packing)
        if any(v is not None and (not math.isfinite(v) or abs(v)>10) for column in decoded for v in column):raise ValueError('Standard full-field velocity scaling/sanity guard')
        fullbytes+=len(raw)
    if set(sections)!={'section-%02d.json'%i for i in range(len(plans))}:raise ValueError('All four unique sections required')
    derived=[]
    for si,plan in enumerate(plans):
        section=sections['section-%02d.json'%si]
        if section['schema']!='osw.pacific-neuc-mean-section.v1' or section['section_index']!=si or any(section[k]!=v for k,v in plan.items() if k!='components') or section['depth_levels_m']!=axes['depth'] or section['snapshot_time_utc'] is not None or section['current_identity_validated'] or section['physical_current_depth_m'] is not None:raise ValueError('Native meridional section geometry/mean/physical claims changed')
        decoded={}
        for name,packing in plan['components'].items():
            c=section['components'][name];raw=base64.b64decode(c['packed_base64'],validate=True);np=len(plan['native_latitude_indices']);nz=len(axes['depth'])
            if c['packing']!={k:v for k,v in packing.items() if k!='ranges'} or c['packed_shape']!=[nz,np] or c['packed_order']!='depth-major then ascending native latitude at one native longitude' or raw!=extract_section_raw(rows,plan,counts,axes,name) or hashlib.sha256(raw).hexdigest()!=c['packed_sha256']:raise ValueError('Section bytes/packing/exact rectangle extraction changed')
            decoded[name]=decode_component(raw,nz,np,packing)
            if c['profiles_m_s']!=decoded[name]:raise ValueError('CF decoded native profiles changed')
        diagnosis=section_diagnostic(axes['depth'],decoded['water_u'],plan['native_latitudes_deg_n'],geometry)
        if section['diagnostic']!=diagnosis or manifest['section_diagnostics'][si]!={'section_index':si,**diagnosis}:raise ValueError('Original source representative diagnosis changed')
        all_layers=[{'column_index':j,'layers':[connected_layer(axes['depth'],decoded['water_u'][j],threshold,geometry['core_search_depth_interval_m']) for threshold in geometry['thresholds_m_s']]} for j,c in enumerate(diagnosis['candidate_scores']) if c['eligible']]
        derived.append({'section_index':si,'candidate_scores':diagnosis['candidate_scores'],'all_qualifying_column_layers':all_layers,'source_representative_diagnosis_unchanged':True,'snapshot_time_utc':None})
    return {'exact_source_rows_verified':len(allowed),'historical_attempts_preserved':len(oldrows),'aggregate_http_attempts':len(ledger['requests']),'packed_bytes_verified':fullbytes,'native_rectangle_profiles_verified':counts['native_profiles_in_rectangle'],'native_profiles_verified':sum(len(s['native_latitude_indices']) for s in plans),'source_representative_diagnoses_unchanged':True,'new_field_requests':0,'physical_current_identity_validated':False},derived


def project_mean_case(raw,op):
    if raw['snapshot_time_utc'] is not None:raise ValueError('Qualified mean has no snapshot date')
    kernel=copy.deepcopy(raw);kernel['snapshot_time_utc']=raw['source_period_key'];case=project(kernel,op)
    case.update(id=raw['mean_case_id'],snapshot_time_utc=None,status='QUALIFIED_PROVIDER_MEAN_MERIDIONAL_UNDERCURRENT_CONTEXT_FIELD_SECTION',metric='qualified_mean_detached_velocity_field_lower_isotach_depth_and_model_layer_span',coordinate_kind='distance_along_sampled_native_meridional_section_not_current_length_or_width')
    for sample in case['samples']:sample.update(method_id=METHOD,comparison_group=case['comparison_group'],temporal_operator_class=case['temporal_operator_class'],nominal_provider_period=case['nominal_provider_period'],snapshot_is_applicable=False,field_geometry_kind=FIELD_KIND,axis_selection_applied=False,current_identity_independently_validated=False,source_section_geometry='longitude',primary_detached_layer_required=True,independent_latitude_context_required=True)
    return case


def field_cases(sections,derived,directory,geometry,op):
    supported=[];blocked=[];low,high=geometry['independent_southern_jet_latitude_context_deg_n']
    for si,d in enumerate(derived):
        s=sections['section-%02d.json'%si];source_file=directory+'section-%02d.json'%si;layers={r['column_index']:r['layers'] for r in d['all_qualifying_column_layers']};anchors=[];distance=0.;previous=None
        for j,lat in enumerate(s['native_latitudes_deg_n']):
            point=[s['sampled_longitude_deg_e'],lat]
            if previous is not None:distance+=GEOD.inv(*previous,*point)[2]/1000
            previous=point;primary=next((x for x in layers.get(j,[]) if x['threshold_m_s']==geometry['primary_threshold_m_s']),None);reasons=[]
            if not d['candidate_scores'][j]['eligible']:reasons.append('not_qualified_complete_positive_primary_mean_field_column')
            if not low<=lat<=high:reasons.append('outside_independent_southern_jet_latitude_context')
            if primary is None or primary['upper_status']!='adjacent_isotach_crossing' or primary['upper_depth_m'] is None or primary['upper_depth_m']<=0:reasons.append('primary_layer_not_resolved_detached_below_surface')
            if primary is None or primary['lower_depth_m'] is None:reasons.append('primary_lower_isotach_unresolved_or_censored')
            eligible=not reasons;paired=eligible and primary['layer_thickness_m'] is not None;profile_ref=source_file+'#/components/water_u/profiles_m_s/'+str(j)
            layer_ref=REPORT+'#/sections/'+str(si)+'/all_qualifying_column_layers/'+str(next((i for i,r in enumerate(d['all_qualifying_column_layers']) if r['column_index']==j),-1))+'/layers/'+str(layers[j].index(primary)) if primary else None
            anchors.append(paired_anchor('neuc-mean-section'+str(si)+'-native'+str(s['native_latitude_indices'][j]),primary,eligible,paired,reasons,distance_km=round(distance,6),reference_lon_lat=point,selected_model_node_lon_lat=point,source_native_latitude_degrees_north=lat,source_horizontal_selection_status='native_field_column_axis_selection_not_applied',source_profile_refs=[profile_ref],source_model_profile_ref=profile_ref,source_connected_diagnosis_ref=layer_ref,source_section_id='mean-section-'+str(si),source_profile_index=j,reference_geometry_is_unselected_gate_midpoint=False,axis_selection_applied=False,field_geometry_kind=FIELD_KIND,source_component_bearing_degrees_true=90,primary_detached_layer_required=True,independent_latitude_context_required=True))
        raw={'entity_id':geometry['entity_id'],'snapshot_time_utc':None,'source_period_key':'provider-mean-1994-2015-qualified','mean_case_id':'pacific-neuc-qualified-mean-section-'+str(si)+'-v1','primary_threshold_m_s':geometry['primary_threshold_m_s'],'anchors':anchors,'geometry_role':FIELD_KIND,'route_id':'pacific-neuc-native-meridional-mean-section-'+str(si),'route_file':None,'source_time_basis':'Qualified provider native-mean-derived fixed-depth velocity,nominal1994-2015;actual weights/coverage/Eulerian equivalence unverified. Threshold of mean velocity is not mean instantaneous boundary depth. No snapshot/seasonal envelope.','projection_gate':op['field_point_eligibility_rule'],'source_component_reference_frame':'fixed_geographic_90degree_true_east_component_held_through_depth','selection_depth_interval_m':geometry['selection_depth_interval_m'],'core_search_depth_interval_m':geometry['core_search_depth_interval_m'],'source_surface_component_gate_m_s':None,'source_mean_context':mean_context(geometry),'temporal_operator_class':geometry['temporal_operator_class'],'nominal_provider_period':geometry['nominal_provider_period'],'snapshot_is_applicable':False,'field_geometry_kind':FIELD_KIND,'axis_selection_applied':False,'method_id':METHOD,'comparison_group':'qualified_provider_mean_native_meridional_east300_1500_detached_southern_context0p02_1994_2015','current_identity_independently_validated':False,'water_mass_classification_performed':False,'source_section_geometry':'longitude','canonical_route_replaced':False,'canonical_route_extrapolation_performed':False,'reference_geometry_scope':FIELD_KIND,'source_representative_diagnosis_ref':source_file+'#/diagnostic','representative_axis_proxy_controls_field_point_eligibility':False,'cross_section_is_physical_current_width':False,'mean_is_mean_of_instantaneous_depths':False,'primary_detached_layer_required':True,'independent_latitude_context_required':True,'independent_latitude_context_deg_n':[low,high]}
        case=project_mean_case(raw,op)
        if any(a['lower_projection_eligible'] for a in anchors):supported.append(case)
        else:case['status']='UNRESOLVED_QUALIFIED_MEAN_UNDERCURRENT_CONTEXT_FIELD_SECTION';blocked.append(case)
    return supported,blocked


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen meridional mean input changed: '+f)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    previous=read(op['previous_inventory_file']);base,old_addenda=read_parts(previous,reader);load_inventory(previous,reader)
    manifest=read(op['source_manifest_file']);sop=read(op['source_operator_file']);geometry=read(sop['geometry_operator_file']);directory=op['source_directory']
    if len(manifest['source_files'])!=7 or len(manifest['section_diagnostics'])!=4 or {m['file'] for m in manifest['source_files']}!={'imported-custody.json','rectangle-water_u.json','rectangle-water_v.json',*('section-%02d.json'%i for i in range(4))}:raise ValueError('Exact source file set required')
    for meta in manifest['source_files']:
        raw=reader(directory+meta['file'])
        if len(raw)!=meta['bytes'] or hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('Retained source bytes changed')
    sections={'section-%02d.json'%i:read(directory+'section-%02d.json'%i) for i in range(4)}
    audit,derived=audit_fields(manifest,sections,{n:read(directory+'rectangle-'+n+'.json') for n in ['water_u','water_v']},read(op['source_ledger_file']),sop,geometry,read(geometry['header_file']),read(geometry['coordinates_file'])['coordinate_arrays'],read(sop['prior_ledger_files'][0]),read(sop['prior_checkpoint_file']),read(sop['prior_checkpoint_bundle_file']),read(directory+'imported-custody.json'),hashlib.sha256(reader(op['source_operator_file'])).hexdigest())
    report={'schema':'osw.pacific-neuc-mean-native-column-layers.v1','operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'source_field_audit':audit,'source_mean_context':mean_context(geometry),'sections':derived,'current_identity_validated':False,'physical_current_depth_m':None,'new_field_requests':0};report_raw=(json.dumps(report,separators=(',',':'),allow_nan=False)+'\n').encode()
    projections,blocked=field_cases(sections,derived,directory,geometry,op)
    piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'pacific-neuc-qualified-mean-field-sections-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'projections':projections,'unresolved_reference_cases':blocked,'source_field_audit':audit,'derived_source_report':piece(REPORT,report_raw),'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=(json.dumps(addendum,separators=(',',':'),allow_nan=False)+'\n').encode();csv_raw=sample_csv_bytes(projections,reader(previous['base']['csv']['file']));pieces={ADDENDUM:add_raw,SAMPLES_CSV:csv_raw,REPORT:report_raw}
    inventory=copy.deepcopy(previous);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)});inventory['counts']=assemble(base,old_addenda+[addendum])['counts'];inventory['view_metadata'].update(schema='osw.current-depth-route-projections.v62',status='REGIONAL_PROFILES_AND_QUALIFIED_MEAN_FIELD_SECTIONS',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation']);pieces[INVENTORY]=encoded(inventory)
    if any(len(raw)>=2500000 for raw in pieces.values()):raise ValueError('Fixed per-file publication ceiling exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f));return inventory,addendum,pieces,view


def main():
    inventory,addendum,pieces,view=build();out=Path('current-depth-route-projections-v62');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv'),(REPORT,'column-layers.json')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'source_field_audit':addendum['source_field_audit'],'supported_new_cases':len(addendum['projections']),'blocked_new_cases':len(addendum['unresolved_reference_cases'])}))


if __name__=='__main__':main()
