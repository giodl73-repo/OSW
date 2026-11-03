"""New current addendum using the frozen source-to-reference projection method."""
import math
from dwbc_abaco_depth_contexts_v1 import validate_contexts,context_config
import copy
import hashlib
import json
from pathlib import Path
from build_current_depth_route_projections_v18 import reference_placeholder,INTERIOR
from build_current_depth_route_projections_v12 import GEOD,paired_anchor,project
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,assemble,load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v54.json'
GENERATOR='analysis/build_current_depth_route_projections_v54.py'
INVENTORY='research/current-depth-route-projection-inventory-v40.json'
ADDENDUM='research/current-depth-route-projection-addenda/dwbc-abaco-multi-context-full-sections-hycom2022-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/dwbc-abaco-multi-context-full-sections-hycom2022-v1.csv'


def context_operator(op,key):
    if key not in ['upper','lower']:raise ValueError('Known predeclared vertical context required')
    active=copy.deepcopy(op);active['active_context_id']=key
    for entity,cfg in active['currents'].items():
        merged=context_config({**active['source_audit_config'],**cfg},key)
        active['currents'][entity]={**cfg,**{k:merged[k] for k in ['selection_depth_interval_m','core_search_depth_interval_m','primary_threshold_m_s']}}
    return active


def context_facts(manifest,chunks,op):
    if manifest['operator_file']!=op['source_operator_file'] or manifest['operator_sha256']!=op['input_sha256'][op['source_operator_file']]:raise ValueError('Raw source manifest operator changed')
    if len(manifest['sections'])!=len(op['section_files']) or len(chunks)!=len(op['section_files']):raise ValueError('Every original raw section required')
    expected={(e,t,s['id']) for e,c in op['currents'].items() for t in op['snapshot_times_utc'] for s in c['sections']}
    seen=set();descriptors=[];key=op['active_context_id']
    for index,entry in enumerate(manifest['sections']):
        file=op['source_section_directory']+entry['file']
        if file not in chunks or file not in op['input_sha256'] or op['source_manifest_index_by_file'].get(file)!=index:raise ValueError('Manifest file/order changed')
        d=chunks[file];entity=d['entity_id']
        identity=(entry['entity_id'],entry['snapshot_time_utc'],entry['section_id'])
        if identity in seen or identity not in expected or entity not in op['currents']:raise ValueError('Duplicate or changed raw owner/date/section')
        seen.add(identity);cfg=op['currents'][entity]
        if (entry['sha256']!=op['input_sha256'][file] or entry['entity_id']!=entity or entry['snapshot_time_utc']!=d['snapshot_time_utc'] or entry['section_id']!=d['section_definition']['id']
            or entry['source_section_geometry']!=d['source_section_geometry'] or entry['native_columns']!=len(d['columns']) or entry['context_diagnoses']!=d['context_diagnoses']):raise ValueError('Manifest context/source metadata changed')
        for field in ['selected_column_index','horizontal_selection_status','selected_column_threshold_layers']:
            if entry[field]!=d['diagnosis'][field]:raise ValueError('Manifest upper default changed')
        diagnosis=d['context_diagnoses'][key]['diagnosis'];selected=diagnosis['selected_column_index'];column=d['columns'][selected] if selected is not None else None
        layers=diagnosis['selected_column_threshold_layers'];primary=next((r for r in layers if r['threshold_m_s']==cfg['primary_threshold_m_s']),None)
        descriptors.append({'diagnostic_context_id':key,'manifest_index':index,'entity_id':entity,'snapshot_time_utc':d['snapshot_time_utc'],'section_id':entry['section_id'],
            'source_file':file,'source_sha256':entry['sha256'],'source_section_geometry':d['source_section_geometry'],'section_definition':d['section_definition'],
            'source_diagnosis_pointer':'/context_diagnoses/'+key+'/diagnosis','source_profile_pointer':'/columns/'+str(selected) if column else None,
            'selected_column_index':selected,'selected_lon_lat':column['sampled_lon_lat'] if column else None,'candidate_count':len(d['columns']),
            'component_bearing_degrees_true':d['component_bearing_degrees_true'],'horizontal_selection_status':diagnosis['horizontal_selection_status'],
            'local_integral_maximum_indices':diagnosis['local_integral_maximum_indices'],'selected_column_threshold_layers':layers,'primary_threshold_m_s':cfg['primary_threshold_m_s'],
            'primary_lower_depth_m':primary['lower_depth_m'] if primary else None,'primary_layer_thickness_m':primary['layer_thickness_m'] if primary else None,
            'selected_native100m_temperature_degrees_celsius':None,
            **{k:cfg[k] for k in ['parent_current_id','identity_relationship','parent_depth_values_inherited','selection_window_basis','identity_evidence_basis']}})
    if seen!=expected:raise ValueError('All original raw section/date identities required')
    return {'descriptors':descriptors}


