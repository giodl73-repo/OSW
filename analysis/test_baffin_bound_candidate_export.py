"""The full-packet command must refuse local execution before any packet read."""
import sys

import pytest
import export_baffin_bound_candidate as e


@pytest.mark.parametrize('argv,environment', [([],{}),(['--cloud-candidate'],{}),([] ,{'GITHUB_ACTIONS':'true'})])
def test_local_or_unrequested_export_refuses_before_resource_or_packet_reads(monkeypatch,argv,environment):
    monkeypatch.setattr(sys,'argv',['export_baffin_bound_candidate.py',*argv])
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    for key,value in environment.items():monkeypatch.setenv(key,value)
    def forbidden(*args):pytest.fail('Full packet/resource access before explicit cloud opt-in')
    monkeypatch.setattr(e,'load_parent',forbidden)
    monkeypatch.setattr(e.shutil,'disk_usage',forbidden)
    with pytest.raises(SystemExit) as error:e.main()
    assert error.value.code == 2


@pytest.mark.parametrize('disk,memory', [(2*1024**3,8*1024**3),(8*1024**3,5*1024**3),(8*1024**3,None)])
def test_cloud_resource_limits_reject(disk,memory):
    with pytest.raises(ValueError):
        e.require_cloud(True,environment={'GITHUB_ACTIONS':'true'},free_disk=disk,available_memory=memory)
