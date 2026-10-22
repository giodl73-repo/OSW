"""Source acquisition guards: clock gaps, paired masks and strict DAP parsing."""
import numpy as np
import pytest
from copy import deepcopy

from acquire_indian_secc_hycom_2013 import coordinates, index_runs, paired_mean
from acquire_south_australian_hycom_2d import parse_ascii
from indian_secc_hycom_local_normals import stronger_candidate
from package_indian_secc_hycom_2013 import unpack_checked
import hashlib
import zipfile


@pytest.mark.parametrize('indices', [[], [7], [0, 8, 16, 23, 31, 39], [0, 8, 15, 23, 30], [1, 4]])
def test_runs_preserve_exact_indices_across_missing_times(indices):
    runs = index_runs(indices)
    assert [i for run in runs for i in run] == indices
    for run in runs:
        if len(run) > 1:
            assert list(range(run[0], run[-1]+1, run[1]-run[0])) == run


def test_components_share_valid_times_and_calendar_denominator():
    u = np.array([[[10, 10]], [[20, -30000]], [[-30000, 30]]], dtype='<i2')
    v = np.array([[[100, -30000]], [[200, 200]], [[300, 300]]], dtype='<i2')
    counts, mean_u, mean_v = paired_mean(u, v, 2, float(np.float32(.001)))
    assert counts.tolist() == [[2, 1]]
    assert mean_u[0, 0] == 15*float(np.float32(.001))
    assert mean_v[0, 0] == 150*float(np.float32(.001))
    assert np.isnan(mean_u[0, 1]) and np.isnan(mean_v[0, 1])


def test_int16_sum_does_not_overflow():
    a = np.full((31, 1, 1), 32767, dtype='<i2')
    counts, u, v = paired_mean(a, a, 25, 1.)
    assert counts.item() == 31 and u.item() == v.item() == 32767


def coordinate_text():
    return 'Dataset {\n}\n---\ntime[2]\n1, 2\n\ndepth[1]\n15\n\nlat[2]\n-1, 0\n\nlon[2]\n75, 76\n'


def test_coordinate_response_rejects_truncation_duplicates_and_order():
    assert coordinates(coordinate_text())['depth'].tolist() == [15]
    for bad in [coordinate_text().replace('1, 2', '1'),
                coordinate_text().replace('75, 76', '76, 75'),
                coordinate_text().replace('lon[2]', 'lat[2]'),
                coordinate_text().replace('75, 76', 'nan, 76')]:
        with pytest.raises(ValueError):
            coordinates(bad)


def cube_text():
    declaration = 'Dataset {\n'+''.join(f'Int16 {v}[time = 1][depth = 1][lat = 1][lon = 2];\n' for v in ['water_u', 'water_v'])+'}\n'
    body = ''
    for v in ['water_u', 'water_v']:
        body += f'{v}.{v}[1][1][1][2]\n[0][0][0], 10, -30000\n'
        for name, values, size in [('time', '1', 1), ('depth', '15', 1), ('lat', '-1', 1), ('lon', '75, 76', 2)]:
            body += f'{v}.{name}[{size}]\n{values}\n'
    return declaration+body


def test_packed_response_rejects_wrong_rows_types_dimensions_and_maps():
    raw = cube_text()
    assert parse_ascii(raw, 1, 1, 2)['water_u'].tolist() == [[[10, -30000]]]
    for bad in [raw.replace('[0][0][0],', '[1][0][0],', 1),
                raw.replace('Int16 water_u', 'Float32 water_u'),
                raw.replace('10, -30000', '10, -30000, 2', 1),
                raw.replace('water_v.lon[2]\n75, 76', 'water_v.lon[2]\n75, 77'),
                raw.replace('10, -30000', '32768, -30000', 1)]:
        with pytest.raises(ValueError):
            parse_ascii(bad, 1, 1, 2)


def test_axis_pass_does_not_bypass_edge_resolution_or_hemisphere_gates():
    pair = [{'normal_sample_step_km': step, 'primary_seed': True,
             'all_five_local_axis_checks_pass': True,
             'stations': [{'threshold_cases': [{}, {'status': 'paired_sampled_edges',
                           'resolution_review_required': False,
                           'any_edge_at_or_north_of_equator': False}]} for _ in range(5)]}
            for step in [5, 10]]
    assert stronger_candidate(pair)
    for key, value in [('status', 'unresolved_edge_pair'), ('resolution_review_required', True),
                       ('resolution_review_required', None), ('any_edge_at_or_north_of_equator', True)]:
        bad = deepcopy(pair)
        bad[1]['stations'][4]['threshold_cases'][1][key] = value
        assert not stronger_candidate(bad)
    bad = deepcopy(pair)
    bad[0]['all_five_local_axis_checks_pass'] = False
    assert not stronger_candidate(bad)
    assert not stronger_candidate(pair[:1])


@pytest.mark.parametrize('name', ['../escape', 'nested/file', 'nested\\file'])
def test_retained_archive_cannot_write_outside_its_target(tmp_path, name):
    archive = tmp_path/'source.zip'
    raw = b'not a source response'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr(name, raw)
    with pytest.raises(ValueError, match='Unsafe|member set'):
        unpack_checked(archive, {name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}}, tmp_path)


def test_retained_archive_rejects_extra_or_changed_bytes(tmp_path):
    archive = tmp_path/'source.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('source.ascii', b'changed')
    with pytest.raises(ValueError, match='checksum'):
        unpack_checked(archive, {'source.ascii': {'bytes': 7, 'sha256': '0'*64}}, tmp_path)
    with pytest.raises(ValueError, match='member set'):
        unpack_checked(archive, {}, tmp_path)
