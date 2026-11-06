"""Tiny synthetic observations only; no provider access or original archive."""
import json
import numpy as np
from netCDF4 import Dataset
import pytest

import audit_osnap_wg_sample_support_v1 as audit


def test_local_refusal_precedes_original_or_preflight_access(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(audit, 'verify_preflight', lambda: pytest.fail('Local source access'))
    with pytest.raises(RuntimeError, match='cloud-only'):
        audit.main(['--cloud-audit'])


def test_implicit_cloud_run_refused(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    with pytest.raises(RuntimeError):
        audit.main([])


def test_time_months_include_empty_february():
    r, labels, available = audit.audit_time(np.array([0, 59.5]))
    assert r['months'] == ['1950-01', '1950-02', '1950-03']
    assert labels.tolist() == ['1950-01', '1950-03']
    assert available.tolist() == [True, True]
    assert r['first_utc'] == '1950-01-01T00:00:00.000000Z'
    assert r['last_utc'] == '1950-03-01T12:00:00.000000Z'


def test_time_mask_does_not_create_a_bridged_cadence():
    r, labels, _ = audit.audit_time(np.ma.array([0, 1, 2], mask=[0, 1, 0]))
    assert r['available_rows'] == 2 and labels[1] == ''
    assert r['adjacent_pairs_with_available_time'] == 0
    assert r['median_positive_adjacent_interval_seconds'] is None
    assert not r['all_rows_available_and_strictly_increasing']


def test_time_duplicates_backwards_and_nonadjacent_duplicates_are_reported():
    r, _, _ = audit.audit_time([0, 1, 1, 0, 3])
    assert r['duplicate_adjacent_times'] == 1
    assert r['duplicate_available_times'] == 2
    assert r['backwards_adjacent_times'] == 1
    assert not r['all_rows_available_and_strictly_increasing']


@pytest.mark.parametrize('data', [[], [[0, 1]], [-1], [90001]])
def test_unsupported_time_ranges_and_dimensions_refused(data):
    with pytest.raises(ValueError):
        audit.audit_time(data)


def test_no_available_times_preserves_empty_support():
    r, labels, available = audit.audit_time(np.ma.masked_all(3))
    assert r['first_utc'] is None and r['months'] == []
    assert labels.tolist() == ['', '', ''] and not available.any()


def test_velocity_pairing_is_per_cell_not_per_profile():
    u = np.ma.array([[1, 2], [3, 4]], mask=[[0, 1], [0, 0]])
    v = np.ma.array([[1, 2], [3, 4]], mask=[[1, 0], [0, 0]])
    r = audit.paired_support(u, v, [True, True])
    assert r['total_cells'] == 4 and r['paired_available_cells'] == 2
    assert r['profiles_with_any_pair'] == 1
    assert r['profiles_with_all_bins_paired'] == 1
    assert r['paired_counts_by_bin'] == [1, 1]


def test_velocity_invalid_time_and_missing_depth_are_distinct():
    depth = np.ma.array([[10, 20], [30, 40]], mask=[[0, 1], [0, 0]])
    r = audit.paired_support([[1, 2], [3, 4]], [[1, 2], [3, 4]], [True, False], depth)
    assert r['paired_available_cells'] == 2
    assert r['paired_with_supplied_time_varying_depth_cells'] == 1


def test_nonfinite_is_never_zero_filled():
    r = audit.paired_support([[0, np.nan, np.inf]], [[0, 1, 2]], [True])
    assert r['paired_available_cells'] == 1
    assert r['u']['unmasked_nonfinite_cells'] == 2


@pytest.mark.parametrize('u,v,ta,depth', [([[1]], [[1, 2]], [True], None),
                                       ([1], [1], [True], None),
                                       ([[1]], [[1]], [], None),
                                       ([[1]], [[1]], [True], [[1, 2]])])
def test_incompatible_axes_are_not_broadcast(u, v, ta, depth):
    with pytest.raises(ValueError):
        audit.paired_support(u, v, ta, depth)


def synthetic_dataset(path, adcp=False):
    with Dataset(path, 'w', format='NETCDF3_CLASSIC') as d:
        d.createDimension('TIME', 3)
        d.createDimension('BINDEPTH' if adcp else 'DEPTH', 2 if adcp else 1)
        d.createDimension('LATITUDE', 1);d.createDimension('LONGITUDE', 1)
        def variable(name, dims, units, values, standard_name=None):
            v = d.createVariable(name, 'f8', dims, fill_value=99999)
            v.units = units
            if standard_name:v.standard_name = standard_name
            v[:] = values
            return v
        variable('TIME', ('TIME',), audit.EPOCH_UNITS, [0, 0.5, 1])
        variable('LATITUDE', ('LATITUDE',), 'degree_north', [59.8])
        variable('LONGITUDE', ('LONGITUDE',), 'degree_east', [-45.7])
        axes = ('TIME', 'BINDEPTH' if adcp else 'DEPTH')
        if adcp:
            variable('DEPTH', axes, 'meters', [[10, 20], [12, 22], [14, 24]])
            variable('BINDEPTH', ('BINDEPTH',), 'meter', [10, 20])
        else:
            variable('DEPTH', ('DEPTH',), 'meter', [250])
        variable('PRES', axes, 'decibar', [[10, 20], [12, 22], [14, 24]] if adcp else [[250], [260], [270]])
        variable('UCUR', axes, 'meter/second', [[1, 99999], [2, 3], [4, 5]] if adcp else [[0], [99999], [1]], 'eastward_sea_water_velocity')
        variable('VCUR', axes, 'meter/second', [[1, 2], [3, 4], [5, 6]] if adcp else [[0], [1], [1]], 'northward_sea_water_velocity')


def test_actual_netcdf_point_meter_keeps_pressure_and_nominal_depth_separate(tmp_path):
    path = tmp_path / 'synthetic.nc';synthetic_dataset(path)
    with Dataset(path) as d:r = audit.audit_dataset(d)
    assert r['nominal_depth']['values_m'] == [250]
    assert r['pressure_proxy_decibar']['max'] == 270
    assert not r['pressure_proxy_decibar']['converted_to_depth']
    assert r['velocity_availability']['paired_available_cells'] == 2
    assert r['monthly'][0]['supplied_time_varying_depth_m'] is None
    assert r['coordinates']['station_position_available']
    assert not r['physical_qc_validity_established']
    json.dumps(r, allow_nan=False)


def test_actual_netcdf_adcp_uses_supplied_moving_depth(tmp_path):
    path = tmp_path / 'synthetic.nc';synthetic_dataset(path, adcp=True)
    with Dataset(path) as d:r = audit.audit_dataset(d)
    assert r['nominal_depth'] is None
    assert r['supplied_depth']['time_varying']
    assert r['monthly'][0]['supplied_time_varying_depth_m']['max'] == 24
    assert r['velocity_availability']['paired_with_supplied_time_varying_depth_cells'] == 5
    assert r['source_depth_coordinates']['BINDEPTH']['values'] == [10, 20]


def test_masked_extra_coordinate_does_not_become_a_singleton_position(tmp_path):
    path = tmp_path / 'synthetic.nc';synthetic_dataset(path)
    with Dataset(path, 'r+') as d:
        d.createDimension('extra_positions', 2)
        # Keep the old name as a different variable, then create the bad coordinate.
        d.renameVariable('LATITUDE', 'original_latitude')
        v = d.createVariable('LATITUDE', 'f8', ('extra_positions',), fill_value=99999)
        v[:] = [59.8, 99999]
    with Dataset(path) as d:r = audit.coordinates(d)
    assert not r['station_position_available']
    assert r['LATITUDE']['values'] == [59.8]


@pytest.mark.parametrize('mutation', ['unit', 'calendar', 'direction'])
def test_actual_netcdf_unreviewed_variable_identity_rejects(tmp_path, mutation):
    path = tmp_path / 'synthetic.nc';synthetic_dataset(path)
    with Dataset(path, 'r+') as d:
        if mutation == 'unit':d.variables['UCUR'].units = 'cm/second'
        if mutation == 'calendar':d.variables['TIME'].calendar = '360_day'
        if mutation == 'direction':d.variables['VCUR'].standard_name = 'eastward_sea_water_velocity'
    with Dataset(path) as d, pytest.raises(ValueError):
        audit.audit_dataset(d)


def test_exact_source_custody_is_required_before_archive_access(tmp_path):
    (tmp_path / 'acquisition.json').write_text('{"changed": true}')
    with pytest.raises(ValueError, match='custody'):
        audit.verify_restored_source(tmp_path, {}, {}, {})


def test_decoded_array_budget_precedes_materialization():
    class OverBudget:
        dtype = np.dtype('float64')
        shape = (100000000,)
        def __getitem__(self, key):pytest.fail('Over-budget variable read')
    with pytest.raises(ValueError, match='budget'):
        audit.read_array(OverBudget())
