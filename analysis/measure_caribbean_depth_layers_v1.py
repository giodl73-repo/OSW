"""Cloud-only, source-specific velocity-layer estimates with explicit censoring."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import io
import json
import math
import os
from pathlib import Path
import statistics
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RULES='research/caribbean-current-depth-operator-v1.json'


def finite(value):return value is not None and math.isfinite(value)


def measure_layer(depth,u,threshold,min_bins=3):
    """Find the contiguous threshold layer containing the strongest westward sample."""
    if len(depth)!=len(u) or not depth or threshold<=0 or min_bins<1:
        raise ValueError('Invalid depth profile or operator')
    if any(not finite(z) for z in depth) or any(b<=a for a,b in zip(depth,depth[1:])):
        raise ValueError('Depth coordinate must increase')
    candidates=[i for i,v in enumerate(u) if finite(v) and -v>=threshold]
    if not candidates:return {'status':'no_threshold_layer_detected'}
    core=min(candidates,key=lambda i:(u[i],depth[i]));lo=hi=core
    while lo>0 and finite(u[lo-1]) and -u[lo-1]>=threshold:lo-=1
    while hi+1<len(u) and finite(u[hi+1]) and -u[hi+1]>=threshold:hi+=1
    runs=sum(i==0 or not finite(u[i-1]) or -u[i-1]<threshold for i in candidates)
    if hi-lo+1<min_bins:
        return {'status':'strongest_component_insufficient_vertical_support','support_bins':hi-lo+1,'threshold_components':runs}

    def boundary(inside,outside,upper):
        if not 0<=outside<len(u):
            return {'status':'sampling_edge_censored','supported_depth_m':depth[inside],
                    'boundary_depth_operator':'<=' if upper else '>='}
        if not finite(u[outside]):
            return {'status':'missing_data_censored','supported_depth_m':depth[inside],
                    'boundary_depth_operator':'<=' if upper else '>='}
        z1,z2=depth[inside],depth[outside];v1,v2=-u[inside],-u[outside]
        estimate=z1+(threshold-v1)*(z2-z1)/(v2-v1)
        return {'status':'bracketed','bracket_m':sorted([z1,z2]),'linear_crossing_m':estimate}

    upper=boundary(lo,lo-1,True);lower=boundary(hi,hi+1,False)
    result={'status':'velocity_defined_layer','core_depth_m':depth[core],
            'core_westward_speed_m_s':-u[core],'support_bins':hi-lo+1,
            'threshold_components':runs,'upper':upper,'lower':lower,
            'layer_thickness_m':None,'layer_thickness_discretization_bracket_m':None}
    if upper['status']==lower['status']=='bracketed':
        result['layer_thickness_m']=lower['linear_crossing_m']-upper['linear_crossing_m']
        result['layer_thickness_discretization_bracket_m']=[
            lower['bracket_m'][0]-upper['bracket_m'][1],
            lower['bracket_m'][1]-upper['bracket_m'][0]]
    return result


def audit_time(start,end,reported,windows):
    if end<start:raise ValueError('Profile end precedes start')
    midpoint=start+(end-start)/2
    contained=[name for name,a,b in windows if start>=a and end<=b]
    return {'source_start':start.isoformat(),'source_end':end.isoformat(),
            'source_reported':reported.isoformat(),'derived_midpoint':midpoint.isoformat(),
            'reported_matches_end':abs((reported-end).total_seconds())<=1,
            'reported_matches_midpoint':abs((reported-midpoint).total_seconds())<=1,
            'contained_transect':contained[0] if len(contained)==1 else None}


class PinnedRangeReader(io.RawIOBase):
    """Seek over the public ZIP using bounded HTTP ranges; never read a full response."""
    def __init__(self,url,size):self.url=url;self.size=size;self.position=0;self.bytes_read=0;self.requests=0
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.position
    def seek(self,offset,whence=0):
        self.position=offset if whence==0 else self.position+offset if whence==1 else self.size+offset
        if self.position<0:raise ValueError('Negative ZIP seek')
        return self.position
    def read(self,n=-1):
        n=self.size-self.position if n<0 else min(n,self.size-self.position)
        if n<=0:return b''
        if n>1500000 or self.bytes_read+n>5000000 or self.requests>=20:raise ValueError('Range retrieval budget exceeded')
        end=self.position+n-1;expected=f'bytes {self.position}-{end}/{self.size}'
        request=urllib.request.Request(self.url,headers={'Range':f'bytes={self.position}-{end}'})
        with urllib.request.urlopen(request,timeout=60) as response:
            if response.status!=206 or response.headers.get('Content-Range')!=expected:
                raise ValueError('Server did not honor exact bounded range; body not read')
            raw=response.read(n+1)
        if len(raw)!=n:raise ValueError('Range size mismatch')
        self.position+=n;self.bytes_read+=n;self.requests+=1
        return raw


def read_verified_member(inventory):
    source=PinnedRangeReader(inventory['archive']['url'],inventory['archive']['bytes'])
    expected=inventory['selected_member']
    with zipfile.ZipFile(source) as archive:
        info=archive.getinfo(expected['path'])
        if info.file_size!=expected['bytes']:raise ValueError('Selected source size changed')
        raw=archive.read(info)
    if hashlib.sha256(raw).hexdigest()!=expected['sha256']:raise ValueError('Selected source checksum changed')
    return raw,{'http_range_requests':source.requests,'downloaded_bytes':source.bytes_read,
                'member_sha256':expected['sha256'],'whole_archive_md5_rechecked':False,
                'whole_archive_checksum_verified_by_run':41390932728}


def measure_source(raw,rules):
    from netCDF4 import Dataset,num2date
    windows=[(w['id'],datetime.fromisoformat(w['start']),datetime.fromisoformat(w['end'])) for w in rules['transect_windows']]
    with Dataset('verified_velocity.nc',memory=raw) as ds:
        if (len(ds.dimensions['depth']),len(ds.dimensions['time']))!=(100,486):raise ValueError('Pinned source shape changed')
        depth=ds['depth'][:].filled(float('nan')).tolist()
        if depth!=[5+10*i for i in range(100)]:raise ValueError('Pinned depth centers changed')
        def date(name,i):
            var=ds[name];v=num2date(var[i],units=var.units,calendar=var.calendar,only_use_cftime_datetimes=False)
            return datetime(v.year,v.month,v.day,v.hour,v.minute,v.second,v.microsecond)
        records=[];timing=[]
        for i in range(486):
            audit=audit_time(date('start_time',i),date('end_time',i),date('time',i),windows);timing.append(audit)
            if audit['contained_transect'] is None:continue
            lat=float(ds['latitude'][i]);lon=float(ds['longitude'][i])
            if not math.isfinite(lat) or not math.isfinite(lon):raise ValueError('Invalid source position')
            u=ds['u_grid'][:,i].filled(float('nan')).tolist()
            record={'source_profile_index':i,'latitude':lat,'longitude':lon,**audit,
                    'scenarios':{str(t):measure_layer(depth,u,t,rules['minimum_contiguous_bins']) for t in rules['threshold_speeds_m_s']}}
            records.append(record)
    summary={}
    for name,_,_ in windows:
        subset=[r for r in records if r['contained_transect']==name];scenarios={}
        for t in rules['threshold_speeds_m_s']:
            layers=[r['scenarios'][str(t)] for r in subset];measured=[r for r in layers if r['status']=='velocity_defined_layer']
            bracketed=[r['lower']['linear_crossing_m'] for r in measured if r['lower']['status']=='bracketed']
            scenarios[str(t)]={'profiles':len(layers),'status_counts':dict(Counter(r['status'] for r in layers)),
                'lower_boundary_status_counts':dict(Counter(r['lower']['status'] for r in measured)),
                'bracketed_lower_depth_summary_m':None if not bracketed else {'min':min(bracketed),'median':statistics.median(bracketed),'max':max(bracketed)},
                'fully_bracketed_layers':sum(r['layer_thickness_m'] is not None for r in measured)}
        summary[name]=scenarios
    return {'profiles':records,'summary':summary,'timestamp_audit':{'profiles_checked':len(timing),
            'reported_matches_end':sum(r['reported_matches_end'] for r in timing),
            'reported_matches_midpoint':sum(r['reported_matches_midpoint'] for r in timing),
            'profiles_wholly_contained_in_selected_windows':len(records),
            'excluded_outside_or_crossing_windows':486-len(records)},
            'unit_source':'article_and_archived_author_transport_code_not_CF_attributes'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS')!='true':raise RuntimeError('Field calculations run only in cloud')
    rules=json.loads((ROOT/RULES).read_bytes())
    inventory_path=ROOT/'research/caribbean-current-depth-source-inventory-result-v1.json'
    if hashlib.sha256(inventory_path.read_bytes()).hexdigest()!=rules['inventory_sha256']:raise ValueError('Source inventory pin changed')
    inventory=json.loads(inventory_path.read_bytes());raw,acquisition=read_verified_member(inventory)
    result={'schema':'osw.caribbean-velocity-defined-depth-layers.v1','status':'PASS_CANDIDATE_VELOCITY_LAYERS_COMPUTED',
            'source_commit':os.environ['GITHUB_SHA'],'operator_file':RULES,
            'operator_sha256':hashlib.sha256((ROOT/RULES).read_bytes()).hexdigest(),
            'source_acquisition':acquisition,**measure_source(raw,rules),
            'interpretation':'Local strongest westward threshold layers across two sequential transects; may include mesoscale flow. Not the unique physical boundary of the entire named Caribbean Current.',
            'discretization_brackets_are_confidence_intervals':False,
            'scientific_admission_status':'candidate_diagnostics_pending_source_review',
            'whole_route_profile_established':False,'annual_extrema_eligible':False,
            'volume_eligible':False,'runtime_changed':False,'full_goal_complete':False}
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'acquisition':acquisition,'timestamp_audit':result['timestamp_audit'],'summary':result['summary']}))


if __name__=='__main__':main()
