"""Exact one-row review-cited width append; installed artifacts are cloud callers only."""
import copy
import hashlib
import json
import re
from pathlib import Path
from eacc_dekeyzer_width_constraint_v1 import validate

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json'
FIGURE='figures/eacc-dekeyzer-2012-cited-width-lower-bound-v2.svg'
OWNER='current:east-african-coastal'
ID='eacc-dekeyzer-2012-bell-cited-width-lower-bound'
KEY='published_eacc_cited_width_constraint_v1'
PARENT='360e775a1dbb49d5c7934cca1f288ab2f2f8cd71bfa8fd1368fb35b086f4e1e0'
DASHBOARD='research/ocean-motion-dashboard.json'

def document():
    raw=(ROOT/SOURCE).read_bytes();doc=json.loads(raw);validate(doc)
    return doc,hashlib.sha256(raw).hexdigest()

def record():
    doc,pin=document();row=copy.deepcopy(doc['records'][0])
    row.update(name='East African Coastal Current',status='editorial_cited_width_constraint_not_independent_measurement',
        measurement_type='published_thesis_cited_width_constraint',width_metric='review_cited_current_width_lower_bound',
        width_metric_label='Thesis-cited exclusive width lower bound',approximate_width_km=None,
        range_interpretation='Over160km is an exclusive lower bound, not a central width, finite interval or annual range.',
        time_convention=row['time_description'],layer=row['layer_description'],section_geometry=None,
        width_sampling_depth_m=None,boundary_sides='not_supplied_for_the_cited_width_constraint',
        source_file=SOURCE,source_file_sha256=pin,source_pointer='/records/0',
        source_url=doc['source']['primary_repository_record'],source_download_url=doc['source']['source_url']+'#page=74',
        source_citation='Dekeyzer (2012), thesis section7.2, printed p.56 / PDF p.74; cites Bell (1972).',
        source_evidence_kind='doctoral_thesis_citing_earlier_width_literature',
        extraction_method='Retain the original thesis prose lower bound; no reconstruction of the cited Bell methods.',
        phase_label='Over 160 km / cited width lower bound',phase_kind='review_cited_width_constraint',
        full_width_inference_eligible=False,is_confidence_interval=False,
        cited_width_constraint_context={'source':doc['source'],'passage':doc['passage'],
            'underlying_cited_work':doc['underlying_cited_work'],'excluded_inferences':doc['excluded_inferences'],
            'lineage_note':doc['lineage_note'],'full_context_figure':FIGURE})
    return row


def phase_plan(prior):
    if not isinstance(prior,dict) or prior.get('current_id')!='east-african-coastal' or not isinstance(prior.get('phases'),list) or not isinstance(prior.get('eligible_indices'),list) or type(prior.get('can_play')) is not bool:
        raise ValueError('Exact preceding EACC phase plan required')
    if any(p.get('id')==ID for p in prior['phases']):raise ValueError('Constraint phase already present')
    if any(type(i) is not int or i<0 or i>=len(prior['phases']) for i in prior['eligible_indices']):raise ValueError('Invalid prior playback support')
    result=copy.deepcopy(prior)
    result['phases'].append({'id':ID,'width_id':ID,'frame_id':None,'direction_id':None,
        'label':record()['phase_label'],'playback_step_eligible':False})
    return result


def changed_fingerprint(prior,group):
    if not isinstance(prior,str) or not re.fullmatch('[0-9a-f]{64}',prior):raise ValueError('Prior fingerprint required')
    _,pin=document()
    return hashlib.sha256(('osw.eacc-cited-width-constraint.v1\n'+group+'\n'+prior+'\n'+pin+'\n'+ID+'\n').encode()).hexdigest()

