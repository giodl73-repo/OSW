"""Reconstruct local M6 velocity means from an unchanged licensed PANGAEA TSV."""
import calendar
import csv
from datetime import datetime, timedelta
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/source-data/darelius-m6-2024/velocity.tsv.gz'
OUTPUT = ROOT/'research/antarctic-slope-m6-velocity-series.json'
PROTOCOL = 'plans/antarctic-slope-m6-velocity-protocol-v1.md'
URL = 'https://doi.pangaea.de/10.1594/PANGAEA.964717'
RAW_SHA = '84b1e299987aa552867873331eb5f29ffd785d62133816233cd3c061f5c6b5d0'
START = datetime(2017, 2, 24, 17)
END = datetime(2021, 2, 13, 10)


def selected(raw):
    rows = csv.DictReader(io.StringIO(raw.decode('utf8').split('*/', 1)[1].lstrip()), delimiter='\t')
    result = {}
    for row in rows:
        if float(row['Depth water [m]']) != 228:
            continue
        time = datetime.fromisoformat(row['Date/Time'])
        u, v = float(row['Cur vel U [cm/s]']), float(row['Cur vel V [cm/s]'])
        if time in result or not START <= time <= END or time.minute or time.second:
            raise ValueError('Duplicate or invalid M6 timestamp')
        if (float(row['Latitude']), float(row['Longitude'])) != (-74.5949, -29.9162):
            raise ValueError('Changed M6 station')
        if not all(math.isfinite(x) for x in [u, v]):
            raise ValueError('Nonfinite released paired reading')
        result[time] = (u, v)
    return result


def aggregate(readings):
    groups = {}
    for time, values in sorted(readings.items()):
        groups.setdefault((time.year, time.month), []).append(values)
    samples = []
    base = dict(entity_id='current:antarctic-slope', current_id='antarctic-slope',
                station='M6', nominal_depth_m=228, units='cm/s',
                source_url=URL, measurement_uncertainty_cm_s=None,
                scope='Local nominal-depth geographic velocity components; no current dimensions or footprint.',
                timestamp_convention='Source timezone unspecified', rank_eligible=False)
    for (year, month), values in groups.items():
        first = datetime(year, month, 1)
        last = datetime(year, month, calendar.monthrange(year, month)[1], 23)
        expected = int((min(last, END)-max(first, START))/timedelta(hours=1))+1
        samples.append(dict(base, id=f'm6-velocity:monthly:{year}-{month:02d}',
                            label=f'M6 228 m · {year}-{month:02d}', series_kind='monthly',
                            year=year, month=month, partial_month=first < START or last > END,
                            contributing_years=[year], contributing_months=1,
                            available_pairs=len(values), expected_hourly_slots=expected,
                            hourly_coverage_fraction=round(len(values)/expected, 8),
                            eastward_mean_cm_s=round(mean(v[0] for v in values), 8),
                            northward_mean_cm_s=round(mean(v[1] for v in values), 8),
                            eastward_interannual_span_cm_s=None, northward_interannual_span_cm_s=None))
    for month in range(1, 13):
        rows = [r for r in samples if r['series_kind']=='monthly' and r['month']==month and not r['partial_month']]
        if not rows:
            continue
        pairs, expected = sum(r['available_pairs'] for r in rows), sum(r['expected_hourly_slots'] for r in rows)
        samples.append(dict(base, id=f'm6-velocity:seasonal:{month:02d}',
                            label=f'M6 228 m · {calendar.month_name[month]} composite', series_kind='seasonal_composite',
                            year=None, month=month, partial_month=False,
                            contributing_years=[r['year'] for r in rows], contributing_months=len(rows),
                            available_pairs=pairs, expected_hourly_slots=expected,
                            hourly_coverage_fraction=round(pairs/expected, 8),
                            **{f'{component}_mean_cm_s':round(mean(r[f'{component}_mean_cm_s'] for r in rows), 8)
                               for component in ['eastward', 'northward']},
                            **{f'{component}_interannual_span_cm_s':[min(r[f'{component}_mean_cm_s'] for r in rows), max(r[f'{component}_mean_cm_s'] for r in rows)]
                               for component in ['eastward', 'northward']}))
    return samples


def build():
    raw = gzip.decompress((ROOT/SOURCE).read_bytes())
    if hashlib.sha256(raw).hexdigest() != RAW_SHA:
        raise ValueError('Changed released M6 source')
    readings = selected(raw)
    samples = aggregate(readings)
    if len(readings)!=16393 or len(samples)!=61:
        raise ValueError('Changed selected source coverage')
    return dict(schema='osw.local-mooring-velocity.v1', status='local_observed_velocity_aggregation',
                current_id='antarctic-slope', station=dict(name='M6', latitude=-74.5949, longitude=-29.9162, nominal_depth_m=228),
                source_file=SOURCE, source_sha256=hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
                uncompressed_sha256=RAW_SHA, source_url=URL,
                attribution='Darelius, E.; Janout, M. A.; Fer, I.; Sallée, J.-B. (2024), PANGAEA.964717, CC BY 4.0. OSW derived aggregation.',
                protocol_file=PROTOCOL, protocol_sha256=hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest(),
                generator_file='analysis/build_antarctic_slope_m6_velocity.py',
                generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_period=['2017-02-24T17:00:00','2021-02-13T10:00:00'], selected_paired_readings=len(readings),
                limitations=['Hourly gaps are omitted, never zero-filled; uneven sampling may bias means.',
                             'Released nominal ADCP bins 52:8:316 m differ from article Table 1, 26:8:298 m; no correction applied.',
                             'No rotation, interpolation, filtering or reproduction of published along-slope results.',
                             'Interannual spans are descriptive, not confidence intervals. Measurement uncertainty unresolved.',
                             'One fixed station and nominal depth cannot establish a whole-current width, length or seasonal footprint.'],
                samples=samples)


if __name__ == '__main__':
    OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print('Built 49 monthly means and 12 equal-year seasonal composites from 16,393 paired readings.')
