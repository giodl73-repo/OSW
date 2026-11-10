"""Synthetic source-retention and scientific display contract tests only."""
import copy
import json

import netCDF4
import numpy as np
import pytest

import caribbean_ru29_source_fields_v1 as subject


def test_packed_originals_masks_and_attributes(tmp_path):
    path = tmp_path/'packed.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createDimension('obs', 3)
        var = ds.createVariable('radius', 'i2', ('obs',), fill_value=-999)
        var.units = 'm'
        var.scale_factor = np.float64(50)
        var.add_offset = np.float64(2)
        var.set_auto_maskandscale(False)
        var[:] = [2, -999, 4]
    v = subject.read_member(path)['variables']['radius']
    assert v['raw_values'] == [2, -999, 4]
    assert v['decoded_mask'] == [False, True, False]
    assert v['attributes']['scale_factor']['value'] == 50
    assert v['attributes']['units']['value'] == 'm'
    assert subject.summarize(v)['raw_minimum'] == -999


def test_nan_infinity_and_exact_nanosecond_integer(tmp_path):
    path = tmp_path/'precision.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createDimension('x', 3)
        ds.createVariable('velocity', 'f8', ('x',), fill_value=np.nan)[:] = [np.nan, np.inf, -np.inf]
        ds.createVariable('clock', 'i8', ('x',))[:] = [2**60+1, 2**60+2, 2**60+3]
    out = subject.read_member(path)['variables']
    assert out['velocity']['raw_values'] == ['NaN', 'Infinity', '-Infinity']
    assert out['velocity']['decoded_mask'] == [True, False, False]
    assert out['clock']['raw_values'][0] == 2**60+1
    assert json.loads(subject.encoded(out)) == out


def test_vlen_filenames_and_unlimited_dimension(tmp_path):
    path = tmp_path/'links.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createDimension('step', None)
        var = ds.createVariable('FileIn', str, ('step',))
        var[0] = '/author/path/day1.nc'
        var[1] = ''
        ds.note = 'Retain original path as source metadata, never execute it'
    out = subject.read_member(path)
    assert out['dimensions']['step'] == {'length': 2, 'unlimited': True}
    assert out['variables']['FileIn']['raw_values'] == ['/author/path/day1.nc', '']
    assert out['variables']['FileIn']['decoded_mask'] == [False, False]


def test_correspondence_fill_and_virtual_preserved(tmp_path):
    path = tmp_path/'virtual.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createDimension('link', 3)
        ds.createVariable('virtual', 'u1', ('link',), fill_value=255)[:] = [0, 1, 255]
    v = subject.read_member(path)['variables']['virtual']
    assert v['raw_values'] == [0, 1, 255]
    assert v['decoded_mask'] == [False, False, True]


@pytest.mark.parametrize('values', [[1], [1, 1], [2, 1], [0, np.nan], [[1, 2]]])
def test_invalid_display_coordinates_rejected(values):
    with pytest.raises(ValueError):
        subject.edges(values)


def test_display_edges_and_scale():
    assert subject.edges([10, 12, 14]).tolist() == [9, 11, 13, 15]
    assert subject.color(-.5) == subject.color(-5)
    assert subject.color(.5) == subject.color(5)
    assert subject.color(np.nan) == '#d1d5db'
    assert subject.color(0) == '#f8f8f8'
    assert subject.color(-.2) != subject.color(.2)


def test_figure_retains_cells_and_missing_and_states_clipping():
    variables = {key: {'raw_values': value, 'decoded_mask': [[False]*2]*2}
                 for key, value in {'u_grid': [[-.6, .1], [.2, 'NaN']],
                                    'v_grid': [[0, -.1], [.5, -.7]]}.items()}
    variables.update({'latitude': {'raw_values': [12, 13]}, 'depth': {'raw_values': [10, 20]}})
    members = {f'adcp-transect-{n}.nc': {'variables': copy.deepcopy(variables)} for n in [1, 2]}
    svg = subject.figure(members).decode('utf8')
    assert svg.count('<rect ') == 16+200+1
    assert svg.count('fill="#d1d5db"') == 2
    assert '[1, 1, 1, 1]' in svg
    assert 'full width, depth and seasonal coverage incomplete' in svg


def test_nested_group_rejected(tmp_path):
    path = tmp_path/'group.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createGroup('unhandled')
    with pytest.raises(ValueError, match='Nested groups'):
        subject.read_member(path)


def test_pin_mismatch_fails_before_arrays_or_products(tmp_path, monkeypatch):
    preflight = tmp_path/subject.PREFLIGHT
    preflight.parent.mkdir(parents=True)
    preflight.write_text('{"input_sha256":{"a":"expected"}}', encoding='utf8')
    monkeypatch.setattr(subject, 'pins', lambda root: {'a': 'changed'})
    monkeypatch.setattr(subject, 'read_member', lambda path: pytest.fail('must not read arrays'))
    with pytest.raises(ValueError, match='pins changed'):
        subject.products(tmp_path)
    assert not (tmp_path/subject.MIRROR).exists()
