"""Append reach scales, property cores and a selected WSC stream-tube domain."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v11 as previous

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v12.json'
RULES='research/current-depth-rules-v12.json'
OUTPUT='research/current-depth-register-v12.json'
CSV='research/current-depth-register-v12.csv'
validate_reference=previous.validate_reference


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No width join or independent repeat established')
    case=row['source_case_id'];entity=row['entity_id']
    if case=='loop-lopera-2025-literature':
        if entity!='current:loop' or row['metric']!='reported_vertical_extent' or row['range_m']!=[1000,1200] or row['evidence_kind']!='published_literature_synthesis':raise ValueError('Loop reach is not a subsurface occupied band')
        if row.get('campaign_window') is not None or row.get('climatology_years') is not None or row['calendar_months'] is not None:raise ValueError('Literature reach does not inherit particle experiment dates')
    elif case=='alaska-tang-2014-sept2008':
        if entity!='current:alaska' or row['metric']!='core_depth' or row['approximate_value_m']!=150 or row['evidence_kind']!='published_geostrophic_section_summary':raise ValueError('Alaska Current core is not eddy extent or coastal-current depth')
        if row.get('core_definition')!={'kind':'source_geostrophic_velocity_core'} or row.get('velocity_reconstruction')!='source_geostrophic_estimate' or row.get('section_sampling_month')!='2008-09':raise ValueError('Preserve geostrophic reconstruction and September2008 context')
        if row.get('survey_window')!={'start':'2008-09-17','end':'2008-09-18'} or row.get('window_role')!='paired_transects_not_exact_core_occupation':raise ValueError('Paired seismic sections are not exact core occupation timing')
    elif case=='ncc-tonani-2019-trench-summary':
        if entity!='current:norwegian-coastal' or row['metric']!='reported_vertical_extent' or row['range_m']!=[50,100] or row['evidence_kind']!='published_literature_synthesis' or row.get('source_wording_class')!='upper_layer_depth_scale':raise ValueError('Retain regional upper-layer scale')
        if row.get('section_sampling_month') is not None or row.get('climatology_years') is not None or row['calendar_months'] is not None:raise ValueError('Regional description is not model validation or display-map timing')
    elif case=='wsc-kolas-fer-2018-aug2015-stream-tubes':
        if entity!='current:west-spitsbergen' or row['metric']!='transport_selected_depth_extent' or row['range_m']!=[50,500] or row['evidence_kind']!='published_geostrophic_stream_tube_summary':raise ValueError('Selected stream-tube depth domain is not full-flow thickness or AW table interval')
        if row.get('source_branch')!='svalbard_branch' or row.get('branch_section_scope')!='partial_named_branch' or row.get('section_names')!=['A','B','C']:raise ValueError('Retain partial Svalbard branch section scope')
        selection={'vertical':'source_Atlantic_Water_layer_or_seabed','water_mass':{'practical_salinity_operator':'>','practical_salinity':34.88,'absolute_salinity_operator':'>','absolute_salinity_g_kg':35.05,'conservative_temperature_operator':'>=','conservative_temperature_c':2},'tube1_lateral':'first_layer_integrated_velocity_drop_below_layer_thickness_times_background_speed','tube1_background_speed_m_s':0.04,'tube1_sensitivity_speeds_m_s':[0.02,0.08],'tube2_volume_flux_constraint_Sv':1.3,'tube2_relative_tolerance':0.1}
        if row.get('transport_selection')!=selection:raise ValueError('Retain water-mass and both alternative lateral operators')
        if row.get('section_sampling_month')!='2015-08' or row.get('campaign_window')!={'start':'2015-08-12','end':'2015-08-21'} or row.get('window_role')!='whole_campaign_not_exact_section_occupation':raise ValueError('Retain snapshot and whole-cruise distinction')
        if row.get('velocity_reconstruction')!='absolute_geostrophic_referenced_to_detided_LADCP_at_100dbar' or row.get('pressure_to_depth_conversion_performed') is not False:raise ValueError('Reference pressure is not a measured flow boundary')
    elif case=='redsea-bower-2005-winter-product-cores':
        if entity!='current:red-sea-saline-overflow' or row['metric']!='core_depth' or row['range_m']!=[400,800] or row['evidence_kind']!='published_campaign_hydrographic_core':raise ValueError('Distinct product cores are not a continuous flow band')
        if row.get('core_definition')!={'kind':'salinity_maxima_of_distinct_equilibrated_product_waters'} or row['phase_label']!='winter_REDSOX2001':raise ValueError('Salinity maxima are distinct from velocity cores and summer survey')
        if row.get('campaign_window')!={'start':'2001-02-05','end':'2001-03-15'} or row.get('window_role')!='whole_campaign_not_exact_product_core_occupation' or row.get('section_sampling_month') is not None:raise ValueError('Retain full winter campaign, not invented station dates')
    else:raise ValueError('Unreviewed source case')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v11.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v12','status':'SCOPED_REACH_CORE_AND_STREAM_TUBE_DEPTH_REFERENCES',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v12.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v12.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Ranges of reach scales, depth bands across property cores and selected stream-tube domains remain distinct. Partial named branches and source reconstruction methods are explicit.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['transport_selection','survey_window','source_wording_class']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
