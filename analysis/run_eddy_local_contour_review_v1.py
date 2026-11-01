"""Cloud-only local-level review using the frozen contour geometry operator."""
import hashlib
import json
import math
import os
from pathlib import Path
import time
import urllib.request

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
import netCDF4
import numpy as np

from eddy_altimetry_contours_v1 import GEOD, contour_candidates, demean

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/eddy-local-contour-review-request-v1.json'
OUT = ROOT / '.pytest_cache/eddy-local-contour-review-v1'


def main():
    assert os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true'
    assert os.environ.get('GITHUB_REPOSITORY') == 'giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF') == 'refs/heads/codex/current-measurement-gaps'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    raw_request = (ROOT / REQUEST).read_bytes(); r = json.loads(raw_request)
    assert r['schema'] == 'osw.eddy-local-contour-review-request.v1' and r['execute'] is True
    assert r['maximum_cloud_jobs'] == 1 and r['maximum_local_heavy_jobs'] == 0
    assert all(r[k] is False for k in ['measurement_admission_permitted', 'physical_identity_join_permitted', 'runtime_installation_permitted', 'native_build_permitted', 'wasm_build_permitted'])
    for path, pin in r['input_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == pin, path
    assert r['date'] == '1997-03-24' and r['source_center_lon_lat'] == [-88.7, 28]
    assert r['levels_m'] == [round(i / 100, 2) for i in range(-10, 31)]
    assert r['minimum_area_review_screen_km2'] == 0 and r['maximum_peak_distance_km'] == 150
    source = r['source']
    assert source == {'url':'https://data.griidc.org/api/file/download/947138','bytes':757416604,'sha256':'526fb93bbb0880a4c6ab9390527cef8ecc4706c7c08d0a075ccfd02de922b527'}
    positions = json.loads((ROOT / r['position_reference_file']).read_bytes())
    position = next(v for v in positions['records'] if v['id'] == r['position_reference_id'])
    assert position['observation_date'] == r['date'] and position['entity_id'] == 'eddy:horizon:loop-26-primary'
    assert position['navigation_candidate']['longitude_deg'] == -88.7 and position['navigation_candidate']['latitude_deg'] == 28
    OUT.mkdir(parents=True, exist_ok=True); original = OUT / 'source.nc'; started = time.monotonic()
    result = {'schema':'osw.eddy-local-contour-review-result.v1','status':'FAILED','source_commit':os.environ['GITHUB_SHA'],
        'request_sha256':hashlib.sha256(raw_request).hexdigest(),'source':source,'date':r['date'],
        'source_center_lon_lat':r['source_center_lon_lat'],'scenarios':[], 'measurements_admitted':0,
        'physical_identity_joins_created':0,'operator_changed':False,'runtime_changed':False}
    try:
        count = 0; digest = hashlib.sha256()
        with urllib.request.urlopen(source['url'], timeout=45) as response, original.open('wb') as target:
            while True:
                assert time.monotonic() - started < 480
                chunk = response.read(min(1048576, source['bytes'] + 1 - count))
                if not chunk: break
                count += len(chunk); assert count <= source['bytes']; digest.update(chunk); target.write(chunk)
        assert count == source['bytes'] and digest.hexdigest() == source['sha256']
        fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
        with netCDF4.Dataset(original) as data:
            assert data['adt'].dimensions == ('time','latitude','longitude') and data['adt'].units == 'm'
            assert data.getncattr('subset:datasetId') == r['source_product_version']
            lon, lat = np.asarray(data['longitude'][:]), np.asarray(data['latitude'][:])
            dates = [str(v)[:10] for v in netCDF4.num2date(data['time'][:], data['time'].units, calendar=data['time'].calendar)]
            assert data['adt'].shape == (9861,120,160)
            index = dates.index(r['date']); field = data['adt'][index,:,:]; result['source_time_index'] = index
            gx, gy = np.meshgrid(lon, lat); grid = np.column_stack([gx.ravel(), gy.ravel()])
            for weighted, ax in zip([False,True], axes):
                z, mean, samples = demean(lon, lat, field, weighted)
                ix, iy = int(np.argmin(abs(lon + 88.7))), int(np.argmin(abs(lat - 28)))
                scenario = {'mean_method':'cos_latitude_weighted' if weighted else 'finite_gridpoint_arithmetic',
                    'removed_spatial_mean_m':mean,'demeaning_ocean_samples':samples,
                    'nearest_gridpoint_to_reported_center':{'lon_lat':[float(lon[ix]),float(lat[iy])],
                        'demeaned_adt_m':float(z[iy,ix]) if np.isfinite(z[iy,ix]) else None}, 'levels':[]}
                for level in r['levels_m']:
                    candidates, rejected = contour_candidates(lon,lat,z,level,minimum_area_km2=0)
                    selected = []
                    for metrics, points in candidates:
                        peak = metrics['peak_grid_position_lon_lat']
                        distance = GEOD.inv(-88.7,28,*peak)[2] / 1000
                        path = PlotPath(points); hits = path.contains_points(r['diagnostic_probes']).tolist()
                        if distance > 150 and not any(hits): continue
                        inside = path.contains_points(grid).reshape(z.shape)
                        selected.append({**metrics,'peak_distance_from_reported_center_km':distance,
                            'diagnostic_probe_hits':hits,'interior_finite_gridpoints':int(np.sum(inside & np.isfinite(z)))})
                        ax.plot(points[:,0],points[:,1],lw=.7,alpha=.7)
                    scenario['levels'].append({'level_m':level,'near_center_candidates':selected,'rejected_contours':rejected})
                result['scenarios'].append(scenario)
                ax.pcolormesh(lon,lat,~np.isfinite(z),cmap='Greys',vmin=0,vmax=1,shading='nearest',alpha=.25)
                ax.scatter([-88.7],[28],color='#a00053',marker='+',s=70,zorder=5)
                ax.set(xlim=(-92,-85),ylim=(25,30.5),title=scenario['mean_method'],xlabel='Longitude',ylabel='Latitude')
                ax.set_aspect(1 / math.cos(math.radians(28))); ax.grid(alpha=.15)
        fig.suptitle('1997-03-24: local closed-contour diagnostics, no named-eddy dimensions\nFixed -0.10..+0.30 m scan at 0.01 m spacing; no area screen; source center marked +')
        fig.savefig(OUT/'local-contour-overview.png',dpi=125); plt.close(fig)
        result.update(status='PASS_LOCAL_CONTOUR_REVIEW_NO_ADMISSION',
            scope='All retained loops are unadmitted diagnostics. Zero area screen exposes sub-resolution/small loops for review, not measured eddies. Local level scan is distinct from the prior fixed-level 4000 km2 pilot. Do not pool nested contours into a physical uncertainty or seasonal range.')
    except Exception as error:
        result['error'] = {'type':type(error).__name__,'message':str(error)[:1000]}; raise
    finally:
        original.unlink(missing_ok=True)
        result['elapsed_seconds'] = round(time.monotonic()-started,2)
        result['images'] = {p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.glob('*.png')}
        encoded = (json.dumps(result,indent=2,allow_nan=False)+'\n').encode(); assert len(encoded)<1000000
        (OUT/'result.json').write_bytes(encoded)
    print(json.dumps({'status':result['status'],'measurements_admitted':0}))


if __name__ == '__main__': main()
