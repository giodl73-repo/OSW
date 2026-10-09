"""Build a separate lossless index corpus, including on-demand seasonal sources."""
import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'almanac/index-catalog.json'
OUTPUT = ROOT / 'almanac/index-data.json.gz'
SEASONS = ROOT / 'research/noaa-munster-eddy-seasonal-manifest-2021-2023.json'
OPTIONAL = 'research/ocean-current-reference-route-state-join.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory():
    registry = json.loads((ROOT / 'almanac/index-sources.json').read_bytes())
    if registry['schema'] != 'osw.almanac-index-sources.v1':
        raise ValueError('Unsupported index source registry')
    declared = registry['documents']
    if len(set(declared)) != len(declared):
        raise ValueError('Duplicate index source address')
    paths = {(ROOT / path).resolve() for path in declared}
    manifest = json.loads(SEASONS.read_bytes())
    paths.update((ROOT / 'almanac' / row['path']).resolve() for row in manifest['snapshots'])
    # Rust support views depend on these even after the browser stops reading them.
    paths.update(ROOT / path for path in [
        'research/ocean-current-dated-timeline-2025.json',
        'research/ocean-current-dated-timeline.json'])
    for path in paths:
        path.relative_to(ROOT)  # Reject escape from the source workspace.
        if path.suffix != '.json':
            raise ValueError('Unsupported index source: ' + str(path))
    return sorted(path.relative_to(ROOT).as_posix() for path in paths)


def build():
    documents, descriptors = {}, []
    for path in inventory():
        raw = (ROOT / path).read_bytes()
        doc = json.loads(raw)
        if not isinstance(doc, (dict, list)):
            raise ValueError('Unsupported index document shape: ' + path)
        documents[path] = raw.decode('utf-8')
        descriptors.append({'path': path, 'source_sha256': digest(raw), 'source_bytes': len(raw),
                            'root_kind': 'object' if isinstance(doc, dict) else 'array',
                            'source_schema': doc.get('schema') if isinstance(doc, dict) else None,
                            'optional': path == OPTIONAL})
    from check_zeehan_seasonal_calendar import PATH as calendar_path, validate as validate_calendar
    validate_calendar(json.loads(documents[calendar_path]))
    from check_atlantic_euc_section_properties import validate as validate_atlantic_sections
    validate_atlantic_sections(json.loads(documents["research/atlantic-euc-layer-island-scope-audit.json"]))
    from build_thor_ursa_source_panels import PATH as panel_path, validate as validate_panels
    validate_panels(json.loads(documents[panel_path]))
    from check_astrid_radial_scales import validate
    validate(json.loads(documents['research/astrid-2000-radial-scale-scope-audit.json']), json.loads(documents['research/named-eddy-geography.json']))
    from build_agulhas_ring_radius_audit import validate as validate_ring_radii
    validate_ring_radii(json.loads(documents['research/agulhas-guerra-2022-ring-radius-scope-audit.json']),json.loads(documents['research/named-eddy-geography.json']))
    from check_original_regional_widths import validate_row as validate_original_width
    for row in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements']:
        if row.get('original_regional_context'):validate_original_width(row)
    station_path = 'research/atlantic-cruise-station-context.json'
    recurrence_path = 'research/black-sea-eddy-recurrence.json'
    if recurrence_path in documents:
        from build_black_sea_eddy_recurrence import validate as validate_recurrence
        validate_recurrence(json.loads(documents[recurrence_path]))
    if station_path in documents:
        from build_atlantic_station_context import build as build_station_context
        if json.loads(documents[station_path]) != build_station_context():
            raise ValueError('Stale or changed Atlantic station context; regenerate from checked archive bytes')
        from build_pelagia_date_reconciliation import build as build_date_reconciliation, OUTPUT as date_path
        if date_path not in documents or json.loads(documents[date_path]) != build_date_reconciliation():
            raise ValueError('Missing or stale corrected station-date source')
    # Bind on-demand discovery to the complete manifest; file support stays distinct
    # from the manifest's source_product/source_subset hashes.
    seasons = json.loads(SEASONS.read_bytes())
    for row in seasons['snapshots']:
        path = (ROOT / 'almanac' / row['path']).resolve().relative_to(ROOT).as_posix()
        doc = json.loads(documents[path])
        if doc['date'] != row['date'] or doc['source_sha256'] != row['source_sha256']:
            raise ValueError('Seasonal snapshot source/date mismatch: ' + path)
        if len(doc['entries']) != row['detection_count']:
            raise ValueError('Seasonal snapshot inventory mismatch: ' + path)
    raw = (json.dumps({'schema': 'osw.almanac-index-bundle.v1', 'documents': documents},
                      ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    catalog = {'schema': 'osw.almanac-index-catalog.v1',
               'status': 'source_snapshot_not_new_scientific_admission',
               'documents': descriptors, 'source_count': len(descriptors),
               'source_bytes': sum(row['source_bytes'] for row in descriptors),
               'bundle_sha256': digest(raw), 'compressed_sha256': digest(compressed),
               'bundle_bytes': len(raw), 'compressed_bytes': len(compressed),
               'scope': 'Exact original JSON sources. File-scoped query addresses are not persistent identities or new current/eddy membership claims.',
               'input_sha256': {path: digest((ROOT / path).read_bytes()) for path in [
                   'almanac/index-sources.json', 'almanac/app.js', 'almanac/atlas-sample-states.js', SEASONS.relative_to(ROOT).as_posix(),
                   'almanac/release/v0.1.0/manifest.json',
                   'analysis/build_almanac_index_bundle.py']}}
    return raw, compressed, catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-json', type=Path,
                        help='Also save decompressed JSON for native inspection')
    args = parser.parse_args()
    raw, compressed, catalog = build()
    OUTPUT.write_bytes(compressed)
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.output_json:
        args.output_json.write_bytes(raw)
    print(f"Built separate index corpus: {catalog['source_count']} sources; "
          f"{catalog['source_bytes']} original bytes; {len(compressed)} compressed bytes")


if __name__ == '__main__':
    main()
