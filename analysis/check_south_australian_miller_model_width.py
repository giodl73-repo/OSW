"""Bind a local model width to the acquired original, without temporal promotion."""
from pathlib import Path
from copy import deepcopy
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/south-australian-miller-2006-model-width-scope-audit.json'

def verify():
    report=json.loads((ROOT/AUDIT).read_bytes())
    row,=report['measurements']
    if (report['schema'],report['current_id'],row['current_id'],row['approximate_width_km'],row['experiment'],row['model_elapsed_day'],row['section_longitude_degrees_east'])!=('osw.published-model-width-scope.v1','south-australian','south-australian',60,6,20,130):
        raise ValueError('Changed Miller model width identity, value or experiment support')
    for key in ['is_annual_mean_width','is_mean_of_instantaneous_widths','whole_current_representative','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible']:
        if row.get(key) is not False:raise ValueError('Promoted Miller model width: '+key)
    for key in ['width_range_km','reported_uncertainty_km','observed_period','calendar_months','fixed_layer_bounds_m','section_geometry','annual_width_range_km']:
        if row.get(key,'missing') is not None:raise ValueError('Invented Miller model support: '+key)
    if report['canonical_width_inventory_admitted'] is not False or report['new_current_identity_admitted'] is not False:
        raise ValueError('Changed Miller inventory admission')
    if report.get('editorial_width_inventory_admitted') is not True or row.get('phase_kind')!='model_snapshot_width_summary' or row.get('unit')!='km':
        raise ValueError('Missing scoped Miller editorial admission')
    for path,pin in report['input_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=pin:raise ValueError('Changed Miller source dependency: '+path)
    receipt=json.loads((ROOT/report['acquisition_file']).read_bytes())
    raw=(ROOT/report['source_document_file']).read_bytes()
    if len(raw)!=receipt['bytes'] or hashlib.sha256(raw).hexdigest()!=receipt['sha256'] or receipt['sha256']!=report['source_document_sha256']:
        raise ValueError('Changed Miller original source bytes')
    return report

def record():
    row=deepcopy(verify()['measurements'][0])
    row.update(source_audit_file=AUDIT,source_audit_sha256=hashlib.sha256((ROOT/AUDIT).read_bytes()).hexdigest())
    return row

def validate_row(row):
    if row!=record():raise ValueError('Miller inventory row differs from source model snapshot')

def validate_inventory(document):
    expected=record()
    actual=[r for r in document['measurements'] if r.get('current_id')=='south-australian' or r.get('id')==expected['id']]
    if actual!=[expected]:raise ValueError('Missing, duplicated or changed Miller width inventory record')

if __name__=='__main__':
    doc=verify();print(json.dumps({'status':'PASS','reported_model_width_km':doc['measurements'][0]['approximate_width_km'],'editorial_inventory_records':1,'canonical_admissions':0}))
