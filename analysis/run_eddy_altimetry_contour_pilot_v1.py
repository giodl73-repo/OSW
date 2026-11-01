"""Cloud-only sparse-day diagnostic, never writes measurement/runtime data."""
import hashlib
import json
import os
import pathlib
import time
import urllib.request

import contourpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
import netCDF4
import numpy as np

from eddy_altimetry_contours_v1 import contour_candidates, demean

REQUEST = pathlib.Path('research/eddy-altimetry-contour-pilot-request-v1.json')
OUT = pathlib.Path('.pytest_cache/eddy-altimetry-contour-pilot-v1')


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true', 'Ocean field processing is cloud-only'
    assert os.environ.get('OSW_EDDY_CONTOUR_PILOT_V1') == '1'
    raw_request = REQUEST.read_bytes(); request = json.loads(raw_request)
    assert request['schema'] == 'osw.eddy-altimetry-contour-pilot-request.v1' and request['execute'] is True
    assert request['maximum_cloud_jobs'] == 1 and request['maximum_local_heavy_jobs'] == 0
    assert request['measurement_admission_permitted'] is False and request['physical_identity_join_permitted'] is False
    assert request['runtime_installation_permitted'] is False and request['native_build_permitted'] is False and request['wasm_build_permitted'] is False
    assert 1 <= len(request['dates']) <= 12 and len(set(request['dates'])) == len(request['dates'])
    for path, expected in request['input_sha256'].items():
        assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest() == expected, path
    source = request['source']
    assert source['url'] == 'https://data.griidc.org/api/file/download/947138'
    assert source['bytes'] == 757416604 and source['sha256'] == '526fb93bbb0880a4c6ab9390527cef8ecc4706c7c08d0a075ccfd02de922b527'
    OUT.mkdir(parents=True, exist_ok=True)
    original = OUT / 'source.nc'
    started = time.monotonic()
    result = {'schema': 'osw.eddy-altimetry-contour-pilot-result.v1', 'status': 'FAILED',
        'source_commit': os.environ['GITHUB_SHA'],
        'request_sha256': hashlib.sha256(raw_request).hexdigest(),
        'source': source, 'days': [], 'measurements_admitted': 0, 'physical_identity_joins_created': 0,
        'scope': 'Unnamed per-day candidate diagnostics. No tracked current/eddy register, runtime, release, state geometry or index modified.'}
    try:
        digest = hashlib.sha256(); count = 0
        with urllib.request.urlopen(urllib.request.Request(source['url'], headers={'User-Agent': 'OSW sparse-day eddy contour pilot'}), timeout=45) as response, original.open('wb') as target:
            while True:
                assert time.monotonic() - started < 480
                chunk = response.read(min(1048576, source['bytes'] + 1 - count))
                if not chunk: break
                count += len(chunk); assert count <= source['bytes']
                digest.update(chunk); target.write(chunk)
        assert count == source['bytes'] and digest.hexdigest() == source['sha256']
        fig, axes = plt.subplots(4, 3, figsize=(15, 14), constrained_layout=True)
        with netCDF4.Dataset(original) as data:
            assert data['adt'].dimensions == ('time', 'latitude', 'longitude') and data['adt'].units == 'm'
            assert data.getncattr('subset:datasetId') == request['source_product_version']
            lon, lat = np.asarray(data['longitude'][:]), np.asarray(data['latitude'][:])
            times = data['time'][:]
            dates = [str(v)[:10] for v in netCDF4.num2date(times, data['time'].units, calendar=data['time'].calendar)]
            assert len(dates) == 9861 and data['adt'].shape == (9861, 120, 160)
            for day, ax in zip(request['dates'], axes.flat):
                index = dates.index(day)
                raw = data['adt'][index, :, :]  # One daily slice, never the time-volume.
                record = {'date': day, 'source_time_index': index, 'scenarios': []}
                for weighted in [False, True]:
                    z, mean, count = demean(lon, lat, raw, weighted)
                    if not weighted:
                        context_lines = contourpy.contour_generator(x=lon, y=lat, z=np.ma.masked_invalid(z),
                            name='serial', line_type='SeparateCode', corner_mask=False, quad_as_tri=False).lines(.17)[0]
                        for points in context_lines:
                            ax.plot(points[:, 0], points[:, 1], color='#75808b', lw=.65, ls='--', alpha=.8)
                    for level in [.15, .17, .19]:
                        candidates, rejected = contour_candidates(lon, lat, z, level)
                        controls = request.get('review_control_points', {}).get(day, {})
                        for row, points in candidates:
                            row['review_control_point_hits'] = {key: Path(points).contains_points(value).tolist()
                                                               for key, value in controls.items()}
                        record['scenarios'].append({'mean_method': 'cos_latitude_weighted' if weighted else 'finite_gridpoint_arithmetic',
                            'removed_spatial_mean_m': mean, 'demeaning_ocean_samples': count,
                            'demeaning_box_degrees': [-99, 17, -80, 31], 'level_m': level,
                            'candidates': [row for row, _ in candidates], 'rejected_contours': rejected})
                        if not weighted:
                            for row, points in candidates:
                                ax.plot(points[:, 0], points[:, 1], color={.15:'#9ba7b4', .17:'#006d77', .19:'#bd8c56'}[level],
                                    lw=1.6 if level == .17 else .7)
                                if level == .17:
                                    p = row['peak_grid_position_lon_lat']
                                    ax.text(*p, row['candidate_id'], fontsize=7, color='#003840')
                    if not weighted:
                        # Only the land/missing mask and extracted contours enter the retained image.
                        ax.pcolormesh(lon, lat, ~np.isfinite(z), cmap='Greys', vmin=0, vmax=1, shading='nearest', alpha=.22)
                        for control_points in request.get('review_control_points', {}).get(day, {}).values():
                            control = np.asarray(control_points)
                            ax.scatter(control[:, 0], control[:, 1], color='#a00053', s=6, marker='+', zorder=5)
                primary = next(s for s in record['scenarios'] if s['mean_method'] == 'finite_gridpoint_arithmetic' and s['level_m'] == .17)
                ax.set(xlim=(-99, -79), ylim=(17, 32), title=f"{day} — {len(primary['candidates'])} eligible closed loops", xlabel='Longitude', ylabel='Latitude')
                ax.set_aspect(1 / np.cos(np.deg2rad(25)))
                ax.grid(alpha=.15)
                result['days'].append(record)
        for ax in list(axes.flat)[len(request['dates']):]: ax.set_visible(False)
        fig.suptitle('Unnamed daily contour candidates — no named-eddy assignment\nArithmetic Gulf demean; teal 0.17 m / grey 0.15 m / brown 0.19 m; area screen ≥4,000 km²\nDashed: all 0.17 m paths for context, including open/rejected outlines; labels restart in every panel', fontsize=12)
        fig.savefig(OUT / 'candidate-overview.png', dpi=125); plt.close(fig)
        result['status'] = 'PASS_EXPLORATORY_CONTOUR_PILOT_NO_ADMISSION'
        result['method'] = {
            'sphere_radius_km': 6371, 'minimum_review_area_km2': 4000,
            'closure': 'ContourPy SeparateCode CLOSEPOLY plus identical first/last coordinates; never snap or bridge.',
            'missing_data': 'corner_mask=False; reject any missing grid-point interior and any domain-clipped contour.',
            'orientation': 'Positive signed spherical area retains high-interior contours; low-interior loops excluded.',
            'mean': 'Finite ocean gridpoints within longitude -99..-80 and latitude 17..31; arithmetic primary, cosine latitude weighting diagnostic alternative.',
            'sensitivity': 'Independent 0.15/0.17/0.19 m contours for each of two means. IDs are local to each date/scenario, never a cross-scenario or temporal identity.',
            'metric_scope': 'Enclosed spherical contour area, planar area-equivalent diameter, geographic bounding arcs and perimeter. Bounding arcs are not along-flow length, minimum width or principal axes.',
            'unquantified': ['Mapping and MDT errors', 'Effective feature resolution', 'Temporal aliasing', 'Physical front representativeness', 'Cross-scenario loop correspondence'],
        }
    except Exception as error:
        result['error'] = {'type': type(error).__name__, 'message': str(error)[:1200]}
        raise
    finally:
        original.unlink(missing_ok=True)
        result['elapsed_seconds'] = round(time.monotonic() - started, 2)
        images = {}
        for path in OUT.glob('*.png'):
            image = path.read_bytes(); images[path.name] = {'bytes': len(image), 'sha256': hashlib.sha256(image).hexdigest()}
        result['images'] = images
        encoded = (json.dumps(result, indent=2, allow_nan=False) + '\n').encode()
        assert len(encoded) < 1000000
        (OUT / 'result.json').write_bytes(encoded)
    print(json.dumps({'status': result['status'], 'days': len(result['days']), 'measurements_admitted': 0}))


if __name__ == '__main__': main()
