"""Explicit acquisition of complete month/halo originals; offline analysis is separate."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import zipfile

import norkyst_continuous_source as source

ROOT = source.ROOT
FOLDER = ROOT / source.SOURCE
CACHE = ROOT / '.pytest_cache/norkyst-continuous-originals'
BASE = 'https://thredds.met.no/thredds/dodsC/romshindcast/norkyst_v3/zdepth/'


def dataset(day):
    return BASE + day[:4] + '/' + day[5:7] + '/norkyst800-' + day.replace('-', '') + '.nc'


def retrieve(url, path, pin=None):
    if path.exists():
        raw = path.read_bytes()
        if pin and source.sha(raw) != pin:
            raise ValueError('Changed cached original: ' + path.name)
        return raw, datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    with urlopen(Request(url, headers={'User-Agent':'OSW/1.0 research source acquisition'}), timeout=45) as response:
        raw = response.read(4_000_001)
    if len(raw) > 4_000_000 or not raw:
        raise ValueError('Empty or oversized source response')
    if pin and source.sha(raw) != pin:
        raise ValueError('Changed retained original: ' + path.name)
    temporary = path.with_suffix(path.suffix + '.part')
    temporary.write_bytes(raw); temporary.replace(path)
    return raw, datetime.now(timezone.utc).isoformat()


def day_job(request, previous):
    day, first, last = request
    key = day.replace('-', '') + f'_{first:02d}-{last:02d}'
    old = previous.get(key, {})
    meta_name = day.replace('-', '') + '.das'
    meta, meta_time = retrieve(dataset(day) + '.das', CACHE / meta_name, old.get('metadata_sha256'))
    source.metadata(meta, day)
    meta_time=old.get('metadata_retrieved_utc',meta_time)
    meta_basis=old.get('metadata_time_basis','Individual original-response acquisition completion')
    probe=json.loads((FOLDER/'metadata-probe.json').read_bytes())
    if any(r.get('date')==day and r.get('kind')=='das' and r.get('sha256')==source.sha(meta) for r in probe['records']):
        meta_time=probe['retrieved_utc']
        meta_basis='First metadata-only probe batch completion upper bound; individual response times were not recorded'
    spatial = '[576:4:764][2420:4:2616]'
    query = ','.join(name + f'[{first}:1:{last}][6]' + spatial for name in source.VARIABLES) + ',sea_mask' + spatial
    url = dataset(day) + '.ascii?' + quote(query, safe=',:')
    raw_name = key + '.ascii'
    raw, field_time = retrieve(url, CACHE / raw_name, old.get('field_sha256'))
    times, arrays = source.parse_fields(raw, day, first, last)
    count = len(times) * len(source.Y) * len(source.X)
    valid = arrays['sea_mask'][None, :, :] == 1
    for name in source.VARIABLES:
        valid = valid & (arrays[name] != -32767)
    return {'key':key, 'date':day, 'first_hour':first, 'last_hour':last, 'hours':len(times),
            'first_epoch_seconds':times[0], 'last_epoch_seconds':times[-1],
            'field_url':url, 'field_member':raw_name, 'field_sha256':source.sha(raw), 'field_bytes':len(raw),
            'field_retrieved_utc':old.get('field_retrieved_utc',field_time),
            'metadata_url':dataset(day) + '.das', 'metadata_member':meta_name,
            'metadata_sha256':source.sha(meta), 'metadata_bytes':len(meta),
            'metadata_retrieved_utc':meta_time,'metadata_time_basis':meta_basis,
            'source_positions':count, 'complete_wet_paired_positions':int(valid.sum()),
            'missing_or_nonwet_positions':count - int(valid.sum())}


def archive(path, members):
    temporary = path.with_suffix('.zip.part')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, raw in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    if path.exists() and path.read_bytes() != temporary.read_bytes():
        temporary.unlink()
        raise ValueError('Refusing to replace a frozen original archive: ' + path.name)
    temporary.replace(path)
    return {'file':path.relative_to(ROOT).as_posix(), 'sha256':source.sha(path.read_bytes()),
            'bytes':path.stat().st_size, 'members':{name:source.sha(raw) for name,raw in sorted(members.items())}}


def retained_responses(*groups):
    result={}
    metadata_pins={}
    for group in groups:
        for row in group:
            if row['key'] in result and row['field_sha256']!=result[row['key']]['field_sha256']:
                raise ValueError('Conflicting retained original field pins')
            if row['date'] in metadata_pins and metadata_pins[row['date']]!=row['metadata_sha256']:
                raise ValueError('Conflicting retained daily metadata pins')
            metadata_pins[row['date']]=row['metadata_sha256'];result[row['key']]=row
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-months', action='store_true')
    args = parser.parse_args()
    declaration = source.preflight()
    months = declaration['acquisition_phase_order'] if args.all_months else declaration['pilot_months']
    phase = 'year' if args.all_months else 'pilot'
    path = FOLDER / ('acquisition-' + phase + '.json')
    old = json.loads(path.read_bytes()) if path.exists() else {}
    pilot_path=FOLDER/'acquisition-pilot.json'
    pilot=json.loads(pilot_path.read_bytes()) if args.all_months and pilot_path.exists() else {}
    previous = retained_responses(pilot.get('responses',[]),old.get('responses',[]))
    CACHE.mkdir(parents=True, exist_ok=True)
    (ROOT / '.pytest_cache/.gitignore').write_text('*\n', encoding='utf8')
    # Reuse the metadata-only probe without replacing its original bytes.
    for day in ['20240101','20240701']:
        original = FOLDER / (day + '.das')
        if not (CACHE / original.name).exists():
            (CACHE / original.name).write_bytes(original.read_bytes())
    result = {'schema':'osw.norkyst-continuous-acquisition.v1','status':'partial_acquisition_not_analysis',
              'preflight_file':source.SOURCE + '/preflight.json','preflight_sha256':source.PREFLIGHT_SHA256,
              'requested_months':months,'target_year_months':list(range(1,13)),
              'source_project':'Norkyst_v3','source_license':'CC-BY-4.0',
              'metadata_probe_file':source.SOURCE+'/metadata-probe.json',
              'metadata_probe_sha256':source.sha((FOLDER/'metadata-probe.json').read_bytes()),
              'credit':'Contains original Norkyst v3 hindcast subsets from MET Norway and Institute of Marine Research; OSW selects space, time and layer. Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026.',
              'responses':[], 'failures':[], 'new_width_record_admitted':False,'annual_width_range_km':None}
    def save():
        result['responses'].sort(key=lambda r:r['key'])
        result['updated_utc'] = datetime.now(timezone.utc).isoformat()
        path.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    requests = source.daily_requests(months)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(day_job, request, previous):request for request in requests}
        for future in as_completed(futures):
            request = futures[future]
            try:
                row = future.result();result['responses'].append(row)
                print(row['key'], row['hours'],'hours validated;',len(result['responses']),'of',len(requests),flush=True)
            except Exception as error:
                result['failures'].append({'request':list(request),'error':str(error)})
                print('FAILED',request,str(error),flush=True)
            save()
    if result['failures']:
        raise ValueError('Incomplete acquisition; originals and partial receipt retained. Rerun the same command to retry failed requests.')
    buckets = {}
    for row in result['responses']:
        bucket = row['date'][:7]
        members = buckets.setdefault(bucket,{})
        for kind in ['field','metadata']:
            name = row[kind + '_member'];raw = (CACHE / name).read_bytes()
            if source.sha(raw) != row[kind + '_sha256']:raise ValueError('Changed original before archiving')
            members[name] = raw
        row['archive_file'] = source.SOURCE + f'/originals-{phase}-{bucket}.zip'
    result['archives'] = [archive(FOLDER / f'originals-{phase}-{bucket}.zip',members) for bucket,members in sorted(buckets.items())]
    result['acquired_hours'] = sum(r['hours'] for r in result['responses'])
    result['status'] = 'complete_original_acquisition_pending_section_and_filter_analysis'
    result['generator_sha256'] = source.sha(Path(__file__).read_bytes())
    result['source_validator_sha256'] = source.sha((ROOT/'analysis/norkyst_continuous_source.py').read_bytes())
    save()
    print('COMPLETE:',result['acquired_hours'],'hourly fields; no derived current dimensions',flush=True)


if __name__ == '__main__':
    main()
