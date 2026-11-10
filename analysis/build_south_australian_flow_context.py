"""Pinned model-grid flow context, never named-current or width admission."""
import calendar
from collections import deque
from datetime import datetime,timedelta,timezone
import json
import math

import numpy as np

from acquire_south_australian_hycom_2d import ROOT,DIRECTORY,verify,sha

PROTOCOL='plans/south-australian-hycom-2d-flow-context-protocol-v1.md'
PROTOCOL_SHA='f4cadbb0adb77a36ef23c9406fb2d2a9793fd525df3aedfe8611f89d21bf7583'
ORIGINAL='research/south-australian-132e-100m-2012-monthly-component-spans.json'
ORIGINAL_SHA='1a70cd4fdb8761b905c14ae7cce2419ae905a489c06421a57fbbd789f009e0e3'
GENERATOR='analysis/build_south_australian_flow_context.py'
OUTPUT='research/south-australian-hycom-2d-flow-context.json'
SOURCE_ACQUISITION_SHA='9d9608f1d84585367209aa1c3bfe2d5fbf4d5c9ae4c74f51ffb2fd6b5f6c3c78'


def connected_component(eastward,supported,seed,threshold):
    """Four-neighbor membership and boundary edge counts, with no bridging."""
    eligible=supported&np.isfinite(eastward)&(eastward>=threshold)
    if not eligible[seed]:
        return {'status':'seed_not_supported_above_threshold','cells':[],
                'touched_box_sides':[],'neighbor_barrier_edges':None}
    queue=deque([seed]);seen={seed};barriers={'unsupported':0,'sub_threshold':0,'domain':0};sides=set()
    ny,nx=eligible.shape
    while queue:
        y,x=queue.popleft()
        for dy,dx,side in [(-1,0,'south'),(1,0,'north'),(0,-1,'west'),(0,1,'east')]:
            other=(y+dy,x+dx);oy,ox=other
            if not (0<=oy<ny and 0<=ox<nx):
                barriers['domain']+=1;sides.add(side)
            elif not supported[other] or not np.isfinite(eastward[other]):barriers['unsupported']+=1
            elif not eligible[other]:barriers['sub_threshold']+=1
            elif other not in seen:seen.add(other);queue.append(other)
    cells=[list(cell) for cell in sorted(seen)]
    return {'status':'seed_component_in_model_grid','cells':cells,
            'touched_box_sides':sorted(sides),'neighbor_barrier_edges':barriers}


def monthly_vectors(arrays,indices,required):
    u=arrays['water_u'][indices];v=arrays['water_v'][indices]
    valid=(u!=-30000)&(v!=-30000)
    counts=valid.sum(axis=0);supported=counts>=required
    fields=[]
    for values in [u,v]:
        sums=np.where(valid,values.astype(float)*.001,0).sum(axis=0)
        fields.append(np.divide(sums,counts,out=np.full(counts.shape,np.nan),where=supported))
    return *fields,counts,supported


