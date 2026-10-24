"""Synthetic installation preconditions; no real installation or browser evidence."""
import copy
import json
import pytest
import indian_coastal_card_presentation_v1 as presentation
import verify_indian_coastal_installation_v1 as verifier


def fixture():
    control = 'f' * 40
    parent = {'schema': 'osw.query-engine-manifest.v1', 'engine': 'rust-osw-query-v1', 'abi_version': 1,
              'sha256': {presentation.UI: 'a' * 64, 'almanac/query-engine.wasm': 'b' * 64,
                         'almanac/query-data.json': 'c' * 64}}
    before = presentation.encoded(parent);display = b'synthetic display'
    overlay = presentation.overlay_manifest(parent, display, parent_manifest_sha=presentation.digest(before),
        source_run_id=verifier.delivery.SOURCE_RUN, control_commit=control)
    after = presentation.encoded(overlay)
    hashes = {'research/fixture-' + str(i) + '.json': str(i) * 64 for i in range(6)}
    receipt = {'schema': 'osw.indian-coastal-card-presentation.result.v1', 'status': 'PASS',
        'source_run_id': verifier.delivery.SOURCE_RUN, 'source_commit': verifier.delivery.SOURCE_COMMIT,
        'presentation_run_id': 789, 'presentation_control_commit': control,
        'bundle_sha256': verifier.delivery.PACKET, 'contract_sha256': verifier.delivery.CONTRACT_SHA,
        'wasm_cards': verifier.delivery.ENTITIES.copy(), 'keyboard_queries': verifier.delivery.ENTITIES.copy(),
        'record_queries': 7, 'errors': [], 'original_downloads': [],
        'current_coverage_catalogue_records': 106, 'current_coverage_catalogue_sha256': 'd' * 64,
        'native_validation_inherited_from_source_run': verifier.delivery.SOURCE_RUN,
        **{key: False for key in ['native_rebuild', 'wasm_rebuild', 'scientific_source_recomputation',
                                  'packet_or_index_modified', 'working_packet_installed']},
        'phone_viewports': [{'entity_id': entity, 'width_px': width}
                           for entity in verifier.delivery.ENTITIES for width in [320, 390]],
        'source_documents': [{'path': path, 'sha256': sha} for path, sha in hashes.items()],
        'parent_engine_manifest_sha256': presentation.digest(before),
        'presentation_engine_manifest_sha256': presentation.digest(after),
        'display_sha256': presentation.digest(display), 'wasm_sha256': parent['sha256']['almanac/query-engine.wasm']}
    return receipt, before, after, display, hashes


def run_fixture(receipt):
    run = {'id': 789, 'head_sha': receipt['presentation_control_commit'], 'head_branch': verifier.delivery.BRANCH,
           'path': verifier.WORKFLOW, 'event': 'push', 'status': 'completed', 'conclusion': 'success'}
    steps = [{'name': name, 'number': i + 1, 'status': 'completed', 'conclusion': 'success'} for i, name in enumerate([
        'Verify the original full validation before restoring any data',
        'Check display-only scope and local resource refusal',
        'Check saved data and WASM, revised cards, links and phone screenshots'])]
    return run, {'total_count': 2, 'jobs': [
        {'name': 'select-phase', 'status': 'completed', 'conclusion': 'success'},
        {'name': 'saved-card-presentation', 'status': 'completed', 'conclusion': 'success', 'steps': steps}]}


def test_exact_synthetic_presentation_binding_passes_without_publication():
    f = fixture();before = copy.deepcopy(f)
    result = verifier.verify_presentation_receipt(*f)
    assert result['unchanged_data_and_wasm_verified'] is True and f == before
    verifier.verify_presentation_run(*run_fixture(f[0]), f[0])


@pytest.mark.parametrize('change', ['packet', 'source_run', 'wasm', 'display', 'rebuild', 'phone', 'source', 'native', 'install'])
def test_mixed_or_incomplete_presentation_receipts_reject(change):
    receipt, before, after, display, hashes = fixture()
    if change == 'packet':receipt['bundle_sha256'] = '0' * 64
    if change == 'source_run':receipt['source_run_id'] += 1
    if change == 'wasm':receipt['wasm_sha256'] = '0' * 64
    if change == 'display':display = b'different'
    if change == 'rebuild':receipt['wasm_rebuild'] = True
    if change == 'phone':receipt['phone_viewports'].pop()
    if change == 'source':receipt['source_documents'].pop()
    if change == 'native':receipt['native_validation_inherited_from_source_run'] += 1
    if change == 'install':receipt['working_packet_installed'] = True
    with pytest.raises(ValueError):verifier.verify_presentation_receipt(receipt, before, after, display, hashes)


