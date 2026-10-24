"""Synthetic publication guards; never contact Git or load real payloads."""
import copy
import sys
import pytest
import install_indian_coastal_context_v1 as install


@pytest.mark.parametrize('arguments,environment', [([], {}),
    (['--publish', '--site', 'fixture', '--audit', 'fixture'], {}),
    ([], {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
          'GITHUB_REF': 'refs/heads/codex/current-measurement-gaps'})])
def test_unrequested_or_local_installation_refuses_before_payload_or_git(monkeypatch, arguments, environment):
    monkeypatch.setattr(sys, 'argv', ['install_indian_coastal_context_v1.py', *arguments])
    for key in ['GITHUB_ACTIONS', 'GITHUB_EVENT_NAME', 'GITHUB_REF']:monkeypatch.delenv(key, raising=False)
    for key, value in environment.items():monkeypatch.setenv(key, value)
    def forbidden(*args, **kwargs):pytest.fail('Disk, payload or Git access before explicit cloud opt-in')
    monkeypatch.setattr(install.shutil, 'disk_usage', forbidden)
    monkeypatch.setattr(install.subprocess, 'check_output', forbidden)
    monkeypatch.setattr(install.subprocess, 'run', forbidden)
    with pytest.raises(SystemExit) as error:install.main()
    assert error.value.code == 2


def compare_fixture():
    return {'status': 'ahead', 'base_commit': {'sha': install.delivery.SOURCE_COMMIT},
            'merge_base_commit': {'sha': install.delivery.SOURCE_COMMIT}, 'total_commits': 1,
            'commits': [{'sha': 'f' * 40}], 'files': [{'filename': install.REQUEST, 'status': 'added'}]}


@pytest.mark.parametrize('change', ['none', 'removed', 'scientific', 'duplicate', 'wrong_parent', 'wrong_head', 'truncated'])
def test_control_delta_is_source_only_and_complete(change):
    d = compare_fixture()
    if change == 'removed':d['files'][0]['status'] = 'removed'
    if change == 'scientific':d['files'].append({'filename': 'analysis/build_west_greenland_core_width_v1.py', 'status': 'modified'})
    if change == 'duplicate':d['files'].append(copy.deepcopy(d['files'][0]))
    if change == 'wrong_parent':d['merge_base_commit']['sha'] = '0' * 40
    if change == 'wrong_head':d['commits'][0]['sha'] = '0' * 40
    if change == 'truncated':d['total_commits'] = 2
    if change == 'none':install.verify_control_delta(d, 'f' * 40)
    else:
        with pytest.raises(ValueError):install.verify_control_delta(d, 'f' * 40)


def request_fixture():
    return {'schema': 'osw.indian-coastal-context.installation-request.v1',
        'source_run_id': install.delivery.SOURCE_RUN, 'source_commit': install.delivery.SOURCE_COMMIT,
        'packet_logical_sha256': install.delivery.PACKET, 'installation_workflow': install.WORKFLOW,
        'visual_review_file': install.REVIEW, 'native_rebuild': False, 'wasm_rebuild': False,
        'scientific_source_recomputation': False, 'main_merged': False, 'scientific_release_published': False,
        'presentation_run_id': 123, 'presentation_control_commit': 'f' * 40,
        'presentation_receipt_sha256': 'a' * 64, 'visual_review_sha256': 'b' * 64}


@pytest.mark.parametrize('change', ['none', 'source', 'packet', 'rebuild', 'boolean_type', 'review_missing', 'run_missing'])
def test_installation_request_cannot_change_review_or_science_scope(change):
    r = request_fixture()
    if change == 'source':r['source_run_id'] += 1
    if change == 'packet':r['packet_logical_sha256'] = '0' * 64
    if change == 'rebuild':r['native_rebuild'] = True
    if change == 'boolean_type':r['native_rebuild'] = 0
    if change == 'review_missing':r.pop('visual_review_sha256')
    if change == 'run_missing':r.pop('presentation_run_id')
    if change == 'none':install.verify_request(r)
    else:
        with pytest.raises(ValueError):install.verify_request(r)


def test_outputs_exclude_historical_parts_and_source_files(tmp_path):
    from query_packet import write_packet
    folder = tmp_path / 'almanac';folder.mkdir()
    packet = write_packet(folder / 'query-data.json', b'{"schema":"osw.query-bundle.v1"}\n')
    required = {install.PROOF, install.COVERAGE, install.PHASE}
    install.verify_outputs(required | {'almanac/' + packet['parts'][0]['path']}, packet)
    for extra in ['analysis/science.py', 'almanac/query-parts/old.bin']:
        with pytest.raises(ValueError):install.verify_outputs(required | {extra}, packet)
    with pytest.raises(ValueError):install.verify_outputs({install.PROOF}, packet)


def test_controller_change_is_exact_phase_recognition_only():
    before = b"assert phase in ('source-review-only-v1', 'indian-coastal-context-v1'), phase\n"
    after = before.replace(b"'indian-coastal-context-v1'), phase",
        b"'indian-coastal-context-v1', 'indian-coastal-card-presentation-v1', 'indian-coastal-context-install-v1'), phase")
    install.verify_phase_controller(before, after)
    for bad in [before, after + b'other change\n', after.replace(b'assert phase', b'assert True or phase')]:
        with pytest.raises(ValueError):install.verify_phase_controller(before, bad)
