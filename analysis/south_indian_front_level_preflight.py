"""Declare supplemental source support before any new depth values are requested."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from acquire_indian_secc_hycom_2013 import pin
from acquire_eac_100m_source import write_json
from acquire_south_indian_front_levels import ROOT, PROTOCOL, validate_plan

DECLARATION = 'research/south-indian-front-level-source-preflight.json'
OPERATOR = 'analysis/south_indian_front_level_preflight.py'
OLD = 'research/source-data/hycom-south-indian-hydrography-2013/'


def dependencies(plan):
    paths = [*plan['operators'], PROTOCOL, OPERATOR,
             'analysis/south_indian_front_temperature.py',
             'research/sparrow-1996-south-indian-front-definition-review.json',
             'research/source-data/sparrow-south-indian-1996/acquisition.json',
             'research/stramma-1992-south-indian-full-paper-review.json',
             'research/south-indian-hycom-2013-paired-profile-candidates.json',
             'research/south-indian-hycom-2013-paired-profile-candidates-v2.json']
    paths += [OLD+n for n in ['selection.json', 'acquisition.json', 'quality.json',
                             'monthly.npz', 'monthly-fields.json', 'source-responses.zip']]
    earlier = json.loads((ROOT/OLD/'acquisition.json').read_bytes())
    paths.extend(earlier['dependencies'])
    for report in ['research/south-indian-hycom-2013-paired-profile-candidates.json',
                   'research/south-indian-hycom-2013-paired-profile-candidates-v2.json']:
        paths.extend(json.loads((ROOT/report).read_bytes())['dependencies'])
    return {name: pin(ROOT/name) for name in dict.fromkeys(paths)}


def check_cohort(plan):
    earlier = json.loads((ROOT/OLD/'selection.json').read_bytes())
    if (plan['dataset_url'] != earlier['dataset_url']
            or plan['selection'] != {**earlier['selection'], 'depth': [19, 22]}
            or plan['missing_daily_00z'] != earlier['missing_daily_00z']
            or plan['minimum_pairs'] != earlier['minimum_pairs']
            or plan['scale'] != earlier['scale'] or plan['offsets'] != earlier['offsets']):
        raise ValueError('Supplementary grid/cohort/packing changed')
    old_times = [(r['month'], i) for r in earlier['requests'] for i in r['time_indices']]
    times = [(r['month'], i) for r in plan['requests'] for i in r['time_indices']]
    if (times != old_times or len(times) != 363
            or any(not 1 <= len(r['time_indices']) <= 3 for r in plan['requests'])):
        raise ValueError('Changed complete daily support or frozen partition')


def declare(directory):
    directory = Path(directory)
    plan = validate_plan(directory)
    check_cohort(plan)
    if (ROOT/DECLARATION).exists() or (directory/'preflight.json').exists():
        raise ValueError('Do not replace an existing source declaration')
    allowed = {'metadata.das', 'metadata.dds', 'coordinates.ascii', 'selection.json'}
    if {p.name for p in directory.iterdir()} != allowed:
        raise ValueError('Unexpected files before first new field acquisition')
    doc = {'schema': 'osw.south-indian-front-level-preflight.v1',
           'declared_utc': datetime.now(timezone.utc).isoformat(),
           'selection': pin(directory/'selection.json'), 'dependencies': dependencies(plan),
           'native_depths_m': [100, 200], 'native_depth_indices': [19, 22],
           'daily_timestamps': 363, 'request_count': len(plan['requests']),
           'maximum_dates_per_request': 3, 'workers': 2,
           'socket_timeout_seconds': 180, 'response_byte_limit': 20_000_000,
           'minimum_free_bytes': 1024**3, 'conversion_gsw_version': '3.6.23',
           'conversion_temperature_scale': 'ITS-90 assumption; not independently verified',
           'source_temperature_is_potential_temperature': False,
           'current_association_verified': False, 'physical_width_admitted': False,
           'physical_axis_admitted': False, 'physical_length_admitted': False,
           'annual_extrema_admitted': False, 'seasonal_footprint_admitted': False,
           'preserve_earlier_source_and_diagnostics': True}
    write_json(ROOT/DECLARATION, doc)
    (directory/'preflight.json').write_bytes((ROOT/DECLARATION).read_bytes())
    return doc


def checked(directory):
    directory = Path(directory)
    plan = validate_plan(directory)
    check_cohort(plan)
    if pin(directory/'preflight.json') != pin(ROOT/DECLARATION):
        raise ValueError('Archived preflight differs')
    doc = json.loads((ROOT/DECLARATION).read_bytes())
    if (doc['schema'] != 'osw.south-indian-front-level-preflight.v1'
            or doc['selection'] != pin(directory/'selection.json')
            or doc['dependencies'] != dependencies(plan)
            or doc['request_count'] != len(plan['requests'])
            or doc['native_depths_m'] != [100, 200] or doc['native_depth_indices'] != [19, 22]
            or doc['daily_timestamps'] != 363 or doc['maximum_dates_per_request'] != 3
            or doc['workers'] != 2 or doc['socket_timeout_seconds'] != 180
            or doc['response_byte_limit'] != 20_000_000 or doc['minimum_free_bytes'] != 1024**3
            or doc['conversion_gsw_version'] != '3.6.23'
            or doc['conversion_temperature_scale'] != 'ITS-90 assumption; not independently verified'
            or doc['preserve_earlier_source_and_diagnostics'] is not True
            or any(doc[key] is not False for key in [
                'source_temperature_is_potential_temperature', 'current_association_verified',
                'physical_width_admitted', 'physical_axis_admitted', 'physical_length_admitted',
                'annual_extrema_admitted', 'seasonal_footprint_admitted'])):
        raise ValueError('Changed frozen supplementary declaration')
    return doc


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['declare', 'check'])
    p.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/south-indian-front-levels-2013')
    args = p.parse_args()
    doc = declare(args.directory) if args.action == 'declare' else checked(args.directory)
    print(json.dumps({'status': 'PASS', 'requests': doc['request_count'],
                      'timestamps': doc['daily_timestamps'], 'depths_m': doc['native_depths_m']}))
