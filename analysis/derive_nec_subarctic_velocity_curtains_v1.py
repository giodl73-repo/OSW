"""Native spatial depth variation for North Equatorial and Aleutian regional contexts."""
import copy,hashlib,json
from collections import Counter
from pathlib import Path
from native_velocity_depth_curtain_v2 import component,runs,connected_layer
from acquire_zonal_current_depth_sections_v1 import diagnose,validate_retained
from interval_depth_diagnostic_v1 import INTERIOR
from assemble_nec_subarctic_depth_completion_v1 import validate_recovered,source_key,ORIGINAL,COMPLETION

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/nec-subarctic-velocity-curtains-operator-v1.json'
COHORTS={'nec-subarctic':(34,{'current:pacific-north-equatorial','current:atlantic-north-equatorial','current:aleutian'})}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def curtain(section,config,file):
    # Reproduce frozen native geometry, component rotation, full candidate scores
    # and selection. A more favorable or better resolved core is never substituted.
    threshold=config['primary_threshold_m_s']
    if threshold not in [.05,.1] or config['thresholds_m_s'].count(threshold)!=1 or section['section_definition']['fixed_axis']!='longitude':raise ValueError('Original unique5/10cm/s longitude primary threshold required')
    validate_retained(section,config)
    z=section['depth_levels_m'];columns=section['columns'];velocity=[c['signed_reference_component_m_s'] for c in columns]
    original=section['diagnosis'];reproduced=diagnose(z,velocity,config)
    if reproduced!=original:raise ValueError('Every original candidate/selection/layer must reproduce exactly')
    selected=original['selected_column_index'];primary=original['selected_column_threshold_layers'][config['thresholds_m_s'].index(threshold)] if selected is not None else None
    result={'entity_id':section['entity_id'],'section_id':section['section_definition']['id'],'snapshot_time_utc':section['snapshot_time_utc'],'source_file':file,'source_sha256':digest(encode(section)),'source_geometry':{'section_definition':copy.deepcopy(section['section_definition']),'retrieved_hyperslab':copy.deepcopy(section['retrieved_hyperslab']),'maximum_nearest_longitude_distance_km':section['maximum_nearest_longitude_distance_km'],'actual_source_longitude_degrees_east':section['actual_source_longitude_degrees_east']},'component_bearing_degrees_true':section['component_bearing_degrees_true'],'original_horizontal_selection_status':original['horizontal_selection_status'],'original_selected_column_index':selected,'original_primary_layer':copy.deepcopy(primary),'depth_levels_m':copy.deepcopy(z),'velocity_threshold_m_s':threshold,'connectivity':'four_native_axis_neighbors_no_diagonal_or_missing_bridge','status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[],'native_input_column_count':len(columns),'connected_native_node_count':0,'core_reselected':False,'water_mass_classification_performed':False,'native_surface_seed_connected':False,'named_current_axis_independently_validated':False,'physical_current_bottom_established':False,'physical_thickness_m':None,'width_m':None,'cross_section_area_m2':None,'volume_m3':None,'annual_extrema_established':False}
    if original['horizontal_selection_status']!=INTERIOR:return result
    if primary is None or primary.get('core_index') is None:return {**result,'status':'ORIGINAL_PRIMARY_CORE_UNRESOLVED_NO_CURTAIN'}
    core=primary['core_index'];nodes=component(z,velocity,selected,core,threshold);found=False
    for index,column in enumerate(columns):
        descriptors=[]
        for first,last in runs(nodes,index):
            layer=connected_layer(z,velocity[index],threshold,[z[first],z[first]])
            # This single-depth interval merely seeds an already connected run;
            # it does not reselect the original current core or truncate tracing.
            if layer.get('core_index')!=first:raise ValueError('Frozen boundary routine must seed the declared run')
            contains=index==selected and first<=core<=last
            if contains:
                expected=copy.deepcopy(layer)
                for key in ['core_index','core_depth_m','core_velocity_m_s']:expected[key]=primary[key]
                if expected!=primary:raise ValueError('Original seed-run boundaries must reproduce exactly')
                found=True
            descriptors.append({'native_depth_indices_inclusive':[first,last],'contains_original_core':contains,'threshold_layer':layer})
        result['columns'].append({'native_column_index':index,'global_longitude_index':column['global_longitude_index'],'global_latitude_index':column['global_latitude_index'],'sampled_lon_lat':copy.deepcopy(column['sampled_lon_lat']),'status':'ORIGINAL_SEED_CONNECTED_SUPPORT' if descriptors else 'NO_SEED_CONNECTED_SUPPORT_NOT_CURRENT_ABSENCE','connected_depth_runs':descriptors})
    if not found:raise ValueError('Original seed must remain in its curtain')
    result['native_surface_seed_connected']=any(y==0 and z[y]==0 for x,y in nodes)
    result.update(status='REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN',connected_native_node_count=len(nodes),lateral_gate_censored=any(x in [0,len(columns)-1] for x,y in nodes))
    return result

def derive_cohort(root,cohort):
    slug=cohort['id']
    if slug not in COHORTS:raise ValueError('Only predeclared NEC/Aleutian contexts allowed')
    expected_count,owners=COHORTS[slug];file='research/'+slug+'-depth-sections-operator-v1.json'
    if cohort['source_operator']!=file or len(cohort['section_files'])!=expected_count or len(set(cohort['section_files']))!=expected_count:raise ValueError('Exact original cohort and source operator required')
    original,completion,recovery,recovered,remaining=validate_recovered(root)
    if set(original['currents'])!=owners or any(original['eligibility'].values()):raise ValueError('Original direct owners and non-promotion required')
    cases=[]
    for p in cohort['section_files']:
        raw=(root/p).read_bytes();section=json.loads(raw)
        key=source_key(section);provenance=COMPLETION if key in remaining else ORIGINAL
        if section['entity_id'] not in owners or section['operator_file']!=provenance or section['operator_sha256']!=digest((root/provenance).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Pinned owner,original/completion provenance and exact snapshot required')
        if key not in remaining and (key not in recovered or raw!=recovered[key][0]):raise ValueError('Recovered original bytes must be preserved')
        config={**original,**original['currents'][section['entity_id']]}
        result=curtain(section,config,p);result['source_collection_operator']=provenance;result['transport_origin']='completion_missing_five' if key in remaining else 'recovered_original_attempt2';result['source_sha256']=digest(raw);result['cohort_id']=slug;result['source_operator']=file;cases.append(result)
    actual={(v['entity_id'],v['section_id'],v['snapshot_time_utc']) for v in cases};expected={(v['entity_id'],v['id'],t) for v in original['sections'] for t in original['snapshot_times_utc']}
    if actual!=expected or len(actual)!=expected_count:raise ValueError('Every original section/date case exactly once required')
    return cases


from derive_surface_regional_velocity_curtains_v1 import counts


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    if any(op['eligibility'].values()) or [c['id'] for c in op['cohorts']]!=list(COHORTS):raise ValueError('Exact NEC/Aleutian cohort and no physical/annual/runtime promotion')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned native source or method changed: '+p)
    cases=[]
    for cohort in op['cohorts']:cases.extend(derive_cohort(root,cohort))
    keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=34 or len(keys)!=len(set(keys)):raise ValueError('Complete unique34-case cohort required')
    report={'schema':'osw.nec-subarctic-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts(cases),'counts_by_cohort':{slug:counts([c for c in cases if c['cohort_id']==slug]) for slug in COHORTS},'counts_by_current':{owner:counts([c for c in cases if c['entity_id']==owner]) for owner in sorted({c['entity_id'] for c in cases})},'counts_by_primary_threshold_m_s':{str(t):counts([c for c in cases if c['velocity_threshold_m_s']==t]) for t in [.05,.1]},'cases':cases,'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB spatial output bound exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('nec-subarctic-velocity-curtains-v1');out.mkdir(exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps({k:report[k] for k in ['counts','counts_by_cohort','counts_by_current','new_ocean_field_requests','new_reference_inventory_rows','volume_estimates']}),flush=True)
