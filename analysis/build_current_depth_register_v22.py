"""Retain Australian seasonal component interfaces and inclusive flow reach."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v21 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v22.json'
RULES='research/current-depth-rules-v22.json'
OUTPUT='research/current-depth-register-v22.json'
CSV='research/current-depth-register-v22.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    common={'metric':'reported_vertical_extent','reference_route_projection_eligible':False}
    if case=='south-australian-duran-2020-cited-component':
        required={'entity_id':'current:south-australian','evidence_kind':'published_literature_synthesis','lower_bound_m':200,'lower_bound_operator':'>=','lower_bound_exclusive':False,'source_reported_speed_max_m_s':0.5,'depth_basis':'inferred_inclusive_reach_from_source_reported_flow','branch_section_scope':'regional_South_Australian_component','reference_route_phase_relation':'catalog_winter_source_phase_unspecified','source_access_scope':'original_author_hosted_pdf_prose_and_page_pixels','phase_label':None}
    elif case=='north-pacific-tabata-1975-historical-profile':
        required={'entity_id':'current:north-pacific','evidence_kind':'published_literature_synthesis','lower_bound_m':500,'lower_bound_operator':'>=','lower_bound_exclusive':False,'source_reported_speed_fraction_of_surface':0.5,'depth_basis':'inferred_inclusive_reach_from_nonzero_speed_at_depth','branch_section_scope':'historical_North_Pacific_Current_profile','source_current_naming_convention':'North_Pacific_distinct_from_Subarctic_Aleutian_and_Alaskan_Stream','exact_source_section_recovered':False,'source_access_scope':'original_society_archive_pdf_prose_and_page_pixels','phase_label':None}
    elif case.startswith('australian-boundary-richardson-2019-'):
        expected={'winter':('austral_winter',300,'southern_Australian_margin','partial_southern_component_in_catalog_winter'),'summer':('austral_summer',250,'southern_Australian_margin','conditional_outside_catalog_winter_phase'),'summer-local-shallow':('austral_summer',150,'upwelling_regions_and_western_Tasmania','conditional_outside_catalog_winter_phase')}
        tag=case.removeprefix('australian-boundary-richardson-2019-')
        if tag not in expected:raise ValueError('Unreviewed seasonal component case')
        phase,value,region,relation=expected[tag]
        required={'entity_id':'current:australian-west-south-boundary-flow','evidence_kind':'published_hydrographic_regional_summary','approximate_value_m':value,'phase_label':phase,'region_name':region,'reference_route_phase_relation':relation,'water_mass_component':'subtropical_surface_water','interface_water_masses':['subtropical_Leeuwin_System','subantarctic_Flinders_System'],'depth_basis':'source_water_mass_interface_depth','branch_section_scope':'southern_system_component_Cape_Leeuwin_to_Tasmania','source_access_scope':'primary_institutional_indexed_abstract'}
    else:raise ValueError('Unreviewed source case')
    for k in ['section_sampling_month','calendar_months','climatology_years']:
        if row.get(k) is not None:raise ValueError('No exact section date or common climatology established')
    for k,v in dict(common,**required).items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v21.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v22','status':'AUSTRALIAN_COMPONENT_REACH_SEASONAL_INTERFACES_AND_NORTH_PACIFIC_REACH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v22.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v22.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Australian southern-limb seasonal water-mass interfaces remain partial component evidence, including conditional summer context for a catalog winter system. Source-reported flow at a depth supports inclusive reach, not terminal depth. Undated South Australian and unlocated historical North Pacific descriptions are not route-projectable profiles.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_reported_speed_max_m_s','reference_route_phase_relation','source_reported_speed_fraction_of_surface','source_current_naming_convention','exact_source_section_recovered','interface_water_masses'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
