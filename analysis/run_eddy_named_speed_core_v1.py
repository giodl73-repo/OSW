"""Cloud-only speed-contour development and transfer diagnostics."""
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import netCDF4
import numpy as np

from eddy_speed_contours_v1 import ReviewRejected, compare_steps, speed_profile

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/eddy-named-speed-core-request-v1.json'
OUT=ROOT/'.pytest_cache/eddy-named-speed-core-v1'


def main():
    assert os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    raw_request=(ROOT/REQUEST).read_bytes();r=json.loads(raw_request)
    assert r['schema']=='osw.eddy-named-speed-core-request.v1' and r['execute'] is True
    assert r['maximum_cloud_jobs']==1 and r['maximum_local_heavy_jobs']==0
    assert all(r[k] is False for k in ['measurement_admission_permitted','physical_identity_join_permitted','runtime_installation_permitted','native_build_permitted','wasm_build_permitted'])
    for p,pin in r['input_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pin,p
    book=json.loads((ROOT/r['casebook_file']).read_bytes())
    assert book['schema']=='osw.eddy-speed-core-source-cases.v1'
    assert r['cases']==book['cases'] and 1<=len(r['cases'])<=6
    assert len({c['case_id'] for c in r['cases']})==len(r['cases'])
    for case in r['cases']:
        assert case['source_position_file'] in r['input_sha256']
        positions=json.loads((ROOT/case['source_position_file']).read_bytes())
        matches=[p for p in positions['records'] if p['id']==case['source_position_id']]
        assert len(matches)==1
        p=matches[0];n=p['navigation_candidate']
        assert p['entity_id']==case['owner_id'] and p['source_name']==case['source_name']
        assert p['observation_date']==case['date'] and p['source_point_role']==case['source_point_role']
        assert [n['longitude_deg'],n['latitude_deg']]==case['source_point']
        assert p['physical_crosswalk_verified'] is False and p['size_inferred'] is False
    source=r['source'];assert source=={'url':'https://data.griidc.org/api/file/download/947138','bytes':757416604,'sha256':'526fb93bbb0880a4c6ab9390527cef8ecc4706c7c08d0a075ccfd02de922b527'}
    OUT.mkdir(parents=True,exist_ok=True);original=OUT/'source.nc';started=time.monotonic()
    result={'schema':'osw.eddy-speed-contour-pilot-result.v1','status':'FAILED','source_commit':os.environ['GITHUB_SHA'],
        'request_sha256':hashlib.sha256(raw_request).hexdigest(),'source':source,'cases':[],
        'measurements_admitted':0,'physical_identity_joins_created':0,'runtime_changed':False}
    try:
        count=0;digest=hashlib.sha256()
        request=urllib.request.Request(source['url'],headers={'User-Agent':'OSW named source-case speed-contour research'})
        with urllib.request.urlopen(request,timeout=45) as response,original.open('wb') as target:
            while True:
                assert time.monotonic()-started<480
                chunk=response.read(min(1048576,source['bytes']+1-count))
                if not chunk:break
                count+=len(chunk);assert count<=source['bytes'];digest.update(chunk);target.write(chunk)
        assert count==source['bytes'] and digest.hexdigest()==source['sha256']
        with netCDF4.Dataset(original) as data:
            assert data['adt'].dimensions==('time','latitude','longitude') and data['adt'].units=='m'
            assert data['adt'].shape==(9861,120,160) and data.getncattr('subset:datasetId')==r['source_product_version']
            lon,lat=np.asarray(data['longitude'][:]),np.asarray(data['latitude'][:])
            dates=[str(v)[:10] for v in netCDF4.num2date(data['time'][:],data['time'].units,calendar=data['time'].calendar)]
            for case in r['cases']:
                index=dates.index(case['date']);field=np.ma.filled(data['adt'][index,:,:],np.nan)
                review={**case,'source_time_index':index,'input_height_reference':'native_daily_ADT_m_not_demeaned','sweeps':[]}
                fig,(map_ax,profile_ax)=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
                map_ax.pcolormesh(lon,lat,~np.isfinite(field),cmap='Greys',vmin=0,vmax=1,shading='nearest',alpha=.25)
                for step,color in [(.005,'#d08c36'),(.0025,'#006d77')]:
                    try:sweep,points=speed_profile(lon,lat,field,case['source_point'],step_m=step)
                    except ReviewRejected as error:
                        sweep={'status':'REJECTED','reason':str(error),'level_step_m':step,'profile':[]};points=None
                    review['sweeps'].append(sweep)
                    if sweep['profile']:
                        profile_ax.plot([v['speed_equivalent_radius_km'] for v in sweep['profile']],
                            [v['mean_geostrophic_speed_m_s'] for v in sweep['profile']],color=color,label=f'{step:g} m step')
                    if points is not None:
                        map_ax.plot(points[:,0],points[:,1],color=color,label=f'{step:g} m speed contour')
                        selected=sweep['selected'];profile_ax.scatter([selected['speed_equivalent_radius_km']],[selected['mean_geostrophic_speed_m_s']],color=color)
                    if sweep.get('peak'):map_ax.scatter(*sweep['peak']['lon_lat'],marker='*',s=50,color=color)
                review['convergence']=compare_steps(*review['sweeps']);result['cases'].append(review)
                x,y=case['source_point'];map_ax.scatter([x],[y],marker='+',s=80,color='#a00053',label='Source point, not physical join')
                map_ax.set(xlim=(x-3,x+3),ylim=(y-2.5,y+2.5),xlabel='Longitude',ylabel='Latitude');map_ax.grid(alpha=.15)
                map_ax.legend(fontsize=7);profile_ax.set(xlabel='Equivalent contour radius (km)',ylabel='Circum-averaged geostrophic speed (m/s)')
                if any(s['profile'] for s in review['sweeps']):profile_ax.legend(fontsize=8)
                profile_ax.grid(alpha=.15);fig.suptitle(f"{case['source_name']} {case['date']}: source-case diagnostic, no measurement admission\n{review['convergence']['status']}")
                fig.savefig(OUT/(case['source_name'].lower()+'-'+case['date']+'-speed-contour.png'),dpi=125);plt.close(fig)
        result['status']='PASS_EXECUTION_SPEED_CONTOUR_REVIEW_NO_ADMISSION'
    except Exception as error:
        result['error']={'type':type(error).__name__,'message':str(error)[:1000]};raise
    finally:
        original.unlink(missing_ok=True);result['elapsed_seconds']=round(time.monotonic()-started,2)
        result['images']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.glob('*.png')}
        encoded=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode();assert len(encoded)<1500000
        (OUT/'result.json').write_bytes(encoded)
    print(json.dumps({'status':result['status'],'case_convergence':[c['convergence']['status'] for c in result['cases']]}))


if __name__=='__main__':main()
