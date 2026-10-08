"""Extract publisher cells without replacing cruise snapshots with decade means."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'research/source-data/cainzos-atlantic-2023/'
OUTPUT = 'research/atlantic-cruise-section-width-extraction.json'
PROTOCOL = 'plans/atlantic-cruise-section-width-protocol-v2.md'
URL = 'https://os.copernicus.org/articles/19/1009/2023/'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
# Explicit source section -> canonical identity; recirculations remain separate.
OWNERS = {
    'Malvinas Current': 'falkland', 'Brazil Current': 'brazil',
    'Benguela Current': 'benguela', 'Canary Current': 'canary',
    'Gulf Stream': 'gulf-stream', 'North Atlantic Current': 'north-atlantic',
    'Irminger Current': 'irminger', 'East Greenland Current': 'east-greenland',
    'Upper West Greenland Current': 'west-greenland',
}
# Table 1 row, section sampling start/end. These are cruise windows, not dates
# when individual selected boundary station pairs were occupied.
CRUISES = {
    (-45, '1990–1999'): (2, '1992-12-27', '1993-01-30'),
    (-30, '1990–1999'): (3, '1992-12-30', '1993-01-28'),
    (-19, '1990–1999'): (4, '1991-02-12', '1991-03-18'),
    (24.5, '1990–1999'): (6, '1992-07-20', '1992-08-14'),
    (47, '1990–1999'): (7, '1993-07-08', '1993-07-25'),
    (53, '1990–1999'): (8, '1990-07-06', '1990-07-09'),
    (58, '1990–1999'): (9, '1991-08-08', '1991-09-03'),
    (-30, '2000–2009'): (10, '2003-11-07', '2003-12-02'),
    (-24, '2000–2009'): (11, '2009-03-16', '2009-04-19'),
    (24.5, '2000–2009'): (12, '2004-04-07', '2004-05-09'),
    (36, '2000–2009'): (13, '2005-05-03', '2005-06-12'),
    (53, '2000–2009'): (14, '2005-05-29', '2005-06-03'),
    (58, '2000–2009'): (15, '2007-09-12', '2007-09-22'),
    (-30, '2010–2019'): (16, '2011-09-28', '2011-10-29'),
    (-24, '2010–2019'): (17, '2018-03-02', '2018-04-05'),
    (24.5, '2010–2019'): (18, '2011-01-28', '2011-03-11'),
    (47, '2010–2019'): (19, '2013-05-29', '2013-06-14'),
    (53, '2010–2019'): (20, '2014-06-09', '2014-06-18'),
    (58, '2010–2019'): (21, '2014-06-24', '2014-07-17'),
}


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def read_cells(path):
    """Read the original first sheet; retain empty cells and source row numbers."""
    with ZipFile(ROOT / path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            for item in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si', NS):
                strings.append(''.join(t.text or '' for t in item.findall('.//s:t', NS)))
        rows = []
        for source_row in ET.fromstring(archive.read('xl/worksheets/sheet1.xml')).findall('s:sheetData/s:row', NS):
            values = {}
            for cell in source_row.findall('s:c', NS):
                value = cell.find('s:v', NS)
                if cell.find('s:f', NS) is not None:
                    raise ValueError('Unexpected publisher formula; cached values cannot replace formulas')
                kind = cell.get('t')
                if kind == 'inlineStr':
                    content = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
                elif value is None:
                    content = None
                elif kind == 's':
                    content = strings[int(value.text)]
                elif kind in ('str', 'b'):
                    content = value.text
                else:
                    content = float(value.text)
                    if content.is_integer(): content = int(content)
                values[re.sub(r'\d', '', cell.attrib['r'])] = content
            rows.append({'row': int(source_row.attrib['r']), 'cells': values})
        return rows


def build():
    acquisition = json.loads((ROOT / (DIRECTORY + 'acquisition.json')).read_bytes())
    for source in acquisition['files']:
        if digest(source['file']) != source['sha256'] or (ROOT / source['file']).stat().st_size != source['bytes']:
            raise ValueError('Changed publisher workbook: ' + source['file'])
    from build_atlantic_station_context import parse_events
    station_acquisition_file = 'research/source-data/cchdo-atlantic-stations/acquisition.json'
    station_acquisition = json.loads((ROOT / station_acquisition_file).read_bytes())
    source_2018 = next(s for s in station_acquisition['files'] if s['paper_cruise_id'] == '740H20180228')
    if digest(source_2018['file']) != source_2018['sha256'] or (ROOT / source_2018['file']).stat().st_size != source_2018['bytes']:
        raise ValueError('Changed 2018 independent cruise identity source')
    archive_events = parse_events((ROOT / source_2018['file']).read_bytes(), 2000)
    if not archive_events or any(e['archive_cruise_label'] != '740H20180228' or e['archive_section_label'] != 'A09.5_24S' for e in archive_events):
        raise ValueError('2018 nominal cruise/section correspondence unresolved')
    identity_evidence = {
        'source_file': source_2018['file'], 'source_sha256': source_2018['sha256'],
        'source_url': source_2018['source_url'], 'cruise_url': source_2018['cruise_url'],
        'source_bytes': source_2018['bytes'], 'archive_section_label': 'A09.5_24S',
        'acquisition_file': station_acquisition_file, 'acquisition_sha256': digest(station_acquisition_file),
        'parser_file': 'analysis/build_atlantic_station_context.py',
        'parser_sha256': digest('analysis/build_atlantic_station_context.py'),
        'scope': 'Independent nominal cruise-section correspondence only; not width endpoints or model station-index recovery.',
    }
    tables = {str(i): read_cells(DIRECTORY + f'table-{i}.xlsx') for i in (1, 2)}
    cruise_rows = {r['row']: r['cells'] for r in tables['1']}
    names = {r['id']: r['name'] for r in json.loads((ROOT / 'research/ocean-current-almanac.json').read_bytes())['entries']}
    records, exclusions = [], []
    group = None
    for source_row in tables['2'][1:]:
        cells = source_row['cells']
        if cells.get('B') is None:
            group = cells['A']
            continue
        match = re.fullmatch(r'(.+) ([\d.]+)∘\s*([NS])', group)
        if not match: raise ValueError('Unrecognized publisher group: ' + group)
        label, latitude, hemisphere = match.groups()
        latitude = float(latitude) * (1 if hemisphere == 'N' else -1)
        decade = cells['A']
        if label not in OWNERS:
            exclusions.append({'table_2_row': source_row['row'], 'source_group': group, 'reason': 'Outside this first batch: recirculation, water/front identity or already-assessed current; no identity or width admission inferred.'})
            continue
        table_1_row, start, end = CRUISES[(latitude, decade)]
        cruise = cruise_rows[table_1_row]
        current = OWNERS[label]
        source_context = {
            'table_2_row': source_row['row'], 'table_1_row': table_1_row,
            'source_group': group, 'inverse_model_decade_group': decade,
            'cruise_id': cruise['D'], 'section_id': cruise['A'],
            'cruise_sampling_window': {'start': start, 'end': end},
            'sampling_window_role': 'whole_section_sampling_window_not_exact_boundary_station_occupation',
            'nominal_section_latitude_degrees_north': latitude,
            'table_1_latitude_label': cruise['E'],
            'source_station_range_label': cells['B'],
            'source_longitude_limits_degrees_east': [float(v) for v in cells['C'].split(':')],
            'source_layer_indices_label': cells['E'],
            'source_depth_extent_m': [int(v) for v in cells['F'].split(' to ')],
            'station_index_convention': 'publisher_table_label_not_reindexed_against_table_1_station_count',
            'nominal_latitude_is_endpoint_latitude': False,
            'depth_extent_is_uniform_fixed_measurement_layer': False,
            'decade_group_is_time_average': False,
            'source_distance_is_recomputed_from_nominal_latitude': False,
            'source_width_uncertainty_km': None,
        }
        if table_1_row == 17:
            if cruise['D'] != '740H20180228' or cruise['A'] != 'A095':
                raise ValueError('Changed publisher 2018 cruise identity')
            source_context['nominal_latitude_reconciliation'] = identity_evidence
        records.append({
            'id': f'cainzos-2023-t02-row-{source_row["row"]}-section-span',
            'current_id': current, 'name': names[current],
            'status': 'editorial_source_extraction_not_canonical',
            'measurement_type': 'published_inverse_hydrographic_section_span',
            'width_metric': 'transport_diagnosed_hydrographic_section_span',
            'width_metric_label': 'transport-selected cruise-section span',
            'approximate_width_km': cells['D'], 'width_range_km': None,
            'range_interpretation': 'Publisher Table 2 distance rounded to kilometres. Width uncertainty is not reported. Transport uncertainty is a separate quantity. Separate cruises and layers are not an annual range.',
            'geographic_scope': f'{group}; source longitude limits {cells["C"]} degrees east. Section track may deviate from nominal latitude near boundaries. Endpoint latitudes remain unextracted.',
            'section_geometry': None,
            'section_orientation': 'Nominally zonal hydrographic track; boundary/platform stations may deviate to cross the main flow. Exact boundary track orientation unresolved.',
            'layer': f'Publisher neutral-density layer indices {cells["E"]}; reported depth extent {cells["F"]} m. Density surfaces are not a uniform fixed-depth slice.',
            'time_convention': f'{cruise["D"]}: section sampled {start} to {end}; inverse-model group {decade}. Cruise snapshot, not a decade mean or seasonal composite.',
            'boundary_rule': 'Section 2.3: station pairs selected by consistent slope of eastward accumulated horizontal mass transport; vertical extent by the same integrated flow direction. No fixed speed cutoff or instantaneous velocity envelope inferred.',
            'boundary_sides': 'source_selected_station_limits',
            'source_url': URL, 'source_citation': 'Caínzos et al. (2023), Consistent picture of the horizontal circulation of the Atlantic Ocean over 3 decades, Ocean Science 19, 1009–1045, doi:10.5194/os-19-1009-2023.',
            'source_locator': f'Table 2, Worksheet 1, row {source_row["row"]}, columns A–F; Table 1 row {table_1_row}; Sections 2.1–2.3.',
            'source_retrieved_date': acquisition['retrieved_date'],
            'source_evidence_kind': 'published_inverse_model_hydrographic_cruise_snapshot',
            'extraction_method': 'Publisher XLSX cells retained and distance transcribed directly; explicit section/cruise join. No map or longitude-to-distance conversion.',
            'whole_current_representative': False, 'width_rank_eligible': False,
            'annual_extrema_eligible': False, 'seasonal_playback_eligible': False,
            'full_width_inference_eligible': False, 'is_confidence_interval': False,
            'phase_kind': 'inverse_hydrographic_section_span',
            'phase_label': f'{cruise["D"]} · {latitude:g} degrees north',
            'observed_period': None, 'calendar_months': None, 'fixed_layer_bounds_m': None,
            'hydrographic_section_context': source_context,
            'remaining_gates': ['Recover actual station coordinates before a geographic edge locator or state intersection.', 'Independent scientific admission and release review.'],
        })
    return {
        'schema': 'osw.atlantic-cruise-section-width-extraction.v1',
        'status': 'editorial_source_extraction_not_canonical',
        'source_url': URL, 'source_license': 'CC-BY-4.0',
        'acquisition_file': DIRECTORY + 'acquisition.json',
        'acquisition_sha256': digest(DIRECTORY + 'acquisition.json'),
        'protocol_file': PROTOCOL, 'protocol_sha256': digest(PROTOCOL),
        'generator_file': 'analysis/build_atlantic_cruise_widths.py',
        'generator_sha256': digest('analysis/build_atlantic_cruise_widths.py'),
        'additional_source_receipts': identity_evidence,
        'original_tables': tables, 'measurements': records, 'excluded_rows': exclusions,
        'scope': 'Local transport-selected hydrographic spans. Cruise snapshots remain separate by section and layer; no global width ranking, annual extrema, route buffers or geographic boundaries.',
    }


def main():
    document = build()
    (ROOT / OUTPUT).write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Extracted {len(document["measurements"])} spans across {len(set(r["current_id"] for r in document["measurements"]))} currents')


def update_inventory():
    """Idempotently import this batch while preserving all earlier records."""
    document = build()
    path = ROOT / 'research/ocean-current-width-inventory.json'
    inventory = json.loads(path.read_bytes())
    inventory['as_of'] = '2026-10-07'
    inventory['measurements'] = [r for r in inventory['measurements'] if not r['id'].startswith('cainzos-2023-t02-row-')]
    inventory['measurements'].extend({**r, 'extraction_file': OUTPUT, 'extraction_sha256': digest(OUTPUT)} for r in document['measurements'])
    for decision in inventory['current_decisions']:
        members = [r['id'] for r in inventory['measurements'] if r['current_id'] == decision['current_id']]
        if members:
            decision['measurement_ids'] = members
            decision['width_decision'] = 'scoped_width_evidence_present'
            if decision['current_id'] in OWNERS.values():
                decision['next_action'] = 'Resolve inverse-model station boundary pairings and evaluate independent scientific admission. Separate cruise spans do not establish seasonal or whole-current width.'
    inventory['counts']['measurements'] = len(inventory['measurements'])
    inventory['counts']['currents_with_scoped_width_evidence'] = len({r['current_id'] for r in inventory['measurements']})
    inventory['counts']['currents_not_assessed'] = sum(d['width_decision'] == 'width_not_assessed' for d in inventory['current_decisions'])
    path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    frames = ROOT / 'research/ocean-current-seasonal-route-frames.json'
    frame_document = json.loads(frames.read_bytes())
    frame_document['width_inventory_sha256'] = digest('research/ocean-current-width-inventory.json')
    frames.write_text(json.dumps(frame_document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-inventory', action='store_true')
    arguments = parser.parse_args()
    main()
    if arguments.update_inventory: update_inventory()
