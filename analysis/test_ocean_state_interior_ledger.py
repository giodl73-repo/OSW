import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_ocean_state_interior_ledger.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_interior_ledger", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_ledger_regenerates_and_keeps_unknowns():
    committed_path = ROOT / "research/ocean-state-interior-ledger-sant-201808.json"
    committed = json.loads(committed_path.read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    assert committed["address"] == {"geometry_edition": "longhurst-v4-54", "province": "SANT", "depth_support": "0-200m"}
    assert committed["valid_time"] == "2018-08-01/P1M"
    assert committed["internal_links"] == []
    overlay = committed["overlays"][0]
    assert overlay["relation"] == "static_structure" and overlay["temporal_support"] == "static_reference"
    assert overlay["summary"]["water_volume_fraction_by_depth_band"]["bathypelagic"] == 0.658225
    assert {item["relation"] for item in committed["unknowns"]} == {"vertical_transfer", "lateral_interior_pathway", "interior_convergence", "transformation", "event_perturbation"}


def test_content_checksum_and_boundary_context_cannot_be_silently_joined():
    payload = MODULE.build()
    content = payload["contents"][0]
    source = ROOT / content["source_artifact"]
    assert content["source_artifact_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert payload["boundary_context"]["join_status"] == "not_joined_to_interior_account"
    assert "open 16-face" in payload["boundary_context"]["reason"]


def test_browser_derivative_matches_committed_ledger():
    source = (ROOT / "exchange/interior-ledger.js").read_text(encoding="utf-8")
    prefix = "window.OSW_STATE_INTERIOR_LEDGER = "
    assert source.startswith(prefix) and source.endswith(";\n")
    assert json.loads(source[len(prefix):-2]) == MODULE.build()


def test_validator_rejects_incompatible_internal_join_and_missing_unknown_reason():
    payload = MODULE.build()
    incompatible = copy.deepcopy(payload)
    incompatible["internal_links"] = [{"address": {**payload["address"], "depth_support": "200-1000m"}, "valid_time": payload["valid_time"]}]
    with pytest.raises(ValueError, match="incompatible"):
        MODULE.validate(incompatible)
    missing_reason = copy.deepcopy(payload)
    missing_reason["unknowns"][0].pop("reason")
    with pytest.raises(ValueError, match="unknowns"):
        MODULE.validate(missing_reason)


def test_validator_rejects_static_overlay_from_another_state():
    payload = MODULE.build()
    incompatible = copy.deepcopy(payload)
    incompatible["overlays"][0]["address"] = {**payload["address"], "province": "SSTC"}
    with pytest.raises(ValueError, match="static overlay address"):
        MODULE.validate(incompatible)
