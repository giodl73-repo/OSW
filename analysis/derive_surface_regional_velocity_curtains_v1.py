"""Native spatial depth variation for five scoped surface-current contexts; no retrieval."""
import copy,hashlib,json
from collections import Counter
from pathlib import Path
import derive_barents_makassar_velocity_curtains_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/surface-regional-velocity-curtains-operator-v1.json'
COHORTS={'adriatic-surface':(32,{'current:east-adriatic','current:western-adriatic'}),'alaska-coastal-shelikof':(16,{'current:alaska-coastal-gulf'}),'hiri-zeehan':(32,{'current:hiri-current','current:zeehan'})}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def derive_cohort(root,cohort):
    slug=cohort['id']
    if slug not in COHORTS:raise ValueError('Only predeclared surface contexts allowed')
    expected_count,owners=COHORTS[slug];file='research/'+slug+'-interval-depth-sections-operator-v1.json'
    if cohort['source_operator']!=file or len(cohort['section_files'])!=expected_count or len(set(cohort['section_files']))!=expected_count:raise ValueError('Exact original cohort and source operator required')
    original=json.loads((root/file).read_bytes())
    if set(original['currents'])!=owners or any(original['eligibility'].values()):raise ValueError('Original direct owners and non-promotion required')
    cases=[]
    for p in cohort['section_files']:
        raw=(root/p).read_bytes();section=json.loads(raw)
        if section['entity_id'] not in owners or section['operator_file']!=file or section['operator_sha256']!=digest((root/file).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Pinned original owner,operator and exact snapshot required')
        config={**original,**original['currents'][section['entity_id']]}
        result=frozen.curtain(section,config,p);result['source_sha256']=digest(raw);result['cohort_id']=slug;result['source_operator']=file;cases.append(result)
    actual={(v['entity_id'],v['section_id'],v['snapshot_time_utc']) for v in cases};expected={(v['entity_id'],v['id'],t) for v in original['sections'] for t in original['snapshot_times_utc']}
    if actual!=expected or len(actual)!=expected_count:raise ValueError('Every original section/date case exactly once required')
    return cases


def counts(cases):
    runs=[v for c in cases for col in c['columns'] for v in col['connected_depth_runs']]
    return {'cases':len(cases),'status_counts':dict(Counter(c['status'] for c in cases)),'native_input_columns':sum(c['native_input_column_count'] for c in cases),'seed_connected_columns':sum(bool(col['connected_depth_runs']) for c in cases for col in c['columns']),'connected_native_nodes':sum(c['connected_native_node_count'] for c in cases),'vertical_runs':len(runs),'multiple_run_columns':sum(len(col['connected_depth_runs'])>1 for c in cases for col in c['columns']),'lower_boundary_status_counts':dict(Counter(v['threshold_layer']['lower_status'] for v in runs)),'lateral_gate_censored_curtains':sum(c.get('lateral_gate_censored',False) for c in cases)}


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    if any(op['eligibility'].values()) or [c['id'] for c in op['cohorts']]!=list(COHORTS):raise ValueError('Exact three cohorts and no physical/annual/runtime promotion')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned native source or method changed: '+p)
    cases=[]
    for cohort in op['cohorts']:cases.extend(derive_cohort(root,cohort))
    keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=80 or len(keys)!=len(set(keys)):raise ValueError('Complete unique80-case cohort required')
    report={'schema':'osw.surface-regional-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts(cases),'counts_by_cohort':{slug:counts([c for c in cases if c['cohort_id']==slug]) for slug in COHORTS},'counts_by_current':{owner:counts([c for c in cases if c['entity_id']==owner]) for owner in sorted({c['entity_id'] for c in cases})},'cases':cases,'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB spatial output bound exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('surface-regional-velocity-curtains-v1');out.mkdir(exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps({k:report[k] for k in ['counts','counts_by_cohort','counts_by_current','new_ocean_field_requests','new_reference_inventory_rows','volume_estimates']}),flush=True)
