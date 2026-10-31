"""Prepare scoped facts after read-only inventory audit; no packet or index access."""
import copy
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[1]
PETERS='research/peters-2005-redsox-summer-reach-followup-v1.json'
ASCLME='research/indian-sec-asclme-2008-cited-width-followup-v1.json'
NILSEN='research/nilsen-2016-spitsbergen-trough-inventory-lead-v1.json'
PARENT='research/current-core-gap-followup-parent-run-v1'
PREPARED='research/current-core-gap-followup-records-prepared-v1.json'
FIGURE='figures/current-core-gap-followup-scoped-dimensions-v1.svg'
LOGICAL='7b4b5133c915102014f93a6d838e62201b0169e1b183b1d4beae65e01972bccf'
PETERS_SOURCE='source:peters-2005-redsox-plume-structure'
ASCLME_SOURCE='source:asclme-2008-survey3-51pp'
FACT_PINS={PETERS:'12d9a12a1e82e73e5b34964f405cc62040f75fc0a9227c3360c2b9a052a48bf3',
    ASCLME:'17a4bf50db4cd90df063a8f2abd0feeb9fca8b12fe5c32b58f20a41a230671fa',
    NILSEN:'58e7290749c28f4df25cd30b1de79626d4abb970648fe1632f308d98ca49861b'}

def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()

