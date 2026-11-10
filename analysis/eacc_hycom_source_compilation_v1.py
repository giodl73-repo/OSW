"""Receipt-bound HYCOM payload validation and streaming monthly compilation.

No network or file IO. Original velocity use requires the separately frozen
cloud source workflow. Synthetic payloads alone have exercised this module.
"""
import calendar
from datetime import datetime, timezone
import hashlib
import json

import numpy as np

from acquire_south_australian_hycom_2d import parse_ascii
from eacc_hycom_source_selection_v1 import MISSING, SCALE, make_selection


RECEIPT_SCHEMA = 'osw.eacc-hycom.velocity-response-receipt.v1'


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf8')


def pin(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def validate_response(raw, request, selection):
    """Validate both packed components and their exact requested coordinates.

    Caller must first reproduce selection from the pinned metadata, as done by
    compile_source. This helper does not authorize acquisition or admission.
    """
    if request not in selection['requests']:
        raise ValueError('Response request is not in source selection')
    if type(raw) is not bytes or len(raw) > selection['response_cap_bytes']:
        raise ValueError('Payload is not bounded original bytes')
    count = len(request['time_indices'])
    if not 1 <= count <= 6:
        raise ValueError('Invalid daily request support')
    axes = selection['selected_coordinates']
    arrays = parse_ascii(raw.decode('utf8'), nt=count, ny=len(axes['lat']), nx=len(axes['lon']))
    expected = {name: axes[name] for name in ('depth', 'lat', 'lon')}
    expected['time'] = [selection['source_time_hours_since_2000_01_01'][i] for i in request['time_indices']]
    for name, values in expected.items():
        if not np.array_equal(arrays[name], np.asarray(values, dtype='<f8')):
            raise ValueError('Response coordinates differ from selection: ' + name)
    return arrays


def validate_receipt(raw, receipt, request, selection):
    if type(raw) is not bytes or len(raw) > selection['response_cap_bytes']:
        raise ValueError('Payload is not bounded original bytes')
    required = {'schema', 'request_file', 'request_url', 'final_url', 'http_status',
                'content_type', 'started_utc', 'finished_utc', 'response', 'selection_sha256'}
    if type(receipt) is not dict or set(receipt) != required:
        raise ValueError('Unexpected response receipt inventory')
    if receipt['schema'] != RECEIPT_SCHEMA or receipt['request_file'] != request['file']:
        raise ValueError('Changed response receipt identity')
    if receipt['request_url'] != request['url'] or receipt['final_url'] != request['url']:
        raise ValueError('Changed requested/final source URL')
    if type(receipt['http_status']) is not int or receipt['http_status'] != 200:
        raise ValueError('Unsuccessful response cannot be compiled')
    if not isinstance(receipt['content_type'], str) or receipt['content_type'].split(';')[0].strip().lower() != 'text/plain':
        raise ValueError('Unexpected source content type')
    if receipt['response'] != pin(raw):
        raise ValueError('Response bytes do not match receipt')
    if receipt['selection_sha256'] != pin(encoded(selection))['sha256']:
        raise ValueError('Receipt belongs to another source selection')
    try:
        started, finished = [datetime.fromisoformat(receipt[key]) for key in ('started_utc', 'finished_utc')]
    except (TypeError, ValueError) as error:
        raise ValueError('Invalid receipt times') from error
    if any(stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp) for stamp in (started, finished)) or finished < started:
        raise ValueError('Receipt times must be ordered UTC instants')
    return started, finished


def _nullable(array):
    values = array.astype(object)
    values[~np.isfinite(array)] = None
    return values.tolist()


