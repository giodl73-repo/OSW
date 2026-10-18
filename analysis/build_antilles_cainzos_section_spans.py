"""Extract three published Antilles spans with quarantined prose conflicts."""
import hashlib
import json
from pathlib import Path
from build_atlantic_cruise_widths import read_cells
from build_atlantic_station_context import parse_events,context_points

ROOT=Path(__file__).resolve().parents[1]
OUTPUT='research/antilles-cainzos-2023-cruise-section-spans.json'
PROTOCOL='plans/antilles-cainzos-cruise-span-protocol-v1.md'
URL='https://os.copernicus.org/articles/19/1009/2023/'
DIRECTORY='research/source-data/cainzos-atlantic-2023/'
STATIONS='research/source-data/cchdo-atlantic-stations/'
FROZEN_INPUTS={'plans/antilles-cainzos-cruise-span-protocol-v1.md': 'ec440a2924fa590d942543e52ec0c824dd4c79038e63a739bd58b8b14d5e8ed7',
 'analysis/build_atlantic_cruise_widths.py': '0c1d22c5bc4999ba1e512b8778888c61d950f843b46dbd328e9c1088c84c3364',
 'analysis/build_atlantic_station_context.py': '27557d2ff6e52e391d9382382be1703fddc561a74c20982f39ecab57edc56d7f',
 'research/source-data/cainzos-atlantic-2023/acquisition.json': '04628fc76664bb4124b205a61ecd6d03b09d661e950b704861a2d9fc50104771',
 'research/source-data/cainzos-atlantic-2023/table-1.xlsx': 'bfe0bbc798ca14677fdfd66668f546e2b75fed4f6350bc29881a47133e40d3f6',
 'research/source-data/cainzos-atlantic-2023/table-2.xlsx': 'eab186e33d87ee67f3d8f825e0b12a07cf3e1f8297e5ef24416f7d6a44961f15',
 'research/source-data/cchdo-atlantic-stations/acquisition.json': 'abbd4a405d25549359df87b02b992d4428111834fe9ab084638f802b2fd125a8',
 'research/source-data/cchdo-atlantic-stations/29HE19920714-summary.txt': '98acd1a469d62e79685b5b800faf2b744434d0a3d8110f8643005aa57e0ddcc0',
 'research/source-data/cchdo-atlantic-stations/74DI20040404-summary.txt': '392e3ca2acb0649f65f0f5b5678f9a7147bb86185911210c2a153e56fdf63221',
 'research/source-data/cchdo-atlantic-stations/29AH20110128-summary.txt': '29f78660a2da440e3dfa10fc0c2efb7037bcce8e73e9b405100793b8ed946b59',
 'research/source-data/cainzos-antilles-2023/journal-article.pdf': '99efb015dc12b994de1a94c38e0bd6813c2b066b54ae9c40514775d6fee071d3',
 'research/source-data/cainzos-antilles-2023/acquisition.json': '5374e00f354c974a384b8a0cea85c04d596470e07cbeee62274f97e9e4a6be11',
 'analysis/acquire_antilles_cainzos_article.py': 'a7d1d25c7501ab43c1fc80794416313373cde70765cb73c0b4947a0d888e7134'}
