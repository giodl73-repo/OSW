"""Native spatial depth variation for Mauritanian,Baffin and northern subsurface contexts."""
import copy,hashlib,json
from collections import Counter
from pathlib import Path
import native_velocity_depth_curtain_v2 as frozen
from latitude_interval_section_audit_v1 import validate_retained as validate_legacy_latitude
from interval_transverse_section_audit_v1 import validate_retained as validate_legacy_longitude

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/boundary-subsurface-velocity-curtains-operator-v1.json'
COHORTS={'mauritania-baffin':(40,{'current:mauritanian','current:baffin'}),'northern':(20,{'current:pacific-north-subsurface-countercurrent','current:atlantic-north-equatorial-undercurrent'})}
AXES={'mauritania-baffin':'latitude','northern':'longitude'}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def geometry_view(section,config,slug):
    if slug not in AXES or section['section_definition']['fixed_axis']!=AXES[slug]:raise ValueError('Original cohort orientation required')
    axis=AXES[slug]
    (validate_legacy_latitude if axis=='latitude' else validate_legacy_longitude)(section,config)
    if 'source_section_geometry' in section:raise ValueError('Original legacy source must have no mixed tag')
    view=copy.deepcopy(section);view['source_section_geometry']=axis
    return view


def derive_cohort(root,cohort):
    slug=cohort['id']
    if slug not in COHORTS:raise ValueError('Only predeclared boundary/subsurface contexts allowed')
    expected_count,owners=COHORTS[slug];file='research/'+slug+'-interval-depth-sections-operator-v1.json'
    if cohort['source_operator']!=file or len(cohort['section_files'])!=expected_count or len(set(cohort['section_files']))!=expected_count:raise ValueError('Exact original cohort and source operator required')
    original=json.loads((root/file).read_bytes())
    if set(original['currents'])!=owners or any(original['eligibility'].values()):raise ValueError('Original direct owners and non-promotion required')
    cases=[]
    for p in cohort['section_files']:
        raw=(root/p).read_bytes();section=json.loads(raw)
        if section['entity_id'] not in owners or section['operator_file']!=file or section['operator_sha256']!=digest((root/file).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Pinned original owner,operator and exact snapshot required')
        config={**original,**original['currents'][section['entity_id']]}
        view=geometry_view(section,config,slug);result=frozen.curtain(view,config,p);result['geometry_adapter']='LEGACY_'+AXES[slug].upper()+'_INTERVAL_VALIDATED_THEN_IN_MEMORY_TAG_ONLY';result['source_sha256']=digest(raw);result['cohort_id']=slug;result['source_operator']=file;cases.append(result)
    actual={(v['entity_id'],v['section_id'],v['snapshot_time_utc']) for v in cases};expected={(v['entity_id'],v['id'],t) for v in original['sections'] for t in original['snapshot_times_utc']}
    if actual!=expected or len(actual)!=expected_count:raise ValueError('Every original section/date case exactly once required')
    return cases


from derive_surface_regional_velocity_curtains_v1 import counts


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    if any(op['eligibility'].values()) or [c['id'] for c in op['cohorts']]!=list(COHORTS):raise ValueError('Exact two boundary/subsurface cohorts and no physical/annual/runtime promotion')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned native source or method changed: '+p)
    cases=[]
    for cohort in op['cohorts']:cases.extend(derive_cohort(root,cohort))
    keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=60 or len(keys)!=len(set(keys)):raise ValueError('Complete unique60-case cohort required')
    report={'schema':'osw.boundary-subsurface-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts(cases),'counts_by_cohort':{slug:counts([c for c in cases if c['cohort_id']==slug]) for slug in COHORTS},'counts_by_current':{owner:counts([c for c in cases if c['entity_id']==owner]) for owner in sorted({c['entity_id'] for c in cases})},'counts_by_primary_threshold_m_s':{str(t):counts([c for c in cases if c['velocity_threshold_m_s']==t]) for t in [.05,.1]},'cases':cases,'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB spatial output bound exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('boundary-subsurface-velocity-curtains-v1');out.mkdir(exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps({k:report[k] for k in ['counts','counts_by_cohort','counts_by_current','new_ocean_field_requests','new_reference_inventory_rows','volume_estimates']}),flush=True)
