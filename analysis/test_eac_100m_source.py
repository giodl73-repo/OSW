"""Exact source bits, independent calendar/gap accounting and dimensional limits."""
from datetime import datetime,timezone
from pathlib import Path
import copy,json
import numpy as np
import pytest
import acquire_eac_100m_source as acquisition
import check_eac_100m_source as source


@pytest.fixture(scope='module')
def checked():return source.load()


@pytest.fixture(scope='module')
def quality():return source.build()


def test_every_selected_field_and_coordinate_is_preserved(checked):
    receipt,header,arrays=checked
    assert set(arrays)==set(acquisition.FIELDS+acquisition.COORDINATES)
    assert all(arrays[k].shape==(3770,124) for k in acquisition.FIELDS)
    assert all(acquisition.array_pin(v)==receipt['source_array_sha256'][k] for k,v in arrays.items())
    assert receipt['complete_source_checksum_verified'] is True
    assert receipt['second_source_read_all_selected_bits_equal'] is True
    assert receipt['collection_version']==23 and receipt['data_version']==19
    assert 'v19' in header['global_attributes']['citation']
    assert arrays['DEPTH'][receipt['source_depth_index']]==100


def test_original_clock_and_month_support_are_not_invented(quality,checked):
    dates=source.times(checked[2]['TIME'])
    assert dates[0]==datetime(2012,4,1,12,tzinfo=timezone.utc)
    assert dates[-1]==datetime(2022,7,27,12,tzinfo=timezone.utc)
    assert all((b-a).total_seconds()==86400 for a,b in zip(dates,dates[1:]))
    assert quality['calendar_bins']==124 and quality['complete_nominal_calendar_bins']==123
    assert sum(m['source_records'] for m in quality['monthly_support'])==3770
    assert quality['monthly_support'][-1]['source_records']==27
    assert quality['monthly_support'][-1]['complete_nominal_calendar_schedule'] is False
    assert all(m['complete_schedule_is_complete_data_coverage'] is False for m in quality['monthly_support'])


def test_actual_missing_mask_and_uncertainty_pairs(quality,checked):
    arrays=checked[2];mask=np.isfinite(arrays['VCUR'])
    assert quality['source_field_values']==3739840
    assert quality['paired_velocity_cells']==354933
    assert quality['paired_velocity_and_uncertainty_cells']==354933
    for name in acquisition.FIELDS:
        assert np.array_equal(np.isfinite(arrays[name]),mask)
        assert quality['fields'][name]['finite_values']==354933
        assert quality['fields'][name]['nan_values']==112547
        assert quality['fields'][name]['positive_infinity_values']==0
        assert quality['fields'][name]['negative_infinity_values']==0
        if name.endswith('_uncertainty'):assert quality['fields'][name]['negative_finite_values']==0
    missing=np.flatnonzero(~mask.any(axis=1))
    assert np.array_equal(missing,np.arange(513,1142))
    assert quality['profiles_without_paired_velocity']==629
    gap=quality['missing_paired_velocity_runs'];assert len(gap)==1
    assert gap[0]['first_source_time']=='2013-08-27T12:00:00Z'
    assert gap[0]['last_source_time']=='2015-05-17T12:00:00Z'
    assert gap[0]['source_records']==629


def test_bottom_zeros_are_not_missing_or_observed_current_absence(quality,checked):
    arrays=checked[2]
    assert quality['finite_paired_velocity_cells_at_or_below_source_bottom']==6282
    populated=[r for r in quality['source_bottom_support'] if r['finite_paired_velocity_records']]
    assert [r['source_position_index'] for r in populated]==[11,12]
    for row in populated:
        assert row['bottom_depth_m']==100
        assert row['finite_paired_velocity_records']==row['zero_paired_velocity_records']==row['zero_paired_velocity_uncertainty_records']==3141
    assert np.isnan(arrays['VCUR'][:,:11]).all()
    assert quality['method_scope']['source_zero_velocity_at_bottom_is_independent_observed_current_absence'] is False
    assert quality['method_scope']['source_zero_uncertainty_is_guaranteed_no_error'] is False


def test_source_header_disagreements_are_retained(quality,checked):
    header=checked[1];lineage=header['global_attributes']['lineage']
    assert "remove data flagged as 'good'" in lineage
    assert 'nearest-neighbour' in lineage
    assert header['datasets']['VCUR']['attributes']['reference_datum']=='true north'
    assert header['datasets']['VCUR_uncertainty']['attributes']['long_name']=='VCUR_standard_error'
    assert len(quality['documentary_disagreements'])==3
    assert quality['method_scope']['OSW_rotation_applied'] is False
    assert quality['method_scope']['OSW_missing_value_filling_applied'] is False


