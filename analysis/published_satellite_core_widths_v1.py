"""Pure source-bound width append; installed packet callers are cloud-only."""
import copy
import hashlib
import json
import re
from pathlib import Path
from build_agulhas_krug_2012_core_widths_v1 import validate

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/agulhas-krug-2012-core-widths-source-facts-v1.json'
FIGURE='figures/agulhas-krug-2012-core-widths-v1.svg'
KEY='published_satellite_core_widths_v1'
PARENT='c27c5c8319ab59fa6069274df1b7d19c87cf5a2aea8a7a04ba808a1636b9e212'
OWNER='current:agulhas'
OLD_IDS={'agulhas-act-eulerian-mean-section-width','agulhas-vinayachandran-2021-typical-core-description'}
DASHBOARD='research/ocean-motion-dashboard.json'


def changed_fingerprint(prior,group):
    if not isinstance(prior,str) or not re.fullmatch('[0-9a-f]{64}',prior):raise ValueError('Prior dashboard fingerprint required')
    _,pin=document();ids=[r['id'] for r in records()]
    return hashlib.sha256(('osw.satellite-core-widths.v1\n'+group+'\n'+prior+'\n'+pin+'\n'+'\n'.join(ids)+'\n').encode()).hexdigest()


def dashboard_row(original,prior_fingerprint,prior_measurements_fingerprint):
    row=copy.deepcopy(original)
    if row['id']!=OWNER:return row
    if row['capabilities']['scoped_width']!=2 or row['fingerprint']!=prior_fingerprint or row['section_fingerprints']['measurements']!=prior_measurements_fingerprint:raise ValueError('Historical Agulhas dashboard row differs')
    if 'width_ids' in row:
        if len(row['width_ids'])!=2 or set(row['width_ids'])!=OLD_IDS:raise ValueError('Historical dashboard width join differs')
        row['width_ids'].extend(r['id'] for r in records())
    row['capabilities']['scoped_width']=4
    row['fingerprint']=changed_fingerprint(prior_fingerprint,'object')
    row['section_fingerprints']['measurements']=changed_fingerprint(prior_measurements_fingerprint,'measurements')
    return row


def dashboard_document(original,source_dashboard_sha256):
    result=copy.deepcopy(original);owners=[r for r in result['entries'] if r['id']==OWNER]
    if len(owners)!=1:raise ValueError('One historical Agulhas dashboard row required')
    prior=owners[0]
    result['entries']=[dashboard_row(r,prior['fingerprint'],prior['section_fingerprints']['measurements']) for r in result['entries']]
    result['snapshot_fingerprint']=changed_fingerprint(original['snapshot_fingerprint'],'snapshot')
    _,pin=document()
    result['published_satellite_core_width_projection_v1']={'source_file':SOURCE,'source_file_sha256':pin,'source_dashboard_sha256':source_dashboard_sha256,'scope':'Two source-defined satellite mean widths; no geometry or annual ranges added.'}
    return result


def document():
    raw=(ROOT/SOURCE).read_bytes();doc=json.loads(raw);validate(doc)
    return doc,hashlib.sha256(raw).hexdigest()


