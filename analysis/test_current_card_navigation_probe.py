"""Resource and sandbox checks for a diagnostic that never publishes."""
from pathlib import Path
import pytest
import probe_current_card_navigation as p


def test_local_probe_refuses_before_data_or_process_access(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    def forbidden(*args,**kwargs):pytest.fail('Local probe accessed saved data or started a server')
    monkeypatch.setattr(p,'verify_artifacts',forbidden)
    monkeypatch.setattr(p.subprocess,'Popen',forbidden)
    with pytest.raises(RuntimeError,match='cloud-only'):p.main()


@pytest.mark.parametrize('relative',['.','almanac','.pytest_cache','../outside-navigation-probe'])
def test_original_or_external_workspace_rejected(relative):
    with pytest.raises(ValueError):p.checked_site(p.ROOT/relative)


def test_owned_ignored_sandbox_path_allowed_without_reading_data():
    assert p.checked_site(p.ROOT/'.pytest_cache/navigation-probe/site')==p.ROOT/'.pytest_cache/navigation-probe/site'
