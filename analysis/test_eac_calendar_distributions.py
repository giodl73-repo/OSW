"""Calendar support, conditional quantiles and source preservation invariants."""
import copy
import json

import numpy as np
import pytest

from build_eac_calendar_distributions import ROOT, REPORT, SOURCE, SCENARIOS, FRACTIONS, RESOLVED, build, quantile, summarize, validate_profiles, verify


@pytest.fixture(scope='module')
def source():
    return json.loads((ROOT/SOURCE).read_bytes())


def primary(row):
    return next(o for o in row['outcomes'] if o['primary'])


def test_complete_report_partition_and_independent_statistics(source):
    stored = json.loads((ROOT/REPORT).read_bytes())
    assert stored == build()
    verified, pins = verify()
    assert verified == stored and REPORT in pins
    profiles = source['profiles']
    assert stored['source_dates'] == len(profiles) == 3770
    for grouping in ['calendar_month_groups', 'calendar_year_groups']:
        indices = [i for row in stored[grouping] for i in row['source_time_indices']]
        assert sorted(indices) == list(range(3770))
        assert len(indices) == len(set(indices))
        assert sum(primary(row)['resolved_dates'] for row in stored[grouping]) == 2883
        for row in stored[grouping]:
            assert len(row['outcomes']) == 9
            for outcome in row['outcomes']:
                selected = [next(c for c in profiles[i]['scenarios'][outcome['scenario']]['cases']
                                 if c['fraction'] == outcome['fraction']) for i in row['source_time_indices']]
                values = [c['section_span_km'] for c in selected if c['status'] == RESOLVED]
                assert sum(outcome['status_counts'].values()) == len(selected) == outcome['attempted_dates']
                assert sum(s['attempted_dates'] for s in outcome['contributing_year_months']) == len(selected)
                assert sum(s['resolved_dates'] for s in outcome['contributing_year_months']) == len(values)
                assert all(sum(s['status_counts'].values()) == s['attempted_dates'] for s in outcome['contributing_year_months'])
                if values:
                    expected = np.quantile(values, [0, .1, .5, .9, 1], method='linear')
                    actual = [outcome[k] for k in ['conditional_min_km', 'conditional_p10_km', 'conditional_median_km', 'conditional_p90_km', 'conditional_max_km']]
                    np.testing.assert_allclose(actual, expected, atol=.000500001, rtol=0)
                    assert all(next(c for c in profiles[i]['scenarios'][outcome['scenario']]['cases'] if c['fraction'] == outcome['fraction'])['section_span_km'] == min(values)
                               for i in outcome['minimum_source_time_indices'])
    years = stored['calendar_year_groups']
    assert [r['year'] for r in years if r['partial_calendar_year']] == [2012, 2022]
    assert next(r for r in years if r['year'] == 2016)['full_calendar_days'] == 366
    july_2022 = next(s for s in primary(stored['calendar_month_groups'][6])['contributing_year_months'] if s['year'] == 2022)
    assert july_2022['partial_calendar_month'] is True and july_2022['attempted_dates'] == 27
    assert july_2022['full_calendar_month_days'] == 31
    assert stored['physical_width_admitted'] is False
    assert stored['annual_physical_width_range_km'] is None


def test_nulls_and_small_sample_quantile_semantics(source):
    assert quantile([], 50) is None
    assert quantile([4], 10) == 4
    assert quantile([0, 10], 10) == 1
    assert quantile([1.0005], 50) == 1.001
    rows = copy.deepcopy(source['profiles'][:2])
    for row in rows:
        for scenario in SCENARIOS:
            for case in row['scenarios'][scenario]['cases']:
                case['status'] = 'unresolved_paired_boundaries'; case['section_span_km'] = None
    snapshot = copy.deepcopy(rows)
    result = summarize(rows)
    assert rows == snapshot
    april = result['calendar_month_groups'][3]
    assert primary(april)['attempted_dates'] == 2 and primary(april)['resolved_dates'] == 0
    assert primary(april)['conditional_median_km'] is None
    assert primary(result['calendar_month_groups'][0])['attempted_dates'] == 0


@pytest.mark.parametrize('mutation', ['duplicate_date', 'missing_date', 'wrong_month', 'missing_scenario', 'duplicate_fraction', 'zero_for_missing', 'nan_resolved'])
def test_corrupt_support_or_invented_values_rejected(source, mutation):
    rows = copy.deepcopy(source['profiles'][:3])
    if mutation == 'duplicate_date': rows[1]['source_time_utc'] = rows[0]['source_time_utc']
    elif mutation == 'missing_date': rows.pop(1); rows[1]['source_time_index'] = 1
    elif mutation == 'wrong_month': rows[0]['month'] = 1
    elif mutation == 'missing_scenario': rows[0]['scenarios'].pop('central')
    elif mutation == 'duplicate_fraction': rows[0]['scenarios']['central']['cases'][1]['fraction'] = .4
    else:
        case = rows[0]['scenarios']['central']['cases'][0]
        case['status'] = 'unresolved_paired_boundaries' if mutation == 'zero_for_missing' else RESOLVED
        case['section_span_km'] = 0 if mutation == 'zero_for_missing' else float('nan')
    with pytest.raises(ValueError): validate_profiles(rows)
