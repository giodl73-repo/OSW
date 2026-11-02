"""Retain Nordic component depths and explicitly out-of-route Davidson context."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v19 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v20.json'
RULES='research/current-depth-rules-v20.json'
OUTPUT='research/current-depth-register-v20.json'
CSV='research/current-depth-register-v20.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case.startswith('norwegian-skjelvan-2001-'):
        expected={'norwegian-basin':('Norwegian Basin',[500,600]),'lofoten-basin':('Lofoten Basin',[800,900])};tag=case.removeprefix('norwegian-skjelvan-2001-')
        if tag not in expected:raise ValueError('Unknown water-mass region')
        name,interval=expected[tag]
        required={'entity_id':'current:norwegian','metric':'reported_vertical_extent','evidence_kind':'published_literature_synthesis','range_m':interval,'region_name':name,'water_mass_component':'Atlantic_Water','water_mass_definition':{'practical_salinity_min':35,'salinity_operator':'>','temperature_min_deg_C':2,'temperature_operator':'>'},'source_current_interpretation':'Norwegian_Atlantic_Current_component','branch_section_scope':'regional_Atlantic_Water_component','source_access_scope':'primary_publisher_indexed_introduction','depth_basis':'source_reported_water_mass_layer_depth'}
    elif case=='north-cape-baumann-2026-bso':
        required={'entity_id':'current:north-cape','metric':'core_lower_boundary_depth','evidence_kind':'published_hydrographic_mean_core','approximate_value_m':350,'section_name':'Barents_Sea_Opening','climatology_years':[1993,2022],'core_definition':{'absolute_salinity_min_g_kg':35.16,'salinity_operator':'>=','excluded_surface_upper_depth_m':50,'fraction_of_maximum_mean_transport':0.5,'ranking':'decreasing_absolute_salinity','static_mean_mask':True},'identity_mapping_source_url':'https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2005GL023440','branch_section_scope':'partial_BSO_inflow_core','depth_basis':'source_salinity_ranked_transport_core'}
        if not row.get('identity_mapping_source_locator'):raise ValueError('Branch identity needs evidence')
    elif case=='davidson-beutel-2025-northern-context':
        required={'entity_id':'current:davidson','metric':'reported_flow_depth_band','evidence_kind':'published_literature_synthesis','range_m':[0,200],'phase_label':'downwelling','branch_section_scope':'conditional_northern_extension_context','reference_route_scope_relation':'outside_declared_35_to_46N_reference_route','reference_route_projection_eligible':False,'depth_basis':'source_regional_downwelling_flow_layer','calendar_months':None}
    else:raise ValueError('Unreviewed source case')
    if row.get('section_sampling_month') is not None:raise ValueError('No exact section month established')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v19.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v20','status':'NORDIC_WATER_MASS_DEPTH_CORE_OPERATOR_AND_CONDITIONAL_DAVIDSON',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v20.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v20.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Regional water-mass depth is distinct from a kinematic boundary. BSO core uses salinity ranking. Conditional Davidson northern context is ineligible for projection along the catalog reference route.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['region_name','water_mass_definition','source_current_interpretation','identity_mapping_source_url','identity_mapping_source_locator','reference_route_scope_relation','reference_route_projection_eligible'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
