"""Source-table transcription and original SVG only; no ocean-field processing."""
import copy
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT='research/eac-kerry-2020-mean-core-transcription-v1.json'
PROTOCOL='plans/eac-kerry-2020-mean-core-dimensions-protocol-v1.md'
FACTS='research/eac-kerry-2020-mean-core-dimensions-source-facts-v1.json'
FIGURE='figures/eac-kerry-2020-mean-core-dimensions-v1.svg'
COMPACT='figures/eac-kerry-2020-mean-core-dimensions-compact-v1.svg'
SOURCE='research/source-data/kerry-eac-2020/article.pdf'
SOURCE_SHA='4a86d49932d8a2b8d9dd9151e491dc7b8556bdd8b5d6faee575a0d9069c8fdac'

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())

def build():
    data=read(INPUT)
    if data['source_sha256']!=SOURCE_SHA or data['table_pdf_page_1_based']!=9 or data['table_number']!=1:
        raise ValueError('Exact original Table1 required')
    expected=[(-27.5,157.6,820,97.1),(-30.3,156.1,1010,104.2),(-32.3,178.7,1190,141.3),(-33.9,198.7,980,114.5),(-36.2,165.0,1250,132.3)]
    if [(r['latitude_degrees_north'],r['offshore_extent_km'],r['maximum_depth_m'],r['section_area_km2']) for r in data['rows']]!=expected:
        raise ValueError('Source table values/latitude order differ')
    records=[]
    for row in data['rows']:
        records.append({**copy.deepcopy(row),'related_current_id':'east-australian',
            'measurement_type':'published_model_mean_core_section_dimensions',
            'offshore_extent_metric':'shore_referenced_extent_of_mean_velocity_contour',
            'depth_metric':'maximum_depth_of_mean_velocity_contour',
            'area_metric':'cross_sectional_area_inside_mean_velocity_contour',
            'source_locator':'Table1, PDF p.9; mean-core definition section4.1, PDF p.10',
            'statistic':'geometry_of_time_mean_velocity_not_mean_of_instantaneous_dimensions',
            'simulation_period':copy.deepcopy(data['simulation_period']),
            'observed_period':None,'calendar_months':None,'fixed_depth_width_km':None,
            'paired_edge_width_km':None,'uniform_current_thickness_m':None,
            'annual_width_range_km':None,'annual_depth_range_m':None,'numeric_uncertainty_km':None,
            'numeric_depth_uncertainty_m':None,'geometry':None,'geographic_state_crossings':None,
            'independent_observation_count':0,'whole_current_representative':False,
            'seasonal_playback_eligible':False,'physical_state_join_eligible':False,
            'parent_attribution_status':'prepared_source_component_context_pending_parent_audit'})
    return {'schema':'osw.eac-published-mean-core-dimensions.v1','status':'PREPARED_SOURCE_FACTS_NOT_INSTALLED',
        'current_context':'East Australian Current system; source regional components retained separately',
        'source':{'doi':data['source_doi'],'citation':'Kerry, C. G. and Roughan, M. (2020), Downstream Evolution of the East Australian Current System: Mean Flow, Seasonal, and Intra-annual Variability, JGR Oceans125, e2019JC015227.',
            'url':'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019JC015227',
            'institutional_pdf_url':'https://www.unsw.edu.au/content/dam/pdfs/science/bees/research-reports/2024-05-oceanography/2019JC015227.pdf',
            'original_file':SOURCE,'original_sha256':SOURCE_SHA,'original_bytes':27878662,
            'rights':'Copyright2020 American Geophysical Union; original and source-page renders not redistributed.'},
        'method':{'model':'ROMS, free-running regional simulation',
            'signed_mean_alongshore_velocity_contour_m_s':-0.05,
            'negative_direction':'poleward','averaging_order':'time_mean_velocity_then_contour_geometry',
            'cross_shore_grid_resolution_km':[2.5,6],'alongshore_grid_resolution_km':5,
            'grid_rotation_clockwise_degrees':20,'vertical_coordinate':'30 terrain-following s-layers',
            'daily_model_fields_saved':True,'instantaneous_dimension_time_series_transcribed':False,
            'simulation_period':copy.deepcopy(data['simulation_period'])},
        'source_labeling_discrepancy':{'kind':'unresolved_source_figure_label',
            'table1_forster_latitude_degrees_north':-32.3,'figure5_panel_c_header_latitude_degrees_north':-32.0,
            'action':'Keep Table1 latitude and values together. Do not silently substitute the rounded32S prose or figure header.'},
        'input_sha256':{p:sha(p) for p in [INPUT,PROTOCOL,'analysis/eac_kerry_2020_mean_core_v1.py']},
        'records':records,'figure_file':FIGURE,'compact_figure_file':COMPACT,
        'annual_dimension_extrema_available':False,'whole_current_length_km':None,
        'new_independent_observations':0,'source_rows_transcribed':5,'installed':False,'coverage_counters_changed':False,
        'interpretation':['Offshore extent and maximum contour depth describe regional mean model geometry, not fixed-depth paired width or uniform thickness.',
            'Differences between sections are spatial; they do not establish an annual range or numerical uncertainty.',
            'The paper uses a fixed mean-core region to summarize varying transports. Transport variability is not dimension variability.',
            'The989km alongshore analysis sections and744km cross-shore analysis windows are not current length or current width.']}

