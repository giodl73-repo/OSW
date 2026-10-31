"""Exact one-row review-cited width append; installed artifacts are cloud callers only."""
import copy
import hashlib
import json
import re
from pathlib import Path
from build_wicc_review_width_v1 import validate

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/wicc-vinayachandran-2021-surface-width-source-facts-v1.json'
FIGURE='figures/wicc-vinayachandran-2021-surface-width-v1.svg'
OWNER='current:west-india-coastal'
ID='wicc-vinayachandran-2021-review-surface-width'
KEY='published_wicc_review_width_v1'
PARENT='b7884cb7b9febf250c73d2402754f2794598d472b7687f45b9a57555691ab017'
DASHBOARD='research/ocean-motion-dashboard.json'

def document():
    raw=(ROOT/SOURCE).read_bytes();doc=json.loads(raw);validate(doc)
    return doc,hashlib.sha256(raw).hexdigest()

def record():
    doc,pin=document();row=copy.deepcopy(doc['records'][0])
    row.update(name='West India Coastal Current',status='editorial_review_cited_width_not_independent_measurement',
        measurement_type='published_review_cited_surface_width',width_metric='review_cited_regional_surface_width',
        width_metric_label='Review-cited surface current width',approximate_width_km=150,width_range_km=None,
        range_interpretation='One approximate review-cited estimate; no seasonal or uncertainty interval.',
        time_convention=row['time_description'],layer=row['layer_description'],section_geometry=None,
        width_sampling_depth_m=None,boundary_sides='source_described_coast_to_current_extent_no_georeferenced_edges',
        source_file=SOURCE,source_file_sha256=pin,source_pointer='/records/0',source_url=doc['source']['url'],
        source_citation='Vinayachandran et al. (2021), doi:10.5194/bg-18-5967-2021, section2.7.1, p.5991',
        source_evidence_kind='published_review_citing_prior_ship_observations',
        extraction_method='Transcribed explicit width description in the original review; no new observation or reconstruction of the cited1990 methods.',
        phase_label='About 150 km / review-cited surface width',phase_kind='review_cited_surface_width',
        full_width_inference_eligible=False,is_confidence_interval=False,
        review_width_context={'source':doc['source'],'underlying_cited_work':doc['underlying_cited_work'],
            'excluded_inferences':doc['excluded_inferences'],'observational_independence_note':doc['observational_independence_note'],'full_context_figure':FIGURE})
    return row

def phase_plan():
    return {'current_id':'west-india-coastal','phases':[{'id':ID,'width_id':ID,'frame_id':None,'direction_id':None,'label':record()['phase_label'],'playback_step_eligible':False}],
        'can_play':False,'eligible_indices':[],
        'range_note':'One approximate review-cited surface width. Exact sampling dates, numerical width depth, uncertainty and annual ranges are unreported; the cited original methods remain unverified.',
        'playback_scope':'Static review-cited evidence; no comparable recorded seasonal sequence.'}

def changed_fingerprint(prior,group):
    if not isinstance(prior,str) or not re.fullmatch('[0-9a-f]{64}',prior):raise ValueError('Prior fingerprint required')
    _,pin=document()
    return hashlib.sha256(('osw.wicc-review-width.v1\n'+group+'\n'+prior+'\n'+pin+'\n'+ID+'\n').encode()).hexdigest()

def dashboard_row(original,prior_fingerprint,prior_measurements_fingerprint):
    row=copy.deepcopy(original)
    if row['id']!=OWNER:return row
    if row['capabilities']['scoped_width']!=0 or row['fingerprint']!=prior_fingerprint or row['section_fingerprints']['measurements']!=prior_measurements_fingerprint:raise ValueError('Historical WICC dashboard differs')
    if 'width_ids' in row:
        if row['width_ids']!=[]:raise ValueError('Historical WICC width join differs')
        row['width_ids']=[ID]
    row['capabilities']['scoped_width']=1;row['fingerprint']=changed_fingerprint(prior_fingerprint,'object')
    row['section_fingerprints']['measurements']=changed_fingerprint(prior_measurements_fingerprint,'measurements')
    return row

def dashboard_document(original,source_dashboard_sha256):
    result=copy.deepcopy(original);owners=[r for r in original['entries'] if r['id']==OWNER]
    if len(owners)!=1:raise ValueError('One historical WICC dashboard row required')
    prior=owners[0]
    result['entries']=[dashboard_row(r,prior['fingerprint'],prior['section_fingerprints']['measurements']) for r in original['entries']]
    result['snapshot_fingerprint']=changed_fingerprint(original['snapshot_fingerprint'],'snapshot')
    _,pin=document();result['published_wicc_review_width_projection_v1']={'source_file':SOURCE,'source_file_sha256':pin,'source_dashboard_sha256':source_dashboard_sha256,'scope':'One review-cited surface width; no independent sample, geometry or annual range.'}
    return result

def prepare(bundle,*,logical_parent_sha256):
    if bundle.get('schema')!='osw.query-bundle.v1' or logical_parent_sha256!=PARENT:raise ValueError('Exact installed logical parent required')
    if KEY in bundle['manifest'] or SOURCE in bundle['manifest'].get('input_sha256',{}):raise ValueError('Review width already present')
    widths=bundle['collections']['widths'];owners=[r for r in bundle['collections']['objects'] if r['id']==OWNER]
    if len(widths)!=174 or any(r.get('current_id')=='west-india-coastal' or r['id']==ID or 'review_width_context' in r for r in widths):raise ValueError('Exact174 preceding widths without WICC required')
    if len(owners)!=1 or owners[0]['width_ids']!=[] or owners[0]['capabilities']['scoped_width']!=0:raise ValueError('Exact unmeasured WICC join required')
    owner=owners[0];receipt=bundle['manifest']['dashboard_receipt'];raw=receipt['source_json'].encode()
    if receipt['source_file']!=DASHBOARD or receipt['source_sha256']!=hashlib.sha256(raw).hexdigest() or bundle['manifest']['input_sha256'][DASHBOARD]!=receipt['source_sha256']:raise ValueError('Historical dashboard custody differs')
    source_rows=[r for r in json.loads(raw)['entries'] if r['id']==OWNER]
    if len(source_rows)!=1:raise ValueError('Historical WICC source row missing')
    dashboard_row(source_rows[0],owner['fingerprint'],owner['section_fingerprints']['measurements'])
    result=copy.deepcopy(bundle);result['collections']['widths'].append(record())
    updated=next(r for r in result['collections']['objects'] if r['id']==OWNER)
    updated['width_ids']=[ID];updated['capabilities']['scoped_width']=1
    updated['fingerprint']=changed_fingerprint(owner['fingerprint'],'object')
    updated['section_fingerprints']['measurements']=changed_fingerprint(owner['section_fingerprints']['measurements'],'measurements')
    _,pin=document();result['manifest']['input_sha256'][SOURCE]=pin
    result['manifest'][KEY]={'logical_parent_sha256':PARENT,'source_file':SOURCE,'source_file_sha256':pin,
        'records_added':1,'prior_width_records':174,'prior_owner_width_ids':[],
        'prior_dashboard_fingerprint':owner['fingerprint'],'prior_measurements_fingerprint':owner['section_fingerprints']['measurements'],
        'width_samples_added':0,'length_records_added':0,'independent_observations_added':0,'geometry_added':False}
    return result
