"""South Java opposing component reference profiles from verified native sections."""
import copy,hashlib,json,math
from pathlib import Path
from south_java_direction_depth_contexts_v1 import TARGET,context_config,validate_contexts
from build_current_depth_route_projections_v18 import reference_placeholder,INTERIOR
from build_current_depth_route_projections_v12 import GEOD,paired_anchor,project
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,assemble,load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v52.json'
GENERATOR='analysis/build_current_depth_route_projections_v52.py'
INVENTORY='research/current-depth-route-projection-inventory-v38.json'
ADDENDUM='research/current-depth-route-projection-addenda/south-java-direction-hycom2022-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/south-java-direction-hycom2022-v1.csv'


def checked_sources(manifest,chunks,sourceop,op):
    if manifest['schema']!='osw.native-direction-context-depth-sections-manifest.v1' or manifest['operator_file']!=op['source_operator_file'] or manifest['operator_sha256']!=op['input_sha256'][op['source_operator_file']] or manifest['input_sha256']!=sourceop['input_sha256']:raise ValueError('Native manifest provenance changed')
    expected={(t,s['id']) for t in sourceop['snapshot_times_utc'] for s in sourceop['sections']};lookup={}
    if len(manifest['sections'])!=16 or len(chunks)!=16:raise ValueError('All16native source sections required')
    cfg={**sourceop,**sourceop['currents'][TARGET]}
    for index,e in enumerate(manifest['sections']):
        file=op['source_section_directory']+e['file']
        if file not in chunks or op['source_manifest_index_by_file'].get(file)!=index or e['sha256']!=op['input_sha256'][file]:raise ValueError('Source file/order/hash changed')
        d=chunks[file];identity=(e['snapshot_time_utc'],e['section_id'])
        if identity not in expected or identity in lookup:raise ValueError('Duplicate/changed source identity')
        if (d['entity_id']!=TARGET or e['entity_id']!=TARGET or d['operator_file']!=op['source_operator_file']
            or d['operator_sha256']!=manifest['operator_sha256'] or d['input_sha256']!=sourceop['input_sha256']
            or d['snapshot_time_utc']!=e['snapshot_time_utc'] or d['source_returned_timestamp_utc']!=d['snapshot_time_utc']
            or d['source_section_geometry']!=e['source_section_geometry'] or d['source_section_geometry']!='longitude'
            or d['section_definition']!=next(s for s in sourceop['sections'] if s['id']==e['section_id'])
            or len(d['columns'])!=e['native_columns']):raise ValueError('Native owner,time,geometry or provenance changed')
        if (d['eligibility']!=sourceop['eligibility'] or any(d['eligibility'].values()) or d['additional_direction_field_requests']!=0
            or any(d[k] is not False for k in ['surface_undercurrent_separation_performed','direction_contexts_are_additive','contexts_are_independent_observations','water_mass_classification_performed','width_or_volume_join_performed'])):raise ValueError('No physical/independent observation promotion')
        validate_contexts(d,cfg)
        for k in ['selected_column_index','horizontal_selection_status','selected_column_threshold_layers']:
            if e[k]!=d['diagnosis'][k]:raise ValueError('Default eastward manifest diagnosis changed')
        for key,c in d['direction_contexts'].items():
            if {k:v for k,v in c.items() if k!='profiles'}!=e['direction_contexts'][key]:raise ValueError('Manifest direction context changed')
        lookup[identity]=(index,file,e,d,d)
    if set(lookup)!=expected:raise ValueError('All original section/date pairs required')
    return lookup


