"""Keep Indian Ocean reach, transport domains and scale distances scientifically distinct."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v18 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v19.json'
RULES='research/current-depth-rules-v19.json'
OUTPUT='research/current-depth-register-v19.json'
CSV='research/current-depth-register-v19.csv'

def validate_reference(row,identities,metrics):
    if row['metric']=='reported_vertical_scale_length':
        if row['vertical_datum']!='not_applicable_scale_distance':raise ValueError('Scale is a distance, not a sea-surface depth')
        previous.validate_reference(dict(row,vertical_datum='local_sea_surface_positive_down'),identities,metrics)
    else:previous.validate_reference(row,identities,metrics)

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case=='indian-sec-premchand-1976-atlantis1965':
        required={'entity_id':'current:indian-south-equatorial','metric':'reported_vertical_extent','evidence_kind':'published_geostrophic_regional_summary','lower_bound_m':500,'lower_bound_operator':'>=','lower_bound_exclusive':False,'campaign_window':{'start_date':'1965-04-25','end_date':'1965-06-20'},'window_role':'whole_cruise_not_exact_cross_section','geostrophic_reference_pressure_dbar':1000,'pressure_to_depth_conversion_performed':False,'depth_basis':'source_regional_geostrophic_flow_reach','bound_interpretation':'inclusive_reach_inferred_from_flow_features_at_reported_depth','branch_section_scope':'western_basin_regional_flow_and_branches'}
    elif case=='south-indian-stramma-1992-transport':
        required={'entity_id':'current:south-indian','metric':'transport_selected_depth_extent','evidence_kind':'published_geostrophic_transport_summary','approximate_value_m':1000,'source_access_scope':'primary_publisher_indexed_abstract','source_feature_name':'South Indian Ocean Current','depth_basis':'source_transport_integration_limit','reference_surface_context':'Deep potential-density reference surfaces, not a fixed no-motion depth or current bottom.'}
    elif case=='west-australian-andrews-1977-scale':
        required={'entity_id':'current:west-australian','metric':'reported_vertical_scale_length','evidence_kind':'published_observed_regional_scale','approximate_value_m':370,'source_scale_definition_recovered':False,'exponential_decay_assumed':False,'source_naming_convention':'Andrews1977_Naturaliste_cyclonic_stream','branch_section_scope':'historical_regional_definition_not_entire_offshore_return','source_access_scope':'primary_publisher_indexed_abstract','survey_years':[1972,1973],'phase_label':'austral_summer','depth_basis':'source_reported_vertical_scale_not_boundary','calendar_months':None}
    else:raise ValueError('Unreviewed source case')
    if row.get('section_sampling_month') is not None:raise ValueError('No exact section month established')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v18.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v19','status':'INDIAN_GEOSTROPHIC_REACH_TRANSPORT_DOMAIN_AND_VERTICAL_SCALE',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v19.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v19.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Indian Ocean references distinguish regional geostrophic reach, transport integration depth and a source-reported scale distance. Distinct SICC/SECC identities and historical WAC naming do not authorize whole-route depth inheritance.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['reference_surface_context','source_scale_definition_recovered','exponential_decay_assumed','survey_years'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
