"""Four-field/depth source integrity and common-time monthly arithmetic."""
import numpy as np
import pytest

from acquire_south_indian_hycom_hydrography import FIELDS, parse_ascii, common_means, check_metadata, METADATA


def response():
    text = 'Dataset {\n'
    for name in FIELDS:
        text += f'Int16 {name}[time = 1][depth = 2][lat = 2][lon = 2];\n'
    text += '}\n---\n'
    for name in FIELDS:
        text += f'{name}.{name}[1][2][2][2]\n'
        for z in range(2):
            for y in range(2):
                text += f'[0][{z}][{y}], 100, -30000\n'
        for n, size, values in [('time', 1, '113976'), ('depth', 2, '15, 1000'),
                                ('lat', 2, '-41, -40'), ('lon', 2, '80, 80.08')]:
            text += f'{name}.{n}[{size}]\n{values}\n'
    return text


def test_four_fields_and_two_depths_preserve_packed_values_and_maps():
    arrays = parse_ascii(response(), 1, 2, 2, 2)
    assert arrays['depth'].tolist() == [15, 1000]
    assert all(arrays[n].shape == (1, 2, 2, 2) and arrays[n].dtype.str == '<i2' for n in FIELDS)
    assert arrays['salinity'][0, 1, 1].tolist() == [100, -30000]


@pytest.mark.parametrize('old,new', [
    ('Int16 salinity', 'Float32 salinity'),
    ('[0][1][0], 100', '[0][0][0], 100'),
    ('100, -30000', '100, 32768'),
    ('100, -30000', '100'),
    ('water_temp.depth[2]\n15, 1000', 'water_temp.depth[2]\n15, 500'),
    ('salinity.lon[2]\n80, 80.08', 'salinity.lon[2]\n80.08, 80'),
    ('water_v.water_v[1][2][2][2]', 'water_v.water_u[1][2][2][2]'),
])
def test_rejects_field_depth_row_type_and_map_corruption(old, new):
    with pytest.raises(ValueError):
        parse_ascii(response().replace(old, new, 1), 1, 2, 2, 2)


def test_missing_salinity_excludes_same_time_from_both_velocities_and_temperature():
    fields = {n: np.array([[[[10]]], [[[20]]], [[[30]]]], dtype='<i2') for n in FIELDS}
    fields['salinity'][1] = -30000
    count, means = common_means(fields, 2, float(np.float32(.001)), {'water_u': 0., 'water_v': 0., 'water_temp': 20., 'salinity': 20.})
    assert count.item() == 2
    assert means['water_u'].item() == means['water_v'].item() == 20*float(np.float32(.001))
    assert means['water_temp'].item() == means['salinity'].item() == 20+20*float(np.float32(.001))
    _, unavailable = common_means(fields, 3, 1., dict.fromkeys(FIELDS, 20.))
    assert all(np.isnan(v).all() for v in unavailable.values())


def test_common_sum_uses_int64_without_int16_overflow():
    fields = {n: np.full((31, 2, 1, 1), 32767, dtype='<i2') for n in FIELDS}
    count, means = common_means(fields, 25, 1., dict.fromkeys(FIELDS, 0.))
    assert count.tolist() == [[[31]], [[31]]]
    assert all(v.tolist() == [[[32767.]], [[32767.]]] for v in means.values())


def test_retained_metadata_rejects_potential_temperature_and_changed_offsets():
    text = (METADATA/'metadata.das').read_text(encoding='utf8')
    check_metadata(text)
    for bad in [text.replace('sea_water_temperature', 'sea_water_potential_temperature'),
                text.replace('in-situ temperature', 'potential temperature'),
                text.replace('Float32 add_offset 20.0;', 'Float32 add_offset 0.0;', 1),
                text.replace('String units "psu";', 'String units "kg/kg";')]:
        with pytest.raises(ValueError):
            check_metadata(bad)
