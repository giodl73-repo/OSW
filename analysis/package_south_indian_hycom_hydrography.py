"""Retain the four-field source and reconstruct all monthly products offline."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
import hashlib

from acquire_eac_100m_source import write_json
from acquire_indian_secc_hycom_2013 import pin
from acquire_south_indian_hycom_hydrography import compile_source, validate_plan, METADATA, ROOT
from package_indian_secc_hycom_2013 import unpack_checked

DESTINATION = ROOT/'research/source-data/hycom-south-indian-hydrography-2013'


def package(directory, destination=DESTINATION):
    directory, destination = Path(directory), Path(destination)
    plan = validate_plan(directory)
    compile_source(directory)
    # These global coordinate/metadata originals were acquired for the previous
    # section; retain their actual receipts, without assigning a new acquisition.
    original_manifest = json.loads((METADATA/'acquisition.json').read_bytes())
    if pin(METADATA/'source-responses.zip') != original_manifest['files']['source-responses.zip']:
        raise ValueError('Changed original metadata archive')
    with zipfile.ZipFile(METADATA/'source-responses.zip') as archive:
        for name in ['metadata-acquisition.json', 'coordinates-acquisition.json']:
            raw = archive.read(name)
            if {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()} != original_manifest['archive_members'][name]:
                raise ValueError('Changed original metadata receipt')
            (directory/name).write_bytes(raw)
    names = ['metadata.das', 'metadata.dds', 'metadata-acquisition.json',
             'coordinates.ascii', 'coordinates-acquisition.json', 'selection.json']
    names += [name for r in plan['requests'] for name in [r['file'], Path(r['file']).with_suffix('.receipt.json').name]]
    operational_dependencies={}
    operational_path=ROOT/'research/south-indian-hycom-longer-timeout-resume.json'
    if operational_path.exists():
        from resume_south_indian_hycom_transport import checked_declaration
        _,operational=checked_declaration(directory,operational_path)
        shutil.copyfile(operational_path,directory/'operational-resume.json')
        names.append('operational-resume.json')
        operational_dependencies={**operational['dependencies'],
                                  operational_path.relative_to(ROOT).as_posix():pin(operational_path)}
    if (directory/'failures.jsonl').exists():
        names.append('failures.jsonl')
    destination.mkdir(parents=True, exist_ok=True)
    # Archive compression is merely storage of original response bytes. The
    # reconstructed NPZ uses the separately frozen portable ZIP_STORED writer.
    with zipfile.ZipFile(destination/'source-responses.zip', 'w') as archive:
        for name in sorted(names):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o600 << 16
            archive.writestr(info, (directory/name).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    products = ['selection.json', 'quality.json', 'monthly.npz', 'monthly-fields.json',
                'metadata.das', 'metadata.dds', 'coordinates.ascii']
    for name in products:
        shutil.copyfile(directory/name, destination/name)
    dependencies = [*plan['operators'], *plan['rules'],
                    'analysis/package_south_indian_hycom_hydrography.py',
                    'analysis/package_indian_secc_hycom_2013.py',
                    'research/south-indian-hycom-hydrography-source-preflight.json']
    dependencies=list(dict.fromkeys([*dependencies,*operational_dependencies]))
    manifest = {
        'schema': 'osw.south-indian-hycom-hydrography-retained-source.v1',
        'files': {name: pin(destination/name) for name in ['source-responses.zip', *products]},
        'dependencies': {name: pin(ROOT/name) for name in dependencies},
        'archive_members': {name: pin(directory/name) for name in sorted(names)},
        'global_metadata_provenance': {'source': METADATA.relative_to(ROOT).as_posix(),
                                       'acquisition_manifest': pin(METADATA/'acquisition.json')},
        'rights': 'Approved for public release. Distribution unlimited. Original NAVO metadata retained.',
        'model_source_not_observation': True,
        'current_association_verified': False, 'physical_width_admission': False,
        'physical_axis_admission': False, 'seasonal_footprint_admission': False,
    }
    write_json(destination/'acquisition.json', manifest)
    return manifest


def reproduce(destination=DESTINATION):
    destination = Path(destination)
    manifest = json.loads((destination/'acquisition.json').read_bytes())
    for group, base in [('files', destination), ('dependencies', ROOT)]:
        for name, expected in manifest[group].items():
            if pin(base/name) != expected:
                raise ValueError('Changed retained product/operator: '+name)
    with tempfile.TemporaryDirectory(prefix='osw-south-indian-hydrography-') as work:
        unpack_checked(destination/'source-responses.zip', manifest['archive_members'], work)
        compile_source(work)
        for name in ['quality.json', 'monthly.npz', 'monthly-fields.json']:
            if pin(Path(work)/name) != manifest['files'][name]:
                raise ValueError('Reconstructed product bytes differ: '+name)
    return {'status': 'PASS', 'network_requests': 0,
            'archive_members_verified': len(manifest['archive_members']),
            'four_field_responses': len(json.loads((destination/'selection.json').read_bytes())['requests']),
            'products': ['quality.json', 'monthly.npz', 'monthly-fields.json']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['package', 'reproduce'])
    parser.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/south-indian-hycom-2013')
    parser.add_argument('--destination', type=Path, default=DESTINATION)
    args = parser.parse_args()
    result = package(args.directory, args.destination) if args.action == 'package' else reproduce(args.destination)
    print(json.dumps(result if args.action == 'reproduce' else result['files'], indent=2))
