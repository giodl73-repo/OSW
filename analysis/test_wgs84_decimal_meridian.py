"""Independent curvature integration and invariants for portable distances."""
import numpy as np
import pytest
from pyproj import Geod
from wgs84_decimal_meridian import meridian_km,meridian_metres


@pytest.mark.parametrize('a,b',[(-48,-47.92),(-42.04,-42),(-48,-30),(-90,90),(0,1),(0,90),(-.0001,.0001)])
def test_distance_agrees_with_independent_quadrature_and_proj(a,b):
    nodes,weights=np.polynomial.legendre.leggauss(64)
    lo,hi=np.deg2rad([a,b]);phi=(lo+hi)/2+(hi-lo)*nodes/2
    f=1/298.257223563;e2=f*(2-f)
    radius=6378137*(1-e2)/(1-e2*np.sin(phi)**2)**1.5
    quadrature=float(np.dot(weights,radius)*(hi-lo)/2/1000)
    value=meridian_km(a,b)
    assert abs(value-quadrature)<1e-8
    assert abs(value-Geod(ellps='WGS84').inv(80,a,80,b)[2]/1000)<1e-8
    assert value.hex()==meridian_km(b,a).hex()


def test_symmetry_zero_and_additivity():
    assert meridian_metres(-40)==meridian_metres(40).copy_negate()
    assert meridian_km(-40,-40)==0
    assert abs(meridian_km(-48,-30)-meridian_km(-48,-40)-meridian_km(-40,-30))<1e-12


@pytest.mark.parametrize('v',[float('nan'),float('inf'),-91,91])
def test_rejects_non_geodetic_latitude(v):
    with pytest.raises(ValueError):meridian_km(v,0)
