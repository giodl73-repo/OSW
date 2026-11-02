"""Retain parent-system seasonal context, source isotachs and qualitative near-zero depth separately."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v15 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v16.json'
RULES='research/current-depth-rules-v16.json'
OUTPUT='research/current-depth-register-v16.json'
CSV='research/current-depth-register-v16.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case.startswith('ligurian-berta-2018-northern-summary-'):
        phase=case.removeprefix('ligurian-berta-2018-northern-summary-')
        if phase not in ['winter','summer']:raise ValueError('Unknown literature season')
        required={'entity_id':'current:ligurian','metric':'reported_vertical_extent' if phase=='winter' else 'reported_vertical_thickness','evidence_kind':'published_literature_synthesis','approximate_value_m':450 if phase=='winter' else 250,'phase_label':phase,'source_feature_name':'Northern Current (Liguro-Provencal-Catalan Current)','identity_relationship':'regional_segment_of_source_named_system','branch_section_scope':'parent_system_context_not_segment_profile','depth_basis':'source_seasonal_literature_description','source_observation_window_assigned':False,'section_sampling_month':None,'calendar_months':None}
    elif case in ['balearic-garcia-ladona-1996-fe89-a','balearic-garcia-ladona-1996-fe89-fdc']:
        group=case.endswith('-fdc')
        required={'entity_id':'current:balearic','metric':'lower_flow_boundary_depth','evidence_kind':'published_geostrophic_section_group_summary' if group else 'published_geostrophic_section','approximate_value_m':200 if group else None,'range_m':None if group else [100,150],'section_labels':['F','D','C'] if group else ['A'],'section_group_summary':group,'boundary_definition':{'kind':'source_geostrophic_current_isotach','speed_m_s':0.05},'geostrophic_reference_pressure_dbar':600,'ADCP_deep_reference_depth_m':300,'depth_basis':'author_selected_velocity_isotach','pressure_to_depth_conversion_performed':False,'campaign_window':{'start_date':'1989-06-04','end_date':'1989-06-19'},'window_role':'whole_cruise_not_exact_cross_section','section_sampling_month':'1989-06'}
    elif case=='rim-podymov-2023-near-halt-band':
        required={'entity_id':'current:black-sea-rim','metric':'reported_near_zero_flow_depth','evidence_kind':'published_literature_synthesis','range_m':[250,300],'velocity_threshold_m_s':None,'exact_zero_established':False,'depth_basis':'source_qualitative_near_halt_description','source_observation_window_assigned':False,'section_sampling_month':None}
        if not row.get('underlying_citation','').startswith('Titov(1980)'):raise ValueError('Retain unreviewed underlying citation')
    else:raise ValueError('Unreviewed source case')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v15.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row,root)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v16','status':'SEASONAL_CONTEXT_ISOTACH_SECTIONS_AND_NEAR_HALT_DEPTH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v16.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v16.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Seasonal parent-system context is distinct from segment profiles. Author isotach boundaries retain reference levels and section support. Qualitative near-halt depth does not establish exact zero or a full-flow bottom.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_feature_name','identity_relationship','boundary_definition','geostrophic_reference_pressure_dbar','ADCP_deep_reference_depth_m','section_labels','section_group_summary','velocity_threshold_m_s','exact_zero_established','underlying_citation','source_observation_window_assigned'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
