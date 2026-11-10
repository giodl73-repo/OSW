"""Cloud GEBCO screening scenarios; gridded bathymetry is not bottom track."""
import hashlib
import itertools
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen
from pyproj import Geod
from audit_malvinas_adcp_depth_v1 import parse
from derive_malvinas_branch_core_scenarios_v1 import spatial_select,smooth,choose_branches,summarize_branch

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/malvinas-bathymetry-screen-operator-v1.json'
STEP=1/240
ORIGIN_LAT=-89.99791666666667
ORIGIN_LON=-179.99791666666667


def grid_index(value,origin):return math.floor((value-origin)/STEP+0.5)


def fetch(url,limit):
    with urlopen(Request(url,headers={'User-Agent':'OSW-depth-screen/1.0'}),timeout=50) as response:raw=response.read(limit+1)
    if len(raw)>limit:raise ValueError('Bounded source response exceeded')
    return raw


def parse_grid(raw,variable,nlat,nlon):
    text=raw.decode('utf8')
    pattern=rf'^{variable}\.{variable}\[{nlat}\]\[{nlon}\]\n(.*?)\n\n{variable}\.lat\[{nlat}\]\n([^\n]+)\n\n{variable}\.lon\[{nlon}\]\n([^\n]+)'
    match=re.search(pattern,text,re.M|re.S)
    if not match:raise ValueError('Unexpected GEBCO ASCII grid')
    grid=[]
    for i,line in enumerate(match.group(1).splitlines()):
        prefix,values=line.split(']',1)
        if int(prefix[1:])!=i:raise ValueError('Nonsequential grid row')
        row=[int(v.strip()) for v in values.lstrip(', ').split(',')]
        if len(row)!=nlon:raise ValueError('Wrong grid column count')
        grid.append(row)
    lat=[float(v.strip()) for v in match.group(2).split(',')];lon=[float(v.strip()) for v in match.group(3).split(',')]
    if len(grid)!=nlat or len(lat)!=nlat or len(lon)!=nlon:raise ValueError('Wrong grid dimensions')
    return grid,lat,lon


def cutoff(bottom_m,mode,draft=6,margin=8):
    if bottom_m is None or bottom_m<=draft:return None
    limit=bottom_m if mode=='bed_only' else draft+0.85*(bottom_m-draft)
    return limit-margin


def screen_rows(samples,bottoms,mode):
    output=[];removed=0;below_bed=0
    for group,bed in zip(samples,bottoms):
        selected=[]
        h=bed['footprint_shallowest_depth_m'] if mode=='footprint_sidelobe85' else bed['point_depth_m']
        limit=cutoff(h,'bed_only' if mode=='bed_only' else 'sidelobe85')
        for r in group:
            row=dict(r)
            if r['depth']>bed['point_depth_m']:below_bed+=1
            if limit is None or r['depth']>limit:
                if row['v'] is not None:removed+=1
                row['v']=None
            selected.append(row)
        output.append(selected)
    return output,{'velocity_samples_excluded_by_screen':removed,'native_samples_below_point_grid_bed':below_bed}


def derive(samples,bottoms,operator):
    scenarios=[]
    for mode in operator['screen_modes']:
        screened,counts=screen_rows(samples,bottoms,mode)
        selected,positions,metadata,resampling=spatial_select(screened)
        shallow=min(r['depth'] for group in selected for r in group)
        for quality,window in itertools.product([50,70,90],[15,25,35]):
            profiles=smooth(selected,positions,quality,window)
            surface=[p.get(shallow,{}).get('v_cm_s') for p in profiles]
            split=choose_branches(surface,positions,40)
            case={'screen_mode':mode,'quality_pg_min_percent':quality,'uniform_window_km':window,'screen_counts':counts}
            if split is None:case.update(status='unknown_two_jet_split_not_resolved',branches=None)
            else:
                k=split['separator_index']
                case.update(status='conditional_screened_two_jet_segmentation',separator_longitude=metadata[k]['lon'],
                            branches={'offshore_main_candidate':summarize_branch(range(k),profiles,positions,metadata),
                                      'western_inshore_candidate':summarize_branch(range(k+1,len(selected)),profiles,positions,metadata)})
            scenarios.append(case)
    return scenarios


