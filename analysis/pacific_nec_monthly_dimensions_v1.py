"""Bounded cloud-only OSCAR regional monthly dimension diagnostic.

Pure profile operators below may be tested without loading fields or engines.
"""
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
from urllib.parse import quote
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/pacific-nec-monthly-dimensions-request-v1.json'
PREFLIGHT = 'research/pacific-nec-monthly-dimensions-preflight-v1.json'
PROTOCOL = 'plans/pacific-nec-oscar-monthly-dimensions-protocol-v1.md'
OUT = ROOT / '.pytest_cache/pacific-nec-monthly-dimensions-v1'
SOURCE = ROOT / '.pytest_cache/pacific-nec-monthly-dimensions-source-v1'
DATASET = 'yearly_336c_0b32_9cd3'
BASE = 'https://oceanwatch.pifsc.noaa.gov/erddap'
BOUNDS = '[(2013-01-01T00:00:00Z):1:(2013-12-28T00:00:00Z)][(15)][(26):1:(4)][(130):1:(240)]'
QUERY = ','.join(v + BOUNDS for v in ('u', 'v'))
URLS = {'metadata.json': BASE + '/info/' + DATASET + '/index.json',
        'vectors.csv': BASE + '/griddap/' + DATASET + '.csv?' + quote(QUERY, safe='')}
MAIN = '19148702de6433253dbf412a0a28c0cb4f8e409e'


