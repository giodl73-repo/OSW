"""Complete provider readback including nested virtual-observation groups."""
import argparse
import json
from pathlib import Path

import netCDF4
import numpy as np

import caribbean_ru29_source_fields_v1 as v1

ROOT = v1.ROOT
SOURCE = v1.SOURCE
MIRROR = 'research/caribbean-ru29-source-fields-v2.json'
REPORT = 'research/caribbean-ru29-source-inventory-v2.json'
FIGURE = 'figures/caribbean-ru29-velocity-sections-v2.svg'
PREFLIGHT = 'research/caribbean-ru29-source-fields-preflight-v2.json'
INPUTS = v1.INPUTS + [v1.PREFLIGHT,
    'analysis/caribbean_ru29_source_fields_v2.py',
    'analysis/test_caribbean_ru29_source_fields_v2.py',
    'plans/caribbean-ru29-source-fields-protocol-v2.md',
    'research/caribbean-ru29-v1-nested-group-diagnostic.json',
    SOURCE+'/recursive-schema-inspection.json']


def read_group(group):
    result = {'path': group.path,
              'dimensions': {n: {'length': len(d), 'unlimited': d.isunlimited()}
                             for n,d in group.dimensions.items()},
              'attributes': v1.attributes(group), 'variables': {}, 'groups': {}}
    for name, var in group.variables.items():
        attrs = v1.attributes(var)
        var.set_auto_chartostring(False)
        decoded = var[:]
        mask = np.ma.getmaskarray(decoded)
        var.set_auto_maskandscale(False)
        raw = np.asarray(var[:])
        if mask.shape != raw.shape:
            raise ValueError('Raw/mask shapes differ')
        result['variables'][name] = {
            'dtype': str(var.dtype), 'dimensions': list(var.dimensions),
            'shape': list(raw.shape), 'attributes': attrs,
            'raw_values': v1.scalar(raw.tolist()), 'decoded_mask': v1.scalar(mask.tolist())}
    result['groups'] = {name: read_group(child) for name,child in group.groups.items()}
    return result


def read_member(path):
    with netCDF4.Dataset(path) as ds:
        return read_group(ds)


def summary(group):
    return {'path': group['path'], 'dimensions': group['dimensions'],
            'variables': {name: v1.summarize(v) for name,v in group['variables'].items()},
            'groups': {name: summary(child) for name,child in group['groups'].items()}}


def pins(root):
    manifest = json.loads((root/v1.MANIFEST).read_text(encoding='utf8'))
    paths = INPUTS + [SOURCE+'/'+m['alias'] for m in manifest['members']]
    return {path: v1.sha((root/path).read_bytes()) for path in paths}


def products(root=ROOT):
    preflight = json.loads((root/PREFLIGHT).read_text(encoding='utf8'))
    if pins(root) != preflight['input_sha256']:
        raise ValueError('Frozen source/method pins changed')
    custody = json.loads((root/v1.MANIFEST).read_text(encoding='utf8'))
    for m in custody['members']:
        original = (root/SOURCE/m['alias']).read_bytes()
        if len(original) != m['uncompressed_bytes'] or v1.sha(original) != m['sha256']:
            raise ValueError('Original member checksum/size mismatch')
    members = {m['alias']: read_member(root/SOURCE/m['alias']) for m in custody['members']}
    mirror = {'schema': 'osw.caribbean-ru29.source-fields.v2', 'source_doi': custody['source_doi'],
              'raw_value_encoding': 'original packed values; nonfinite tagged strings; separate decoded mask',
              'members': members}
    mirror_bytes = v1.encoded(mirror)
    report = {'schema': 'osw.caribbean-ru29.source-inventory.v2',
              'source_doi': custody['source_doi'], 'license': custody['license'],
              'whole_archive_checksum_locally_verified': False,
              'input_sha256': preflight['input_sha256'], 'mirror_sha256': v1.sha(mirror_bytes),
              'whole_current_length_measured': False, 'physical_current_width_measured': False,
              'seasonal_envelope_measured': False, 'eddy_pipeline_reproduced': False,
              'members': {name: summary(member) for name,member in members.items()}}
    return {MIRROR: mirror_bytes, REPORT: v1.encoded(report), FIGURE: v1.figure(members)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    outputs = products()
    for path, data in outputs.items():
        target = ROOT/path
        if args.command == 'check':
            if target.read_bytes() != data:
                raise ValueError('Product differs: '+path)
        else:
            if target.exists() and target.read_bytes() != data:
                raise ValueError('Refusing to replace frozen product: '+path)
            target.write_bytes(data)
    print(json.dumps({'status': 'PASS', 'products': {p: v1.sha(b) for p,b in outputs.items()}}))


if __name__ == '__main__':
    main()
