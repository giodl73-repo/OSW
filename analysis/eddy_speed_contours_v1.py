"""Development speed-core diagnostics. No physical identity or release admission."""
import math

import numpy as np
from matplotlib.path import Path

from eddy_altimetry_contours_v1 import GEOD, RADIUS_M, contour_candidates

GRAVITY_M_S2 = 9.80665
OMEGA_RAD_S = 7.292115e-5
METHOD = 'osw_native_grid_geostrophic_speed_contour_v1'


class ReviewRejected(ValueError):
    pass


def geostrophic_velocity(lon, lat, height):
    lon, lat = np.asarray(lon), np.asarray(lat)
    z = np.ma.filled(np.ma.asarray(height, dtype=float), np.nan)
    assert z.shape == (len(lat), len(lon)) and min(z.shape) >= 5
    assert np.all(np.diff(lon) > 0) and np.all(np.diff(lat) > 0)
    assert np.all((lat > 5) & (lat < 75)), 'This northern-hemisphere pilot excludes small Coriolis parameters'
    radians = np.deg2rad(lat)
    north_gradient = np.gradient(z, radians * RADIUS_M, axis=0, edge_order=2)
    east_gradient = np.gradient(z, np.deg2rad(lon) * RADIUS_M, axis=1, edge_order=2) / np.cos(radians[:, None])
    supported = np.zeros(z.shape, dtype=bool)
    supported[1:-1, 1:-1] = (np.isfinite(z[1:-1, 1:-1]) & np.isfinite(z[:-2, 1:-1])
        & np.isfinite(z[2:, 1:-1]) & np.isfinite(z[1:-1, :-2]) & np.isfinite(z[1:-1, 2:]))
    factor = GRAVITY_M_S2 / (2 * OMEGA_RAD_S * np.sin(radians[:, None]))
    return np.where(supported, -factor * north_gradient, np.nan), np.where(supported, factor * east_gradient, np.nan)


def maxima_masks(height):
    z = np.asarray(height, dtype=float)
    middle = z[1:-1, 1:-1]
    neighbors = [z[1+dy:z.shape[0]-1+dy, 1+dx:z.shape[1]-1+dx]
        for dy in [-1, 0, 1] for dx in [-1, 0, 1] if dx or dy]
    finite = np.isfinite(middle) & np.logical_and.reduce([np.isfinite(v) for v in neighbors])
    strict = finite & np.logical_and.reduce([middle > v for v in neighbors])
    plateau = finite & np.logical_and.reduce([middle >= v for v in neighbors]) & ~strict
    plateau &= np.logical_or.reduce([middle > v for v in neighbors])
    full_strict = np.zeros(z.shape, dtype=bool); full_plateau = full_strict.copy()
    full_strict[1:-1, 1:-1] = strict; full_plateau[1:-1, 1:-1] = plateau
    return full_strict, full_plateau


def select_peak(lon, lat, height, source_point, search_radius_km=150):
    strict, plateau = maxima_masks(height)
    def candidates(mask):
        rows = []
        for iy, ix in np.argwhere(mask):
            distance = GEOD.inv(*source_point, float(lon[ix]), float(lat[iy]))[2] / 1000
            if distance <= search_radius_km:
                rows.append({'ix':int(ix), 'iy':int(iy), 'lon_lat':[float(lon[ix]),float(lat[iy])],
                    'height_m':float(height[iy,ix]), 'distance_from_source_point_km':float(distance)})
        return rows
    if candidates(plateau): raise ReviewRejected('plateau_or_tied_peak_in_search_region')
    peaks = candidates(strict)
    if not peaks: raise ReviewRejected('no_strict_peak_in_search_region')
    if len(peaks) != 1: raise ReviewRejected('multiple_peaks_in_search_region')
    return peaks[0], strict, plateau


def contour_mean_speed(lon, lat, u, v, points):
    points = np.asarray(points)
    assert np.array_equal(points[0], points[-1]) and len(points) >= 4
    midpoints = (points[:-1] + points[1:]) / 2
    ix = np.searchsorted(lon, midpoints[:,0], side='right') - 1
    iy = np.searchsorted(lat, midpoints[:,1], side='right') - 1
    if np.any((ix < 0) | (ix >= len(lon)-1) | (iy < 0) | (iy >= len(lat)-1)):
        raise ReviewRejected('velocity_interpolation_outside_grid')
    tx = (midpoints[:,0] - lon[ix]) / (lon[ix+1] - lon[ix])
    ty = (midpoints[:,1] - lat[iy]) / (lat[iy+1] - lat[iy])
    def interpolate(values):
        corners = [values[iy,ix], values[iy,ix+1], values[iy+1,ix], values[iy+1,ix+1]]
        if not all(np.all(np.isfinite(c)) for c in corners): raise ReviewRejected('missing_velocity_support')
        return corners[0]*(1-tx)*(1-ty) + corners[1]*tx*(1-ty) + corners[2]*(1-tx)*ty + corners[3]*tx*ty
    speed = np.hypot(interpolate(u), interpolate(v))
    lengths = np.asarray(GEOD.inv(points[:-1,0], points[:-1,1], points[1:,0], points[1:,1])[2])
    if not np.all(np.isfinite(lengths)) or lengths.sum() <= 0: raise ReviewRejected('invalid_contour_length')
    return float(np.sum(speed * lengths) / np.sum(lengths))


