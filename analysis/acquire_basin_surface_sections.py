"""Acquire/verify four exact archived OSCAR vector sections, without admission."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.parse import quote
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/source-data/oscar-basin-sections-2013'
CONFIG = ROOT / 'research/basin-surface-section-input.json'
OUTPUT = ROOT / 'research/basin-surface-section-inventory.json'
BASE = 'https://oceanwatch.pifsc.noaa.gov/erddap'
DATASET = 'yearly_336c_0b32_9cd3'
EXPECTED_SECTIONS = (
    ('portugal','portugal-40n','latitude',40,'longitude',[-32,-8],[-24,-12],'southward','research/portugal-current-naming-seasonal-scope-audit.json'),
    ('south-atlantic','south-atlantic-30w','longitude',-30,'latitude',[-48,-30],[-43,-36],'eastward','research/south-atlantic-reach-reference-path-input.json'),
    ('south-pacific','south-pacific-100w','longitude',-100,'latitude',[-45,-25],[-37,-31],'eastward','research/south-pacific-eastern-front-reach-layer-time-scope-audit.json'),
    ('south-indian','south-indian-80e','longitude',80,'latitude',[-48,-30],[-43,-37],'eastward','research/south-indian-eastern-reach-naming-layer-scope-audit.json'),
)


def validate_config(config):
    keys=['current_id','section_id','fixed_axis','fixed_coordinate','varying_axis','domain','peak_search','component','scope_audit']
    actual=[tuple(s[k] for k in keys) for s in config['sections']]
    if actual!=list(EXPECTED_SECTIONS) or config['dataset_id']!=DATASET or config['product_version']!='2017.0' or config['year']!=2013 or config['nominal_depth_m']!=15:
        raise ValueError('Changed declared section identities, geography or product')
    if config['annual_extrema_eligible'] is not False or config['whole_current_representative'] is not False:
        raise ValueError('Local sections cannot become whole-current dimensions')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def urls(config):
    validate_config(config)
    result = {'metadata.json': f'{BASE}/info/{DATASET}/index.json'}
    for section in config['sections']:
        low, high = section['domain']
        if section['fixed_axis'] == 'latitude':
            coordinates = f"[({section['fixed_coordinate']})][({low+360}):1:({high+360})]"
        else:
            coordinates = f"[({high}):1:({low})][({section['fixed_coordinate']%360})]"
        query = ','.join(f'{component}[(2013-01-01T00:00:00Z):1:(2013-12-28T00:00:00Z)][(15)]{coordinates}' for component in ['u', 'v'])
        result[section['section_id']+'.csv'] = f'{BASE}/griddap/{DATASET}.csv?'+quote(query, safe='')
    return result


def parse(metadata, raw, section):
    attrs = {(r[1], r[2]): r[4] for r in json.loads(metadata)['table']['rows'] if r[0]=='attribute'}
    for key, value in {('u','units'):'m s-1', ('v','units'):'m s-1', ('NC_GLOBAL','version'):'2017.0', ('depth','actual_range'):'15.0, 15.0'}.items():
        if attrs.get(key) != value:
            raise ValueError('Changed OSCAR version, units or nominal depth')
    lines = list(csv.reader(io.StringIO(raw.decode('utf-8'))))
    if lines[:2] != [['time','depth','latitude','longitude','u','v'], ['UTC','m','degrees_north','degrees_east','m s-1','m s-1']]:
        raise ValueError('Unexpected vector-section columns/units')
    frames = {}
    low, high = section['domain']
    count = round((high-low)*3)+1
    for line in lines[2:]:
        if len(line) != 6:
            raise ValueError('Malformed vector-section row')
        instant = datetime.fromisoformat(line[0].replace('Z','+00:00'))
        depth, latitude, source_longitude, u, v = map(float, line[1:])
        longitude = source_longitude-360 if source_longitude>=180 else source_longitude
        fixed = latitude if section['fixed_axis']=='latitude' else longitude
        coordinate = longitude if section['varying_axis']=='longitude' else latitude
        if instant.year != 2013 or instant.utcoffset().total_seconds()!=0 or depth!=15 or abs(fixed-section['fixed_coordinate'])>1e-8 or not low-1e-8<=coordinate<=high+1e-8:
            raise ValueError('Unexpected section coordinate/time/layer')
        if any(math.isinf(x) for x in [u,v]):
            raise ValueError('Infinite velocity')
        row = {'coordinate': coordinate, 'longitude': longitude, 'latitude': latitude,
               'eastward_m_s': None if math.isnan(u) else u, 'northward_m_s': None if math.isnan(v) else v}
        frame = frames.setdefault(line[0], {})
        if coordinate in frame:
            raise ValueError('Duplicate section timestamp/coordinate')
        frame[coordinate] = row
    result = []
    for stamp, samples in sorted(frames.items()):
        grid = sorted(samples)
        if len(grid)!=count or abs(grid[0]-low)>1e-8 or abs(grid[-1]-high)>1e-8 or any(abs(b-a-1/3)>1e-8 for a,b in zip(grid,grid[1:])):
            raise ValueError('Incomplete or changed section grid')
        result.append({'time': stamp, 'samples':[samples[x] for x in grid]})
    times = [datetime.fromisoformat(x['time'].replace('Z','+00:00')) for x in result]
    # Legacy OSCAR has 72 nominal five-day records, including four six-day
    # gaps, in 2013. Preserve actual provider times; do not invent 73 frames.
    gaps = [(b-a).total_seconds()/86400 for a,b in zip(times,times[1:])]
    if len(times)!=72 or times[0].isoformat()!='2013-01-01T00:00:00+00:00' or times[-1].isoformat()!='2013-12-26T00:00:00+00:00' or set(gaps)!={5,6} or gaps.count(6)!=4 or any(sum(t.month==m for t in times)<5 for m in range(1,13)):
        raise ValueError('Changed nominal five-day annual sampling')
    return attrs, result


def build():
    config = json.loads(CONFIG.read_bytes())
    manifest = json.loads((CACHE/'acquisition.json').read_bytes())
    if manifest['config_sha256'] != sha(CONFIG.read_bytes()):
        raise ValueError('Changed predeclared section rules')
    contents = {}
    for name, url in urls(config).items():
        data = (CACHE/name).read_bytes()
        receipt = manifest['files'][name]
        if receipt['url']!=url or receipt['bytes']!=len(data) or receipt['sha256']!=sha(data):
            raise ValueError('Changed query or original provider bytes: '+name)
        contents[name] = data
    sections = []
    for section in config['sections']:
        attrs, frames = parse(contents['metadata.json'], contents[section['section_id']+'.csv'], section)
        sections.append({**section, 'frames':frames, 'source_csv_file':(CACHE/ (section['section_id']+'.csv')).relative_to(ROOT).as_posix(),
                         'counts':{'times':len(frames), 'cells_per_time':len(frames[0]['samples']), 'missing_vector_pairs':sum(s['eastward_m_s'] is None or s['northward_m_s'] is None for f in frames for s in f['samples'])}})
    return {'schema':'osw.basin-surface-section-inventory.v1', 'status':'acquired_surface_product_sections_not_measurement_admission',
            'config_file':CONFIG.relative_to(ROOT).as_posix(), 'config_sha256':sha(CONFIG.read_bytes()),
            'acquisition_file':(CACHE/'acquisition.json').relative_to(ROOT).as_posix(), 'acquisition_sha256':sha((CACHE/'acquisition.json').read_bytes()),
            'source_files':manifest['files'], 'provider':'Earth & Space Research / NOAA PIFSC ERDDAP mirror', 'dataset_id':DATASET, 'product_version':'2017.0',
            'nominal_depth_coordinate_m':15, 'layer_interpretation':'Satellite-derived near-surface product with nominal 15 m coordinate; not a direct 15 m instrument section or depth-resolved velocity.',
            'time_convention':'72 nominal five-day 2013 archive samples, with four six-day gaps, January 1 through December 26. One year, not climatology or adequate evidence for annual extrema.',
            'source_license':attrs[('NC_GLOBAL','license')], 'sections':sections,
            'whole_current_width_km':None, 'annual_width_range_km':None, 'width_rank_eligible':False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--acquire', action='store_true')
    args = parser.parse_args()
    if args.acquire:
        if CACHE.exists():
            raise ValueError('Source directory exists; refusing overwrite')
        config = json.loads(CONFIG.read_bytes())
        responses = {}
        source_urls = urls(config)
        for name, url in source_urls.items():
            with urllib.request.urlopen(url, timeout=60) as response:
                responses[name] = response.read()
        for section in config['sections']:
            parse(responses['metadata.json'], responses[section['section_id']+'.csv'], section)
        CACHE.mkdir(parents=True)
        for name, data in responses.items():
            (CACHE/name).write_bytes(data)
        manifest = {'schema':'osw.source-acquisition.v1', 'acquired_at':datetime.now(timezone.utc).isoformat(), 'dataset_id':DATASET,
                    'config_sha256':sha(CONFIG.read_bytes()), 'files':{name:{'url':source_urls[name], 'bytes':len(data), 'sha256':sha(data)} for name,data in responses.items()}}
        (CACHE/'acquisition.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    document = build()
    OUTPUT.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({s['section_id']:s['counts'] for s in document['sections']}))


if __name__=='__main__':
    main()
