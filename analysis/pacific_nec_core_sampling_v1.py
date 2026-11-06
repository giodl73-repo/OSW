"""Native-data-preserving anchor-grid and vertex-sampling operators."""
import math
import pacific_nec_connected_core_v1 as native


def indices(size,stride,phase):
    if size<2 or stride not in (1,2,4) or not 0<=phase<stride:raise ValueError('Invalid sampling grid')
    return sorted({0,size-1,*range(phase,size,stride)})


def corridor_path(latitude,longitude,east,north,west_x,west_y,east_x,east_y,
                  threshold=.025,penalty=.02,angle=60):
    """A native witness for one coarse leg, not a shortcut through its chord."""
    if not 0<=west_x<east_x<len(longitude):raise ValueError('Invalid coarse leg')
    ny=len(latitude)
    if not 0<=west_y<ny or not 0<=east_y<ny:raise ValueError('Invalid anchor latitude')
    mask=lambda y,x:native.valid(east[y][x]) and native.valid(north[y][x]) and east[y][x]<-threshold
    if not mask(east_y,east_x) or not mask(west_y,west_x):return None
    scores={east_y:0.0};ways={east_y:1};parents={}
    for x in range(east_x-1,west_x-1,-1):
        ideal=west_y+(east_y-west_y)*(x-west_x)/(east_x-west_x)
        ys={west_y} if x==west_x else {math.floor(ideal),math.ceil(ideal)}
        following={};counts={}
        for y in sorted(ys):
            if not 0<=y<ny or not mask(y,x):continue
            for old_y in sorted(scores):
                if abs(old_y-y)>1:continue
                if old_y!=y and not (mask(old_y,x) or mask(y,x+1)):continue
                geometry=(longitude[x+1],latitude[old_y],longitude[x],latitude[y])
                if not (native.aligned(*geometry,east[old_y][x+1],north[old_y][x+1],angle)
                    and native.aligned(*geometry,east[y][x],north[y][x],angle)):continue
                score=scores[old_y]-(east[old_y][x+1]+east[y][x])/2-penalty*(y-old_y)**2
                if y not in following or score>following[y]+1e-12:
                    following[y]=score;counts[y]=ways[old_y];parents[(x,y)]=old_y
                elif abs(score-following[y])<=1e-12:counts[y]=min(2,counts[y]+ways[old_y])
        scores,ways=following,counts
        if not scores:return None
    y=west_y;path=[y]
    for x in range(west_x,east_x):y=parents[(x,y)];path.append(y)
    return {'score':scores[west_y],'ways':ways[west_y],'path':path}


def anchored_path(latitude,longitude,east,north,x_indices,y_indices,cache=None):
    if x_indices[0]!=0 or x_indices[-1]!=len(longitude)-1 or y_indices[0]!=0 or y_indices[-1]!=len(latitude)-1:
        raise ValueError('Sampling must retain gates and window boundaries')
    if sorted(set(x_indices))!=x_indices or sorted(set(y_indices))!=y_indices:raise ValueError('Sampling order differs')
    cache={} if cache is None else cache
    def edge(x,y,old_x,old_y):
        key=(x,y,old_x,old_y)
        if key not in cache:cache[key]=corridor_path(latitude,longitude,east,north,*key)
        return cache[key]
    scores={y:0.0 for y in y_indices if native.valid(east[y][-1]) and native.valid(north[y][-1]) and east[y][-1]<-.025}
    ways={y:1 for y in scores};parents={}
    if not scores:return {'reason':'no_eligible_east_gate','path':None,'anchors':None,'score':None}
    for j in range(len(x_indices)-2,-1,-1):
        x,old_x=x_indices[j:j+2];following={};counts={}
        for yi,y in enumerate(y_indices):
            for old_y in y_indices[max(0,yi-1):yi+2]:
                if old_y not in scores:continue
                witness=edge(x,y,old_x,old_y)
                if witness is None:continue
                score=scores[old_y]+witness['score'];number=min(2,ways[old_y]*witness['ways'])
                if y not in following or score>following[y]+1e-12:
                    following[y]=score;counts[y]=number;parents[(j,y)]=(old_y,witness['path'])
                elif abs(score-following[y])<=1e-12:counts[y]=min(2,counts[y]+number)
        scores,ways=following,counts
        if not scores:return {'reason':'no_native_supported_anchor_connection','failed_longitude_east':longitude[x],
                              'path':None,'anchors':None,'score':None}
    maximum=max(scores.values());winners=sorted(y for y,score in scores.items() if abs(score-maximum)<=1e-12)
    ambiguous=sum(ways[y] for y in winners)>1;y=winners[0];path=[];anchors=[y]
    for j in range(len(x_indices)-1):
        old_y,leg=parents[(j,y)];path.extend(leg[:-1]);anchors.append(old_y);y=old_y
    path.append(y)
    if len(path)!=len(longitude):raise ValueError('Native witness is incomplete')
    return {'reason':'ambiguous_score_tie' if ambiguous else None,'path':path,'anchors':anchors,'score':maximum}


def length(longitude,latitude,path,distance,selected=None):
    chosen=list(range(len(path))) if selected is None else selected
    chosen=list(reversed(chosen))  # Preserve the preceding westward point order.
    return math.fsum(distance(longitude[a],latitude[path[a]],longitude[b],latitude[path[b]]) for a,b in zip(chosen,chosen[1:]))
