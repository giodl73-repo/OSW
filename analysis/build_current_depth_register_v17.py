"""Retain Pacific branch section sequences and qualified censored depth evidence."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v16 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v17.json'
RULES='research/current-depth-rules-v17.json'
OUTPUT='research/current-depth-register-v17.json'
CSV='research/current-depth-register-v17.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case.startswith('peru-penven-2005-'):
        required={'entity_id':'current:peru-humboldt','evidence_kind':'published_model_climatology','model_product':'Penven2005_ROMS_climatology','model_analysis_years':[3,10],'model_years_are_calendar_years':False,'branch_section_scope':'partial_named_branch'}
        if case=='peru-penven-2005-pcc-mean':
            required.update({'metric':'reported_vertical_extent','approximate_value_m':50,'source_branch':'peru_coastal_current','section_latitude_band_degrees_north':[-13,-7],'depth_basis':'source_model_jet_description'})
        else:
            sections={'punta-falsa':('Punta Falsa',-6,240),'chimbote':('Chimbote',-9.4,280),'callao':('Callao',-12.1,310),'pisco':('Pisco',-14,470),'san-juan':('San Juan',-15.7,550),'arica':('Arica',-18.6,620)}
            tag=case.removeprefix('peru-penven-2005-pcuc-')
            if tag not in sections:raise ValueError('Unknown PCUC section')
            name,lat,value=sections[tag]
            required.update({'metric':'lower_flow_boundary_depth','approximate_value_m':value,'source_branch':'peru_chile_undercurrent','section_name':name,'section_latitude_degrees_north':lat,'boundary_definition':{'kind':'maximum_depth_of_source_poleward_velocity_isotach','speed_m_s':0.02},'depth_basis':'author_selected_model_velocity_isotach','profile_series_id':'peru-penven-2005-pcuc-six-section-sequence','profile_series_kind':'source_reported_branch_section_sequence','potential_vorticity_prediction_used':False})
    elif case=='peru-chaigneau-2013-poc-mean':
        required={'entity_id':'current:peru-humboldt','metric':'reported_vertical_extent','evidence_kind':'published_observational_mean_summary','lower_bound_m':500,'lower_bound_operator':'>=','lower_bound_exclusive':False,'source_branch':'peru_oceanic_current','branch_section_scope':'partial_named_branch','observing_record_span_years':[2008,2012],'velocity_reconstruction':'author_calibrated_hourly_mean_SADCP_10m_bins_and_spatial_interpolation','depth_basis':'observed_flow_reach_not_terminal_boundary'}
    elif case=='oyashio-qiu-2019-summer-fall':
        required={'entity_id':'current:oyashio','metric':'reported_vertical_extent','evidence_kind':'published_literature_synthesis','upper_bound_m':2000,'upper_bound_exclusive':True,'phase_label':'summer_and_fall','source_phases':['summer','fall'],'branch_section_scope':'regional_slope_flow','depth_basis':'source_seasonal_confinement_upper_bound','calendar_months':None}
    elif case=='kuroshio-extension-qu-2001-deep-component':
        required={'entity_id':'current:kuroshio-extension','metric':'reported_vertical_extent','evidence_kind':'published_observational_climatology','lower_bound_m':1000,'lower_bound_operator':'>=','lower_bound_exclusive':False,'reported_component_depth_m':1000,'bound_interpretation':'inclusive_reach_inferred_from_flow_component_at_reported_depth','branch_section_scope':'regional_deep_flow_and_recirculation_context','archive_product':'World_Ocean_Database_1994','archive_version_is_observation_year':False,'deep_recirculation_influence_retained':True,'depth_basis':'source_reported_deep_flow_component'}
    else:raise ValueError('Unreviewed source case')
    if row.get('section_sampling_month') is not None:raise ValueError('No exact occupation month established')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v16.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v17','status':'PACIFIC_BRANCH_DEPTH_SEQUENCE_AND_CENSORED_REACH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v17.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v17.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Pacific system branches retain distinct depth definitions and six alongshore undercurrent sections. Model years are simulation indices. Observed inclusive reach and seasonal confinement bounds do not establish complete current bottoms.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['model_analysis_years','model_years_are_calendar_years','profile_series_id','profile_series_kind','potential_vorticity_prediction_used','source_phases','reported_component_depth_m','bound_interpretation','archive_product','archive_version_is_observation_year','deep_recirculation_influence_retained'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
