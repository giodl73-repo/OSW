"""Small lazy page payload: unchanged occupation records from frozen readback."""
import argparse
import json

import caribbean_ru29_source_fields_v2 as method

OUTPUT = 'research/caribbean-ru29-source-page-v1.json'


def build():
    outputs = method.products()
    for path, rebuilt in outputs.items():
        if (method.ROOT/path).read_bytes() != rebuilt:
            raise ValueError('Frozen source product changed: '+path)
    mirror = json.loads(outputs[method.MIRROR])
    facts = json.loads((method.ROOT/method.SOURCE/'source-facts.json').read_bytes())
    return {'schema': 'osw.caribbean-ru29.source-page.v1',
            'source_mirror': method.MIRROR, 'source_sha256': method.v1.sha(outputs[method.MIRROR]),
            'scope': 'Complete provider interpolated occupations; not simultaneous snapshots or full current widths.',
            'velocity_units': 'm/s', 'depth_units': 'm',
            'units_locator': facts['velocity_units_locator'],
            'occupations': [{'source_member': f'adcp-transect-{n+1}.nc',
                             'declared_utc_window': facts['occupation_windows_utc'][n],
                             'source_group': mirror['members'][f'adcp-transect-{n+1}.nc']}
                            for n in range(2)]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    raw = method.v1.encoded(build())
    target = method.ROOT/OUTPUT
    if args.command == 'check':
        if target.read_bytes() != raw:
            raise ValueError('Changed source page payload')
    else:
        target.write_bytes(raw)
    print(json.dumps({'status': 'PASS', 'file': OUTPUT, 'bytes': len(raw), 'sha256': method.v1.sha(raw)}))


if __name__ == '__main__':
    main()
