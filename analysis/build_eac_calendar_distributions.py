"""Describe dated EAC section spans by calendar month/year, retaining failures."""
import argparse
import calendar
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/eac-csiro-100m-section-core-spans.json'
SOURCE_SHA = '73285adebd96c852a42a144e2d262691c0903032dc41fe4500fa90322b370436'
PROTOCOL = 'plans/eac-section-calendar-distribution-protocol-v1.md'
REPORT = 'research/eac-section-calendar-distributions.json'
OPERATOR = 'analysis/build_eac_calendar_distributions.py'
SCENARIOS = ('central', 'minus_supplied_component_magnitudes', 'plus_supplied_component_magnitudes')
FRACTIONS = (0.4, 0.5, 0.6)
RESOLVED = 'resolved_section_component_span'


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def quantile(values, numerator, denominator=100):
    """Type-7 quantile, with explicit decimal readback precision."""
    if not values:
        return None
    ordered = sorted(Decimal(str(value)) for value in values)
    position = Decimal(len(ordered)-1)*Decimal(numerator)/Decimal(denominator)
    lower = int(position)
    upper = min(lower+1, len(ordered)-1)
    value = ordered[lower]+(position-lower)*(ordered[upper]-ordered[lower])
    return float(value.quantize(Decimal('.001'), rounding=ROUND_HALF_UP))


def validate_profiles(profiles):
    if not profiles:
        raise ValueError('Empty source record')
    dates = []
    for index, row in enumerate(profiles):
        stamp = row['source_time_utc']
        day = date.fromisoformat(stamp[:10])
        if not stamp.endswith('Z') or row['source_time_index'] != index:
            raise ValueError('Changed UTC/index support')
        if (row['year'], row['month']) != (day.year, day.month):
            raise ValueError('Changed calendar fields')
        if set(row['scenarios']) != set(SCENARIOS):
            raise ValueError('Missing or extra scenario')
        for scenario in SCENARIOS:
            cases = row['scenarios'][scenario]['cases']
            if len(cases) != 3 or sorted(c['fraction'] for c in cases) != list(FRACTIONS):
                raise ValueError('Missing or duplicate threshold case')
            for case in cases:
                value = case['section_span_km']
                if case['status'] == RESOLVED:
                    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                        raise ValueError('Invalid resolved span')
                elif value is not None:
                    raise ValueError('Unresolved span must remain null')
        dates.append(day)
    if any(b != a+timedelta(days=1) for a, b in zip(dates, dates[1:])):
        raise ValueError('Duplicate, unsorted or missing calendar date')
    return dates


def outcomes(rows):
    results = []
    for scenario in SCENARIOS:
        for fraction in FRACTIONS:
            selected = [(r, next(c for c in r['scenarios'][scenario]['cases'] if c['fraction'] == fraction)) for r in rows]
            resolved = [(r, c['section_span_km']) for r, c in selected if c['status'] == RESOLVED]
            values = [v for _, v in resolved]
            support = []
            for year, month in sorted({(r['year'], r['month']) for r in rows}):
                subset = [(r, c) for r, c in selected if (r['year'], r['month']) == (year, month)]
                support.append({'year': year, 'month': month, 'attempted_dates': len(subset),
                                'resolved_dates': sum(c['status'] == RESOLVED for _, c in subset),
                                'full_calendar_month_days': calendar.monthrange(year, month)[1],
                                'partial_calendar_month': len(subset) != calendar.monthrange(year, month)[1],
                                'status_counts': dict(sorted(Counter(c['status'] for _, c in subset).items()))})
            results.append({'scenario': scenario, 'fraction': fraction,
                            'primary': scenario == 'central' and fraction == .5,
                            'attempted_dates': len(rows), 'resolved_dates': len(resolved),
                            'status_counts': dict(sorted(Counter(c['status'] for _, c in selected).items())),
                            'contributing_year_months': support,
                            'conditional_min_km': quantile(values, 0),
                            'conditional_p10_km': quantile(values, 10),
                            'conditional_median_km': quantile(values, 50),
                            'conditional_p90_km': quantile(values, 90),
                            'conditional_max_km': quantile(values, 100),
                            'minimum_source_time_indices': [r['source_time_index'] for r, v in resolved if v == min(values)] if values else [],
                            'maximum_source_time_indices': [r['source_time_index'] for r, v in resolved if v == max(values)] if values else []})
    return results


