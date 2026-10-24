"""Source-reported dimensions admitted separately from accepted current identities."""
from pathlib import Path
import hashlib,json
import current_identity_admissions as identity
from build_ocean_motion_claims import review_fingerprint

ROOT=Path(__file__).resolve().parents[1]
PATH='research/southern-east-madagascar-prose-dimension-admissions.json'
PROTOCOL='plans/published-prose-dimension-admission-protocol-v1.md'
OPERATOR='analysis/current_measurement_admissions.py'
FIGURE='figures/southern-east-madagascar-admitted-dimensions.svg'
EXPORT='research/ocean-current-working-measurements.json'
ENTITY=identity.ENTITY
WIDTH_ID='southern-east-madagascar-nauw2008-near-surface-survey-width'
MEASUREMENT_ID='measurement:southern-east-madagascar:reported-extent'
CLAIM_ID='claim:'+MEASUREMENT_ID

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def build():
    admission=identity.verify()['entries'][0]
    source=admission['source'];dimensions=admission['source_dimensions']['records']
    length,width=dimensions
    if (length['dimension'],length['value_km'],width['dimension'],width['value_km'],width['observed_period'])!=('length',650,'width',120,'2001-04'):
        raise ValueError('Changed Nauw prose source reports')
    base=identity.read(identity.BASE+'measurements.json')
    rank=1+sum(r['rank_eligible'] and r['value']>650 for r in base)
    if rank!=12:raise ValueError('Renew reported-length ranking admission')
    scope='Author-reported approximate southern branch extent from about 20°S to Cap Sainte Marie near 25°30′S. Contextual literature estimate citing Duncan (1970) and Lutjeharms (1988b), not a new April 2001 path measurement. Coordinates, reference axis, fixed layer, reference period and error unspecified.'
    measurement={'id':MEASUREMENT_ID,'claim_id':CLAIM_ID,'entity_id':ENTITY,'quantity':'reported_length',
        'value':650,'unit':'km','approximate':True,'evidence_status':'published_estimate','rank_eligible':True,
        'source_id':source['id'],'source_locator':'Introduction paragraph2','scope':scope,
        'geometry_id':None,'observation_time':None,'uncertainty_km':None,'historical_release_admitted':False}
    measurement.update(reference_period=None,fixed_layer_bounds_m=None,endpoint_coordinates_lon_lat=None,
        source_report_type='contextual_literature_estimate_not_new_cruise_path_measurement')
    claim={'id':CLAIM_ID,'subject_id':ENTITY,'object_id':None,'predicate':'reported_length',
        'value':650,'unit':'km','target_collection':'measurements','target_id':MEASUREMENT_ID,
        'source_id':source['id'],'source_locator':'Introduction paragraph2','source_locator_status':'publisher_full_text_prose',
        'evidence_class':'published_estimate','assertion_status':'source_reported_approximate_extent',
        'scope':scope,'observation_time':None,'review_status':'not_individually_reviewed','reviewer':None,
        'review_date':None,'review_note':'Internal editorial passage review supports the reported number and branch scope; external scientific review remains pending.',
        'method':'Linked factual extraction from original publisher HTML; no geodesic calculation or figure digitization.'}
    claim.update(assertion_status='reported_or_derived_measurement',source_locator_status='specific',
        method_source_id=source['id'],method_status='described',source_date='2008-08-05',
        source_snapshot_id=None,support_claim_id=None)
    claim['review_fingerprint']=review_fingerprint(claim)
    source_record=dict(source)
    source_record['used_in_collections']=list(dict.fromkeys(source['used_in_collections']+['measurements','claims','widths','current_measurement_admissions']))
    source_record['rights_policy_url']=PROTOCOL
    source_record['metadata_note']='Original publisher prose supports a contextual branch extent and one near-surface survey-width summary. No original publication or source figure redistributed; original-file checksum and source-figure review remain unavailable.'
    width_row={'id':WIDTH_ID,'current_id':identity.ID,'name':admission['entity']['label'],
        'status':'editorial_source_extraction_not_historical_release','measurement_type':'published_regional_summary',
        'width_metric':'author_reported_near_surface_survey_width','approximate_width_km':120,'width_range_km':None,
        'range_interpretation':'One approximate survey summary, not a variability range, confidence interval or four independent widths.',
        'geographic_scope':'Sections T5–T8 off southeast Madagascar. No section endpoints or paired current-edge coordinates extracted.',
        'vertical_scope':'Near surface. Upper 100 m VMADCP mean velocity is method context, not a verified fixed width layer.',
        'layer':'Near surface; velocity averaging over the upper 100 m is context, not a verified width layer.','fixed_layer_bounds_m':None,'boundary_rule':'Author prose current width; numerical width-edge cutoff and coordinates unspecified. Transport-integration zero contours and 5°C isotherm not transferred.',
        'boundary_sides':'author_reported_width_edges_not_supplied','source_url':source['url'],
        'source_citation':source['preferred_citation'],'source_locator':'Results3.1 paragraph17; abstract',
        'source_access':'Original publisher full HTML inspected 2026-10-21; no original PDF checksum or figure digitization claimed.',
        'extraction_method':'Direct factual prose extraction. No interpolation, speed-threshold selection or figure measurement.',
        'source_precision':'of order 120 km','uncertainty_km':None,'observed_period':'2001-04','time_precision':'month',
        'calendar_months':None,'phase_label':'April 2001 T5–T8 near-surface survey summary',
        'phase_kind':'published_near_surface_survey_summary','time_convention':'One April 2001 survey; not April climatology.',
        'whole_current_representative':False,'width_rank_eligible':False,'full_width_inference_eligible':False,
        'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'is_confidence_interval':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'geographic_current_edges':None,
        'source_quality_note':'Unspecified width boundaries and error. Velocity averaging, core-to-coast distance, transport integration and eddy-enhanced transport are distinct quantities.',
        'source_report_file':PATH,'velocity_averaging_layer_m':[0,100],
        'velocity_averaging_layer_is_verified_width_layer':False,'source_statements_count':1,
        'survey_sections':['T5','T6','T7','T8'],'independent_width_samples_admitted':False,
        'physical_current_envelope_admitted':False,'historical_release_admitted':False}
    width_row.update(is_annual_mean=False,is_climatology=False)
    assessment=identity.additions()['length_assessments'][0]
    assessment.update(evidence_status='published_estimate',rank_eligible=True,published_length_km=650,published_rank=rank,
        scope=scope,measurement_id=MEASUREMENT_ID,measurement_admission_file=PATH)
    planning=dict(admission['route_planning_decision'])
    planning.update(existing_length_evidence_status='published_estimate',published_length_rank_eligible=True,
        existing_scope='Reported approximate 650 km southern branch extent admitted; no source-supported route geometry recovered.',
        planning_basis='Published length and geographic route are separate evidence. A prose extent does not construct an axis.')
    inputs={p:digest(p) for p in [PROTOCOL,OPERATOR,identity.PATH,identity.PROPOSALS,identity.BASE+'measurements.json',
        identity.BASE+'length_assessments.json','research/ocean-current-width-inventory.json',FIGURE,'analysis/build_ocean_motion_claims.py']}
    return {'schema':'osw.published-prose-dimension-admissions.v1','version':'0.2.0-draft-prose-1',
        'current_id':identity.ID,'entity_id':ENTITY,'source_url':source['url'],'source_citation':source['preferred_citation'],
        'status':'source_reported_extent_and_scoped_survey_width_admitted','input_sha256':inputs,
        'source_access':'Original publisher full HTML inspected 2026-10-21; original PDF unavailable.',
        'original_source_file_sha256':None,'source_figures_digitized':False,'source_figures_reviewed':False,
        'source_use':'Linked original factual paraphrases and OSW diagram; no publication or provider figures redistributed.',
        'measurement':measurement,'claim':claim,'source_record':source_record,'width_record':width_row,'length_assessment':assessment,
        'route_planning_decision':planning,'figure_file':FIGURE,'working_ranked_length_count':12,
        'physical_edges_admitted':False,'annual_extrema_admitted':False,'external_scientific_review_claimed':False}

