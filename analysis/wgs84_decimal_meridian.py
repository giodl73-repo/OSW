"""Deterministic WGS84 meridian integrals, with one final binary64 rounding."""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from functools import lru_cache
import math

PRECISION=70
SERIES_ORDER=16
TRIG_TERMS=70
PI='3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628'


@lru_cache(maxsize=4096)
def meridian_metres(latitude):
    """Signed equator-to-latitude arc; latitude is an exact input binary64."""
    latitude=float(latitude)
    if not math.isfinite(latitude) or not -90<=latitude<=90:
        raise ValueError('Invalid geodetic latitude')
    with localcontext() as context:
        context.prec=PRECISION;context.rounding=ROUND_HALF_EVEN
        phi=Decimal.from_float(latitude)*Decimal(PI)/Decimal(180)
        term=phi;sin_phi=term
        cos_term=Decimal(1);cos_phi=cos_term
        square=phi*phi
        for k in range(1,TRIG_TERMS):
            term=-term*square/Decimal((2*k)*(2*k+1));sin_phi+=term
            cos_term=-cos_term*square/Decimal((2*k-1)*(2*k));cos_phi+=cos_term
        f=Decimal(1)/Decimal('298.257223563');e2=f*(Decimal(2)-f)
        integral=phi;total=integral;coefficient=Decimal(1);eccentricity_power=Decimal(1)
        for n in range(1,SERIES_ORDER+1):
            integral=(Decimal(2*n-1)*integral-sin_phi**(2*n-1)*cos_phi)/Decimal(2*n)
            coefficient*=Decimal(2*n+1)/Decimal(2*n)
            eccentricity_power*=e2
            total+=coefficient*eccentricity_power*integral
        return +(Decimal(6378137)*(Decimal(1)-e2)*total)


def meridian_km(south,north):
    with localcontext() as context:
        context.prec=PRECISION;context.rounding=ROUND_HALF_EVEN
        return float(abs(meridian_metres(float(north))-meridian_metres(float(south)))/Decimal(1000))
