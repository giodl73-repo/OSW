"""Actual archived source bits, independent clocks and archive custody gates."""
from pathlib import Path
import json,hashlib,shutil,stat,zipfile
import h5py
import numpy as np
import pytest
import acquire_loop_durante_2026 as source


@pytest.fixture(scope='module')
def checked():return source.verify()


def test_complete_source_bits_and_matlab_dimensions(checked):
    receipt,report,arrays=checked
    with h5py.File(source.DIRECTORY/'Figures2_4_processed.mat','r') as h5:
        for name,array in arrays.items():
            raw=h5[name][()]
            assert array.shape==tuple(reversed(raw.shape))
            assert array.T.copy().tobytes()==raw.tobytes()
            row=next(r for r in report['source_field_schema'] if r['field']==name)
            assert row['source_array_sha256']==hashlib.sha256(raw.tobytes()).hexdigest()
    assert len(arrays)==25 and report['source_numerical_data_are_author_processed']
    assert not report['current_length_admitted'] and not report['width_measurement_admitted']
    assert receipt['source_version']=='0'


def test_missing_time_is_not_filled_and_source_clocks_stay_separate(checked):
    _,report,arrays=checked
    assert report['times']['tid']['records']==4111
    assert report['times']['tisp']['nonfinite']==1
    assert report['concurrent_time_association']['tisp_nonfinite_source_indices']==[3462]
    assert report['concurrent_time_association']['position_index_basis'].startswith('zero_based')
    assert all(v['indexing']=='one_based_MATLAB' for v in report['source_phase_indices'].values())
    assert report['concurrent_time_association']['paired_time_differences']==0
    assert not report['concurrent_time_association']['missing_times_filled_from_other_axis']
    assert np.isnan(arrays['tisp'].reshape(-1)[3462])
    assert np.isfinite(arrays['tid'].reshape(-1)[3462])
    assert report['times']['htimef']['records']==11902
    assert report['times']['htimef']['first_finite_calendar']=='1993-01-01T00:00:00'
    assert report['times']['htimef']['last_finite_calendar']=='2025-08-02T00:00:00'
    assert all(t['timezone'] is None for t in report['times'].values())


def test_date_conversion_known_epoch_hours_and_nulls():
    value=source.matlab_time(np.array([719529.,np.nan,719529.5]))
    assert value['first_finite_calendar']=='1970-01-01T00:00:00'
    assert value['last_finite_calendar']=='1970-01-01T12:00:00'
    assert value['records']==3 and value['nonfinite']==1 and value['noninteger_serial_times']==1
    with pytest.raises(ValueError):source.matlab_time(np.array([100.]))


@pytest.mark.parametrize('bad',['../outside.mat','/absolute.mat','C:/outside.mat','dir\\outside.mat'])
def test_unsafe_archive_addresses_rejected(bad):
    with pytest.raises(ValueError):source.validate_members([zipfile.ZipInfo(bad)])


def test_duplicate_symlink_and_large_members_rejected():
    m=zipfile.ZipInfo('data/x.mat')
    with pytest.raises(ValueError):source.validate_members([m,m])
    link=zipfile.ZipInfo('link');link.external_attr=(stat.S_IFLNK|0o777)<<16
    with pytest.raises(ValueError):source.validate_members([link])
    m.file_size=50_000_001
    with pytest.raises(ValueError):source.validate_members([m])


@pytest.mark.parametrize('mode',['source','quality','inventory','admission'])
def test_changed_retained_source_or_receipt_rejected(tmp_path,mode):
    folder=tmp_path/'source';shutil.copytree(source.DIRECTORY,folder)
    if mode=='source':
        p=folder/'Figures2_4_processed.mat';raw=bytearray(p.read_bytes());raw[-1]^=1;p.write_bytes(raw)
    elif mode=='quality':
        p=folder/'quality.json';doc=json.loads(p.read_bytes());doc['current_length_admitted']=True;p.write_text(json.dumps(doc))
    else:
        p=folder/'acquisition.json';doc=json.loads(p.read_bytes())
        if mode=='inventory':doc['files'].pop('DATA_DICTIONARY.md')
        else:doc['width_measurement_admitted']=True
        p.write_text(json.dumps(doc))
    with pytest.raises(ValueError):source.verify(folder)
