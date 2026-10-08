"""Recover traceable cruise sampling positions without inferring current edges."""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'research/source-data/cchdo-atlantic-stations/'
OUTPUT = 'research/atlantic-cruise-station-context.json'
PROTOCOL = 'plans/atlantic-station-context-protocol-v1.md'
PATTERN = re.compile(
    r'^\s*(\S+)\s+(?:(\S+)\s+)?(\S+)\s+(\S+)\s+(\S+)\s+'
    r'(\d{6})\s+(\d{4}|-9)\s+(\S+)\s+'
    r'(\d{1,2})\s+(\d+(?:\.\d+)?)\s+([NS])\s+'
    r'(\d{1,3})\s+(\d+(?:\.\d+)?)\s+([EW])\s+(\S+)(.*)$')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def parse_events(raw, century):
    lines = raw.decode('ascii').splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip().startswith('----')) + 1
    events = []
    for line_number, line in enumerate(lines[start:], start + 1):
        if not line.strip() or line.strip() == '\x1a':
            continue
        match = PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Unparsed source line {line_number}: {line!r}')
        (expocode, section, station, cast, instrument, raw_date, raw_time, code,
         lat_d, lat_m, ns, lon_d, lon_m, ew, navigation, trailing) = match.groups()
        lat = int(lat_d) + float(lat_m) / 60
        lon = int(lon_d) + float(lon_m) / 60
        if float(lat_m) > 60 or float(lon_m) > 60 or lat > 90 or lon > 180:
            raise ValueError(f'Invalid source coordinate at line {line_number}')
        try:
            decoded_date = date(century + int(raw_date[4:]), int(raw_date[:2]), int(raw_date[2:4])).isoformat()
        except ValueError:
            decoded_date = None
        events.append({
            'source_line': line_number, 'raw_line': line,
            'archive_cruise_label': expocode, 'archive_section_label': section,
            'station_label': station, 'cast_label': cast,
            'instrument': instrument, 'event_code': code,
            'raw_date_mmddyy': raw_date, 'decoded_date': decoded_date,
            'raw_time_utc': raw_time, 'navigation_code': navigation,
            'raw_latitude': f'{lat_d} {lat_m} {ns}',
            'raw_longitude': f'{lon_d} {lon_m} {ew}',
            'source_minutes_equal_sixty': float(lat_m) == 60 or float(lon_m) == 60,
            'coordinates': [round(lon * (-1 if ew == 'W' else 1), 8),
                            round(lat * (-1 if ns == 'S' else 1), 8)],
            'trailing_metadata': trailing,
        })
    return events


def context_points(events, window):
    """Display one reported hydrographic event per cast within the paper window."""
    selected = {}
    priority = {'BO': 0, 'MR': 1, 'BE': 2, 'EN': 3}
    for event in events:
        if event['instrument'] not in ('ROS', 'CTD') or not event['decoded_date']:
            continue
        if not window['start'] <= event['decoded_date'] <= window['end']:
            continue
        key = (event['archive_section_label'], event['station_label'], event['cast_label'])
        rank = (priority.get(event['event_code'], 4), event['source_line'])
        previous = selected.get(key)
        if previous is None or rank < previous[0]:
            selected[key] = (rank, event)
    return [dict(event) for _, event in sorted(selected.values(), key=lambda pair: pair[1]['source_line'])]


