"""Source-scoped Madagascar width preparation; no fields or runtime packet loads."""
from pathlib import Path
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/ponsoni-emc-2016-dimension-source-facts-v1.json'
PREPARED = 'research/ponsoni-emc-2016-width-prepared-v1.json'
FIGURE = 'figures/ponsoni-emc-2016-dimensions-compact-v1.svg'
PROTOCOL = 'plans/ponsoni-emc-2016-dimension-evidence-protocol-v1.md'
RECEIPT = 'research/source-data/ponsoni-emc-2016/acquisition-v1.json'
SHA = '5f0c0595739ff22a84fa30d9bdeefe2b4a9a2a1d1ea211642c01e37a0ac1b4b4'

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def build():
    receipt = json.loads((ROOT/RECEIPT).read_bytes())
    assert receipt['sha256'] == SHA and receipt['bytes'] == 5135210
    # This small source ledger proves the prior identity and survey summary;
    # it is not treated as the current installed packet.
    prior = json.loads((ROOT/'research/southern-east-madagascar-prose-dimension-admissions.json').read_bytes())
    assert prior['entity_id'] == 'current:southern-east-madagascar'
    events = [
        ('2010-11-17','h','Strong transport event'),
        ('2010-12-30','b','Nearshore flow reversal; offshore migration'),
        ('2011-01-19','i','Wider than the November 2010 event'),
        ('2011-06-02','g','Deep core excursion'),
        ('2011-07-07','c','Cyclonic-eddy-associated flow reversal'),
        ('2012-07-22','f','Exceptionally weak current'),
        ('2012-11-28','d','Weak surface and undercurrent example'),
        ('2012-12-25','e','Strong surface and undercurrent example'),
    ]
    facts = {
        'schema':'osw.ponsoni-emc-dimension-source-facts.v1',
        'status':'ORIGINAL_SELECTED_PAGES_REVIEWED_SOURCE_PREPARATION_NOT_INSTALLED',
        'entity_id':prior['entity_id'],
        'source':{'authors':['Leandro Ponsoni','Borja Aguiar-González','Herman Ridderinkhof','Leo R. M. Maas'],
                  'year':2016,'title':'The East Madagascar Current: Volume Transport and Variability Based on Long-Term Observations',
                  'doi':'10.1175/JPO-D-15-0154.1','url':'https://www.vliz.be/imisdocs/publications/288912.pdf',
                  'original_sha256':SHA,'original_bytes':5135210,'pages':21},
        'identity_evidence':{'locator':'printed1046 / PDF2, opening paragraph',
            'scope':'Poleward East Madagascar Current, also termed Southeast Madagascar Current; existing southern-east-madagascar owner candidate.',
            'remote_installed_identity_join_verified':False,'undercurrent_or_north_current_inheritance':False},
        'period':{'start':'2010-10-07','end':'2013-03-12','source_reported_days':888,'locator':'printed1047 / PDF3, section2b'},
        'section':{'nominal_latitude_degrees_north':-23,'precise_section_coordinates':None,
                   'scope':'Five-mooring INATEX array immediately north of23S off southeastern Madagascar',
                   'moorings':[{'id':f'EMC{i+1}','coast_distance_km':v} for i,v in enumerate([6.3,18.6,44.8,58.7,110.8])],
                   'locator':'printed1047 / PDF3, section2a'},
        'width_summary':{'range_km':[60,100],'approximate':True,'interpretation':'Author-reported typical study-summary width, not a measured annual minimum/maximum.',
                         'locator':'abstract printed1045 / PDF1; discussion printed1060 / PDF16',
                         'edge_operator':None,'fixed_layer_bounds_m':None,'uncertainty_km':None,'central_width_km':None,
                         'annual_range_km':None,'confidence_interval':False},
        'separate_context':{'mean_vertical_reach_m':1000,'mean_core_coast_distance_km':20,
                            'approximate':True,'uniform_thickness_inference':False,'width_edge_inference':False,
                            'locator':'printed1060 / PDF16; mean level of no motion discussed printed1051 / PDF7'},
        'processing_caveats':['Upper roughly50m extrapolated to surface; surface core is not directly sampled at all levels.',
            'Upper EMC3 ADCP failed; horizontal interpolation fills missing data.',
            'Daily low-pass-filtered velocities on1km cross-shore by8m vertical grid; grid spacing is not uncertainty.',
            'Figure4 cross-shore origin is EMC1,6.3km from shore, not the coastline.',
            'Mooring spacing can miss the true instantaneous current core.'],
        'event_index':[{'id':'ponsoni-emc-2016-fig4-'+p,'date':d,'source_panel':'Figure4'+p,
            'source_pdf_page':8,'description':s,'width_km':None,'current_axis_coordinates':None,
            'kind':'published_selected_event_not_climatology','seasonal_playback_eligible':False} for d,p,s in events],
        'event_context':{'date':'2011-06-02','source_panel':'Figure4g',
            'approximate_core_depth_m':450,'minus_10_cm_s_isotach_depth_at_EMC3_m':2500,
            'locator':'printed1053 / PDF9, section3a','catalogue_thickness_extrema_eligible':False},
        'prior_survey_comparison':{'record_id':'southern-east-madagascar-nauw2008-near-surface-survey-width',
            'period':'2001-04','approximate_width_km':120,'new_observation':False,
            'same_boundary_operator_verified':False,'combined_annual_range_eligible':False},
        'whole_current_length_km':None,'seasonal_width_series':None,'geographic_envelope':None,
        'new_installed_measurement_records':0,'prepared_width_records':1,'width_samples_prepared':0,
        'event_index_records_prepared':8,'source_figure_digitization':False,'original_fields_processed':False,
        'figure_file':FIGURE,'input_sha256':{p:sha(p) for p in [PROTOCOL,RECEIPT,
            'analysis/ponsoni_emc_2016_dimensions_v1.py','research/southern-east-madagascar-prose-dimension-admissions.json']}}
    width = {'schema':'osw.prepared-scoped-width-record.v1','status':'PREPARED_NOT_INSTALLED',
        'id':'southern-east-madagascar-ponsoni2016-inatex-study-summary-width',
        'current_id':'southern-east-madagascar','entity_id':facts['entity_id'],
        'measurement_type':'published_regional_summary','width_metric':'author_reported_typical_mooring_study_width',
        'approximate_width_km':None,'width_range_km':[60,100],
        'range_interpretation':facts['width_summary']['interpretation'],
        'geographic_scope':facts['section']['scope'],'boundary_rule':'Author prose; paired edges and numerical cutoff unspecified.',
        'boundary_sides':'author_reported_width_edges_not_supplied','fixed_layer_bounds_m':None,
        'vertical_scope':'Approximately surface to1000m mean reach is separate context; no fixed width layer established.',
        'observed_period':{'start':'2010-10-07','end':'2013-03-12'},'time_precision':'study_period',
        'source_url':facts['source']['url'],'source_doi':facts['source']['doi'],
        'source_locator':facts['width_summary']['locator'],'source_report_file':FACTS,
        'source_report_sha256':hashlib.sha256(encoded(facts)).hexdigest(),
        'uncertainty_km':None,'whole_current_width_km':None,'annual_width_range_km':None,'geographic_current_edges':None,
        'whole_current_representative':False,'width_rank_eligible':False,'full_width_inference_eligible':False,
        'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'is_confidence_interval':False,
        'independent_width_samples_admitted':False,'remote_duplicate_and_join_check_pending':True}
    return facts,width

