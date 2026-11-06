"""Explicit conditional TEOS-10 daily conversion; never rewrites raw fields."""
import gsw
import numpy as np

VERSION = '3.6.23'


def potential_temperature(sa, temperature, pressure):
    if gsw.__version__ != VERSION:
        raise ValueError('Unpinned GSW version')
    return gsw.pt0_from_t(sa, temperature, pressure)


def daily(fields, depth, latitude, longitude, scale, offsets):
    """Return common mask/conditional pt0 using exact native daily packed pairs."""
    if gsw.__version__ != VERSION:
        raise ValueError('Unpinned GSW version')
    names = ['water_u', 'water_v', 'water_temp', 'salinity']
    shape = np.asarray(fields[names[0]]).shape
    if (len(shape) != 4 or shape[1:] != (len(depth), len(latitude), len(longitude))
            or list(depth) != [100, 200]):
        raise ValueError('Changed daily grid or native depths')
    arrays = {n: np.asarray(fields[n]) for n in names}
    if any(a.shape != shape or a.dtype.kind != 'i' or a.dtype.itemsize != 2 for a in arrays.values()):
        raise ValueError('Expected complete matching packed Int16 daily fields')
    lat = np.asarray(latitude, dtype=float)[None, None, :, None]
    lon = np.asarray(longitude, dtype=float)[None, None, None, :]
    z = np.asarray(depth, dtype=float)[None, :, None, None]
    if (not np.isfinite(lat).all() or not np.isfinite(lon).all()
            or np.any(np.abs(lat) > 90) or np.any((lon < -180) | (lon > 360))):
        raise ValueError('Invalid native geography')
    mask = np.logical_and.reduce([arrays[n] != -30000 for n in names])
    salinity = arrays['salinity'].astype(float)*scale+offsets['salinity']
    temperature = arrays['water_temp'].astype(float)*scale+offsets['water_temp']
    if np.any(mask & (salinity < 0)):
        raise ValueError('Negative valid Practical Salinity cannot be clamped')
    pressure = np.broadcast_to(gsw.p_from_z(-z, lat, 0, 0), shape)
    sp = np.where(mask, salinity, np.nan)
    t = np.where(mask, temperature, np.nan)
    sa = gsw.SA_from_SP(sp, pressure, lon, lat)
    theta = potential_temperature(sa, t, pressure)
    if not np.isfinite(theta[mask]).all() or not np.isfinite(sa[mask]).all():
        raise ValueError('Derived nonfinite value on raw common-valid support')
    return {'common_mask': mask, 'sea_pressure_dbar': pressure,
            'absolute_salinity_g_kg': sa,
            'potential_temperature_0_dbar_assuming_ITS90_c': theta,
            'temperature_scale_verified': False,
            'temperature_scale_assumption': 'ITS-90',
            'pressure_uses_zero_dynamic_height_and_surface_geopotential': True,
            'current_association_verified': False, 'physical_width_admitted': False}


def monthly(daily_result, minimum):
    """Chronological daily mean; retain raw common support and failed eligibility."""
    mask = daily_result['common_mask']
    theta = daily_result['potential_temperature_0_dbar_assuming_ITS90_c']
    counts = mask.sum(axis=0).astype('<i2')
    mean = np.full(counts.shape, np.nan, dtype='<f8')
    np.divide(np.where(mask, theta, 0).sum(axis=0, dtype=np.float64), counts,
              out=mean, where=counts >= minimum)
    return counts, mean
