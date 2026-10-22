"""Apply unchanged OSCAR local-normal checks to the frozen HYCOM source.

Candidate diagnostics are not catalog current widths or annual ranges.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
from acquire_indian_secc_hycom_2013 import pin, validate_plan
from acquire_eac_100m_source import write_json
from indian_secc_local_normals import case, SAMPLE_COLUMNS
from west_australian_regional_streamlines import Field

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'plans/indian-secc-hycom-local-normal-protocol-v1.md'
ANCHORS = 'research/indian-secc-positive-band-connectivity.json'
PREFLIGHT = 'research/indian-secc-hycom-2013-diagnostic-preflight.json'


def stronger_candidate(cases):
    """Axis, paired-edge, resolution and hemisphere gates remain separate."""
    if len(cases) != 2 or {c['normal_sample_step_km'] for c in cases} != {5, 10}:
        return False
    for c in cases:
        if not c['primary_seed'] or not c['all_five_local_axis_checks_pass'] or len(c['stations']) != 5:
            return False
        for station in c['stations']:
            nominal = station['threshold_cases'][1]
            if (nominal['status'] != 'paired_sampled_edges'
                    or nominal['resolution_review_required'] is not False
                    or nominal['any_edge_at_or_north_of_equator'] is not False):
                return False
    return True


def build(directory):
    directory = Path(directory)
    declared = json.loads((ROOT/PREFLIGHT).read_bytes())
    for path, expected in declared['dependencies'].items():
        if pin(ROOT/path) != expected:
            raise ValueError('Changed declared diagnostic dependency: '+path)
    plan = validate_plan(directory)
    quality = json.loads((directory/'quality.json').read_bytes())
    if quality['selection'] != pin(directory/'selection.json') or quality['monthly_arrays'] != pin(directory/'monthly.npz'):
        raise ValueError('Changed source preparation')
    anchors = json.loads((ROOT/ANCHORS).read_bytes())
    with np.load(directory/'monthly.npz', allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in archive.files}
    if arrays['month'].tolist() != list(range(1, 13)) or arrays['depth'].tolist() != [15]:
        raise ValueError('Changed month or depth support')
    cases = []
    for m in range(1, 13):
        field = Field(arrays['lon'], arrays['lat'], arrays['u_m_s'][m-1], arrays['v_m_s'][m-1])
        for anchor in anchors['months'][m-1]['anchors']:
            for offset in [-1, 0, 1]:
                for step in [5, 10]:
                    cases.append(case(field, anchor, offset, step, m))
    comparisons = []
    for a, b in zip(cases[::2], cases[1::2]):
        comparisons.append({'month': a['month'], 'section_id': a['section_id'],
                            'native_latitude_offset': a['native_latitude_offset'],
                            'case_ids': [a['id'], b['id']],
                            'both_five_station_axis_checks_pass': a['all_five_local_axis_checks_pass'] and b['all_five_local_axis_checks_pass'],
                            'all_station_half_peak_resolution_hemisphere_checks_pass': stronger_candidate([a, b]),
                            'named_current_association_verified': False, 'width_admitted': False})
    monthly = []
    for m in range(1, 13):
        selected = [c for c in cases if c['month'] == m]
        monthly.append({'month': m, 'attempts': len(selected),
                        'five_station_axis_passes': sum(c['all_five_local_axis_checks_pass'] for c in selected),
                        'both_step_primary_axis_passes': sum(c['month'] == m and c['native_latitude_offset'] == 0 and c['both_five_station_axis_checks_pass'] for c in comparisons),
                        'stronger_candidates': sum(c['month'] == m and c['all_station_half_peak_resolution_hemisphere_checks_pass'] for c in comparisons),
                        'paired_half_peak_sections': sum(s['threshold_cases'][1]['status'] == 'paired_sampled_edges' for c in selected for s in c['stations'])})
    dependencies = [PROTOCOL, PREFLIGHT, ANCHORS, 'analysis/indian_secc_hycom_local_normals.py',
                    'analysis/indian_secc_local_normals.py', 'analysis/west_australian_regional_streamlines.py',
                    'analysis/west_australian_regional_streamlines_rk4.py']
    return {'schema': 'osw.indian-secc-hycom-local-normals.v1',
            'status': 'exploratory_model_local_candidates_not_current_dimensions',
            'current_id': 'indian-south-equatorial-countercurrent',
            'source_quality': pin(directory/'quality.json'), 'selection': pin(directory/'selection.json'),
            'dependencies': {p: pin(ROOT/p) for p in dependencies},
            'sample_columns': SAMPLE_COLUMNS, 'cases': cases, 'step_comparisons': comparisons,
            'monthly_summary': monthly,
            'counts': {'attempts': len(cases), 'status_counts': dict(sorted(Counter(c['status'] for c in cases).items())),
                       'five_station_axis_passes': sum(m['five_station_axis_passes'] for m in monthly),
                       'both_step_primary_axis_passes': sum(m['both_step_primary_axis_passes'] for m in monthly),
                       'stronger_candidates': sum(m['stronger_candidates'] for m in monthly),
                       'paired_half_peak_sections': sum(m['paired_half_peak_sections'] for m in monthly)},
            'packing_scale': plan['packing_scale_float32_as_float64'],
            'source_model_year': 2013, 'source_depth_m': 15,
            'current_association_verified': False, 'physical_current_axis_admitted': False,
            'whole_current_width_km': None, 'whole_current_length_km': None,
            'annual_physical_width_range_km': None, 'width_rank_eligible': False,
            'physical_state_join_eligible': False, 'seasonal_current_footprint_admitted': False,
            'limitations': ['Monthly means of paired available daily-00Z reanalysis samples, not observations or a full three-hourly mean.',
                            'Product, forcing, depth interpretation and temporal support differ from OSCAR; this does not isolate grid-resolution effects.',
                            'Original OSCAR seed coordinates are snapped to HYCOM native latitudes; native-offset physical distances differ.',
                            'Short mean-field streamlines and local threshold spans do not establish named-current identity or annual physical extents.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/indian-secc-hycom-2013')
    parser.add_argument('--output', type=Path, default=ROOT/'research/indian-secc-hycom-2013-local-normal-spans.json')
    args = parser.parse_args()
    report = build(args.directory)
    write_json(args.output, report)
    print(json.dumps(report['counts']))