def require(value, message):
    if not value:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_bytes((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def read(path):return json.loads((ROOT / path).read_bytes())


def finite(value):return value is not None and math.isfinite(value)


def integrate(x, y):
    return math.fsum((b-a)*(p+q)/2 for a,b,p,q in zip(x,x[1:],y,y[1:]))


def interpolate(x, values, location):
    for a,b,va,vb in zip(x,x[1:],values,values[1:]):
        if a <= location <= b:return va + (vb-va)*(location-a)/(b-a)
    raise ValueError('Interpolation outside support')


def axis_profile(latitude, east, north, window=(8,18)):
    selected = [i for i,y in enumerate(latitude) if window[0]-1e-8 <= y <= window[1]+1e-8]
    x = [latitude[i] for i in selected]
    u = [east[i] for i in selected];v = [north[i] for i in selected]
    result = {'latitude': None, 'eastward_m_s': None, 'northward_m_s': None,
              'westward_share': None, 'mean_westward_m_s': None, 'reason': None}
    require(len(x)>=2 and abs(x[0]-window[0])<1e-7 and abs(x[-1]-window[1])<1e-7, 'Incomplete axis window')
    if not all(finite(a) and finite(b) for a,b in zip(u,v)):
        return dict(result, reason='missing_monthly_vector_in_window')
    weights = [max(-a,0) for a in u]
    west = integrate(x,weights);absolute = integrate(x,[abs(a) for a in u])
    if west <= 0 or absolute <= 0:return dict(result,reason='no_westward_flow')
    share = west/absolute;mean = west/(x[-1]-x[0])
    result.update(westward_share=share,mean_westward_m_s=mean)
    if share < .8:return dict(result,reason='westward_share_below_0.8')
    if mean < .02:return dict(result,reason='mean_westward_speed_below_0.02')
    center = integrate(x,[y*w for y,w in zip(x,weights)])/west
    center_u = interpolate(x,u,center);center_v = interpolate(x,v,center)
    result.update(latitude=center,eastward_m_s=center_u,northward_m_s=center_v)
    if center_u >= 0:return dict(result,latitude=None,reason='centroid_lies_in_nonwestward_flow')
    return result


def section_span(latitude, east, threshold=0):
    """Connected zonal-component span; missing/boundary/tie remain withheld."""
    window = [i for i,y in enumerate(latitude) if 8-1e-8 <= y <= 18+1e-8]
    empty = {'south_latitude':None,'north_latitude':None,'peak_latitude':None,
             'peak_westward_m_s':None,'threshold_m_s':threshold,'reason':None}
    if not all(finite(east[i]) for i in window):return dict(empty,reason='missing_peak_window')
    peak = max(-east[i] for i in window)
    candidates = [i for i in window if abs(-east[i]-peak)<=1e-12]
    if peak < .05:return dict(empty,reason='peak_below_0.05')
    if len(candidates)!=1:return dict(empty,reason='ambiguous_peak_tie')
    index=candidates[0];result=dict(empty,peak_latitude=latitude[index],peak_westward_m_s=peak)
    if peak<=threshold:return dict(result,reason='peak_not_above_threshold')
    edges=[];failures=[]
    for direction,side in ((-1,'south'),(1,'north')):
        previous=index;edge=None;reason=None
        for current in range(index+direction,len(latitude) if direction==1 else -1,direction):
            if not finite(east[current]):reason='missing_'+side+'_edge';break
            speed=-east[current]
            if speed<=threshold:
                old=-east[previous]
                edge=latitude[previous]+(threshold-old)*(latitude[current]-latitude[previous])/(speed-old)
                break
            previous=current
        if edge is None and reason is None:reason=side+'_halo_censored'
        edges.append(edge)
        if reason:failures.append(reason)
    result.update(south_latitude=edges[0],north_latitude=edges[1])
    if failures:return dict(result,reason=';'.join(failures))
    if edges[1]<=edges[0]:return dict(result,reason='nonpositive_span')
    return result


def axis_length(longitude, profiles, distance, maximum_jump=1):
    require(len(longitude)==len(profiles) and len(longitude)>=2
            and all(finite(x) for x in longitude)
            and all(0<b-a<180 for a,b in zip(longitude,longitude[1:])), 'Incomplete or ambiguous longitude support')
    reasons=Counter(p['reason'] for p in profiles if p['reason'])
    if reasons:return {'length_km':None,'reason':'rejected_columns','rejected_columns':dict(reasons),'maximum_jump_deg':None}
    jumps=[abs(b['latitude']-a['latitude']) for a,b in zip(profiles,profiles[1:])]
    jump=max(jumps)
    if jump>maximum_jump:return {'length_km':None,'reason':'adjacent_latitude_jump','rejected_columns':{},'maximum_jump_deg':jump}
    length=math.fsum(distance(x,a['latitude'],y,b['latitude']) for x,y,a,b in zip(longitude,longitude[1:],profiles,profiles[1:]))
    require(finite(length) and length>0,'Invalid geodesic length')
    return {'length_km':length,'reason':None,'rejected_columns':{},'maximum_jump_deg':jump}


def monthly_range(rows, key):
    values=[r[key] for r in rows if r[key] is not None]
    return {'minimum_km':min(values) if values else None,'maximum_km':max(values) if values else None,
            'valid_months':[r['month'] for r in rows if r[key] is not None],
            'missing_months':[r['month'] for r in rows if r[key] is None],
            'complete_2013_monthly_mean_regional_range':len(rows)==len(values)==12,
            'whole_current_annual_range':False,'physical_uncertainty':False,'climatology':False}


def guard():
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
            and os.environ.get('RUNNER_OS')=='Linux'
            and os.environ.get('OSW_PACIFIC_NEC_MONTHLY_DIMENSIONS_V1')=='1','Cloud-only field processing')
    require(os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
            and os.environ.get('GITHUB_EVENT_NAME')=='push'
            and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW','Wrong repository/event/ref')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        require(os.environ.get(key)=='1','Worker limit differs')
    request=read(REQUEST)
    require(request['schema']=='osw.pacific-nec-monthly-dimensions-request.v1' and request['execute'] is True
            and request['cloud_source_processing_permitted'] is True,'Request disabled or invalid')
    for key in ('local_source_processing_permitted','native_build_permitted','wasm_build_permitted',
                'browser_automation_permitted','installation_permitted','main_update_permitted'):
        require(request[key] is False,'Forbidden permission: '+key)
    require(request['max_cloud_jobs']==1 and request['max_local_heavy_jobs']==0,'Job bounds differ')
    require(sha((ROOT/PREFLIGHT).read_bytes())==request['preflight_sha256'],'Preflight differs')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(sha((ROOT/path).read_bytes())==pin,'Source differs: '+path)
    phase=read('research/current-gap-delivery-phase.json')
    require(phase['heavy_work_permitted'] is False,'Broad phase enabled')
    for path in pref['disabled_requests']:
        value=read(path);require(value.get('execute',value.get('execution_permitted')) is False,'Other request enabled')
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],text=True,timeout=55).strip()
    require(git('rev-parse','HEAD')==os.environ['GITHUB_SHA'] and not git('status','--porcelain'),'Checkout differs')
    require(git('ls-remote','origin','refs/heads/main').split()[0]==MAIN,'Main moved')
    require(git('ls-remote','origin','refs/heads/codex/current-measurement-gaps').split()[0]==os.environ['GITHUB_SHA'],'Working branch moved')
    for path,row in pref['installed_files'].items():
        require(git('rev-parse','HEAD:'+path)==row['git_blob_oid']
                and int(git('cat-file','-s',row['git_blob_oid']))==row['bytes'],'Installed artifact differs')


