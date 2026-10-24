import numpy as np
import pytest
import build_indian_secc_eof_feasibility as experiment
from build_indian_secc_eof_feasibility import RESULT,build,compare_modes,context_energy,covariance_eof,retained_columns,spectral_fraction
from copy import deepcopy
import json
import hashlib


def test_known_independent_oscillations_reconstruct_original_units():
    time=np.arange(264)
    components=np.column_stack([4*np.sin(2*np.pi*time/6),2*np.sin(2*np.pi*time/12),np.cos(2*np.pi*time/12)])
    original=components+np.array([12,-3,7])
    mean,spatial,pc,variance=covariance_eof(original)
    np.testing.assert_allclose(mean,[12,-3,7],atol=1e-12)
    np.testing.assert_allclose(pc@spatial+mean,original,atol=1e-12)
    np.testing.assert_allclose(spatial@spatial.T,np.eye(3),atol=1e-12)
    np.testing.assert_allclose(variance,[16/21,4/21,1/21],atol=1e-12)
    assert spectral_fraction(pc[:,0],2)==pytest.approx(1)
    assert spectral_fraction(pc[:,0],1)==pytest.approx(0,abs=1e-12)
    assert spectral_fraction(pc[:,1],1)==pytest.approx(1)


def test_temporal_sign_reversal_preserves_variance_and_orientation():
    rng=np.random.default_rng(29);matrix=rng.normal(size=(264,8))
    a=covariance_eof(matrix);b=covariance_eof(-matrix)
    np.testing.assert_allclose(a[3],b[3],atol=1e-12)
    for vectors in [a[1],b[1]]:
        assert all(row[np.argmax(abs(row))]>=0 for row in vectors)
    np.testing.assert_allclose(a[2]@a[1],-(b[2]@b[1]),atol=1e-12)


def test_deficient_cell_drops_entire_latitude_without_filling():
    matrix=np.ones((264,3));matrix[40,1]=np.nan
    assert retained_columns(matrix).tolist()==[True,False,True]
    assert np.isnan(matrix[40,1])
    with pytest.raises(ValueError):covariance_eof(matrix)


def test_shared_classification_endpoints_do_not_double_count_energy():
    latitude=np.array([-7,-6,-5,-2.5,0,3,4,5.5,6])
    loading=np.ones(len(latitude))/np.sqrt(len(latitude))
    bands={'WJ':[-2.5,3],'MC':[3,5.5],'SECC':[-6,-2.5]}
    energy=context_energy(latitude,loading,bands)
    assert energy==pytest.approx({'WJ':3/9,'MC':2/9,'SECC':2/9})
    assert sum(energy.values())<=1


@pytest.mark.parametrize('matrix',[np.ones((264,3)),np.array([[1,2,3]]),np.array([1,2,3]),np.array([[1,np.inf],[2,3]])])
def test_undefined_decompositions_do_not_report_zero_current(matrix):
    with pytest.raises(ValueError):covariance_eof(matrix)


def synthetic_fit():
    time=np.arange(264)
    spatial=np.eye(5)
    pc=np.array([np.sin(2*np.pi*time/(i+3)) for i in range(5)])
    return {'longitude':80+1/3,'domain':[-2/3,2/3],
        'latitude_degrees':[-2/3,-1/3,0,1/3,2/3],
        'modes':[{'spatial_loading':s.tolist(),'principal_component_m_s':p.tolist()} for s,p in zip(spatial,pc)]}


def test_matching_recovers_permuted_sign_reversed_mode_outside_first_three():
    left=synthetic_fit();right=deepcopy(left)
    order=[2,1,3,4,0]
    right['modes']=[right['modes'][i] for i in order]
    right['modes'][4]['spatial_loading']=(-np.array(right['modes'][4]['spatial_loading'])).tolist()
    right['modes'][4]['principal_component_m_s']=(-np.array(right['modes'][4]['principal_component_m_s'])).tolist()
    result=compare_modes(left,right)
    assert [m['target_rank'] for m in result['matched_modes']]==[5,2,1]
    assert all(m['absolute_loading_cosine']==pytest.approx(1) and m['loading_aligned_pc_correlation']==pytest.approx(1) for m in result['matched_modes'])
    # Matching can recover all modes while the *first-three* subspaces differ.
    assert max(result['first_three_subspace_principal_angles_degrees'])==pytest.approx(90)


def test_comparison_does_not_hide_negative_temporal_agreement():
    left=synthetic_fit();right=deepcopy(left)
    right['modes'][0]['principal_component_m_s']=(-np.array(right['modes'][0]['principal_component_m_s'])).tolist()
    match=compare_modes(left,right)['matched_modes'][0]
    assert match['absolute_loading_cosine']==pytest.approx(1)
    assert match['loading_aligned_pc_correlation']==pytest.approx(-1)


def test_comparison_rejects_incompatible_time_support():
    left=synthetic_fit();right=deepcopy(left)
    right['modes'][0]['principal_component_m_s'].pop()
    with pytest.raises(ValueError,match='Invalid PC'):compare_modes(left,right)


def test_complete_originals_reproduce_saved_experiment_and_keep_missing_support():
    actual=build();saved=json.loads(RESULT.read_bytes())
    # BLAS implementations can differ in their last floating point digits.
    # Structure, provenance, missingness and eligibility remain exact.
    def equivalent(a,b):
        assert type(a) is type(b)
        if isinstance(a,dict):
            assert a.keys()==b.keys()
            for key in a:equivalent(a[key],b[key])
        elif isinstance(a,list):
            assert len(a)==len(b)
            for x,y in zip(a,b):equivalent(x,y)
        elif isinstance(a,float):
            assert np.isfinite(a) and np.isfinite(b)
            assert a==pytest.approx(b,rel=1e-10,abs=1e-11)
        else:assert a==b
    equivalent(actual,saved)
    assert len(actual['fits'])==6 and len(actual['mode_comparisons'])==15
    assert all(d['source_frames']==1585 and d['overlapping_equator_rows_equal']==1585 and d['excluded_times']==['2017-01-01T00:00:00Z'] for d in actual['datasets'])
    for fit in actual['fits']:
        assert fit['dropped_latitudes']==[14/3,5,16/3,17/3,6]
        assert fit['modes'][1]['absolute_peak_at_retained_domain_edge']
        assert all(not m['named_current_identity_assigned'] for m in fit['modes'])
    assert all(actual[k] is False for k in ['current_association_verified','new_width_record_admitted','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible'])
    assert actual['whole_current_width_km'] is None and actual['annual_width_range_km'] is None


def test_changed_preflight_rejects_before_analysis(tmp_path,monkeypatch):
    raw=(experiment.OUT/'preflight.json').read_bytes()
    altered=raw.replace(b'[-8, 6]',b'[-7, 6]')
    (tmp_path/'preflight.json').write_bytes(altered)
    receipt=json.loads((experiment.OUT/'acquisition.json').read_bytes())
    receipt['preflight_sha256']=hashlib.sha256(altered).hexdigest()
    (tmp_path/'acquisition.json').write_bytes(json.dumps(receipt).encode())
    monkeypatch.setattr(experiment,'OUT',tmp_path)
    with pytest.raises(ValueError,match='Changed frozen'):build()
