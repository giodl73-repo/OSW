"""Append equatorial depth cases with inclusive bounds and explicit core kinds."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v8 as previous

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v9.json'
RULES='research/current-depth-rules-v9.json'
OUTPUT='research/current-depth-register-v9.json'
CSV='research/current-depth-register-v9.csv'


def validate_reference(row,identities,metrics):
    operator=row.get('lower_bound_operator')
    if operator is None:return previous.validate_reference(row,identities,metrics)
    if row.get('lower_bound_m') is None or operator not in ['>','>=']:
        raise ValueError('Lower-bound operator requires a supported numeric bound')
    exclusive=operator=='>'
    if row.get('lower_bound_exclusive') is not exclusive:raise ValueError('Bound operator and exclusivity disagree')
    # The frozen validator checks all non-inclusivity constraints. Preserve original evidence.
    previous.validate_reference(dict(row,lower_bound_exclusive=True),identities,metrics)


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No independent repeat or compatible width join established')
    case=row['source_case_id'];entity=row['entity_id']
    if case=='atlantic-secc-bourles-1999-march1994':
        if entity!='current:atlantic-south-equatorial-countercurrent' or row.get('section_sampling_month')!='1994-03' or row.get('section_longitude_degrees_east')!=-30 or row.get('section_latitude_band_degrees_north')!=[-8,-6] or row['evidence_kind']!='published_observed_section':raise ValueError('CITHER2 section support changed')
        if row['id'].endswith('-reach'):
            if row['metric']!='reported_vertical_extent' or row.get('lower_bound_m')!=400 or row.get('lower_bound_operator')!='>=' or row.get('lower_bound_exclusive') is not False:raise ValueError('At least400m must remain inclusive lower bound')
        else:
            expected={'atlantic-secc-bourles-1999-shallow-core':40,'atlantic-secc-bourles-1999-deep-core':240}
            if row['id'] not in expected or row['metric']!='core_depth' or row['approximate_value_m']!=expected[row['id']] or row.get('core_definition')!={'kind':'maximum_eastward_velocity'}:raise ValueError('Distinct observed velocity cores changed')
    elif case=='atlantic-necc-bourles-1999-march1994':
        if entity!='current:atlantic-north-equatorial-countercurrent' or row['metric']!='core_depth' or row['approximate_value_m']!=60 or row.get('section_sampling_month')!='1994-03' or row.get('core_definition')!={'kind':'maximum_eastward_velocity'}:raise ValueError('NECC velocity core changed')
    elif case in ['atlantic-necc-sivkov-2021-setting','atlantic-neuc-sivkov-2021-setting']:
        expected=('current:atlantic-north-equatorial-countercurrent',[0,100]) if 'necc-' in case else ('current:atlantic-north-equatorial-undercurrent',[100,300])
        if (entity,row['range_m'])!=expected or row['metric']!='reported_flow_depth_band' or row['evidence_kind']!='published_literature_synthesis' or row.get('section_sampling_month') is not None:raise ValueError('Setting summary cannot inherit Ioffe2000 occupation dates')
    elif case=='atlantic-euc-philander-2001-western-summary':
        if entity!='current:atlantic-equatorial-undercurrent' or row['metric']!='core_depth' or row['approximate_value_m']!=100 or row['evidence_kind']!='published_literature_synthesis' or row.get('core_definition')!={'kind':'velocity_core_in_thermocline'}:raise ValueError('Western Atlantic summary is not a basin-wide fixed core')
    elif case=='pacific-neuc-li-2018-argo-135-140E':
        expected={'NEUCS':300,'NEUCM':450,'NEUCN':600}
        if entity!='current:pacific-north-equatorial-undercurrent' or row.get('source_jet') not in expected or row['approximate_value_m']!=expected[row['source_jet']] or row['metric']!='upper_flow_boundary_depth':raise ValueError('Pacific jet upper boundaries changed')
        if row['evidence_kind']!='published_geostrophic_climatology' or row.get('climatology_years')!=[2004,2014] or row.get('section_longitude_band_degrees_east')!=[135,140] or row.get('reference_dataset')!='Roemmich_Gilson_Argo' or row.get('velocity_reconstruction')!='P_vector_and_thermal_wind':raise ValueError('Argo reconstruction is distinct from LICOM simulation')
    elif case=='pacific-secc-rotschi-1972-170E-threshold-summary':
        if entity!='current:pacific-south-equatorial-countercurrent' or row['metric']!='core_lower_boundary_depth' or row['approximate_value_m']!=300 or row.get('section_longitude_degrees_east')!=170 or row.get('core_definition')!={'kind':'source_geostrophic_speed_threshold','speed_m_s':0.1,'operator':'>'}:raise ValueError('General threshold reach cannot become whole-current bottom')
    elif case=='pgw-pous-2004-gogp99-thermohaline-core':
        if entity!='current:persian-gulf-saline-overflow' or row['metric']!='core_depth' or row['approximate_value_m']!=220 or row.get('core_definition')!={'kind':'thermohaline_maxima','sigma0_kg_m3':26.5}:raise ValueError('PGW property core is not a maximum-speed core')
        if row.get('campaign_window')!={'start':'1999-10-08','end':'1999-11-10'} or row.get('window_role')!='whole_campaign_not_exact_core_occupation':raise ValueError('Retain whole-campaign temporal scope')
    else:raise ValueError('Unreviewed source case')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v8.py',RULES,SOURCE,'research/source-data/li-neuc-2018/journal-article.xml']:
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
    return {'schema':'osw.current-depth-register.v9','status':'SCOPED_EQUATORIAL_DEPTH_REFERENCES_WITH_INCLUSIVE_BOUNDS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v9.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v9.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Inclusive lower bounds preserve at-least statements. Thermohaline and velocity cores remain separately defined; named jets do not fill other families or basin identities.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['lower_bound_operator','source_jet','reference_dataset','velocity_reconstruction',
              'section_longitude_band_degrees_east','campaign_window','window_role']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')


if __name__=='__main__':
    d=build();(ROOT/OUTPUT).write_bytes((json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf8'));(ROOT/CSV).write_bytes(csv_bytes(d));print(json.dumps(d['counts']))
