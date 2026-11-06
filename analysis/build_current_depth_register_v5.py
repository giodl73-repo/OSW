"""Add independently mapped Atlantic sections without borrowing unrelated widths."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
import build_current_depth_register_v4 as previous
from build_current_depth_register_v2 import validate_reference
from build_atlantic_cruise_widths import read_cells

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v5.json'
RULES=previous.RULES
OUTPUT='research/current-depth-register-v5.json'
CSV='research/current-depth-register-v5.csv'
TABLE1='research/source-data/cainzos-atlantic-2023/table-1.xlsx'
TABLE2='research/source-data/cainzos-atlantic-2023/table-2.xlsx'
# Explicitly reviewed table groups, rather than name/family inheritance.
JOINS={45:('north-brazil',44,5,-11,'source_named_current_at_11S'),
       47:('florida',46,6,24.5,'source_named_current'),
       48:('florida',46,12,24.5,'source_named_current'),
       49:('florida',46,18,24.5,'source_named_current'),
       86:('labrador',85,8,53,'upper_component_only'),
       87:('labrador',85,14,53,'upper_component_only'),
       88:('labrador',85,20,53,'upper_component_only')}


def validate_section(row,tables):
    n=row['table_2_row']
    if n not in JOINS:raise ValueError('Unreviewed source identity mapping')
    entity,group,cruise_row,latitude,component=JOINS[n]
    source=tables[2][n];cruise=tables[1][cruise_row]
    expected={'entity_id':'current:'+entity,'table_2_group_row':group,
              'table_1_row':cruise_row,'nominal_latitude_degrees_north':latitude,
              'source_component_scope':component,'source_group':tables[2][group]['A'],
              'cruise_id':cruise['D'],'section_id':cruise['A'],
              'source_section_dates_label':cruise['B'],'source_section_year_label':str(cruise['C']),
              'inverse_model_decade_group':source['A'],'station_range_label':source['B'],
              'longitude_limits_label':source['C'],'neutral_density_layer_indices':source['E'],
              'raw_depth_cell':source['F'],'same_source_width_reference_id':None,
              'metric':'transport_selected_depth_extent','evidence_kind':'published_inverse_hydrographic_section',
              'observed_period':None,'sampling_window_role':'whole_section_not_exact_boundary_station_occupation'}
    for field,value in expected.items():
        if row.get(field)!=value:raise ValueError('Source scope/cell mismatch: '+field)
    match=re.fullmatch(r'(\d+) to (\d+)',source['F'])
    if not match or row['range_m']!=[int(match[1]),int(match[2])]:
        raise ValueError('Depth must reproduce metre column F')
    import datetime
    start,end=(datetime.date.fromisoformat(row['section_sampling_window'][k]) for k in ['start','end'])
    if start>end:raise ValueError('Invalid section window')
    # Dates are explicit transcriptions independently checked against original Table1.
    windows={5:('1994-04-01','1994-05-07'),6:('1992-07-20','1992-08-14'),
             12:('2004-04-07','2004-05-09'),18:('2011-01-28','2011-03-11'),
             8:('1990-07-06','1990-07-09'),14:('2005-05-29','2005-06-03'),
             20:('2014-06-09','2014-06-18')}
    if (start.isoformat(),end.isoformat())!=windows[cruise_row]:raise ValueError('Section dates changed')
    for field in ['decade_group_is_time_average','depth_extent_is_uniform_fixed_layer',
                  'rectangle_cross_section_inferred','cross_section_area_eligible',
                  'exact_boundary_coordinates_available','component_promoted_to_entire_system']:
        if row.get(field) is not False:raise ValueError('Section promoted: '+field)


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v4.py',SOURCE,TABLE1,TABLE2]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Source pin mismatch')
    tables={i:{r['row']:r['cells'] for r in read_cells(str(root/p))} for i,p in [(1,TABLE1),(2,TABLE2)]}
    if tables[2][1]['F']!='Depth (m)':raise ValueError('Publisher depth units changed')
    if {r['table_2_row'] for r in source['references']}!=set(JOINS):raise ValueError('Reviewed source rows missing')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_section(row,tables)
        if row['id'] in seen:raise ValueError('Duplicate reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v5','status':'SCOPED_DEPTH_REFERENCES_WITH_ADDITIONAL_ATLANTIC_SECTIONS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v5.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v5.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' An upper-component depth reference does not cover the deep component; independent sections do not inherit unrelated width observations.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


csv_bytes=previous.csv_bytes


if __name__=='__main__':
    d=build();(ROOT/OUTPUT).write_bytes((json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf8'));(ROOT/CSV).write_bytes(csv_bytes(d));print(json.dumps(d['counts']))
