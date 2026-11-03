"""Cloud-only NGCC direction diagnostics from previously retained native fields."""
import copy,hashlib,json
from pathlib import Path
import numpy as np
from interval_depth_diagnostic_v1 import diagnose
from mixed_interval_section_geometry_v1 import validate_retained
from sample_eac_hycom_route_depth_v1 import along_velocity,clean,canonical_hash

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/ngcc-direction-depth-source-operator-v1.json'
OUT=Path('ngcc-direction-depth-sources-v1')
TARGET='current:new-guinea-coastal-current'
NATIVE_OWNER='current:new-guinea-coastal-undercurrent'


def encoded(data):return (json.dumps(data,indent=2,allow_nan=False)+'\n').encode('utf8')


def direction_config(op,key):
    if set(op['direction_contexts'])!={'southeastward','northwestward'} or op['entity_id']!=TARGET:raise ValueError('Declared NGCC owner/direction contexts required')
    expected={'southeastward':110,'northwestward':290}
    for name,c in op['direction_contexts'].items():
        if (c['id']!=name or c['component_bearing_degrees_true']!=expected[name] or c['selection_depth_interval_m']!=[0,100]
            or c['core_search_depth_interval_m']!=[0,100] or c['primary_threshold_m_s']!=.1
            or c['surface_component_gate_m_s'] is not None or c.get('temperature_gate') is not None):raise ValueError('Predeclared upper100m directional diagnostic changed')
    return {**op,**op['direction_contexts'][key]}


def virtual_section(raw,config):
    virtual=copy.deepcopy(raw);virtual['entity_id']=TARGET
    virtual['section_definition']['entity_id']=TARGET;virtual['component_bearing_degrees_true']=config['component_bearing_degrees_true']
    for column in virtual['columns']:
        u=np.asarray([np.nan if x is None else x for x in column['eastward_velocity_m_s']])
        v=np.asarray([np.nan if x is None else x for x in column['northward_velocity_m_s']])
        signed=along_velocity(u,v,config['component_bearing_degrees_true'])
        column['signed_reference_component_m_s']=clean(np.where(np.isfinite(u)&np.isfinite(v),signed,np.nan))
    virtual['decoded_columns_sha256']=canonical_hash(virtual['columns'])
    virtual['diagnosis']=diagnose(virtual['depth_levels_m'],[c['signed_reference_component_m_s'] for c in virtual['columns']],config)
    validate_retained(virtual,config)
    return virtual


def derive_direction(raw,native_file,native_pin,op,key):
    config=direction_config(op,key);virtual=virtual_section(raw,config)
    profiles=[{'sampled_lon_lat':c['sampled_lon_lat'],'source_native_profile_ref':native_file+'#/columns/'+str(i),
               'component_bearing_degrees_true':config['component_bearing_degrees_true'],
               'signed_reference_component_m_s':c['signed_reference_component_m_s']} for i,c in enumerate(virtual['columns'])]
    return {'context_id':key,'entity_id':TARGET,'component_bearing_degrees_true':config['component_bearing_degrees_true'],
            'selection_depth_interval_m':[0,100],'core_search_depth_interval_m':[0,100],'primary_threshold_m_s':.1,
            'native_field_file':native_file,'native_field_sha256':native_pin,'profiles':profiles,
            'decoded_virtual_columns_sha256':virtual['decoded_columns_sha256'],'diagnosis':virtual['diagnosis'],
            'direction_contexts_are_additive':False,'contexts_are_independent_observations':False,
            'undercurrent_depth_values_inherited':False,'surface_undercurrent_separation_performed':False}


