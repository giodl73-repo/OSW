"""Retain historical instrument reach and regime-limited Guiana observations."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v24 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v25.json'
RULES='research/current-depth-rules-v25.json'
OUTPUT='research/current-depth-register-v25.json'
CSV='research/current-depth-register-v25.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No compatible width or independent repeat established')
    common={'metric':'reported_vertical_extent','lower_bound_operator':'>=','lower_bound_exclusive':False}
    case=row['source_case_id']
    if case=='jutland-svansson-1989-s66-station41':
        required={'entity_id':'current:jutland','evidence_kind':'institutional_historical_current_record','lower_bound_m':19,'depth_basis':'inclusive_reach_from_named_record_at_stated_instrument_depth','source_station_id':'41','reported_current_meter_depth_m':19,'source_station_position_degrees_minutes':{'latitude_north':[57,28.8],'longitude_east':[8,11.8]},'survey_year':1966,'phase_label':'boreal_summer','temporal_operator':'source_daily_mean_current_record','source_figure_panel':'Figure5_top_record','branch_section_scope':'local_outer_Skagerrak_Jutland_record','source_access_scope':'primary_institutional_indexed_figure_caption_and_station_label'}
    elif case=='guiana-baklouti-2007-m2-later-northwestward-regime':
        required={'entity_id':'current:guiana','evidence_kind':'published_mooring_regime_summary','lower_bound_m':118,'depth_basis':'inclusive_reach_at_valid_ADCP_limit_in_reported_flow_regime','source_station_id':'M2','mooring_record_window':{'start_date':'2003-10-06','end_date':'2004-02-18'},'phase_label':'post_transition_northwestward_regime','regime_transition_description':'site_and_depth_dependent_late_November_to_mid_December_2003','source_station_position_degrees_minutes':{'latitude_north':[5,25.16],'longitude_west':[50,56.71]},'source_station_water_depth_m':150.3,'ADCP_mounting_depth_m':130,'valid_ADCP_depth_range_m':[13,118],'ADCP_cell_height_m':3,'sampling_limit_is_flow_boundary':False,'current_persistence_interpretation':'episodic_regime_not_year_round_current','source_current_name':'Guyana_Current','branch_section_scope':'regional_French_Guiana_shelf_edge_northwestward_regime','source_access_scope':'primary_publisher_full_HTML'}
    else:raise ValueError('Unreviewed source case')
    for k in ['section_sampling_month','calendar_months','climatology_years']:
        if row.get(k) is not None:raise ValueError('No monthly/annual climatology established')
    for k,v in dict(common,**required).items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v24.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v25','status':'JUTLAND_HISTORICAL_RECORD_AND_EPISODIC_GUIANA_ADCP_REACH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v25.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v25.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' A named historical instrument record supports inclusive reach at its measurement depth. Guiana later-regime reach is limited to the deepest valid ADCP sample, with oscillatory early flow and non-permanent current identity explicit; mounting depth and bathymetry do not supply flow boundaries.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['reported_current_meter_depth_m','source_station_position_degrees_minutes','survey_year','source_figure_panel','mooring_record_window','regime_transition_description','ADCP_mounting_depth_m','valid_ADCP_depth_range_m','ADCP_cell_height_m','current_persistence_interpretation','source_current_name'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
