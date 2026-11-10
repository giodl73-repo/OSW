"""Retain inverse-section depth extents with exact publisher cells and cruise joins."""
import hashlib
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path
import build_current_depth_register_v2 as previous
from build_atlantic_cruise_widths import read_cells

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v3.json'
RULES='research/current-depth-rules-v3.json'
OUTPUT='research/current-depth-register-v3.json'
CSV='research/current-depth-register-v3.csv'
WIDTHS='research/ocean-current-width-inventory.json'
TABLE1='research/source-data/cainzos-atlantic-2023/table-1.xlsx'
TABLE2='research/source-data/cainzos-atlantic-2023/table-2.xlsx'


def validate_section(row,widths,tables):
    width=widths[row['same_source_width_reference_id']]
    context=width['hydrographic_section_context']
    source=tables[2][row['table_2_row']]
    cruise=tables[1][row['table_1_row']]
    if row['metric']!='transport_selected_depth_extent' or row['evidence_kind']!='published_inverse_hydrographic_section':
        raise ValueError('Section extent must retain inverse-transport definition')
    if row['entity_id']!='current:'+width['current_id'] or row['table_2_row']!=context['table_2_row'] or row['table_1_row']!=context['table_1_row']:
        raise ValueError('Source current or row correspondence changed')
    m=re.fullmatch(r'(\d+) to (\d+)',source['F'])
    if not m or row['range_m']!=[int(m[1]),int(m[2])] or row['raw_depth_cell']!=source['F']:
        raise ValueError('Depth must reproduce publisher metre cell F, not transport or density indices')
    for field,expected in [('source_group',context['source_group']),('neutral_density_layer_indices',source['E']),('station_range_label',source['B']),('longitude_limits_label',source['C']),('inverse_model_decade_group',source['A']),('cruise_id',cruise['D']),('section_id',cruise['A']),('nominal_latitude_degrees_north',context['nominal_section_latitude_degrees_north']),('section_sampling_window',context['cruise_sampling_window'])]:
        if row[field]!=expected:raise ValueError('Section context mismatch: '+field)
    if row['observed_period'] is not None or row['sampling_window_role']!='whole_section_not_exact_boundary_station_occupation':
        raise ValueError('Whole-section dates cannot become exact boundary occupation')
    import datetime
    start,end=(datetime.date.fromisoformat(row['section_sampling_window'][k]) for k in ['start','end'])
    if start>end:raise ValueError('Invalid section sampling window')
    for field in ['decade_group_is_time_average','depth_extent_is_uniform_fixed_layer','rectangle_cross_section_inferred','cross_section_area_eligible','exact_boundary_coordinates_available']:
        if row[field] is not False:raise ValueError('Section scope promoted: '+field)


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Previous register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for path in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v2.py','analysis/build_atlantic_cruise_widths.py',TABLE1,TABLE2,WIDTHS,RULES,SOURCE]:
        pins[path]=hashlib.sha256((root/path).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    for path,digest in source['source_input_sha256'].items():
        if pins.get(path)!=digest:raise ValueError('Pinned source changed: '+path)
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Previous-register pin mismatch')
    # Read the tiny original publisher workbooks, never the ocean runtime or fields.
    tables={1:{r['row']:r['cells'] for r in read_cells(TABLE1)},2:{r['row']:r['cells'] for r in read_cells(TABLE2)}}
    if tables[2][1]['F']!='Depth (m)' or tables[2][1]['E']!='Layers':raise ValueError('Publisher units/header changed')
    widths={r['id']:r for r in json.loads((root/WIDTHS).read_bytes())['measurements']}
    identities={r['entity_id'] for r in prior['records']}
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence}
    for i,row in enumerate(source['references']):
        previous.validate_reference(row,identities,rules['metric_types'])
        validate_section(row,widths,tables)
        if row['id'] in seen:raise ValueError('Duplicate reference ID')
        seen.add(row['id'])
        evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for old in prior['records']:
        row=dict(old);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v3','status':'SCOPED_DEPTH_CORE_AND_TRANSPORT_SECTION_EXTENT_REFERENCES','rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v3.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v3.py').read_bytes()).hexdigest(),'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),'coverage_interpretation':'Depth-reference coverage includes source-selected inverse-transport sections and core context. It does not imply complete lower boundaries, full thickness fields, seasonal envelopes or volumes. Cruise/decade groups remain distinct.','records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=['id','entity_id','metric','approximate_value_m','range_m','lower_bound_m','lower_bound_exclusive','unit','phase_label','geographic_scope','temporal_scope','table_2_row','table_1_row','source_group','cruise_id','section_id','nominal_latitude_degrees_north','neutral_density_layer_indices','raw_depth_cell','section_window_start','section_window_end','sampling_window_role','same_source_width_reference_id','source_case_id','source_definition','source_url','source_locator','qualification']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for row in document['evidence']:
        value=dict(row)
        if value.get('range_m') is not None:value['range_m']=json.dumps(value['range_m'],separators=(',',':'))
        if value.get('section_sampling_window'):
            value['section_window_start']=value['section_sampling_window']['start'];value['section_window_end']=value['section_sampling_window']['end']
        writer.writerow(value)
    return out.getvalue().encode('utf8')


if __name__=='__main__':
    d=build();(ROOT/OUTPUT).write_bytes((json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf8'));(ROOT/CSV).write_bytes(csv_bytes(d));print(json.dumps(d['counts']))
