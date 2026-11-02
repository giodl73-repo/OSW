"""Retain deep Atlantic domains including unresolved seafloor endpoints."""
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import build_current_depth_register_v6 as previous
from build_atlantic_cruise_widths import read_cells

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v7.json'
RULES='research/current-depth-rules-v7.json'
OUTPUT='research/current-depth-register-v7.json'
CSV='research/current-depth-register-v7.csv'
ARTICLE='research/source-data/cainzos-atlantic-2023/article.xml'
TABLE1='research/source-data/cainzos-atlantic-2023/table-1.xlsx'
TABLE2='research/source-data/cainzos-atlantic-2023/table-2.xlsx'
NS={'o':'http://docs.oasis-open.org/ns/oasis-exchange/table'}
# table id, tbody row -> current, group row, Table1 cruise row, nominal latitude.
JOINS={('Ch1.T5',18):('labrador',17,8,53),('Ch1.T5',19):('labrador',17,14,53),
       ('Ch1.T5',20):('labrador',17,20,53),('Ch1.T5',22):('deep-western-boundary',21,7,47),
       ('Ch1.T5',23):('deep-western-boundary',21,19,47),('Ch1.T5',25):('deep-western-boundary',24,13,36),
       ('Ch1.T5',27):('deep-western-boundary',26,6,24.5),('Ch1.T5',28):('deep-western-boundary',26,12,24.5),
       ('Ch1.T5',29):('deep-western-boundary',26,18,24.5),('Ch1.T6',2):('deep-western-boundary',1,5,-11),
       ('Ch1.T6',4):('deep-western-boundary',3,4,-19),('Ch1.T6',6):('deep-western-boundary',5,11,-24),
       ('Ch1.T6',7):('deep-western-boundary',5,17,-24),('Ch1.T6',9):('deep-western-boundary',8,3,-30),
       ('Ch1.T6',10):('deep-western-boundary',8,10,-30),('Ch1.T6',11):('deep-western-boundary',8,16,-30),
       ('Ch1.T6',13):('deep-western-boundary',12,2,-45)}
WINDOWS={2:('1992-12-27','1993-01-30'),3:('1992-12-30','1993-01-28'),
         4:('1991-02-12','1991-03-18'),5:('1994-04-01','1994-05-07'),
         6:('1992-07-20','1992-08-14'),7:('1993-07-08','1993-07-25'),
         8:('1990-07-06','1990-07-09'),10:('2003-11-07','2003-12-02'),
         11:('2009-03-16','2009-04-19'),12:('2004-04-07','2004-05-09'),
         13:('2005-05-03','2005-06-12'),14:('2005-05-29','2005-06-03'),
         16:('2011-09-28','2011-10-29'),17:('2018-03-02','2018-04-05'),
         18:('2011-01-28','2011-03-11'),19:('2013-05-29','2013-06-14'),
         20:('2014-06-09','2014-06-18')}


def read_deep_tables(root=ROOT):
    document=ET.parse(root/ARTICLE).getroot();tables={}
    for wrap in document.findall('.//table-wrap'):
        name=wrap.get('id')
        if name not in ['Ch1.T5','Ch1.T6']:continue
        if ''.join(wrap.find('label').itertext()).replace('\u00a0',' ')!='Table 3':raise ValueError('XML id is not printed Table3')
        rows={}
        for i,row in enumerate(wrap.findall('.//o:tbody/o:row',NS),1):
            rows[i]={entry.get('colname',entry.get('namest')):''.join(entry.itertext()).strip() for entry in row}
        tables[name]=rows
    if set(tables)!={'Ch1.T5','Ch1.T6'}:raise ValueError('Missing deep table parts')
    return tables


