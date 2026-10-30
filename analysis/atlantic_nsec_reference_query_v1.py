"""Prepare two editorial reference rows against the exact cloud-audited parent."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
FILE='research/atlantic-nsec-reference-query-contract-v1.json'
PREPARED='research/atlantic-nsec-schematic-reference-reaches-prepared-v1.json'
REVIEW='research/atlantic-nsec-reference-parent-execution-review-v1.json'
PARENT_FOLDER='research/atlantic-nsec-reference-parent-run-v1/'
PARENT='191874b005d09c9680e13e5f1fd037a4045a47bbc709782318c3a3d5561d5127'
OWNER='current:atlantic-south-equatorial'
PUBLICATION='source:stramma-schott-1999-tropical-atlantic-mean-flow'
METHOD='source:osw-atlantic-nsec-schematic-reference-method-v1'
KEY='atlantic_nsec_reference_routes_v1'


def read(p):return json.loads((ROOT/p).read_bytes())
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def fingerprint(v):return hashlib.sha256(encoded(v)).hexdigest()
def owns(row):return row.get('entity_id')==OWNER or row.get('current_id')=='atlantic-south-equatorial'
def query_url(route):
    query={'collection':'reference_routes','filters':[{'field':'id','op':'eq','value':route}],'limit':1}
    return 'query.html?q='+quote(json.dumps(query,separators=(',',':')))+'&inspect='+quote(route)+'#query-map-section'
def atlas_url(route):return 'reference-routes.html?atlas-layout=map&atlas-feature='+quote(OWNER)+'&atlas-route='+quote(route)+'#route-atlas'


def build_contract():
    audit=read(PARENT_FOLDER+'result.json');selected=read(PARENT_FOLDER+'selected-records.json');review=read(REVIEW)
    request=read('research/atlantic-nsec-reference-parent-request-v1.json')
    if audit['status']!='PASS_READ_ONLY_PARENT_AND_GEOGRAPHY' or audit['logical_sha256']!=PARENT or audit['parent_audit']['candidate_id_matches']!=0 or selected['reference_routes'] or selected['publication_candidates']:
        raise ValueError('Exact duplicate-free parent and missing publication required')
    if review['status']!='PASS_EXACT_PARENT_DUPLICATE_AUDIT_AND_54_CASE_COAST_REVIEW' or not review['all_54_scenarios_clear_both_masks'] or len(review['actual_maps_viewed'])!=1 or review['actual_maps_viewed'][0]['actually_viewed'] is not True:
        raise ValueError('All scenarios and actual map review required')
    for p,pin in review['retained_evidence_sha256'].items():
        if sha(p)!=pin:raise ValueError('Changed retained evidence: '+p)
    if request['execute'] is not False or request['completed_run_id']!=41059549594:raise ValueError('Completed disabled audit required')
    prepared=read(PREPARED);routes=[]
    for i,source in enumerate(prepared['routes']):
        phase='Northern spring' if source['phase']=='northern_spring' else 'Northern fall'
        cases=[r['reference_length_km'] for r in prepared['editorial_sensitivity_cases'] if r['route_id']==source['id']]
        route={'id':source['id'],'entity_id':OWNER,'current_id':'atlantic-south-equatorial',
            'name':f'Atlantic SEC northern branch — {phase.lower()} regional reference',
            'label':f'nSEC {phase.lower()}: 0°–35°W reference reach','type':'editorial_regional_reference_connection',
            'status':'reviewed_editorial_regional_reference_connection','record_type':'regional_editorial_reference_not_observed_axis',
            'scope':'OSW mid-basin reach of the Atlantic SEC northern branch only. The selected 0° and 35°W gates are not current origin or termination. Other SEC branches and boundary-current extensions are excluded.',
            'layer':prepared['layer'],'time_convention':prepared['time_convention'],'phase':source['phase'],'source_panel':source['source_panel'],
            'source_id':PUBLICATION,'source_ids':[PUBLICATION,METHOD],'method_source_id':METHOD,
            'source_url':prepared['source_url'],'source_locator':prepared['source_locator'],
            'source_file':PREPARED,'source_file_sha256':sha(PREPARED),'source_pointer':'/routes/'+str(i),
            'coordinates_lon_lat':source['coordinates_lon_lat'],'geometry':{'type':'LineString','coordinates':source['coordinates_lon_lat']},
            'geometry_role':'editorial_reference_route','role':'editorial_reference_route',
            'computed_nominal_reference_length_km':source['calculated_reference_length_km'],
            'approximate_reference_path_km':source['approximate_display_length_km'],
            'editorial_probe_length_range_km':[min(cases),max(cases)],'scenario_count':len(cases),
            'editorial_probe_interpretation':prepared['sensitivity_interpretation'],'comparison_group':'osw_studied_reach_routes',
            'figure_file':'figures/atlantic-nsec-schematic-reference-reaches-prepared-v1.svg',
            'rank_eligible':False,'whole_current_length_km':None,'physical_width_km':None,'current_thickness_m':None,
            'annual_length_range_km':None,'annual_width_range_km':None,'uncertainty_km':None,'sample_date':None,
            'independent_observation_count':0,'physical_current_axis_admitted':False,'physical_current_edges_admitted':False,
            'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'geographic_seasonal_playback_eligible':False,
            'nasa_identity_verified':False,'nominal_atlas_state_crossings':None,'recommended_nasa_tile_id':None}
        routes.append(route)
    if len(routes)!=2 or any(r['scenario_count']!=27 for r in routes):raise ValueError('Two independently scoped references required')
    sources=[{'id':PUBLICATION,'kind':'external','title':'The mean flow field of the tropical Atlantic Ocean',
        'label':'The mean flow field of the tropical Atlantic Ocean','authors':['Lothar Stramma','Friedrich Schott'],
        'year':1999,'doi':prepared['source_doi'],'url':prepared['source_url'],'material_use_class':'editorial_schematic_reference_context',
        'provider_asset_redistributed':False,'source_pdf_sha256':prepared['source_pdf_sha256'],
        'source_facts_file':'research/atlantic-nsec-schematic-reference-preparation-review-v1.json',
        'source_facts_sha256':sha('research/atlantic-nsec-schematic-reference-preparation-review-v1.json')},
        {'id':METHOD,'kind':'internal','path':'analysis/atlantic_nsec_reference_reaches_v1.py',
         'url':'../analysis/atlantic_nsec_reference_reaches_v1.py','title':'OSW Atlantic nSEC schematic regional reference method v1'}]
    old=selected['objects'][0];owner=copy.deepcopy(old)
    if old['route_ids'] or old['capabilities']['reference_route']!=0:raise ValueError('Prior owner routes need reconciliation')
    owner['route_ids']=[r['id'] for r in routes];owner['capabilities']['reference_route']=2
    owner['route_url']=atlas_url(routes[0]['id'])
    for route in routes:
        owner['map_features'].append({'geometry':copy.deepcopy(route['geometry']),'candidate_id':route['id'],
            'role':'editorial_reference_route','source_id':PUBLICATION,'source_url':route['source_url'],
            'source_file':PREPARED,'source_file_sha256':route['source_file_sha256'],'source_pointer':route['source_pointer'],
            'note':route['scope'],'layer':route['layer'],'time_convention':route['time_convention'],
            'observation_date':None,'physical_current_axis_admitted':False,'physical_state_join_eligible':False})
        owner['evidence_links'].append({'label':route['label'],'url':query_url(route['id'])})
    owner['source_ids']=sorted(set(old['source_ids'])|{PUBLICATION,METHOD});owner['linked_source_count']=len(owner['source_ids'])
    owner['section_fingerprints']['routes_geometry']=fingerprint({'prior':old['section_fingerprints']['routes_geometry'],'routes':routes})
    owner['section_fingerprints']['sources']=fingerprint({'prior':old['section_fingerprints']['sources'],'new_sources':sources})
    owner['fingerprint']=fingerprint({k:v for k,v in owner.items() if k!='fingerprint'})
    prior_decision=selected['route_decisions'][0];decision=copy.deepcopy(prior_decision)
    decision.update(prior_route_decision=copy.deepcopy(prior_decision),route_ids=owner['route_ids'],candidate_count=2,
        construction_status='regional_schematic_references_constructed_whole_current_unresolved',
        source_catalog_file=PREPARED,source_catalog_sha256=sha(PREPARED),
        next_action='Recover whole-current endpoints and other SEC branches; two regional schematic reaches do not establish a complete axis or annual range.')
    decision['source_decision'].update(candidate_ids=owner['route_ids'],reference_path_decision=decision['construction_status'],next_action=decision['next_action'])
    decision['source_decision'].update(known_component_currents=['Atlantic SEC northern branch (nSEC)'],
        component_inventory_status='partial_source_specific_branch_reference_not_complete_SEC_inventory')
    counts=copy.deepcopy(read('research/current-core-dimensions-query-contract-v1.json')['parent_collection_counts'])
    for name,extra in [('sources',2),('widths',1),('current_regional_reaches',1)]:counts[name]+=extra
    if sum(counts.values())!=110324 or len(counts)!=78:raise ValueError('Wrong exact installed parent counts')
    inputs=[PREPARED,REVIEW,PARENT_FOLDER+'result.json',PARENT_FOLDER+'selected-records.json',PARENT_FOLDER+'run-receipt.json',
        PARENT_FOLDER+'geography.json','research/atlantic-nsec-reference-parent-request-v1.json',
        'research/atlantic-nsec-schematic-reference-reach-input-v1.json','research/atlantic-nsec-schematic-reference-preparation-review-v1.json',
        'figures/atlantic-nsec-schematic-reference-reaches-prepared-v1.svg','analysis/atlantic_nsec_reference_reaches_v1.py',
        'analysis/atlantic_nsec_reference_query_v1.py']
    return {'schema':'osw.atlantic-nsec-reference-query-contract.v1','parent_logical_sha256':PARENT,
        'parent_collection_counts':counts,'prior_owner':old,'prior_entity':selected['entities'][0],
        'prior_decision':prior_decision,'prior_owner_sources':selected['owner_sources'],'prior_widths':selected['widths'],
        'prior_length_assessments':selected['length_assessments'],'final_owner':owner,'final_decision':decision,
        'routes':routes,'new_sources':sources,'reference_routes_added':2,'publication_sources_added':1,'internal_method_sources_added':1,
        'reported_whole_current_lengths_added':0,'annual_ranges_added':0,'physical_geometries_added':0,
        'independent_observations_added':0,'input_sha256':{p:sha(p) for p in inputs},'installed':False}


if __name__=='__main__':
    path=ROOT/FILE
    if path.exists():raise ValueError('Use a new contract version')
    path.write_bytes(encoded(build_contract()));print('Prepared two editorial references, one publication, one internal method and exact owner/decision projections.')
