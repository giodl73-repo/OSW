"""Native spatial depth variation for Davidson and southern Black Sea Rim surface-qualified contexts."""
import copy,hashlib,json
from collections import Counter
from pathlib import Path
import native_surface_qualified_velocity_curtain_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/davidson-rim-velocity-curtains-operator-v1.json'
COHORTS={'davidson-rim':(32,{'current:davidson','current:black-sea-rim'})}
BATCH_COUNTS={'current:davidson':16,'current:black-sea-rim':16}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


SOURCE_AXES={'current:davidson': 'latitude', 'current:black-sea-rim': 'longitude'}

def source_curtain(section,config,file):
    owner=config['entity_id']
    if owner not in SOURCE_AXES or section['entity_id']!=owner or section['schema']!='osw.surface-qualified-mixed-depth-section.v1' or section.get('source_section_geometry')!=SOURCE_AXES[owner] or section['section_definition']['fixed_axis']!=SOURCE_AXES[owner]:raise ValueError('Exact original owner and surface-qualified mixed geometry required')
    result=frozen.curtain(section,config,file)
    result['original_surface_velocity_qualification_applied']=section['surface_velocity_qualification_applied']
    result['original_surface_component_gate_m_s']=section['surface_component_gate_m_s']
    result['surface_gate_requires_primary_surface_connectivity']=False
    return result


def derive_cohort(root,cohort,owner=None):
    slug=cohort['id']
    if slug not in COHORTS:raise ValueError('Only predeclared Davidson and Rim surface-qualified contexts allowed')
    expected_count,owners=COHORTS[slug];file='research/'+slug+'-surface-qualified-depth-sections-operator-v1.json'
    if cohort['source_operator']!=file or len(cohort['section_files'])!=expected_count or len(set(cohort['section_files']))!=expected_count:raise ValueError('Exact original cohort and source operator required')
    original=json.loads((root/file).read_bytes())
    if set(original['currents'])!=owners or any(original['eligibility'].values()):raise ValueError('Original direct owners and non-promotion required')
    batches=cohort['section_files_by_current']
    if set(batches)!=owners or owner not in batches or any(len(batches[k])!=BATCH_COUNTS[k] for k in owners):raise ValueError('Exact declared current batch required')
    flattened=[p for batch in batches.values() for p in batch]
    if len(flattened)!=32 or len(set(flattened))!=32 or set(flattened)!=set(cohort['section_files']):raise ValueError('All32sourcecases inexactlyonecurrentbatch required')
    cases=[]
    for p in batches[owner]:
        raw=(root/p).read_bytes();section=json.loads(raw)
        if section['entity_id']!=owner or section['operator_file']!=file or section['operator_sha256']!=digest((root/file).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Pinned original owner,operator and exact snapshot required')
        config={**original,**original['currents'][section['entity_id']]}
        definitions=[d for d in original['sections'] if d['entity_id']==owner and d['id']==section['section_definition']['id']]
        if len(definitions)!=1 or section['section_definition']!=definitions[0]:raise ValueError('Exactoriginal section definition required')
        result=source_curtain(section,config,p);result['source_sha256']=digest(raw);result['cohort_id']=slug;result['source_operator']=file;cases.append(result)
    actual={(v['entity_id'],v['section_id'],v['snapshot_time_utc']) for v in cases};expected={(v['entity_id'],v['id'],t) for v in original['sections'] if v['entity_id']==owner for t in original['snapshot_times_utc']}
    if actual!=expected or len(actual)!=BATCH_COUNTS[owner]:raise ValueError('Every original current section/date case exactly once required')
    return cases


from derive_surface_regional_velocity_curtains_v1 import counts


def build(root=ROOT,owner=None):
    op=json.loads((root/OPERATOR).read_bytes())
    if owner not in BATCH_COUNTS:raise ValueError('Explicit canonical current batch required')
    if any(op['eligibility'].values()) or [c['id'] for c in op['cohorts']]!=list(COHORTS):raise ValueError('Exact original Davidson and Rim surface-qualified cohort and no physical/annual/runtime promotion')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned native source or method changed: '+p)
    cases=[]
    for cohort in op['cohorts']:cases.extend(derive_cohort(root,cohort,owner))
    keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=BATCH_COUNTS[owner] or len(keys)!=len(set(keys)):raise ValueError('Complete uniqueowner-case cohort required')
    report={'schema':'osw.davidson-rim-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','source_plan_case_count':32,'batch_current_id':owner,'operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts(cases),'counts_by_cohort':{slug:counts([c for c in cases if c['cohort_id']==slug]) for slug in COHORTS},'counts_by_current':{owner:counts([c for c in cases if c['entity_id']==owner]) for owner in sorted({c['entity_id'] for c in cases})},'counts_by_primary_threshold_m_s':{str(t):counts([c for c in cases if c['velocity_threshold_m_s']==t]) for t in [.05,.1]},'cases':cases,'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB spatial output bound exceeded')
    return report,raw


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--current',required=True,choices=list(BATCH_COUNTS));args=parser.parse_args()
    report,raw=build(owner=args.current);out=Path('davidson-rim-velocity-curtains-v1')/args.current.split(':')[1];out.mkdir(parents=True,exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps({'current':args.current,'bytes':len(raw),'counts':report['counts']}),flush=True)
