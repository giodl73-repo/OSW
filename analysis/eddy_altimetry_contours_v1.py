"""Exploratory daily ADT contours; no eddy identity or measurement admission."""
import hashlib
import math

import contourpy
import numpy as np
from matplotlib.path import Path
from pyproj import Geod

RADIUS_M = 6371000.0  # Explicit OSW metric convention, not an inferred source CRS.
GEOD = Geod(a=RADIUS_M, b=RADIUS_M)


def demean(lon, lat, field, weighted=False):
    lon, lat = np.asarray(lon), np.asarray(lat)
    z = np.ma.filled(np.ma.asarray(field, dtype=float), np.nan)
    assert z.shape == (len(lat), len(lon))
    assert np.all(np.diff(lon) > 0) and np.all(np.diff(lat) > 0)
    box = ((lat[:, None] >= 17) & (lat[:, None] <= 31)
           & (lon[None, :] >= -99) & (lon[None, :] <= -80) & np.isfinite(z))
    assert box.sum() > 100
    weights = np.broadcast_to(np.cos(np.deg2rad(lat))[:, None], z.shape) if weighted else np.ones(z.shape)
    mean = float(np.sum(z[box] * weights[box]) / np.sum(weights[box]))
    return z - mean, mean, int(box.sum())


def contour_candidates(lon, lat, z, level, minimum_area_km2=4000):
    """Return closed high-interior loops; reject open, masked and clipped outlines."""
    lon, lat, z = np.asarray(lon), np.asarray(lat), np.asarray(z)
    assert z.shape == (len(lat), len(lon)) and np.all(np.diff(lon) > 0) and np.all(np.diff(lat) > 0)
    generator = contourpy.contour_generator(x=lon, y=lat, z=np.ma.masked_invalid(z),
        name='serial', line_type='SeparateCode', corner_mask=False, quad_as_tri=False)
    vertices, codes = generator.lines(level)
    gx, gy = np.meshgrid(lon, lat)
    grid = np.column_stack([gx.ravel(), gy.ravel()])
    accepted, rejected = [], {}

    def reject(reason):
        rejected[reason] = rejected.get(reason, 0) + 1

    for points, kind in zip(vertices, codes):
        if len(points) < 4 or kind[-1] != 79 or not np.array_equal(points[0], points[-1]):
            reject('open_or_degenerate'); continue
        west, south = points.min(axis=0)
        east, north = points.max(axis=0)
        if west <= lon[0] or east >= lon[-1] or south <= lat[0] or north >= lat[-1]:
            reject('domain_clipped'); continue
        inside = Path(points).contains_points(grid).reshape(z.shape)
        if not inside.any() or np.any(inside & ~np.isfinite(z)):
            reject('missing_interior_or_no_sampled_interior'); continue
        area, perimeter = GEOD.polygon_area_perimeter(points[:, 0], points[:, 1])
        # ContourPy directs higher values to the left; positive signed area is a high interior.
        if area <= 0:
            reject('low_interior'); continue
        if area / 1e6 < minimum_area_km2:
            reject('below_review_area_screen'); continue
        peak_flat = int(np.argmax(np.where(inside, z, -np.inf)))
        iy, ix = np.unravel_index(peak_flat, z.shape)
        midlat = float((north + south) / 2)
        ew = GEOD.inv(west, midlat, east, midlat)[2] / 1000
        ns = RADIUS_M / 1000 * math.radians(float(north - south))
        metrics = {
            'bbox_degrees': [float(west), float(south), float(east), float(north)],
            'area_km2': float(area / 1e6),
            'area_equivalent_diameter_km': float(2 * math.sqrt(area / 1e6 / math.pi)),
            'east_west_bounding_arc_km_at_midlatitude': float(ew),
            'north_south_bounding_arc_km': float(ns),
            'perimeter_km': float(perimeter / 1000),
            'peak_grid_position_lon_lat': [float(lon[ix]), float(lat[iy])],
            'peak_demeaned_adt_m': float(z[iy, ix]),
            'vertices': int(len(points)),
            'vertices_float64_little_endian_sha256': hashlib.sha256(np.asarray(points, dtype='<f8').tobytes()).hexdigest(),
        }
        accepted.append((metrics, points))
    accepted.sort(key=lambda item: tuple(item[0]['bbox_degrees']))
    for index, (row, _) in enumerate(accepted, 1):
        row['candidate_id'] = f'C{index:02d}'
    return accepted, rejected