def test_fixed_geometry_preserves_every_coordinate(quality,checked):
    arrays=checked[2];geometry=quality['fixed_source_geometry']
    np.testing.assert_array_equal(np.array(geometry['longitude_latitude_points'])[:,0],arrays['LONGITUDE'])
    np.testing.assert_array_equal(np.array(geometry['longitude_latitude_points'])[:,1],arrays['LATITUDE'])
    assert geometry['crs']=='WGS84' and geometry['array_length_is_current_length'] is False
    assert 173<geometry['source_array_polyline_length_km']<174
    assert geometry['grid_segment_distance_m_range'][0]>999
    assert geometry['grid_segment_distance_m_range'][1]<2008


def test_source_quality_cannot_be_promoted_to_dimensions(quality):
    assert quality['whole_current_width_km'] is None and quality['annual_width_range_km'] is None
    assert quality['geographic_current_edges'] is None
    assert quality['width_measurement_admitted'] is False and quality['width_rank_eligible'] is False
    assert quality['seasonal_current_polygon_playback_eligible'] is False
    assert quality['method_scope']['daily_records_are_independent_observations'] is False
    assert quality['method_scope']['per_cell_observed_versus_filled_flags_available_in_selected_product'] is False


def test_independent_missing_run_examples():
    dates=[datetime(2001,1,i+1,tzinfo=timezone.utc) for i in range(5)]
    assert source.absent_runs([False]*5,dates)==[]
    gaps=source.absent_runs([True,False,True,True,True],dates)
    assert [(g['first_source_index'],g['last_source_index'],g['source_records']) for g in gaps]==[(0,0,1),(2,4,3)]


def test_deterministic_subset_writer_preserves_signed_zero_and_nan_bits(tmp_path):
    arrays={'one':np.array([0.,-0.,np.nan,-2.5],dtype='<f8'),'two':np.arange(12,dtype='<f8').reshape(3,4)}
    a=tmp_path/'a.npz';b=tmp_path/'b.npz';acquisition.write_npz(a,arrays);acquisition.write_npz(b,arrays)
    assert a.read_bytes()==b.read_bytes()
    with np.load(a,allow_pickle=False) as saved:
        for key in arrays:assert acquisition.array_pin(saved[key])==acquisition.array_pin(arrays[key])


def test_altered_or_coherently_rebound_acquisition_is_rejected(tmp_path,checked):
    receipt=copy.deepcopy(checked[0]);receipt['whole_current_width_km']=173
    acquisition.write_json(tmp_path/'acquisition.json',receipt)
    with pytest.raises(ValueError,match='Changed frozen'):
        source.load(tmp_path)


def test_figure_source_and_accessibility_registration(quality):
    receipt=json.loads((acquisition.ROOT/'research/eac-csiro-v23-100m-source-fields-figure.json').read_bytes())
    assert receipt['source_sha256']==acquisition.sha(acquisition.ROOT/source.REPORT)
    assert receipt['source_profiles']==3770 and receipt['source_field_panels']==8
    assert receipt['fixed_geometry_not_current_edges'] is True
    assert receipt['physical_width_admitted'] is False
    assert receipt['provider_uncertainty_reinterpreted_as_confidence_interval'] is False
    for asset in receipt['figures'].values():assert acquisition.sha(acquisition.ROOT/asset['file'])==asset['sha256']
    svg=(acquisition.ROOT/receipt['figures']['.svg']['file']).read_text(encoding='utf8')
    assert 'role="img"' in svg and 'eac-source-description' in svg


def test_json_query_records_round_trip_every_finite_value_and_missing_position(checked):
    from build_eac_source_profiles import verify
    stored,contract=verify()
    assert len(stored['profiles'])==3770 and contract['profiles_without_paired_velocity']==629
    dates=source.times(checked[2]['TIME'])
    for i,row in enumerate(stored['profiles']):
        assert row['source_time_index']==i
        assert row['source_time_utc']==source.iso(dates[i])
        assert (row['year'],row['month'])==(dates[i].year,dates[i].month)
    assert stored['source_time_is_independent_observation_time'] is False
    assert stored['source_values_rounded_by_OSW'] is False


def test_json_missing_to_zero_change_is_rejected():
    from build_eac_source_profiles import OUTPUT,verify_json_against_subset
    stored=json.loads((acquisition.ROOT/OUTPUT).read_bytes())
    assert stored['profiles'][0]['fields']['VCUR'][0] is None
    stored['profiles'][0]['fields']['VCUR'][0]=0
    with pytest.raises(ValueError,match='lost source bits/missing'):
        verify_json_against_subset(stored)