def dashboard_row(original,prior_fingerprint,prior_measurements_fingerprint):
    row=copy.deepcopy(original)
    if row['id']!=OWNER:return row
    if row['capabilities']['scoped_width']!=0 or row['fingerprint']!=prior_fingerprint or row['section_fingerprints']['measurements']!=prior_measurements_fingerprint:raise ValueError('Historical EACC dashboard differs')
    if 'width_ids' in row:
        if row['width_ids']!=[]:raise ValueError('Historical EACC width join differs')
        row['width_ids']=[ID]
    row['capabilities']['scoped_width']=1;row['fingerprint']=changed_fingerprint(prior_fingerprint,'object')
    row['section_fingerprints']['measurements']=changed_fingerprint(prior_measurements_fingerprint,'measurements')
    return row

def dashboard_document(original,source_dashboard_sha256):
    result=copy.deepcopy(original);owners=[r for r in original['entries'] if r['id']==OWNER]
    if len(owners)!=1:raise ValueError('One historical EACC dashboard row required')
    prior=owners[0]
    result['entries']=[dashboard_row(r,prior['fingerprint'],prior['section_fingerprints']['measurements']) for r in original['entries']]
    result['snapshot_fingerprint']=changed_fingerprint(original['snapshot_fingerprint'],'snapshot')
    _,pin=document();result['published_eacc_cited_width_constraint_projection_v1']={'source_file':SOURCE,'source_file_sha256':pin,'source_dashboard_sha256':source_dashboard_sha256,'scope':'One thesis-cited exclusive width lower bound; no independent sample, geometry or annual range.'}
    return result

def prepare(bundle,*,logical_parent_sha256):
    if bundle.get('schema')!='osw.query-bundle.v1' or logical_parent_sha256!=PARENT:raise ValueError('Exact installed logical parent required')
    if KEY in bundle['manifest'] or SOURCE in bundle['manifest'].get('input_sha256',{}):raise ValueError('Review width already present')
    widths=bundle['collections']['widths'];owners=[r for r in bundle['collections']['objects'] if r['id']==OWNER]
    if len(widths)!=175 or any(r.get('current_id')=='east-african-coastal' or r['id']==ID or 'cited_width_constraint_context' in r for r in widths):raise ValueError('Exact175 preceding widths without EACC required')
    if len(owners)!=1 or owners[0]['width_ids']!=[] or owners[0]['capabilities']['scoped_width']!=0:raise ValueError('Exact unmeasured EACC join required')
    owner=owners[0];receipt=bundle['manifest']['dashboard_receipt'];raw=receipt['source_json'].encode()
    if receipt['source_file']!=DASHBOARD or receipt['source_sha256']!=hashlib.sha256(raw).hexdigest() or bundle['manifest']['input_sha256'][DASHBOARD]!=receipt['source_sha256']:raise ValueError('Historical dashboard custody differs')
    source_rows=[r for r in json.loads(raw)['entries'] if r['id']==OWNER]
    if len(source_rows)!=1:raise ValueError('Historical EACC source row missing')
    dashboard_row(source_rows[0],owner['fingerprint'],owner['section_fingerprints']['measurements'])
    result=copy.deepcopy(bundle);result['collections']['widths'].append(record())
    updated=next(r for r in result['collections']['objects'] if r['id']==OWNER)
    updated['width_ids']=[ID];updated['capabilities']['scoped_width']=1
    updated['fingerprint']=changed_fingerprint(owner['fingerprint'],'object')
    updated['section_fingerprints']['measurements']=changed_fingerprint(owner['section_fingerprints']['measurements'],'measurements')
    _,pin=document();result['manifest']['input_sha256'][SOURCE]=pin
    result['manifest'][KEY]={'logical_parent_sha256':PARENT,'source_file':SOURCE,'source_file_sha256':pin,
        'records_added':1,'prior_width_records':175,'prior_owner_width_ids':[],
        'prior_dashboard_fingerprint':owner['fingerprint'],'prior_measurements_fingerprint':owner['section_fingerprints']['measurements'],
        'width_samples_added':0,'length_records_added':0,'independent_observations_added':0,'geometry_added':False}
    return result