def build():
    if sha(ROOT/PROTOCOL)!=PROTOCOL_SHA or sha(ROOT/ORIGINAL)!=ORIGINAL_SHA:
        raise ValueError('Changed flow-context protocol/original diagnostic')
    if sha(DIRECTORY/'acquisition.json')!=SOURCE_ACQUISITION_SHA:
        raise ValueError('Changed frozen surrounding-source acquisition receipt')
    receipt,arrays,quality=verify()
    original=json.loads((ROOT/ORIGINAL).read_bytes())
    dates=[datetime(2000,1,1,tzinfo=timezone.utc)+timedelta(hours=float(t)) for t in arrays['time']]
    longitude=quality['source_132e_overlap']['longitude_index_in_subset']
    months=[]
    for month in range(1,13):
        indices=[i for i,d in enumerate(dates) if d.month==month]
        required=math.ceil(.8*calendar.monthrange(2012,month)[1])
        u,v,counts,supported=monthly_vectors(arrays,indices,required)
        old=original['months'][month-1]
        if old['month']!=month or old['minimum_required_pairs']!=required:raise ValueError('Changed original month support')
        for y,profile in enumerate(old['profile']):
            if counts[y,longitude]!=profile['paired_source_samples']:raise ValueError('Changed original monthly pair count')
            for values,key in [(u,'eastward_m_s'),(v,'northward_m_s')]:
                expected=profile[key];actual=values[y,longitude]
                if (expected is None and not np.isnan(actual)) or (expected is not None and (not np.isfinite(actual) or abs(actual-expected)>1e-12)):
                    raise ValueError('Changed original monthly component mean')
        seed_indices=np.flatnonzero(arrays['lat']==old['nominal']['peak_coordinate'])
        if len(seed_indices)!=1:raise ValueError('Original peak has no unique native latitude')
        seed=(int(seed_indices[0]),longitude);seed_u=float(u[seed]);seed_v=float(v[seed])
        peak=old['nominal']['peak_component_m_s']
        if not supported[seed] or not math.isfinite(seed_u) or abs(seed_u-peak)>1e-12:raise ValueError('Changed original peak support/value')
        speed=math.hypot(seed_u,seed_v)
        cases=[]
        for fraction in [.4,.5,.6]:
            threshold=fraction*peak;component=connected_component(u,supported,seed,threshold)
            cells=component['cells'];ys=[p[0] for p in cells];xs=[p[1] for p in cells]
            component.update(fraction=fraction,threshold_m_s=threshold,cell_count=len(cells),
                occupied_native_longitudes=len(set(xs)),
                longitude_bounds=[float(arrays['lon'][min(xs)]),float(arrays['lon'][max(xs)])] if cells else None,
                latitude_bounds=[float(arrays['lat'][min(ys)]),float(arrays['lat'][max(ys)])] if cells else None)
            cases.append(component)
        months.append({'month':month,'source_indices':indices,'source_days':len(indices),'minimum_required_pairs':required,
            'supported_cells':int(supported.sum()),'paired_counts_by_cell':counts.tolist(),
            'seed':{'indices':list(seed),'longitude':float(arrays['lon'][longitude]),'latitude':float(arrays['lat'][seed[0]]),
                    'eastward_m_s':seed_u,'northward_m_s':seed_v,'speed_m_s':speed,
                    'angle_degrees_north_of_east':math.degrees(math.atan2(seed_v,seed_u)),
                    'eastward_fraction_of_speed':seed_u/speed if speed else None},
            'original_section_span_km':old['nominal']['span_km'],'threshold_cases':cases})
    return {'schema':'osw.south-australian-hycom-2d-flow-context.v1','current_id':'south-australian',
            'status':'model_grid_flow_context_not_current_identity_or_dimensions','year':2012,'depth_m':100,
            'protocol_file':PROTOCOL,'protocol_sha256':PROTOCOL_SHA,'generator_file':GENERATOR,'generator_sha256':sha(ROOT/GENERATOR),
            'source_acquisition_file':(DIRECTORY/'acquisition.json').relative_to(ROOT).as_posix(),
            'source_acquisition_sha256':sha(DIRECTORY/'acquisition.json'),'original_diagnostic_file':ORIGINAL,'original_diagnostic_sha256':ORIGINAL_SHA,
            'longitude':arrays['lon'].tolist(),'latitude':arrays['lat'].tolist(),'months':months,
            'adjacency':'four_neighbor_native_grid','cells_are_current_footprint':False,
            'current_association_verified':False,'width_measurement_admitted':False,
            'annual_range_admitted':False,'is_climatology':False,
            'scope_note':'Threshold connectivity of monthly mean model vectors; not material paths, current axes, physical widths or annual extrema. Box contacts and disconnections do not establish named-current identity.'}


if __name__=='__main__':
    report=build();(ROOT/OUTPUT).write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'months':len(report['months']),'cases':sum(len(m['threshold_cases']) for m in report['months'])}))
