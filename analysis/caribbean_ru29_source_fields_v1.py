"""Frozen complete provider readback; no physical current dimension inference."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path

import netCDF4
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/source-data/caribbean-ru29-2024-v1'
MANIFEST = SOURCE + '/custody.json'
MIRROR = 'research/caribbean-ru29-source-fields-v1.json'
REPORT = 'research/caribbean-ru29-source-inventory-v1.json'
FIGURE = 'figures/caribbean-ru29-velocity-sections-v1.svg'
PREFLIGHT = 'research/caribbean-ru29-source-fields-preflight-v1.json'
INPUTS = ['analysis/caribbean_ru29_source_fields_v1.py',
          'analysis/test_caribbean_ru29_source_fields_v1.py',
          'plans/caribbean-ru29-source-fields-protocol-v1.md', MANIFEST,
          SOURCE + '/schema-inspection.json', SOURCE + '/source-facts.json',
          SOURCE + '/payload-range-receipts.json', SOURCE + '/header-range-receipts.json',
          SOURCE + '/README.md']


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('utf8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scalar(value):
    if isinstance(value, bytes):
        return {'bytes_hex': value.hex()}
    if isinstance(value, (np.ndarray, list, tuple)):
        return [scalar(x) for x in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return 'NaN' if math.isnan(value) else ('Infinity' if value > 0 else '-Infinity')
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(type(value).__name__)


def attributes(obj):
    return {key: {'dtype': str(np.asarray(obj.getncattr(key)).dtype),
                  'value': scalar(obj.getncattr(key))}
            for key in obj.ncattrs()}


def read_member(path):
    with netCDF4.Dataset(path) as ds:
        result = {'dimensions': {name: {'length': len(dim), 'unlimited': dim.isunlimited()}
                                 for name, dim in ds.dimensions.items()},
                  'attributes': attributes(ds), 'variables': {}}
        if ds.groups:
            raise ValueError('Nested groups require a new readback version')
        for name, var in ds.variables.items():
            attrs = attributes(var)
            var.set_auto_chartostring(False)
            decoded = var[:]
            mask = np.ma.getmaskarray(decoded)
            var.set_auto_maskandscale(False)
            var.set_auto_chartostring(False)
            raw = np.asarray(var[:])
            result['variables'][name] = {
                'dtype': str(var.dtype), 'dimensions': list(var.dimensions),
                'shape': list(raw.shape), 'attributes': attrs,
                'raw_values': scalar(raw.tolist()),
                'decoded_mask': scalar(mask.tolist())}
        return result


def summarize(variable):
    raw = np.asarray(variable['raw_values'], dtype=object).reshape(-1)
    numeric = [x for x in raw if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return {'value_count': len(raw),
            'decoded_masked_count': int(np.asarray(variable['decoded_mask'], dtype=bool).sum()),
            'raw_numeric_count': len(numeric),
            'raw_minimum': min(numeric) if numeric else None,
            'raw_maximum': max(numeric) if numeric else None,
            'range_semantics': 'packed raw values, not decoded physical quantities'}


def edges(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all() or not (np.diff(values) > 0).all():
        raise ValueError('Display coordinates must be finite and strictly increasing')
    mid = (values[:-1] + values[1:]) / 2
    return np.r_[values[0] - (values[1]-values[0])/2, mid,
                 values[-1] + (values[-1]-values[-2])/2]


def color(value):
    if not math.isfinite(value):
        return '#d1d5db'
    t = min(abs(value) / 0.5, 1)
    end = (37, 99, 160) if value < 0 else (192, 57, 43)
    return '#%02x%02x%02x' % tuple(round(248 + t*(c-248)) for c in end)


def figure(members):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="850" viewBox="0 0 1100 850" role="img" aria-labelledby="title desc">',
           '<title id="title">Caribbean Current: two 2024 RU29 velocity sections</title>',
           '<desc id="desc">Provider interpolated multiweek sections near 69 degrees west. Both horizontal components, identical colour scales; grey means missing. These sections do not measure full current width.</desc>',
           '<rect width="1100" height="850" fill="white"/>',
           '<g font-family="Arial,sans-serif" fill="#172b3a"><text x="50" y="30" font-size="22">Caribbean Current · RU29 observed section products</text>',
           '<text x="50" y="55" font-size="13">Provider interpolation near 69°W · m/s · blue west/south, red east/north · grey missing</text>']
    clipped = []
    for col in range(2):
        variables = members[f'adcp-transect-{col+1}.nc']['variables']
        lat = edges(variables['latitude']['raw_values'])
        depth = edges(variables['depth']['raw_values'])
        for row, component in enumerate(['u_grid', 'v_grid']):
            data = np.asarray(variables[component]['raw_values'], dtype=float)
            mask = np.asarray(variables[component]['decoded_mask'], dtype=bool)
            if data.shape != (len(depth)-1, len(lat)-1) or mask.shape != data.shape:
                raise ValueError('Display array shape mismatch')
            data = np.where(mask, np.nan, data)
            clipped.append(int((np.isfinite(data) & (np.abs(data) > 0.5)).sum()))
            x0, y0, w, h = 70+col*535, 115+row*305, 440, 240
            title = f'Occupation {col+1} · {"E–W" if row == 0 else "N–S"}'
            svg.append(f'<text x="{x0}" y="{y0-14}" font-size="16">{title}</text>')
            for z in range(data.shape[0]):
                for a in range(data.shape[1]):
                    x = x0+w*(lat[a]-lat[0])/(lat[-1]-lat[0])
                    y = y0+h*(depth[z]-depth[0])/(depth[-1]-depth[0])
                    cw = w*(lat[a+1]-lat[a])/(lat[-1]-lat[0])
                    ch = h*(depth[z+1]-depth[z])/(depth[-1]-depth[0])
                    svg.append(f'<rect x="{x:.4f}" y="{y:.4f}" width="{cw:.4f}" height="{ch:.4f}" fill="{color(float(data[z,a]))}"/>')
            for a in [0, len(lat)//2, len(lat)-1]:
                x = x0+w*(lat[a]-lat[0])/(lat[-1]-lat[0])
                svg.append(f'<text x="{x:.2f}" y="{y0+h+18}" text-anchor="middle" font-size="11">{lat[a]:.2f}°N</text>')
            for z in [0, len(depth)//2, len(depth)-1]:
                y = y0+h*(depth[z]-depth[0])/(depth[-1]-depth[0])
                svg.append(f'<text x="{x0-7}" y="{y:.2f}" text-anchor="end" font-size="11">{depth[z]:.0f}m</text>')
    for i in range(200):
        svg.append(f'<rect x="{350+i*2}" y="715" width="2" height="14" fill="{color(-.5+i/199)}"/>')
    svg.extend(['<text x="350" y="747" font-size="12">−0.5</text><text x="550" y="747" font-size="12">0</text><text x="720" y="747" font-size="12">+0.5 m/s</text>',
                '<text x="50" y="775" font-size="12">1: 27 Apr–18 May 2024 · 2: 18 May–6 Jun 2024 · occupations are not simultaneous snapshots</text>',
                '<text x="50" y="797" font-size="12">Finite cells beyond ±0.5 m/s (u1, v1, u2, v2): '+html.escape(str(clipped))+'</text>',
                '<text x="50" y="820" font-size="12">Gradone et al. 2026 / Zenodo 18332586 · CC BY 4.0 · full width, depth and seasonal coverage incomplete</text></g></svg>'])
    return ('\n'.join(svg)+'\n').encode('utf8')


def pins(root):
    manifest = json.loads((root/MANIFEST).read_text(encoding='utf8'))
    paths = INPUTS + [SOURCE+'/'+m['alias'] for m in manifest['members']]
    return {path: sha((root/path).read_bytes()) for path in paths}


def products(root=ROOT):
    preflight = json.loads((root/PREFLIGHT).read_text(encoding='utf8'))
    if pins(root) != preflight['input_sha256']:
        raise ValueError('Frozen source/method pins changed')
    custody = json.loads((root/MANIFEST).read_text(encoding='utf8'))
    for m in custody['members']:
        original = (root/SOURCE/m['alias']).read_bytes()
        if len(original) != m['uncompressed_bytes'] or sha(original) != m['sha256']:
            raise ValueError('Original member checksum/size mismatch')
    members = {m['alias']: read_member(root/SOURCE/m['alias']) for m in custody['members']}
    mirror = {'schema': 'osw.caribbean-ru29.source-fields.v1', 'source_doi': custody['source_doi'],
              'raw_value_encoding': 'original packed values; nonfinite tagged strings; separate decoded mask',
              'members': members}
    mirror_bytes = encoded(mirror)
    report = {'schema': 'osw.caribbean-ru29.source-inventory.v1',
              'source_doi': custody['source_doi'], 'license': custody['license'],
              'whole_archive_checksum_locally_verified': False,
              'input_sha256': preflight['input_sha256'], 'mirror_sha256': sha(mirror_bytes),
              'whole_current_length_measured': False, 'physical_current_width_measured': False,
              'seasonal_envelope_measured': False, 'eddy_pipeline_reproduced': False,
              'members': {name: {'dimensions': member['dimensions'],
                                  'variables': {key: summarize(v) for key,v in member['variables'].items()}}
                          for name,member in members.items()}}
    return {MIRROR: mirror_bytes, REPORT: encoded(report), FIGURE: figure(members)}


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
    print(json.dumps({'status': 'PASS', 'products': {p: sha(b) for p,b in outputs.items()}}))


if __name__ == '__main__':
    main()
