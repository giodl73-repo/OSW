"""Check source support, map/display rules and profile synchronization."""
import hashlib
import json
from pathlib import Path
import numpy as np
from fetch_norkyst_ingoy_annual_samples import DATES
from build_norkyst_ingoy_maps import RULES, decoded, rotated_vectors

ROOT=Path(__file__).resolve().parents[1]


def validate(doc,timeline):
    if doc['rules']!=RULES or doc['status']!='model_field_display_not_canonical_current_geometry' or doc['annual_extrema_eligible'] is not False or doc['state_footprint_join_eligible'] is not False or doc['source_license']!='CC-BY-4.0':
        raise ValueError('Changed map meaning or rendering rules')
    for kind in ['acquisition','generator','protocol','projection_helper']:
        if hashlib.sha256((ROOT/doc[f'{kind}_file']).read_bytes()).hexdigest()!=doc[f'{kind}_sha256']:raise ValueError('Stale map provenance')
    if [frame['date'] for frame in doc['frames']]!=DATES:raise ValueError('Incomplete frame support')
    if len(doc['frames'])!=len(timeline['frames']):raise ValueError('Incomplete profile synchronization')
    for frame,section in zip(doc['frames'],timeline['frames']):
        for key in ['date','sample_time_utc','receipt_file','receipt_sha256']:
            if frame[key]!=section[key]:raise ValueError('Map/profile mismatch')
        path=ROOT/frame['receipt_file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=frame['receipt_sha256']:raise ValueError('Stale map source')
        if hashlib.sha256((ROOT/frame['figure']).read_bytes()).hexdigest()!=frame['figure_sha256']:raise ValueError('Changed map figure')
        receipt=json.loads(path.read_text(encoding='utf-8'))
        sal,east,north=(decoded(receipt,name) for name in ['salinity','u_eastward','v_northward'])
        lon,lat=(np.asarray(receipt['packed_field_arrays'][name]) for name in ['lon','lat'])
        u,v=rotated_vectors(lon,lat,east,north)
        if not np.allclose(np.hypot(u,v),np.hypot(east,north),atol=1e-10,equal_nan=True):raise ValueError('Arrow speed changed by rotation')
        stride=RULES['velocity_arrow_grid_stride'];sl=(slice(None,None,stride),slice(None,None,stride))
        if frame['salinity_valid_cells']!=int(np.isfinite(sal).sum()) or frame['vector_valid_cells']!=int(np.isfinite(u[sl]).sum()) or frame['salinity_cells_outside_color_limits']!=int(((sal<33)|(sal>35.2)).sum()):raise ValueError('Changed map counts or clipped-color declaration')
        bounds={'west':float(lon.min()),'east':float(lon.max()),'south':float(lat.min()),'north':float(lat.max())}
        if frame['geographic_bounds']!=bounds or frame['map_role']!='regional_model_field_subset_not_named_current_boundary_or_state_footprint':raise ValueError('Changed geographic/physical map interpretation')


def main():
    doc=json.loads((ROOT/'research/norkyst-ingoy-2024-map-frames.json').read_text(encoding='utf-8'))
    timeline=json.loads((ROOT/'research/norkyst-ingoy-2024-section-timeline.json').read_text(encoding='utf-8'))
    validate(doc,timeline)
    print('OK: 12 synchronized projected maps; sources, vectors, color support, files and non-admission verified')


if __name__=='__main__':main()
