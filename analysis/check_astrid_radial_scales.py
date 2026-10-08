"""Bind two distinct diagnostic radii to inspected original-source definitions."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH='research/astrid-2000-radial-scale-scope-audit.json'
HASH='00f15a476e1584ae8666d3ab5198d4139b4b63da5d2c78ca7ddd179ee3836776'
def validate(doc,geography):
    raw=(ROOT/doc['source_document_file']).read_bytes()
    if (doc['source_document_sha256'],doc['source_document_bytes'])!=(HASH,1136090) or hashlib.sha256(raw).hexdigest()!=HASH:raise ValueError('Changed Astrid original')
    acq=(ROOT/doc['acquisition_file']).read_bytes()
    if hashlib.sha256(acq).hexdigest()!=doc['acquisition_sha256'] or json.loads(acq)['sha256']!=HASH:raise ValueError('Changed Astrid acquisition')
    rows=doc['measurements']
    if len(rows)!=2:raise ValueError('Incomplete Astrid radial definitions')
    for row,(value,metric) in zip(rows,[(120,'radius_of_maximum_tangential_velocity'),(140,'thermocline_relaxation_integration_radius')]):
        if (row['entity_id'],row['value_km'],row['metric'])!=('eddy:geography:astrid-2000',value,metric):raise ValueError('Changed Astrid radius definition')
        if any(row[k] is not False for k in ['annual_extrema_eligible','seasonal_playback_eligible','footprint_inference_eligible','diameter_inference_eligible','area_inference_eligible']):raise ValueError('Promoted Astrid model radius')
        if any(row[k] is not None for k in ['geometry','reported_uncertainty_km','observed_period','calendar_months']):raise ValueError('Invented Astrid radius support')
    if doc['closed_footprint'] is not None or doc['annual_radius_range_km'] is not None or doc['nasa_individual_identity_claim'] is not False:raise ValueError('Invented Astrid footprint or year range')
    row=next(r for r in geography['entries'] if r['id']=='astrid-2000')
    if row['radial_scale_evidence']!=rows or row['reported_radius_km']!=120 or row['reported_radius_metric']!=rows[0]['metric'] or row['reported_radius_definition']!=rows[0]['definition'] or row['radial_scale_audit_file']!=PATH or row['radial_scale_audit_sha256']!=hashlib.sha256((ROOT/PATH).read_bytes()).hexdigest():raise ValueError('Astrid geography radius scope differs from source audit')
