"""Ensure the delivery browser gate respects the local resource hold."""
import pytest
import test_baffin_bound_browser as browser


def test_local_delivery_gate_refuses_before_reading_contract_or_starting_process(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    def forbidden(*args,**kwargs):
        pytest.fail('Local browser gate accessed data or started a process')
    monkeypatch.setattr(browser.a,'read',forbidden)
    monkeypatch.setattr(browser.subprocess,'run',forbidden)
    with pytest.raises(RuntimeError,match='local browsers remain held'):
        browser.main()
