"""Append regional coastal references without promoting seasonal branches to whole routes."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v9 as previous

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v10.json'
RULES='research/current-depth-rules-v10.json'
OUTPUT='research/current-depth-register-v10.json'
CSV='research/current-depth-register-v10.csv'
validate_reference=previous.validate_reference


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case=='zeehan-cresswell-2000-dec1997':
        if row['entity_id']!='current:zeehan' or row['metric']!='reported_vertical_extent' or row.get('lower_bound_m')!=300 or row.get('lower_bound_operator')!='>' or row.get('lower_bound_exclusive') is not True:
            raise ValueError('Below300m is a censored strict lower bound')
        if row.get('section_sampling_month')!='1997-12' or row.get('sampling_limit_is_flow_boundary') is not False or row['evidence_kind']!='published_observed_section':
            raise ValueError('Retain December1997 Strahan observation support')
    elif case=='monsoon-anutaliya-2022-winter-summary':
        if row['entity_id']!='current:monsoon' or row['metric']!='reported_vertical_extent' or row['approximate_value_m']!=1000 or row['evidence_kind']!='published_literature_synthesis':
            raise ValueError('Winter branch reach is a literature summary')
        if row.get('source_branch')!='winter_monsoon_current' or row.get('branch_section_scope')!='partial_seasonal_branch' or row['phase_label']!='winter_monsoon' or row['calendar_months']!=[11,12,1,2]:
            raise ValueError('Do not promote winter reach to all monsoon branches')
        if row.get('campaign_window') is not None or row.get('section_sampling_month') is not None:
            raise ValueError('Literature depth does not inherit PIES observation dates')
    elif case=='algerian-taupier-letage-2003-meander-aw':
        if row['entity_id']!='current:algerian' or row['metric']!='reported_vertical_thickness' or row['approximate_value_m']!=200 or row['evidence_kind']!='published_literature_synthesis' or row.get('branch_section_scope')!='typical_meander_atlantic_water_layer':
            raise ValueError('Typical meander AW layer is distinct from eddy depth')
        if row.get('campaign_window') is not None or row.get('section_sampling_month') is not None:
            raise ValueError('Introductory thickness has no ELISA occupation date')
    elif case in ['wicc-shetye-1991-southern-winter','wicc-shetye-1991-northern-winter']:
        latitude,value=(10,200) if 'southern' in case else (22,400)
        if row['entity_id']!='current:west-india-coastal' or row['metric']!='reported_vertical_extent' or row['approximate_value_m']!=value or row.get('section_latitude_degrees_north')!=latitude or row['evidence_kind']!='published_observed_section_summary':
            raise ValueError('WICC regional depth descriptions cannot be interchanged')
        if row.get('campaign_window')!={'start_month':'1987-12','end_month':'1988-01'} or row.get('window_role')!='whole_campaign_not_exact_section_occupation' or row.get('section_sampling_month') is not None:
            raise ValueError('Exact regional occupation timing unknown')
        if row.get('source_access_scope')!='primary_publisher_abstract' or row['phase_label']!='northeast_monsoon':
            raise ValueError('Retain primary abstract access and winter phase')
    else:raise ValueError('Unreviewed source case')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v9.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v10','status':'SCOPED_COASTAL_REGIONAL_AND_WINTER_BRANCH_DEPTH_REFERENCES',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v10.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v10.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Regional variation within one campaign is not seasonal extrema. Winter-branch reach remains partial, and current-meander layer thickness is distinct from developed eddy extent.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['source_branch','source_access_scope']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
