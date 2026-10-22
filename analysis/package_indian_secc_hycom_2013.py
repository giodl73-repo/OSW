"""Retain bounded original responses and reproduce the source without network."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

from acquire_eac_100m_source import write_json
from acquire_indian_secc_hycom_2013 import compile_source, pin, validate_plan

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT/'research/source-data/hycom-indian-secc-2013'


def package(directory, destination=DESTINATION):
    directory, destination = Path(directory), Path(destination)
    plan = validate_plan(directory)
    compile_source(directory)
    names = ['metadata.das', 'metadata.dds', 'metadata-acquisition.json', 'coordinates.ascii',
             'coordinates-acquisition.json', 'selection.json']
    names += [n for r in plan['requests'] for n in [r['file'], Path(r['file']).with_suffix('.receipt.json').name]]
    names += [n for n in ['selection-before-six-day-chunks.json', 'source-protocol-before-six-day-chunks.md',
                         'failures.jsonl'] if (directory/n).exists()]
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination/'source-responses.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in sorted(names):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o600 << 16
            archive.writestr(info, (directory/name).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    products = ['selection.json', 'quality.json', 'monthly.npz', 'monthly-fields.json', 'metadata.das', 'metadata.dds', 'coordinates.ascii']
    for name in products:
        shutil.copyfile(directory/name, destination/name)
    paths = ['analysis/acquire_indian_secc_hycom_2013.py', 'analysis/package_indian_secc_hycom_2013.py',
             'analysis/acquire_south_australian_hycom_2d.py',
             'analysis/acquire_eac_100m_source.py', 'plans/indian-secc-hycom-2013-source-protocol-v1.md',
             'research/indian-secc-hycom-2013-source-preflight.json']
    manifest = {'schema': 'osw.indian-secc-hycom-retained-source.v1',
                'files': {n: pin(destination/n) for n in ['source-responses.zip', *products]},
                'dependencies': {p: pin(ROOT/p) for p in paths},
                'archive_members': {n: pin(directory/n) for n in sorted(names)},
                'rights': 'Approved for public release. Distribution unlimited. Original NAVO metadata retained.',
                'model_source_not_observation': True, 'physical_width_admission': False}
    write_json(destination/'acquisition.json', manifest)
    return manifest


def unpack_checked(archive_path, members, target):
    """Only explicitly pinned, flat, bounded original files may be unpacked."""
    with zipfile.ZipFile(archive_path) as archive:
        info = archive.infolist()
        if len(info) != len(members) or len({i.filename for i in info}) != len(info) or {i.filename for i in info} != set(members):
            raise ValueError('Source archive member set differs')
        for item in info:
            expected = members[item.filename]
            if (Path(item.filename).name != item.filename or '/' in item.filename or '\\' in item.filename
                    or item.file_size != expected['bytes'] or item.file_size > 20_000_000):
                raise ValueError('Unsafe or oversized source member')
            raw = archive.read(item)
            if hashlib.sha256(raw).hexdigest() != expected['sha256']:
                raise ValueError('Source archive member checksum differs')
            (Path(target)/item.filename).write_bytes(raw)


def reproduce(destination=DESTINATION):
    destination = Path(destination)
    manifest = json.loads((destination/'acquisition.json').read_bytes())
    for name, expected in manifest['files'].items():
        if pin(destination/name) != expected:
            raise ValueError('Changed retained product: '+name)
    for name, expected in manifest['dependencies'].items():
        if pin(ROOT/name) != expected:
            raise ValueError('Changed source operator or dependency: '+name)
    with tempfile.TemporaryDirectory(prefix='osw-secc-hycom-') as work:
        unpack_checked(destination/'source-responses.zip', manifest['archive_members'], work)
        compile_source(work)
        for name in ['quality.json', 'monthly.npz', 'monthly-fields.json']:
            if pin(Path(work)/name) != manifest['files'][name]:
                raise ValueError('Reconstructed product bytes differ: '+name)
    return {'status': 'PASS', 'archive_members_verified': len(manifest['archive_members']),
            'velocity_responses': len(json.loads((destination/'selection.json').read_bytes())['requests']),
            'products': ['quality.json', 'monthly.npz', 'monthly-fields.json'], 'network_requests': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['package', 'reproduce'])
    parser.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/indian-secc-hycom-2013')
    parser.add_argument('--destination', type=Path, default=DESTINATION)
    args = parser.parse_args()
    result = package(args.directory, args.destination) if args.action == 'package' else reproduce(args.destination)
    print(json.dumps(result if args.action == 'reproduce' else result['files'], indent=2))
