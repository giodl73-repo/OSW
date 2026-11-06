"""Prepare five basin-qualified identities without borrowing family measurements."""
import copy
import hashlib
import json
from pathlib import Path
import unicodedata
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
FACTS='research/equatorial-basin-identity-source-review-v1.json'
FACTS_SHA='a1311e765758ade450cc4f244131832c554c0d84c8196762a501d25bf87def8d'
AUDIT='research/equatorial-basin-parent-run-v1/selected-records.json'
RESULT='research/equatorial-basin-parent-run-v1/result.json'
FILE='research/equatorial-basin-identity-query-contract-v1.json'
PROTOCOL='plans/equatorial-basin-identity-contract-v1.md'
FIGURE='figures/equatorial-basin-identity-members-v1.svg'
SOURCE='source:4556886a82d6f61a'
KEY='equatorial_basin_identities_v1'
PARENT='bef41b14f78c84a9b7b2d135dd900d67504618bfadaec4b3397be6982ae33ae8'
EXPECTED=('atlantic-north-equatorial','pacific-north-equatorial','atlantic-south-equatorial',
          'pacific-south-equatorial','indian-south-equatorial')
BRANCH_SOURCES={'pacific-north-equatorial':'research/pacific-nec-monthly-bifurcation-extraction.json',
                'indian-south-equatorial':'research/indian-sec-monthly-bifurcation-extraction.json'}
CAPABILITIES=('dated_diagnostics','flow_network','geometry','observed_velocity','passage_transport',
 'radius_evidence','reference_route','reported_length','scope_notes','scoped_width','source_connectivity','time_samples','width_samples')

