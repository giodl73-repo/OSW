"""Small corruption fixtures; no saved packet or browser is opened."""
import copy
import pytest
import eacc_connection_presentation_v1 as method


def parent():
    return {'schema': 'osw.query-engine-manifest.v1', 'engine': 'rust-osw-query-v1',
            'abi_version': 1, 'sha256': {method.UI: 'a'*64, 'almanac/query-engine.wasm': 'b'*64,
            'almanac/query-data.json': 'c'*64}, 'prior_overlay': {'retain': True}}


def test_adds_only_diagram_and_changes_only_ui_with_no_input_mutation():
    original = parent(); before = copy.deepcopy(original)
    updated = method.overlay(original, b'new UI', b'new SVG', control_commit='e'*40)
    assert original == before
    assert updated['sha256']['almanac/query-engine.wasm'] == 'b'*64
    assert updated['sha256']['almanac/query-data.json'] == 'c'*64
    assert updated['prior_overlay'] == original['prior_overlay']
    assert updated[method.KEY]['new_scientific_records'] == 0


@pytest.mark.parametrize('case', ['wasm','data','old-overlay','extra-asset','remove-asset',
    'rebuild','source-record','scope','base','manifest'])
def test_corruption_rejects(case):
    original = parent()
    updated = method.overlay(original, b'new UI', b'new SVG', control_commit='e'*40)
    if case == 'wasm': updated['sha256']['almanac/query-engine.wasm'] = '0'*64
    elif case == 'data': updated['sha256']['almanac/query-data.json'] = '0'*64
    elif case == 'old-overlay': updated['prior_overlay'] = {}
    elif case == 'extra-asset': updated['sha256']['almanac/extra.js'] = '0'*64
    elif case == 'remove-asset': del updated['sha256'][method.FIGURE]
    elif case == 'rebuild': updated[method.KEY]['wasm_rebuild'] = True
    elif case == 'source-record': updated[method.KEY]['new_scientific_records'] = 1
    elif case == 'scope': updated[method.KEY]['changed_existing_paths'].append('data')
    elif case == 'base': updated[method.KEY]['base_commit'] = '0'*40
    else: updated[method.KEY]['parent_engine_manifest_sha256'] = '0'*64
    with pytest.raises(ValueError): method.validate(original, updated)


def test_requires_real_change_and_rejects_repeated_overlay():
    original = parent(); original['sha256'][method.UI] = method.digest(b'same')
    with pytest.raises(ValueError): method.overlay(original, b'same', b'SVG', control_commit='e'*40)
    original[method.KEY] = {}
    with pytest.raises(ValueError): method.overlay(original, b'new', b'SVG', control_commit='e'*40)


@pytest.mark.parametrize('cloud,args', [(False, []), (False, ['--site', 'fixture', '--output', 'fixture']), (True, [])])
def test_local_or_incomplete_invocation_refuses_before_data_access(monkeypatch, cloud, args):
    import sys
    import check_eacc_connection_presentation_v1 as checker
    monkeypatch.setattr(sys, 'argv', ['checker', *args])
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    if cloud: monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setenv('GITHUB_REF', 'refs/heads/codex/current-measurement-gaps')
    def forbidden(*a, **k): pytest.fail('Saved engine or browser opened before opt-in')
    monkeypatch.setattr(checker.method, 'verify_files', forbidden)
    monkeypatch.setattr(checker.subprocess, 'Popen', forbidden)
    with pytest.raises(SystemExit) as error: checker.main()
    assert error.value.code == 2
