"""Read-only saved-cohort installation gates; never publish or rebuild here."""
import hashlib
import json

import indian_coastal_card_presentation_v1 as presentation
import indian_coastal_delivery_receipts_v1 as delivery

WORKFLOW = '.github/workflows/indian-coastal-card-presentation-v1.yml'


def verify_presentation_run(run, jobs, receipt):
    if (run.get('head_sha') != receipt.get('presentation_control_commit')
            or run.get('head_branch') != delivery.BRANCH or run.get('path') != WORKFLOW
            or run.get('event') != 'push' or run.get('status') != 'completed'
            or run.get('conclusion') != 'success' or type(run.get('id')) is not int
            or run['id'] != receipt.get('presentation_run_id')):
        raise ValueError('Exact successful presentation run required')
    rows = jobs.get('jobs', [])
    if (jobs.get('total_count') != 2 or len(rows) != 2
            or {row.get('name') for row in rows} != {'select-phase', 'saved-card-presentation'}
            or any(row.get('status') != 'completed' or row.get('conclusion') != 'success' for row in rows)):
        raise ValueError('Complete saved-presentation jobs required')
    steps = next(row['steps'] for row in rows if row['name'] == 'saved-card-presentation')
    required = ['Verify the original full validation before restoring any data',
                'Check display-only scope and local resource refusal',
                'Check saved data and WASM, revised cards, links and phone screenshots']
    numbers = []
    for name in required:
        found = [step for step in steps if step.get('name') == name]
        if (len(found) != 1 or found[0].get('status') != 'completed'
                or found[0].get('conclusion') != 'success' or type(found[0].get('number')) is not int):
            raise ValueError('Required presentation gate missing/failed: ' + name)
        numbers.append(found[0]['number'])
    if any(number <= 0 for number in numbers) or any(a >= b for a, b in zip(numbers, numbers[1:])):
        raise ValueError('Presentation preflight and browser order changed')


def verify_presentation_receipt(receipt, parent_engine_raw, overlay_engine_raw, display_raw, document_hashes):
    expected = {'schema': 'osw.indian-coastal-card-presentation.result.v1', 'status': 'PASS',
                'source_run_id': delivery.SOURCE_RUN, 'source_commit': delivery.SOURCE_COMMIT,
                'bundle_sha256': delivery.PACKET, 'contract_sha256': delivery.CONTRACT_SHA,
                'native_validation_inherited_from_source_run': delivery.SOURCE_RUN,
                'wasm_cards': delivery.ENTITIES, 'keyboard_queries': delivery.ENTITIES, 'record_queries': 7,
                'errors': [], 'original_downloads': []}
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError('Presentation/source receipt identity or coverage changed')
    if (receipt.get('current_coverage_catalogue_records') != 106
            or not isinstance(receipt.get('current_coverage_catalogue_sha256'), str)
            or len(receipt['current_coverage_catalogue_sha256']) != 64):
        raise ValueError('Compact authoritative current-coverage snapshot required')
    if any(receipt.get(key) is not False for key in ['native_rebuild', 'wasm_rebuild',
            'scientific_source_recomputation', 'packet_or_index_modified', 'working_packet_installed']):
        raise ValueError('Display proof cannot claim a rebuild, data change or installation')
    if receipt.get('phone_viewports') != [{'entity_id': entity, 'width_px': width}
            for entity in delivery.ENTITIES for width in [320, 390]]:
        raise ValueError('All four actual phone views required')
    docs = receipt.get('source_documents', [])
    if len(document_hashes) != 6 or len(docs) != 6 or {
            row.get('path'): row.get('sha256') for row in docs} != document_hashes:
        raise ValueError('Complete unchanged source queries required')
    parent, updated = json.loads(parent_engine_raw), json.loads(overlay_engine_raw)
    presentation.validate_overlay(parent, updated)
    adjustment = updated['presentation_adjustment']
    if (receipt.get('parent_engine_manifest_sha256') != presentation.digest(parent_engine_raw)
            or receipt.get('presentation_engine_manifest_sha256') != presentation.digest(overlay_engine_raw)
            or receipt.get('display_sha256') != presentation.digest(display_raw)
            or updated['sha256'][presentation.UI] != presentation.digest(display_raw)
            or receipt.get('wasm_sha256') != parent['sha256']['almanac/query-engine.wasm']
            or adjustment.get('parent_engine_manifest_sha256') != presentation.digest(parent_engine_raw)
            or adjustment.get('source_run_id') != delivery.SOURCE_RUN
            or adjustment.get('presentation_control_commit') != receipt.get('presentation_control_commit')):
        raise ValueError('Mixed original/display/data/engine cohorts refused')
    return {'display_overlay_verified': True, 'unchanged_data_and_wasm_verified': True,
            'native_rebuild_performed': False, 'wasm_rebuild_performed': False}