JOBS=[(51,6,'1990\u20131999','29HE19920714','1992-07-20','1992-08-14',125,'29HE06_1'),
      (52,12,'2000\u20132009','74DI20040404','2004-04-07','2004-05-09',38,'74DI20040404'),
      (53,18,'2010\u20132019','29AH20110128','2011-01-28','2011-03-11',39,'29AH20110128')]


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def build():
    if len(FROZEN_INPUTS)!=13:raise ValueError('Missing reviewed Antilles source pins')
    for name,pin in FROZEN_INPUTS.items():
        if digest(name)!=pin:raise ValueError('Changed reviewed Antilles source: '+name)
    acquisition=json.loads((ROOT/(DIRECTORY+'acquisition.json')).read_bytes())
    tables={str(i):read_cells(DIRECTORY+f'table-{i}.xlsx') for i in (1,2)}
    first={r['row']:r['cells'] for r in tables['1']};second={r['row']:r['cells'] for r in tables['2']}
    if second[50]['A']!='Antilles Current 24.5\u2218\u2009N':raise ValueError('Changed publisher current identity')
    station_acquisition=json.loads((ROOT/(STATIONS+'acquisition.json')).read_bytes())
    sources={s['paper_cruise_id']:s for s in station_acquisition['files']}
    records=[];contexts=[]
    conflicts=[{'id':'prose_location','status':'unresolved_source_wording_excluded_from_geography',
                'source_locator':'Section3.1.7','source_phrase':'from Cape Hatteras',
                'interpretation':'The table identifies Antilles/A05. The incompatible prose place name is retained without author correction or a Cape Hatteras map location.'},
               {'id':'prose_rounding','source_locator':'Section3.1.7 versus Table2 row53 columnD',
                'prose_approximate_value_km':38,'table_value_km':39,
                'interpretation':'Transcribe the original table39 km; do not overwrite with the prose approximation.'}]
    for row_no,cruise_row,decade,cruise_id,start,end,width,archive_id in JOBS:
        cells=second[row_no];cruise=first[cruise_row];window={'start':start,'end':end}
        if (cells['A'],cells['D'],cruise['D'],cruise['A'])!=(decade,width,cruise_id,'A05'):raise ValueError('Changed publisher cruise join')
        source=sources[cruise_id];raw=(ROOT/source['file']).read_bytes()
        if len(raw)!=source['bytes'] or hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Changed station summary')
        century=int(start[:4])//100*100;events=parse_events(raw,century)
        if not events or {e['archive_cruise_label'] for e in events}!={archive_id} or {e['archive_section_label'] for e in events}!={'A05'}:raise ValueError('Unresolved archive cruise identity')
        points=context_points(events,window)
        if not points:raise ValueError('No compatible dated hydrographic sampling context')
        context={'table_2_row':row_no,'table_1_row':cruise_row,'source_group':second[50]['A'],
          'inverse_model_decade_group':decade,'cruise_id':cruise_id,'section_id':'A05','cruise_sampling_window':window,
          'sampling_window_role':'whole_section_sampling_window_not_exact_boundary_station_occupation',
          'nominal_section_latitude_degrees_north':24.5,'table_1_latitude_label':cruise['E'],
          'source_station_range_label':cells['B'],'source_longitude_limits_degrees_east':[float(v) for v in cells['C'].split(':')],
          'source_layer_indices_label':cells['E'],'source_depth_extent_m':[int(v) for v in cells['F'].split(' to ')],
          'station_index_convention':'publisher_table_label_not_reindexed_against_archive_station_labels',
          'nominal_latitude_is_endpoint_latitude':False,'depth_extent_is_uniform_fixed_measurement_layer':False,
          'decade_group_is_time_average':False,'source_distance_is_recomputed_from_nominal_latitude':False,
          'source_width_uncertainty_km':None,
          'source_conflicts':conflicts if row_no==53 else conflicts[:1],
          'independent_cruise_context':{'source_file':source['file'],'source_sha256':source['sha256'],
             'cruise_url':source['cruise_url'],'archive_cruise_label':archive_id,'archive_section_label':'A05',
             'in_window_hydrographic_casts':len(points),'boundary_station_mapping_status':'unresolved'}}
        record={'id':f'cainzos-2023-t02-row-{row_no}-section-span','current_id':'antilles','name':'Antilles Current',
          'status':'editorial_source_extraction_not_canonical','measurement_type':'published_inverse_hydrographic_section_span',
          'width_metric':'transport_diagnosed_hydrographic_section_span','width_metric_label':'transport-selected cruise-section span',
          'approximate_width_km':width,'width_range_km':None,
          'range_interpretation':'Publisher table distance in kilometres; width error unreported. Separate cruises are not an annual range; transport errors are not width errors.',
          'geographic_scope':'Antilles Current, nominal A05 24.5 N section. Western station tracks deviate from nominal latitude; exact model boundary pairings remain unresolved. Incompatible Cape Hatteras prose is excluded from geography.',
          'section_geometry':None,'section_orientation':'Nominally zonal hydrographic section; exact boundary-track orientation unresolved.',
          'layer':f"Publisher neutral-density layer indices {cells['E']}; reported depth extent {cells['F']} m. Not a uniform fixed-depth slice.",
          'time_convention':f'{cruise_id}: whole section sampled {start} to {end}; inverse-model group {decade}. Cruise snapshot, not a decade mean or seasonal composite.',
          'boundary_rule':'Section2.3: station pairs selected by consistent slope of eastward accumulated horizontal mass transport; vertical extent retains the integrated flow direction. No fixed velocity cutoff inferred.',
          'boundary_sides':'source_selected_station_limits','source_url':URL,
          'source_citation':'Cainzos et al. (2023), Ocean Science19,1009-1045, doi:10.5194/os-19-1009-2023.',
          'source_locator':f'Table2 Worksheet1 row{row_no} columnsA-F; Table1 row{cruise_row}; Sections2.1-2.3 and3.1.7 (prose conflict retained).',
          'source_retrieved_date':acquisition['retrieved_date'],'source_evidence_kind':'published_inverse_model_hydrographic_cruise_snapshot',
          'extraction_method':'Unchanged original XLSX cells; explicit table/cruise join with independent A05 archive context. Source prose location/rounding conflicts retained; no longitude-distance conversion.',
          'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,
          'seasonal_playback_eligible':False,'full_width_inference_eligible':False,'is_confidence_interval':False,
          'phase_kind':'inverse_hydrographic_section_span','phase_label':f'{cruise_id} - nominal A05',
          'observed_period':None,'calendar_months':None,'fixed_layer_bounds_m':None,
          'hydrographic_section_context':context,
          'remaining_gates':['Recover actual model boundary station pairings before mapped edges or state intersections.','Source prose place name remains uncorrected; no author confirmation or independent scientific admission claimed.']}
        records.append(record)
        contexts.append({'measurement_id':record['id'],'current_id':'antilles','paper_cruise_id':cruise_id,
          'paper_section_id':'A05','paper_station_range_label':cells['B'],'sampling_window':window,
          'status':'dated_cruise_sampling_context','geometry_role':'cruise_sampling_context_not_current_boundary',
          'boundary_station_mapping_status':'unresolved','current_footprint_eligible':False,
          'state_intersection_eligible':False,'annual_series_eligible':False,
          'coordinate_uncertainty_degrees':None,'coordinate_datum':None,'point_count':len(points),'points':points,
          'source_file':source['file'],'source_sha256':source['sha256'],'cruise_url':source['cruise_url']})
    return {'schema':'osw.antilles-published-cruise-spans.v1','status':'editorial_source_extraction_not_canonical',
      'current_id':'antilles','source_url':URL,'source_license':'CC-BY-4.0','article_review':{'original_pdf_pages':[5,14],'review_scope':'Table2 continuation and Section3.1.7 visually inspected; not a full page-by-page review.'},'protocol_file':PROTOCOL,
      'protocol_sha256':digest(PROTOCOL),'generator_file':'analysis/build_antilles_cainzos_section_spans.py',
      'generator_sha256':digest('analysis/build_antilles_cainzos_section_spans.py'),'input_sha256':FROZEN_INPUTS,
      'original_source_tables':tables,'source_conflicts':conflicts,'measurements':records,'measurement_contexts':contexts,
      'prior_values_viewed_before_protocol':True,'fully_blinded':False,'new_geographic_edges_admitted':False,
      'whole_current_width_km':None,'annual_width_range_km':None,
      'scope':'Three source-reported transport-selected spans, not whole-current widths, annual ranges or mapped edges.'}


if __name__=='__main__':
    document=build();(ROOT/OUTPUT).write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Extracted Antilles cruise spans:',[r['approximate_width_km'] for r in document['measurements']])
