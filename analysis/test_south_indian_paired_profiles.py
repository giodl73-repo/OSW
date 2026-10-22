"""Gradient support, candidate censoring and missing-value safeguards."""
import numpy as np
import pytest
from south_indian_paired_profiles import positive_maxima, adjacent_gradients, support_distance, profile
from acquire_south_indian_hycom_hydrography import FIELDS


def test_plateau_retains_full_support_and_both_flanks():
    events=positive_maxima([np.nan,1,2,2,1,np.nan])
    assert len(events)==1
    assert events[0]['start_index']==2 and events[0]['end_index']==3
    assert events[0]['both_flanks_finite']


def test_missing_and_domain_end_peaks_remain_censored():
    events=positive_maxima([3,2,np.nan,4,4])
    assert [(e['start_index'],e['end_index']) for e in events]==[(0,0),(3,4)]
    assert events[0]['flanks'][0]['status']=='domain_end'
    assert [f['status'] for f in events[1]['flanks']]==['missing_neighbor','domain_end']
    assert not any(e['both_flanks_finite'] for e in events)
    assert positive_maxima([-2,-1,0,np.nan])==[]


def test_native_spacing_is_not_assumed_uniform_and_no_missing_bridge():
    lat=[-42,-41.96,-41.88,-41.80]
    fields={name:np.array([0.,1.,3.,np.nan]) for name in FIELDS}
    spacing,gradient=adjacent_gradients(lat,80,fields)
    assert 1.99<spacing[1]/spacing[0]<2.01
    assert gradient['salinity'][0]==1/spacing[0]
    assert gradient['salinity'][1]==2/spacing[1]
    assert np.isnan(gradient['salinity'][2])


@pytest.mark.parametrize('lat', [[-40,-41],[-41,-41],[np.nan,-40],[-40]])
def test_rejects_invalid_latitude(lat):
    with pytest.raises(ValueError):
        adjacent_gradients(lat,80,{n:np.zeros(len(lat)) for n in FIELDS})


def test_support_distance_uses_brackets_not_arbitrary_midpoints():
    assert support_distance(80,[-42,-41],[-41.5,-40])==0
    assert support_distance(80,[-42,-41],[-40,-39])==support_distance(80,[-40,-39],[-42,-41])
    assert 110<support_distance(80,[-42,-41],[-40,-39])<112


def test_all_candidate_peaks_retained_and_no_identity_inferred():
    fields={name:np.array([0.,1.,0.,1.,0.]) for name in FIELDS}
    result=profile([-42,-41.9,-41.8,-41.7,-41.6],80,fields)
    assert len(result['positive_eastward_velocity_maxima'])==2
    assert len(result['positive_salinity_gradient_maxima'])==2
    for event in result['positive_eastward_velocity_maxima']:
        assert not event['physical_width_admitted'] and not event['current_association_verified']
        assert event['closest_positive_salinity_gradient_ids']


def test_no_salinity_gradient_means_no_invented_association():
    fields={name:np.array([0.,1.,0.]) for name in FIELDS}
    fields['salinity'][:]=35
    event=profile([-42,-41.9,-41.8],80,fields)['positive_eastward_velocity_maxima'][0]
    assert event['closest_positive_salinity_gradient_ids']==[]
    assert event['closest_gradient_support_distance_km'] is None


def test_equal_nearest_gradient_supports_are_both_retained():
    lat=np.array([-42.,-41.,-40.,-39.])
    fields={name:np.array([0.,1.,1.,0.]) for name in FIELDS}
    spacing,_=adjacent_gradients(lat,80,fields)
    fields['salinity']=np.r_[0.,np.cumsum(spacing*np.array([1.,0.,1.]))]
    result=profile(lat,80,fields)
    event=result['positive_eastward_velocity_maxima'][0]
    assert event['start_index']==1 and event['end_index']==2
    assert event['closest_positive_salinity_gradient_ids']==['salinity-gradient-0','salinity-gradient-1']
    assert event['closest_gradient_support_distance_km']==0
    assert not any(g['both_flanks_finite'] for g in result['positive_salinity_gradient_maxima'])
