"""Pure connected-component/core-path operators for a declared OSCAR diagnostic."""
from collections import deque
import math


def valid(value):return value is not None and math.isfinite(value)


def eligible(east,north,threshold):
    return [[valid(u) and valid(v) and u < -threshold for u,v in zip(ur,vr)] for ur,vr in zip(east,north)]


def components(mask):
    ny=len(mask);nx=len(mask[0]);labels=[[-1]*nx for _ in range(ny)];groups=[]
    for y in range(ny):
        for x in range(nx):
            if not mask[y][x] or labels[y][x]>=0:continue
            ident=len(groups);cells=set();queue=deque([(y,x)]);labels[y][x]=ident
            while queue:
                a,b=queue.popleft();cells.add(a*nx+b)
                for c,d in ((a-1,b),(a+1,b),(a,b-1),(a,b+1)):
                    if 0<=c<ny and 0<=d<nx and mask[c][d] and labels[c][d]<0:
                        labels[c][d]=ident;queue.append((c,d))
            groups.append({'id':ident,'cells':cells,'touches_west_gate':any(i%nx==0 for i in cells),
                           'touches_east_gate':any(i%nx==nx-1 for i in cells),
                           'touches_window_edge':any(i//nx in (0,ny-1) for i in cells)})
    return labels,groups


def aligned(lon_east,lat_east,lon_west,lat_west,u,v,angle):
    dx=(lon_west-lon_east)*math.cos(math.radians((lat_east+lat_west)/2));dy=lat_west-lat_east
    denominator=math.hypot(dx,dy)*math.hypot(u,v)
    return denominator>0 and (u*dx+v*dy)/denominator >= math.cos(math.radians(angle))-1e-12


def core_path(latitude,longitude,east,north,threshold=.025,penalty=.02,angle=60):
    ny=len(latitude);nx=len(longitude)
    if ny<2 or nx<2 or len(east)!=ny or len(north)!=ny or any(len(row)!=nx for row in east+north):
        raise ValueError('Incomplete source grid')
    if any(b<=a for a,b in zip(latitude,latitude[1:])) or any(not 0<b-a<180 for a,b in zip(longitude,longitude[1:])):
        raise ValueError('Grid order or longitude ambiguity')
    if threshold<0 or penalty<0 or not 0<angle<=90:raise ValueError('Invalid frozen path parameter')
    mask=eligible(east,north,threshold)
    scores=[0.0 if mask[y][-1] else None for y in range(ny)]
    ways=[1 if value is not None else 0 for value in scores];parents={}
    if not any(ways):return {'reason':'no_eligible_east_gate','path':None,'score':None,'ambiguous':False}
    for x in range(nx-2,-1,-1):
        next_scores=[None]*ny;next_ways=[0]*ny
        for y in range(ny):
            if not mask[y][x]:continue
            for old_y in range(max(0,y-1),min(ny,y+2)):
                if scores[old_y] is None:continue
                if old_y!=y and not (mask[old_y][x] or mask[y][x+1]):continue
                coords=(longitude[x+1],latitude[old_y],longitude[x],latitude[y])
                if not (aligned(*coords,east[old_y][x+1],north[old_y][x+1],angle)
                        and aligned(*coords,east[y][x],north[y][x],angle)):continue
                score=scores[old_y]-(east[old_y][x+1]+east[y][x])/2-penalty*(y-old_y)**2
                if next_scores[y] is None or score>next_scores[y]+1e-12:
                    next_scores[y]=score;next_ways[y]=ways[old_y];parents[(x,y)]=old_y
                elif abs(score-next_scores[y])<=1e-12:next_ways[y]=min(2,next_ways[y]+ways[old_y])
        scores,ways=next_scores,next_ways
        if not any(ways):return {'reason':'no_directed_connection','failed_longitude_east':longitude[x],
                                'path':None,'score':None,'ambiguous':False}
    maximum=max(s for s in scores if s is not None)
    winners=[y for y,s in enumerate(scores) if s is not None and abs(s-maximum)<=1e-12]
    ambiguous=sum(ways[y] for y in winners)>1
    y=winners[0];path=[y]
    for x in range(nx-1):y=parents[(x,y)];path.append(y)
    return {'reason':'ambiguous_score_tie' if ambiguous else None,'path':path,'score':maximum,'ambiguous':ambiguous}


def anchored_span(latitude,east,index):
    result={'south_latitude':None,'north_latitude':None,'anchor_latitude':latitude[index],
            'reason':None,'source_cell_interval':None}
    if not valid(east[index]) or east[index]>=0:return dict(result,reason='anchor_not_westward')
    edges=[];limits=[];reasons=[]
    for direction,side in ((-1,'south'),(1,'north')):
        previous=index;edge=None;reason=None
        for current in range(index+direction,len(latitude) if direction==1 else -1,direction):
            if not valid(east[current]):reason='missing_'+side+'_edge';break
            if east[current]>=0:
                edge=latitude[previous]-east[previous]*(latitude[current]-latitude[previous])/(east[current]-east[previous]);break
            previous=current
        if edge is None and reason is None:reason=side+'_halo_censored'
        edges.append(edge);limits.append(previous)
        if reason:reasons.append(reason)
    return dict(result,south_latitude=edges[0],north_latitude=edges[1],source_cell_interval=limits,
                reason=';'.join(reasons) if reasons else None)


def component_links(previous,following,minimum=.5):
    """Return all nonempty overlaps plus unique mutual-threshold connections."""
    edges=[]
    for a in previous:
        for b in following:
            overlap=len(a['cells']&b['cells'])
            if not overlap:continue
            af=overlap/len(a['cells']);bf=overlap/len(b['cells'])
            edges.append({'previous':a['id'],'following':b['id'],'intersecting_cells':overlap,
                'previous_fraction':af,'following_fraction':bf,'jaccard':overlap/len(a['cells']|b['cells']),
                'meets_mutual_threshold':af>=minimum and bf>=minimum})
    candidates=[e for e in edges if e['meets_mutual_threshold']]
    for row in edges:
        row['unique_one_to_one']=row['meets_mutual_threshold'] and sum(e['previous']==row['previous'] for e in candidates)==1 and sum(e['following']==row['following'] for e in candidates)==1
    return edges


def interval_continuation(a,b):
    if a is None or b is None:return {'continues':False,'reason':'missing_paired_span'}
    intersection=max(0,min(a[1],b[1])-max(a[0],b[0]));aw=a[1]-a[0];bw=b[1]-b[0]
    if aw<=0 or bw<=0:raise ValueError('Invalid paired span')
    af=intersection/aw;bf=intersection/bw
    return {'continues':af>=.5 and bf>=.5,'previous_fraction':af,'following_fraction':bf,
            'reason':None if af>=.5 and bf>=.5 else 'local_branch_overlap_below_half'}
