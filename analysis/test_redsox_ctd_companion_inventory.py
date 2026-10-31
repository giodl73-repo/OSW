import json,zipfile
import pytest
import build_redsox_ctd_companion_inventory as ctd


def raw_profile(station=1,campaign='RSX1'):
    name=f'{campaign}/rsx{campaign[-1]}{station:03d}.ctd.1m.asc'
    with zipfile.ZipFile(ctd.SOURCE/'ctd-ascii-originals.zip') as z:return name,z.read(name)


def test_all_originals_reproduce_and_source_issues_remain_visible():
    actual=ctd.build();assert actual==json.loads(ctd.OUTPUT.read_bytes())
    assert actual['counts']=={'ctd_profiles':461,'samples':441183,'campaigns':{'RSX1':237,'RSX2':224},
        'schemas':{'p S T sigma_theta o2 c':76,'z p T S sigma_theta o2 c theta':225,'p T S sigma_theta o2 c theta':160},
        'header_filename_station_conflicts':3,'unparseable_source_station_labels':6,
        'unparseable_source_times':1,'invalid_source_positions':1,
        'filename_joins':444,'unmatched_ladcp_profiles':1,'ctd_profiles_without_ladcp_filename_match':17}
    assert actual['reviewed_support_counts']=={'profiles':13,'positions':4,'cast_numbers':9,'cast_event_times':1}
    assert actual['unmatched_ladcp_ids']==['rsx1-074-hr']
    assert all(not j['same_physical_cast_verified'] for j in actual['filename_joins'])
    assert not actual['pressure_is_depth'] and not actual['new_width_record_admitted']


def test_reviewed_positions_recover_support_without_overwriting_bad_originals():
    profiles={p['id']:p for p in ctd.build()['profiles']}
    a=profiles['rsx1-075-ctd'];assert a['position_lon_lat']==[43,12]
    assert a['reviewed_source_support']['position_lon_lat']==pytest.approx([43.6,12+12.02/60])
    b=profiles['rsx1-194-ctd'];assert b['position_lon_lat'] is None
    assert b['source_coordinate_strings_lon_lat']==['45.2485','1108.13']
    assert b['reviewed_source_support']['position_lon_lat']==pytest.approx([45.2485,11.1355])
    assert b['reviewed_source_support']['source_precision_arcminutes']==.01


def test_cast_event_does_not_fabricate_a_missing_start_time():
    record=next(p for p in ctd.build()['profiles'] if p['id']=='rsx1-003-ctd')
    assert record['source_start_time']=='48.43-11-01' and record['start_time_utc'] is None
    assert record['reviewed_source_support']['cast_event_time_utc']=='2001-02-17T08:36:00Z'
    assert record['reviewed_source_support']['event_time_is_ctd_start_time'] is False


def test_conflicting_header_labels_keep_their_original_and_reviewed_identities():
    record=next(p for p in ctd.build()['profiles'] if p['id']=='rsx2-014-ctd')
    assert record['source_header_station']=='RSX2013' and record['parsed_header_station']==13
    assert record['filename_station']==14 and record['reviewed_source_support']['reviewed_cast_number']==14
    assert 'filename_and_header_station_disagree' in record['source_metadata_issues']


def test_pressure_only_schema_does_not_invent_geometric_depth():
    name,raw=raw_profile();record=ctd.profile_record(name,raw)
    assert 'p' in record['variables'] and 'z' not in record['variables']
    assert record['variables']['p']['source_units']=='dbar'
    assert 'no_explicit_depth_column_pressure_is_not_depth' in record['source_metadata_issues']


@pytest.mark.parametrize('mutation',['units','sequence','count'])
def test_corrupt_or_reinterpreted_ctd_data_reject(mutation):
    _,raw=raw_profile()
    if mutation=='units':raw=raw.replace(b'# _p_data_units dbar',b'# _p_data_units m')
    elif mutation=='sequence':raw=raw.replace(b'# sequence p S T sigma_theta o2 c',b'# sequence p T S sigma_theta o2 c')
    else:raw=raw.replace(b'# nquan 6',b'# nquan 8')
    with pytest.raises(ValueError):ctd.parse_ctd(raw)


def test_changed_reconciliation_cannot_silently_move_a_cast(tmp_path,monkeypatch):
    data=json.loads(ctd.RECONCILIATION.read_bytes());data['reconciliations'][0]['reviewed_cast_number']=1
    path=tmp_path/'altered.json';path.write_text(json.dumps(data));monkeypatch.setattr(ctd,'RECONCILIATION',path)
    with pytest.raises(ValueError,match='Changed frozen'):ctd.apply_reviewed_support([])