def verify():
    expected=build()
    if (ROOT/PATH).read_bytes()!=encoded(expected):raise ValueError('Stale prose dimension admission')
    return expected

def verify_inputs():
    doc=verify()
    if (ROOT/EXPORT).read_bytes()!=encoded(working_export(doc)):raise ValueError('Stale working measurement export')
    return doc,{**doc['input_sha256'],PATH:digest(PATH),EXPORT:digest(EXPORT)}

def working_export(doc=None):
    doc=verify() if doc is None else doc
    assessments=identity.read(identity.BASE+'length_assessments.json')+[doc['length_assessment']]
    return {'schema':'osw.working-current-measurements.v1','version':doc['version'],
        'base_release':'0.1.0','working_catalogue_file':identity.CATALOGUE,'admission_file':PATH,
        'scope':'Qualified source-reported dimensions and scoped widths; not a uniform physical current inventory or annual envelope.',
        'input_sha256':{PATH:digest(PATH),OPERATOR:digest(OPERATOR),identity.BASE+'sources.json':digest(identity.BASE+'sources.json')},
        'ranked_length_count':12,'scoped_width_count':157,'scoped_width_owners':83,
        'measurements':identity.read(identity.BASE+'measurements.json')+[doc['measurement']],
        'length_assessments':assessments,
        'widths':identity.read('research/ocean-current-width-inventory.json')['measurements']+[doc['width_record']],
        'sources':identity.read(identity.BASE+'sources.json')+[doc['source_record']]}

def append(collections,doc=None):
    doc=verify() if doc is None else doc
    for name,key in [('measurements','measurement'),('claims','claim'),('widths','width_record')]:
        row=doc[key];rows=collections.setdefault(name,[])
        if any(r['id']==row['id'] for r in rows):raise ValueError('Duplicate prose dimension admission')
        rows.append(row)
    matches=[i for i,r in enumerate(collections['length_assessments']) if r['entity_id']==ENTITY]
    if len(matches)!=1:raise ValueError('Missing admitted-current length assessment')
    collections['length_assessments'][matches[0]]=doc['length_assessment']
    source=doc['source_record'];matches=[i for i,r in enumerate(collections['sources']) if r['id']==source['id']]
    if len(matches)!=1:raise ValueError('Missing prose dimension source record')
    collections['sources'][matches[0]]=source
    collections['current_measurement_admissions']=[{'id':'current_measurement_admission:'+identity.ID,**doc}]

if __name__=='__main__':
    doc=build();(ROOT/PATH).write_bytes(encoded(doc))
    (ROOT/EXPORT).write_bytes(encoded(working_export(doc)))
    print(json.dumps({'ranked_reported_length_km':650,'rank':12,'scoped_survey_width_km':120,'physical_annual_ranges_admitted':False}))
