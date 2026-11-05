"""Native spatial depth variation for North Brazil legacy surface-branch context."""
import copy,hashlib,json
from collections import Counter
from pathlib import Path
import native_north_brazil_velocity_curtain_v1 as frozen
import acquire_north_brazil_depth_sections_v1 as legacy

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/north-brazil-velocity-curtains-operator-v1.json'
COHORTS={'north-brazil':(14,{'current:north-brazil'})}
BATCH_COUNTS={'current:north-brazil':14}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def restore_source(view,original_columns_hash):
    original=copy.deepcopy(view)
    for column in original['columns']:column['signed_northwest_component_m_s']=column.pop('signed_reference_component_m_s')
    original['section_definition'].pop('entity_id');original.pop('native100m_temperature_degrees_celsius');original.pop('temperature_source');original['decoded_columns_sha256']=original_columns_hash
    return original


def source_view(section,original):
    if original['entity_id']!='current:north-brazil' or section['entity_id']!=original['entity_id'] or section['schema']!='osw.north-brazil-depth-section.v1' or 'source_section_geometry' in section or 'native100m_temperature_degrees_celsius' in section or 'temperature_source' in section:raise ValueError('Exact original NBC legacy source required')
    matches=[d for d in original['sections'] if d['id']==section['section_definition']['id']]
    if len(matches)!=1 or section['section_definition']!=matches[0] or 'entity_id' in section['section_definition'] or 'fixed_axis' in section['section_definition']:raise ValueError('Exact original legacy section definition required')
    if original['component_bearing_degrees_true']!=315 or original['primary_threshold_m_s']!=.1 or original['surface_component_gate_m_s']!=.05 or any(original['eligibility'].values()):raise ValueError('Original NBC declaration required')
    legacy.validate_retained(section,original)
    view=copy.deepcopy(section)
    for column in view['columns']:
        if 'signed_reference_component_m_s' in column:raise ValueError('No mixed component aliases in source')
        column['signed_reference_component_m_s']=column.pop('signed_northwest_component_m_s')
    view['section_definition']['entity_id']=original['entity_id'];view['native100m_temperature_degrees_celsius']=None;view['temperature_source']=None;view['decoded_columns_sha256']=legacy.canonical_hash(view['columns'])
    config=copy.deepcopy(original);config['legacy_original_decoded_columns_sha256']=section['decoded_columns_sha256'];config['temperature_gate']=None;config['sections']=[{**d,'entity_id':original['entity_id']} for d in original['sections']]
    if restore_source(view,section['decoded_columns_sha256'])!=section:raise ValueError('In-memory aliases must restore every original source field')
    return view,config


def source_curtain(section,original,file):
    view,config=source_view(section,original);result=frozen.curtain(view,config,file)
    result['schema_adapter']='REVERSIBLE_NBC_COMPONENT_ALIAS_DEFINITION_OWNER_AND_NONTHERMAL_NULL_VIEW'
    result['legacy_binary32_component_reproduction_exact']=True;result['schema_adapter_changes_source_bytes']=False;result['component_values_changed_by_adapter']=False
    result['original_decoded_columns_sha256']=section['decoded_columns_sha256'];result['canonical_view_decoded_columns_sha256']=view['decoded_columns_sha256']
    return result


def derive_cohort(root,cohort,owner=None):
    slug=cohort['id']
    if slug not in COHORTS:raise ValueError('Only predeclared North Brazil legacy contexts allowed')
    expected_count,owners=COHORTS[slug];file='research/'+slug+'-depth-sections-operator-v1.json'
    if cohort['source_operator']!=file or len(cohort['section_files'])!=expected_count or len(set(cohort['section_files']))!=expected_count:raise ValueError('Exact original cohort and source operator required')
    original=json.loads((root/file).read_bytes())
    if {original['entity_id']}!=owners or any(original['eligibility'].values()):raise ValueError('Original direct owners and non-promotion required')
    batches=cohort['section_files_by_current']
    if set(batches)!=owners or owner not in batches or any(len(batches[k])!=BATCH_COUNTS[k] for k in owners):raise ValueError('Exact declared current batch required')
    flattened=[p for batch in batches.values() for p in batch]
    if len(flattened)!=14 or len(set(flattened))!=14 or set(flattened)!=set(cohort['section_files']):raise ValueError('All14sourcecases inexactlyonecurrentbatch required')
    cases=[]
    for p in batches[owner]:
        raw=(root/p).read_bytes();section=json.loads(raw)
        if section['entity_id']!=owner or section['operator_file']!=file or section['operator_sha256']!=digest((root/file).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Pinned original owner,operator and exact snapshot required')
        config=original
        definitions=[d for d in original['sections'] if d['id']==section['section_definition']['id']]
        if len(definitions)!=1 or section['section_definition']!=definitions[0]:raise ValueError('Exactoriginal section definition required')
        result=source_curtain(section,config,p);result['source_sha256']=digest(raw);result['cohort_id']=slug;result['source_operator']=file;cases.append(result)
    actual={(v['entity_id'],v['section_id'],v['snapshot_time_utc']) for v in cases};expected={(owner,v['id'],t) for v in original['sections'] for t in original['snapshot_times_utc']}
    if actual!=expected or len(actual)!=BATCH_COUNTS[owner]:raise ValueError('Every original current section/date case exactly once required')
    return cases


from derive_surface_regional_velocity_curtains_v1 import counts


def build(root=ROOT,owner=None):
    op=json.loads((root/OPERATOR).read_bytes())
    if owner not in BATCH_COUNTS:raise ValueError('Explicit canonical current batch required')
    if any(op['eligibility'].values()) or [c['id'] for c in op['cohorts']]!=list(COHORTS):raise ValueError('Exact original North Brazil legacy cohort and no physical/annual/runtime promotion')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned native source or method changed: '+p)
    cases=[]
    for cohort in op['cohorts']:cases.extend(derive_cohort(root,cohort,owner))
    keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=BATCH_COUNTS[owner] or len(keys)!=len(set(keys)):raise ValueError('Complete uniqueowner-case cohort required')
    report={'schema':'osw.north-brazil-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','source_plan_case_count':14,'batch_current_id':owner,'operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts(cases),'counts_by_cohort':{slug:counts([c for c in cases if c['cohort_id']==slug]) for slug in COHORTS},'counts_by_current':{owner:counts([c for c in cases if c['entity_id']==owner]) for owner in sorted({c['entity_id'] for c in cases})},'counts_by_primary_threshold_m_s':{str(t):counts([c for c in cases if c['velocity_threshold_m_s']==t]) for t in [.05,.1]},'cases':cases,'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB spatial output bound exceeded')
    return report,raw


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--current',required=True,choices=list(BATCH_COUNTS));args=parser.parse_args()
    report,raw=build(owner=args.current);out=Path('north-brazil-velocity-curtains-v1')/args.current.split(':')[1];out.mkdir(parents=True,exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps({'current':args.current,'bytes':len(raw),'counts':report['counts']}),flush=True)