def figure(doc,compact=False):
    width,height=(480,890) if compact else (1040,650)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">East Australian Current regional mean-core dimensions</title>',
        '<desc id="desc">Five published model cross sections. Offshore extent and maximum contour depth have separate scales. These are dimensions of a long-term mean, not seasonal ranges, uniform thickness or mapped current edges.</desc>',
        f'<rect width="{width}" height="{height}" fill="#f5f9f9"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#173b49}.title{font-weight:700;font-size:24px}.label{font-size:16px}.small{font-size:14px}.value{font-size:17px;font-weight:700}.grid{stroke:#cbdcdd;stroke-width:1}</style>',
        '<text x="24" y="36" class="title">East Australian Current</text>',
        '<text x="24" y="64" class="label">Regional mean core · 1994–2016 model</text>']
    if compact:
        parts+=['<text x="24" y="92" class="small">Mean alongshore velocity contour: −0.05 m/s</text>']
        for i,r in enumerate(doc['records']):
            y=132+i*132
            parts+=[f'<text x="24" y="{y}" class="label">{abs(r["latitude_degrees_north"]):g}°S · {html.escape(r["place"])}</text>',
                f'<text x="24" y="{y+25}" class="small">Offshore extent</text><line x1="155" y1="{y+20}" x2="420" y2="{y+20}" class="grid"/>',
                f'<circle cx="{155+r["offshore_extent_km"]/240*265:.2f}" cy="{y+20}" r="5" fill="#087f8c"/><text x="155" y="{y+45}" class="value">{r["offshore_extent_km"]:.1f} km</text>',
                f'<text x="24" y="{y+70}" class="small">Maximum depth</text><line x1="155" y1="{y+65}" x2="420" y2="{y+65}" class="grid"/>',
                f'<circle cx="{155+r["maximum_depth_m"]/1400*265:.2f}" cy="{y+65}" r="5" fill="#ad5c14"/><text x="155" y="{y+90}" class="value">{r["maximum_depth_m"]:,} m</text>']
        parts+=['<text x="24" y="808" class="small">Extent scale: 0–240 km · depth: 0–1,400 m</text>',
            '<text x="24" y="832" class="small">Spatial sections; annual ranges unknown.</text>',
            '<text x="24" y="856" class="small">Kerry &amp; Roughan (2020), Table 1 · OSW chart</text>']
    else:
        parts+=['<text x="24" y="93" class="small">Boundary: −0.05 m/s contour in mean alongshore velocity · five source cross sections</text>',
            '<text x="290" y="134" class="label">Offshore extent (km)</text>',
            '<text x="650" y="134" class="label">Maximum contour depth (m)</text>']
        for x0,scale,steps in [(290,240,[0,60,120,180,240]),(650,1400,[0,350,700,1050,1400])]:
            for tick in steps:
                x=x0+tick/scale*300
                parts+=[f'<line x1="{x}" y1="150" x2="{x}" y2="470" class="grid"/><text x="{x}" y="495" text-anchor="middle" class="small">{tick:,}</text>']
        for i,r in enumerate(doc['records']):
            y=185+i*65
            parts+=[f'<text x="24" y="{y-5}" class="label">{abs(r["latitude_degrees_north"]):g}°S · {html.escape(r["place"])}</text>',
                f'<text x="24" y="{y+16}" class="small">Area {r["section_area_km2"]:.1f} km²</text>',
                f'<circle cx="{290+r["offshore_extent_km"]/240*300:.2f}" cy="{y}" r="6" fill="#087f8c"/><text x="{290+r["offshore_extent_km"]/240*300+10:.2f}" y="{y+5}" class="value">{r["offshore_extent_km"]:.1f}</text>',
                f'<circle cx="{650+r["maximum_depth_m"]/1400*300:.2f}" cy="{y}" r="6" fill="#ad5c14"/><text x="{650+r["maximum_depth_m"]/1400*300+10:.2f}" y="{y+5}" class="value">{r["maximum_depth_m"]:,}</text>']
        parts+=['<text x="24" y="540" class="label">Regional mean geometry; annual ranges and numerical uncertainty are unknown.</text>',
            '<text x="24" y="568" class="small">Offshore extent is not a fixed-depth paired width. Maximum depth is not uniform current thickness.</text>',
            '<text x="24" y="594" class="small">Forster latitude follows Table 1 (32.3°S); Figure 5(c) is labeled 32.0°S. No curve digitization.</text>',
            '<text x="24" y="625" class="small">Kerry &amp; Roughan (2020), doi:10.1029/2019JC015227, Table 1 · Original OSW chart</text>']
    return ('\n'.join(parts+['</svg>'])+'\n').encode()

if __name__=='__main__':
    for path in [FACTS,FIGURE,COMPACT]:
        if (ROOT/path).exists():raise ValueError('Prepared outputs already exist; use a new version')
    doc=build()
    for path,raw in [(FACTS,encoded(doc)),(FIGURE,figure(doc)),(COMPACT,figure(doc,True))]:(ROOT/path).write_bytes(raw)
    print('Prepared five source-scoped mean model sections and two original SVGs; not installed')
