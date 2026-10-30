"""Prepare two reported regional jet widths; never synthesize current geometry."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FACTS='research/pacific-sec-gourdeau-2008-width-source-facts-v1.json'
PREPARED='research/pacific-sec-gourdeau-2008-widths-prepared-v1.json'
FIGURE='figures/pacific-sec-gourdeau-2008-regional-widths-v1.svg'
PDF_SHA='bb3cadf9154823522aea2f8ee0f12eec2ff53c525b6e941d79c3e23228c0cf7b'

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def prepare(facts=None):
    facts=copy.deepcopy(facts if facts is not None else json.loads((ROOT/FACTS).read_bytes()))
    expected=[('north_vanuatu_jet','North Vanuatu Jet',300),('north_caledonian_jet','North Caledonian Jet',100)]
    if (facts['doi']!='10.1175/2007JPO3780.1' or facts['source_pdf_sha256']!=PDF_SHA
        or facts['source_pdf_bytes']!=1229574 or facts['all_11_original_pages_individually_viewed'] is not True
        or facts['entity_id']!='current:pacific-south-equatorial'
        or facts['campaign_start']!='2005-07-17' or facts['campaign_end']!='2005-10-17'
        or facts['glider_sampling_layer_m']!=[0,600]
        or [(r['component_key'],r['component'],r['reported_approximate_width_km']) for r in facts['width_candidates']]!=expected):
        raise ValueError('Reviewed source identity, components, campaign and values required')
    for key in ['width_edge_threshold','width_edge_coordinates','fixed_depth_width_operator','annual_width_range','numerical_width_uncertainty','whole_current_width','whole_current_length']:
        if facts[key] is not None:raise ValueError('Unsupported dimension or precision: '+key)
    if (facts['campaign_dates_are_individual_edge_crossing_dates'] is not False
        or facts['survey_track_distance_is_current_length'] is not False
        or facts['transport_error_is_width_error'] is not False or facts['geometry_added'] is not False):
        raise ValueError('Unsupported geometry, dates or uncertainty conversion')
    rows=[]
    for n,(component,label,width) in enumerate(expected):
        rows.append({'schema':'osw.scoped-width-evidence.v1','id':'pacific-sec-gourdeau2008-'+component.replace('_','-')+'-reported-width',
            'entity_id':facts['entity_id'],'current_id':'pacific-south-equatorial','name':'Pacific South Equatorial Current',
            'component':component,'component_label':label,'status':'published_regional_component_width',
            'measurement_type':'source_reported_campaign_jet_width','width_metric':'author_reported_regional_jet_width',
            'approximate_width_km':width,'source_reported_width_km':width,'display':'about '+str(width)+' km',
            'width_range_km':None,'annual_width_range_km':None,'numerical_width_uncertainty_km':None,
            'boundary_rule':None,'edge_operator':None,'paired_edge_coordinates':None,'section_geometry':None,
            'fixed_layer_bounds_m':None,'sampling_layer_bounds_m':[0,600],
            'observation_period':{'from':'2005-07-17','to':'2005-10-17','kind':'campaign_envelope','individual_crossing_dates_known':False},
            'whole_current_representative':False,'seasonal_playback_eligible':False,'width_rank_eligible':False,
            'independent_observation_count':None,'source_file':FACTS,'source_pointer':'/width_candidates/'+str(n),
            'source_pdf_sha256':PDF_SHA,'source_doi':facts['doi'],'source_locator':'Abstract p.715; Results p.722; Figs.2,4,5',
            'scope':'Coral Sea inflow component; author-reported width from a nonsynoptic campaign. Exact numerical edge threshold unspecified.',
            'layer_note':'Glider observations cover 0-600 m. This is not a fixed-depth width or current thickness.',
            'source_scope_notes':copy.deepcopy(facts['source_scope_notes'])})
    return {'schema':'osw.pacific-sec-gourdeau-2008-width-preparation.v1','status':'PREPARED_EXACT_PARENT_DUPLICATE_AUDIT_AND_DELIVERY_PENDING',
        'source_facts_file':FACTS,'source_facts_sha256':hashlib.sha256(encoded(facts)).hexdigest(),'figure':FIGURE,
        'width_records':rows,'width_records_proposed':2,'whole_current_lengths_added':0,'annual_ranges_added':0,
        'width_samples_added':0,'geometry_added':False,'installed':False,'full_goal_complete':False}

def figure(prepared):
    if prepared!=prepare():raise ValueError('Exact prepared source facts required')
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="530" viewBox="0 0 1000 530" role="img" aria-labelledby="title desc">
<title id="title">Pacific SEC: two regional jet widths</title>
<desc id="desc">Reported approximate widths: North Vanuatu Jet 300 km; North Caledonian Jet 100 km. Different components from July to October 2005, not annual bounds or whole-current widths.</desc>
<rect width="1000" height="530" fill="#f2f8f8"/>
<g fill="#153c47" font-family="Arial, sans-serif">
<text x="40" y="53" font-size="29" font-weight="bold">Pacific SEC: two regional jet widths</text>
<text x="40" y="88" font-size="18">Coral Sea inflow | July-October 2005 campaign | Gourdeau et al. (2008)</text>
<text x="40" y="146" font-size="21" font-weight="bold">North Vanuatu Jet</text>
<rect x="40" y="166" width="720" height="34" rx="4" fill="#087e8b"/>
<text x="780" y="191" font-size="23" font-weight="bold">about 300 km</text>
<text x="40" y="251" font-size="21" font-weight="bold">North Caledonian Jet</text>
<rect x="40" y="271" width="240" height="34" rx="4" fill="#6b4da2"/>
<text x="300" y="296" font-size="23" font-weight="bold">about 100 km</text>
<text x="40" y="344" font-size="17">Common linear scale: bar length shows the reported approximate width.</text>
<text x="40" y="390" font-size="18" font-weight="bold">Two components, not a 100-300 km seasonal range.</text>
<text x="40" y="421" font-size="17">Annual bounds, numerical width uncertainty and exact edge threshold: unknown.</text>
<text x="40" y="451" font-size="17">Glider sampling: 0-600 m; neither a fixed-depth width nor full-current thickness.</text>
<text x="40" y="497" font-size="16">Source: Gourdeau et al. (2008), doi:10.1175/2007JPO3780.1 | pp.715,722</text>
</g></svg>
'''.encode()

if __name__=='__main__':
    value=prepare();(ROOT/PREPARED).write_bytes(encoded(value));(ROOT/FIGURE).write_bytes(figure(value))