def validate_direction(raw,derived,op):
    file=derived['native_field_file']
    if (file not in op['native_section_files'] or derived['native_field_sha256']!=op['input_sha256'][file]
        or canonical_hash(raw['columns'])!=op['native_decoded_columns_sha256'][file]):raise ValueError('Pinned native field/columns changed')
    key=derived['context_id']
    expected=derive_direction(raw,derived['native_field_file'],derived['native_field_sha256'],op,key)
    if derived!=expected:raise ValueError('Derived direction/component/profile pointer/diagnosis changed')
    return True


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();op=json.loads(reader(OPERATOR))
    if any(op['eligibility'].values()):raise ValueError('No physical or runtime promotion')
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Frozen source changed: '+file)
    sourceop=json.loads(reader(op['native_operator_file']));manifest=json.loads(reader(op['native_manifest_file']))
    if manifest['operator_file']!=op['native_operator_file'] or manifest['operator_sha256']!=op['input_sha256'][op['native_operator_file']]:raise ValueError('Native manifest operator changed')
    expected={(t,s['id']) for t in op['snapshot_times_utc'] for s in op['sections']};seen=set();pieces={};entries=[]
    for entry in manifest['sections']:
        native_file=op['native_section_directory']+entry['file'];raw_bytes=reader(native_file);raw=json.loads(raw_bytes)
        if hashlib.sha256(raw_bytes).hexdigest()!=entry['sha256'] or entry['sha256']!=op['input_sha256'][native_file] or len(raw_bytes)!=entry['bytes']:raise ValueError('Original native section hash/size changed')
        identity=(entry['snapshot_time_utc'],entry['section_id'])
        if identity in seen or identity not in expected or raw['entity_id']!=NATIVE_OWNER:raise ValueError('Native field owner/date/section changed')
        seen.add(identity)
        if (raw['snapshot_time_utc']!=entry['snapshot_time_utc'] or raw['section_definition']['id']!=entry['section_id']
            or raw['operator_sha256']!=manifest['operator_sha256'] or raw['operator_file']!=op['native_operator_file']):raise ValueError('Original native section context changed')
        validate_retained(raw,{**sourceop,**sourceop['currents'][NATIVE_OWNER]})
        definition=next(s for s in op['sections'] if s['id']==entry['section_id'])
        if definition!={**raw['section_definition'],'entity_id':TARGET}:raise ValueError('Declared reused section differs from native geometry')
        contexts={key:derive_direction(raw,native_file,entry['sha256'],op,key) for key in ['southeastward','northwestward']}
        for derived in contexts.values():validate_direction(raw,derived,op)
        record={'schema':'osw.reused-native-direction-depth-section.v1','entity_id':TARGET,
                'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),
                'native_field_file':native_file,'native_field_sha256':entry['sha256'],'native_acquisition_owner_entity_id':NATIVE_OWNER,
                'snapshot_time_utc':raw['snapshot_time_utc'],'source_returned_timestamp_utc':raw['source_returned_timestamp_utc'],
                'section_definition':definition,'source_section_geometry':raw['source_section_geometry'],'depth_levels_m':raw['depth_levels_m'],
                'direction_contexts':contexts,'eligibility':op['eligibility'],'source_native_fields_reused':True,
                'new_velocity_field_requests':0,'new_independent_observations':0,'undercurrent_depth_values_inherited':False,
                'surface_undercurrent_separation_performed':False,'water_mass_classification_performed':False,
                'direction_contexts_are_additive':False,'contexts_are_independent_observations':False,'full_goal_complete':False}
        filename=raw['snapshot_time_utc'][:10]+'-ngcc-'+entry['section_id']+'.json';payload=encoded(record)
        if len(payload)>=2500000:raise ValueError('Fixed per-file cap exceeded')
        pieces[filename]=payload
        entries.append({'file':filename,'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload),'entity_id':TARGET,
                        'section_id':entry['section_id'],'snapshot_time_utc':raw['snapshot_time_utc'],'native_field_file':native_file,
                        'native_field_sha256':entry['sha256'],'native_profiles':len(raw['columns']),
                        'direction_contexts':{key:{k:v for k,v in context.items() if k!='profiles'} for key,context in contexts.items()}})
    if seen!=expected or len(entries)!=16:raise ValueError('All16original section/date cases required')
    summary={'raw_sections_reused':16,'native_profiles_reused':sum(e['native_profiles'] for e in entries),'direction_context_diagnoses':32,
             'new_velocity_field_requests':0,'new_independent_observations':0,'new_physical_depth_measurements':0,
             'by_context':{key:{'diagnoses':len(entries),'selected_profiles':sum(e['direction_contexts'][key]['diagnosis']['selected_column_index'] is not None for e in entries),
                               'horizontal_status_counts':{status:sum(e['direction_contexts'][key]['diagnosis']['horizontal_selection_status']==status for e in entries) for status in sorted({e['direction_contexts'][key]['diagnosis']['horizontal_selection_status'] for e in entries})}}
                           for key in ['southeastward','northwestward']}}
    result={'schema':'osw.reused-native-direction-depth-manifest.v1','operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),
            'input_sha256':op['input_sha256'],'sections':entries,'counts':summary,'runtime_changed':False,'full_goal_complete':False}
    pieces['manifest.json']=encoded(result)
    if len(pieces['manifest.json'])>=2500000:raise ValueError('Fixed manifest cap exceeded')
    return result,pieces


def main():
    manifest,pieces=build();OUT.mkdir(exist_ok=True)
    for file,raw in pieces.items():(OUT/file).write_bytes(raw)
    print(json.dumps(manifest['counts']))


if __name__=='__main__':main()
