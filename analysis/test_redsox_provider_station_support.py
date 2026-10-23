"""Provider agreement never supplies physical-cast or sample-clock proof."""
from copy import deepcopy

import pytest

from redsox_provider_station_support import assess, stamp


def pair():
    return ({'id': 'rsx1-073-hr', 'campaign': 'RSX1', 'station': 73,
             'position_lon_lat': [43.6706, 12.2161], 'time_utc': '2001-02-23T12:03:45Z'},
            {'id': 'rsx1-073-ctd', 'campaign': 'RSX1', 'filename_station': 73,
             'parsed_header_station': 73, 'position_lon_lat': [43.6706, 12.2161],
             'start_time_utc': '2001-02-23T11:48:26Z'})


def test_agreement_is_not_physical_or_clock_validation():
    v, h = pair()
    join = {'ladcp_id': v['id'], 'ctd_id': h['id'], 'same_physical_cast_verified': False}
    r = assess(v, h, join)
    assert r['status'] == 'consistent_provider_station_records'
    assert r['provider_station_fields_agree']
    assert r['ladcp_minus_ctd_start_seconds'] == 919
    assert r['original_filename_join'] == join
    assert not r['physical_cast_identity_verified']
    assert not r['sample_level_synchronization_verified']
    assert not join['same_physical_cast_verified']


def test_timestamp_order_is_preserved_without_inventing_a_lag():
    v, h = pair(); h['start_time_utc'] = '2001-02-23T12:04:45Z'
    r = assess(v, h)
    assert r['provider_station_fields_agree']
    assert r['ladcp_minus_ctd_start_seconds'] == -60


def test_midnight_is_review_not_a_different_cast_claim():
    v, h = pair(); h['start_time_utc'] = '2001-02-22T23:59:59Z'
    r = assess(v, h)
    assert r['status'] == 'provider_metadata_review_required'
    assert r['failed_checks'] == ['same_reported_utc_date']
    assert not r['physical_cast_identity_verified']


def test_all_conflicts_and_missing_metadata_survive():
    v, h = pair(); h = deepcopy(h)
    h.update(campaign='RSX2', filename_station=72, parsed_header_station=None,
             position_lon_lat=None, start_time_utc=None)
    r = assess(v, h)
    assert len(r['failed_checks']) == 7
    assert r['ladcp_minus_ctd_start_seconds'] is None


def test_no_nearest_position_tolerance_or_header_repair():
    v, h = pair(); h['position_lon_lat'][0] += 1e-9
    r = assess(v, h)
    assert r['failed_checks'] == ['same_serialized_position']
    assert not r['provider_station_fields_agree']


def test_missing_companion_is_not_an_empty_passing_record():
    v, _ = pair(); r = assess(v, None)
    assert r['status'] == 'missing_ctd_record'
    assert r['failed_checks'] == ['missing_ctd_record']
    assert not r['provider_station_fields_agree']


def test_utc_date_normalization_requires_a_timezone():
    assert stamp('2001-02-24T00:30:00+01:00').isoformat() == '2001-02-23T23:30:00+00:00'
    with pytest.raises(ValueError, match='timezone'):
        stamp('2001-02-23T12:00:00')
