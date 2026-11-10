"""Lossless native source-array inventory; no current edge or width inference."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

ROOT = Path(__file__).resolve().parents[1]
BASE = 'research/source-data/kopte-angola-2017/'
ARCHIVE = BASE + 'eaf-nansen-original.zip'
REPORT = 'research/angola-nansen-native-sections-v1.json'
FIELDS = 'research/angola-nansen-native-fields-v1'
PROTOCOL = 'plans/angola-nansen-native-section-protocol-v1.md'
OPERATOR = 'analysis/angola_nansen_native_sections.py'
TEST = 'analysis/test_angola_nansen_native_sections.py'
PREFLIGHT = 'research/angola-nansen-native-sections-preflight-v1.json'
INPUTS = [ARCHIVE, BASE + 'eaf-nansen-provider-index.tsv', BASE + 'acquisition.json',
          'research/angola-nansen-methods-source-review.json', PROTOCOL, OPERATOR, TEST]
SECTIONS = ['2007403', '2008402', '2008406', '2009403', '2009406', '2010402',
            '2010406', '2011403', '2011408', '2014401', '2014405']
UNITS = {'TIME': 'days since 1990-01-01 00:00:00', 'LAT': 'deg north',
         'LON': 'deg east', 'DEPTH': 'm', 'U_CUR': 'm/s', 'V_CUR': 'm/s'}
TIME_ATTRS = {'units': UNITS['TIME'], 'standard_name': 'time', 'axis': 'T',
              'time_origin': '01-JAN-1990:00'}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('utf8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def compressed(raw):
    target = io.BytesIO()
    with gzip.GzipFile(fileobj=target, mode='wb', filename='', mtime=0, compresslevel=9) as out:
        out.write(raw)
    return target.getvalue()


def array_values(values):
    """Keep every cell and source NaN; never interpret a finite value as missing."""
    array = np.asanyarray(values)
    if array.dtype != np.dtype('float64'):
        raise ValueError('Expected native float64 source array')
    if np.ma.isMaskedArray(array) and np.any(np.ma.getmaskarray(array)):
        raise ValueError('Masked source data require a new explicit mask review')
    array = np.asarray(array)
    if np.isinf(array).any():
        raise ValueError('Infinite source values require review')
    flat = [None if np.isnan(v) else float(v) for v in array.flat]
    result = np.asarray(flat, dtype=object).reshape(array.shape).tolist()
    valid = array[np.isfinite(array)]
    return result, {'cells': int(array.size), 'finite': int(valid.size),
                    'missing': int(np.isnan(array).sum()),
                    'finite_range': [float(valid.min()), float(valid.max())] if valid.size else None}


def section(raw, member):
    with Dataset('provider', memory=raw) as source:
        if source.ncattrs() or set(source.dimensions) != {'PROFILE', 'DEPTH'} or set(source.variables) != set(UNITS):
            raise ValueError('Changed native section schema')
        shapes = {'PROFILE': len(source.dimensions['PROFILE']), 'DEPTH': len(source.dimensions['DEPTH'])}
        if not all(shapes.values()):
            raise ValueError('Empty native section dimension')
        variables = {}
        for name, unit in UNITS.items():
            variable = source.variables[name]
            dimensions = ('PROFILE', 'DEPTH') if name in ('U_CUR', 'V_CUR') else ('DEPTH',) if name == 'DEPTH' else ('PROFILE',)
            attrs = {key: variable.getncattr(key) for key in variable.ncattrs()}
            expected = TIME_ATTRS if name == 'TIME' else {'units': unit}
            if variable.dimensions != dimensions or attrs != expected:
                raise ValueError('Changed native dimensions, units or attributes: ' + name)
            variable.set_auto_maskandscale(False)
            values, summary = array_values(variable[:])
            variables[name] = {'dimensions': list(dimensions), 'attributes': attrs,
                               'values': values, 'summary': summary}
    u = np.asarray(variables['U_CUR']['values'], dtype=float)
    v = np.asarray(variables['V_CUR']['values'], dtype=float)
    return {'schema': 'osw.angola-nansen-native-field.v1', 'source_member': member,
            'source_member_sha256': digest(raw), 'dimensions': shapes, 'variables': variables,
            'component_mask_disagreements': int(np.count_nonzero(np.isnan(u) != np.isnan(v))),
            'time_zone': 'not_explicit_in_source', 'calendar': 'not_explicit_in_source',
            'source_quality_flags_present': False, 'velocity_rotation_applied': False,
            'physical_width_admitted': False}


def reserve():
    if shutil.disk_usage(ROOT).free < 1024 ** 3:
        raise ValueError('Need1GiB free before native section compilation')


def pins():
    return {path: digest((ROOT/path).read_bytes()) for path in INPUTS}


def declare():
    if any((ROOT/path).exists() for path in [PREFLIGHT, REPORT, FIELDS]):
        raise ValueError('Declaration or scientific products already exist; use a new version')
    doc = {'schema': 'osw.angola-nansen-native-preflight.v1', 'input_sha256': pins(),
           'actual_arrays_processed': False, 'exploratory_header_and_methods_review_disclosed': True,
           'physical_width_admitted': False}
    (ROOT/PREFLIGHT).write_bytes(encoded(doc))
    return doc


def calculate():
    declaration = json.loads((ROOT/PREFLIGHT).read_bytes())
    if declaration['input_sha256'] != pins() or declaration['actual_arrays_processed'] is not False:
        raise ValueError('Changed declared native source inputs')
    acquisition = json.loads((ROOT/(BASE+'acquisition.json')).read_bytes())
    original = (ROOT/ARCHIVE).read_bytes()
    if digest(original) != acquisition['sha256'] or len(original) != acquisition['bytes']:
        raise ValueError('Changed original provider archive')
    members, sections, products = [], [], {}
    expected = {f'EAF_Nansen/EAF_Nansen_vmADCP.12S.{code}.nc' for code in SECTIONS}
    expected |= {'EAF_Nansen/', 'EAF_Nansen/EAF_Nansen_CTDs.Angola.11S.1991_2014.nc'}
    with zipfile.ZipFile(io.BytesIO(original)) as archive:
        infos = archive.infolist()
        if len(infos) != len(expected) or {i.filename for i in infos} != expected or any(i.file_size > 50*1024**2 for i in infos):
            raise ValueError('Changed complete source archive inventory')
        for info in infos:
            raw = archive.read(info.filename)
            members.append({'path': info.filename, 'bytes': len(raw), 'sha256': digest(raw),
                            'role': 'directory' if info.is_dir() else 'native_velocity_section' if 'vmADCP' in info.filename else 'hydrography_not_processed'})
        for code in SECTIONS:
            member = f'EAF_Nansen/EAF_Nansen_vmADCP.12S.{code}.nc'
            document = section(archive.read(member), member)
            raw = encoded(document); packed = compressed(raw)
            path = FIELDS + '/' + code + '.json.gz'
            products[path] = packed
            sections.append({'id': 'angola-nansen:'+code, 'source_member': member,
                'source_member_sha256': document['source_member_sha256'], 'field_file': path,
                'field_sha256': digest(packed), 'field_bytes': len(packed),
                'decoded_sha256': digest(raw), 'decoded_bytes': len(raw),
                'dimensions': document['dimensions'], 'variable_summaries': {k:v['summary'] for k,v in document['variables'].items()},
                'component_mask_disagreements': document['component_mask_disagreements'],
                'physical_width_admitted': False})
    report = {'schema': 'osw.angola-nansen-native-sections.v1',
        'proposed_current_id': 'angola', 'canonical_current_identity_admitted': False,
        'status': 'complete_native_source_sections_not_current_widths',
        'source_doi': 'https://doi.org/10.1594/PANGAEA.868683', 'source_license': 'CC-BY-3.0',
        'credit': acquisition['credit'], 'input_sha256': {**pins(), PREFLIGHT: digest((ROOT/PREFLIGHT).read_bytes())},
        'members': members, 'sections': sections, 'section_count': len(sections),
        'profile_count': sum(s['dimensions']['PROFILE'] for s in sections),
        'velocity_cells_per_component': sum(s['dimensions']['PROFILE']*s['dimensions']['DEPTH'] for s in sections),
        'nominal_section_latitude_degrees_north': -12,
        'time_zone': 'not_explicit_in_source', 'source_quality_flags_present': False,
        'methods_review': 'research/angola-nansen-methods-source-review.json',
        'physical_width_admitted': False, 'whole_current_length_km': None,
        'annual_width_range_km': None, 'current_edge_geometry': None,
        'limitation': 'Native unrotated U_CUR/V_CUR samples on unequal depth grids and uneven dates. Profile index is not cross-shore distance. Finite values are not independently quality approved. No interpolation, model filling, physical edges, annual range or canonical identity admission.'}
    return report, products


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['declare', 'build', 'check'])
    args = parser.parse_args()
    if args.command == 'declare':
        declare(); print('Declared inputs before source-array compilation'); return
    reserve()
    if args.command == 'build' and ((ROOT/REPORT).exists() or (ROOT/FIELDS).exists()):
        raise ValueError('Products already exist; retain them and use a new version')
    report, products = calculate()
    if args.command == 'check':
        if (ROOT/REPORT).read_bytes() != encoded(report) or any((ROOT/path).read_bytes() != raw for path,raw in products.items()):
            raise ValueError('Native source products differ')
        print('PASS: complete report and every native field byte exact'); return
    (ROOT/FIELDS).mkdir()
    for path, raw in products.items(): (ROOT/path).write_bytes(raw)
    (ROOT/REPORT).write_bytes(encoded(report))
    print(json.dumps({key:report[key] for key in ['section_count','profile_count','velocity_cells_per_component']}))


if __name__ == '__main__':
    main()