def context_cases(manifest,chunks,op):
    supported=[];blocked=[]
    for key in ['upper','lower']:
        active=context_operator(op,key);facts=context_facts(manifest,chunks,active)
        added,unresolved=full_section_cases(facts,chunks,active);supported.extend(added);blocked.extend(unresolved)
    return supported,blocked


def full_section_cases(facts,chunks,op):
    for source in chunks.values():
        entity=source['entity_id']
        if (entity not in op['currents'] or source['schema']!='osw.multi-context-interval-depth-section.v1'
            or source['operator_file']!=op['source_operator_file']
            or source['operator_sha256']!=op['input_sha256'][op['source_operator_file']]):raise ValueError('Interval source operator/schema/owner changed')
        validate_contexts(source,{**op['source_audit_config'],**op['currents'][entity]})
    keyed={}
    for index,row in enumerate(facts['descriptors']):
        key=row['entity_id'],row['snapshot_time_utc'],row['section_id']
        if key in keyed:raise ValueError('Duplicate original current/date/section')
        keyed[key]=index,row
    expected={(entity,t,s['id']) for entity,c in op['currents'].items() for t in op['snapshot_times_utc'] for s in c['sections']}
    if set(keyed)!=expected:raise ValueError('All declared source section/date cases required')
    supported=[];blocked=[]
    for entity,config in op['currents'].items():
        for stamp in op['snapshot_times_utc']:
            anchors=[];distance=0.;previous=None
            for definition in config['sections']:
                index,row=keyed[entity,stamp,definition['id']];source=chunks[row['source_file']];diagnosis=source['context_diagnoses'][op['active_context_id']]['diagnosis']
                selected=row['selected_column_index'];profile=source['columns'][selected] if selected is not None else None
                if (source['entity_id']!=entity or source['snapshot_time_utc']!=stamp or source['source_returned_timestamp_utc']!=stamp
                    or source['section_definition']!=definition or row['section_definition']!=definition
                    or source['component_bearing_degrees_true']!=config['component_bearing_degrees_true']
                    or row['component_bearing_degrees_true']!=config['component_bearing_degrees_true']
                    or row['source_section_geometry']!=source['source_section_geometry']
                    or row['identity_evidence_basis']!=config['identity_evidence_basis']
                    or row['selection_window_basis']!=config['selection_window_basis']
                    or any(row[k]!=config[k] for k in ['parent_current_id','identity_relationship','parent_depth_values_inherited'])
                    or row['source_sha256']!=op['input_sha256'][row['source_file']]
                    or row['primary_threshold_m_s']!=config['primary_threshold_m_s']
                    or row['candidate_count']!=len(source['columns'])
                    or diagnosis['selected_column_index']!=selected
                    or row['horizontal_selection_status']!=diagnosis['horizontal_selection_status']
                    or row['selected_column_threshold_layers']!=diagnosis['selected_column_threshold_layers']):raise ValueError('Source identity, section, frame or selection changed')
                if row['source_diagnosis_pointer']!='/context_diagnoses/'+op['active_context_id']+'/diagnosis' or row['diagnostic_context_id']!=op['active_context_id'] or row['manifest_index']!=op['source_manifest_index_by_file'][row['source_file']]:raise ValueError('Context diagnosis/manifest pointer changed')
                layers=row['selected_column_threshold_layers'];matches=[r for r in layers if r['threshold_m_s']==config['primary_threshold_m_s']]
                if profile is not None:
                    if row['source_profile_pointer']!='/columns/'+str(selected) or row['selected_lon_lat']!=profile['sampled_lon_lat'] or len(matches)!=1:raise ValueError('Primary layer, profile pointer or position changed')
                    layer=matches[0]
                    temperatures=source['native100m_temperature_degrees_celsius']
                    actual_temperature=temperatures[selected] if temperatures is not None else None
                    if row['selected_native100m_temperature_degrees_celsius']!=actual_temperature:raise ValueError('Selected model temperature changed')
                    if config['temperature_gate'] is not None and (actual_temperature is None or actual_temperature>config['temperature_gate']['maximum_temperature_degrees_celsius']):raise ValueError('Selected model temperature gate not met')
                    if layer['lower_depth_m']!=row['primary_lower_depth_m'] or layer['layer_thickness_m']!=row['primary_layer_thickness_m']:raise ValueError('Primary source depth changed')
                    point=profile['sampled_lon_lat'];geometry_placeholder=False
                else:
                    if matches or layers or row['source_profile_pointer'] is not None or row['selected_lon_lat'] is not None or row['primary_lower_depth_m'] is not None:raise ValueError('Invented selected profile in unresolved source section')
                    layer=None;point=reference_placeholder(source,definition);geometry_placeholder=True
                if previous is not None:
                    metres=GEOD.inv(*previous,*point)[2]
                    if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct finite original section positions required')
                    distance+=metres/1000
                previous=point;reasons=[]
                if profile is None:reasons.append('no_qualifying_source_column_reference_gate_midpoint_only')
                if row['horizontal_selection_status']!=INTERIOR:reasons.append('section_axis_proxy_not_interior_bracketed')
                if layer is None or layer['lower_depth_m'] is None:reasons.append('primary_lower_boundary_censored_or_unresolved')
                lower=not reasons;span=lower and layer['layer_thickness_m'] is not None
                anchors.append(paired_anchor(entity.split(':')[1]+'-dwbc-abaco-multi-context'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'-'+stamp[:10]+'-'+definition['id'],layer,lower,span,reasons,
                    source_section_id=definition['id'],source_diagnostic_context_id=op['active_context_id'],distance_km=round(distance,6),reference_lon_lat=point,
                    reference_geometry_is_unselected_gate_midpoint=geometry_placeholder,
                    selected_model_node_lon_lat=profile['sampled_lon_lat'] if profile else None,
                    source_component_bearing_degrees_true=config['component_bearing_degrees_true'],
                    source_horizontal_selection_status=row['horizontal_selection_status'],
                    source_profile_refs=[op['source_manifest_file']+'#/sections/'+str(row['manifest_index'])+'/context_diagnoses/'+op['active_context_id']],
                    source_model_profile_ref=row['source_file']+'#'+row['source_profile_pointer'] if profile else None,
                    source_connected_diagnosis_ref=row['source_file']+'#/context_diagnoses/'+op['active_context_id']+'/diagnosis/selected_column_threshold_layers/'+str(layers.index(layer)) if layer else None,
                    source_section_definition=definition,source_candidate_count=row['candidate_count'],
                    source_local_integral_maximum_indices=row['local_integral_maximum_indices'],
                    source_selected_native100m_temperature_degrees_celsius=row['selected_native100m_temperature_degrees_celsius']))
            raw={'diagnostic_context_id':op['active_context_id'],'vertical_contexts_are_additive':False,'contexts_are_independent_observations':False,'entity_id':entity,'snapshot_time_utc':stamp,'primary_threshold_m_s':config['primary_threshold_m_s'],'anchors':anchors,
                'geometry_role':'regional_reference_connector_between_selected_model_columns_with_explicit_unselected_gate_midpoint_placeholders',
                'route_id':entity.split(':')[1]+'-full-section-reference-'+op['active_context_id']+'-'+stamp[:10],'route_file':None,
                'source_time_basis':'HYCOM instantaneous March/June/September/December15,2022 00Z;quarterly probes,not seasonal means or annual envelopes.',
                'projection_gate':'Interior maximum of complete finite declared current-specific signed interval without surface qualification;resolved declared primary lower contour;axis identity remains unvalidated.',
                'selection_depth_interval_m':config['selection_depth_interval_m'],'core_search_depth_interval_m':config['core_search_depth_interval_m'],'source_surface_component_gate_m_s':None,
                'parent_current_id':config['parent_current_id'],'identity_relationship':config['identity_relationship'],'parent_depth_values_inherited':config['parent_depth_values_inherited'],'selection_window_basis':config['selection_window_basis'],'identity_evidence_basis':config['identity_evidence_basis'],'current_identity_independently_validated':False,'source_section_geometry':config['sections'][0]['fixed_axis'],'water_mass_classification_performed':False,'canonical_route_replaced':False,'canonical_route_extrapolation_performed':False,'reference_geometry_scope':'independent_regional_connector_between_original_sections',
                'method_id':'interval_'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'-primary'+str(config['primary_threshold_m_s']).replace('.','p')+'-no-surface-gate-v1','comparison_group':'model_interval_'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'_primary'+str(config['primary_threshold_m_s']).replace('.','p')+'_no_surface_gate',
                'source_component_reference_frame':'fixed_geographic_'+str(config['component_bearing_degrees_true'])+'degree_true_held_through_depth',
                'branch_scope':config['branch_scope'],'temperature_gate':config['temperature_gate']}
            case=project(raw,op);case['id']=entity.split(':')[1]+'-dwbc-abaco-multi-context'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'-'+stamp[:10]+'-component'+str(config['component_bearing_degrees_true'])+'-v1'
            for sample in case['samples']:sample.update(diagnostic_context_id=op['active_context_id'],vertical_contexts_are_additive=False,contexts_are_independent_observations=False,method_id=case['method_id'],comparison_group=case['comparison_group'],parent_current_id=config['parent_current_id'],identity_relationship=config['identity_relationship'],parent_depth_values_inherited=config['parent_depth_values_inherited'],selection_window_basis=config['selection_window_basis'],identity_evidence_basis=config['identity_evidence_basis'],current_identity_independently_validated=False,source_section_geometry=config['sections'][0]['fixed_axis'],water_mass_classification_performed=False)
            if any(a['lower_projection_eligible'] for a in anchors):supported.append(case)
            else:
                case['status']='UNRESOLVED_REGIONAL_REFERENCE_CASE_NO_SUPPORTED_PRIMARY_DEPTH'
                blocked.append(case)
    return supported,blocked



