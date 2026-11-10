"""Prove local export refusal before any full-packet/resource access."""
import sys
import pytest
import export_indian_coastal_context_candidate as exporter


@pytest.mark.parametrize('argv,cloud', [([], False), (['--cloud-candidate'], False), ([], True)])
def test_local_or_unrequested_export_refuses_before_any_payload_read(monkeypatch, argv, cloud):
    monkeypatch.setattr(sys, 'argv', ['export_indian_coastal_context_candidate.py', *argv])
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    if cloud:monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    def forbidden(*args):pytest.fail('Resource or packet access before cloud opt-in')
    monkeypatch.setattr(exporter, 'load_parent', forbidden)
    monkeypatch.setattr(exporter.shutil, 'disk_usage', forbidden)
    monkeypatch.setattr(exporter.context, 'evidence', forbidden)
    with pytest.raises(SystemExit) as error:exporter.main()
    assert error.value.code == 2


@pytest.mark.parametrize('disk,memory', [(2*1024**3, 8*1024**3), (8*1024**3, 5*1024**3), (8*1024**3, None)])
def test_insufficient_cloud_resources_reject(disk, memory):
    with pytest.raises(ValueError):
        exporter.require_cloud(True, environment={'GITHUB_ACTIONS': 'true'}, free_disk=disk, available_memory=memory)
