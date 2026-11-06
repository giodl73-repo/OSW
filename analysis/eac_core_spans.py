"""Compact frozen scene contract for the independently queryable EAC spans."""
import argparse
import json
from acquire_eac_100m_source import ROOT, sha
from build_eac_section_core_spans import REPORT, OPERATOR, PROTOCOL, verify

FILE = 'research/eac-csiro-100m-section-core-spans-summary.json'
FIGURE = 'research/eac-csiro-100m-section-core-spans-figure.json'
HELPER = 'analysis/eac_core_spans.py'
ID = 'diagnostic:eac-csiro100m-section-core-spans'


def build():
    report = verify(); figure = json.loads((ROOT/FIGURE).read_bytes())
    if figure['source_sha256'] != sha(ROOT/REPORT) or figure['physical_width_admitted'] is not False:
        raise ValueError('Changed EAC core figure source/scope')
    pins = {**report['input_sha256'], REPORT: sha(ROOT/REPORT), HELPER: sha(ROOT/HELPER),
            FIGURE: sha(ROOT/FIGURE), figure['generator_file']: figure['generator_sha256'],
            report['source_file']: report['source_sha256']}
    for asset in figure['figures'].values(): pins[asset['file']] = asset['sha256']
    for path, pin in pins.items():
        if sha(ROOT/path) != pin: raise ValueError('Changed EAC core dependency: '+path)
    bounds = [v+sign*a for row in report['profiles'] for v, a in zip(row['section_normal_velocity_m_s'], row['projected_supplied_magnitudes_m_s'])
              if v is not None and a is not None for sign in [-1, 1]]
    low, high = min(bounds), max(bounds); pad = (high-low)*.05
    return {'schema': 'osw.eac-section-core-summary.v1', 'status': report['status'],
            'entity_id': report['entity_id'], 'current_id': report['current_id'], 'depth_m': 100,
            'raw_profile_file': REPORT, 'raw_profile_sha256': pins[REPORT],
            'original_source_file': report['source_file'], 'original_source_sha256': report['source_sha256'],
            'counts': report['counts'], 'input_sha256': pins, 'geometry': report['geometry'],
            'overall_outcomes': report['overall_outcomes'], 'months': report['monthly_summaries'],
            'scenario_names': ['central', 'minus_supplied_component_magnitudes', 'plus_supplied_component_magnitudes'],
            'fractions': [.4, .5, .6], 'y_domain': [low-pad, high+pad],
            'figure_file': figure['figures']['.svg']['file'], 'figure_alt': figure['alt'],
            'physical_width_admitted': False, 'whole_current_width_km': None, 'annual_width_range_km': None,
            'geographic_current_edges': None, 'width_rank_eligible': False,
            'sampling_support_is_measurement_error': False,
            'supplied_magnitudes_are_statistical_confidence': False,
            'source_timestamps_independent_observations': False,
            'limitations': [
                'Distances along the fixed source section, not flow-normal physical widths or current edges.',
                'Five-day-filtered, SOM-filled, spatially mapped output; dates and grid cells are not independent observations.',
                'Bottom cells at or above100m are excluded, not substituted with zero-flow edges. Missing cells block crossings.',
                'Supplied-magnitude scenarios and threshold choices are sensitivity assumptions, not confidence bounds.',
                'Sampling brackets are interpolation support, not measurement error or instrument resolution.',
                'Resolved distributions condition on successful bracketing, not annual physical extrema.',
                'Original QC/mapping documentary disagreements remain unresolved.']}


def verify_inputs():
    expected = build(); stored = json.loads((ROOT/FILE).read_bytes())
    if stored != expected: raise ValueError('Changed EAC core summary/scene')
    return stored, {**stored['input_sha256'], FILE: sha(ROOT/FILE)}


def record(doc):
    return {'id': ID, 'label': 'EAC100m dated section-core spans; not physical widths',
            'entity_id': 'current:east-australian', 'current_id': 'east-australian',
            'status': doc['status'], 'rank_eligible': False, 'source_file': FILE,
            'source_file_sha256': sha(ROOT/FILE), 'source_json': (ROOT/FILE).read_bytes().decode('utf8'), 'document': doc}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    if args.check: doc, _ = verify_inputs()
    else:
        doc = build(); (ROOT/FILE).write_bytes((json.dumps(doc, separators=(',', ':'), allow_nan=False)+'\n').encode())
    print(json.dumps({'counts': doc['counts'], 'summary_bytes': (ROOT/FILE).stat().st_size}))
