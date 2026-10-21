"""Monthly surrounding source fields; no current axis or width inferred."""
import calendar
import json

import numpy as np

from acquire_west_australian_oscar_2d import ROOT, DIRECTORY, PROTOCOL, OPERATOR, baseline, digest, load
from build_west_australian_oscar_spans import profiles as old_monthly_profiles

REPORT = 'research/west-australian-oscar-2d-monthly-source-fields.json'
BUILDER = 'analysis/build_west_australian_oscar_2d_source.py'


def encoded(document):
    return (json.dumps(document, separators=(',', ':'), allow_nan=False)+'\n').encode()


def monthly(arrays):
    frames = []
    for month in range(1, 13):
        indices = [i for i, stamp in enumerate(arrays['times']) if int(stamp[5:7]) == month]
        count = np.zeros((25, 169), dtype=np.int64)
        # Python float sum matches the existing section's compensated summation.
        # A vectorized running NumPy sum would change some readbacks by one ULP.
        for i in indices:
            paired = np.isfinite(arrays['u'][i]) & np.isfinite(arrays['v'][i])
            count += paired
        eligible = count >= 5
        u = np.full((25, 169), np.nan); v = np.full_like(u, np.nan)
        for yi, xi in zip(*np.where(eligible)):
            selected = [i for i in indices if np.isfinite(arrays['u'][i, yi, xi]) and np.isfinite(arrays['v'][i, yi, xi])]
            u[yi, xi] = sum(float(arrays['u'][i, yi, xi]) for i in selected)/len(selected)
            v[yi, xi] = sum(float(arrays['v'][i, yi, xi]) for i in selected)/len(selected)
        def nullable(values):
            return [[None if not np.isfinite(value) else float(value) for value in row] for row in values]
        frames.append({'month': month, 'source_time_indices': indices,
                       'source_times': [arrays['times'][i] for i in indices],
                       'available_source_times': len(indices), 'paired_samples': count.tolist(),
                       'eastward_m_s': nullable(u), 'northward_m_s': nullable(v),
                       'eligible_mean_cells': int(eligible.sum()),
                       'outside_fixed_color_scale_cells': int(((v < -.2) | (v > .2)).sum())})
    return frames


def build():
    receipt = json.loads((DIRECTORY/'acquisition.json').read_bytes())
    for path, expected in receipt['input_sha256'].items():
        if digest((ROOT/path).read_bytes()) != expected:
            raise ValueError('Changed acquisition contract: '+path)
    arrays, quality = load()
    if quality != receipt['quality']:
        raise ValueError('Changed recorded source quality')
    frames = monthly(arrays)
    config = json.loads((ROOT/'research/west-australian-oscar-section-input.json').read_bytes())
    original_months = old_monthly_profiles(baseline(), config)
    for frame, old in zip(frames, original_months):
        for key in ['eastward_m_s', 'northward_m_s']:
            actual = np.array([np.nan if v is None else v for v in frame[key][12]], dtype='<f8')
            expected = np.array([np.nan if r[key] is None else r[key] for r in old['profile']], dtype='<f8')
            if not np.array_equal(np.isnan(actual), np.isnan(expected)):
                raise ValueError('Changed old monthly mask')
            finite = np.isfinite(expected)
            if not np.array_equal(actual[finite].view('<u8'), expected[finite].view('<u8')):
                raise ValueError('Changed old monthly finite float64 bits')
        if frame['paired_samples'][12] != [r['paired_source_samples'] for r in old['profile']]:
            raise ValueError('Changed old monthly paired support')
    paths = [PROTOCOL, OPERATOR, BUILDER, 'research/west-australian-current-naming-seasonal-scope-audit.json',
             'research/west-australian-32s-2013-monthly-component-spans.json',
             (DIRECTORY/'source-responses.zip').relative_to(ROOT).as_posix(),
             (DIRECTORY/'acquisition.json').relative_to(ROOT).as_posix()]
    return {'schema': 'osw.west-australian-oscar-2d-monthly-source.v1',
            'status': 'surrounding_source_context_not_current_geometry',
            'current_id': 'west-australian', 'entity_id': 'current:west-australian',
            'dataset_id': receipt['dataset_id'], 'product_version': receipt['product_version'],
            'input_sha256': {path: digest((ROOT/path).read_bytes()) for path in paths},
            'source_license': receipt['source_license'], 'attribution': receipt['attribution'],
            'source_first_time': arrays['times'][0], 'source_last_time': arrays['times'][-1],
            'nominal_depth_m': 15, 'layer_interpretation': 'Satellite-derived upper-ocean product; nominal coordinate is not an observed depth-resolved layer.',
            'longitude_degrees_east': arrays['longitude'].tolist(),
            'latitude_degrees_north': arrays['latitude'].tolist(), 'quality': quality,
            'monthly_mean_rule': 'Chronological paired-vector sums; at least five paired records per calendar month/cell.',
            'comparison_section_latitude': -32, 'old_monthly_finite_bits_masks_and_counts_exact': True,
            'months': frames, 'current_association_verified': False,
            'whole_current_length_km': None, 'whole_current_width_km': None,
            'annual_physical_length_range_km': None, 'annual_physical_width_range_km': None,
            'rank_eligible': False, 'seasonal_current_footprint_admitted': False,
            'comparison_figure': 'figures/west-australian-oscar-2d-source.svg',
            'limitations': ['Regional source viewport is not a current boundary or complete named-current extent.',
                            'Surface component fields do not establish a connected velocity axis or depth-resolved flow.',
                            'A monthly mean velocity field is not a mean instantaneous current width.',
                            'Five/six-day mapped source records are not independent point observations.',
                            'Coastal Leeuwin, subsurface undercurrents and historical naming conventions remain distinct.']}


def verify():
    document = json.loads((ROOT/REPORT).read_bytes())
    if document != build(): raise ValueError('Changed two-dimensional source report')
    manifest_path = 'research/west-australian-oscar-2d-source-figure.json'
    manifest = json.loads((ROOT/manifest_path).read_bytes())
    if manifest['source_file'] != REPORT or manifest['source_sha256'] != digest((ROOT/REPORT).read_bytes()) or manifest['current_geometry_admitted'] is not False:
        raise ValueError('Changed two-dimensional source figure binding/admission')
    pins = {**document['input_sha256'], REPORT: digest((ROOT/REPORT).read_bytes()),
            manifest_path: digest((ROOT/manifest_path).read_bytes()), manifest['generator_file']: manifest['generator_sha256']}
    for asset in manifest['figures'].values(): pins[asset['file']] = asset['sha256']
    for path, expected in pins.items():
        if digest((ROOT/path).read_bytes()) != expected: raise ValueError('Changed source context dependency: '+path)
    return document, pins


if __name__ == '__main__':
    document = build()
    (ROOT/REPORT).write_bytes(encoded(document))
    print(json.dumps({'source': document['quality'], 'monthly_eligible_cells': [r['eligible_mean_cells'] for r in document['months']],
                      'old_monthly_finite_bits_masks_and_counts_exact': True}))
