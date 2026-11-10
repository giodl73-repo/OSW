"""Original surrounding vectors, paired means, masks and old-section identity."""
import copy
import io
import json
import zipfile

import numpy as np
import pytest

from acquire_west_australian_oscar_2d import ROOT, DIRECTORY, baseline, load, parse
from build_west_australian_oscar_2d_source import REPORT, build, monthly


@pytest.fixture(scope='module')
def original():
    with zipfile.ZipFile(DIRECTORY/'source-responses.zip') as archive:
        return archive.read('metadata.json'), archive.read('vectors.csv'), baseline()


def test_exact_source_and_monthly_support():
    arrays, quality = load()
    assert quality['vector_positions'] == 304200
    assert quality['finite_pairs'] == 299088
    assert quality['both_missing'] == 5112 and quality['one_component_missing'] == 0
    assert quality['comparison_section_finite_bits_and_masks_exact'] is True
    stored = json.loads((ROOT/REPORT).read_bytes())
    assert stored == build()
    frames = stored['months']
    assert len(frames) == 12
    assert sorted(i for f in frames for i in f['source_time_indices']) == list(range(72))
    for frame in frames:
        ix = frame['source_time_indices']
        pairs = np.isfinite(arrays['u'][ix]) & np.isfinite(arrays['v'][ix])
        np.testing.assert_array_equal(frame['paired_samples'], pairs.sum(axis=0))
        for key, field in [('eastward_m_s','u'), ('northward_m_s','v')]:
            actual = np.array(frame[key], dtype=float)
            selected = np.where(pairs, arrays[field][ix], np.nan)
            total = np.nansum(selected, axis=0)
            counts = pairs.sum(axis=0)
            expected = np.full_like(total, np.nan)
            np.divide(total, counts, out=expected, where=counts >= 5)
            np.testing.assert_array_equal(np.isnan(actual), np.isnan(expected))
            # Forward-error bound for independent finite IEEE sums/division.
            # Relative-only tolerances are inappropriate near cancellation to zero.
            absolute_sum = np.nansum(np.abs(selected), axis=0)
            bound = np.finfo(float).eps*(len(ix)+2)*absolute_sum/np.maximum(counts,1)
            finite = np.isfinite(expected)
            assert np.all(np.abs(actual[finite]-expected[finite]) <= bound[finite])
    assert stored['old_monthly_finite_bits_masks_and_counts_exact'] is True
    assert stored['whole_current_width_km'] is None and stored['whole_current_length_km'] is None


@pytest.mark.parametrize('mutation', ['header', 'units', 'clock', 'infinite', 'duplicate', 'missing_last', 'changed_old_value', 'changed_old_mask'])
def test_changed_source_rejected(original, mutation):
    metadata, raw, previous = original
    lines = raw.decode().splitlines()
    if mutation == 'header': lines[0] = lines[0].replace('longitude','x')
    elif mutation == 'units': lines[1] = lines[1].replace('m s-1','cm s-1')
    elif mutation == 'missing_last': lines.pop()
    elif mutation == 'duplicate': lines[3] = lines[2]
    else:
        i = 2+12*169 if mutation.startswith('changed_old') else 2
        row = lines[i].split(',')
        if mutation == 'clock': row[0] = '2013-01-02T00:00:00Z'
        elif mutation == 'infinite': row[4] = 'Infinity'
        elif mutation == 'changed_old_mask': row[4] = 'NaN'
        else: row[4] = str(float(row[4])+.001)
        lines[i] = ','.join(row)
    with pytest.raises(ValueError): parse(metadata, ('\n'.join(lines)+'\n').encode(), previous)


def test_means_use_paired_support_and_do_not_mutate_inputs():
    times = [f'2013-01-{day:02d}T00:00:00Z' for day in range(1, 7)]
    u = np.ones((6,25,169)); v = np.full_like(u, 2)
    u[0,0,0] = np.nan
    v[1,0,1] = np.nan
    u[:2,0,2] = np.nan
    arrays = {'times': times, 'u':u, 'v':v}
    before_u, before_v = u.copy(), v.copy()
    rows = monthly(arrays)
    assert rows[0]['paired_samples'][0][:3] == [5,5,4]
    assert rows[0]['eastward_m_s'][0][:3] == [1,1,None]
    assert rows[0]['northward_m_s'][0][:3] == [2,2,None]
    assert rows[1]['eligible_mean_cells'] == 0
    np.testing.assert_array_equal(u, before_u); np.testing.assert_array_equal(v, before_v)