def sample_bottoms(samples,grid,tids,lats,lons,start_lat,start_lon):
    geod=Geod(ellps='WGS84');result=[]
    for group in samples:
        r=group[0];gi=grid_index(r['lat'],ORIGIN_LAT);gj=grid_index(r['lon'],ORIGIN_LON)
        i,j=gi-start_lat,gj-start_lon
        h=-grid[i][j]
        if h<=6:raise ValueError('Non-ocean/very shallow cell requires separate review')
        # Circular envelope covers unknown beam azimuth plus a nominal grid-cell radius.
        radius=h*math.tan(math.radians(30))+400
        candidates=[]
        for a,lat in enumerate(lats):
            if abs(lat-r['lat'])*111500>radius+500:continue
            for b,lon in enumerate(lons):
                if abs(lon-r['lon'])*80000>radius+500:continue
                if geod.inv(r['lon'],r['lat'],lon,lat)[2]<=radius:
                    if grid[a][b]>=0:raise ValueError('Beam envelope contains land; separate review required')
                    candidates.append((-grid[a][b],a,b))
        if not candidates:raise ValueError('Empty footprint')
        # Explicit coordinate buffer check in metres; no clipping a requested footprint.
        lat_margin=min(abs(r['lat']-lats[0]),abs(lats[-1]-r['lat']))*110500
        lon_margin=min(abs(r['lon']-lons[0]),abs(lons[-1]-r['lon']))*77000
        if min(lat_margin,lon_margin)<radius:raise ValueError('Requested footprint exceeds bounded tile')
        shoal,a,b=min(candidates)
        result.append({'datetime':r['date'],'longitude':r['lon'],'latitude':r['lat'],
                       'point_depth_m':h,'point_tid_code':tids[i][j],'point_grid_lon_lat':[lons[j],lats[i]],
                       'footprint_radius_m':round(radius,6),'footprint_shallowest_depth_m':shoal,
                       'footprint_shallowest_tid_code':tids[a][b],'footprint_shallowest_grid_lon_lat':[lons[b],lats[a]],
                       'footprint_sampled_cells':len(candidates)})
    return result


def main():
    operator=json.loads((ROOT/OPERATOR).read_bytes())
    raw=fetch(operator['adcp_url'],8388608)
    if hashlib.sha256(raw).hexdigest()!=operator['adcp_raw_sha256']:raise ValueError('ADCP source changed')
    _,groups,count=parse(raw);samples=[v for _,v in sorted(groups.items())]
    coords=[r[0] for r in samples];pad=12
    a=min(grid_index(r['lat'],ORIGIN_LAT) for r in coords)-pad;b=max(grid_index(r['lat'],ORIGIN_LAT) for r in coords)+pad
    c=min(grid_index(r['lon'],ORIGIN_LON) for r in coords)-pad;e=max(grid_index(r['lon'],ORIGIN_LON) for r in coords)+pad
    nlat,nlon=b-a+1,e-c+1
    if nlat*nlon>30000:raise ValueError('GEBCO tile exceeds cell bound')
    constraint=f'[{a}:1:{b}][{c}:1:{e}]'
    elevation_url=operator['gebco_elevation_url']+'.ascii?elevation'+constraint
    tid_url=operator['gebco_tid_url']+'.ascii?tid'+constraint
    elevation_raw=fetch(elevation_url,1048576);tid_raw=fetch(tid_url,1048576)
    grid,lats,lons=parse_grid(elevation_raw,'elevation',nlat,nlon)
    tids,tid_lats,tid_lons=parse_grid(tid_raw,'tid',nlat,nlon)
    if lats!=tid_lats or lons!=tid_lons:raise ValueError('GEBCO coordinate mismatch')
    for i,lat in enumerate(lats):
        if abs(lat-(ORIGIN_LAT+(a+i)*STEP))>1e-7:raise ValueError('Unexpected latitude registration')
    for j,lon in enumerate(lons):
        if abs(lon-(ORIGIN_LON+(c+j)*STEP))>1e-7:raise ValueError('Unexpected longitude registration')
    bottoms=sample_bottoms(samples,grid,tids,lats,lons,a,c)
    scenarios=derive(samples,bottoms,operator)
    result={'schema':'osw.malvinas-bathymetry-screen.v1','status':'GEBCO_SCREEN_SCENARIOS_NOT_SHIP_BOTTOM_TRACK_QC',
            'adcp_raw_sha256':hashlib.sha256(raw).hexdigest(),'native_rows':count,'native_ensembles':len(samples),
            'gebco_tile_shape':[nlat,nlon],'gebco_elevation_url':elevation_url,'gebco_tid_url':tid_url,
            'gebco_elevation_response_sha256':hashlib.sha256(elevation_raw).hexdigest(),'gebco_tid_response_sha256':hashlib.sha256(tid_raw).hexdigest(),
            'point_tid_counts':dict(Counter(str(r['point_tid_code']) for r in bottoms)),
            'bottom_samples':bottoms,'scenarios':scenarios,'canonical_depth_references_added':0,
            'physical_current_bottoms_established':0,'volume_estimates':0,'full_goal_complete':False,
            'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [OPERATOR,'analysis/derive_malvinas_bathymetry_screen_v1.py','analysis/derive_malvinas_branch_core_scenarios_v1.py','analysis/audit_malvinas_adcp_depth_v1.py']}}
    output=ROOT/'malvinas-bathymetry-screen-v1';output.mkdir(exist_ok=True)
    for name,data in [('elevation.ascii',elevation_raw),('tid.ascii',tid_raw),('candidate.json',(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode('utf8'))]:(output/name).write_bytes(data)
    print(json.dumps([{'screen':r['screen_mode'],'pg':r['quality_pg_min_percent'],'km':r['uniform_window_km'],'cores':{k:v.get('sampled_maximum_depths_m') for k,v in (r['branches'] or {}).items()}} for r in scenarios]))


if __name__=='__main__':main()
