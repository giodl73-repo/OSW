"""Source-operator guards and tiny synthetic deployment; no originals."""
import math
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from netCDF4 import Dataset

import build_west_greenland_core_width_v1 as operator


def test_local_guard_precedes_preflight_originals_and_numeric_work(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(operator, 'verify_preflight', lambda: pytest.fail('Local original access'))
    with pytest.raises(RuntimeError, match='cloud-only'):operator.main(['--cloud-core-width'])


def test_cloud_requires_explicit_execution_flag(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    with pytest.raises(RuntimeError):operator.main([])


def fake_headers():
    return {'instrument_headers': [{'member': f'LS{i}/no-extension-{i}',
                                    'header': {'variables': {'UCUR': {}, 'BINDEPTH': {}}}}
                                   for i in range(1, 9)]}


def test_selection_is_schema_and_station_based_not_suffix_based():
    data = fake_headers()
    data['instrument_headers'].append({'member': 'LS7/point-meter.nc', 'header': {'variables': {'UCUR': {}}}})
    selected = operator.selected_adcp_headers(data)
    assert list(selected) == operator.STATIONS
    assert selected['LS7']['member'] == 'LS7/no-extension-7'


@pytest.mark.parametrize('change', ['duplicate', 'missing', 'foreign_station'])
def test_ambiguous_adcp_selection_rejects(change):
    data = fake_headers()
    if change == 'duplicate':data['instrument_headers'].append(data['instrument_headers'][0])
    if change == 'missing':data['instrument_headers'].pop()
    if change == 'foreign_station':data['instrument_headers'][0]['member'] = 'LS9/outside.nc'
    with pytest.raises(ValueError):operator.selected_adcp_headers(data)


def synthetic_instruments():
    from pyproj import Geod
    hours = np.arange(np.datetime64('2017-01-01', 'h'), np.datetime64('2017-02-01', 'h'), np.timedelta64(1, 'h'))
    indices = (hours - np.datetime64('1950-01-01', 'h')).astype('timedelta64[h]').astype('int64')
    geod = Geod(ellps='WGS84');result = {}
    profile = [-.1, 0, .5, 1, .5, 0, -.1, -.2]
    for index, name in enumerate(operator.STATIONS):
        km = (index - 3) * 10
        bearing = operator.method.BEARING_DEGREES_TRUE - 90 + (180 if km < 0 else 0)
        lon, lat, _ = geod.fwd(-46, 59.6, bearing, abs(km) * 1000)
        coordinates = {key: {'values': [value], 'attributes': {'reference': 'WGS84', 'uncertainty': .004}}
                       for key, value in [('LONGITUDE', lon), ('LATITUDE', lat)]}
        result[name] = {'coordinates': coordinates, 'hour_indices': indices,
                        'alignment_offsets_seconds': np.zeros(len(indices)),
                        'along_m_s': np.full(len(indices), profile[index]), 'cross_m_s': np.zeros(len(indices)),
                        'layer_reasons': ['available_layer'] * len(indices), 'member': name + '/synthetic',
                        'sha256': 'synthetic-not-an-original'}
    return result


def test_synthetic_deployment_retains_all_hours_support_and_thresholds():
    result, traces = operator.build_diagnostic(synthetic_instruments())
    assert result['station_order'] == operator.STATIONS and result['hour_grid_rows'] == 744
    row = result['months'][0]
    assert row['eligible_for_core_span'] and row['common_available_hours'] == 528
    nominal = row['threshold_results'][1]
    assert nominal['status'] == 'resolved_regional_core_span'
    assert nominal['span_km'] == pytest.approx(20, abs=1e-8)
    assert len(row['threshold_results']) == 3
    assert nominal['left_bracket_stations'] and nominal['right_bracket_stations']
    assert traces['filtered_layer_along_m_s'].shape == (744, 8)
    assert traces['joint_available_hours'].sum() == 528
    assert traces['ls1_layer_reason_codes'].shape == (744,)


def test_original_station_identity_order_is_not_replaced_by_geographic_sort():
    instruments = synthetic_instruments()
    instruments['LS1']['coordinates'], instruments['LS8']['coordinates'] = instruments['LS8']['coordinates'], instruments['LS1']['coordinates']
    with pytest.raises(ValueError, match='offshore'):operator.section_coordinates(instruments)


def test_missing_station_is_not_substituted_in_complete_deployment():
    data = synthetic_instruments();data.pop('LS1')
    with pytest.raises(ValueError):operator.build_diagnostic(data)


def test_unsupported_month_keeps_all_sensitivity_failures_and_null_values():
    data = synthetic_instruments();data['LS1']['along_m_s'][:] = np.nan
    result, _ = operator.build_diagnostic(data)
    row = result['months'][0]
    assert not row['eligible_for_core_span']
    assert [r['fraction_of_peak'] for r in row['threshold_results']] == [.4, .5, .6]
    assert all(r['status'] == 'monthly_support_insufficient' and r['span_km'] is None for r in row['threshold_results'])
    figure = operator.diagnostic_svg(result)
    ET.fromstring(figure)
    assert b'support fail' in figure and b'not whole-current width' in figure


def netcdf_fixture(path):
    with Dataset(path, 'w', format='NETCDF3_CLASSIC') as d:
        for name, count in [('TIME', 3), ('BINDEPTH', 4), ('LATITUDE', 1), ('LONGITUDE', 1)]:d.createDimension(name, count)
        def variable(name, dims, units, values, standard=None):
            v = d.createVariable(name, 'f8', dims, fill_value=99999);v.units = units;v[:] = values
            if standard:v.standard_name = standard
            return v
        variable('TIME', ('TIME',), operator.support.EPOCH_UNITS, [0, 1 / 24, 2 / 24])
        for name, value, units in [('LATITUDE', 59.6, 'degree_north'), ('LONGITUDE', -46, 'degree_east')]:
            v = variable(name, (name,), units, [value]);v.reference = 'WGS84'
        axes = ('TIME', 'BINDEPTH')
        variable('DEPTH', axes, 'meters', [[40, 60, 80, 100]] * 3)
        variable('UCUR', axes, 'meter/second', [[0] * 4] * 3, 'eastward_sea_water_velocity')
        variable('VCUR', axes, 'meter/second', [[1] * 4] * 3, 'northward_sea_water_velocity')


def test_actual_synthetic_netcdf_reader_uses_moving_layer_and_surveyed_positions(tmp_path):
    path = tmp_path / 'synthetic.nc';netcdf_fixture(path)
    with Dataset(path) as dataset:row = operator.read_adcp(dataset)
    assert row['hour_indices'].tolist() == [0, 1, 2]
    assert row['layer_reasons'] == ['available_layer'] * 3
    assert row['along_m_s'].tolist() == pytest.approx([math.cos(math.radians(318.1))] * 3)
    assert row['coordinates']['LATITUDE']['values'] == [59.6]


@pytest.mark.parametrize('change', ['velocity_units', 'datum', 'calendar', 'nominal_depth'])
def test_actual_synthetic_netcdf_reader_rejects_identity_changes(tmp_path, change):
    path = tmp_path / 'synthetic.nc';netcdf_fixture(path)
    with Dataset(path, 'r+') as d:
        if change == 'velocity_units':d.variables['UCUR'].units = 'centimeter/second'
        if change == 'datum':d.variables['LATITUDE'].reference = 'unspecified'
        if change == 'calendar':d.variables['TIME'].calendar = '360_day'
        if change == 'nominal_depth':d.variables['DEPTH'].units = 'nominal_labels'
    with Dataset(path) as dataset, pytest.raises(ValueError):operator.read_adcp(dataset)