def download():
    SOURCE.mkdir(parents=True,exist_ok=False)
    files={}
    for name,url in URLS.items():
        limit=512000 if name=='metadata.json' else 256*1024*1024
        digest=hashlib.sha256();count=0
        with urllib.request.urlopen(url,timeout=180) as response, (SOURCE/name).open('xb') as output:
            require(response.status==200,'Provider response failed')
            for block in iter(lambda:response.read(1024*1024),b''):
                count+=len(block);require(count<=limit,'Provider payload exceeds bound')
                digest.update(block);output.write(block)
        files[name]={'url':url,'bytes':count,'sha256':digest.hexdigest()}
    return files


def parse_cube(metadata, path):
    import numpy as np
    attrs={(r[1],r[2]):r[4] for r in metadata['table']['rows'] if r[0]=='attribute'}
    for key,value in {('NC_GLOBAL','version'):'2017.0',('depth','actual_range'):'15.0, 15.0',
                      ('u','units'):'m s-1',('v','units'):'m s-1'}.items():
        require(attrs.get(key)==value,'Changed source version/layer/units')
    require('may be used and redistributed for free' in attrs.get(('NC_GLOBAL','license'),''),'Source license differs')
    sums=np.zeros((12,67,331,2));counts=np.zeros((12,67,331),dtype=np.uint16)
    times=[];seen=set();month_counts=[0]*12;previous=None;row_count=0
    with path.open(newline='',encoding='utf8') as stream:
        reader=csv.reader(stream)
        require(next(reader,None)==['time','depth','latitude','longitude','u','v'],'Changed source columns')
        require(next(reader,None)==['UTC','m','degrees_north','degrees_east','m s-1','m s-1'],'Changed source units')
        for row_count,row in enumerate(reader,1):
            require(row_count<=1596744 and len(row)==6,'Extra or malformed row')
            frame,offset=divmod(row_count-1,67*331);yi,xi=divmod(offset,331)
            if offset==0:
                instant=datetime.fromisoformat(row[0].replace('Z','+00:00'))
                require(instant.year==2013 and instant.utcoffset().total_seconds()==0
                        and row[0] not in seen,'Changed source timestamp')
                if previous:require(4*86400<=(instant-previous).total_seconds()<=6*86400,'Unexpected time gap')
                previous=instant;times.append(row[0]);seen.add(row[0]);month=instant.month-1;month_counts[month]+=1
            require(row[0]==times[frame],'Source row clock/order differs')
            depth,lat,lon,u,v=map(float,row[1:])
            require(depth==15 and abs(lat-(26-yi/3))<1e-7 and abs(lon-(130+xi/3))<1e-7,'Source grid differs')
            require(not math.isinf(u) and not math.isinf(v),'Infinite velocity')
            if math.isfinite(u) and math.isfinite(v):
                sums[month,yi,xi,0]+=u;sums[month,yi,xi,1]+=v;counts[month,yi,xi]+=1
    require(row_count==1596744 and len(times)==72 and all(5<=n<=7 for n in month_counts),'Incomplete year or cube')
    require((previous-datetime.fromisoformat(times[0].replace('Z','+00:00'))).days>=350,'Incomplete annual support')
    means=np.full_like(sums,np.nan)
    for month in range(12):
        mask=counts[month]==month_counts[month]
        means[month][mask]=sums[month][mask]/month_counts[month]
    return means[:,::-1,:,:],counts[:,::-1,:],times,month_counts,attrs


