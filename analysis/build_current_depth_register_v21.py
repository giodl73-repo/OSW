"""Retain regional dominant-flow extent and explicitly attributed water-mass bands."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v20 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v21.json'
RULES='research/current-depth-rules-v21.json'
OUTPUT='research/current-depth-register-v21.json'
CSV='research/current-depth-register-v21.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case=='south-atlantic-smythe-wright-1998-cape-basin':
        required={'entity_id':'current:south-atlantic','metric':'reported_vertical_extent','evidence_kind':'published_geostrophic_regional_summary','approximate_value_m':1000,'depth_basis':'source_dominant_flow_layer_extent','dominant_flow_fraction_quantified':False,'velocity_reference_depth_m':1500,'reference_is_flow_boundary':False,'branch_section_scope':'Cape_Basin_two_frontal_jets','source_cruise_months':['1978-12','1983-10','1989-01','1989-04','1990-02','1993-01'],'continuous_temporal_coverage':False,'source_access_scope':'original_author_hosted_pdf_prose_and_page_pixels'}
    elif case=='portugal-voelker-2022-modern-subpolar-component':
        required={'entity_id':'current:portugal','metric':'reported_flow_depth_band','evidence_kind':'published_literature_synthesis','range_m':[250,500],'water_mass_component':'subpolar_ENACW','branch_section_scope':'regional_subpolar_water_mass_component','depth_basis':'source_water_mass_component_depth_band','source_access_scope':'primary_publisher_indexed_section_2_1','context_time_basis':'modern_regional_setting_not_paleorecord','source_component_attribution_explicit':True}
    else:raise ValueError('Unreviewed source case')
    for k in ['section_sampling_month','calendar_months','phase_label','climatology_years']:
        if row.get(k) is not None:raise ValueError('No common dated section or seasonal support')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v20.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v21','status':'SOUTH_ATLANTIC_DOMINANT_LAYER_AND_PORTUGAL_COMPONENT',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v21.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v21.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Dominant-flow layer extent retains an unquantified fraction and assumed geostrophic reference. Multicruise support is not continuous. Portugal subpolar ENACW is component evidence in a modern setting, distinct from adjacent Azores water and the paleorecord.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['dominant_flow_fraction_quantified','velocity_reference_depth_m','reference_is_flow_boundary','source_cruise_months','continuous_temporal_coverage','context_time_basis','source_component_attribution_explicit'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
