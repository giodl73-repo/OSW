"""Retain genuine supplementary originals and strictly replay raw monthly products."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

from acquire_indian_secc_hycom_2013 import pin
from acquire_eac_100m_source import write_json
from acquire_south_indian_front_levels import ROOT, METADATA, compile_source
from south_indian_front_level_preflight import checked, DECLARATION
from package_indian_secc_hycom_2013 import unpack_checked

DESTINATION = ROOT/'research/source-data/hycom-south-indian-front-levels-2013'
OPERATOR = 'analysis/package_south_indian_front_levels.py'
PRODUCTS = ['quality.json', 'monthly.npz', 'monthly-fields.json']
FIXED = ['metadata.das', 'metadata.dds', 'coordinates.ascii', 'selection.json', 'preflight.json']


def populate(directory, destination):
    directory, destination = Path(directory), Path(destination)
    declaration = checked(directory)
    compile_source(directory)
    plan = json.loads((directory/'selection.json').read_bytes())
    earlier = json.loads((METADATA/'acquisition.json').read_bytes())
    if pin(METADATA/'source-responses.zip') != earlier['files']['source-responses.zip']:
        raise ValueError('Changed original global metadata archive')
    receipts = {}
    with zipfile.ZipFile(METADATA/'source-responses.zip') as archive:
        for name in ['metadata-acquisition.json', 'coordinates-acquisition.json']:
            raw = archive.read(name)
            actual = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            if actual != earlier['archive_members'][name]:
                raise ValueError('Changed original metadata/coordinate receipt')
            receipts[name] = raw
    names = list(FIXED)
    names += [n for r in plan['requests'] for n in [r['file'], Path(r['file']).with_suffix('.receipt.json').name]]
    if (directory/'failures.jsonl').exists(): names.append('failures.jsonl')
    members = {name: (directory/name).read_bytes() for name in names}
    members.update(receipts)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination/'source-responses.zip', 'w') as archive:
        for name, raw in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o600 << 16
            archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    for name in [*FIXED, *PRODUCTS]:
        shutil.copyfile(directory/name, destination/name)
    paths = [*declaration['dependencies'], DECLARATION, OPERATOR,
             'analysis/package_indian_secc_hycom_2013.py']
    manifest = {'schema': 'osw.south-indian-front-level-retained-source.v1',
                'files': {name: pin(destination/name) for name in ['source-responses.zip', *FIXED, *PRODUCTS]},
                'dependencies': {name: pin(ROOT/name) for name in dict.fromkeys(paths)},
                'archive_members': {name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                                    for name, raw in sorted(members.items())},
                'global_metadata_provenance': {'source': METADATA.relative_to(ROOT).as_posix(),
                                               'acquisition_manifest': pin(METADATA/'acquisition.json')},
                'source_model_year': 2013, 'native_depths_m': [100, 200],
                'rights': 'Approved for public release. Distribution unlimited. Original NAVO metadata retained.',
                'model_source_not_observation': True, 'source_temperature_is_potential_temperature': False,
                'current_association_verified': False, 'physical_width_admitted': False,
                'physical_axis_admitted': False, 'physical_length_admitted': False,
                'seasonal_footprint_admitted': False, 'annual_extrema_admitted': False}
    write_json(destination/'acquisition.json', manifest)
    return manifest


def reproduce(destination=DESTINATION):
    destination = Path(destination)
    manifest = json.loads((destination/'acquisition.json').read_bytes())
    if manifest['schema'] != 'osw.south-indian-front-level-retained-source.v1':
        raise ValueError('Wrong supplementary source schema')
    for name, expected in manifest['files'].items():
        if pin(destination/name) != expected: raise ValueError('Changed retained source: '+name)
    for name, expected in manifest['dependencies'].items():
        if pin(ROOT/name) != expected: raise ValueError('Changed source dependency: '+name)
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        working = Path(temporary)
        unpack_checked(destination/'source-responses.zip', manifest['archive_members'], working)
        checked(working)
        compile_source(working)
        for name in PRODUCTS:
            if (working/name).read_bytes() != (destination/name).read_bytes():
                raise ValueError('Original-based source product bytes differ: '+name)
    return {'status': 'PASS', 'network_requests': 0,
            'archive_members_verified': len(manifest['archive_members']),
            'source_responses': sum(n.endswith('.ascii') and n != 'coordinates.ascii'
                                    for n in manifest['archive_members']),
            'products': {name: pin(destination/name) for name in PRODUCTS}}


def package(directory, destination=DESTINATION):
    destination = Path(destination).resolve()
    intended = (ROOT/'research/source-data').resolve()
    if not destination.is_relative_to(intended) or destination == intended:
        raise ValueError('Public source destination must stay inside research/source-data')
    if destination.exists():
        raise ValueError('Existing source requires inspection; do not overwrite publication')
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        staged = Path(temporary)/'source'
        populate(directory, staged)
        result = reproduce(staged)
        # All source and strict original-based product checks pass before publication.
        shutil.copytree(staged, destination)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['package', 'reproduce'])
    p.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/south-indian-front-levels-2013')
    args = p.parse_args()
    result = package(args.directory) if args.action == 'package' else reproduce()
    print(json.dumps(result, indent=2))