@pytest.mark.parametrize('change', ['pending', 'failed', 'run', 'source', 'job_missing', 'skipped', 'order'])
def test_wrong_or_partial_presentation_run_rejects(change):
    receipt = fixture()[0];run, jobs = run_fixture(receipt)
    if change == 'pending':run['status'] = 'in_progress'
    if change == 'failed':run['conclusion'] = 'failure'
    if change == 'run':run['id'] += 1
    if change == 'source':run['head_sha'] = '0' * 40
    if change == 'job_missing':jobs['jobs'].pop()
    if change == 'skipped':jobs['jobs'][1]['steps'][-1]['conclusion'] = 'skipped'
    if change == 'order':jobs['jobs'][1]['steps'][0]['number'] = 99
    with pytest.raises(ValueError):verifier.verify_presentation_run(run, jobs, receipt)


def visual_fixture():
    receipt_raw = presentation.encoded(fixture()[0])
    images = {entity.split(':')[1] + '-' + str(width) + 'px.png': b'synthetic screenshot ' + str(width).encode()
              for entity in verifier.delivery.ENTITIES for width in [320, 390]}
    review = {'schema': 'osw.indian-coastal-context.card-visual-review.v2', 'status': 'PASS',
              'installation_approved': True, 'source_run_id': verifier.delivery.SOURCE_RUN,
              'presentation_run_id': 789, 'presentation_control_commit': 'f' * 40,
              'packet_logical_sha256': verifier.delivery.PACKET,
              'browser_report_sha256': presentation.digest(receipt_raw),
              'screenshots': [{'path': name, 'sha256': presentation.digest(raw), 'bytes': len(raw),
                               'actually_viewed': True} for name, raw in images.items()]}
    return review, receipt_raw, images


def test_synthetic_visual_review_requires_exact_receipt_and_all_four_images():
    verifier.verify_visual_review(*visual_fixture())


@pytest.mark.parametrize('change', ['old_review', 'not_approved', 'wrong_receipt', 'missing_image', 'not_viewed', 'changed_image', 'wrong_run'])
def test_old_unreviewed_or_mixed_visual_evidence_rejects(change):
    review, receipt, images = visual_fixture()
    if change == 'old_review':review['schema'] = 'osw.indian-coastal-context.card-visual-review.v1'
    if change == 'not_approved':review['installation_approved'] = False
    if change == 'wrong_receipt':review['browser_report_sha256'] = '0' * 64
    if change == 'missing_image':images.pop(next(iter(images)))
    if change == 'not_viewed':review['screenshots'][0]['actually_viewed'] = False
    if change == 'changed_image':images[next(iter(images))] = b'changed'
    if change == 'wrong_run':review['presentation_run_id'] += 1
    with pytest.raises(ValueError):verifier.verify_visual_review(review, receipt, images)


def test_transport_streams_tiny_synthetic_packet_and_rejects_corruption(tmp_path):
    from query_packet import write_packet
    raw = b'{"schema":"osw.query-bundle.v1","fixture":true}\n'
    folder = tmp_path / 'almanac';folder.mkdir()
    packet = write_packet(folder / 'query-data.json', raw)
    pins = {'almanac/' + row['path']: row['sha256'] for row in packet['parts']}
    assert verifier.verify_transport(tmp_path, packet, pins, expected_logical=presentation.digest(raw)) == len(raw)
    (folder / packet['parts'][0]['path']).write_bytes(b'x' * len(raw))
    with pytest.raises(ValueError):verifier.verify_transport(tmp_path, packet, pins, expected_logical=presentation.digest(raw))


@pytest.mark.parametrize('change', ['none', 'count', 'duplicate', 'payload', 'owner', 'new_measurement'])
def test_compact_coverage_requires_all_current_metadata_and_excludes_payloads(change):
    rows = [{key: None for key in presentation.COVERAGE_FIELDS} for _ in range(106)]
    for i, row in enumerate(rows):
        row.update(id='current:synthetic-' + str(i), label='Synthetic current', type='named_current',
                   capabilities={}, measurement_ids=[], width_ids=[], width_sample_ids=[], route_ids=[])
    document = {'schema': 'osw.current-coverage-catalogue.snapshot.v1', 'source_run_id': verifier.delivery.SOURCE_RUN,
                'bundle_sha256': verifier.delivery.PACKET, 'currents': 106, 'new_measurements': 0, 'records': rows}
    if change == 'count':rows.pop()
    if change == 'duplicate':rows[-1]['id'] = rows[0]['id']
    if change == 'payload':rows[0]['geometry'] = {'coordinates': [1, 2]}
    if change == 'owner':rows[0]['type'] = 'named_eddy'
    if change == 'new_measurement':document['new_measurements'] = 1
    raw = presentation.encoded(document);receipt = {'current_coverage_catalogue_sha256': presentation.digest(raw)}
    if change == 'none':assert verifier.verify_coverage_snapshot(raw, receipt)['currents'] == 106
    else:
        with pytest.raises(ValueError):verifier.verify_coverage_snapshot(raw, receipt)