def validate_section(row,tables,cruises):
    key=(row['xml_table_id'],row['xml_tbody_row'])
    if key not in JOINS:raise ValueError('Unreviewed XML row identity')
    entity,group,tr,lat=JOINS[key];source=tables[key[0]][key[1]];cruise=cruises[tr]
    expected={'entity_id':'current:'+entity,'xml_group_row':group,'source_group':tables[key[0]][group]['col1'],
              'table_1_row':tr,'cruise_id':cruise['D'],'section_id':cruise['A'],
              'source_section_dates_label':cruise['B'],'source_section_year_label':str(cruise['C']),
              'nominal_latitude_degrees_north':lat,'inverse_model_decade_group':source['col1'],
              'station_range_label':source['col2'],'longitude_limits_label':source['col3'],
              'source_horizontal_span_km':int(source['col4']),'neutral_density_layer_indices':source['col5'],
              'raw_depth_cell':source['col6'],'evidence_kind':'published_inverse_hydrographic_section',
              'observed_period':None,'same_source_width_reference_id':None,
              'sampling_window_role':'whole_section_not_exact_boundary_station_occupation',
              'source_component_scope':'deep_component_only' if entity=='labrador' else 'regional_atlantic_section'}
    for field,value in expected.items():
        if row.get(field)!=value:raise ValueError('Publisher section mismatch: '+field)
    if row['section_sampling_window']!=dict(zip(['start','end'],WINDOWS[tr])):raise ValueError('Whole-section window changed')
    finite=re.fullmatch(r'(\d+) to (\d+)',source['col6']);bottom=re.fullmatch(r'(\d+) to bottom',source['col6'])
    if finite:
        if row['metric']!='transport_selected_depth_extent' or row['range_m']!=[int(finite[1]),int(finite[2])] or row.get('lower_domain_boundary_kind')!='reported_numeric_depth' or row.get('domain_upper_depth_m') is not None or row.get('domain_lower_depth_m') is not None:
            raise ValueError('Numeric domain must preserve both reported depths')
    elif bottom:
        if row['metric']!='transport_selected_upper_depth' or row['approximate_value_m']!=int(bottom[1]) or row.get('domain_upper_depth_m')!=int(bottom[1]) or row.get('lower_domain_boundary_kind')!='seafloor_unspecified_numeric_depth' or row.get('domain_lower_depth_m') is not None:
            raise ValueError('Seafloor terminal cannot become a numerical bottom or thickness')
    else:raise ValueError('Unsupported publisher depth syntax')
    for flag in ['decade_group_is_time_average','depth_extent_is_uniform_fixed_layer','rectangle_cross_section_inferred',
                 'cross_section_area_eligible','exact_boundary_coordinates_available','component_promoted_to_entire_system',
                 'horizontal_span_is_cross_stream_width','independent_observation_count_claimed']:
        if row.get(flag) is not False:raise ValueError('Unreviewed section promotion: '+flag)


def validate_other(row,table2):
    if row['entity_id']=='current:acc':
        cells=table2[23]
        if row['metric']!='transport_selected_depth_extent' or row['range_m']!=[0,3035] or row.get('table_2_row')!=23 or row.get('raw_depth_cell')!=cells['F'] or row.get('source_group')!=table2[22]['A'] or row.get('source_component_scope')!='front_component_only' or row.get('section_sampling_window')!=dict(zip(['start','end'],WINDOWS[2])):
            raise ValueError('ACC front must retain source row and component scope')
        if row.get('table_1_row')!=2 or row.get('cruise_id')!='74DI19921222':raise ValueError('ACC front cruise changed')
    elif row['entity_id']=='current:california':
        expected={'california-stone-2018-offshore-reach':(500,'offshore'),
                  'california-stone-2018-near-coast-reach':(150,'within_300km_of_coast')}
        if row['id'] not in expected:raise ValueError('Unreviewed California scope')
        value,scope=expected[row['id']]
        if row['metric']!='reported_vertical_extent' or row['approximate_value_m']!=value or row.get('cross_shore_scope')!=scope or row['evidence_kind']!='published_literature_synthesis' or row.get('observed_period') is not None or row.get('climatology_period') is not None:
            raise ValueError('California regional summaries are not model-period observations')
    else:raise ValueError('Unreviewed current')
    if row.get('component_promoted_to_entire_system') is not False or row.get('same_source_width_reference_id') is not None:
        raise ValueError('No whole-system promotion or width join established')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v6.py',RULES,SOURCE,ARTICLE,TABLE1,TABLE2]:pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Original source changed')
    tables=read_deep_tables(root);cruises={r['row']:r['cells'] for r in read_cells(str(root/TABLE1))};table2={r['row']:r['cells'] for r in read_cells(str(root/TABLE2))}
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        previous.validate_reference(row,identities,rules['metric_types'])
        if row.get('xml_table_id'):validate_section(row,tables,cruises)
        else:validate_other(row,table2)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    if {(r['xml_table_id'],r['xml_tbody_row']) for r in source['references'] if r.get('xml_table_id')}!=set(JOINS):raise ValueError('Deep source coverage changed')
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v7','status':'SCOPED_DEPTH_REFERENCES_WITH_DEEP_ATLANTIC_DOMAINS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v7.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v7.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Deep domains with unspecified seafloor endpoints do not establish numerical thickness; spatially distinct summaries and current components remain separate.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['xml_table_id','xml_tbody_row','xml_group_row','source_component_scope','cross_shore_scope',
              'domain_upper_depth_m','domain_lower_depth_m','lower_domain_boundary_kind','source_horizontal_span_km']
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
