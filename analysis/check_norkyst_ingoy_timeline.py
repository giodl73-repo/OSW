"""Reconstruct the acquired/model section diagnostic and enforce its scope."""
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from fetch_norkyst_ingoy_annual_samples import DATES, parse_ascii
from build_norkyst_ingoy_timeline import profile

ROOT = Path(__file__).resolve().parents[1]


def validate(document):
    if document['status'] != 'model_section_diagnostic_not_canonical_current_measurement' or document['annual_extrema_eligible'] is not False or document['source_license'] != 'CC-BY-4.0':
        raise ValueError('Invalid model admission or license')
    if document['section'] != {'longitude_degrees_east': 24, 'start_latitude': 71.1, 'end_latitude': 73, 'depth_m': 10, 'sample_spacing_degrees': 0.01, 'orientation': 'fixed meridional section, not a fitted flow-normal section', 'location_role': 'Ingoy region coastal-to-offshore diagnostic; selected limits are not current boundaries'}:
        raise ValueError('Changed fixed section')
    for kind in ['acquisition', 'generator', 'protocol']:
        if hashlib.sha256((ROOT/document[f'{kind}_file']).read_bytes()).hexdigest() != document[f'{kind}_sha256']:
            raise ValueError('Stale derived provenance')
    if [frame['date'] for frame in document['frames']] != DATES:
        raise ValueError('Incomplete or changed preselected dates')
    for frame in document['frames']:
        path = ROOT/frame['receipt_file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != frame['receipt_sha256']:
            raise ValueError('Changed pinned receipt')
        receipt = json.loads(path.read_text(encoding='utf-8'))
        datetime.fromisoformat(receipt['retrieved_at_utc'])
        if receipt['grid_index_slices'] != {'Y': [576,4,764], 'X': [2420,4,2616]} or receipt['packing'] != {'salinity': {'scale':0.001,'offset':30.0,'fill':-32767,'units':'1'}, 'u_eastward': {'scale':0.001,'offset':0.0,'fill':-32767,'units':'m/s'}, 'v_northward': {'scale':0.001,'offset':0.0,'fill':-32767,'units':'m/s'}}:
            raise ValueError('Changed grid/packing/units')
        for kind in ['response', 'metadata']:
            if hashlib.sha256((ROOT/receipt[f'source_{kind}_file']).read_bytes()).hexdigest() != receipt[f'source_{kind}_sha256']:
                raise ValueError('Changed raw source')
        arrays, axes = parse_ascii((ROOT/receipt['source_response_file']).read_bytes())
        if arrays != receipt['packed_field_arrays'] or axes != {'time': datetime.fromisoformat(frame['date']+'T12:00:00+00:00').timestamp(), 'depth': 10.0}:
            raise ValueError('Changed parsed fields or source axes')
        if receipt['source_project'] != 'Norkyst_v3' or receipt['source_license'] != 'CC-BY-4.0' or receipt['annual_extrema_eligible'] is not False or receipt['width_rank_eligible'] is not False:
            raise ValueError('Invalid source interpretation')
        if frame['sample_time_utc'] != receipt['sample_time_utc'] or frame['source_url'] != receipt['source_url'] or frame['current_length_km'] is not None or frame['current_width_km'] is not None:
            raise ValueError('Invented current metric or changed frame support')
        if frame['profile'] != profile(receipt):
            raise ValueError('Changed interpolated profile')
        for point in frame['profile']:
            if any(value is not None and not math.isfinite(value) for key,value in point.items() if key in ['salinity','u_eastward','v_northward']):
                raise ValueError('Nonfinite profile')


def main():
    validate(json.loads((ROOT/'research/norkyst-ingoy-2024-section-timeline.json').read_text(encoding='utf-8')))
    print('OK: 12 pinned hourly profiles; raw fields, coordinates, interpolation and non-admission verified')


if __name__ == '__main__':
    main()
