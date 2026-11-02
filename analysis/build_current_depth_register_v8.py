"""Append regionally defined thickness, core and branch depth references."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v7 as previous
from build_current_depth_register_v6 import validate_reference as validate_depth_reference

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v8.json'
RULES='research/current-depth-rules-v8.json'
OUTPUT='research/current-depth-register-v8.json'
CSV='research/current-depth-register-v8.csv'


def validate_reference(row,identities,metrics):
    if row['metric']!='reported_vertical_thickness':
        return validate_depth_reference(row,identities,metrics)
    if row['vertical_datum']!='not_applicable_thickness_distance':
        raise ValueError('Thickness is a distance, not depth below the surface')
    # Reuse the frozen non-datum checks without changing stored evidence.
    checked=dict(row,vertical_datum='local_sea_surface_positive_down')
    validate_depth_reference(checked,identities,metrics)


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No matched width or independent repeat claim established')
    entity=row['entity_id'];case=row['source_case_id']
    if entity=='current:kuroshio':
        if row['evidence_kind']!='published_model_climatology' or row.get('model_product')!='Hsin2008_EAMS_nested_POM' or row.get('climatology_years')!=[1982,2005]:raise ValueError('Kuroshio must retain model/period')
        expected={'kuroshio-hsin-2008-inshore-reach':('reported_vertical_extent',300,'inshore_22.5N'),
                  'kuroshio-hsin-2008-offshore-reach':('reported_vertical_extent',600,'offshore_22.5N'),
                  'kuroshio-hsin-2008-southern-core-boundary':('core_lower_boundary_depth',600,'section_22.5N'),
                  'kuroshio-hsin-2008-northern-core-boundary':('core_lower_boundary_depth',1000,'north_of_25.25N')}
        if row['id'] not in expected:raise ValueError('Unreviewed Kuroshio region')
        metric,value,scope=expected[row['id']]
        if (row['metric'],row['approximate_value_m'],row.get('branch_section_scope'))!=(metric,value,scope):raise ValueError('Branch or metric changed')
        if metric=='core_lower_boundary_depth' and row.get('core_definition')!={'kind':'source_velocity_isotach','speed_m_s':0.1}:raise ValueError('Retain10cm/s core operator')
    elif entity=='current:norwegian-atlantic-slope':
        expected={'nwasc-baumann-2026-svinoy-core-bottom':(460,'Svinoy',1500),
                  'nwasc-baumann-2026-gimsoy-core-bottom':(530,'Gimsoy',2500)}
        if row['id'] not in expected:raise ValueError('Unreviewed section')
        value,section,isobath=expected[row['id']]
        definition={'absolute_salinity_min_g_kg':35.16,'salinity_operator':'>=',
                    'excluded_surface_upper_depth_m':50,'shoreward_isobath_m':isobath,
                    'fraction_of_mean_transport':0.5,'ranking':'decreasing_absolute_geostrophic_velocity',
                    'static_mean_mask':True}
        if row['metric']!='core_lower_boundary_depth' or row['approximate_value_m']!=value or row.get('section_name')!=section or row.get('core_definition')!=definition or row.get('climatology_years')!=[1993,2022] or row['evidence_kind']!='published_hydrographic_mean_core':raise ValueError('Static salinity/transport-selected core changed')
    elif entity in ['current:tsushima','current:guinea']:
        if row['metric']!='reported_vertical_thickness':raise ValueError('Source thickness cannot become bottom depth')
        if entity=='current:tsushima':
            if row['approximate_value_m']!=200 or row['evidence_kind']!='institutional_literature_synthesis' or case!='tsushima-jma-regional-thickness':raise ValueError('Tsushima regional thickness changed')
        elif row['range_m']!=[30,40] or row['evidence_kind']!='published_literature_synthesis' or case!='guinea-djakoure-2017-regional-thickness':raise ValueError('Guinea thickness summary changed')
        if row.get('climatology_years') is not None:raise ValueError('Unrelated model/figure dates are not thickness observation dates')
    elif entity=='current:new-ireland-coastal-undercurrent':
        if row['metric']!='core_depth' or row['approximate_value_m']!=235 or row['evidence_kind']!='published_literature_synthesis' or row.get('underlying_observational_citation')!='Butt and Lindstrom1994, WEPOCS' or row.get('climatology_years') is not None:raise ValueError('Cited observed core cannot become model isopycnal or dated new observation')
    elif entity=='current:solomon-island-coastal-undercurrent':
        if row['metric']!='core_depth' or row['approximate_value_m']!=200 or row['evidence_kind']!='published_model_climatology' or row.get('model_product')!='Melet2010_fine_grid' or row.get('climatology_years')!=[1986,2004] or row.get('section_latitude_degrees_north')!=-6:raise ValueError('SIUC model core context changed')
    elif entity=='current:mediterranean-undercurrent':
        expected={'med-bower-2002-may1993-section1-thickness':('reported_vertical_thickness',200,1),
                  'med-bower-2002-may1993-section3-velocity-core':('core_depth',1100,3)}
        if row['id'] not in expected:raise ValueError('Unreviewed Mediterranean section')
        if (row['metric'],row['approximate_value_m'],row.get('hydrographic_section_number'))!=expected[row['id']]:raise ValueError('Section thickness and core depth must remain separate')
        if row.get('section_sampling_month')!='1993-05' or row['evidence_kind']!='published_geostrophic_section' or row.get('velocity_reference')!='salinity_minimum_assumed_level_of_no_motion' or row.get('pressure_to_depth_conversion_performed') is not False:raise ValueError('Retain section method, month and original metre statement')
    else:raise ValueError('Unreviewed identity')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v7.py',RULES,SOURCE]:pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
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
    return {'schema':'osw.current-depth-register.v8','status':'SCOPED_DEPTH_REFERENCES_WITH_REGIONAL_THICKNESS_AND_DEFINED_CORES',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v8.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v8.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Source-reported regional thickness is distinct from bottom or core depth and is not a whole-route thickness field. Core operators and branch definitions remain explicit.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['vertical_datum','climatology_years','core_definition','branch_section_scope','section_name',
              'hydrographic_section_number','section_sampling_month','velocity_reference',
              'pressure_to_depth_conversion_performed','underlying_observational_citation']
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
