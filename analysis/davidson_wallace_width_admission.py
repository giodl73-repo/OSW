"""Prepare scoped Davidson course-report evidence; no new physical reconstruction."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from build_ocean_motion_claims import review_fingerprint
from object_source_links import project

ROOT = Path(__file__).resolve().parents[1]
VERSION_KEY = 'davidson_reported_width_version'
VERSION = 'wallace-line67-v1'
FILE = 'research/davidson-wallace-2008-width-admission-v1.json'
ADAPTER = 'analysis/davidson_wallace_width_admission.py'
ENTITY = 'current:davidson'
WIDTH = 'davidson-wallace-2008-line67-27-59m-reported-span'
CLAIM = 'claim:width:' + WIDTH
ADMISSION = 'current_measurement_admission:davidson:wallace-2008-line67'
PAPER = 'source:wallace-davidson-2008-course-report'
METHOD = 'source:osw-davidson-wallace-reported-width-v1'
UNIT = 'source:nist-sp811-international-nautical-mile'
REPORT = 'research/davidson-wallace-2008-reported-width-v1.json'
FIGURE = 'figures/davidson-wallace-2008-reported-width-v1.svg'
PROOF = 'research/davidson-wallace-2008-source-replay-proof-v1.json'
PREFLIGHT = 'research/davidson-wallace-2008-reported-width-preflight-v1.json'
PROTOCOL = 'plans/davidson-wallace-reported-width-protocol-v1.md'
RELEASE_ENTITIES = 'almanac/release/v0.1.0/entities.json'
FROZEN_OUTPUTS = {
    REPORT: 'df69f0c4aad47903b51f3431cfa6760c7eefe035f4fc1d03af467433dd3b8bf2',
    FIGURE: '48ad6871e4839d9c21809ea2322eac7d8d7081fec2786c0f7877e3af3dc75d67',
}
PROOF_SHA = '1228787c8d30b4ec20a025cedca22c2e2a2f189eb58a10018587c89c339242a5'


def encoded(value):
    return (json.dumps(value,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def read(relative):
    path=(ROOT/relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('Missing or invalid admission dependency: '+relative)
    return path.read_bytes()


def pin(relative):
    return hashlib.sha256(read(relative)).hexdigest()


def query_url(collection,identity):
    query={'collection':collection,'filters':[{'field':'id','op':'eq','value':identity}],'limit':1}
    return 'query.html?q='+quote(json.dumps(query,separators=(',',':')),safe='')


def build_contract():
    for path,sha in FROZEN_OUTPUTS.items():
        if pin(path)!=sha:raise ValueError('Executed source output changed: '+path)
    if pin(PROOF)!=PROOF_SHA:raise ValueError('Executed source replay proof changed')
    report=json.loads(read(REPORT));proof=json.loads(read(PROOF));preflight=json.loads(read(PREFLIGHT))
    if (report['preflight_sha256']!=pin(PREFLIGHT)
            or proof['status']!='PASS_SOURCE_GENERATION_AND_EXACT_REPLAY_ONLY'
            or proof['outputs_sha256']!=FROZEN_OUTPUTS
            or proof['canonical_admission_verified'] is not False):
        raise ValueError('Unverified source-stage report or replay binding')
    for expected in preflight['dependencies'].values():
        raw=read(expected['path'])
        if len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:
            raise ValueError('Frozen source dependency changed')
    statement=report['reported_statements'][0]
    if (statement['source_value'],statement['source_unit_label'],statement['converted_width_km_decimal'],
            statement['depth_interval_m'],statement['exact_occupation_date'])!=(35,'NM','64.82',[27,59],None):
        raise ValueError('Unexpected source value or support')
    released=json.loads(read(RELEASE_ENTITIES))
    rows=released if isinstance(released,list) else released['entities']
    entities=[row for row in rows if row['id']==ENTITY]
    if len(entities)!=1 or entities[0]['type']!='named_current':raise ValueError('Accepted Davidson identity required')
    scope=('Source reports approximately 35 NM for a regional poleward-flow span along Line 67 off Monterey Bay, '
           'in the 27–59 m depth-averaged ADCP discussion. International-nautical-mile normalization is 64.82 km; '
           'display about 65 km. Campaign 23–30 January 2008, exact occupation date unknown. '
           'Course cruise report; peer review and publication date unverified. No paired edges, '
           'velocity cutoff, error, flow-normal orientation, whole-current width or annual range established.')
    sources=[
        {'id':PAPER,'kind':'report','label':'Wallace Davidson Current January 2008 course cruise report',
         'title':'In-situ Observations of the Davidson Current','author':'Ken Wallace',
         'url':report['source_url'],'publication_date':None,'publication_year':None,
         'source_locator':statement['source_locator'],'source_evidence_kind':'primary_course_cruise_report',
         'peer_review_verified':False,'original_sha256':report['source_sha256'],
         'original_file':'research/source-data/wallace-davidson-2008/journal-article.pdf',
         'original_bytes':678350,'original_pdf_pages':30,
         'license':'No redistribution permission inferred; original remains ignored.',
         'provider_asset_redistributed':False,'review_scope':'Selected PDF pages 1, 8, 9, 22, 23; not full scientific peer review.'},
        {'id':METHOD,'kind':'internal','label':'OSW Davidson reported regional transect width v1',
         'title':'Source extraction, exact unit normalization and scoped scalar display',
         'url':'../'+PROTOCOL,'path':PROTOCOL,'source_report_file':REPORT,
         'source_report_sha256':FROZEN_OUTPUTS[REPORT],'source_replay_proof':PROOF,
         'provider_asset_redistributed':False,'scientific_approval_inferred':False},
        {'id':UNIT,'kind':'unit_definition','label':'NIST SP811 international nautical mile',
         'title':'International nautical mile: 1852 metres',
         'url':report['prospective_unit_convention']['source_url'],
         'source_locator':'NIST SP 811 chapter 5, Table 9 nautical mile entry',
         'definition_exact_m':1852,'role':'Unit normalization, not an independent ocean observation',
         'provider_asset_redistributed':False},
    ]
    width={
        'id':WIDTH,'current_id':'davidson','entity_id':ENTITY,'name':'Davidson Current',
        'status':'working_editorial_source_evidence_not_historical_release',
        'measurement_type':'source_reported_regional_transect_summary',
        'width_metric':'author_reported_poleward_flow_transect_span',
        'approximate_width_km':65,'width_range_km':None,'source_precision':'about',
        'source_reported_value':35,'source_reported_unit':'nautical_mile','source_unit_label':'NM',
        'normalized_width_km_decimal':'64.82','conversion_factor_m_per_nautical_mile':1852,
        'display_rounding_rule':'nearest whole kilometer; original source approximation retained',
        'geographic_scope':statement['region'],'layer':'Depth-averaged 27–59 m ADCP lateral transect',
        'depth_average_interval_m':[27,59],'fixed_layer_bounds_m':None,
        'source_reported_depth_level_m':None,
        'section_orientation':'Coast-normal transect; flow-normal orientation not verified',
        'section_geometry':None,'transect_normal_to_flow_verified':False,
        'boundary_rule':'Author-reported lateral span; paired edges and numerical cutoff unspecified',
        'boundary_sides':'author_reported_span_edges_not_supplied',
        'source_id':PAPER,'method_source_id':METHOD,'source_ids':[UNIT],
        'source_url':report['source_url'],'source_citation':report['source_citation'],
        'source_locator':statement['source_locator'],'source_publication_year':None,
        'source_evidence_kind':'primary_course_cruise_report','peer_review_verified':False,
        'original_source_file_sha256':report['source_sha256'],
        'source_report_file':REPORT,'source_report_sha256':FROZEN_OUTPUTS[REPORT],
        'extraction_method':'Frozen prose extraction and unit normalization; no digitization or raw ADCP reprocessing',
        'claim_id':CLAIM,'width_admission_file':FILE,'width_admission_id':ADMISSION,
        'observation_window':['2008-01-23','2008-01-30'],
        'observed_period':'2008-01-23/2008-01-30','exact_occupation_date':None,
        'time_precision':'campaign_window_only_not_exact_width_occupation',
        'calendar_months':None,'phase_label':'January 2008 cruise, exact occupation unknown',
        'phase_kind':'reported_depth_averaged_campaign_summary',
        'time_convention':'Campaign bounds only; no exact width occupation, annual calendar or publication-date inference',
        'range_interpretation':'One approximate regional span; not variability or an uncertainty interval',
        'uncertainty_km':None,'numeric_velocity_cutoff':None,'geographic_current_edges':None,
        'whole_current_width_km':None,'annual_width_range_km':None,
        'whole_current_representative':False,'width_rank_eligible':False,
        'full_width_inference_eligible':False,'annual_extrema_eligible':False,
        'seasonal_playback_eligible':False,'geographic_width_bar_eligible':False,
        'is_confidence_interval':False,'is_annual_mean':False,'is_climatology':False,
        'source_statements_count':1,'independent_width_samples_admitted':False,
        'physical_current_envelope_admitted':False,'historical_release_admitted':False,
        'figure_file':FIGURE,'figure_sha256':FROZEN_OUTPUTS[FIGURE],
        'figure_scope_note':'One numerical marker, not a geographic width bar or annual envelope',
        'source_quality_note':scope,
    }
    claim={'id':CLAIM,'subject_id':ENTITY,'object_id':None,'predicate':'reported_width',
           'value':65,'unit':'km','approximate':True,'target_collection':'widths','target_id':WIDTH,
           'source_id':PAPER,'method_source_id':METHOD,'source_locator':statement['source_locator'],
           'source_locator_status':'specific','evidence_class':'primary_course_cruise_report_summary',
           'assertion_status':'reported_measurement_summary','scope':scope,
           'observation_time':None,'observation_window':width['observation_window'].copy(),
           'time_precision':width['time_precision'],'method':PROTOCOL,'method_status':'described',
           'source_date':None,'source_publication_year':None,'source_snapshot_id':None,
           'support_claim_id':None,'review_status':'not_individually_reviewed',
           'reviewer':None,'review_date':None,
           'review_note':'Repository method review is not scientific approval of the course-report width.'}
    claim['review_fingerprint']=review_fingerprint(claim)
    admission={'id':ADMISSION,'entity_id':ENTITY,'status':'scoped_source_report_admission',
               'width_id':WIDTH,'claim_id':CLAIM,'source_ids':[PAPER,METHOD,UNIT],
               'source_report_file':REPORT,'source_report_sha256':FROZEN_OUTPUTS[REPORT],
               'scope':scope,'raw_width_samples_added':0,'annual_ranges_added':0,
               'geographic_footprints_added':0,'new_identities_added':0,
               'existing_historical_width_replaced':False,'physical_playback_eligible':False,
               'historical_release_admitted':False,'scientific_peer_review_verified':False}
    paths={ADAPTER,'analysis/test_davidson_wallace_width_admission.py',REPORT,FIGURE,PROOF,PREFLIGHT,RELEASE_ENTITIES,'analysis/object_source_links.py',
           'analysis/build_ocean_motion_claims.py',*[entry['path'] for entry in preflight['dependencies'].values()]}
    return {'schema':'osw.davidson-reported-width-admission.v1','status':'prepared_working_admission_not_published',
            'manifest_fields':{VERSION_KEY:VERSION},
            'entity_id':ENTITY,'accepted_entity':entities[0],'source_records':sources,
            'width_record':width,'claim':claim,'admission':admission,
            'input_sha256':{path:pin(path) for path in sorted(paths)},
            'card_links':[
                {'label':'Compare the January 2008 reported transect span','url':'../'+FIGURE},
                {'label':'Query the January 2008 span: about 65 km','url':query_url('widths',WIDTH)},
                {'label':'Read the width admission and limitations','url':query_url('current_measurement_admissions',ADMISSION)},
            ],'canonical_delivery_verified':False}


def records(document):
    return [('sources',row) for row in document['source_records']]+[
        ('widths',document['width_record']),('claims',document['claim']),
        ('current_measurement_admissions',document['admission'])]


def prepare(collections,document):
    """Prepare an atomic append; no supplied object, list or record is mutated."""
    if encoded(document)!=read(FILE) or encoded(document)!=encoded(build_contract()):
        raise ValueError('Changed or unverified Davidson contract')
    required={'objects','entities','sources','claims','widths','measurements','geometries','media','reference_routes'}
    if required-set(collections):raise ValueError('Incomplete parent collections')
    if any(not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows) for rows in collections.values()):
        raise ValueError('Invalid collection shape')
    owners=[r for r in collections['objects'] if r.get('id')==ENTITY]
    entities=[r for r in collections['entities'] if r.get('id')==ENTITY]
    if len(owners)!=1 or entities!=[document['accepted_entity']] or owners[0].get('type')!='named_current':
        raise ValueError('Missing, duplicate or changed accepted Davidson identity')
    staged=dict(collections);added={}
    for name,row in records(document):
        current=staged.get(name,[])
        matches=[old for old in current if old.get('id')==row['id']]
        if name=='sources' and row['id']==UNIT and matches==[row]:continue
        if matches:raise ValueError('Admission collision in '+name)
        staged[name]=[*current,copy.deepcopy(row)];added[name]=added.get(name,0)+1
    registry=[r['id'] for r in staged['sources']]
    if len(registry)!=len(set(registry)):raise ValueError('Duplicate registered source identity')
    owner=copy.deepcopy(owners[0]);ids=owner.get('width_ids',[])
    if not isinstance(ids,list) or len(ids)!=len(set(ids)) or WIDTH in ids:
        raise ValueError('Invalid existing owner width references')
    old_owned_widths=[r for r in collections['widths'] if r.get('current_id')=='davidson']
    if set(ids)!={r['id'] for r in old_owned_widths}:raise ValueError('Incomplete parent width ownership')
    owner['width_ids']=[*ids,WIDTH];owner['capabilities']['scoped_width']=len(owner['width_ids'])
    owner['evidence_links'].extend(copy.deepcopy(document['card_links']))
    owned=[]
    for name,rows in staged.items():
        if name in {'objects','sources'}:continue
        owned.extend(row for row in rows if ENTITY in [row.get(k) for k in ('id','entity_id','subject_id','object_id')]
                     or row.get('current_id')=='davidson')
    owner=project(owner,registry,owned)
    claims=[r for r in staged['claims'] if ENTITY in (r.get('subject_id'),r.get('object_id'))]
    owner['recorded_claims']=len(claims);owner['claim_review_counts']={}
    for row in claims:
        status=row.get('review_status') or 'unspecified'
        if not isinstance(status,str):raise ValueError('Invalid claim review status')
        owner['claim_review_counts'][status]=owner['claim_review_counts'].get(status,0)+1
    groups=owner['section_fingerprints']
    groups['claims']=fingerprint(claims)
    groups['measurements']=fingerprint([[r for r in staged['measurements'] if r.get('entity_id')==ENTITY],
                                         [r for r in staged['widths'] if r.get('current_id')=='davidson'],None])
    groups['source_ownership']=fingerprint(owner['source_ids'])
    owner['fingerprint']=fingerprint({key:value for key,value in owner.items() if key!='fingerprint'})
    staged['objects']=[owner if row['id']==ENTITY else row for row in collections['objects']]
    return staged,{'status':'prepared_not_published','added_rows':added,
                   'prior_nonobject_rows_preserved':True,'other_owners_unchanged':True,
                   'raw_samples_added':0,'annual_ranges_added':0,'geometry_or_state_joins_added':0,
                   'canonical_delivery_verified':False,'complete_parent_packet_verified':False}


def prepare_candidate(manifest,collections,document):
    """Return collections and manifest together; fail without changing either input."""
    if not isinstance(manifest,dict) or not isinstance(manifest.get('input_sha256'),dict):
        raise ValueError('Complete parent input manifest required')
    if VERSION_KEY in manifest:
        raise ValueError('Davidson feature already declared; do not replay over a newer cohort')
    staged,receipt=prepare(collections,document)
    metadata=copy.deepcopy(manifest)
    for path,sha in {**document['input_sha256'],FILE:pin(FILE)}.items():
        previous=metadata['input_sha256'].get(path)
        if previous is not None and previous!=sha:
            raise ValueError('Changed parent dependency requires a separate reviewed transition: '+path)
        metadata['input_sha256'][path]=sha
    metadata.update(copy.deepcopy(document['manifest_fields']))
    return metadata,staged,receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','check'])
    action=parser.parse_args().action
    raw=encoded(build_contract())
    if action=='build':(ROOT/FILE).write_bytes(raw)
    elif read(FILE)!=raw:raise ValueError('Stale admission contract')
    print('PASS prepared Davidson scoped admission '+action+'; live packet unchanged')


if __name__=='__main__':main()