def diagnose(means,counts,times,month_counts):
    from pyproj import Geod
    geod=Geod(ellps='WGS84')
    def distance(x,a,y,b):return geod.inv(x,a,y,b)[2]/1000
    latitude=[4+i/3 for i in range(67)];longitude=[130+i/3 for i in range(331)]
    months=[];sensitivities=[];sections=[]
    for mi in range(12):
        for window in ((8,18),(7,19),(9,17)):
            profiles=[axis_profile(latitude,means[mi,:,xi,0].tolist(),means[mi,:,xi,1].tolist(),window) for xi in range(331)]
            for jump in (.5,1,2):
                value=axis_length(longitude,profiles,distance,jump)
                sensitivities.append(dict(value,month=mi+1,window_deg_north=list(window),maximum_allowed_jump_deg=jump))
                if window==(8,18) and jump==1:
                    months.append(dict(value,month=mi+1,sample_count=month_counts[mi],
                        source_times=[t for t in times if int(t[5:7])==mi+1],
                        length_rounded_km=100*math.floor(value['length_km']/100+.5) if value['length_km'] is not None else None,
                        axis=[{'longitude_east_unwrapped':x,**p} for x,p in zip(longitude,profiles)],
                        all_sample_counts_present=bool((counts[mi,12:43,:]==month_counts[mi]).all())))
        for lon in (137,180,220):
            xi=round((lon-130)*3);u=means[mi,:,xi,0].tolist()
            for threshold in (0,.025,.05):
                span=section_span(latitude,u,threshold)
                width=distance(lon,span['south_latitude'],lon,span['north_latitude']) if span['reason'] is None else None
                sections.append(dict(span,month=mi+1,longitude_east=lon,width_km=width,
                    width_rounded_km=10*math.floor(width/10+.5) if width is not None else None,
                    monthly_complete_samples=month_counts[mi],
                    profile=[{'latitude':y,'eastward_m_s':float(a) if finite(a) else None,
                              'northward_m_s':float(b) if finite(b) else None,'paired_sample_count':int(n),
                              'missing_samples':month_counts[mi]-int(n)}
                             for y,a,b,n in zip(latitude,means[mi,:,xi,0],means[mi,:,xi,1],counts[mi,:,xi])]))
    return {'months':months,'sensitivities':sensitivities,'section_spans':sections,
            'regional_length_range':monthly_range(months,'length_km'),
            'section_span_ranges':{str(lon):monthly_range([r for r in sections if r['longitude_east']==lon and r['threshold_m_s']==0],'width_km') for lon in (137,180,220)}}


def figure(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig=plt.figure(figsize=(13,9),layout='constrained');grid=fig.add_gridspec(2,2,height_ratios=[1.2,1])
    atlas=fig.add_subplot(grid[0,:]);lengths=fig.add_subplot(grid[1,0]);widths=fig.add_subplot(grid[1,1])
    colors=plt.cm.tab20(np.linspace(0,1,12))
    for row,color in zip(report['months'],colors):
        atlas.plot([p['longitude_east_unwrapped'] for p in row['axis']],
                   [p['latitude'] if p['reason'] is None else np.nan for p in row['axis']],
                   color=color,lw=1.4,label=f"2013-{row['month']:02d}"+(' (partial)' if row['reason'] else ''))
    atlas.set(xlim=(130,240),ylim=(7,19),ylabel='Latitude north',title='Windowed westward-speed centroid: 130E to 120W regional gates')
    atlas.set_xticks([130,150,180,210,240],['130E','150E','180','150W','120W']);atlas.grid(alpha=.2)
    atlas.legend(ncol=6,fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.07))
    valid=[r for r in report['months'] if r['length_km'] is not None]
    if valid:lengths.plot([r['month'] for r in report['months']],[r['length_km'] if r['length_km'] is not None else np.nan for r in report['months']],marker='o')
    for row in report['months']:
        if row['length_km'] is None:lengths.plot(row['month'],.04,'x',color='gray',transform=lengths.get_xaxis_transform())
    lengths.set(title='Regional length of monthly-mean diagnostic axis',ylabel='WGS84 km',xlabel='2013 month',xticks=range(1,13));lengths.grid(alpha=.2)
    for lon,color in zip((137,180,220),('tab:blue','tab:orange','tab:green')):
        rows=[r for r in report['section_spans'] if r['longitude_east']==lon and r['threshold_m_s']==0]
        widths.plot([r['month'] for r in rows],[r['width_km'] if r['width_km'] is not None else np.nan for r in rows],marker='o',color=color,label={137:'137E',180:'180',220:'140W'}[lon])
        for row in rows:
            if row['width_km'] is None:widths.plot(row['month'],.03+(lon==180)*.03+(lon==220)*.06,'x',color=color,transform=widths.get_xaxis_transform())
    widths.set(title='Connected westward zonal-component section spans',ylabel='Meridional WGS84 km',xlabel='2013 month',xticks=range(1,13));widths.grid(alpha=.2);widths.legend(fontsize=9)
    fig.suptitle('Pacific NEC | OSCAR2017.0 | nominal15m near-surface product | 2013\nOSW regional candidates, not whole-current dimensions or climatology',fontsize=13)
    fig.supxlabel('Crosses at panel bottom = withheld, not zero. Fixed meridian spans are not flow-normal widths. Numerical sensitivity is not physical uncertainty.',fontsize=10)
    fig.savefig(OUT/'diagnostic.png',dpi=150);fig.savefig(OUT/'diagnostic.svg');plt.close(fig)