def compile_source(metadata, selection, response_files, load_response):
    """Compile one response at a time; keep every month and missing cell.

    load_response(name) returns (original bytes, parsed receipt). The exact
    inventory includes every planned response; a missing downloaded payload is
    a custody failure, distinct from a provider timestamp absent in metadata.
    """
    if selection != make_selection(metadata):
        raise ValueError('Source selection cannot be reproduced from metadata')
    expected = [request['file'] for request in selection['requests']]
    inventory = list(response_files)
    if len(inventory) != len(set(inventory)) or set(inventory) != set(expected):
        raise ValueError('Incomplete, duplicate or unexpected response inventory')
    shape = tuple(len(selection['selected_coordinates'][name]) for name in ('lat', 'lon'))
    months, receipts = [], {}
    previous_finished = None
    for month in range(1, 13):
        counts = np.zeros(shape, dtype='<i2')
        totals = [np.zeros(shape, dtype='<i8'), np.zeros(shape, dtype='<i8')]
        source_hours = []
        for request in selection['requests']:
            if request['month'] != month:
                continue
            raw, receipt = load_response(request['file'])
            started, finished = validate_receipt(raw, receipt, request, selection)
            if previous_finished is not None and started < previous_finished:
                raise ValueError('Response receipts overlap or violate source request order')
            previous_finished = finished
            arrays = validate_response(raw, request, selection)
            u, v = arrays['water_u'], arrays['water_v']
            valid = (u != MISSING) & (v != MISSING)
            counts += valid.sum(axis=0).astype('<i2')
            for total, array in zip(totals, (u, v)):
                total += np.where(valid, array, 0).sum(axis=0, dtype=np.int64)
            source_hours.extend(arrays['time'].tolist())
            receipts[request['file']] = {
                'response': pin(raw), 'canonical_receipt': pin(encoded(receipt)),
                'request_url': request['url'], 'started_utc': receipt['started_utc'],
                'finished_utc': receipt['finished_utc']}
        calendar_days = calendar.monthrange(2013, month)[1]
        minimum = (4 * calendar_days + 4) // 5
        # Plan reproduction guarantees unique ordered daily00Z times. Assert
        # again at the aggregation boundary instead of counting duplicate days.
        stamps = [datetime(2000, 1, 1, tzinfo=timezone.utc).timestamp() + hours * 3600 for hours in source_hours]
        if len(stamps) != len(set(stamps)) or source_hours != sorted(source_hours) or len(stamps) > calendar_days:
            raise ValueError('Duplicate, reordered or excessive monthly samples')
        means = []
        for total in totals:
            mean = np.full(shape, np.nan, dtype='<f8')
            np.divide(total * SCALE, counts, out=mean, where=counts >= minimum)
            means.append(mean)
        eligible = counts >= minimum
        months.append({'month': month, 'calendar_days': calendar_days, 'minimum_pairs': minimum,
                       'sample_days': len(source_hours),
                       'source_time_hours_since_2000_01_01': source_hours,
                       'paired_samples': counts.tolist(),
                       'eastward_m_s': _nullable(means[0]), 'northward_m_s': _nullable(means[1]),
                       'eligible_cells': int(eligible.sum()),
                       'paired_count_min': int(counts.min()), 'paired_count_max': int(counts.max())})
    return {'schema': 'osw.eacc-hycom.monthly-vector-fields.v1',
            'evidence_class': 'paired_daily_model_sample_means_not_current_measurements',
            'dataset_url': selection['dataset_url'], 'source_model_year': 2013,
            'provider_depth_m': 15, 'velocity_units': 'm/s',
            'longitude_degrees_east': selection['selected_coordinates']['lon'],
            'latitude_degrees_north': selection['selected_coordinates']['lat'],
            'source_metadata': selection['metadata'], 'selection': pin(encoded(selection)),
            'original_response_bindings': receipts, 'packing_scale_float64_hex': SCALE.hex(),
            'missing_daily_00z': selection['missing_daily_00z'], 'months': months,
            'source_response_binding_verified': True, 'missing_mean_value': None,
            'interpretation': 'Paired daily00Z sample means at a standard output depth on a remapped model grid; not observations, all-time monthly means or climatology.',
            'current_association_verified': False, 'whole_current_width_km': None,
            'whole_current_length_km': None, 'annual_physical_range_admitted': False,
            'measurement_uncertainty_km': None, 'width_rank_eligible': False,
            'length_rank_eligible': False, 'physical_state_join_eligible': False}