def build():
    acquisition_path = DIRECTORY + 'acquisition.json'
    acquisition = json.loads((ROOT / acquisition_path).read_bytes())
    extraction_path = 'research/atlantic-cruise-section-width-extraction.json'
    extraction = json.loads((ROOT / extraction_path).read_bytes())
    windows = {}
    for record in extraction['measurements']:
        ctx = record['hydrographic_section_context']
        windows.setdefault(ctx['cruise_id'], []).append(ctx['cruise_sampling_window'])
    # The 2018 source is retained as evidence for the held-out 24 S rows, not admitted widths.
    windows['740H20180228'] = [{'start': '2018-03-02', 'end': '2018-04-05'}]
    cruises = []
    for source in acquisition['files']:
        raw = (ROOT / source['file']).read_bytes()
        if len(raw) != source['bytes'] or hashlib.sha256(raw).hexdigest() != source['sha256']:
            raise ValueError('Changed station source: ' + source['file'])
        identifier = source['paper_cruise_id']
        expected_windows = windows[identifier]
        century = int(expected_windows[0]['start'][:4]) // 100 * 100
        events = parse_events(raw, century)
        expected_years = {year for window in expected_windows
                          for year in range(int(window['start'][:4]), int(window['end'][:4]) + 1)}
        conflicting = [e['source_line'] for e in events if e['decoded_date'] is None
                       or int(e['decoded_date'][:4]) not in expected_years]
        cruises.append({
            **source, 'paper_sampling_windows': expected_windows,
            'archive_cruise_labels': sorted({e['archive_cruise_label'] for e in events}),
            'archive_section_labels': sorted({e['archive_section_label'] for e in events if e['archive_section_label']}),
            'source_event_count': len(events),
            'hydrographic_cast_count': len({(e['archive_section_label'], e['station_label'], e['cast_label'])
                                           for e in events if e['instrument'] in ('ROS', 'CTD')}),
            'source_date_conflict_lines': conflicting, 'events': events,
        })
    by_cruise = {row['paper_cruise_id']: row for row in cruises}
    spans = []
    for record in extraction['measurements']:
        ctx = record['hydrographic_section_context']
        cruise = by_cruise.get(ctx['cruise_id'])
        points = context_points(cruise['events'], ctx['cruise_sampling_window']) if cruise else []
        spans.append({
            'measurement_id': record['id'], 'current_id': record['current_id'],
            'paper_cruise_id': ctx['cruise_id'], 'paper_section_id': ctx['section_id'],
            'paper_station_range_label': ctx['source_station_range_label'],
            'sampling_window': ctx['cruise_sampling_window'],
            'status': 'dated_cruise_sampling_context' if points else
                      ('source_date_conflict' if cruise and cruise['source_date_conflict_lines'] else 'station_source_not_recovered'),
            'geometry_role': 'cruise_sampling_context_not_current_boundary',
            'boundary_station_mapping_status': 'unresolved',
            'current_footprint_eligible': False, 'state_intersection_eligible': False,
            'annual_series_eligible': False, 'coordinate_uncertainty_degrees': None,
            'coordinate_datum': None, 'point_count': len(points), 'points': points,
            'source_file': cruise['file'] if cruise else None,
            'source_sha256': cruise['sha256'] if cruise else None,
            'cruise_url': cruise['cruise_url'] if cruise else None,
        })
    return {
        'schema': 'osw.atlantic-cruise-station-context.v1',
        'status': 'source_context_not_new_scientific_admission',
        'acquisition_file': acquisition_path, 'acquisition_sha256': digest(acquisition_path),
        'protocol_file': PROTOCOL, 'protocol_sha256': digest(PROTOCOL),
        'generator_file': 'analysis/build_atlantic_station_context.py',
        'generator_sha256': digest('analysis/build_atlantic_station_context.py'),
        'width_extraction_file': extraction_path, 'width_extraction_sha256': digest(extraction_path),
        'scope': 'Original archive event positions and dated cruise sampling context. Paper station indices are unresolved; no current edges, route distances, annual cycles or state joins.',
        'cruises': cruises, 'measurement_contexts': spans,
        'source_conflicts': [
            {'paper_cruise_id': '740H20180228', 'kind': 'nominal_latitude_conflict_resolved',
             'paper_table_1_label': '19 S', 'paper_table_2_label': '24 S',
             'archive_summary_section_label': 'A09.5_24S',
             'evidence_url': 'https://cchdo.ucsd.edu/cruise/740H20180228',
             'evidence_locator': "Brian King's 2018-04-23 station-section note and 2018-04-18 submission",
             'resolution': 'Use nominal 24 S for the cruise correspondence; original publisher cell retained. Station-index pairing remains unresolved. Held-out widths are not admitted by this audit.'},
            {'paper_cruise_id': '64PE20070830', 'kind': 'station_date_year_conflict_unresolved',
             'resolution': 'Summary dates decode to 2005 despite paper sampling window in 2007. Retain source dates and omit dated map points until independently corrected.'},
        ],
    }


if __name__ == '__main__':
    document = build()
    (ROOT / OUTPUT).write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Recovered {sum(c['source_event_count'] for c in document['cruises'])} events from {len(document['cruises'])} cruises; "
          f"{sum(bool(s['points']) for s in document['measurement_contexts'])} dated measurement contexts")
