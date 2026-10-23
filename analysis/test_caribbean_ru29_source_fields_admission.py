"""Independent actual-original comparison; does not call the frozen producer."""
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'research/source-data/caribbean-ru29-2024-v1'


def restored(value):
    if isinstance(value, list):
        return [restored(v) for v in value]
    if isinstance(value, dict) and set(value) == {'bytes_hex'}:
        return bytes.fromhex(value['bytes_hex'])
    if value in ('NaN', 'Infinity', '-Infinity') if isinstance(value, str) else False:
        return {'NaN': float('nan'), 'Infinity': float('inf'), '-Infinity': -float('inf')}[value]
    return value


def compare_group(original, saved, summary):
    assert saved['path'] == original.path == summary['path']
    assert set(saved['variables']) == set(original.variables) == set(summary['variables'])
    assert set(saved['groups']) == set(original.groups) == set(summary['groups'])
    assert set(saved['dimensions']) == set(original.dimensions)
    assert set(saved['attributes']) == set(original.ncattrs())
    for name in original.ncattrs():
        np.testing.assert_equal(np.asarray(restored(saved['attributes'][name]['value'])), np.asarray(original.getncattr(name)))
    variables, cells = 0, 0
    for name, var in original.variables.items():
        item = saved['variables'][name]
        var.set_auto_chartostring(False)
        mask = np.ma.getmaskarray(var[:])
        var.set_auto_maskandscale(False)
        raw = np.asarray(var[:])
        np.testing.assert_equal(np.asarray(restored(item['raw_values']), dtype=raw.dtype), raw)
        np.testing.assert_equal(np.asarray(item['decoded_mask'], dtype=bool), mask)
        assert item['shape'] == list(var.shape)
        assert item['dimensions'] == list(var.dimensions)
        assert item['dtype'] == str(var.dtype)
        assert set(item['attributes']) == set(var.ncattrs())
        for attr in var.ncattrs():
            expected = np.asarray(var.getncattr(attr))
            assert item['attributes'][attr]['dtype'] == str(expected.dtype)
            np.testing.assert_equal(np.asarray(restored(item['attributes'][attr]['value']), dtype=expected.dtype), expected)
        assert summary['variables'][name]['value_count'] == raw.size
        assert summary['variables'][name]['decoded_masked_count'] == int(mask.sum())
        variables += 1
        cells += raw.size
    for name, group in original.groups.items():
        v, c = compare_group(group, saved['groups'][name], summary['groups'][name])
        variables += v
        cells += c
    return variables, cells


def test_every_original_cell_attribute_group_and_mask_retained():
    raw = (ROOT/'research/caribbean-ru29-source-fields-v2.json').read_bytes()
    mirror = json.loads(raw)
    report = json.loads((ROOT/'research/caribbean-ru29-source-inventory-v2.json').read_bytes())
    assert report['mirror_sha256'] == hashlib.sha256(raw).hexdigest()
    custody = json.loads((SOURCE/'custody.json').read_bytes())
    assert set(mirror['members']) == set(report['members']) == {m['alias'] for m in custody['members']}
    variables, cells = 0, 0
    for member in custody['members']:
        path = SOURCE/member['alias']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == member['sha256']
        with netCDF4.Dataset(path) as original:
            v, c = compare_group(original, mirror['members'][member['alias']], report['members'][member['alias']])
        variables += v
        cells += c
    assert variables == 306
    assert cells == 3609111
    assert report['whole_current_length_measured'] is False
    assert report['physical_current_width_measured'] is False
    assert report['seasonal_envelope_measured'] is False
    assert report['eddy_pipeline_reproduced'] is False


def test_lazy_page_retains_both_complete_occupation_records():
    raw = (ROOT/'research/caribbean-ru29-source-fields-v2.json').read_bytes()
    mirror = json.loads(raw)
    page = json.loads((ROOT/'research/caribbean-ru29-source-page-v1.json').read_bytes())
    assert page['source_sha256'] == hashlib.sha256(raw).hexdigest()
    assert len(page['occupations']) == 2
    for n, occupation in enumerate(page['occupations'], 1):
        assert occupation['source_member'] == f'adcp-transect-{n}.nc'
        assert occupation['source_group'] == mirror['members'][occupation['source_member']]