def speed_profile(lon, lat, height, source_point, step_m=.005, maximum_drop_m=.60,
                  minimum_interior_samples=12, search_radius_km=150):
    lon, lat = np.asarray(lon), np.asarray(lat)
    z = np.ma.filled(np.ma.asarray(height, dtype=float), np.nan)
    assert 0 < step_m < maximum_drop_m and minimum_interior_samples >= 1
    assert math.isclose(maximum_drop_m / step_m, round(maximum_drop_m / step_m), abs_tol=1e-9)
    u, v = geostrophic_velocity(lon,lat,z)
    peak, strict, plateau = select_peak(lon,lat,z,source_point,search_radius_km)
    gx, gy = np.meshgrid(lon,lat); grid = np.column_stack([gx.ravel(),gy.ravel()])
    maxima_positions = grid[strict.ravel()]; plateau_positions = grid[plateau.ravel()]
    profile = []; exclusions = {}; paths = []
    def exclude(reason): exclusions[reason] = exclusions.get(reason,0) + 1
    for index in range(1, round(maximum_drop_m / step_m)+1):
        drop = index * step_m; level = peak['height_m'] - drop
        loops, _ = contour_candidates(lon,lat,z,level,minimum_area_km2=0)
        enclosing = [(m,p) for m,p in loops if Path(p).contains_point(peak['lon_lat'])]
        if len(enclosing) != 1: exclude('no_unique_closed_contour_enclosing_peak'); continue
        metrics, points = enclosing[0]; path = Path(points)
        if int(np.sum(path.contains_points(maxima_positions))) != 1:
            exclude('multiple_enclosed_maxima'); continue
        if len(plateau_positions) and np.any(path.contains_points(plateau_positions)):
            exclude('enclosed_plateau_or_tied_peak'); continue
        count = int(np.sum(path.contains_points(grid)))
        if count < minimum_interior_samples: exclude('insufficient_sampled_interior'); continue
        try: speed = contour_mean_speed(lon,lat,u,v,points)
        except ReviewRejected as error: exclude(str(error)); continue
        profile.append({**metrics,'drop_from_peak_m':drop,'contour_height_m':level,
            'interior_finite_gridpoints':count,'enclosed_strict_maxima':1,
            'mean_geostrophic_speed_m_s':speed,'speed_equivalent_radius_km':math.sqrt(metrics['area_km2']/math.pi)})
        paths.append(points)
    result = {'method':METHOD,'peak':peak,'level_step_m':step_m,'maximum_drop_m':maximum_drop_m,
        'minimum_interior_samples':minimum_interior_samples,'search_radius_km':search_radius_km,
        'profile':profile,'exclusions':exclusions,'measurements_admitted':0}
    if len(profile) < 3:
        result.update(status='REJECTED',reason='insufficient_supported_contours'); return result, None
    speeds = np.asarray([p['mean_geostrophic_speed_m_s'] for p in profile]); best = int(np.argmax(speeds))
    if best in [0,len(profile)-1]:
        result.update(status='REJECTED',reason='maximum_at_supported_sweep_boundary'); return result,None
    if np.sum(np.isclose(speeds,speeds[best],rtol=1e-10,atol=1e-12)) != 1:
        result.update(status='REJECTED',reason='tied_maximum_speed'); return result,None
    result.update(status='PASS_SPEED_CORE_DIAGNOSTIC',selected=profile[best],selected_profile_index=best)
    return result,paths[best]


def compare_steps(coarse, fine):
    if any(r['status'] != 'PASS_SPEED_CORE_DIAGNOSTIC' for r in [coarse,fine]):
        return {'status':'REJECTED','reason':'one_or_both_step_sweeps_rejected'}
    assert coarse['peak']['lon_lat'] == fine['peak']['lon_lat']
    keys = {'area_km2':.10,'speed_equivalent_radius_km':.05,'mean_geostrophic_speed_m_s':.05,
        'east_west_bounding_arc_km_at_midlatitude':.10,'north_south_bounding_arc_km':.10}
    differences = {k:abs(coarse['selected'][k]-fine['selected'][k])/fine['selected'][k] for k in keys}
    return {'status':'PASS_STEP_CONVERGENCE_DIAGNOSTIC' if all(differences[k]<=keys[k] for k in keys) else 'REJECTED',
        'relative_differences':differences,'maximum_relative_differences':keys,
        'interpretation':'OSW numerical convergence gates, not physical measurement uncertainty.'}