def prepare(peters=None,asclme=None,nilsen=None):
    for path,pin in FACT_PINS.items():
        if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Changed original reviewed source facts: '+path)
    p,a,n=[copy.deepcopy(value if value is not None else read(path)) for value,path in [(peters,PETERS),(asclme,ASCLME),(nilsen,NILSEN)]]
    for value,path in [(p,PETERS),(a,ASCLME),(n,NILSEN)]:
        if value!=read(path):raise ValueError('Changed reviewed source identity or scientific scope: '+path)
    result=read(PARENT+'/result.json');selected=read(PARENT+'/selected-records.json')
    receipt=read(PARENT+'/run-receipt.json')
    if (receipt['run_id']!=41039800756 or receipt['run_attempt']!=1 or receipt['artifact_id']!=12970530165
        or receipt['artifact_zip_sha256']!='eb91780b71faa27ffd05eed70793584a59d69472f8155ba2ca990624f3131fe8'
        or receipt['source_commit']!=result['source_commit']
        or any(sha((ROOT/PARENT/name).read_bytes())!=pin for name,pin in receipt['members_sha256'].items())):
        raise ValueError('Exact cloud result custody required')
    if (result['status']!='PASS_READ_ONLY' or result['source_commit']!='61735a2661d68b47568446785e33b647fd6af5e9'
        or result['logical_sha256']!=LOGICAL or result['selected_records_sha256']!=sha((ROOT/PARENT/'selected-records.json').read_bytes())
        or selected['candidate_record_id_matches'] or selected['named_feature_matches']):
        raise ValueError('Exact reviewed parent without candidate collisions required')
    if any(v['status']!='MISSING' for v in result['publication_resolutions'].values()):raise ValueError('Publication reconciliation required')
    pc=p['candidate'];ac=a['candidate_claim'];pub=p['publication'];report=a['source_report']
    if (p['entity_id']!='current:red-sea-saline-overflow' or pub['doi']!='10.1175/JPO2679.1'
        or pub['pdf_sha256']!='dd85cd4a85fc8842b3819a5d30a2c645b0c74942f4cffa07b450afea372ef61c'
        or pub['pdf_bytes']!=1432988 or not {3,6,7,8,10}.issubset(pub['selected_pdf_pages_individually_viewed'])
        or pc['reported_length_interval_km']!=[110,120]
        or pc['source_contour_references']!=[{'quantity':'speed','value':0.2,'unit':'m/s'},{'quantity':'salinity','value':38,'unit_as_printed':'psu'}]
        or pc['campaign_envelope']['from']!='2001-08-21' or pc['campaign_envelope']['to']!='2001-09-12'
        or pc['campaign_envelope']['exact_reach_occupation_period'] is not False):
        raise ValueError('Reviewed Peters source, regional interval and campaign required')
    if any(pc[k] is not None for k in ['annual_length_range_km','numerical_length_uncertainty_km','geometry','fixed_depth_bounds_m','exact_observed_period']):raise ValueError('Unsupported Peters physical precision')
    if any(pc[k] is not False for k in ['whole_current_representative','whole_current_rank_eligible','seasonal_playback_eligible','synoptic_snapshot']):raise ValueError('Unsupported Peters whole-current or time inference')
    winter_notes=selected['identities'][p['entity_id']]['object']['scope_notes']
    if not any(note.get('audit_file')==p['duplicate_guard']['existing_winter_audit_file'] and '130' in note['summary'] for note in winter_notes):raise ValueError('Preserve existing winter reach')
    if (a['entity_id']!='current:indian-south-equatorial'
        or report['pdf_sha256']!='3209080e3ea3a99de715949769d508e058a1edda879ffb99c96cf60e29766424'
        or report['pages']!=51 or report['pdf_bytes']!=2306067 or not {1,27,30,51}.issubset(report['selected_pdf_pages_individually_viewed'])
        or ac['reported_approximate_width_km']!=650
        or ac['measurement_type']!='literature_cited_approximate_regional_width_claim'
        or ac['source_evidence_kind']!='cruise_report_citing_earlier_width_literature'
        or a['underlying_work_candidate']['original_full_text_reviewed'] is not False
        or a['underlying_work_candidate']['report_bibliography_lists_this_work'] is not False):
        raise ValueError('Reviewed 51-page report and secondary claim class required')
    if any(ac[k] is not None for k in ['observation_period','width_sampling_depth_m','paired_edges','width_operator','annual_width_range_km','numerical_width_uncertainty_km','independent_observation_count']):raise ValueError('Unsupported ASCLME dates, edges, layer or uncertainty')
    if any(ac[k] is not False for k in ['whole_current_representative','width_rank_eligible','seasonal_playback_eligible']):raise ValueError('Unsupported ASCLME whole-current or time inference')
    if n['publication']['source_figures_visually_reviewed'] is not False or n['candidate_entity_id']!='current:spitsbergen-trough':raise ValueError('Nilsen source gate requires a new reviewed preparation')
    reach={'schema':'osw.scoped-length-evidence.v1','id':pc['id'],'entity_id':p['entity_id'],'current_id':'red-sea-saline-overflow',
        'name':'Red Sea saline overflow','component_label':pc['component'],'status':'published_regional_plume_reach',
        'measurement_type':pc['measurement_type'],'length_metric':'author_reported_summer_descending_plume_reach_interval',
        'reported_length_interval_km':[110,120],'representative_length_km':None,
        'interval_interpretation':'Source-reported summer extent interval; not a statistical uncertainty or annual range.',
        'display':'110–120 km','distance_origin':pc['distance_origin'],'source_contour_references':pc['source_contour_references'],
        'boundary_note':pc['boundary_note'],'logical_combination_of_contours':None,'paired_endpoint_coordinates':None,
        'campaign_envelope':pc['campaign_envelope'],'observation_period':None,'synoptic_snapshot':False,
        'fixed_layer_bounds_m':None,'geometry':None,'annual_length_range_km':None,'numerical_length_uncertainty_km':None,
        'whole_current_representative':False,'rank_eligible':False,'seasonal_playback_eligible':False,
        'source_id':PETERS_SOURCE,'source_file':PETERS,'source_pointer':'/candidate','source_doi':pub['doi'],
        'source_url':pub['url'],'source_pdf_sha256':pub['pdf_sha256'],'source_locator':pc['source_locator'],
        'preserved_winter_context_file':p['duplicate_guard']['existing_winter_audit_file'],
        'scope_notes':p['excluded_inferences']}
    width={'schema':'osw.scoped-width-evidence.v1','id':ac['id'],'entity_id':a['entity_id'],'current_id':'indian-south-equatorial',
        'name':'Indian South Equatorial Current','status':'literature_cited_regional_width_claim',
        'source_evidence_kind':ac['source_evidence_kind'],'measurement_type':ac['measurement_type'],
        'width_metric':'literature_cited_approximate_regional_width','approximate_width_km':650,'display':'about 650 km (cited estimate)',
        'geographic_scope':ac['region'],'observation_period':None,'fixed_layer_bounds_m':None,'paired_edge_coordinates':None,
        'boundary_rule':None,'section_geometry':None,'width_range_km':None,'annual_width_range_km':None,'numerical_width_uncertainty_km':None,
        'whole_current_representative':False,'width_rank_eligible':False,'seasonal_playback_eligible':False,'independent_observation_count':None,
        'source_id':ASCLME_SOURCE,'source_file':ASCLME,'source_pointer':'/candidate_claim','source_url':report['url'],
        'source_pdf_sha256':report['pdf_sha256'],'source_locator':ac['source_locator'],'cited_author_year':'New et al. (2007)',
        'underlying_work_candidate':a['underlying_work_candidate'],'underlying_work_is_verified_claim_source':False,
        'report_cover_dates_are_width_dates':False,'adjacent_map_date_is_width_date':False,'scope_notes':a['excluded_inferences']}
    sources=[{'id':PETERS_SOURCE,'kind':'external','title':pub['title'],'label':pub['title'],'authors':pub['authors'],'year':2005,
        'doi':pub['doi'],'url':pub['url'],'source_pdf_sha256':pub['pdf_sha256'],'provider_asset_redistributed':False,
        'material_use_class':'source_scoped_factual_claim'},
        {'id':ASCLME_SOURCE,'kind':'external','title':report['title'],'label':report['title'],'authors':report['authors'],'year':2008,
        'doi':None,'url':report['url'],'source_pdf_sha256':report['pdf_sha256'],'source_pdf_pages':51,
        'series_identifier':report['series_identifier'],'catalogue_status':'final','cover_status':'Preliminary cruise report',
        'provider_asset_redistributed':False,'material_use_class':'literature_cited_source_scoped_factual_claim'}]
    return {'schema':'osw.current-core-gap-followup-prepared.v1','status':'PREPARED_SOURCE_SCOPED_RECORDS_RUNTIME_DELIVERY_PENDING',
        'logical_parent_sha256':LOGICAL,'parent_audit_result_file':PARENT+'/result.json',
        'input_sha256':{path:sha((ROOT/path).read_bytes()) for path in [PETERS,ASCLME,NILSEN,PARENT+'/result.json',PARENT+'/selected-records.json',PARENT+'/run-receipt.json']},
        'regional_length_records':[reach],'width_claim_records':[width],'publication_records':sources,
        'named_inventory_candidate':{'entity_id':n['candidate_entity_id'],'label':n['candidate_name'],'source_doi':n['publication']['doi'],
            'status':'HELD_IDENTITY_SCOPE_AND_ORIGINAL_FIGURE_REVIEW_PENDING','installed_full_name_match_count':0,
            'alias_equivalence_asserted':False,'numeric_records_admitted':0,'geometry':None,
            'primary_metadata_url':'https://pure.uhi.ac.uk/en/publications/a-simple-shelf-circulation-model-intrusion-of-atlantic-water-on-t/'},
        'figure':FIGURE,'new_whole_current_lengths':0,'new_annual_ranges':0,'new_independent_observations':0,
        'new_geometries':0,'installed':False,'full_goal_complete':False,
        'runtime_requirements':[
            'Preserve exact current identities, historical lengths, routes, widths, scope notes and all legacy API cases.',
            'Expose summer reach as a separate scoped length evidence collection and owner capability; never overwrite whole-current length assessment.',
            'Expose the cited width with its evidence class, unverified original attribution and unknown dates in query, object, dashboard, atlas and seasons.',
            'Index original facts and exact record pointers; link both publications to owners without duplicating the existing winter observation.',
            'Render separate length and width scales; interval marks mean source-reported extent, not uncertainty or annual bounds.',
            'Run complete native/WASM response comparisons and review desktop/narrow browser screenshots in sequenced cloud jobs before installation.'
        ]}

