"""Retain surrounding OSCAR vectors and prove the prior 32 S slice unchanged."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import tempfile
from urllib.parse import quote
import urllib.request
import zipfile

import numpy as np

from acquire_basin_surface_sections import parse as parse_section

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'research/source-data/oscar-west-australian-2d-2013'
PROTOCOL = 'plans/west-australian-oscar-2d-source-selection-protocol-v1.md'
OPERATOR = 'analysis/acquire_west_australian_oscar_2d.py'
OLD = ROOT/'research/source-data/oscar-west-australian-2013'
CONFIG = ROOT/'research/west-australian-oscar-section-input.json'
BASE = 'https://oceanwatch.pifsc.noaa.gov/erddap'
DATASET = 'yearly_336c_0b32_9cd3'
LIMIT = 40_000_000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def urls():
    bounds = '[(2013-01-01T00:00:00Z):1:(2013-12-28T00:00:00Z)][(15)][(-28):1:(-36)][(60):1:(116)]'
    query = ','.join(c+bounds for c in ['u', 'v'])
    return {'metadata.json': BASE+'/info/'+DATASET+'/index.json',
            'vectors.csv': BASE+'/griddap/'+DATASET+'.csv?'+quote(query, safe='')}


def baseline():
    receipt = json.loads((OLD/'acquisition.json').read_bytes())
    for name, row in receipt['files'].items():
        if digest((OLD/name).read_bytes()) != row['sha256']:
            raise ValueError('Changed old section original: '+name)
    config = json.loads(CONFIG.read_bytes())
    _, frames = parse_section((OLD/'metadata.json').read_bytes(), (OLD/'section.csv').read_bytes(), config)
    return frames


def parse(metadata, raw, previous=None):
    attrs = {(r[1], r[2]): r[4] for r in json.loads(metadata)['table']['rows'] if r[0] == 'attribute'}
    for key, value in {('u', 'units'): 'm s-1', ('v', 'units'): 'm s-1', ('NC_GLOBAL', 'version'): '2017.0', ('depth', 'actual_range'): '15.0, 15.0'}.items():
        if attrs.get(key) != value:
            raise ValueError('Changed OSCAR metadata')
    if 'may be used and redistributed for free' not in attrs.get(('NC_GLOBAL', 'license'), ''):
        raise ValueError('Missing source redistribution permission')
    previous = baseline() if previous is None else previous
    times = [frame['time'] for frame in previous]
    if len(times) != 72 or len(set(times)) != 72:
        raise ValueError('Changed prior time support')
    reader = csv.reader(io.StringIO(raw.decode('utf8')))
    if next(reader, None) != ['time', 'depth', 'latitude', 'longitude', 'u', 'v'] or next(reader, None) != ['UTC', 'm', 'degrees_north', 'degrees_east', 'm s-1', 'm s-1']:
        raise ValueError('Changed vector columns/units')
    latitude = np.full(25, np.nan); longitude = np.full(169, np.nan)
    u = np.full((72, 25, 169), np.nan); v = np.full_like(u, np.nan)
    count = 0
    for count, row in enumerate(reader, 1):
        if len(row) != 6 or count > u.size:
            raise ValueError('Malformed or extra vector row')
        ti, rest = divmod(count-1, 25*169); yi, xi = divmod(rest, 169)
        depth, lat, lon, east, north = map(float, row[1:])
        if row[0] != times[ti] or depth != 15 or abs(lat-(-28-yi/3)) > 1e-7 or abs(lon-(60+xi/3)) > 1e-7:
            raise ValueError('Changed vector grid, ordering, clock or depth')
        if any(np.isinf(value) for value in [east, north]):
            raise ValueError('Infinite velocity')
        if ti == 0 and xi == 0: latitude[yi] = lat
        if ti == 0 and yi == 0: longitude[xi] = lon
        if lat != latitude[yi] or lon != longitude[xi]:
            raise ValueError('Inconsistent coordinate spelling/value across rows')
        u[ti, yi, xi] = east; v[ti, yi, xi] = north
    if count != u.size:
        raise ValueError('Incomplete rectangular source cube')
    if latitude[12] != -32:
        raise ValueError('Missing comparison section')
    for ti, frame in enumerate(previous):
        for key, array in [('eastward_m_s', u), ('northward_m_s', v)]:
            expected = np.array([np.nan if r[key] is None else r[key] for r in frame['samples']], dtype='<f8')
            actual = array[ti, 12, :]
            if not np.array_equal(np.isnan(actual), np.isnan(expected)):
                raise ValueError('Changed comparison-section masks')
            finite = np.isfinite(expected)
            if not np.array_equal(actual[finite].view('<u8'), expected[finite].view('<u8')):
                raise ValueError('Changed finite comparison-section float64 bits')
        if not np.array_equal(longitude, np.array([r['longitude'] for r in frame['samples']])):
            raise ValueError('Changed comparison-section longitude')
    paired = np.isfinite(u) & np.isfinite(v)
    quality = {'source_times': 72, 'latitude_positions': 25, 'longitude_positions': 169,
               'vector_positions': int(u.size), 'finite_pairs': int(paired.sum()),
               'both_missing': int((np.isnan(u) & np.isnan(v)).sum()),
               'one_component_missing': int((np.isnan(u) ^ np.isnan(v)).sum()),
               'comparison_section_positions': 72*169, 'comparison_section_finite_bits_and_masks_exact': True}
    return {'times': times, 'latitude': latitude, 'longitude': longitude, 'u': u, 'v': v}, quality


def load():
    receipt = json.loads((DIRECTORY/'acquisition.json').read_bytes())
    archive = (DIRECTORY/'source-responses.zip').read_bytes()
    if digest(archive) != receipt['archive_sha256']:
        raise ValueError('Changed source archive')
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        if source.namelist() != ['metadata.json', 'vectors.csv']:
            raise ValueError('Changed source archive members')
        members = {name: source.read(name) for name in source.namelist()}
    for name, raw in members.items():
        row = receipt['files'][name]
        if row['url'] != urls()[name] or len(raw) != row['bytes'] or digest(raw) != row['sha256']:
            raise ValueError('Changed archived response')
    return parse(members['metadata.json'], members['vectors.csv'])


def acquire():
    if DIRECTORY.exists():
        raise ValueError('Source directory exists; refusing overwrite')
    pins = {p: digest((ROOT/p).read_bytes()) for p in [PROTOCOL, OPERATOR]}
    received, receipts = {}, {}
    cache = ROOT/'.pytest_cache/west-australian-2d-downloads'; cache.mkdir(parents=True, exist_ok=True)
    for name, url in urls().items():
        receipt_path = cache/(name+'.receipt.json')
        if receipt_path.exists():
            saved = json.loads(receipt_path.read_bytes()); raw = (cache/name).read_bytes()
            if saved['url'] != url or saved['sha256'] != digest(raw) or saved['bytes'] != len(raw):
                raise ValueError('Changed saved response; refusing replacement')
            received[name] = raw; receipts[name] = saved
            continue
        started = datetime.now(timezone.utc).isoformat()
        with urllib.request.urlopen(url, timeout=90) as response:
            raw = response.read(LIMIT+1)
            if response.status != 200 or len(raw) > LIMIT:
                raise ValueError('Unexpected source HTTP status or response size')
            receipts[name] = {'url': url, 'resolved_url': response.url, 'http_status': response.status,
                              'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
                              'bytes': len(raw), 'sha256': digest(raw), 'download_collector_sha256': pins[OPERATOR]}
            received[name] = raw
            (cache/name).write_bytes(raw)
            receipt_path.write_bytes((json.dumps(receipts[name], indent=2)+'\n').encode())
    arrays, quality = parse(received['metadata.json'], received['vectors.csv'])
    if pins != {p: digest((ROOT/p).read_bytes()) for p in pins}:
        raise ValueError('Selection/collector changed during acquisition')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in ['metadata.json', 'vectors.csv']:
            item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)); item.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(item, received[name])
    encoded = buffer.getvalue()
    receipt = {'schema': 'osw.west-australian-oscar-2d-acquisition.v1', 'status': 'COMPLETE_VALIDATED',
               'dataset_id': DATASET, 'product_version': '2017.0', 'input_sha256': pins,
               'files': receipts, 'archive_sha256': digest(encoded), 'archive_bytes': len(encoded),
               'quality': quality, 'new_current_dimension_admitted': False,
               'attribution': 'OSCAR third-degree surface currents, version2017.0, NOAA OceanWatch ERDDAP distribution; source metadata retained verbatim.',
               'source_license': 'Source metadata explicitly permits free use and redistribution, with accuracy/use disclaimers; see archived NC_GLOBAL license.'}
    DIRECTORY.parent.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(dir=DIRECTORY.parent) as temporary:
        staging = Path(temporary)/DIRECTORY.name; staging.mkdir()
        (staging/'source-responses.zip').write_bytes(encoded)
        (staging/'acquisition.json').write_bytes((json.dumps(receipt, indent=2)+'\n').encode())
        staging.rename(DIRECTORY)
    print(json.dumps(quality), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--acquire', action='store_true'); args = parser.parse_args()
    if args.acquire: acquire()
    else: print(json.dumps(load()[1]))