def figure(facts):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="480" height="1040" viewBox="0 0 480 1040" role="img" aria-labelledby="title desc">',
        '<title id="title">Madagascar Current: regional width and dated events</title>',
        '<desc id="desc">Prepared evidence, not installed. Typical study-summary width60 to100km. The prior April2001 survey reports approximately120km with a different unspecified boundary operator. Eight dated events are an index, not a seasonal cycle.</desc>',
        '<rect width="480" height="1040" fill="#f3f8fa"/>']
    def text(x,y,s,size=14,color='#18394b',weight='400'):
        parts.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(s)}</text>')
    text(24,35,'MADAGASCAR CURRENT',23,weight='700')
    text(24,62,'Regional evidence • nominal 23°S',16)
    text(24,87,'Prepared source evidence • not yet installed',13,'#72521b')
    parts.append('<rect x="16" y="108" width="448" height="279" rx="10" fill="white"/>')
    text(30,137,'Width summaries (km)',18,weight='700')
    text(30,163,'2010–2013 mooring study: about 60–100 km')
    x=lambda v:40+v*2.8
    for v in range(0,141,20):
        parts.append(f'<line x1="{x(v)}" y1="184" x2="{x(v)}" y2="253" stroke="#dae5ea"/>')
        text(x(v),274,str(v),12)
    parts.append(f'<line x1="{x(60)}" y1="199" x2="{x(100)}" y2="199" stroke="#167a85" stroke-width="12"/>')
    text(30,230,'April 2001 survey: about 120 km',13)
    parts.append(f'<circle cx="{x(120)}" cy="247" r="5" fill="#91663b"/>')
    text(30,302,'Different studies; matching edges unverified.',13)
    text(30,325,'The interval is not an annual min/max or error bar.',13)
    text(30,350,'Mean reach ~1,000 m; core ~20 km offshore.',13)
    text(30,372,'Neither value supplies a paired width boundary.',13)
    text(24,422,'Selected dated flow events',19,weight='700')
    text(24,447,'Figure 4, placed here in chronological order',13)
    for i,event in enumerate(facts['event_index']):
        y=479+i*51
        parts.append(f'<circle cx="31" cy="{y-4}" r="4" fill="#167a85"/>')
        text(45,y,event['date']+' • '+event['source_panel'],14,weight='700')
        # All descriptions intentionally fit the narrow source card.
        text(45,y+20,event['description'],12)
    text(24,908,'Discrete events; no numerical event widths extracted.',13)
    text(24,930,'No annual interpolation or seasonal animation implied.',13)
    text(24,960,'Source: Ponsoni et al. (2016), JPO 46, 1045–1065',12)
    text(24,981,'doi:10.1175/JPO-D-15-0154.1 • Figures 1, 2, 4',12)
    text(24,1002,'Surface extrapolation and missing-instrument gaps apply.',12)
    text(24,1023,'Original OSW diagram; publication figures not reproduced.',12)
    parts.append('</svg>')
    return ('\n'.join(parts)+'\n').encode('utf8')

if __name__ == '__main__':
    facts,width=build()
    for path,raw in [(FACTS,encoded(facts)),(PREPARED,encoded(width)),(FIGURE,figure(facts))]:
        if (ROOT/path).exists():
            raise ValueError('Use a new version; preserve frozen source evidence')
        (ROOT/path).write_bytes(raw)
    print('Prepared one scoped width record and eight dated event references; installed counts unchanged.')
