"""Freeze two regional references and24 source-plot profiles against one audited parent."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
FILE='research/current-reference-profile-batch-query-contract-v1.json'
KEY='current_reference_profile_batch_v1'
PARENT='09b882c97c922a0643880885a6165388bf41b19903e72a6d9ca44437da1ed41e'
FOLDER='research/atlantic-nec-reference-parent-run-v1/'
ROUTES='research/atlantic-nec-schematic-reference-reaches-prepared-v1.json'
PROFILES='research/pacific-sec-sun-2025-core-migration-profile-prepared-v1.json'
COLLECTION='current_core_migration_profiles'
NEC='current:atlantic-north-equatorial'
SEC='current:pacific-south-equatorial'
PUBLICATION='source:stramma-schott-1999-tropical-atlantic-mean-flow'
METHOD='source:osw-atlantic-nec-schematic-reference-method-v1'
SUN='source:sun-zhang-2025-pacific-sec-core-migration'
PROFILE_METHOD='source:osw-sun-2025-core-migration-plot-reading-v1'

def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def owns(row,owner):return row.get('entity_id')==owner or row.get('current_id')==owner.removeprefix('current:')
def query_url(collection,field,value,inspect=None):
    q={'collection':collection,'filters':[{'field':field,'op':'eq','value':value}],'limit':100}
    return 'query.html?q='+quote(json.dumps(q,separators=(',',':')))+(('&inspect='+quote(inspect)) if inspect else '')+'#query-chart-section'
def atlas_url(route):return 'reference-routes.html?atlas-layout=map&atlas-feature='+quote(NEC)+'&atlas-route='+quote(route)+'#route-atlas'

def build_contract():
    audit=read(FOLDER+'result.json');selected=read(FOLDER+'selected-records.json')
    review=read('research/atlantic-nec-reference-parent-execution-review-v1.json')
    request=read('research/atlantic-nec-reference-parent-request-v1.json')
    if (audit['status']!='PASS_READ_ONLY_PARENT_AND_GEOGRAPHY' or audit['logical_sha256']!=PARENT
        or audit['parent_audit']['candidate_id_matches']!=0 or selected['reference_routes']
        or len(selected['publication_candidates'])!=1 or selected['sun_2025_source_candidates']
        or selected['prepared_profile_ids_checked']!=24):raise ValueError('Exact duplicate-free two-owner parent required')
    if (review['status']!='PASS_EXACT_PARENT_DUPLICATE_AUDIT_AND_36_CASE_COAST_REVIEW'
        or not review['all_36_scenarios_clear_both_masks'] or len(review['actual_maps_viewed'])!=1
        or review['actual_maps_viewed'][0]['actually_viewed'] is not True
        or request['execute'] is not False or request['completed_run_id']!=41133819361):
        raise ValueError('Completed geography and actual-map acceptance required')
    for p,pin in review['retained_evidence_sha256'].items():
        if sha(p)!=pin:raise ValueError('Retained evidence changed: '+p)
    publication=selected['publication_candidates'][0]
    if publication['id']!=PUBLICATION:raise ValueError('Existing publication must be reused exactly')
    prepared=read(ROUTES);profile=read(PROFILES)
    routes=[]
    for i,source in enumerate(prepared['routes']):
        phase='Northern spring' if source['phase']=='northern_spring' else 'Northern fall'
        cases=[c['reference_length_km'] for c in prepared['editorial_sensitivity_cases'] if c['route_id']==source['id']]
        if len(cases)!=18:raise ValueError('All18 gate/drawing choices per phase required')
        routes.append({'id':source['id'],'entity_id':NEC,'current_id':'atlantic-north-equatorial',
            'name':f'Atlantic NEC — {phase.lower()} interior reference',
            'label':f'NEC {phase.lower()}: 30°–55°W interior reach',
            'type':'editorial_regional_reference_connection','status':'reviewed_editorial_regional_reference_connection',
            'record_type':'regional_editorial_reference_not_observed_axis',
            'scope':'One NEC-labelled schematic curve between selected30W and55W interior gates. Other parallel NEC flows and eastern/western continuations are excluded; gates are not current endpoints.',
            'layer':prepared['layer'],'time_convention':prepared['time_convention'],'phase':source['phase'],
            'source_panel':source['source_panel'],'source_id':PUBLICATION,'source_ids':[PUBLICATION,METHOD],
            'method_source_id':METHOD,'source_url':prepared['source_url'],'source_locator':prepared['source_locator'],
            'source_file':ROUTES,'source_file_sha256':sha(ROUTES),'source_pointer':'/routes/'+str(i),
            'coordinates_lon_lat':source['coordinates_lon_lat'],'geometry':{'type':'LineString','coordinates':source['coordinates_lon_lat']},
            'geometry_role':'editorial_reference_route','role':'editorial_reference_route',
            'computed_nominal_reference_length_km':source['calculated_reference_length_km'],
            'approximate_reference_path_km':source['approximate_display_length_km'],
            'editorial_probe_length_range_km':[min(cases),max(cases)],'scenario_count':18,
            'editorial_probe_interpretation':prepared['scenario_rule']['interpretation'],
            'comparison_group':'osw_studied_reach_routes','figure_file':'figures/atlantic-nec-regional-reference-reaches-v1.svg',
            'compact_figure_file':'figures/atlantic-nec-regional-reference-reaches-compact-v1.svg',
            'rank_eligible':False,'whole_current_length_km':None,'physical_width_km':None,'current_thickness_m':None,
            'annual_length_range_km':None,'annual_width_range_km':None,'uncertainty_km':None,'sample_date':None,
            'independent_observation_count':0,'physical_current_axis_admitted':False,'physical_current_edges_admitted':False,
            'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'geographic_seasonal_playback_eligible':False,
            'comparison_of_phases_is_measured_seasonal_change':False,
            'nasa_identity_verified':False,'nominal_atlas_state_crossings':None,'recommended_nasa_tile_id':None})
    records=[]
    for i,row in enumerate(profile['rows']):
        record=copy.deepcopy(row)
        record.update(label=f'Southern Pacific SEC core movement · {abs(row["section_longitude_degrees_east"])}°W · {row["sampling_depth_m"]}m',
            type='source_plot_core_migration',record_type='regional_published_plot_reading',
            value=row['approximate_migration_degrees'],unit='degrees latitude poleward',
            source_id=SUN,source_ids=[SUN,PROFILE_METHOD],source_url='https://doi.org/10.1186/s40562-025-00393-7',
            source_file=PROFILES,source_file_sha256=sha(PROFILES),source_pointer='/rows/'+str(i),
            source_locator='Original PDF4, Figure'+row['source_panel']+'; method PDF3 and discussion PDF5,7',
            layer=f'{row["sampling_depth_m"]}m source depth; geostrophy referenced to2000m, not a thickness measurement.',
            time_convention='Author figure period1960-2020. Adjacent contours compare1960-1989 and1990-2020; bars do not establish an annual series or exact endpoint displacement.',
            scope='Southern branch under the source10S split, two regional longitude sections. IAP1degree mapped field; finer plot reading adds no physical resolution.',
            component_scope='Southern branch south of10S under Sun and Zhang2025; do not equate branch names from other sources.',
            figure_file='figures/pacific-sec-sun-2025-core-migration-profile-v1.svg',
            compact_figure_file='figures/pacific-sec-sun-2025-core-migration-profile-compact-v1.svg',
            plot_reading_interval_is_measurement_uncertainty=False,underlying_grid_degrees=1,
            no_motion_reference_depth_m=2000,uncertainty_degrees=None,annual_axis_position_range_degrees=None,
            independent_observation_count=0,geometry=None)
        records.append(record)
    if len(records)!=24 or len({r['id'] for r in records})!=24:raise ValueError('Exact24 unique profile readings required')
    sources=[{'id':METHOD,'kind':'internal','path':'analysis/atlantic_nec_reference_reaches_v1.py',
        'url':'../analysis/atlantic_nec_reference_reaches_v1.py','title':'OSW Atlantic NEC interior schematic reference method v1'},
        {'id':SUN,'kind':'external','title':'Observed poleward shift of the South Equatorial Current and associated thermohaline variations in the South Pacific subtropical gyre',
         'authors':['Jingxuan Sun','Linlin Zhang'],'year':2025,'doi':'10.1186/s40562-025-00393-7',
         'url':'https://doi.org/10.1186/s40562-025-00393-7','source_facts_file':'research/pacific-sec-sun-2025-source-facts-v1.json',
         'source_facts_sha256':sha('research/pacific-sec-sun-2025-source-facts-v1.json'),
         'material_use_class':'regional_source_plot_reading','provider_asset_redistributed':False},
        {'id':PROFILE_METHOD,'kind':'internal','path':'analysis/extract_pacific_sec_sun_2025_core_migration_v1.py',
         'url':'../analysis/extract_pacific_sec_sun_2025_core_migration_v1.py','title':'OSW Sun2025 core-migration plot-reading method v1'}]
    pacific=selected['pacific_sec_existing_records']
    prior={NEC:{'objects':selected['objects'],'entities':selected['entities'],'widths':selected['widths'],'length_assessments':selected['length_assessments'],'reference_routes':selected['reference_routes']},SEC:pacific}
    final={}
    for owner,oldset in prior.items():
        if len(oldset['objects'])!=1 or len(oldset['entities'])!=1:raise ValueError('Unique owner/identity required')
        old=oldset['objects'][0];obj=copy.deepcopy(old)
        if owner==NEC:
            if old['route_ids'] or old['capabilities']['reference_route']!=0:raise ValueError('NEC already has routes')
            obj['route_ids']=[r['id'] for r in routes];obj['capabilities']['reference_route']=2;obj['route_url']=atlas_url(routes[0]['id'])
            for route in routes:
                obj['map_features'].append({'geometry':copy.deepcopy(route['geometry']),'candidate_id':route['id'],
                    'role':'editorial_reference_route','source_id':PUBLICATION,'source_url':route['source_url'],
                    'source_file':ROUTES,'source_file_sha256':sha(ROUTES),'source_pointer':route['source_pointer'],
                    'note':route['scope'],'layer':route['layer'],'time_convention':route['time_convention'],
                    'observation_date':None,'physical_current_axis_admitted':False,'physical_state_join_eligible':False})
                obj['evidence_links'].append({'label':route['label'],'url':query_url('reference_routes','id',route['id'],route['id'])})
            obj['section_fingerprints']['routes_geometry']=digest({'prior':old['section_fingerprints']['routes_geometry'],'routes':routes})
            extra={PUBLICATION,METHOD}
        else:
            obj['core_migration_profile_ids']=[r['id'] for r in records];obj['capabilities']['core_migration_profile']=24
            obj['evidence_links'].append({'label':'Core movement by depth ·1960-2020 source profile','url':query_url(COLLECTION,'current_id','pacific-south-equatorial')})
            obj['section_fingerprints']['measurements']=digest({'prior':old['section_fingerprints']['measurements'],'core_migration_profiles':records})
            extra={SUN,PROFILE_METHOD}
        obj['source_ids']=sorted(set(old['source_ids'])|extra);obj['linked_source_count']=len(obj['source_ids'])
        obj['section_fingerprints']['sources']=digest({'prior':old['section_fingerprints']['sources'],'added_ids':sorted(extra)})
        obj['fingerprint']=digest({k:v for k,v in obj.items() if k!='fingerprint'});final[owner]=obj
    decision=copy.deepcopy(selected['route_decisions'][0]);prior_decision=copy.deepcopy(decision)
    decision.update(prior_route_decision=prior_decision,route_ids=[r['id'] for r in routes],candidate_count=2,
        construction_status='regional_schematic_references_constructed_whole_current_unresolved',
        source_catalog_file=ROUTES,source_catalog_sha256=sha(ROUTES),
        next_action='Recover whole-current NEC endpoints and dated velocity axes; two interior schematic reaches do not establish whole-current length or an annual range.')
    decision['source_decision'].update(candidate_ids=decision['route_ids'],reference_path_decision=decision['construction_status'],next_action=decision['next_action'])
    counts=copy.deepcopy(read('research/atlantic-nsec-reference-query-contract-v2.json')['parent_collection_counts'])
    counts['reference_routes']+=2;counts['sources']+=2
    if len(counts)!=78 or sum(counts.values())!=110328:raise ValueError('Installed parent counts differ')
    inputs=[ROUTES,PROFILES,'research/atlantic-nec-schematic-reference-reach-input-v1.json',
        'research/atlantic-nec-schematic-reference-preparation-review-v1.json',
        'research/atlantic-nec-reference-parent-execution-review-v1.json','research/atlantic-nec-reference-parent-request-v1.json',
        FOLDER+'result.json',FOLDER+'selected-records.json',FOLDER+'geography.json',FOLDER+'run-receipt.json',
        'research/pacific-sec-sun-2025-source-facts-v1.json','research/pacific-sec-sun-2025-migration-extraction-input-v1.json',
        'research/pacific-sec-sun-2025-profile-preparation-review-v1.json',
        'analysis/atlantic_nec_reference_reaches_v1.py','analysis/extract_pacific_sec_sun_2025_core_migration_v1.py',
        'analysis/current_reference_profile_batch_query_v1.py',
        'figures/atlantic-nec-regional-reference-reaches-v1.svg','figures/atlantic-nec-regional-reference-reaches-compact-v1.svg',
        'figures/pacific-sec-sun-2025-core-migration-profile-v1.svg','figures/pacific-sec-sun-2025-core-migration-profile-compact-v1.svg']
    return {'schema':'osw.current-reference-profile-batch-query-contract.v1','parent_logical_sha256':PARENT,
        'parent_collection_counts':counts,'prior_owners':prior,'final_objects':final,
        'prior_decision':prior_decision,'final_decision':decision,'prior_publication':publication,
        'prior_source_inventory':selected['owner_sources'],'routes':routes,'records':records,'new_sources':sources,
        'collection':COLLECTION,'input_sha256':{p:sha(p) for p in inputs},
        'reference_routes_added':2,'profile_records_added':24,'collections_added':1,'sources_added':3,
        'whole_current_lengths_added':0,'widths_added':0,'annual_ranges_added':0,'physical_geometries_added':0,
        'independent_observations_added':0,'installed':False}

def marker(contract,pin):
    return {'schema':'osw.current-reference-profile-batch-runtime.v1','parent_logical_sha256':PARENT,
        'contract_file':FILE,'contract_sha256':pin,'reference_routes_added':2,'profile_records_added':24,
        'collection':COLLECTION,'sources_added':3,'collections_added':1,'whole_current_lengths_added':0,
        'widths_added':0,'annual_ranges_added':0,'physical_geometries_added':0,'independent_observations_added':0}

def apply_verified(collections,manifest,contract,*,parent_logical_sha256,contract_sha256):
    if parent_logical_sha256!=PARENT or contract['parent_logical_sha256']!=PARENT or KEY in manifest:
        raise ValueError('Exact unapplied parent required')
    counts=contract['parent_collection_counts']
    if set(collections)!=set(counts) or any(len(collections[n])!=v for n,v in counts.items()):raise ValueError('Complete parent counts differ')
    if COLLECTION in collections:raise ValueError('Profile collection already exists')
    for owner,prior in contract['prior_owners'].items():
        for name in ['objects','entities']:
            if [r for r in collections[name] if r.get('id')==owner]!=prior[name]:raise ValueError('Owner identity changed')
        for name in ['widths','length_assessments','reference_routes']:
            if [r for r in collections[name] if owns(r,owner)]!=prior[name]:raise ValueError('Prior dimensional support changed')
    for row in contract['prior_source_inventory']+[contract['prior_publication']]:
        if [r for r in collections['sources'] if r.get('id')==row['id']]!=[row]:raise ValueError('Prior publication changed')
    if [r for r in collections['route_decisions'] if r.get('id')==contract['prior_decision']['id']]!=[contract['prior_decision']]:raise ValueError('Prior decision changed')
    additions=contract['routes']+contract['records']+contract['new_sources'];ids={r['id'] for r in additions}
    if len(ids)!=29 or any(r.get('id') in ids for rows in collections.values() for r in rows):raise ValueError('New ID collision')
    pins={**contract['input_sha256'],FILE:contract_sha256}
    if any(p in manifest.get('input_sha256',{}) and manifest['input_sha256'][p]!=v for p,v in pins.items()):raise ValueError('Historical source pin would change')
    after=dict(collections);after['reference_routes']=[*collections['reference_routes'],*copy.deepcopy(contract['routes'])]
    after['sources']=[*collections['sources'],*copy.deepcopy(contract['new_sources'])];after[COLLECTION]=copy.deepcopy(contract['records'])
    after['objects']=[copy.deepcopy(contract['final_objects'].get(r['id'],r)) for r in collections['objects']]
    after['route_decisions']=[copy.deepcopy(contract['final_decision']) if r['id']==contract['prior_decision']['id'] else r for r in collections['route_decisions']]
    updated=copy.deepcopy(manifest);updated['input_sha256']={**manifest.get('input_sha256',{}),**pins};updated[KEY]=marker(contract,contract_sha256)
    return after,updated

def prepare(collections,manifest,contract,*,parent_logical_sha256):
    raw=encoded(build_contract())
    if encoded(contract)!=raw or (ROOT/FILE).read_bytes()!=raw:
        raise ValueError('Exact frozen source contract required')
    return apply_verified(collections,manifest,contract,parent_logical_sha256=parent_logical_sha256,
        contract_sha256=hashlib.sha256(raw).hexdigest())

if __name__=='__main__':
    path=ROOT/FILE
    if path.exists():raise ValueError('Use a new contract version')
    path.write_bytes(encoded(build_contract()));print('Frozen two NEC references,24 source profiles,three sources and two owner projections.')