def figure(value):
    if value!=prepare():raise ValueError('Exact prepared source-scoped records required')
    raw='''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="750" viewBox="0 0 1000 750" role="img" aria-labelledby="title desc">
<title id="title">Two scoped current dimensions: regional reach and cited width</title>
<desc id="desc">Red Sea Northern Channel summer plume reach: reported 110 to 120 kilometres. Indian South Equatorial Current upstream width: cited estimate about 650 kilometres. Separate scales and evidence classes. Neither is a whole-current dimension, annual range, or measurement uncertainty.</desc>
<rect width="1000" height="750" fill="#f2f8f8"/>
<g font-family="Arial,sans-serif" fill="#153c47">
<text x="40" y="48" font-size="27" font-weight="bold">Two regional dimensions, with their source limits</text>
<text x="40" y="82" font-size="18">Prepared evidence • runtime integration and browser review pending</text>
<text x="40" y="132" font-size="23" font-weight="bold">Red Sea: Northern Channel summer plume reach</text>
<text x="40" y="162" font-size="18">Peters et al. (2005), §5b, p.578 • distance from Perim Narrows</text>
<path d="M60 232H810" stroke="#728b92" stroke-width="2"/>
<g font-size="16" text-anchor="middle"><text x="60" y="259">0</text><text x="310" y="259">50</text><text x="560" y="259">100</text><text x="810" y="259">150 km</text></g>
<path d="M610 208H660M610 196V220M660 196V220" stroke="#087e8b" stroke-width="8" fill="none"/>
<text x="690" y="215" font-size="22" font-weight="bold">110–120 km</text>
<text x="40" y="295" font-size="17">Source extent interval using speed 0.2 m/s and salinity 38 psu contours.</text>
<text x="40" y="322" font-size="17">Campaign: 21 Aug–12 Sep 2001; exact reach occupation dates unknown.</text>
<text x="40" y="349" font-size="17">Existing winter 130 km report uses different support; no annual range formed.</text>
<path d="M40 378H960" stroke="#c4d5da"/>
<text x="40" y="421" font-size="23" font-weight="bold">Indian SEC: width upstream of the Mascarene Plateau</text>
<text x="40" y="452" font-size="18">ASCLME 2008, 51-page report, p.30 • cites New et al. (2007)</text>
<path d="M60 520H760" stroke="#728b92" stroke-width="2"/>
<path d="M710 492L720 502L710 512L700 502Z" fill="#6b4da2"/>
<text x="736" y="507" font-size="21" font-weight="bold">~650 km</text>
<g font-size="16" text-anchor="middle"><text x="60" y="548">0</text><text x="260" y="548">200</text><text x="460" y="548">400</text><text x="660" y="548">600</text><text x="760" y="548">700 km</text></g>
<text x="40" y="585" font-size="17">Cited estimate; original attribution and measurement method remain unverified.</text>
<text x="40" y="612" font-size="17">Width dates, depth, paired edges and numerical uncertainty: unknown.</text>
<text x="40" y="660" font-size="19" font-weight="bold">Separate scales • regional evidence • no whole-current ranking</text>
<text x="40" y="692" font-size="17">Neither record supplies annual extrema, observed geometry or seasonal playback.</text>
<text x="40" y="721" font-size="15">Spitsbergen Trough Current: name candidate held; no distances admitted pending original figure review.</text>
</g></svg>
'''.encode()
    ElementTree.fromstring(raw)
    return raw

if __name__=='__main__':
    value=prepare();(ROOT/PREPARED).write_bytes(encoded(value));(ROOT/FIGURE).write_bytes(figure(value))
    print(json.dumps({'status':value['status'],'regional_length_records':1,'cited_width_records':1,'named_feature_held':True,'installed':False}))
