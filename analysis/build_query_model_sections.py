"""Project checked NorKyst sections into query records; never current boundaries."""
import copy
import hashlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = 'research/norkyst-ingoy-2024-section-timeline.json'
MAPS = 'research/norkyst-ingoy-2024-map-frames.json'
UNITS = {'salinity': '1', 'u_eastward': 'm/s', 'v_northward': 'm/s'}
SAMPLE_ROLE = 'interpolated_fixed_section_model_field_not_current_boundary'


def build(timeline, maps, input_sha256):
    """Caller validates original source reconstruction before this projection."""
    frames, samples = [], []
    map_frames = {frame['date']: frame for frame in maps['frames']}
    for frame_index, original in enumerate(timeline['frames']):
        day = date.fromisoformat(original['date'])
        mapped = map_frames[original['date']]
        if any(original[key] != mapped[key] for key in
               ['sample_time_utc', 'receipt_file', 'receipt_sha256']):
            raise ValueError('Model profile and map have different source support')
        frame_id = 'model-frame:norkyst-ingoy:' + original['date']
        context = {'entity_id': 'current:' + timeline['current_context_id'],
                   'current_id': timeline['current_context_id'],
                   'date': original['date'], 'year': day.year, 'month': day.month,
                   'sample_time_utc': original['sample_time_utc'],
                   'depth_m': timeline['section']['depth_m'],
                   'annual_extrema_eligible': False, 'width_rank_eligible': False,
                   'state_footprint_join_eligible': False,
                   'source_file': TIMELINE, 'source_sha256': input_sha256[TIMELINE]}
        frames.append({**context, 'id': frame_id,
                       'label': 'NorKyst Ingøy section — ' + original['date'],
                       'record_type': 'model_section_frame',
                       'source_project': timeline['source_project'],
                       'source_license': timeline['source_license'],
                       'credit': timeline['credit'],
                       'source_catalog_url': timeline['source_catalog_url'],
                       'source_url': original['source_url'],
                       'receipt_file': original['receipt_file'],
                       'receipt_sha256': original['receipt_sha256'],
                       'section': copy.deepcopy(timeline['section']),
                       'sampling_rule': timeline['sampling_rule'],
                       'interpolation': timeline['interpolation'],
                       'limitations': timeline['limitations'],
                       'current_length_km': None, 'current_width_km': None,
                       'field_units': copy.deepcopy(UNITS),
                       'sample_count': len(original['profile']),
                       'available_sample_count': sum(all(point[key] is not None for key in UNITS)
                                                     for point in original['profile']),
                       'map_figure': mapped['figure'],
                       'map_figure_sha256': mapped['figure_sha256'],
                       'map_role': mapped['map_role'],
                       'map_source_file': MAPS, 'map_source_sha256': input_sha256[MAPS],
                       'url': 'norkyst-section.html?date=' + original['date']})
        for sample_index, point in enumerate(original['profile']):
            samples.append({**context,
                            'id': f'model-sample:norkyst-ingoy:{original["date"]}:{sample_index:03}',
                            'label': f'NorKyst {original["date"]} — section sample {sample_index:03}',
                            'record_type': 'model_section_sample',
                            'model_frame_id': frame_id, 'sample_index': sample_index,
                            'source_path': f'/frames/{frame_index}/profile/{sample_index}',
                            'sample_role': SAMPLE_ROLE,
                            'field_values_available': all(point[key] is not None for key in UNITS),
                            **copy.deepcopy(point)})
    return {'model_frames': frames, 'model_samples': samples}


def source_hashes():
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in [TIMELINE, MAPS]}
