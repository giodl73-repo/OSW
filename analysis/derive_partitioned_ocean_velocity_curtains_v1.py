"""Native spatial depth variation for partitioned South Atlantic and Tasman Front contexts."""
import copy,hashlib,json
from collections import Counter
from pathlib import Path
import native_velocity_depth_curtain_v2 as frozen
from interval_transverse_section_audit_v1 import validate_retained as validate_legacy_longitude
from current_depth_search_partitions_v1 import validate_partitions,validate_section_partition

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/partitioned-ocean-velocity-curtains-operator-v1.json'
COHORTS={'partitioned-ocean':(64,{'current:south-atlantic','current:tasman-front'})}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def geometry_view(section,config):
    validate_section_partition(section,config)
    validate_legacy_longitude(section,config)
    if 'source_section_geometry' in section:raise ValueError('Original partitioned longitude source must have no mixed tag')
    view=copy.deepcopy(section);view['source_section_geometry']='longitude'
    return view


def derive_cohort(root,cohort,partition=None):
    slug=cohort['id']
    if slug not in COHORTS:raise ValueError('Only predeclared partitioned ocean contexts allowed')
    expected_count,owners=COHORTS[slug];file='research/'+slug+'-depth-sections-operator-v1.json'
    if cohort['source_operator']!=file or len(cohort['section_files'])!=expected_count or len(set(cohort['section_files']))!=expected_count:raise ValueError('Exact original cohort and source operator required')
    original=json.loads((root/file).read_bytes());validate_partitions(original)
    if set(original['currents'])!=owners or any(original['eligibility'].values()):raise ValueError('Original direct owners and non-promotion required')
    batches=cohort['section_files_by_partition']
    if set(batches)!=set(original['search_partitions']) or partition not in batches:raise ValueError('Exact original partition batch required')
    flattened=[p for batch in batches.values() for p in batch]
    if len(flattened)!=64 or len(set(flattened))!=64 or set(flattened)!=set(cohort['section_files']) or any(len(batch)!=16 for batch in batches.values()):raise ValueError('Four disjoint complete16case partition batches required')
    cases=[]
    for p in batches[partition]:
        raw=(root/p).read_bytes();section=json.loads(raw)
        if section['search_partition_id']!=partition or section['entity_id'] not in owners or section['operator_file']!=file or section['operator_sha256']!=digest((root/file).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Pinned original owner,operator and exact snapshot required')
        config={**original,**original['currents'][section['entity_id']]}
        view=geometry_view(section,config);result=frozen.curtain(view,config,p);result['geometry_adapter']='ORIGINAL_PARTITION_AND_LONGITUDE_INTERVAL_VALIDATED_THEN_IN_MEMORY_TAG_ONLY';result['search_partition_id']=section['search_partition_id'];result['search_partition_kind']=section['search_partition_kind'];result['partition_is_current_identity']=False;result['cross_partition_join_performed']=False;result['front_or_water_mass_classification_performed']=False;result['source_sha256']=digest(raw);result['cohort_id']=slug;result['source_operator']=file;cases.append(result)
    actual={(v['entity_id'],v['section_id'],v['snapshot_time_utc']) for v in cases};expected={(v['entity_id'],v['id'],t) for v in original['sections'] if v['search_partition_id']==partition for t in original['snapshot_times_utc']}
    if actual!=expected or len(actual)!=16:raise ValueError('Every original partition section/date case exactly once required')
    return cases


from derive_surface_regional_velocity_curtains_v1 import counts


def build(root=ROOT,partition=None):
    op=json.loads((root/OPERATOR).read_bytes())
    if any(op['eligibility'].values()) or [c['id'] for c in op['cohorts']]!=list(COHORTS):raise ValueError('Exact partitioned ocean cohort and no physical/annual/runtime promotion')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned native source or method changed: '+p)
    cases=[]
    for cohort in op['cohorts']:cases.extend(derive_cohort(root,cohort,partition))
    keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=16 or len(keys)!=len(set(keys)):raise ValueError('Complete unique16-case partition batch required')
    report={'schema':'osw.partitioned-ocean-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','source_plan_case_count':64,'batch_partition_id':partition,'operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts(cases),'counts_by_cohort':{slug:counts([c for c in cases if c['cohort_id']==slug]) for slug in COHORTS},'counts_by_current':{owner:counts([c for c in cases if c['entity_id']==owner]) for owner in sorted({c['entity_id'] for c in cases})},'counts_by_primary_threshold_m_s':{str(t):counts([c for c in cases if c['velocity_threshold_m_s']==t]) for t in [.05,.1]},'counts_by_partition':{p:counts([c for c in cases if c['search_partition_id']==p]) for p in sorted({c['search_partition_id'] for c in cases})},'partition_profile_counts_are_independent_observation_counts':False,'cases':cases,'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB spatial output bound exceeded')
    return report,raw


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--partition',required=True,choices=['sac-northern-search','sac-southern-search','tasman-north-bank-search','tasman-south-bank-search']);args=parser.parse_args()
    report,raw=build(partition=args.partition);out=Path('partitioned-ocean-velocity-curtains-v1')/args.partition;out.mkdir(parents=True,exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps({'partition':args.partition,'bytes':len(raw),'counts':report['counts'],'counts_by_current':report['counts_by_current']}),flush=True)