def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OPERATOR)
    for p,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=pin:raise ValueError('Frozen source changed: '+p)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    previous=read(op['previous_inventory_file']);base,prior_addenda=read_parts(previous,reader)
    load_inventory(previous,reader)
    projections,blocked=context_cases(read(op['source_manifest_file']),{p:read(p) for p in op['section_files']},op)
    for case in projections+blocked:case['source_surface_component_gate_m_s']=op['currents'][case['entity_id']]['surface_component_gate_m_s']
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'dwbc-abaco-multi-context-full-sections-hycom2022-v1',
        'base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),
        'input_sha256':op['input_sha256'],'projections':projections,'unresolved_reference_cases':blocked,
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=encoded(addendum);csv_raw=sample_csv_bytes(projections,reader(previous['base']['csv']['file']))
    pieces={ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest=copy.deepcopy(previous);manifest['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)})
    manifest['counts']=assemble(base,prior_addenda+[addendum])['counts']
    manifest['view_metadata'].update(schema='osw.current-depth-route-projections.v54',status='REGIONAL_DEPTH_BASE_PLUS_PINNED_CURRENT_ADDENDA',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces[INVENTORY]=encoded(manifest)
    result=load_inventory(manifest,lambda p:pieces[p] if p in pieces else reader(p))
    return manifest,addendum,pieces,result


def main():
    manifest,addendum,pieces,result=build();out=Path('current-depth-route-projections-v54');out.mkdir(exist_ok=True)
    for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]:
        if len(pieces[path])>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
        (out/name).write_bytes(pieces[path])
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
