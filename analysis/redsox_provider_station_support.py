"""Audit complete provider metadata agreement without asserting synchronized casts."""
from collections import Counter
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = 'research/redsox-provider-station-support-preflight-v1.json'
REPORT = 'research/redsox-provider-station-support.json'
LADCP = 'research/redsox-ladcp-source-inventory.json'
CTD = 'research/redsox-ctd-companion-inventory.json'
METHODS = 'research/redsox-instrument-and-clock-source-review.json'


def pin(path):
    raw = (ROOT / path).read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def stamp(value):
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.utcoffset() is None:
        raise ValueError('Unspecified source timezone')
    return parsed.astimezone(timezone.utc)


def assess(velocity, hydrography, original_join=None):
    if hydrography is None:
        return {'status': 'missing_ctd_record', 'provider_station_fields_agree': False,
                'failed_checks': ['missing_ctd_record'], 'checks': {},
                'ladcp_minus_ctd_start_seconds': None, 'original_filename_join': None,
                'physical_cast_identity_verified': False, 'sample_level_synchronization_verified': False}
    a, b = stamp(velocity['time_utc']), stamp(hydrography['start_time_utc'])
    checks = {
        'same_campaign': velocity['campaign'] == hydrography['campaign'],
        'same_filename_station': velocity['station'] == hydrography['filename_station'],
        'ctd_header_agrees_with_station': hydrography['parsed_header_station'] == velocity['station'],
        'both_reported_positions_present': velocity['position_lon_lat'] is not None and hydrography['position_lon_lat'] is not None,
        'same_serialized_position': velocity['position_lon_lat'] is not None and velocity['position_lon_lat'] == hydrography['position_lon_lat'],
        'both_reported_times_present': a is not None and b is not None,
        'same_reported_utc_date': a is not None and b is not None and a.date() == b.date()}
    failed = [k for k, value in checks.items() if not value]
    return {'status': 'consistent_provider_station_records' if not failed else 'provider_metadata_review_required',
            'provider_station_fields_agree': not failed, 'failed_checks': failed, 'checks': checks,
            'ladcp_minus_ctd_start_seconds': None if a is None or b is None else int((a-b).total_seconds()),
            'original_filename_join': original_join,
            'physical_cast_identity_verified': False, 'sample_level_synchronization_verified': False}


def build():
    preflight = json.loads((ROOT / PREFLIGHT).read_bytes())
    for path, expected in preflight['dependencies'].items():
        if pin(path) != expected:
            raise ValueError('Changed frozen station-support input: ' + path)
    from build_redsox_ladcp_source_inventory import build as rebuild_velocity
    from build_redsox_ctd_companion_inventory import build as rebuild_ctd
    velocity = json.loads((ROOT / LADCP).read_bytes())
    hydrography = json.loads((ROOT / CTD).read_bytes())
    if velocity != rebuild_velocity() or hydrography != rebuild_ctd():
        raise ValueError('Changed original-source inventory reconstruction')
    if len(velocity['profiles']) != 445 or len(hydrography['profiles']) != 461:
        raise ValueError('Changed original archive coverage')
    candidates = {(r['campaign'], r['filename_station']): r for r in hydrography['profiles']}
    if len(candidates) != 461 or len({(r['campaign'], r['station']) for r in velocity['profiles']}) != 445:
        raise ValueError('Duplicate provider cast keys')
    joins = {r['ladcp_id']: r for r in hydrography['filename_joins']}
    if len(joins) != len(hydrography['filename_joins']):
        raise ValueError('Duplicate original filename joins')
    rows = []
    used = set()
    for v in velocity['profiles']:
        h = candidates.get((v['campaign'], v['station']))
        original = joins.get(v['id'])
        if (h is None) != (original is None) or (h is not None and original['ctd_id'] != h['id']):
            raise ValueError('Changed original provider join membership')
        if h is not None:
            used.add(h['id'])
        rows.append({'id': v['id'], 'campaign': v['campaign'], 'station': v['station'],
                     'velocity_metadata': v, 'ctd_metadata': h,
                     'assessment': assess(v, h, original),
                     'clock_context': 'Documented REDSOX-2 packet-loss synchronization limitation; individual alignment not recovered.' if v['campaign'] == 'RSX2' else 'REDSOX-1 individual sample synchronization not established by these metadata.',
                     'measurement_processing_exclusions_cleared': False,
                     'physical_width_admitted': False})
    unmatched = [r for r in hydrography['profiles'] if r['id'] not in used]
    if [r['id'] for r in unmatched] != hydrography['ctd_ids_without_ladcp_filename_match']:
        raise ValueError('Changed unmatched CTD membership')
    return {'schema': 'osw.redsox-provider-station-support.v1',
            'current_id': 'red-sea-saline-overflow',
            'status': 'provider_record_consistency_not_synchronized_cast_or_width_admission',
            'dependencies': preflight['dependencies'], 'methods_review': METHODS,
            'profiles': rows, 'ctd_records_without_ladcp': unmatched,
            'counts': {'velocity_records': len(rows), 'ctd_records': len(candidates),
                       'original_filename_joins': len(joins), 'unmatched_ctd_records': len(unmatched),
                       'status_counts': dict(sorted(Counter(r['assessment']['status'] for r in rows).items()))},
            'physical_cast_identity_verified': False, 'sample_level_synchronization_verified': False,
            'new_width_record_admitted': False, 'whole_current_width_km': None,
            'annual_width_range_km': None,
            'limitation': 'Matching provider station fields and a documented shared package do not independently verify exact cast identity, sample synchronization, processing validity or physical current edges.'}


def encoded(document=None):
    if document is None:
        document = build()
    return (json.dumps(document, indent=2, allow_nan=False) + '\n').encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    if args.action == 'build' and shutil.disk_usage(ROOT).free < 1024 ** 3:
        raise RuntimeError('Retain the1GiB derived-data start reserve')
    raw = encoded(); path = ROOT / REPORT
    if args.action == 'check':
        if path.read_bytes() != raw:
            raise ValueError('Station-support report differs from exact offline rebuild')
        print('PASS complete station-support report byte exact')
    else:
        if path.exists():
            raise ValueError('Refusing to overwrite an actual station-support calculation')
        path.write_bytes(raw); print('Wrote', REPORT, len(raw), 'bytes')
