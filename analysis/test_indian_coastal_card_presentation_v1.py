"""Small overlay corruption fixtures; no atlas data or browser is opened."""
import copy
import hashlib
import sys
import pytest
import indian_coastal_card_presentation_v1 as presentation


def parent():
    return {'schema': 'osw.query-engine-manifest.v1', 'engine': 'rust-osw-query-v1', 'abi_version': 1,
            'sha256': {presentation.UI: 'a' * 64, 'almanac/query-engine.wasm': 'b' * 64,
                       'almanac/query-data.json': 'c' * 64, 'almanac/index-data.json.gz': 'd' * 64}}


def overlay(p):
    return presentation.overlay_manifest(p, b'synthetic new display bytes',
        parent_manifest_sha='e' * 64, source_run_id=123, control_commit='f' * 40)


def test_overlay_preserves_every_data_and_compiled_code_pin_without_parent_mutation():
    p = parent();before = copy.deepcopy(p);updated = overlay(p)
    assert p == before
    assert {k: v for k, v in updated['sha256'].items() if k != presentation.UI} == {
        k: v for k, v in p['sha256'].items() if k != presentation.UI}
    assert updated['presentation_adjustment']['native_rebuild'] is False
    assert updated['presentation_adjustment']['wasm_rebuild'] is False


@pytest.mark.parametrize('change', ['data', 'wasm', 'source', 'added', 'engine', 'recompute'])
def test_more_than_display_adjustment_rejects(change):
    p = parent();updated = overlay(p)
    if change == 'data':updated['sha256']['almanac/query-data.json'] = '0' * 64
    if change == 'wasm':updated['sha256']['almanac/query-engine.wasm'] = '0' * 64
    if change == 'source':updated['presentation_adjustment']['changed_source_paths'].append('research/original.json')
    if change == 'added':updated['sha256']['almanac/extra.js'] = '0' * 64
    if change == 'engine':updated['engine'] = 'different'
    if change == 'recompute':updated['presentation_adjustment']['scientific_source_recomputation'] = True
    with pytest.raises(ValueError):presentation.validate_overlay(p, updated)


@pytest.mark.parametrize('path', ['../outside', '/absolute', 'C:/outside', 'a\\b', 'a/./b', 'a//b'])
def test_saved_source_path_cannot_leave_site(tmp_path, path):
    with pytest.raises(ValueError):presentation.local_path(tmp_path, path)


def test_saved_engine_source_and_payload_bytes_are_checked(tmp_path):
    paths = [presentation.UI, 'almanac/query-engine.wasm', 'almanac/query-data.json',
             'almanac/index-catalog.json', 'almanac/index-data.json.gz']
    pins = {}
    for name in paths:
        target = tmp_path / name;target.parent.mkdir(parents=True, exist_ok=True)
        raw = ('synthetic:' + name).encode();target.write_bytes(raw)
        pins[name] = hashlib.sha256(raw).hexdigest()
    manifest = {**parent(), 'sha256': pins}
    presentation.verify_files(tmp_path, manifest)
    (tmp_path / 'almanac/query-engine.wasm').write_bytes(b'changed')
    with pytest.raises(ValueError, match='changed'):presentation.verify_files(tmp_path, manifest)


@pytest.mark.parametrize('arguments,cloud', [([], False), (['--site', 'fixture', '--audit', 'fixture'], False),
                                         ([], True)])
def test_local_or_unrequested_presentation_cannot_open_files_or_browser(monkeypatch, arguments, cloud):
    import check_indian_coastal_card_presentation_v1 as checker
    monkeypatch.setattr(sys, 'argv', ['check_indian_coastal_card_presentation_v1.py', *arguments])
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    if cloud:monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setenv('GITHUB_REF', 'refs/heads/codex/current-measurement-gaps')
    def forbidden(*args):pytest.fail('Saved data or browser opened before cloud opt-in')
    monkeypatch.setattr(checker.delivery, 'verify_run', forbidden)
    monkeypatch.setattr(checker.subprocess, 'Popen', forbidden)
    with pytest.raises(SystemExit) as error:checker.main()
    assert error.value.code == 2
