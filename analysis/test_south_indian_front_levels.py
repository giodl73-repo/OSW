"""Supplementary layer selection, custody and temperature-reference regressions."""
import ast
import copy
import inspect
import json
from pathlib import Path
import shutil
from urllib.parse import unquote

import gsw
import numpy as np
import pytest

import acquire_south_indian_front_levels as source
import acquire_south_indian_hycom_hydrography as original
import south_indian_front_level_preflight as preflight
from south_indian_front_temperature import daily, monthly, potential_temperature


@pytest.fixture
def selection(tmp_path):
    directory = tmp_path/'source'; directory.mkdir()
    for name in ['metadata.das', 'metadata.dds', 'coordinates.ascii']:
        shutil.copyfile(source.METADATA/name, directory/name)
    plan = source.make_plan(directory)
    (directory/'selection.json').write_text(json.dumps(plan), encoding='utf8')
    return directory, plan


def test_complete_original_cohort_new_exact_depths_and_bounded_urls(selection):
    directory, plan = selection
    preflight.check_cohort(plan)
    assert plan['selection']['depth'] == [19, 22]
    assert len(plan['selection']['lat']) == 326 and len(plan['selection']['lon']) == 3
    assert sum(len(r['time_indices']) for r in plan['requests']) == 363
    assert all(1 <= len(r['time_indices']) <= 3 for r in plan['requests'])
    for request in plan['requests']:
        query = unquote(request['url']).split('?', 1)[1]
        for name in source.FIELDS:
            assert name+'[' in query
        assert query.count('[19:3:22][800:1:1125][3249:1:3251]') == 4
    assert source.validate_plan(directory) == plan


@pytest.mark.parametrize('change', ['depth', 'latitude', 'time', 'packing', 'minimum'])
def test_reject_changed_support(selection, change):
    _, plan = selection
    bad = copy.deepcopy(plan)
    if change == 'depth': bad['selection']['depth'][0] = 18
    if change == 'latitude': bad['selection']['lat'].pop()
    if change == 'time': bad['requests'][0]['time_indices'].pop()
    if change == 'packing': bad['scale'] = .001
    if change == 'minimum': bad['minimum_pairs'][0] -= 1
    with pytest.raises(ValueError): preflight.check_cohort(bad)


def test_declaration_precedes_fields_and_rejects_mutation(selection, tmp_path, monkeypatch):
    directory, _ = selection
    monkeypatch.setattr(preflight, 'DECLARATION', str(tmp_path/'declaration.json'))
    doc = preflight.declare(directory)
    assert preflight.checked(directory) == doc
    with pytest.raises(ValueError): preflight.declare(directory)
    doc['physical_width_admitted'] = True
    raw = (json.dumps(doc)+'\n').encode()
    Path(preflight.DECLARATION).write_bytes(raw)
    (directory/'preflight.json').write_bytes(raw)
    with pytest.raises(ValueError): preflight.checked(directory)


def test_cannot_adopt_already_downloaded_values(selection, tmp_path, monkeypatch):
    directory, _ = selection
    monkeypatch.setattr(preflight, 'DECLARATION', str(tmp_path/'declaration.json'))
    (directory/'m01-r00.ascii').write_bytes(b'Unexpected earlier field values')
    with pytest.raises(ValueError): preflight.declare(directory)


def test_raw_parser_and_common_means_preserve_original_method():
    for name in ['parse_ascii', 'common_means', 'check_metadata']:
        assert ast.dump(ast.parse(inspect.getsource(getattr(source, name)))) == ast.dump(
            ast.parse(inspect.getsource(getattr(original, name))))


def test_teos_official_reference_examples():
    # TEOS-10 official pt0_from_t examples (first and last entries).
    actual = potential_temperature([34.7118, 34.7324], [28.7856, 4.4036], [10, 1000])
    np.testing.assert_allclose(actual, [28.783196819670632, 4.324510571845719], rtol=0, atol=1e-12)
    np.testing.assert_allclose(gsw.p_from_z([-125, -1000], 4, 0, 0),
                               [125.731858435610, 1007.990337692001], rtol=0, atol=1e-9)
    # The older3.05 web SA example uses different atlas values. Use the pinned
    # release's independent MATLAB check data and its published accuracy bound.
    with np.load(Path(gsw.__file__).parent/'tests/gsw_cv_v3_0.npz', allow_pickle=False) as d:
        actual = gsw.SA_from_SP(d['SP_chck_cast'], d['p_chck_cast'],
                                d['long_chck_cast'], d['lat_chck_cast'])
        np.testing.assert_allclose(actual, d['SA_from_SP'], rtol=0,
                                   atol=float(d['SA_from_SP_ca']), equal_nan=True)


def packed():
    fields = {n: np.zeros((2, 2, 2, 1), dtype='<i2') for n in source.FIELDS}
    fields['salinity'][:] = 15000
    fields['water_temp'][0] = -10000
    fields['water_temp'][1] = 10000
    return fields


def convert(fields):
    return daily(fields, [100, 200], [-45, -35], [80],
                 float(np.float32(.001)), {'water_temp': 20., 'salinity': 20.})


def test_daily_conversion_not_conversion_of_monthly_mean():
    fields = packed(); result = convert(fields)
    counts, mean = monthly(result, 2)
    assert np.all(counts == 2) and np.isfinite(mean).all()
    average_inputs = {n: np.repeat(np.mean(a, axis=0, keepdims=True).astype('<i2'), 2, axis=0)
                      for n, a in fields.items()}
    _, wrong = monthly(convert(average_inputs), 2)
    assert np.max(np.abs(mean-wrong)) > 1e-5
    assert result['temperature_scale_verified'] is False
    assert result['temperature_scale_assumption'] == 'ITS-90'
    assert result['physical_width_admitted'] is False
    assert np.all(result['sea_pressure_dbar'] > 100)


def test_common_mask_retains_velocity_failures_and_calendar_eligibility():
    fields = packed(); fields['water_v'][0, 0, 0, 0] = -30000
    result = convert(fields)
    assert np.isnan(result['potential_temperature_0_dbar_assuming_ITS90_c'][0, 0, 0, 0])
    counts, mean = monthly(result, 2)
    assert counts[0, 0, 0] == 1 and np.isnan(mean[0, 0, 0])
    assert np.isfinite(mean[1]).all()


def test_negative_valid_salinity_rejected_instead_of_gsw_clamping():
    fields = packed(); fields['salinity'][0, 0, 0, 0] = -25000
    with pytest.raises(ValueError, match='clamped'): convert(fields)


def test_unpinned_thermodynamics_rejected(monkeypatch):
    monkeypatch.setattr(gsw, '__version__', 'other')
    with pytest.raises(ValueError, match='version'): convert(packed())