def verify_visual_review(review, receipt_raw, screenshot_raw):
    """Require an actual replacement-image review, not the original cleanup finding."""
    if (review.get('schema') != 'osw.indian-coastal-context.card-visual-review.v2'
            or review.get('status') != 'PASS' or review.get('installation_approved') is not True
            or review.get('browser_report_sha256') != presentation.digest(receipt_raw)
            or review.get('source_run_id') != delivery.SOURCE_RUN
            or review.get('packet_logical_sha256') != delivery.PACKET):
        raise ValueError('Passing replacement visual review bound to exact receipt required')
    receipt = json.loads(receipt_raw)
    if (review.get('presentation_run_id') != receipt.get('presentation_run_id')
            or review.get('presentation_control_commit') != receipt.get('presentation_control_commit')):
        raise ValueError('Replacement visual review belongs to a different presentation run')
    names = {entity.split(':')[1] + '-' + str(width) + 'px.png'
             for entity in delivery.ENTITIES for width in [320, 390]}
    screenshots = review.get('screenshots', [])
    if len(screenshots) != 4 or set(screenshot_raw) != names or {row.get('path') for row in screenshots} != names:
        raise ValueError('All four replacement screenshots must be inspected')
    for row in screenshots:
        raw = screenshot_raw[row['path']]
        if (row.get('actually_viewed') is not True or row.get('sha256') != presentation.digest(raw)
                or row.get('bytes') != len(raw)):
            raise ValueError('Unreviewed or changed replacement screenshot')


def verify_coverage_snapshot(raw, receipt):
    document = json.loads(raw)
    rows = document.get('records', [])
    if (presentation.digest(raw) != receipt.get('current_coverage_catalogue_sha256')
            or document.get('schema') != 'osw.current-coverage-catalogue.snapshot.v1'
            or document.get('source_run_id') != delivery.SOURCE_RUN
            or document.get('bundle_sha256') != delivery.PACKET
            or document.get('currents') != 106 or len(rows) != 106
            or len({row.get('id') for row in rows}) != 106
            or type(document.get('new_measurements')) is not int or document['new_measurements'] != 0):
        raise ValueError('Wrong or incomplete current coverage metadata snapshot')
    for row in rows:
        if (set(row) != set(presentation.COVERAGE_FIELDS) or row.get('type') != 'named_current'
                or not isinstance(row.get('id'), str) or not row['id'].startswith('current:')
                or not isinstance(row.get('capabilities'), dict)
                or any(not isinstance(row.get(field), list) or any(not isinstance(value, str) for value in row[field])
                       for field in ['measurement_ids', 'width_ids', 'width_sample_ids', 'route_ids'])):
            raise ValueError('Coverage metadata omitted fields or included non-current/payload data')
    return document


def verify_transport(root, packet, pins, *, expected_logical=delivery.PACKET):
    """Stream checked transport bytes in the cloud; never parse the full bundle."""
    from query_packet import descriptors
    actual, size = hashlib.sha256(), 0
    for part in descriptors(packet):
        path = 'almanac/' + part['path']
        target = presentation.local_path(root, path)
        if pins.get(path) != part['sha256'] or target.stat().st_size != part['byte_length']:
            raise ValueError('Unpinned or changed candidate transport part')
        local = hashlib.sha256()
        with target.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                actual.update(chunk);local.update(chunk);size += len(chunk)
        if local.hexdigest() != part['sha256']:raise ValueError('Candidate part checksum changed')
    if (actual.hexdigest() != expected_logical or packet['logical_sha256'] != expected_logical
            or size != packet['logical_byte_length']):
        raise ValueError('Saved candidate logical identity changed')
    return size
