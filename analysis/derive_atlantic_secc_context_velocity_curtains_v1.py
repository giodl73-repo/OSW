"""Two non-additive context exports from the same sixteen original native sections."""
import copy,hashlib,json
from pathlib import Path
import atlantic_secc_depth_contexts_v1 as original
import native_velocity_depth_curtain_v2 as frozen
from derive_surface_regional_velocity_curtains_v1 import counts

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/atlantic-secc-context-velocity-curtains-operator-v1.json'
SOURCE_OPERATOR='research/atlantic-secc-multi-context-depth-sections-operator-v1.json'
OWNER='current:atlantic-south-equatorial-countercurrent'
CONTEXTS=('shallow','deep')


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode()


def context_view(section,config,context):
    if context not in CONTEXTS:raise ValueError('Explicit original context required')
    if section['schema']!=original.SCHEMA or section['entity_id']!=OWNER or config['entity_id']!=OWNER or section['source_section_geometry']!='longitude' or section['section_definition']['fixed_axis']!='longitude':raise ValueError('Exact original Atlantic SECC source required')
    original.validate_contexts(section,config)
    view=copy.deepcopy(section);view['diagnosis']=copy.deepcopy(section['context_diagnoses'][context]['diagnosis'])
    restored=copy.deepcopy(view);restored['diagnosis']=copy.deepcopy(restored['context_diagnoses']['shallow']['diagnosis'])
    if restored!=section:raise ValueError('Diagnostic view must restore every source field exactly')
    return view,original.context_config(config,context)


def source_curtain(section,config,file,context):
    view,cfg=context_view(section,config,context)
    result=frozen.curtain(view,cfg,file)
    result.update(diagnostic_context_id=context,source_default_diagnostic_context_id='shallow',selection_depth_interval_m=copy.deepcopy(cfg['selection_depth_interval_m']),core_search_depth_interval_m=copy.deepcopy(cfg['core_search_depth_interval_m']),vertical_contexts_are_additive=False,contexts_are_independent_observations=False,source_arrays_changed=False,diagnostic_view_changes_source_bytes=False,source_context_diagnosis_sha256=digest(encode(section['context_diagnoses'][context]['diagnosis'])))
    return result


def build(root=ROOT,context=None):
    if context not in CONTEXTS:raise ValueError('Explicit shallow or deep context required')
    op=json.loads((root/OPERATOR).read_bytes())
    if any(op['eligibility'].values()) or op['contexts']!=list(CONTEXTS) or op['source_operator']!=SOURCE_OPERATOR:raise ValueError('Exact two contexts and no physical promotion required')
    for file,pin in op['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Pinned native source or method changed: '+file)
    config=json.loads((root/SOURCE_OPERATOR).read_bytes())
    if set(config['currents'])!={OWNER} or any(config['eligibility'].values()):raise ValueError('One original canonical owner required')
    cfg={**config,**config['currents'][OWNER]};files=op['section_files']
    if len(files)!=16 or len(set(files))!=16:raise ValueError('Sixteen unique original source cases required')
    definitions={d['id']:d for d in config['sections']};cases=[]
    for file in files:
        raw=(root/file).read_bytes();section=json.loads(raw)
        if section['operator_file']!=SOURCE_OPERATOR or section['operator_sha256']!=digest((root/SOURCE_OPERATOR).read_bytes()) or section['source_returned_timestamp_utc']!=section['snapshot_time_utc'] or section['section_definition']!=definitions[section['section_definition']['id']]:raise ValueError('Exact source operator, definition and timestamp required')
        result=source_curtain(section,cfg,file,context);result['source_sha256']=digest(raw);result['source_operator']=SOURCE_OPERATOR;cases.append(result)
    actual={(v['entity_id'],v['section_id'],v['snapshot_time_utc']) for v in cases};expected={(d['entity_id'],d['id'],t) for d in config['sections'] for t in config['snapshot_times_utc']}
    if actual!=expected or len(actual)!=16:raise ValueError('Complete original section/date matrix required')
    report={'schema':'osw.atlantic-secc-context-velocity-depth-curtains.v1','status':'NON_ADDITIVE_CONTEXT_GEOMETRY_NOT_INDEPENDENT_CURRENT_BODIES','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'entity_id':OWNER,'diagnostic_context_id':context,'source_default_diagnostic_context_id':'shallow','source_plan_case_count':16,'source_context_case_count':16,'vertical_contexts_are_additive':False,'contexts_are_independent_observations':False,'counts':counts(cases),'cases':cases,'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed 2.4MB context output cap exceeded')
    return report,raw


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--context',required=True,choices=CONTEXTS);args=parser.parse_args();report,raw=build(context=args.context);out=Path('atlantic-secc-context-velocity-curtains-v1')/args.context;out.mkdir(parents=True,exist_ok=True);(out/'curtains.json').write_bytes(raw);print(json.dumps({'context':args.context,'bytes':len(raw),'counts':report['counts']}),flush=True)
