"""Native depth variation around frozen cores; velocity-only regional proxies."""
import copy,hashlib,json,math
from collections import Counter,deque
from pathlib import Path
from derive_eac_connected_layer_thickness_v1 import connected_layer
from interval_depth_diagnostic_v1 import diagnose,INTERIOR
from mixed_interval_section_geometry_v1 import validate_retained

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/barents-makassar-velocity-curtains-operator-v1.json'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(obj):return (json.dumps(obj,separators=(',',':'),allow_nan=False)+'\n').encode()


def component(z,columns,selected,core):
    finite=lambda x:type(x) in (int,float) and math.isfinite(x)
    if not 2<=len(z)<=40 or not 3<=len(columns)<=150 or len(z)*len(columns)>6000 or any(len(c)!=len(z) for c in columns):raise ValueError('Bounded rectangular native section required')
    if not all(finite(v) and v>=0 for v in z) or any(b<=a for a,b in zip(z,z[1:])) or any(v is not None and (not finite(v) or abs(v)>10) for c in columns for v in c):raise ValueError('Original native finite depths and finite-or-missing velocity required')
    if type(selected)!=int or type(core)!=int or not 0<=selected<len(columns) or not 0<=core<len(z):raise ValueError('Original integer core indices required')
    def qualifies(x,y):return columns[x][y] is not None and columns[x][y]>.1
    if not qualifies(selected,core):raise ValueError('Original core must exceed unchanged strict threshold')
    nodes={(selected,core)};queue=deque(nodes)
    while queue:
        x,y=queue.popleft()
        for i,j in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if 0<=i<len(columns) and 0<=j<len(z) and (i,j) not in nodes and qualifies(i,j):nodes.add((i,j));queue.append((i,j))
    return nodes


def runs(nodes,column):
    out=[]
    for index in sorted(y for x,y in nodes if x==column):
        if out and out[-1][1]+1==index:out[-1][1]=index
        else:out.append([index,index])
    return out


def curtain(section,config,file):
    # Reproduce frozen native geometry, component rotation, full candidate scores
    # and selection. A more favorable or better resolved core is never substituted.
    validate_retained(section,config)
    z=section['depth_levels_m'];columns=section['columns'];velocity=[c['signed_reference_component_m_s'] for c in columns]
    original=section['diagnosis'];reproduced=diagnose(z,velocity,config)
    if reproduced!=original:raise ValueError('Every original candidate/selection/layer must reproduce exactly')
    selected=original['selected_column_index'];primary=original['selected_column_threshold_layers'][1] if selected is not None else None
    result={'entity_id':section['entity_id'],'section_id':section['section_definition']['id'],'snapshot_time_utc':section['snapshot_time_utc'],'source_file':file,'source_sha256':digest(encode(section)),'source_geometry':section['source_section_geometry'],'component_bearing_degrees_true':section['component_bearing_degrees_true'],'original_horizontal_selection_status':original['horizontal_selection_status'],'original_selected_column_index':selected,'original_primary_layer':copy.deepcopy(primary),'depth_levels_m':copy.deepcopy(z),'velocity_threshold_m_s':.1,'connectivity':'four_native_axis_neighbors_no_diagonal_or_missing_bridge','status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[],'native_input_column_count':len(columns),'connected_native_node_count':0,'core_reselected':False,'water_mass_classification_performed':False,'named_current_axis_independently_validated':False,'physical_current_bottom_established':False,'physical_thickness_m':None,'width_m':None,'cross_section_area_m2':None,'volume_m3':None,'annual_extrema_established':False}
    if original['horizontal_selection_status']!=INTERIOR:return result
    if primary is None or primary.get('core_index') is None:return {**result,'status':'ORIGINAL_PRIMARY_CORE_UNRESOLVED_NO_CURTAIN'}
    core=primary['core_index'];nodes=component(z,velocity,selected,core);found=False
    for index,column in enumerate(columns):
        descriptors=[]
        for first,last in runs(nodes,index):
            layer=connected_layer(z,velocity[index],.1,[z[first],z[first]])
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
    result.update(status='REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN',connected_native_node_count=len(nodes),lateral_gate_censored=any(x in [0,len(columns)-1] for x,y in nodes))
    return result


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Pinned input changed: '+file)
    original=json.loads((root/op['source_operator']).read_bytes());cases=[]
    if len(op['section_files'])!=32 or len(set(op['section_files']))!=32:raise ValueError('All32 original cases required')
    for file in op['section_files']:
        raw=(root/file).read_bytes();section=json.loads(raw)
        if section['operator_file']!=op['source_operator'] or section['operator_sha256']!=digest((root/op['source_operator']).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Original operator and returned time required')
        config={**original,**original['currents'][section['entity_id']]}
        result=curtain(section,config,file);result['source_sha256']=digest(raw);cases.append(result)
    actual={(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases}
    expected={(s['entity_id'],s['id'],t) for s in original['sections'] for t in original['snapshot_times_utc']}
    if actual!=expected or len(actual)!=32:raise ValueError('Every original section/date exactly once required')
    allruns=[r for c in cases for col in c['columns'] for r in col['connected_depth_runs']]
    counts={'cases':len(cases),'status_counts':dict(Counter(c['status'] for c in cases)),'native_input_columns':sum(c['native_input_column_count'] for c in cases),'seed_connected_columns':sum(bool(col['connected_depth_runs']) for c in cases for col in c['columns']),'connected_native_nodes':sum(c['connected_native_node_count'] for c in cases),'vertical_runs':len(allruns),'multiple_run_columns':sum(len(col['connected_depth_runs'])>1 for c in cases for col in c['columns']),'lower_boundary_status_counts':dict(Counter(r['threshold_layer']['lower_status'] for r in allruns)),'lateral_gate_censored_curtains':sum(c.get('lateral_gate_censored',False) for c in cases),'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0}
    report={'schema':'osw.barents-makassar-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts,'cases':cases,'interpretation':'Native depth variation of the connected velocity component around each original selected core. North Cape eastward regional proxy and Makassar southward branch proxy; no water mass or independent named-axis identification. No geographic interpolation, joining cuts, seasonal envelope, physical width/area/volume or duplicate reference admission.','runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Unchanged source output cap exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('barents-makassar-velocity-curtains-v1');out.mkdir(exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps(report['counts']),flush=True)
