"""Cloud-only sampled core scenarios with explicit two-jet segmentation."""
import hashlib
import itertools
import json
from pathlib import Path
from urllib.request import Request, urlopen
from pyproj import Geod
from audit_malvinas_adcp_depth_v1 import parse

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/malvinas-branch-core-operator-v1.json'


def smooth(samples,positions,quality,window,min_fraction=0.8,min_count=5):
    """Centered uniform average on native levels; absent samples remain absent."""
    levels=sorted({r['depth'] for group in samples for r in group})
    native=[{r['depth']:r for r in group} for group in samples]
    result=[]
    half=window/2
    for i,x in enumerate(positions):
        if not samples[i] or x<positions[0]+half or x>positions[-1]-half:
            result.append({});continue
        neighbors=[j for j,y in enumerate(positions) if abs(y-x)<=half]
        profile={}
        for depth in levels:
            valid=[(positions[j],native[j][depth]['v']) for j in neighbors if depth in native[j]
                   and native[j][depth]['v'] is not None and native[j][depth]['quality'] is not None
                   and native[j][depth]['quality']>=quality]
            if len(valid)<min_count or len(valid)<min_fraction*len(neighbors):continue
            if max(p[0] for p in valid)-min(p[0] for p in valid)<0.6*window:continue
            profile[depth]={'v_cm_s':sum(v for _,v in valid)/len(valid),'contributors':len(valid),'possible_ensembles':len(neighbors)}
        result.append(profile)
    return result


