"""Saved-cohort source continuation; original scientific producers stay frozen.

Original bodies are restored/validated only in the gated cloud runner.
Synthetic fixtures alone exercise these functions locally.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request

from eacc_hycom_cloud_acquisition_v2 import (
    _NoRedirect, _read, _write_once, digest, encoded,
)
from eacc_hycom_source_compilation_v1 import pin, validate_receipt, validate_response
from eacc_hycom_source_selection_v1 import make_selection


SOCKET_TIMEOUT_SECONDS = 50


def fetch_response(url, cap):
    """One bounded attempt at the same frozen URL; no redirect or retry."""
    request = urllib.request.Request(url, headers={'User-Agent': 'OSW-EACC-saved-cohort/1.0'})
    with urllib.request.build_opener(_NoRedirect).open(request, timeout=SOCKET_TIMEOUT_SECONDS) as response:
        content_type = response.headers.get('Content-Type', '')
        if response.status != 200 or content_type.split(';')[0].strip().lower() != 'text/plain' or response.url != url:
            raise ValueError('Unexpected source HTTP metadata')
        declared = response.headers.get('Content-Length')
        if declared is not None and (not declared.isdigit() or int(declared) > cap):
            raise ValueError('Source Content-Length exceeds byte cap')
        chunks, count = [], 0
        while True:
            chunk = response.read(min(65536, cap + 1 - count))
            if not chunk:
                break
            chunks.append(chunk); count += len(chunk)
            if count > cap:
                raise ValueError('Source response exceeds byte cap')
        if declared is not None and count != int(declared):
            raise ValueError('Truncated source response')
        return {'raw': b''.join(chunks), 'http_status': response.status,
                'content_type': content_type, 'final_url': response.url}


def verify_basis(directory, selection, review):
    """Rehash original bodies, receipts and metadata; never trust a filename."""
    directory = Path(directory).resolve()
    responses = review['source_responses']
    if review.get('source_compilation_completed') is not False:
        raise ValueError('Source continuation cannot rerun an already compiled case')
    names = [item['file'] for item in responses]
    expected_prefix = [request['file'] for request in selection['requests'][:len(names)]]
    if not names or names != expected_prefix or len(names) >= len(selection['requests']):
        raise ValueError('Retained source is not a nonempty strict request prefix')
    expected = {'coordinates.ascii', 'metadata.das', 'metadata.dds', 'preflight.json',
                'selection.json', 'environment.json', 'case-failure.json', 'responses/failure.json'}
    expected |= {'responses/' + name for name in names}
    expected |= {'responses/' + name + '.receipt.json' for name in names}
    basis_format = review.get('basis_format', 'original_v2')
    if basis_format == 'continued_v1':
        expected |= {'source-lineage.json', 'resume-preflight.json',
                     'origin/environment.json', 'origin/case-failure.json', 'origin/failure.json'}
    elif basis_format != 'original_v2':
        raise ValueError('Unknown restored source layout')
    actual = set()
    for path in directory.rglob('*'):
        if path.is_symlink() or not path.resolve().is_relative_to(directory):
            raise ValueError('Unsafe restored artifact path')
        if path.is_file():
            actual.add(path.relative_to(directory).as_posix())
    if actual != expected:
        raise ValueError('Unexpected/incomplete original artifact inventory')
    preflight_raw = _read(directory, 'preflight.json', 262144)
    if digest(preflight_raw) != review['preflight_sha256']:
        raise ValueError('Original preflight does not match reviewed source')
    preflight = json.loads(preflight_raw)
    for name, expected_sha in review.get('local_transfer', {}).get('selected_metadata_sha256', {}).items():
        relative = 'responses/failure.json' if name == 'failure.json' else name
        if relative not in expected or digest(_read(directory, relative, 262144)) != expected_sha:
            raise ValueError('Reviewed source metadata byte fingerprint changed')
    raw_selection = _read(directory, 'selection.json', 131072)
    if digest(raw_selection) != preflight['selection_sha256'] or json.loads(raw_selection) != selection:
        raise ValueError('Original raw selection bytes or plan changed')
    canonical_sha = digest(encoded(selection))
    metadata = {name: _read(directory, name, 262144) for name in ('coordinates.ascii', 'metadata.das', 'metadata.dds')}
    if make_selection(metadata) != selection:
        raise ValueError('Restored metadata does not reconstruct source selection')
    environment = json.loads(_read(directory, 'environment.json', 32768))
    if (environment['source_commit'] != review['source_commit']
            or environment['run_id'] != review['run_id'] or environment['run_attempt'] != review['run_attempt']
            or environment['scientific_input_sha256'] != preflight['input_sha256']):
        raise ValueError('Changed original execution identity')
    failure = json.loads(_read(directory, 'responses/failure.json', 32768))
    if (failure['completed_files'] != names or failure['request'] != selection['requests'][len(names)]
            or failure['source_field_compilation_completed'] is not False):
        raise ValueError('Restored failure is not the reviewed incomplete prefix')
    case_failure = json.loads(_read(directory, 'case-failure.json', 32768))
    if case_failure != review['case_failure'] or failure != review['failure']:
        raise ValueError('Original failure evidence differs from reviewed metadata')
    previous_finished = None
    for item, request in zip(responses, selection['requests']):
        name = item['file']
        raw = _read(directory, 'responses/' + name, selection['response_cap_bytes'])
        receipt_raw = _read(directory, 'responses/' + name + '.receipt.json', 8192)
        receipt = json.loads(receipt_raw)
        if pin(raw) != item['response'] or digest(receipt_raw) != item['receipt_sha256']:
            raise ValueError('Retained original response/receipt checksum changed')
        if receipt['selection_sha256'] != canonical_sha:
            raise ValueError('Receipt is not bound to canonical source semantics')
        started, finished = validate_receipt(raw, receipt, request, selection)
        if previous_finished is not None and started < previous_finished:
            raise ValueError('Original source receipts overlap or reorder requests')
        previous_finished = finished
        validate_response(raw, request, selection)
    return names


def resume_responses(basis, output, selection, review, fetch=fetch_response, clock=None, ready=None):
    """Copy successes byte-for-byte and fetch only the remaining exact URLs."""
    from eacc_hycom_source_compilation_v1 import RECEIPT_SCHEMA
    basis, output = Path(basis).resolve(), Path(output).resolve()
    if output.is_relative_to(basis) or basis.is_relative_to(output):
        raise ValueError('Continuation output and restored source must be separate')
    completed = verify_basis(basis, selection, review)
    clock = clock or (lambda: datetime.now(timezone.utc))
    output.mkdir(parents=True, exist_ok=False)
    destination = output / 'responses'; destination.mkdir()
    # Preserve source metadata exactly. New-run provenance is separate.
    for name in ('coordinates.ascii', 'metadata.das', 'metadata.dds', 'selection.json', 'preflight.json'):
        _write_once(output / name, _read(basis, name, 262144))
    origin = output / 'origin'; origin.mkdir()
    for name in ('environment.json', 'case-failure.json'):
        _write_once(origin / name, _read(basis, name, 32768))
    _write_once(origin / 'failure.json', _read(basis, 'responses/failure.json', 32768))
    for name in completed:
        _write_once(destination / name, _read(basis, 'responses/' + name, selection['response_cap_bytes']))
        _write_once(destination / (name + '.receipt.json'), _read(basis, 'responses/' + name + '.receipt.json', 8192))
    reused = len(completed)
    previous_finished = datetime.fromisoformat(json.loads(
        _read(basis, 'responses/' + completed[-1] + '.receipt.json', 8192))['finished_utc'])
    _write_once(output / 'source-lineage.json', encoded({
        'schema': 'osw.eacc-hycom.source-lineage.v1', 'basis_run_id': review['run_id'],
        'basis_run_attempt': review['run_attempt'], 'basis_source_commit': review['source_commit'],
        'basis_artifact': review.get('artifact'), 'reused_requests': reused,
        'parent_lineage': json.loads(_read(basis, 'source-lineage.json', 262144)) if review.get('basis_format') == 'continued_v1' else None,
        'reused_files': completed.copy(), 'original_preflight_sha256': review['preflight_sha256'],
        'canonical_selection_sha256': digest(encoded(selection)),
        'original_selection_file_sha256': digest(_read(basis, 'selection.json', 131072)),
        'socket_timeout_seconds': SOCKET_TIMEOUT_SECONDS, 'physical_method_changed': False}))
    if ready is not None:
        ready(output)
    for request in selection['requests'][reused:]:
        try:
            started = clock().isoformat()
            result = fetch(request['url'], selection['response_cap_bytes'])
            finished = clock().isoformat()
            raw = result['raw']
            if type(raw) is not bytes or len(raw) > selection['response_cap_bytes']:
                raise ValueError('Fetch returned unbounded/nonoriginal bytes')
            receipt = {'schema': RECEIPT_SCHEMA, 'request_file': request['file'],
                       'request_url': request['url'], 'final_url': result['final_url'],
                       'http_status': result['http_status'], 'content_type': result['content_type'],
                       'started_utc': started, 'finished_utc': finished, 'response': pin(raw),
                       'selection_sha256': digest(encoded(selection))}
            _write_once(destination / request['file'], raw)
            _write_once(destination / (request['file'] + '.receipt.json'), encoded(receipt))
            start_time, finish_time = validate_receipt(raw, receipt, request, selection)
            if start_time < previous_finished:
                raise ValueError('Continued source receipts overlap or reverse time')
            previous_finished = finish_time
            validate_response(raw, request, selection)
            completed.append(request['file'])
            print('continued', request['file'], len(raw), flush=True)
        except Exception as error:
            _write_once(destination / 'failure.json', encoded({
                'schema': 'osw.eacc-hycom.acquisition-failure.v1', 'request': request,
                'completed_files': completed, 'error_type': type(error).__name__,
                'error': str(error)[:2048], 'finished_utc': clock().isoformat(),
                'automatic_retry': False, 'source_field_compilation_completed': False}))
            raise
    return completed


def review_projection(fields, diagnostic, lineage):
    """Copy existing results only; no source arrays, estimator or uncertainty."""
    if (fields['schema'] != 'osw.eacc-hycom.monthly-vector-fields.v1'
            or diagnostic['schema'] != 'osw.eacc-regional-model-core.numerical-diagnostic.v2'
            or len(fields['months']) != 12 or len(diagnostic['cases']) != 72):
        raise ValueError('Projection requires complete original source/diagnostic schemas')
    summaries = []
    for case in diagnostic['cases']:
        center = next((station for station in case['stations'] if station['station_arc_parameter_km'] == 0), None)
        thresholds = []
        if center is not None:
            for threshold in center['threshold_cases']:
                thresholds.append({key: threshold[key] for key in (
                    'fraction', 'status', 'diagnostic_span_km', 'resolved_span_km',
                    'native_cell_scale_km', 'span_in_native_cell_scales')})
        summaries.append({key: case[key] for key in (
            'id', 'month', 'native_latitude_offset', 'normal_sample_step_km', 'status',
            'all_five_local_axis_checks_pass', 'all_five_half_peak_spans_resolved')} |
            {'central_thresholds': thresholds})
    return {'schema': 'osw.eacc-hycom.compact-review.v1', 'source_lineage': lineage,
            'investigated_current_id': 'current:east-african-coastal',
            'evidence_class': diagnostic['evidence_class'],
            'source_model_year': fields['source_model_year'], 'provider_depth_m': fields['provider_depth_m'],
            'source_metadata': fields['source_metadata'], 'selection': fields['selection'],
            'source_months': [{key: month[key] for key in (
                'month', 'sample_days', 'minimum_pairs', 'eligible_cells', 'paired_count_min', 'paired_count_max')}
                for month in fields['months']],
            'months': diagnostic['months'], 'case_summaries': summaries,
            'normal_step_comparisons': diagnostic['normal_step_comparisons'],
            'native_seed_comparisons': diagnostic['native_seed_comparisons'],
            'current_association_verified': False, 'measurement_uncertainty_km': None,
            'annual_physical_minimum_width_km': None, 'annual_physical_maximum_width_km': None,
            'new_current_widths_admitted': 0, 'physical_method_changed': False}
