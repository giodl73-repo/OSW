"""Retain sampled Adriatic coastal water and observed-mean reach definitions."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v23 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v24.json'
RULES='research/current-depth-rules-v24.json'
OUTPUT='research/current-depth-register-v24.json'
CSV='research/current-depth-register-v24.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No same-source width or independent repeat established')
    case=row['source_case_id']
    if case=='western-adriatic-bernardi-aubry-2018-odw2012':
        required={'entity_id':'current:western-adriatic','metric':'sampled_water_mass_depth_band','evidence_kind':'published_hydrographic_sample_group','range_m':[0.5,15],'depth_basis':'source_sampled_water_mass_depth_group','water_mass_component':'river_influenced_WACC','campaign_window':{'start_date':'2012-03-23','end_date':'2012-04-02'},'window_role':'whole_campaign_not_exact_boundary_occupation','classification_properties':['temperature','salinity','dissolved_oxygen'],'sample_collection':'CTD_rosette_Niskin','upper_endpoint_is_physical_flow_boundary':False,'lower_endpoint_is_physical_flow_boundary':False,'continuous_velocity_layer_established':False,'branch_section_scope':'southern_Adriatic_regional_coastal_water_component','source_access_scope':'primary_publisher_full_HTML'}
    elif case=='east-adriatic-vilibic-2018-a4-residual-mean':
        required={'entity_id':'current:east-adriatic','metric':'reported_vertical_extent','evidence_kind':'published_mooring_mean_figure_presence','lower_bound_m':30,'lower_bound_operator':'>=','lower_bound_exclusive':False,'depth_basis':'conservative_inclusive_reach_from_observed_mean_vector_presence','source_station_id':'A4','source_station_water_depth_m':56,'averaging_period':{'start_date':'2015-02-01','end_date':'2015-04-01'},'deployment_window_description':'late_November_2014_to_early_July_2015','graphical_read_depth_m':30,'graphical_read_operator':{'panel':'A4','series':'observed_ADCP_mean_vectors_left_set','depth_tick_m':30,'read_kind':'nonzero_vector_presence_only','excluded_graphics':['standard_deviation_ellipses','blue_model_vectors'],'velocity_digitized':False,'statistical_significance_established':False},'source_depth_axis_convention':'negative_vertical_coordinate_labels_read_as_positive_depth','sampling_limit_is_flow_boundary':False,'branch_section_scope':'local_northeastern_Adriatic_A4_observed_mean','source_access_scope':'primary_publisher_HTML_and_original_figure_pixels'}
    else:raise ValueError('Unreviewed source case')
    for k in ['section_sampling_month','calendar_months','phase_label','climatology_years']:
        if row.get(k) is not None:raise ValueError('No monthly/annual seasonal profile established')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v23.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v24','status':'ADRIATIC_SAMPLED_COASTAL_COMPONENT_AND_OBSERVED_MEAN_REACH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v24.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v24.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Adriatic water-mass sample-depth bands do not establish continuous flow layers or endpoint thickness. A conservative observed-mean figure-presence bound retains its labeled depth, series, averaging dates and lack of statistical significance; it is not station bathymetry, model depth or terminal flow depth.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['classification_properties','sample_collection','upper_endpoint_is_physical_flow_boundary','lower_endpoint_is_physical_flow_boundary','continuous_velocity_layer_established','source_station_id','source_station_water_depth_m','deployment_window_description','graphical_read_depth_m','graphical_read_operator','source_depth_axis_convention'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
