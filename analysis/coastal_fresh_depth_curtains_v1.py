"""Native coastal depth curtains connected to the unchanged original velocity core."""
import copy,hashlib,json,math
from collections import Counter,deque
from pathlib import Path
import load_current_depth_reference_inventory_v12 as inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/coastal-fresh-depth-curtains-operator-v1.json'
OUT='research/coastal-fresh-depth-curtains-v1.json'
RULES=inventory.source.RULES


def connected_nodes(z,velocity,salinity,column,core,entity):
    if entity not in RULES:raise ValueError('Declared source-specific owner required')
    n=len(velocity);m=len(z)
    finite=lambda x:type(x) in (int,float) and math.isfinite(x)
    if not 1<=n<=150 or not 2<=m<=40 or n*m>6000 or len(salinity)!=n or any(len(a)!=m for a in velocity+salinity):raise ValueError('Bounded corresponding native columns required')
    if not all(finite(v) and v>=0 for v in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Increasing nonnegative depths required')
    if any(v is not None and not finite(v) for a in velocity+salinity for v in a) or any(v is not None and not 0<=v<=50 for a in salinity for v in a):raise ValueError('Finite or explicit missing native inputs required')
    if type(column)!=int or type(core)!=int or not 0<=column<n or not 0<=core<m:raise ValueError('Exact original core indices required')
    salt=RULES[entity][1]
    def qualifies(x,y):return velocity[x][y] is not None and salinity[x][y] is not None and velocity[x][y]>.1 and salinity[x][y]<salt
    if not qualifies(column,core):return set()
    seen={(column,core)};queue=deque(seen)
    while queue:
        x,y=queue.popleft()
        for i,j in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if 0<=i<n and 0<=j<m and (i,j) not in seen and qualifies(i,j):seen.add((i,j));queue.append((i,j))
    return seen


def runs_for_column(nodes,column):
    indices=sorted(y for x,y in nodes if x==column);runs=[]
    for y in indices:
        if runs and runs[-1][1]+1==y:runs[-1][1]=y
        else:runs.append([y,y])
    return runs


def curtain(case,bundle):
    original=case['original'];classification=case['classification'];file=original['source_section_file'];section=bundle['sections'][file];profile=case['profile'];entity=original['entity_id']
    result={'entity_id':entity,'snapshot_time_utc':original['snapshot_time_utc'],'section_id':original['section_id'],'original_velocity_source_file':file,'original_velocity_source_sha256':original['source_section_sha256'],'full_salinity_source':copy.deepcopy(case['profile_piece']),'original_classification':copy.deepcopy(classification),'original_selected_column_index':section['diagnosis']['selected_column_index'],'original_core_index':classification.get('original_core_index'),'depth_levels_m':copy.deepcopy(section['depth_levels_m']),'native_latitude_degrees_north':profile['native_latitude_degrees_north'],'native_latitude_index':profile['native_latitude_index'],'component_bearing_degrees_true':RULES[entity][0],'velocity_threshold_m_s':.1,'practical_salinity_exclusive_upper_threshold':RULES[entity][1],'connectivity':'four_native_axis_neighbors_only_no_diagonal_or_missing_bridge','columns':[],'connected_native_node_count':0,'core_reselected':False,'physical_current_bottom_established':False,'physical_layer_thickness_m':None,'cross_section_area_m2':None,'width_m':None,'volume_m3':None,'whole_route_profile_established':False,'annual_extrema_established':False}
    if classification['status']!='conditional_fresh_component_core_supported':return {**result,'status':'ORIGINAL_CORE_UNRESOLVED_OR_OUTSIDE_CLASS_NO_CURTAIN'}
    z=section['depth_levels_m'];velocity=[c['signed_reference_component_m_s'] for c in section['columns']];salinity=profile['practical_salinity_columns'];selected=result['original_selected_column_index'];core=result['original_core_index']
    nodes=connected_nodes(z,velocity,salinity,selected,core,entity)
    if not nodes:raise ValueError('Supported original core must seed its own component')
    diagnose=inventory.source.ncc_diagnose if entity=='current:norwegian-coastal' else inventory.source.egcc_diagnose
    original_run_found=False
    for index,column in enumerate(section['columns']):
        runs=[]
        for first,last in runs_for_column(nodes,index):
            diagnostic=diagnose(z,velocity[index],salinity[index],first)
            if diagnostic['upper']['last_connected_native_index']!=first or diagnostic['lower']['last_connected_native_index']!=last:raise ValueError('Connected membership and frozen vertical diagnostic disagree')
            runs.append({'native_depth_indices_inclusive':[first,last],'upper':diagnostic['upper'],'lower':diagnostic['lower'],'contains_original_core':index==selected and first<=core<=last})
            if runs[-1]['contains_original_core']:
                if diagnostic['upper']!=classification['upper'] or diagnostic['lower']!=classification['lower']:raise ValueError('Original core boundaries must reproduce exactly')
                original_run_found=True
        deepest=runs[-1]['lower'] if runs else None
        result['columns'].append({'native_column_index':index,'native_longitude_index':column['global_longitude_index'],'native_longitude_degrees_east':column['native_source_longitude_degrees_east'],'status':'ORIGINAL_SEED_CONNECTED_NATIVE_SUPPORT' if runs else 'NO_ORIGINAL_SEED_CONNECTED_SUPPORT_NOT_CURRENT_ABSENCE','connected_depth_runs':runs,'deepest_connected_sample_depth_m':z[runs[-1]['native_depth_indices_inclusive'][1]] if runs else None,'deepest_run_lower_boundary_depth_m':deepest['boundary_depth_m'] if deepest else None,'deepest_run_lower_status':deepest['status'] if deepest else None,'touches_lateral_sampling_edge':bool(runs) and index in (0,len(velocity)-1)})
    if not original_run_found:raise ValueError('Original core cannot disappear')
    return {**result,'status':'NATIVE_SEED_CONNECTED_CONDITIONAL_DEPTH_CURTAIN','connected_native_node_count':len(nodes)}


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OPERATOR)
    if op['classifiers']!={k:{'bearing_degrees_true':v[0],'velocity_threshold_m_s':.1,'salinity_threshold_exclusive':v[1]} for k,v in RULES.items()} or any(op['eligibility'].values()) or op['connectivity']!='four_native_axis_neighbors_only_no_diagonal_or_missing_bridge':raise ValueError('Frozen connectivity,source rules and eligibility required')
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Frozen curtain input changed: '+file)
    manifest=read(op['reference_inventory_file']);inventory.load_inventory(manifest,reader);parts=inventory.read_parts(manifest,reader);cohorts=parts[-1]
    if len(cohorts)!=1:raise ValueError('One complete original coastal cohort required')
    addendum,bundle=cohorts[0];cases=inventory.reproduce(bundle);rows=[curtain(c,bundle) for c in cases]
    columns=[c for r in rows for c in r['columns']];runs=[v for c in columns for v in c['connected_depth_runs']]
    result={'schema':'osw.coastal-fresh-depth-curtains.v1','status':'REPRODUCED_NATIVE_ORIGINAL_CORE_CONNECTED_DEPTH_CURTAINS','operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'source_reference_inventory_file':op['reference_inventory_file'],'source_admission_report':copy.deepcopy(addendum['reference_admission_report']),'records':rows,'counts':{'original_cases':len(rows),'curtains':sum(r['status']=='NATIVE_SEED_CONNECTED_CONDITIONAL_DEPTH_CURTAIN' for r in rows),'unclassified_cases':sum(not r['columns'] for r in rows),'native_columns_retained':len(columns),'seed_connected_columns':sum(bool(c['connected_depth_runs']) for c in columns),'seed_connected_native_nodes':sum(r['connected_native_node_count'] for r in rows),'connected_vertical_runs':len(runs),'multiple_run_columns':sum(len(c['connected_depth_runs'])>1 for c in columns),'lower_boundary_status_counts':dict(Counter(v['lower']['status'] for v in runs)),'laterally_censored_sections':sum(any(c['touches_lateral_sampling_edge'] for c in r['columns']) for r in rows)},'interpretation':op['interpretation'],'new_ocean_field_requests':0,'new_reference_inventory_rows_admitted':0,'physical_current_bottom_established':False,'physical_layer_thickness_established':False,'cross_section_area_established':False,'physical_width_established':False,'volume_established':False,'runtime_changed':False,'full_goal_complete':False}
    raw=(json.dumps(result,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    if len(raw)>=2400000:raise ValueError('Fixed source batch publication cap exceeded')
    return result,raw


def main():
    report,raw=build();out=Path('coastal-fresh-depth-curtains-v1');out.mkdir(exist_ok=True);(out/'depth-curtains.json').write_bytes(raw);print(json.dumps(report['counts']))


if __name__=='__main__':main()