def summarize(profiles):
    dates = validate_profiles(profiles)
    months = []
    for month in range(1, 13):
        rows = [r for r in profiles if r['month'] == month]
        months.append({'month': month, 'source_time_indices': [r['source_time_index'] for r in rows], 'outcomes': outcomes(rows)})
    years = []
    for year in range(dates[0].year, dates[-1].year+1):
        rows = [r for r in profiles if r['year'] == year]
        expected = 366 if calendar.isleap(year) else 365
        years.append({'year': year, 'full_calendar_days': expected,
                      'attempted_dates': len(rows), 'partial_calendar_year': len(rows) != expected,
                      'source_time_indices': [r['source_time_index'] for r in rows], 'outcomes': outcomes(rows)})
    return {'source_first_date': dates[0].isoformat(), 'source_last_date': dates[-1].isoformat(),
            'source_dates': len(profiles), 'calendar_month_groups': months, 'calendar_year_groups': years}


def build():
    if sha(SOURCE) != SOURCE_SHA:
        raise ValueError('Changed frozen dated diagnostic')
    source = json.loads((ROOT/SOURCE).read_bytes())
    for path, digest in source['input_sha256'].items():
        if sha(path) != digest:
            raise ValueError('Changed source dependency: '+path)
    if sha(source['source_file']) != source['source_sha256']:
        raise ValueError('Changed original profile corpus')
    return {'schema': 'osw.eac-section-calendar-distributions.v1',
            'status': 'exploratory_conditional_distributions_not_physical_width',
            'current_id': 'east-australian', 'entity_id': 'current:east-australian', 'depth_m': 100,
            'input_sha256': {SOURCE: SOURCE_SHA, PROTOCOL: sha(PROTOCOL), OPERATOR: sha(OPERATOR)},
            'source_file': SOURCE, 'source_profiles_pointer': '/profiles',
            'comparison_figure': 'figures/eac-section-calendar-distributions.svg',
            'figure_manifest': 'research/eac-section-calendar-distributions-figure.json',
            'metric': 'fixed_section_right_normal_peak_connected_component_span',
            'quantile_rule': 'type7_linear_decimal_half_up_0.001_km',
            'month_weighting': 'equal_resolved_mapped_source_dates_not_equal_years',
            'primary_scenario': 'central', 'primary_fraction': .5,
            'scenarios': list(SCENARIOS), 'fractions': list(FRACTIONS),
            **summarize(source['profiles']),
            'physical_width_admitted': False, 'width_rank_eligible': False,
            'whole_current_width_km': None, 'annual_physical_width_range_km': None,
            'geographic_current_edges': None, 'seasonal_map_playback_eligible': False,
            'independent_daily_observations': False, 'percentiles_are_confidence_intervals': False,
            'limitations': ['Conditional on successful bracketing; unresolved dates are retained in denominators.',
                            'Five-day-filtered SOM-filled mapped source; repeated dates are correlated.',
                            'Pooled calendar months have unequal year support; no equal-year climatology or trend inferred.',
                            'Partial first/last calendar years are retained and flagged.',
                            'Scenario and threshold sensitivity remain separate; no statistical uncertainty inferred.',
                            'Section spans are not physical whole-current widths or annual extrema.']}


def verify():
    document = json.loads((ROOT/REPORT).read_bytes())
    if document != build():
        raise ValueError('Changed calendar distribution report')
    manifest_path = document['figure_manifest']
    manifest = json.loads((ROOT/manifest_path).read_bytes())
    if manifest['source_file'] != REPORT or manifest['source_sha256'] != sha(REPORT) or manifest['physical_width_admitted'] is not False:
        raise ValueError('Changed calendar figure binding or admission')
    pins = {**document['input_sha256'], REPORT: sha(REPORT), manifest_path: sha(manifest_path)}
    for path, digest in [(manifest['protocol_file'], manifest['protocol_sha256']),
                         (manifest['generator_file'], manifest['generator_sha256'])]:
        pins[path] = digest
    for asset in manifest['figures'].values():
        pins[asset['file']] = asset['sha256']
        if (ROOT/asset['file']).stat().st_size != asset['bytes']:
            raise ValueError('Changed calendar figure bytes')
    for path, digest in pins.items():
        if sha(path) != digest:
            raise ValueError('Changed calendar dependency: '+path)
    return document, pins


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    document = build()
    encoded = (json.dumps(document, indent=2, allow_nan=False)+'\n').encode()
    if args.check:
        if (ROOT/REPORT).read_bytes() != encoded:
            raise ValueError('Changed calendar distribution report')
    else:
        (ROOT/REPORT).write_bytes(encoded)
    print(json.dumps({'source_dates': document['source_dates'], 'month_groups': 12,
                      'year_groups': len(document['calendar_year_groups']), 'cases_per_group': 9}))


if __name__ == '__main__':
    main()
