from pathlib import Path
import json,zipfile
import pytest
import build_redsox_ladcp_source_inventory as source


@pytest.fixture
def raw_profile():
    name='RSX1/rsx1001.downup.nav.ladcpp.asc'
    with zipfile.ZipFile(source.SOURCE/'ladcp-ascii-originals.zip') as z:
        return name,z.read(name)


def test_original_reproduction_preserves_all_conflicts_and_survey_support():
    actual=source.build()
    assert actual==json.loads(source.OUTPUT.read_bytes())
    assert actual['counts']=={'profiles':445,'samples':42004,'nquan_conflicts':310,
        'uninterpretable_reference_headers':15,'component_mask_disagreements':0}
    assert [c['profiles'] for c in actual['campaigns']]==[222,223]
    assert [len(c['station_ids_not_distributed_in_1_to_published_count']) for c in actual['campaigns']]==[16,4]
    assert all(not r['current_width_admitted'] and not r['descending_plume_membership_verified'] for r in actual['profiles'])
    assert actual['quality_context']['RSX1']['author_typical_velocity_uncertainty_m_s']==.03
    assert actual['quality_context']['RSX2']['author_typical_velocity_uncertainty_m_s']==.04
    assert not actual['quality_summaries_are_width_uncertainty'] and not actual['quality_summaries_are_per_cast_intervals']
    assert not actual['nquan_conflicts_repaired'] and not actual['uninterpretable_reference_headers_repaired']
    assert not actual['new_width_record_admitted'] and actual['whole_current_width_km'] is None


def test_nquan_conflict_is_exposed_without_rewriting_observed_columns(raw_profile):
    name,raw=raw_profile
    header,rows,issues=source.parse_gpl(raw)
    assert header['nquan']=='12' and header['sequence']=='hz zz ur vr'
    assert len(rows)==90 and all(len(row)==4 for row in rows)
    assert issues==['declared_nquan_disagrees_with_sequence_and_observed_rows']
    record=source.profile_record(name,raw)
    assert record['declared_nquan']==12 and record['actual_columns']==4
    assert record['position_lon_lat']==[49.8649,5.45491]
    assert record['time_utc']=='2001-02-14T11:49:08Z'


def test_wrapped_source_units_are_read_as_one_value(raw_profile):
    _,raw=raw_profile
    assert source.parse_gpl(raw)[0]['_ur_data_units']==source.VELOCITY_UNITS
    with pytest.raises(ValueError,match='source units'):
        source.parse_gpl(raw.replace(b'# _hz_data_units m',b'# _hz_data_units km'))


def test_missing_sentinel_remains_unknown_not_zero_velocity(raw_profile):
    _,raw=raw_profile
    before,after=raw.split(b'#END#')
    lines=after.splitlines();index=next(i for i,line in enumerate(lines) if line.strip())
    values=lines[index].split();values[2]=b'-1e30';lines[index]=b' '.join(values)
    _,rows,_=source.parse_gpl(before+b'#END#'+b'\n'.join(lines))
    assert rows[0][2] is None and rows[0][3] is not None


@pytest.mark.parametrize('change', ['count','sequence','terminator','frame','nonfinite','duplicate'])
def test_malformed_or_reinterpreted_profiles_are_rejected(raw_profile,change):
    _,raw=raw_profile
    if change=='count':raw=raw.replace(b'# n_values 90',b'# n_values 91')
    elif change=='sequence':raw=raw.replace(b'# sequence hz zz ur vr',b'# sequence hz zz vr ur')
    elif change=='terminator':raw=raw.replace(b'#END#',b'#NOEND#')
    elif change=='frame':raw=raw.replace(b'# coordinates earth',b'# coordinates ship')
    elif change=='duplicate':raw=b'# n_values 90\n'+raw
    else:
        before,after=raw.split(b'#END#');parts=after.split();parts[2]=b'nan'
        raw=before+b'#END#\n'+b'\n'.join(b' '.join(parts[i:i+4]) for i in range(0,len(parts),4))
    with pytest.raises(ValueError):source.parse_gpl(raw)


def test_changed_coherent_acquisition_does_not_override_frozen_original_pins(tmp_path,monkeypatch):
    for name in source.PINS:
        raw=(source.SOURCE/name).read_bytes()
        if name=='acquisition.json':
            receipt=json.loads(raw);receipt['expected_files']=444;raw=json.dumps(receipt).encode()
        (tmp_path/name).write_bytes(raw)
    monkeypatch.setattr(source,'SOURCE',tmp_path)
    with pytest.raises(ValueError,match='Changed frozen REDSOX source'):source.build()