def records():
    doc,pin=document();rows=[]
    for index,original in enumerate(doc['records']):
        row=copy.deepcopy(original)
        row.update(name='Agulhas Current',entity_id=OWNER,status='editorial_source_extraction_not_canonical',
            measurement_type='published_satellite_core_mean_width',width_metric='satellite_gaussian_core_mean' if index==0 else 'satellite_thermal_core_mean',
            width_metric_label=row['label'],approximate_width_km=row['reported_mean_width_km'],width_range_km=None,
            range_interpretation='Separate method-specific means; not seasonal limits, confidence intervals or width errors.',
            geographic_scope=doc['regional_support']['section'],section_geometry=None,
            section_orientation=doc['regional_support']['orientation'],layer='Satellite-derived surface core; no fixed measurement depth assigned.',
            time_convention=row['source_time_description'],boundary_rule=row['operator'],
            source_url=doc['source']['url'],source_citation='Krug and Tournadre (2012), doi:10.1029/2012GL052335',
            source_evidence_kind='published_satellite_regional_mean_core',
            extraction_method='Transcribed author-reported mean; no source-curve digitization or current-field processing.',
            source_file=SOURCE,source_file_sha256=pin,source_pointer=f'/records/{index}',
            phase_label=row['label']+' / published mean',phase_kind='satellite_core_mean_width',
            observed_period=None,fixed_layer_bounds_m=None,boundary_sides='source_defined_paired_core_edges',
            whole_current_representative=False,width_rank_eligible=False,full_width_inference_eligible=False,
            annual_extrema_eligible=False,seasonal_playback_eligible=False,is_confidence_interval=False,
            confidence_interval_km=None,geometry=None,
            satellite_core_context={'regional_support':copy.deepcopy(doc['regional_support']),
                'source_ambiguities':copy.deepcopy(doc['source_ambiguities']),
                'seasonality_finding':copy.deepcopy(doc['seasonality_finding']),
                'excluded_context':copy.deepcopy(doc['excluded_context']),
                'full_context_figure':FIGURE})
        rows.append(row)
    return rows


def prepare(bundle,*,logical_parent_sha256):
    if bundle.get('schema')!='osw.query-bundle.v1' or logical_parent_sha256!=PARENT:raise ValueError('Exact installed logical parent required')
    if KEY in bundle['manifest'] or SOURCE in bundle['manifest'].get('input_sha256',{}):raise ValueError('Satellite source already present')
    widths=bundle['collections']['widths'];objects=bundle['collections']['objects'];rows=records()
    if len(widths)!=172 or any(r['id'] in {r['id'] for r in rows} or 'satellite_core_context' in r for r in widths):raise ValueError('Exact172 old widths without new source required')
    owners=[r for r in objects if r['id']==OWNER]
    if len(owners)!=1 or owners[0]['capabilities']['scoped_width']!=2 or set(owners[0]['width_ids'])!=OLD_IDS or len(owners[0]['width_ids'])!=2:raise ValueError('Exact existing Agulhas width join required')
    if {r['id'] for r in widths if r.get('current_id')=='agulhas'}!=OLD_IDS:raise ValueError('Existing Agulhas widths differ')
    receipt=bundle['manifest'].get('dashboard_receipt',{});raw=receipt.get('source_json','').encode()
    if receipt.get('source_file')!=DASHBOARD or receipt.get('source_sha256')!=hashlib.sha256(raw).hexdigest() or bundle['manifest']['input_sha256'].get(DASHBOARD)!=receipt.get('source_sha256'):raise ValueError('Historical dashboard receipt differs')
    original_dashboard=json.loads(raw);prior_fingerprint=owners[0]['fingerprint'];prior_measurements_fingerprint=owners[0]['section_fingerprints']['measurements']
    source_owners=[r for r in original_dashboard['entries'] if r['id']==OWNER]
    if len(source_owners)!=1:raise ValueError('Historical dashboard owner missing')
    dashboard_row(source_owners[0],prior_fingerprint,prior_measurements_fingerprint)
    result=copy.deepcopy(bundle);result['collections']['widths'].extend(rows)
    owner=next(r for r in result['collections']['objects'] if r['id']==OWNER)
    owner['width_ids'].extend(r['id'] for r in rows);owner['capabilities']['scoped_width']=4
    owner['fingerprint']=changed_fingerprint(prior_fingerprint,'object')
    owner['section_fingerprints']['measurements']=changed_fingerprint(prior_measurements_fingerprint,'measurements')
    _,pin=document();result['manifest'].setdefault('input_sha256',{})[SOURCE]=pin
    result['manifest'][KEY]={'logical_parent_sha256':PARENT,'source_file':SOURCE,'source_file_sha256':pin,
        'records_added':2,'prior_width_records':172,'prior_agulhas_width_ids':list(owners[0]['width_ids']),
        'width_samples_added':0,'length_records_added':0,'geometry_added':False,
        'prior_dashboard_fingerprint':prior_fingerprint,'prior_measurements_fingerprint':prior_measurements_fingerprint}
    return result
