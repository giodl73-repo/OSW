"""Exact synthetic thermodynamic conformance; never actual model measurements."""
import argparse
import json
from pathlib import Path
import tempfile

import numpy as np

from acquire_indian_secc_hycom_2013 import coordinates, pin, write_stored_npz
from acquire_south_indian_front_levels import ROOT, METADATA
from south_indian_front_temperature import daily, monthly

REFERENCE = ROOT/'research/source-data/south-indian-front-temperature-conformance'


def probe():
    c = coordinates((METADATA/'coordinates.ascii').read_text(encoding='utf8'))
    lat = c['lat'][800:1126]
    lon = c['lon'][3249:3252]
    shape = (5, 2, len(lat), len(lon))
    i = np.arange(np.prod(shape), dtype=np.int64).reshape(shape)
    fields = {'water_u': ((i*7) % 1800-900).astype('<i2'),
              'water_v': ((i*11) % 2400-1200).astype('<i2'),
              'water_temp': ((i*17) % 24000-19000).astype('<i2'),
              'salinity': ((i*29) % 4000+14000).astype('<i2')}
    fields['water_u'][0, 0, ::41, 0] = -30000
    fields['salinity'][1, 1, ::37, 2] = -30000
    fields['water_v'][:2, 0, 0, 0] = -30000
    fields['water_temp'][:, 1, 1, 1] = -30000
    result = daily(fields, [100, 200], lat, lon, float(np.float32(.001)),
                   {'water_temp': 20., 'salinity': 20.})
    counts, mean = monthly(result, 4)
    mask = result['common_mask']
    # Missing-value payloads use the writer's explicit NumPy NaN sentinel.
    # Every finite numeric bit remains subject to exact comparison.
    return {'sea_pressure_dbar': np.asarray(result['sea_pressure_dbar'], dtype='<f8'),
            'absolute_salinity_g_kg': np.asarray(np.where(mask, result['absolute_salinity_g_kg'], np.nan), dtype='<f8'),
            'potential_temperature_0_dbar_assuming_ITS90_c': np.asarray(np.where(mask,
                result['potential_temperature_0_dbar_assuming_ITS90_c'], np.nan), dtype='<f8'),
            'common_mask': mask.astype('u1'), 'common_samples': counts,
            'monthly_potential_temperature_0_dbar_assuming_ITS90_c': mean}


def metadata():
    return {'schema': 'osw.south-indian-front-temperature-conformance.v1',
            'role': 'synthetic numerical probe; not source observations, model output or admitted measurements',
            'gsw_version': '3.6.23', 'synthetic_daily_shape': [5, 2, 326, 3],
            'minimum_synthetic_common_samples': 4,
            'missing_nan_payload': 'explicit numpy.nan sentinel; finite numeric bits never rounded',
            'dependencies': {p: pin(ROOT/p) for p in [
                'analysis/check_south_indian_front_temperature_portability.py',
                'analysis/south_indian_front_temperature.py',
                'analysis/acquire_indian_secc_hycom_2013.py',
                'plans/indian-secc-hycom-array-serialization-protocol-v1.md',
                'research/source-data/hycom-south-indian-hydrography-2013/coordinates.ascii']},
            'current_association_verified': False, 'physical_width_admitted': False}


def initialize():
    if REFERENCE.exists(): raise ValueError('Do not replace the conformance reference')
    REFERENCE.mkdir(parents=True)
    write_stored_npz(REFERENCE/'synthetic.npz', probe())
    doc = {**metadata(), 'reference': pin(REFERENCE/'synthetic.npz')}
    (REFERENCE/'reference.json').write_bytes((json.dumps(doc, indent=2)+'\n').encode())


def check():
    doc = json.loads((REFERENCE/'reference.json').read_bytes())
    if {k: v for k, v in doc.items() if k != 'reference'} != metadata():
        raise ValueError('Changed synthetic method or dependencies')
    if pin(REFERENCE/'synthetic.npz') != doc['reference']:
        raise ValueError('Changed exact conformance reference')
    current = probe()
    (ROOT/'.pytest_cache').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        rebuilt = Path(temporary)/'synthetic.npz'
        write_stored_npz(rebuilt, current)
        exact = rebuilt.read_bytes() == (REFERENCE/'synthetic.npz').read_bytes()
    diagnostics = {}
    with np.load(REFERENCE/'synthetic.npz', allow_pickle=False) as expected:
        for name, actual in current.items():
            old = expected[name]
            finite = np.isfinite(actual) & np.isfinite(old)
            diagnostics[name] = {'bytes_exact': actual.tobytes() == old.tobytes(),
                                 'changed_finite_values': int(np.count_nonzero(actual[finite] != old[finite])),
                                 'maximum_absolute_difference': float(np.max(np.abs(actual[finite]-old[finite])))
                                     if finite.any() else 0,
                                 'finite_masks_exact': bool(np.array_equal(np.isfinite(actual), np.isfinite(old)))}
    result = {'status': 'PASS' if exact else 'FAIL', 'whole_stored_npz_exact': exact,
              'arrays': diagnostics, 'source_field_values_used': False, 'physical_width_admitted': False}
    print(json.dumps(result, indent=2))
    if not exact: raise SystemExit(1)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--initialize', action='store_true')
    args = p.parse_args()
    if args.initialize: initialize()
    check()
