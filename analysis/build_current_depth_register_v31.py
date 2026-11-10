"""Retain separate western/eastern SPC geostrophic depth diagnostics."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v30 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v31.json'
RULES='research/current-depth-rules-v31.json'
OUTPUT='research/current-depth-register-v31.json'
CSV='research/current-depth-register-v31.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v1.json'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    common={'entity_id':'current:south-pacific','metric':'reported_vertical_extent','evidence_kind':'published_geostrophic_section','temporal_operator':'source_quasi_synoptic_hydrographic_section','source_access_scope':'original_author_repository_PDF_prose_and_tables','same_source_width_reference_id':None,'independent_observation_count_claimed':False}
    case=row['source_case_id']
    if case=='south-pacific-stramma-1995-baldrige-d-march1990':
        required={'approximate_value_m':500,'section_sampling_month':'1990-03','source_section_id':'d','source_research_vessel':'Baldrige','section_nominal_longitude_degrees_east':-170,'source_STF_bracketing_latitude_range_degrees_north':[-43.5,-42.5],'source_STF_bracket_longitude_degrees_east':-170.6,'phase_label':'late_austral_summer','depth_basis':'approximate_depth_of_source_reported_nonzero_geostrophic_flow','source_depth_phrase':'nearly_500m','source_speed_context_cm_s':4,'geostrophic_reference_definition':{'kind':'potential_density_sigma_2','sigma_2_kg_m3':36.75,'source_table_depth_range_m':[1800,1840],'role':'assumed_processing_reference_not_flow_boundary'},'branch_section_scope':'western_SPC_Baldrige_section_d'}
    elif case=='south-pacific-stramma-1995-deryugin-q1-july1968':
        required={'approximate_value_m':None,'range_m':[200,300],'section_sampling_month':'1968-07','source_section_id':'q1','source_research_vessel':'Deryugin','section_nominal_longitude_degrees_east':-97,'source_STF_bracketing_latitude_range_degrees_north':[-35.4,-34.7],'phase_label':'austral_winter','depth_basis':'source_approximate_regional_geostrophic_flow_extent','source_table2_reference_depth_summary_m':[780,1510],'source_table2_reference_flag':'deepest_available_depth','figure5_reference_policy':'starts_sigma2_36.75_in_southwest_rises_to_250m_near_coast','branch_section_scope':'eastern_SPC_Deryugin_first_STF_intersection'}
    else:raise ValueError('Unreviewed source case')
    for k,v in dict(common,**required).items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)
    for k in ['lower_bound_m','upper_bound_m','calendar_months','climatology_years','section_sampling_window','section_latitude_degrees_north']:
        if row.get(k) is not None:raise ValueError('No rounded reach bound, exact axis/day or seasonal climatology established')

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v30.py',RULES,SOURCE,'research/current-depth-member-index-v1.json']:
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
    return {'schema':'osw.current-depth-register.v31','status':'SOUTH_PACIFIC_REGIONAL_GEOSTROPHIC_DEPTH_VARIATION',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v31.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v31.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' South Pacific Current nearly500m nonzero-flow depth and eastern200–300m extent interval retain separate geostrophic sections/years. Neither gives physical full-flow thickness or a seasonal envelope.',
            'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_research_vessel','source_STF_bracketing_latitude_range_degrees_north','source_STF_bracket_longitude_degrees_east','source_depth_phrase','source_speed_context_cm_s','geostrophic_reference_definition','source_table2_reference_depth_summary_m','source_table2_reference_flag','figure5_reference_policy','source_site_id'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
