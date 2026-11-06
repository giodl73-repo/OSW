"""Synthetic recursion, inherited dimension, packing and exact retention."""
import netCDF4
import numpy as np

import caribbean_ru29_source_fields_v2 as subject


def test_nested_virtual_groups_and_inherited_dimensions(tmp_path):
    path = tmp_path/'groups.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createDimension('parent_obs', 2)
        ds.createVariable('root', 'i4', ('parent_obs',))[:] = [1, 2]
        for name in ['LastVirtualObs', 'LastPreviousVirtualObs']:
            group = ds.createGroup(name)
            group.comment = 'Preserve state; not an observed eddy footprint'
            var = group.createVariable('track', 'u4', ('parent_obs',))
            var[:] = [7, 4294967294]
            child = group.createGroup('nested')
            label = child.createVariable('label', str, ('parent_obs',))
            label[0], label[1] = 'state', ''
    result = subject.read_member(path)
    assert list(result['groups']) == ['LastVirtualObs', 'LastPreviousVirtualObs']
    for group in result['groups'].values():
        assert group['dimensions'] == {}
        assert group['variables']['track']['dimensions'] == ['parent_obs']
        assert group['variables']['track']['raw_values'] == [7, 4294967294]
        assert group['groups']['nested']['variables']['label']['raw_values'] == ['state', '']
    summary = subject.summary(result)
    assert summary['groups']['LastVirtualObs']['variables']['track']['value_count'] == 2
    assert summary['groups']['LastPreviousVirtualObs']['path'] == '/LastPreviousVirtualObs'


def test_nested_packing_masks_and_no_clipping(tmp_path):
    path = tmp_path/'packed.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        group = ds.createGroup('state')
        group.createDimension('obs', 3)
        var = group.createVariable('velocity', 'i2', ('obs',), fill_value=-999)
        var.scale_factor = np.float64(.01)
        var.set_auto_maskandscale(False)
        var[:] = [-999, -60, 90]
    variable = subject.read_member(path)['groups']['state']['variables']['velocity']
    assert variable['raw_values'] == [-999, -60, 90]
    assert variable['decoded_mask'] == [True, False, False]
    assert variable['attributes']['scale_factor']['value'] == .01
    assert subject.summary(subject.read_member(path))['groups']['state']['variables']['velocity']['raw_maximum'] == 90