def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def fingerprint(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def normalized(value):return ' '.join(unicodedata.normalize('NFKC',str(value)).casefold().split())
def query_url(collection,field,value):
    request={'collection':collection,'filters':[{'field':field,'op':'eq','value':value}],'limit':100}
    return 'query.html?q='+quote(json.dumps(request,separators=(',',':')),safe='')

def build_contract():
    facts=read(FACTS);audit=read(AUDIT);result=read(RESULT)
    if (sha(FACTS)!=FACTS_SHA or sha(AUDIT)!='f776c9c13782ac8a0f4ec2564c5b1bd4e83dbfba736fba8b7c2f58fc00f0a03c'
        or result['logical_sha256']!=PARENT or result['identity_resolution_counts']!={'MISSING_EXACT_IDENTITY':5}
        or tuple(p['proposed_id'] for p in facts['proposals'])!=EXPECTED
        or facts['proposals']!=[audit['proposals'][p]['proposal'] for p in EXPECTED]):
        raise ValueError('Frozen five-member installed audit differs')
    paths={FACTS,AUDIT,RESULT,PROTOCOL,FIGURE,'analysis/equatorial_basin_identity_query_v1.py',
        'plans/current-identity-admission-protocol-v1.md','research/equatorial-basin-parent-execution-review-v1.json',
        'research/equatorial-basin-family-inventory-audit.json'}
    paths.update(BRANCH_SOURCES.values())
    for current,path in BRANCH_SOURCES.items():
        branch=read(path)
        if (branch['proposed_current_id']!=current or branch['metric']!='regional_bifurcation_latitude'
            or any(branch[key] is not None for key in ['geometry','whole_current_length_km','current_width_km','annual_dimension_range_km'])
            or branch['rank_eligible'] is not False or branch['geographic_playback_eligible'] is not False):
            raise ValueError('Existing branching chart scope differs')
    additions={key:[] for key in ['entities','names','length_assessments','current_identity_admissions','objects','route_decisions','current_basin_memberships']}
    source=next(r for r in audit['existing_glossary_sources'] if r['id']==SOURCE)
    for proposal in facts['proposals']:
        short=proposal['proposed_id'];ident='current:'+short;family='current:'+proposal['parent_current_id']
        admission='current_admission:'+short;membership='basin_membership:'+short;route='route-decision:'+short
        scope=(proposal['basin']+' westward '+proposal['source_term']+' under the NOAA glossary basin convention. '
            'The qualified label is editorial. Dimensions, layer bounds, current axis and annual envelopes require separate evidence. '
            'This is distinct from the existing cross-basin family, countercurrents, undercurrents and regional branches.')
        entity={'id':ident,'label':proposal['proposed_label'],'type':'named_current','basin':proposal['basin'],
            'setting':'equatorial','time_behavior':'persistent_variable','vertical_setting':'unspecified','identity_level':'current',
            'source_id':SOURCE,'source_record_id':short,'source_kind':'primary_glossary_basin_qualified_identity',
            'source_locator':proposal['source_locator'],'identity_scope_note':scope,'identity_admission_id':admission,
            'catalogue_version':'0.2.0-draft-equatorial-basins','almanac_url':'object.html?id='+quote(ident,safe='')}
        additions['entities'].append(entity)
        additions['names'].append({'id':'name:'+ident+':preferred','entity_id':ident,'label':entity['label'],
            'preferred':True,'name_role':'preferred','source_id':SOURCE,'label_qualification':'OSW basin qualifier of NOAA shared current term'})
        additions['length_assessments'].append({'id':'length_assessment:'+short,'entity_id':ident,'source_id':SOURCE,
            'source_locator':proposal['source_locator'],'evidence_status':'identity_only_dimensions_not_admitted',
            'rank_eligible':False,'published_length_km':None,'published_rank':None,'lower_bound_km':None,
            'proposed_system_length_km':None,'scope':'Basin-specific identity; no length, width, axis or annual envelope admitted.'})
        decision={'id':route,'entity_id':ident,'current_id':short,'label':entity['label'],
            'strategy_id':'source_supported_basin_axis_and_endpoints','strategy_label':'Resolve basin-specific axis and endpoints',
            'construction_status':'not_constructed_source_axis_and_endpoints_unresolved','candidate_count':0,'route_ids':[],
            'next_action':'Review basin-specific alongflow continuity, layer and endpoints before an editorial route or physical length.',
            'scope':scope,'status':'identity_admitted_route_unresolved','rank_eligible':False,'source_id':SOURCE,
            'source_url':source['url'],'source_catalog_file':FILE,'scope_reviews':[]}
        additions['route_decisions'].append(decision)
        member={'id':membership,'entity_id':ident,'current_id':short,'family_entity_id':family,
            'relation':'editorial_basin_member','source_term':proposal['source_term'],'basin':proposal['basin'],
            'source_id':SOURCE,'source_locator':proposal['source_locator'],'source_review_file':FACTS,
            'label_qualification':'OSW basin qualifier; NOAA uses a shared heading',
            'membership_is_physical_connection':False,'measurements_inherited':False,'geometry':None,'figure':FIGURE}
        additions['current_basin_memberships'].append(member)
        additions['current_identity_admissions'].append({'id':admission,'entity_id':ident,'proposal_id':short,
            'entity':copy.deepcopy(entity),'route_planning_decision':copy.deepcopy(decision),
            'status':'editorial_identity_admitted_measurements_separately_gated','source_id':SOURCE,'source_ids':[SOURCE],
            'source_review_file':FACTS,'source_review_sha256':sha(FACTS),'source_locator':proposal['source_locator'],
            'family_membership_id':membership,'distinguished_from':[family,'countercurrents','undercurrents','regional branches'],
            'canonical_measurements_admitted':False,'external_scientific_review_claimed':False,
            'rank_eligible':False,'physical_edges_admitted':False,'seasonal_playback_eligible':False,
            'geometry':None,'annual_width_range_km':None,'annual_length_range_km':None})
        owner={key:copy.deepcopy(entity[key]) for key in ['id','label','type','basin','setting','time_behavior','identity_level','source_kind','vertical_setting','identity_scope_note']}
        owner.update(source_ids=[SOURCE],linked_source_count=1,capabilities={key:0 for key in CAPABILITIES},
            dashboard_search=entity['label']+' '+entity['basin'],search_aliases=[],object_url=entity['almanac_url'],route_url=None,
            season_url='seasons.html?current='+quote(short,safe=''),published_length_km=None,latest_observation_date=None,
            recorded_claims=0,nasa_links=0,claim_review_counts={},
            evidence_links=[{'label':'Inspect basin-specific identity','url':query_url('current_identity_admissions','id',admission)},
                {'label':'Inspect family relationship','url':query_url('current_basin_memberships','id',membership)},
                {'label':'Open current family','url':'object.html?id='+quote(family,safe='')},
                {'label':'Read naming source','url':query_url('sources','id',SOURCE)},
                {'label':'Inspect route worklist','url':query_url('route_decisions','id',route)},
                {'label':'Basin identity diagram','url':'../'+FIGURE}])
        for key in ['connections','current_section_ids','diagnostic_ids','map_features','measurement_ids','route_ids','scope_notes',
                'series','state_codes','state_evidence','velocity_sample_ids','width_ids','width_sample_ids']:
            owner[key]=[]
        owner['route_decision_ids']=[route]
        if short in ['pacific-north-equatorial','indian-south-equatorial']:
            owner['evidence_links'].append({'label':'Existing regional bifurcation chart (not current dimensions)',
                'url':'index.html?branch-current='+short+'#branching-title'})
        groups={'identity':entity,'sources':[source],'claims':[],'measurements':[[],[],None],
            'routes_geometry':[[],[],[],[]],'media':[],'time_evidence':[[],None,None,None]}
        owner['section_fingerprints']={key:fingerprint(value) for key,value in groups.items()}
        owner['fingerprint']=fingerprint(owner);additions['objects'].append(owner)
    counts=copy.deepcopy(result['collection_counts'])
    after={**counts,**{key:counts.get(key,0)+len(rows) for key,rows in additions.items()}}
    return {'schema':'osw.equatorial-basin-identity.query-contract.v1','status':'PREPARED_ADDITIVE_WORKING_IDENTITIES_NOT_INSTALLED',
        'parent_logical_sha256':PARENT,'input_sha256':{p:sha(p) for p in sorted(paths)},
        'expected_entity_ids':['current:'+v for v in EXPECTED],'reused_source_id':SOURCE,
        'prior_family_records':audit['families'],'prior_glossary_sources':audit['existing_glossary_sources'],
        'prior_collection_counts':counts,'after_collection_counts':after,'additions':additions,
        'accepted_current_identities_before':106,'accepted_current_identities_after':111,
        'new_publication_sources':0,'new_measurements':0,'new_geometry':0,'installed':False,'full_goal_complete':False}

def prepare(collections,manifest,contract,*,parent_logical_sha256):
    if parent_logical_sha256!=PARENT:raise ValueError('Exact installed logical parent required')
    if encoded(contract)!=(ROOT/FILE).read_bytes() or contract!=build_contract():raise ValueError('Frozen unmodified contract required')
    if KEY in manifest or 'current_basin_memberships' in collections:raise ValueError('Repeated or conflicting membership extension')
    if {k:len(v) for k,v in collections.items()}!=contract['prior_collection_counts']:raise ValueError('Installed collection inventory differs')
    for name,rows in collections.items():
        ids=[r.get('id') for r in rows]
        if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):raise ValueError('Unique IDs required: '+name)
    ids=set(contract['expected_entity_ids']);labels={normalized(r['label']) for r in contract['additions']['entities']}
    for name in ['entities','objects','names']:
        if any(r['id'] in ids or r.get('entity_id') in ids or normalized(r.get('label','')) in labels for r in collections[name]):
            raise ValueError('Existing identity, qualified alias or partial record: '+name)
    for ident,prior in contract['prior_family_records'].items():
        for name in ['entities','objects']:
            if [r for r in collections[name] if r['id']==ident]!=prior[name]:raise ValueError('Audited family differs: '+ident)
        if [r for r in collections['names'] if r.get('entity_id')==ident]!=prior['names']:raise ValueError('Family aliases differ')
    for row in contract['prior_glossary_sources']:
        if [r for r in collections['sources'] if r['id']==row['id']]!=[row]:raise ValueError('Historical glossary source differs')
    inputs=manifest.get('input_sha256',{})
    pins={**contract['input_sha256'],FILE:sha(FILE)}
    if any(p in inputs and inputs[p]!=pin for p,pin in pins.items()):raise ValueError('Historical input rebinding refused')
    result={key:list(rows) for key,rows in collections.items()}
    for name,rows in contract['additions'].items():
        existing={r['id'] for r in result.get(name,[])}
        if any(r['id'] in existing for r in rows):raise ValueError('Admission row ID collision: '+name)
        result[name]=result.get(name,[])+copy.deepcopy(rows)
    final=copy.deepcopy(manifest);final.setdefault('input_sha256',{}).update(pins)
    final[KEY]={'contract_file':FILE,'contract_sha256':sha(FILE),'parent_logical_sha256':PARENT,
        'new_identity_ids':contract['expected_entity_ids'],'accepted_current_identities':111,
        'new_measurements':0,'new_publication_sources':0,'physical_geometry_added':False}
    collections.clear();collections.update(result);manifest.clear();manifest.update(final)
