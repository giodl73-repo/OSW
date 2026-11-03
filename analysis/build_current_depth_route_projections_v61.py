"""Qualified mean field cross-sections,distinct from dated axis-proxy routes."""
import base64,copy,hashlib,json,math
from pathlib import Path
import west_australian_mean_corridor_v1 as source_method
from build_current_depth_route_projections_v12 import GEOD,paired_anchor,project
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,assemble,load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v61.json'
GENERATOR='analysis/build_current_depth_route_projections_v61.py'
INVENTORY='research/current-depth-route-projection-inventory-v47.json'
ADDENDUM='research/current-depth-route-projection-addenda/west-australian-qualified-mean-field-sections-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/west-australian-qualified-mean-field-sections-v1.csv'
FIELD_KIND='native_zonal_mean_field_section_not_along_current_axis'
METHOD='qualified_provider_mean_native_field_column0_500_north0p01_v1'


def audit_mean_fields(manifest,sections,ledger,sop,header,axes,prior,source_operator_sha):
    plans,counts=source_method.plan_sections(axes,header,sop,prior)
    context=source_method.mean_context(sop,axes)
    if manifest['schema']!='osw.west-australian-qualified-mean-corridor.v1' or manifest['counts']!=counts or manifest['operator_file']!=source_method.OPERATOR or manifest['operator_sha256']!=source_operator_sha or manifest['input_sha256']!=sop['input_sha256'] or manifest['source_mean_context']!=context or manifest['entity_id']!=sop['entity_id'] or manifest['regional_inventory_promotion_authorized'] or manifest['new_physical_depth_measurements']!=0 or manifest['runtime_changed'] or manifest['full_goal_complete']:raise ValueError('Qualified mean manifest changed')
    if (manifest['source_object_url'],manifest['source_content_length'],manifest['source_last_modified'])!=(header['source_object_url'],header['source_content_length'],header['source_last_modified']):raise ValueError('Mean manifest source identity changed')
    expected=[r for p in plans for c in p['components'].values() for r in c['ranges']]
    if (ledger['source_url'],ledger['source_bytes'],ledger['source_last_modified'])!=(header['source_object_url'],header['source_content_length'],header['source_last_modified']):raise ValueError('Wire custody source changed')
    if ledger['automatic_retries']!=0 or ledger['completed_ranges']!=len(expected) or len(ledger['requests'])!=len(expected) or ledger['allowed_ranges']!=len(expected):raise ValueError('Exact all-row custody required')
    if ledger['attempted_requested_bytes']!=counts['packed_component_bytes'] or ledger['response_body_bytes']!=counts['packed_component_bytes']:raise ValueError('Exact complete payload budget required')
    for key,opkey in [('maximum_requests','maximum_http_requests'),('maximum_requested_bytes','maximum_requested_bytes'),('maximum_response_body_bytes','maximum_response_body_bytes'),('maximum_total_response_body_bytes','maximum_total_response_body_bytes')]:
        if ledger[key]!=sop[opkey]:raise ValueError('Frozen transport budget changed')
    rows={}
    for (start,n),row in zip(expected,ledger['requests']):
        if row['status']!='success' or row['ranges']!=[[start,n]] or row['response_body_bytes']!=n or row['content_range']!='bytes '+str(start)+'-'+str(start+n-1)+'/'+str(header['source_content_length']) or len(row['parts'])!=1:raise ValueError('Single range/source ordering/custody changed')
        part=row['parts'][0]
        if (part['start'],part['length'])!=(start,n) or part['sha256']!=row['response_body_sha256']:raise ValueError('Exact row body hash required')
        rows[start,n]=part['sha256']
    if len(manifest['source_files'])!=len(plans) or set(sections)!={r['file'] for r in manifest['source_files']} or len({r['section_index'] for r in manifest['source_files']})!=len(plans):raise ValueError('All unique mean sections required')
    qualifying=0;resolved=0
    for meta,plan in zip(manifest['source_files'],plans):
        s=sections[meta['file']];si=meta['section_index'];components=plan['components'];np=len(plan['native_longitude_indices']);nz=len(axes['depth'])
        if si!=plans.index(plan) or s['section_index']!=si or s['schema']!='osw.west-australian-qualified-mean-section.v1' or s['entity_id']!=sop['entity_id'] or s['operator_file']!=manifest['operator_file'] or s['operator_sha256']!=source_operator_sha or s['input_sha256']!=sop['input_sha256']:raise ValueError('Mean section operator/schema/owner changed')
        if s['source_mean_context']!=context or s['depth_levels_m']!=axes['depth'] or s['component_bearing_degrees_true']!=0 or s['current_identity_validated'] or s['physical_current_depth_m'] is not None:raise ValueError('Mean/frame/depth/physical claim changed')
        if any(s[k]!=v for k,v in plan.items() if k!='components'):raise ValueError('Exact native section geometry changed')
        decoded={}
        for name,packing in components.items():
            c=s['components'][name];raw=base64.b64decode(c['packed_base64'],validate=True)
            if c['packing']!={k:v for k,v in packing.items() if k!='ranges'} or c['packed_shape']!=[nz,np] or c['packed_order']!='depth-major then native longitude' or len(raw)!=nz*np*2 or hashlib.sha256(raw).hexdigest()!=c['packed_sha256']:raise ValueError('Packed row shape/packing/hash changed')
            for iz,key in enumerate(packing['ranges']):
                if hashlib.sha256(raw[iz*np*2:(iz+1)*np*2]).hexdigest()!=rows[key]:raise ValueError('Packed bytes do not match exact source response')
            decoded[name]=source_method.decode_component(raw,nz,np,packing)
            if any(v is not None and (not math.isfinite(v) or abs(v)>10) for col in decoded[name] for v in col):raise ValueError('Standard velocity scaling/sanity guard')
        expected_columns=[{'profile_index':j,'native_longitude_index':ix,'sampled_lon_lat':[plan['native_longitudes_deg_e'][j],plan['sampled_latitude_deg_n']],'eastward_velocity_m_s':decoded['water_u'][j],'northward_velocity_m_s':decoded['water_v'][j],'signed_reference_component_m_s':decoded['water_v'][j]} for j,ix in enumerate(plan['native_longitude_indices'])]
        if s['columns']!=expected_columns:raise ValueError('Native decoded frame/column/position changed')
        diagnosis=source_method.corridor_diagnosis(axes['depth'],decoded['water_v'],sop)
        if s['diagnosis']!=diagnosis:raise ValueError('Source representative/corridor/layer diagnosis changed')
        expected_summary={'section_index':si,'selected_column_index':diagnosis['selected_column_index'],'horizontal_selection_status':diagnosis['horizontal_selection_status'],'qualifying_columns':len(diagnosis['qualifying_column_indices']),'qualifying_groups':len(diagnosis['qualifying_component_groups']),'selected_column_threshold_layers':diagnosis['selected_column_threshold_layers']}
        if manifest['section_diagnostics'][si]!=expected_summary:raise ValueError('Source summary changed')
        qualifying+=len(diagnosis['qualifying_column_indices'])
        resolved+=sum(l['lower_depth_m'] is not None for r in diagnosis['all_qualifying_column_layers'] for l in r['layers'] if l['threshold_m_s']==sop['primary_threshold_m_s'])
    return {'native_profiles_verified':counts['native_profiles'],'exact_source_rows_verified':len(expected),'packed_bytes_verified':counts['packed_component_bytes'],'qualifying_field_columns':qualifying,'resolved_qualifying_primary_depths':resolved,'source_representative_diagnoses_unchanged':True,'new_field_requests':0,'physical_current_identity_validated':False}