def spatial_select(samples):
    """One native ensemble nearest each1km cell center; retain empty cells."""
    metadata=[r[0] for r in samples]
    start=metadata[0]['lon'];lat=sum(r['lat'] for r in metadata)/len(metadata)
    geod=Geod(ellps='WGS84')
    distances=[geod.inv(start,lat,r['lon'],lat)[2]/1000*(1 if r['lon']<=start else -1) for r in metadata]
    if min(distances)<-1 or distances[-1]<max(distances)-1 or max(r['lat'] for r in metadata)-min(r['lat'] for r in metadata)>0.05:
        raise ValueError('Crossing geometry exceeds reviewed nearly zonal extent')
    bins={}
    for i,x in enumerate(distances):
        cell=int(x//1)
        if cell<0:continue
        if cell not in bins or (abs(x-(cell+0.5)),i)<(abs(distances[bins[cell]]-(cell+0.5)),bins[cell]):bins[cell]=i
    positions=[k+0.5 for k in range(max(bins)+1)]
    chosen=[samples[bins[k]] if k in bins else [] for k in range(len(positions))]
    meta=[metadata[bins[k]] if k in bins else None for k in range(len(positions))]
    return chosen,positions,meta,{'native_ensembles':len(samples),'occupied_1km_cells':len(bins),
        'empty_1km_cells':len(positions)-len(bins),'eastward_steps':sum(b<a for a,b in zip(distances,distances[1:])),
        'selection':'nearest_native_ensemble_to_each_1km_cell_center_ties_earliest'}


def choose_branches(surface,positions,min_separation):
    """Two positive local maxima; the intervening minimum is the split."""
    peaks=[i for i in range(1,len(surface)-1) if surface[i] is not None and surface[i]>0
           and surface[i-1] is not None and surface[i+1] is not None
           and surface[i]>=surface[i-1] and surface[i]>=surface[i+1]
           and (surface[i]>surface[i-1] or surface[i]>surface[i+1])]
    pairs=[(i,j) for i,j in itertools.combinations(peaks,2) if positions[j]-positions[i]>=min_separation]
    if not pairs:return None
    i,j=max(pairs,key=lambda pair:(surface[pair[0]]+surface[pair[1]],positions[pair[1]]-positions[pair[0]]))
    between=[k for k in range(i+1,j) if surface[k] is not None]
    if not between:return None
    split=min(between,key=lambda k:(surface[k],abs(positions[k]-(positions[i]+positions[j])/2)))
    return {'offshore_surface_peak_index':i,'inshore_surface_peak_index':j,'separator_index':split}


def summarize_branch(indices,profiles,positions,native_metadata):
    cells=[(p['v_cm_s'],i,z) for i in indices for z,p in profiles[i].items() if p['v_cm_s']>0]
    if not cells:return {'status':'unknown_no_supported_positive_cells','depth_m':None}
    maximum=max(v for v,_,_ in cells)
    maxima=[(i,z) for v,i,z in cells if abs(v-maximum)<1e-12]
    i,z=maxima[0]
    profile=profiles[i];levels=sorted(profile)
    return {'status':'conditional_sampled_branch_maximum','smoothed_northward_max_cm_s':round(maximum,6),
            'sampled_maximum_depths_m':sorted({depth for _,depth in maxima}),
            'maximum_native_ensemble_indices':[index for index,_ in maxima],
            'longitude':native_metadata[i]['lon'],'latitude':native_metadata[i]['lat'],
            'datetime_at_window_center':native_metadata[i]['date'],'center_distance_from_eastern_start_km':round(positions[i],6),
            'maximum_at_shallowest_supported_level':z==levels[0],
            'maximum_at_deepest_supported_level':z==levels[-1],
            'supported_depth_domain_m':[levels[0],levels[-1]],
            'vertical_profile_at_selected_center':[{'depth_m':depth,**profile[depth]} for depth in levels],
            'flow_bottom_m':None,'physical_thickness_m':None,'uncertainty_m':None}


def derive(raw,operator):
    _,groups,count=parse(raw)
    ordered=sorted(groups.items());original_samples=[v for _,v in ordered]
    samples,positions,metadata,resampling=spatial_select(original_samples)
    shallow=min(r['depth'] for group in samples for r in group)
    scenarios=[]
    for quality,window in itertools.product(operator['quality_pg_scenarios_percent'],operator['uniform_window_scenarios_km']):
        profiles=smooth(samples,positions,quality,window)
        surface=[p.get(shallow,{}).get('v_cm_s') for p in profiles]
        split=choose_branches(surface,positions,operator['minimum_surface_peak_separation_km'])
        scenario={'quality_pg_min_percent':quality,'uniform_window_km':window,'shallowest_native_depth_m':shallow}
        if split is None:
            scenario.update(status='unknown_two_jet_split_not_resolved',branches=None)
        else:
            k=split['separator_index'];scenario.update(status='conditional_two_jet_segmentation',split=split,
                separator_distance_from_east_km=round(positions[k],6),separator_longitude=metadata[k]['lon'],
                branches={'offshore_main_candidate':summarize_branch(range(0,k),profiles,positions,metadata),
                          'western_inshore_candidate':summarize_branch(range(k+1,len(samples)),profiles,positions,metadata)})
        scenarios.append(scenario)
    return {'schema':'osw.malvinas-branch-core-scenarios.v1','status':'CONDITIONAL_NATIVE_DEPTH_CORE_SCENARIOS_NOT_PAPER_REPRODUCTION',
            'source_doi':operator['source_doi'],'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),
            'native_rows':count,'native_ensembles':len(original_samples),'spatial_resampling':resampling,'scenarios':scenarios,
            'canonical_depth_references_added':0,'physical_flow_boundaries_established':0,
            'whole_route_depth_profiles':0,'volume_estimates':0,'full_goal_complete':False}


if __name__=='__main__':
    operator=json.loads((ROOT/OPERATOR).read_bytes())
    with urlopen(Request(operator['data_url'],headers={'User-Agent':'OSW-depth-scenario/1.0'}),timeout=50) as response:
        raw=response.read(operator['maximum_download_bytes']+1)
    if len(raw)>operator['maximum_download_bytes'] or hashlib.sha256(raw).hexdigest()!=operator['expected_raw_sha256']:
        raise ValueError('Raw archive differs from audited source or exceeds bound')
    result=derive(raw,operator)
    result['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [OPERATOR,'analysis/derive_malvinas_branch_core_scenarios_v1.py','analysis/audit_malvinas_adcp_depth_v1.py']}
    output=ROOT/'malvinas-branch-core-scenarios-v1';output.mkdir(exist_ok=True)
    (output/'candidate.json').write_bytes((json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode('utf8'))
    summary=[]
    for scenario in result['scenarios']:
        branches={name:{field:branch.get(field) for field in ['sampled_maximum_depths_m','smoothed_northward_max_cm_s','longitude']}
                  for name,branch in (scenario.get('branches') or {}).items()}
        summary.append({'pg':scenario['quality_pg_min_percent'],'window_km':scenario['uniform_window_km'],
                        'status':scenario['status'],'branches':branches})
    print(json.dumps(summary))
