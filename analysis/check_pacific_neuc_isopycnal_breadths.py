"""Author-reported angular component breadths retain density and mean support."""
import copy,hashlib,json
from pathlib import Path
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/pacific-neuc-li-2018-isopycnal-breadth-scope-audit.json'
AUDIT_SHA='2edff326fd4b7bbc2c6a8cdd1ef0324bac77a62f7e85579cd8ff38753e2db9a6'

def document():
    raw=(ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=AUDIT_SHA:raise ValueError('Changed Pacific NEUC source breadth scope')
    doc=json.loads(raw)
    for kind in ['source_document','acquisition','protocol','source_figure_receipt']:
        if hashlib.sha256((ROOT/doc[kind+'_file']).read_bytes()).hexdigest()!=doc[kind+'_sha256']:
            raise ValueError('Changed Pacific NEUC dependency: '+kind)
    if (ROOT/doc['source_document_file']).stat().st_size!=doc['source_document_bytes']:raise ValueError('Changed Pacific NEUC archived article size')
    for figure in doc['source_figures']:
        raw=(ROOT/figure['asset_file']).read_bytes()
        if len(raw)!=figure['asset_bytes'] or hashlib.sha256(raw).hexdigest()!=figure['asset_sha256']:raise ValueError('Changed Pacific NEUC source figure')
    return doc

def records(doc=None):
    doc=document() if doc is None else doc;rows=copy.deepcopy(doc['measurements'])
    for i,r in enumerate(rows):r['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
    return rows

def validate_row(row,audit=None):
    doc=document()
    if audit is not None and audit!=doc:raise ValueError('Changed Pacific NEUC reviewed source')
    expected=next((r for r in records(doc) if r['id']==row.get('id')),None)
    if row!=expected:raise ValueError('Pacific NEUC component, isopycnal or temporal support changed')
    c=row['original_regional_context'];degrees=c['source_reported_latitude_span_degrees'];km=Geod(ellps='WGS84').inv(0,-degrees/2,0,degrees/2)[2]/1000
    if abs(km-c['unrounded_distance_km'])>1e-6 or row['approximate_width_km']!=round(km/10)*10:raise ValueError('Pacific NEUC angular conversion differs')

if __name__=='__main__':
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    rows=[r for r in inventory['measurements'] if r['current_id']=='pacific-north-equatorial-undercurrent']
    if len(rows)!=2:raise ValueError('Missing distinct southern/northern NEUC descriptions')
    for row in rows:validate_row(row)
    print('PASS: two distinct Argo isopycnal NEUC breadths; no inferred middle breadth or annual range')