def main():
    guard();OUT.mkdir(parents=True,exist_ok=False)
    files=download()
    write(OUT/'download.json',{'schema':'osw.pacific-nec-oscar-download-receipt.v1','query':QUERY,'files':files,
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
        'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'provider_fields_retained_on_cloud_only':True})
    means,counts,times,month_counts,attrs=parse_cube(json.loads((SOURCE/'metadata.json').read_bytes()),SOURCE/'vectors.csv')
    acquisition={'schema':'osw.pacific-nec-oscar-source-acquisition.v1','query':QUERY,'files':files,
        'times':times,'month_sample_counts':month_counts,'rows':1596744,'license':attrs[('NC_GLOBAL','license')],
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT']}
    write(SOURCE/'acquisition.json',acquisition);write(OUT/'acquisition.json',acquisition)
    report=diagnose(means,counts,times,month_counts)
    report.update(schema='osw.pacific-nec-monthly-regional-dimensions.v1',status='CANDIDATE_DIAGNOSTICS_REQUIRING_PHYSICAL_AND_VISUAL_REVIEW',
        entity_id='current:pacific-north-equatorial',source=acquisition,protocol_sha256=sha((ROOT/PROTOCOL).read_bytes()),
        operator_sha256=sha(Path(__file__).read_bytes()),whole_current_length_km=None,whole_current_width_km=None,
        whole_current_annual_ranges=None,physical_uncertainty=None,is_climatology=False,independent_observations_added=0,
        installed=False,main_updated=False,full_goal_complete=False)
    write(OUT/'diagnostic.json',report);figure(report)
    result={'schema':'osw.pacific-nec-monthly-dimensions-result.v1','status':'PASS_BOUNDED_SOURCE_DIAGNOSTIC_REVIEW_PENDING',
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'monthly_axis_cases':12,'qualified_regional_lengths':sum(r['length_km'] is not None for r in report['months']),
        'axis_sensitivity_cases':len(report['sensitivities']),'section_span_cases':len(report['section_spans']),
        'qualified_nominal_section_spans':sum(r['width_km'] is not None and r['threshold_m_s']==0 for r in report['section_spans']),
        'regional_length_range':report['regional_length_range'],'section_span_ranges':report['section_span_ranges'],
        'generated_files':{p.name:{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in OUT.iterdir()},
        'installed':False,'main_updated':False,'full_goal_complete':False}
    write(OUT/'result.json',result)
    print(json.dumps({k:result[k] for k in ('status','qualified_regional_lengths','qualified_nominal_section_spans','installed')}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True)
            write(OUT/'failure.json',{'status':'FAIL','error_type':type(error).__name__,'message':str(error)[:2000],
                                    'installed':False,'main_updated':False})
        raise