def project_mean_case(raw,op):
    if raw['snapshot_time_utc'] is not None:raise ValueError('Mean field cannot acquire a snapshot date')
    # Immutable numeric kernel uses this slot only to form an ID. A non-date
    # period key is internal;the output snapshot is always null.
    kernel_input=copy.deepcopy(raw);kernel_input['snapshot_time_utc']=raw['source_period_key']
    case=project(kernel_input,op);case.update(id=raw['mean_case_id'],snapshot_time_utc=None,status='QUALIFIED_PROVIDER_MEAN_FIELD_SECTION_NOT_CURRENT_ROUTE',metric='qualified_mean_velocity_field_lower_isotach_depth_and_model_layer_span',coordinate_kind='distance_along_sampled_native_zonal_section_not_current_length_or_width')
    for sample in case['samples']:
        sample.update(method_id=METHOD,comparison_group=case['comparison_group'],temporal_operator_class=case['temporal_operator_class'],nominal_provider_period=case['nominal_provider_period'],snapshot_is_applicable=False,field_geometry_kind=FIELD_KIND,axis_selection_applied=False,current_identity_independently_validated=False,source_section_geometry='latitude')
    return case


def field_cases(manifest,sections,source_directory,sop,op):
    supported=[];blocked=[]
    for meta in manifest['source_files']:
        s=sections[meta['file']];si=s['section_index'];source_file=source_directory+meta['file'];diagnosis=s['diagnosis'];layers={r['column_index']:r['layers'] for r in diagnosis['all_qualifying_column_layers']};anchors=[];distance=0.;previous=None
        for j,column in enumerate(s['columns']):
            point=column['sampled_lon_lat']
            if previous is not None:distance+=GEOD.inv(*previous,*point)[2]/1000
            previous=point;primary=next((r for r in layers.get(j,[]) if r['threshold_m_s']==sop['primary_threshold_m_s']),None);reasons=[]
            if not diagnosis['candidate_scores'][j]['eligible']:reasons.append('not_qualified_complete_positive_primary_mean_field_column')
            if primary is None or primary['lower_depth_m'] is None:reasons.append('primary_lower_isotach_unresolved_or_censored')
            eligible=not reasons;paired=eligible and primary['layer_thickness_m'] is not None
            anchors.append(paired_anchor('wac-mean-section'+str(si)+'-native'+str(column['native_longitude_index']),primary,eligible,paired,reasons,distance_km=round(distance,6),reference_lon_lat=point,selected_model_node_lon_lat=point,source_native_longitude_degrees_east=point[0],source_horizontal_selection_status='native_field_column_axis_selection_not_applied',source_profile_refs=[source_file+'#/columns/'+str(j)],source_model_profile_ref=source_file+'#/columns/'+str(j),source_connected_diagnosis_ref=source_file+'#/diagnosis/all_qualifying_column_layers/'+str(next((i for i,r in enumerate(diagnosis['all_qualifying_column_layers']) if r['column_index']==j),-1))+'/layers/'+str(layers[j].index(primary)) if primary else None,source_section_id='mean-section-'+str(si),source_profile_index=j,reference_geometry_is_unselected_gate_midpoint=False,axis_selection_applied=False,field_geometry_kind=FIELD_KIND))
        for anchor in anchors:anchor['source_component_bearing_degrees_true']=0
        raw={'entity_id':sop['entity_id'],'snapshot_time_utc':None,'source_period_key':'provider-mean-1994-2015-qualified','mean_case_id':'west-australian-qualified-mean-section-'+str(si)+'-v1','primary_threshold_m_s':sop['primary_threshold_m_s'],'anchors':anchors,'geometry_role':FIELD_KIND,'route_id':'west-australian-native-zonal-mean-section-'+str(si),'route_file':None,'source_time_basis':'Qualified provider native-mean-derived fixed-depth velocity,nominal1994-2015;actual weights/coverage/Eulerian equivalence unverified. Threshold of mean velocity is not mean instantaneous boundary depth. No snapshot/seasonal envelope.','projection_gate':op['field_point_eligibility_rule'],'source_component_reference_frame':'fixed_geographic_0degree_true_north_component_held_through_depth','selection_depth_interval_m':sop['selection_depth_interval_m'],'core_search_depth_interval_m':sop['core_search_depth_interval_m'],'source_surface_component_gate_m_s':None,'source_mean_context':s['source_mean_context'],'temporal_operator_class':sop['temporal_operator_class'],'nominal_provider_period':sop['nominal_provider_period'],'snapshot_is_applicable':False,'field_geometry_kind':FIELD_KIND,'axis_selection_applied':False,'method_id':METHOD,'comparison_group':'qualified_provider_mean_native_field_0_500_north0p01_1994_2015','current_identity_independently_validated':False,'water_mass_classification_performed':False,'source_section_geometry':'latitude','canonical_route_replaced':False,'canonical_route_extrapolation_performed':False,'reference_geometry_scope':FIELD_KIND,'source_representative_diagnosis_ref':source_file+'#/diagnosis','representative_axis_proxy_controls_field_point_eligibility':False,'cross_section_is_physical_current_width':False,'mean_is_mean_of_instantaneous_depths':False}
        case=project_mean_case(raw,op)
        if any(a['lower_projection_eligible'] for a in anchors):supported.append(case)
        else:case['status']='UNRESOLVED_QUALIFIED_MEAN_FIELD_SECTION';blocked.append(case)
    return supported,blocked


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen mean field input changed: '+f)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    previous=read(op['previous_inventory_file']);base,old_addenda=read_parts(previous,reader);load_inventory(previous,reader)
    manifest=read(op['source_manifest_file']);sections={r['file']:read(op['source_directory']+r['file']) for r in manifest['source_files']};sop=read(op['source_operator_file'])
    for meta in manifest['source_files']:
        raw=reader(op['source_directory']+meta['file'])
        if len(raw)!=meta['bytes'] or hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('Source section custody changed')
    audit=audit_mean_fields(manifest,sections,read(op['source_ledger_file']),sop,read(sop['header_file']),read(sop['coordinates_file'])['coordinate_arrays'],read(sop['prior_custody_ledger']),hashlib.sha256(reader(op['source_operator_file'])).hexdigest())
    projections,blocked=field_cases(manifest,sections,op['source_directory'],sop,op)
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'west-australian-qualified-mean-field-sections-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'projections':projections,'unresolved_reference_cases':blocked,'source_field_audit':audit,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=source_method.encoded(addendum);csv_raw=sample_csv_bytes(projections,reader(previous['base']['csv']['file']));pieces={ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest=copy.deepcopy(previous);manifest['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)});manifest['counts']=assemble(base,old_addenda+[addendum])['counts'];manifest['view_metadata'].update(schema='osw.current-depth-route-projections.v61',status='REGIONAL_PROFILES_AND_QUALIFIED_MEAN_FIELD_SECTIONS',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation']);pieces[INVENTORY]=encoded(manifest)
    if any(len(v)>=2500000 for v in pieces.values()):raise ValueError('Fixed per-file publication ceiling exceeded')
    result=load_inventory(manifest,lambda f:pieces[f] if f in pieces else reader(f));return manifest,addendum,pieces,result


def main():
    manifest,addendum,pieces,result=build();out=Path('current-depth-route-projections-v61');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':result['counts'],'source_field_audit':addendum['source_field_audit']}))


if __name__=='__main__':main()
