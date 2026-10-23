"""Synthetic native arrays only; fixed before processing the actual source cells."""
import gzip
import json

import numpy as np
import pytest
from netCDF4 import Dataset
from angola_nansen_native_sections import array_values, compressed, encoded, section, TIME_ATTRS, UNITS


def test_lossless_finite_signed_zero_and_nan_positions():
    values=np.array([[1.2345678901234567, np.nan],[-0.0,2**-100]],dtype='float64')
    result,summary=array_values(values)
    decoded=json.loads(encoded(result))
    assert decoded[0][1] is None and np.signbit(decoded[1][0])
    assert decoded[0][0]==values[0,0] and decoded[1][1]==values[1,1]
    assert summary=={'cells':4,'finite':3,'missing':1,'finite_range':[-0.0,1.2345678901234567]}


def test_all_missing_keeps_shape_and_no_numeric_range():
    values,summary=array_values(np.full((2,3),np.nan,dtype='float64'))
    assert values==[[None,None,None],[None,None,None]]
    assert summary=={'cells':6,'finite':0,'missing':6,'finite_range':None}


@pytest.mark.parametrize('bad',[np.array([np.inf]),np.array([-np.inf]),np.array([1],dtype='float32'),np.ma.array([2.0],mask=[True])])
def test_unsupported_values_and_masks_rejected(bad):
    with pytest.raises(ValueError):array_values(bad)


def test_deterministic_gzip_and_strict_json():
    raw=encoded({'finite':[-0.0,1.2345678901234567],'missing':None})
    assert compressed(raw)==compressed(raw) and gzip.decompress(compressed(raw))==raw
    assert compressed(raw)[4:8]==b'\0'*4 and compressed(raw)[9]==255
    with pytest.raises(ValueError):encoded({'bad':float('nan')})


def source_fixture(path,change=None):
    with Dataset(path,'w') as d:
        d.createDimension('PROFILE',2);d.createDimension('DEPTH',3)
        for name,unit in UNITS.items():
            dims=('PROFILE','DEPTH') if name in ['U_CUR','V_CUR'] else ('DEPTH',) if name=='DEPTH' else ('PROFILE',)
            if change=='dimensions' and name=='V_CUR':dims=('DEPTH','PROFILE')
            v=d.createVariable(name,'f8',dims)
            for key,value in (TIME_ATTRS if name=='TIME' else {'units':unit}).items():v.setncattr(key,value)
            if change=='units' and name=='V_CUR':v.units='cm/s'
            if change=='quality_attribute' and name=='V_CUR':v.quality='unknown'
            v[:]=np.zeros(v.shape,dtype='float64')
            if name=='U_CUR':v[0,0]=np.nan
        if change=='extra_variable':d.createVariable('QC','f8',('PROFILE',))
    return path.read_bytes()


def test_synthetic_section_keeps_unequal_masks_and_all_native_cells(tmp_path):
    raw=source_fixture(tmp_path/'native.nc');result=section(raw,'synthetic')
    assert result['dimensions']=={'PROFILE':2,'DEPTH':3}
    assert result['variables']['U_CUR']['values']==[[None,0.0,0.0],[0.0,0.0,0.0]]
    assert result['variables']['V_CUR']['summary']['finite']==6
    assert result['component_mask_disagreements']==1
    assert result['time_zone']=='not_explicit_in_source'
    assert not result['physical_width_admitted'] and not result['velocity_rotation_applied']


@pytest.mark.parametrize('change',['dimensions','units','quality_attribute','extra_variable'])
def test_changed_native_schema_cannot_be_silently_reinterpreted(tmp_path,change):
    with pytest.raises(ValueError):section(source_fixture(tmp_path/'bad.nc',change),'synthetic')
