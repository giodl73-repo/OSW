"""Independent averaging, geometry, coverage and source-reconstruction checks."""
import copy
import csv
import io
import json
from pathlib import Path
import pytest
from pyproj import Geod
from build_southern_basin_oscar_climatology import ROOT, OUTPUT, CACHE, build, climatology, span
from build_basin_surface_section_spans import diagnostic_matches
from check_southern_basin_oscar_climatology import saved, validate_inventory, DATA_PIN


def section():
    return {'fixed_axis':'longitude','fixed_coordinate':80+1/3,'varying_axis':'latitude','domain':[-12,0],'peak_search':[-6,-2.5],'component':'eastward'}


def test_full_source_reconstruction_and_independent_native_vector_mean():
    retained=json.loads((ROOT/OUTPUT).read_bytes())
    assert diagnostic_matches(retained,build())
    assert sum(s['counts']['source_times'] for s in retained['sections'])==4752
    for s in retained['sections']:
        assert s['excluded_boundary_times']==['2017-01-01T00:00:00Z']
        assert s['unexpected_time_gaps']==[]
        assert s['counts']['missing_vector_pairs']==0
        original=list(csv.reader(io.StringIO((CACHE/(s['section_id']+'.csv')).read_text(encoding='utf8'))))[2:]
        cells=[r for r in original if r[0].startswith('2013-03') and abs(float(r[2])+40)<1e-8]
        profile=s['yearly']['2013']['months'][2]['profile']
        measured=next(p for p in profile if abs(p['latitude']+40)<1e-8)
        assert measured['paired_source_samples']==len(cells)
        assert measured['eastward_m_s']==pytest.approx(sum(float(r[4]) for r in cells)/len(cells),abs=1e-15)
        assert measured['northward_m_s']==pytest.approx(sum(float(r[5]) for r in cells)/len(cells),abs=1e-15)


def fixture_years():
    yearly={}
    for year in range(1995,2017):
        scale=1 if year==1995 else 0
        profile=[{'coordinate':x,'longitude':80+1/3,'latitude':x,'eastward_m_s':scale*v,'northward_m_s':.1,'component_m_s':scale*v,'paired_source_samples':5 if year==1995 else 6} for x,v in zip([-8,-6,-4,-2,0],[0,.5,1,.5,0])]
        yearly[str(year)]={'months':[{'profile':copy.deepcopy(profile),'approximate_section_span_km':100,'nominal':{'status':'paired_boundaries'}} for _ in range(12)]}
    return yearly


def test_equal_year_weights_are_not_pooled_record_weights():
    result=climatology(fixture_years(),section())[0]
    peak=result['profile'][2]
    assert peak['eastward_m_s']==pytest.approx(1/22)
    assert peak['eastward_m_s']!=pytest.approx(5/(5+21*6))
    assert len(peak['valid_years'])==22
    assert result['width_of_climatological_mean_is_mean_yearly_width'] is False


def test_paired_year_mask_and_minimum_coverage_preserve_null():
    yearly=fixture_years()
    for year in range(1995,2000):
        for month in yearly[str(year)]['months']:month['profile'][2]['eastward_m_s']=None
    peak=climatology(yearly,section())[0]['profile'][2]
    assert len(peak['valid_years'])==17
    assert peak['eastward_m_s'] is None and peak['northward_m_s'] is None


def test_search_window_is_not_a_boundary_and_weak_flow_is_not_zero():
    profile=fixture_years()['1995']['months'][0]['profile']
    result=span(profile,section(),'Jan',1)
    assert result['crossing_outside_context_window']
    low,high=[result['nominal']['boundaries'][k]['coordinate'] for k in ['low_coordinate','high_coordinate']]
    assert high==-2 and low==-6
    assert result['nominal']['span_km']==pytest.approx(Geod(ellps='WGS84').inv(80+1/3,low,80+1/3,high)[2]/1000)
    for p in profile:p['component_m_s']=-.1
    result=span(profile,section(),'Sep',9)
    assert result['approximate_section_span_km'] is None
    assert result['nominal']['status']=='weak_or_no_eligible_peak'


def test_three_basins_keep_original_2013_vectors_and_monthly_operator():
    from acquire_basin_surface_sections import build as original_inventory
    from build_basin_surface_section_spans import monthly_profiles
    retained=json.loads((ROOT/OUTPUT).read_bytes())
    old={r['current_id']:r for r in original_inventory()['sections']}
    docs=saved()
    assert [d['current_id'] for d in docs]==['south-atlantic','south-pacific','south-indian']
    assert len({d['diagnostic_id'] for d in docs})==3
    assert sum(m['approximate_section_span_km'] is not None for d in docs for m in d['months'])==33
    assert sum(m['yearly_resolved_count'] for d in docs for m in d['months'])==792
    for s,d in zip(retained['sections'],docs):
        assert d['year'] is None and d['climatology_period_years']==[1995,2016]
        assert d['annual_width_range_km'] is None and not d['seasonal_playback_eligible']
        for before,after in zip(monthly_profiles(old[s['current_id']]),s['yearly']['2013']['months']):
            assert before['profile']==after['profile']


def test_gap_inventory_rejects_missing_evidence_or_published_width_promotion():
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    validate_inventory(inventory)
    for mode in ['missing','pooled_width','uncertainty']:
        bad=copy.deepcopy(inventory)
        entry=next(r for r in bad['section_span_diagnostics'] if r['current_id']=='south-atlantic')
        if mode=='missing':entry['sources'].pop()
        if mode=='pooled_width':entry['whole_current_width_km']=300
        if mode=='uncertainty':entry['annual_width_range_km']=[100,600]
        with pytest.raises(ValueError):validate_inventory(bad)
