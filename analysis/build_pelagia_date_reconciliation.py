"""Match original casts against a separately sourced corrected bottle product."""
import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from build_atlantic_station_context import parse_events

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'research/source-data/cchdo-pelagia-2007/'
OUTPUT = 'research/pelagia-2007-station-date-reconciliation.json'
PROTOCOL = 'plans/pelagia-station-date-reconciliation-protocol-v1.md'
SUMMARY = 'research/source-data/cchdo-atlantic-stations/64PE20070830-summary.txt'


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def extract_casts(raw):
    lines = raw.decode('ascii').splitlines()
    if lines[0] != 'BOTTLE,20240919CCHHYDRO':
        raise ValueError('Changed bottle edition')
    header = next(i for i, line in enumerate(lines) if line.startswith('EXPOCODE,'))
    casts = {}
    for line_number, values in enumerate(csv.DictReader(lines[header:]), header + 2):
        identifier = values['EXPOCODE'].strip()
        if not identifier and line_number == header + 2:
            continue  # The Exchange units row is not a bottle observation.
        if identifier == 'END_DATA':
            continue
        if not identifier:
            raise ValueError('Missing bottle cruise identity')
        record = {k: values[k].strip() for k in ['EXPOCODE', 'SECT_ID', 'STNNBR', 'CASTNO', 'DATE', 'TIME', 'LATITUDE', 'LONGITUDE']}
        stamp = record['DATE']
        record['date'] = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:])).isoformat()
        if not '2007-08-30' <= record['date'] <= '2007-09-27':
            raise ValueError('Bottle date outside original cruise interval')
        lat, lon = float(record['LATITUDE']), float(record['LONGITUDE'])
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError('Invalid bottle position')
        key = (record['STNNBR'], record['CASTNO'])
        if key in casts:
            if casts[key]['record'] != record:
                raise ValueError('Conflicting bottle metadata for a cast')
            casts[key]['bottle_source_lines'].append(line_number)
        else:
            casts[key] = {'record': record, 'bottle_source_lines': [line_number]}
    return casts


def reconcile(events, casts):
    records, seen = [], set()
    for event in events:
        key = (event['station_label'], event['cast_label'])
        if key in seen or key not in casts:
            raise ValueError('Ambiguous or missing archive cast identity')
        seen.add(key)
        cast = casts[key]; record = cast['record']
        if record['EXPOCODE'] != event['archive_cruise_label'] or record['SECT_ID'] != event['archive_section_label']:
            raise ValueError('Cruise or section mismatch')
        if record['date'][5:] != event['decoded_date'][5:]:
            raise ValueError('Source month/day mismatch')
        differences = [float(record['LONGITUDE']) - event['coordinates'][0],
                       float(record['LATITUDE']) - event['coordinates'][1]]
        if any(abs(v) > .00013334 for v in differences):
            raise ValueError('Source position mismatch')
        def minutes(value):
            if len(value) != 4 or not value.isdigit() or int(value[:2]) > 23 or int(value[2:]) > 59:
                raise ValueError('Invalid source UTC time')
            return int(value[:2]) * 60 + int(value[2:])
        time_difference = minutes(record['TIME']) - minutes(event['raw_time_utc'])
        if abs(time_difference) > 1:
            raise ValueError('Source time mismatch exceeds one minute')
        records.append({
            'summary_source_line': event['source_line'], 'station_label': key[0], 'cast_label': key[1],
            'original_summary_date': event['decoded_date'], 'original_summary_time_utc': event['raw_time_utc'],
            'corrected_bottle_date': record['date'], 'corrected_bottle_time_utc': record['TIME'],
            'bottle_minus_summary_time_minutes': time_difference,
            'bottle_minus_summary_coordinates_degrees': differences,
            'bottle_source_lines': cast['bottle_source_lines'],
            'identity_basis': 'exact cruise/section/station/cast; same month/day; corroborated position; UTC times within one minute',
        })
    if seen != set(casts):
        raise ValueError('Extra bottle casts without summary matches')
    return records


def build():
    acquisition = json.loads((ROOT / (DIRECTORY + 'acquisition.json')).read_bytes())
    summary_acquisition = json.loads((ROOT / 'research/source-data/cchdo-atlantic-stations/acquisition.json').read_bytes())
    summary_source = next(r for r in summary_acquisition['files'] if r['file'] == SUMMARY)
    for source in [acquisition, summary_source]:
        if digest(source['file']) != source['sha256'] or (ROOT / source['file']).stat().st_size != source['bytes']:
            raise ValueError('Changed pinned source: ' + source['file'])
    events = parse_events((ROOT / SUMMARY).read_bytes(), 2000)
    casts = extract_casts((ROOT / acquisition['file']).read_bytes())
    records = reconcile(events, casts)
    if len(records) != 46:
        raise ValueError('Changed Pelagia station inventory')
    return {'schema': 'osw.pelagia-station-date-reconciliation.v1',
            'status': 'source_metadata_reconciliation_not_boundary_admission',
            'paper_cruise_id': '64PE20070830', 'summary_source_file': SUMMARY,
            'summary_sha256': digest(SUMMARY), 'bottle_source_file': acquisition['file'],
            'bottle_sha256': acquisition['sha256'], 'acquisition_file': DIRECTORY + 'acquisition.json',
            'acquisition_sha256': digest(DIRECTORY + 'acquisition.json'),
            'protocol_file': PROTOCOL, 'protocol_sha256': digest(PROTOCOL),
            'generator_file': 'analysis/build_pelagia_date_reconciliation.py',
            'generator_sha256': digest('analysis/build_pelagia_date_reconciliation.py'),
            'summary_parser_file': 'analysis/build_atlantic_station_context.py',
            'summary_parser_sha256': digest('analysis/build_atlantic_station_context.py'),
            'source_url': acquisition['source_url'], 'cruise_url': acquisition['cruise_url'],
            'date_source': 'explicitly corrected integrated bottle product, not year inferred from cruise identifier',
            'records': records}


if __name__ == '__main__':
    document = build()
    (ROOT / OUTPUT).write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')
    print('Reconciled', len(document['records']), 'original cast dates')
