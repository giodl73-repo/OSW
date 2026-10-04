"""Pin twelve noon hindcast subsets; one snapshot per month, never month means."""
import hashlib
import json
import math
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://thredds.met.no/thredds/'
DATES = [f'2024-{month:02d}-15' for month in range(1, 13)]
OUTPUT = ROOT / 'research/norkyst-ingoy-2024-monthly-sample-receipts.json'
Y = (576, 4, 764)
X = (2420, 4, 2616)
FIELDS = ['salinity', 'u_eastward', 'v_northward', 'sea_mask', 'lon', 'lat']


def download(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        data = response.read(8_000_001)
    if len(data) > 8_000_000:
        raise ValueError('Unexpectedly large subset response')
    return data


def parse_ascii(content):
    """Parse DAP2 ASCII Grid arrays; exclude their repeated map coordinates."""
    body = content.decode('utf-8').split('---------------------------------------------', 1)[1]
    result = {}
    maps = {}
    for name in FIELDS:
        header = re.search(rf'(?m)^{name}\.{name}((?:\[\d+\])+)[\r\n]+', body)
        if not header:
            raise ValueError(f'Missing array {name}')
        shape = [int(n) for n in re.findall(r'\[(\d+)\]', header.group(1))]
        rows = []
        tail = body[header.end():]
        for line in tail.splitlines():
            if not line.strip():
                break
            prefix, values = line.split(',', 1)
            indexes = [int(n) for n in re.findall(r'\[(\d+)\]', prefix)]
            if indexes != ([0, 0, len(rows)] if len(shape) == 4 else [len(rows)]):
                raise ValueError('Unexpected array row indices')
            rows.append([float(value) for value in values.split(',')])
        if shape[-2:] != [48, 50] or len(rows) != 48 or any(len(row) != 50 for row in rows):
            raise ValueError('Unexpected subset shape')
        if len(shape) == 4 and shape[:2] != [1, 1]:
            raise ValueError('Unexpected time/depth shape')
        if any(not math.isfinite(value) for row in rows for value in row):
            raise ValueError('Nonfinite source array')
        if name in FIELDS[:4] and any(value != int(value) for row in rows for value in row):
            raise ValueError('Noninteger packed source array')
        result[name] = rows
        if name in ['salinity', 'u_eastward', 'v_northward']:
            for axis in ['time', 'depth']:
                match = re.search(rf'(?m)^{name}\.{axis}\[1\][\r\n]+([^\r\n]+)', body)
                value = float(match.group(1))
                if axis in maps and maps[axis] != value:
                    raise ValueError('Inconsistent field time/depth')
                maps[axis] = value
    return result, maps


def main():
    observations = []
    previous = json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else None
    metadata = ROOT / 'research/norkyst-ingoy-source-metadata-20240115.das'
    dataset = 'romshindcast/norkyst_v3/zdepth/2024/01/norkyst800-20240115.nc'
    if not metadata.exists():
        metadata.write_bytes(download(BASE + 'dodsC/' + dataset + '.das'))
    attrs = metadata.read_text(encoding='utf-8')
    for required in ['CC-BY-4.0', 'project "Norkyst_v3"', 'scale_factor 0.001', 'add_offset 30.0', 'standard_name "eastward_sea_water_velocity"']:
        if required not in attrs:
            raise ValueError('Unexpected source metadata')
    for day in DATES:
        stamp = day.replace('-', '')
        path = ROOT / f'research/norkyst-ingoy-{stamp}.json'
        raw = ROOT / f'research/norkyst-ingoy-{stamp}.ascii'
        dataset = f'romshindcast/norkyst_v3/zdepth/2024/{day[5:7]}/norkyst800-{stamp}.nc'
        day_metadata = ROOT / f'research/norkyst-ingoy-source-metadata-{stamp}.das'
        if not day_metadata.exists():
            day_metadata.write_bytes(download(BASE + 'dodsC/' + dataset + '.das'))
        day_attrs = day_metadata.read_text(encoding='utf-8')
        for required in ['CC-BY-4.0', 'project "Norkyst_v3"', f'time_coverage_start "{day}T00:00:00"']:
            if required not in day_attrs:
                raise ValueError('Unexpected daily source metadata')
        for name, offset in [('salinity', '30.0'), ('u_eastward', '0.0'), ('v_northward', '0.0')]:
            block = re.search(rf'(?m)^    {name} \{{(.*?)^    \}}', day_attrs, re.S).group(1)
            if 'scale_factor 0.001' not in block or f'add_offset {offset}' not in block or '_FillValue -32767' not in block:
                raise ValueError('Changed daily field packing')
        slice2 = f'[{Y[0]}:{Y[1]}:{Y[2]}][{X[0]}:{X[1]}:{X[2]}]'
        query = ','.join(name + ('[12][6]' if name in FIELDS[:3] else '') + slice2 for name in FIELDS)
        url = BASE + 'dodsC/' + dataset + '.ascii?' + urllib.parse.quote(query, safe=',:')
        if not raw.exists():
            raw.write_bytes(download(url))
        content = raw.read_bytes()
        arrays, axes = parse_ascii(content)
        expected_time = datetime.fromisoformat(day + 'T12:00:00+00:00').timestamp()
        if axes != {'time': expected_time, 'depth': 10.0}:
            raise ValueError('Unexpected noon/depth coordinates')
        old = next((row for row in previous['observations'] if row['date'] == day), None) if previous else None
        if old and hashlib.sha256(content).hexdigest() != old['source_response_sha256']:
            raise ValueError('Changed pinned source subset')
        receipt = {
            'schema': 'osw.norkyst-hindcast-subset.v1',
            'status': 'research_model_subset_not_current_footprint_or_canonical_measurement',
            'source_provider': 'MET Norway and Institute of Marine Research',
            'source_project': 'Norkyst_v3', 'source_url': url,
            'retrieved_at_utc': datetime.fromtimestamp(raw.stat().st_mtime, timezone.utc).isoformat(),
            'source_license': 'CC-BY-4.0',
            'source_citation': 'Albretsen, Sperrevik and Simonsen (2026), Norkyst v3 hindcast archive; Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026.',
            'source_response_file': raw.relative_to(ROOT).as_posix(),
            'source_response_sha256': hashlib.sha256(content).hexdigest(),
            'source_metadata_file': day_metadata.relative_to(ROOT).as_posix(),
            'source_metadata_sha256': hashlib.sha256(day_metadata.read_bytes()).hexdigest(),
            'sample_time_utc': day + 'T12:00:00Z', 'depth_m': 10,
            'sampling_kind': 'one_hourly_snapshot_per_month_not_monthly_or_daily_mean',
            'grid_index_slices': {'Y': list(Y), 'X': list(X)},
            'subset_shape': [48, 50], 'native_grid_spacing_m': 800,
            'subset_grid_stride': 4,
            'packed_field_arrays': arrays,
            'packing': {'salinity': {'scale': 0.001, 'offset': 30.0, 'fill': -32767, 'units': '1'}, 'u_eastward': {'scale': 0.001, 'offset': 0.0, 'fill': -32767, 'units': 'm/s'}, 'v_northward': {'scale': 0.001, 'offset': 0.0, 'fill': -32767, 'units': 'm/s'}},
            'scope_note': 'Rectangular projected-grid subset near Ingoy, decimated to 3.2 km. Contains coastal and offshore waters, not exclusively the named current. Model total velocities include tides and other flow components.',
            'annual_extrema_eligible': False, 'width_rank_eligible': False,
        }
        if old and hashlib.sha256(path.read_bytes()).hexdigest() != old['receipt_sha256']:
            raise ValueError('Changed pinned receipt')
        if not path.exists():
            path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        elif json.loads(path.read_text(encoding='utf-8'))['source_metadata_file'] != receipt['source_metadata_file'] or 'retrieved_at_utc' not in json.loads(path.read_text(encoding='utf-8')):
            # Upgrade initial receipts to verified per-day metadata, preserving fields.
            path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        observations.append({'date': day, 'file': path.relative_to(ROOT).as_posix(), 'receipt_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source_url': url, 'source_response_sha256': receipt['source_response_sha256']})
        OUTPUT.write_text(json.dumps({'schema': 'osw.norkyst-annual-sample-acquisition.v1', 'status': 'research_only_not_canonical', 'sampling_year': 2024, 'requested_dates': DATES, 'sampling_rule': 'Fifteenth day at 12:00 UTC, 10 m depth, four-cell stride; fixed before acquisition. Twelve hourly model snapshots, not monthly means or climatology.', 'observations': observations}, indent=2) + '\n', encoding='utf-8')
        print(day, 'pinned', flush=True)


if __name__ == '__main__':
    main()
