"""Explicit source-threshold native tracing; v1 remains frozen and reproduced at0.1m/s."""
import copy,hashlib,json,math
from collections import deque
from derive_barents_makassar_velocity_curtains_v1 import runs,connected_layer,diagnose,INTERIOR,validate_retained


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def component(z,columns,selected,core,threshold):
    if type(threshold) not in (int,float) or not math.isfinite(threshold) or threshold<=0:raise ValueError('Explicit positive finite source threshold required')
    finite=lambda x:type(x) in (int,float) and math.isfinite(x)
    if not 2<=len(z)<=40 or not 3<=len(columns)<=150 or len(z)*len(columns)>6000 or any(len(c)!=len(z) for c in columns):raise ValueError('Bounded rectangular native section required')
    if not all(finite(v) and v>=0 for v in z) or any(b<=a for a,b in zip(z,z[1:])) or any(v is not None and (not finite(v) or abs(v)>10) for c in columns for v in c):raise ValueError('Original native finite depths and finite-or-missing velocity required')
    if type(selected)!=int or type(core)!=int or not 0<=selected<len(columns) or not 0<=core<len(z):raise ValueError('Original integer core indices required')
    def qualifies(x,y):return columns[x][y] is not None and columns[x][y]>threshold
    if not qualifies(selected,core):raise ValueError('Original core must exceed unchanged strict threshold')
    nodes={(selected,core)};queue=deque(nodes)
    while queue:
        x,y=queue.popleft()
        for i,j in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if 0<=i<len(columns) and 0<=j<len(z) and (i,j) not in nodes and qualifies(i,j):nodes.add((i,j));queue.append((i,j))
    return nodes


def curtain(section,config,file):
    # Reproduce frozen native geometry, component rotation, full candidate scores
    # and selection. A more favorable or better resolved core is never substituted.
    threshold=config['primary_threshold_m_s']
    if type(threshold) not in (int,float) or not math.isfinite(threshold) or threshold<=0 or config['thresholds_m_s'].count(threshold)!=1:raise ValueError('Exact one source primary threshold required')
    validate_retained(section,config)
    z=section['depth_levels_m'];columns=section['columns'];velocity=[c['signed_reference_component_m_s'] for c in columns]
    original=section['diagnosis'];reproduced=diagnose(z,velocity,config)
    if reproduced!=original:raise ValueError('Every original candidate/selection/layer must reproduce exactly')
    selected=original['selected_column_index'];primary=original['selected_column_threshold_layers'][config['thresholds_m_s'].index(threshold)] if selected is not None else None
    result={'entity_id':section['entity_id'],'section_id':section['section_definition']['id'],'snapshot_time_utc':section['snapshot_time_utc'],'source_file':file,'source_sha256':digest(encode(section)),'source_geometry':section['source_section_geometry'],'component_bearing_degrees_true':section['component_bearing_degrees_true'],'original_horizontal_selection_status':original['horizontal_selection_status'],'original_selected_column_index':selected,'original_primary_layer':copy.deepcopy(primary),'depth_levels_m':copy.deepcopy(z),'velocity_threshold_m_s':threshold,'connectivity':'four_native_axis_neighbors_no_diagonal_or_missing_bridge','status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[],'native_input_column_count':len(columns),'connected_native_node_count':0,'core_reselected':False,'water_mass_classification_performed':False,'named_current_axis_independently_validated':False,'physical_current_bottom_established':False,'physical_thickness_m':None,'width_m':None,'cross_section_area_m2':None,'volume_m3':None,'annual_extrema_established':False}
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
    result.update(status='REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN',connected_native_node_count=len(nodes),lateral_gate_censored=any(x in [0,len(columns)-1] for x,y in nodes))
    return result
