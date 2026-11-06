"""Source integrity, geography and independent old-section overlap gates."""
import copy
import json
import io

import numpy as np
import pytest

import acquire_south_australian_hycom_2d as source


@pytest.fixture(scope='module')
def original():
    assert source.sha(source.ROOT/source.ORIGINAL)==source.ORIGINAL_SHA
    return source.parse_ascii((source.ROOT/source.ORIGINAL).read_text(),nx=1)


def test_existing_section_is_losslessly_parsed(original):
    from build_south_australian_hycom_spans import source_inventory
    # Independent existing parser is the numerical oracle, including masks.
    old=source_inventory()
    for field,key in [('water_u','source_u_int16'),('water_v','source_v_int16')]:
        values=np.array([[s[key] for s in frame['samples']] for frame in old['frames']],dtype='<i2')
        assert np.array_equal(original[field][:,:,0],values)
    assert original['water_u'].dtype==np.dtype('<i2')
    assert original['water_v'].size==27816
    assert source.sha(source.ROOT/source.PROTOCOL)==source.PROTOCOL_SHA


@pytest.mark.parametrize('old,new',[
    ('[0][0][0], 89','[0][0][1], 89'),
    ('[0][0][0], 89','[0][0][0], 32768'),
    ('[0][0][0], 89','[0][0][0], 89.5'),
    ('water_v.water_v[366][1][76][1]','water_v.water_v[365][1][76][1]'),
    ('water_v.lon[1]\n132','water_v.lon[1]\n133'),
])
def test_malformed_or_misaligned_source_rejected(old,new):
    text=(source.ROOT/source.ORIGINAL).read_text()
    assert old in text
    with pytest.raises(ValueError):source.parse_ascii(text.replace(old,new,1),nx=1)


def test_full_overlap_and_geographic_validation(original):
    cube={k:v.copy() for k,v in original.items()}
    cube['lon']=130+np.arange(51)*.08
    for name in ['water_u','water_v']:cube[name]=np.repeat(original[name],51,axis=2)
    dates,index=source.check_cube(cube,original)
    assert index==25 and len(dates)==366 and dates[59].day==29
    report=source.quality(cube,dates,index)
    assert report['source_132e_overlap']['scalar_values_compared']==55632
    assert sum(report['paired_counts_by_date'])==report['paired_positions']
    assert np.array(report['paired_counts_by_cell']).sum()==report['paired_positions']
    assert not report['width_measurement_admitted']
    for name in ['water_u','water_v']:
        bad=copy.deepcopy(cube);bad[name][10,5,25]+=1
        with pytest.raises(ValueError,match='packed original overlap'):source.check_cube(bad,original)
    bad=copy.deepcopy(cube);bad['lon'][0]=129
    with pytest.raises(ValueError,match='geographic selection'):source.check_cube(bad,original)
    bad=copy.deepcopy(cube);bad['time'][0]+=1
    with pytest.raises(ValueError,match='coordinate overlap'):source.check_cube(bad,original)
    rounded=copy.deepcopy(cube);rounded['lon'][0]-=.000015
    source.check_cube(rounded,original)
    rounded['lon'][0]-=.00001
    with pytest.raises(ValueError,match='geographic selection'):source.check_cube(rounded,original)


@pytest.mark.parametrize('old,new',[
    ('Float32 scale_factor 0.001;','Float32 scale_factor 0.01;'),
    ('Int16 _FillValue -30000;','Int16 _FillValue -9999;'),
    ('hours since 2000-01-01 00:00:00','hours since 2012-01-01 00:00:00'),
    ('Distribution unlimited.','Distribution restricted.'),
])
def test_changed_packing_clock_or_rights_rejected(old,new):
    das=(source.ROOT/'research/source-data/hycom-south-australian-2012/metadata.das').read_text()
    source.check_metadata(das)
    with pytest.raises(ValueError):source.check_metadata(das.replace(old,new))


def test_receipt_cannot_omit_sources_or_admit_measurements(tmp_path):
    receipt={'schema':'osw.south-australian-hycom-2d-acquisition.v1','files':{}}
    (tmp_path/'acquisition.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='inventory/schema'):source.verify(tmp_path)
    receipt.update(files={name:{} for name in set(source.urls())|{'source-vectors.npz','quality.json'}},
                   protocol_file=source.PROTOCOL,protocol_sha256=source.PROTOCOL_SHA,
                   operator_file=source.OPERATOR,operator_sha256=source.sha(source.ROOT/source.OPERATOR),
                   npz_writer_file='analysis/acquire_eac_100m_source.py',
                   npz_writer_sha256=source.sha(source.ROOT/'analysis/acquire_eac_100m_source.py'),
                   current_association_verified=True,width_measurement_admitted=False)
    (tmp_path/'acquisition.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='cannot admit'):source.verify(tmp_path)
    receipt['current_association_verified']=False;receipt['operator_sha256']='0'*64
    (tmp_path/'acquisition.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='operator/protocol pin'):source.verify(tmp_path)


def test_failed_validation_retains_all_received_originals(tmp_path,monkeypatch):
    stage=tmp_path/'stage';stage.mkdir()
    monkeypatch.setattr(source.tempfile,'mkdtemp',lambda **kwargs:str(stage))
    class Response(io.BytesIO):
        headers={'Content-Type':'text/plain'}
    monkeypatch.setattr(source.urllib.request,'urlopen',lambda *args,**kwargs:Response(b'invalid original response'))
    with pytest.raises(ValueError,match='Incomplete HYCOM'):source.acquire(tmp_path/'public')
    assert not (tmp_path/'public').exists()
    for name in source.urls():assert (stage/name).read_bytes()==b'invalid original response'
    failure=json.loads((stage/'failure.json').read_bytes())
    assert failure['error_type']=='ValueError'
    assert failure['protocol_sha256']==source.PROTOCOL_SHA
