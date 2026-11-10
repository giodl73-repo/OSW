"""Synthetic runtime receipts; no real passing browser result is asserted."""
import copy
import json
from pathlib import Path
import pytest
import indian_coastal_delivery_receipts_v1 as delivery
import indian_coastal_dimension_context_v1 as context


def fixture():
    # The export is an actual reviewed small metadata record. Runtime receipts
    # below are synthetic success fixtures, not evidence of real cloud success.
    source = json.loads((Path(__file__).resolve().parents[1] /
        'research/indian-coastal-context-candidate-export-execution-review-v1.json').read_bytes())
    source.update(schema='osw.indian-coastal-context-candidate.v1', status='PASS', published=False)
    contract = json.loads((context.ROOT / context.FILE).read_bytes())
    hashes = {path: context.pin(path) for path in contract['source_documents']}
    browser = {'status': 'PASS', 'bundle_sha256': delivery.PACKET, 'contract_sha256': delivery.CONTRACT_SHA,
               'native_wasm_cards': delivery.ENTITIES.copy(), 'record_queries': 7,
               'keyboard_queries': delivery.ENTITIES.copy(), 'new_physical_measurements': 0,
               'errors': [], 'original_downloads': [],
               'phone_widths_verified': [{'entity_id': entity, 'width_px': width}
                                        for entity in delivery.ENTITIES for width in [320, 390]],
               'source_documents': [{'path': path, 'sha256': sha} for path, sha in hashes.items()]}
    prior = {'status': 'PASS', 'bundle_sha256': delivery.PACKET, 'named_currents': 106,
             'native_wasm_object_views_equal': ['west-india-coastal', 'east-india-coastal',
                 'east-african-coastal', 'south-java', 'brazil'],
             'keyboard_evidence_query': True, 'dashboard_all_106_currents': True,
             'dashboard_alias_native_wasm_parity': True, 'source_context_coverage_modes_verified': 4,
             'phone_horizontal_overflow': False, 'errors': [], 'original_downloads': []}
    return source, browser, prior, hashes


def run_fixture():
    run = {'id': delivery.SOURCE_RUN, 'head_sha': delivery.SOURCE_COMMIT, 'head_branch': delivery.BRANCH,
           'event': 'push', 'path': delivery.WORKFLOW, 'status': 'completed', 'conclusion': 'success'}
    jobs = {'total_count': 2, 'jobs': [
        {'name': 'select-phase', 'status': 'completed', 'conclusion': 'success'},
        {'name': 'candidate-and-views', 'status': 'completed', 'conclusion': 'success', 'steps': [
            {'name': name, 'status': 'completed', 'conclusion': 'success', 'number': index + 1}
            for index, name in enumerate(delivery.STEPS)]}]}
    return run, jobs


def test_complete_synthetic_receipts_allow_verification_but_never_claim_installation():
    f = fixture();before = copy.deepcopy(f)
    result = delivery.verify_receipts(*f)
    assert result['native_wasm_and_browser_receipts_verified'] is True
    assert result['working_packet_installed'] is False and f == before
    delivery.verify_run(*run_fixture())


@pytest.mark.parametrize('change', ['parent', 'packet', 'width_count', 'physical_admission', 'array_preservation',
    'foreign_owner', 'source_replacement', 'source_added', 'browser_pending', 'browser_cohort', 'browser_card',
    'browser_queries', 'phone_missing', 'source_hash', 'source_duplicate', 'missing_expected_receipt',
    'download', 'dashboard', 'prior_cohort'])
def test_incomplete_or_mixed_receipts_reject(change):
    source, browser, prior, hashes = fixture()
    if change == 'parent':source['parent_logical_sha256'] = '0' * 64
    if change == 'packet':source['candidate']['logical_sha256'] = '0' * 64
    if change == 'width_count':source['candidate']['widths'] += 1
    if change == 'physical_admission':source['admission']['new_paired_widths'] = 1
    if change == 'array_preservation':source['admission']['preservation']['source_arrays_preserved'] = False
    if change == 'foreign_owner':source['admission']['changed_owner_ids'] = ['eddy:unrelated']
    if change == 'source_replacement':source['index_extension']['scientific_source_documents_replaced'] = 1
    if change == 'source_added':source['index_extension']['added_source_paths'].pop()
    if change == 'browser_pending':browser['status'] = 'RUNNING'
    if change == 'browser_cohort':browser['bundle_sha256'] = '0' * 64
    if change == 'browser_card':browser['native_wasm_cards'].pop()
    if change == 'browser_queries':browser['record_queries'] = 6
    if change == 'phone_missing':browser['phone_widths_verified'].pop()
    if change == 'source_hash':browser['source_documents'][0]['sha256'] = '0' * 64
    if change == 'source_duplicate':browser['source_documents'].append(copy.deepcopy(browser['source_documents'][0]))
    if change == 'missing_expected_receipt':hashes.pop('research/source-data/painter-eacc-2020/acquisition.json')
    if change == 'download':browser['original_downloads'] = ['https://example.invalid/original.nc']
    if change == 'dashboard':prior['dashboard_all_106_currents'] = False
    if change == 'prior_cohort':prior['bundle_sha256'] = '0' * 64
    with pytest.raises(ValueError):delivery.verify_receipts(source, browser, prior, hashes)


@pytest.mark.parametrize('change', ['live', 'failed', 'source', 'branch', 'workflow', 'missing_job',
    'duplicate_job', 'skipped_matrix', 'missing_step', 'reordered', 'duplicate_step'])
def test_wrong_live_partial_or_reordered_run_rejects(change):
    run, jobs = run_fixture();steps = jobs['jobs'][1]['steps']
    if change == 'live':run['status'] = 'in_progress'
    if change == 'failed':run['conclusion'] = 'failure'
    if change == 'source':run['head_sha'] = '0' * 40
    if change == 'branch':run['head_branch'] = 'main'
    if change == 'workflow':run['path'] = '.github/workflows/unrelated.yml'
    if change == 'missing_job':jobs['jobs'].pop(0)
    if change == 'duplicate_job':jobs['jobs'].append(copy.deepcopy(jobs['jobs'][1]))
    if change == 'skipped_matrix':steps[-1]['conclusion'] = 'skipped'
    if change == 'missing_step':steps.pop()
    if change == 'reordered':steps[2]['number'], steps[3]['number'] = steps[3]['number'], steps[2]['number']
    if change == 'duplicate_step':steps.append(copy.deepcopy(steps[-1]))
    with pytest.raises(ValueError):delivery.verify_run(run, jobs)