def direction_case(stamp,key,lookup,sourceop,op):
    cfg=context_config({**sourceop,**sourceop['currents'][TARGET]},key);bearing=cfg['component_bearing_degrees_true'];anchors=[];distance=0.;previous=None
    for definition in sourceop['sections']:
        index,file,e,d,raw=lookup[stamp,definition['id']];context=d['direction_contexts'][key];diagnosis=context['diagnosis'];selected=diagnosis['selected_column_index']
        profile=context['profiles'][selected] if selected is not None else None
        layers=diagnosis['selected_column_threshold_layers'];matches=[r for r in layers if r['threshold_m_s']==cfg['primary_threshold_m_s']]
        if (profile is None and layers) or (profile is not None and len(matches)!=1):raise ValueError('Selected primary layer cardinality changed')
        layer=matches[0] if matches else None
        point=profile['sampled_lon_lat'] if profile else reference_placeholder(raw,definition)
        if previous is not None:
            metres=GEOD.inv(*previous,*point)[2]
            if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct original section positions required')
            distance+=metres/1000
        previous=point;reasons=[]
        if profile is None:reasons.append('no_qualifying_source_column_reference_gate_midpoint_only')
        if diagnosis['horizontal_selection_status']!=INTERIOR:reasons.append('section_axis_proxy_not_interior_bracketed')
        if layer is None or layer['lower_depth_m'] is None:reasons.append('primary_lower_boundary_censored_or_unresolved')
        lower=not reasons;span=lower and layer['layer_thickness_m'] is not None
        prefix='/direction_contexts/'+key
        anchors.append(paired_anchor('south-java-'+key+'-'+stamp[:10]+'-'+definition['id'],layer,lower,span,reasons,
            source_section_id=definition['id'],source_diagnostic_context_id=key,distance_km=round(distance,6),reference_lon_lat=point,
            selected_model_node_lon_lat=point if profile else None,reference_geometry_is_unselected_gate_midpoint=profile is None,
            source_component_bearing_degrees_true=bearing,source_horizontal_selection_status=diagnosis['horizontal_selection_status'],
            source_profile_refs=[op['source_manifest_file']+'#/sections/'+str(index)+'/direction_contexts/'+key],
            source_model_profile_ref=file+'#'+prefix+'/profiles/'+str(selected) if profile else None,
            source_native_model_profile_ref=file+'#'+profile['source_native_profile_pointer'] if profile else None,
            source_native_acquisition_owner_entity_id=TARGET,
            source_connected_diagnosis_ref=file+'#'+prefix+'/diagnosis/selected_column_threshold_layers/'+str(layers.index(layer)) if layer else None,
            source_section_definition=definition,source_candidate_count=len(context['profiles']),
            source_local_integral_maximum_indices=diagnosis['local_integral_maximum_indices']))
    method='interval_0_150-primary0p05-component'+str(bearing)+'-no-surface-gate-v1'
    flags={'diagnostic_context_id':key,'direction_contexts_are_additive':False,'contexts_are_independent_observations':False,
           'undercurrent_depth_values_inherited':False,'surface_undercurrent_separation_performed':False,
           'source_native_fields_reused':True,'new_velocity_field_requests':0,'new_independent_observations':0,
           'current_identity_independently_validated':False,'water_mass_classification_performed':False,
           'selection_window_basis':sourceop['currents'][TARGET]['selection_window_basis'],'identity_evidence_basis':sourceop['currents'][TARGET]['identity_evidence_basis'],
           'method_id':method,'comparison_group':'model_interval_0_150_primary0p05_component'+str(bearing)+'_no_surface_gate',
           'source_section_geometry':'longitude','parent_current_id':None,'parent_depth_values_inherited':False,
           'identity_relationship':'surface_current_with_non_additive_opposing_direction_contexts'}
    case=project({'entity_id':TARGET,'snapshot_time_utc':stamp,'primary_threshold_m_s':.05,'anchors':anchors,
                  'geometry_role':'regional_reference_connector_between_selected_model_columns_with_explicit_unselected_gate_midpoint_placeholders',
                  'route_id':'south-java-'+key+'-reference-'+stamp[:10],'route_file':None,
                  'flow_direction_context':key+' fixed'+str(bearing)+'degree true;tested independently of calendar;section order is not a downstream trajectory.',
                  'source_time_basis':'Retained HYCOM instantaneous March/June/September/December15,2022 00Z;quarterly probes,not seasonal means/annual envelopes/1990-2003OFESclimatology or2004-2006observational occupations.',
                  'projection_gate':'Frozen upper150m integral/core>5cm/s,interior bracketed selected column and resolved primary lower contour;no positive surface/thermal/relative gate. No opposite-context/deep fill.',
                  'selection_depth_interval_m':[0,150],'core_search_depth_interval_m':[0,150],'source_surface_component_gate_m_s':None,
                  'source_component_reference_frame':'fixed_geographic_'+str(bearing)+'degree_true_held_through_depth',
                  'branch_scope':sourceop['currents'][TARGET]['branch_scope'],'temperature_gate':None,'canonical_route_replaced':False,'canonical_route_extrapolation_performed':False,
                  'reference_geometry_scope':'independent_regional_connector_between_original_sections',**flags},op)
    case['id']='south-java-direction-'+key+'-'+stamp[:10]+'-component'+str(bearing)+'-v1'
    for sample in case['samples']:sample.update(flags)
    if not any(a['lower_projection_eligible'] for a in anchors):case['status']='UNRESOLVED_REGIONAL_REFERENCE_CASE_NO_SUPPORTED_PRIMARY_DEPTH'
    return case


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Frozen projection input changed: '+file)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    previous=read(op['previous_inventory_file']);base,prior=read_parts(previous,reader);load_inventory(previous,reader)
    sourceop=read(op['source_operator_file'])
    lookup=checked_sources(read(op['source_manifest_file']),{f:read(f) for f in op['section_files']},sourceop,op)
    cases=[direction_case(stamp,key,lookup,sourceop,op) for key in ['eastward','westward'] for stamp in sourceop['snapshot_times_utc']]
    supported=[c for c in cases if any(a['lower_projection_eligible'] for a in c['anchors'])];blocked=[c for c in cases if c not in supported]
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'south-java-direction-hycom2022-v1',
              'base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),
              'input_sha256':op['input_sha256'],'projections':supported,'unresolved_reference_cases':blocked,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=encoded(addendum);csv_raw=sample_csv_bytes(supported,reader(previous['base']['csv']['file']));pieces={ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest=copy.deepcopy(previous);manifest['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)})
    manifest['counts']=assemble(base,prior+[addendum])['counts']
    manifest['view_metadata'].update(schema='osw.current-depth-route-projections.v52',status='REGIONAL_DEPTH_BASE_PLUS_PINNED_CURRENT_ADDENDA',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces[INVENTORY]=encoded(manifest);result=load_inventory(manifest,lambda f:pieces[f] if f in pieces else reader(f))
    return manifest,addendum,pieces,result


def main():
    manifest,addendum,pieces,result=build();out=Path('current-depth-route-projections-v52');out.mkdir(exist_ok=True)
    for file,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]:
        if len(pieces[file])>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
        (out/name).write_bytes(pieces[file])
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
