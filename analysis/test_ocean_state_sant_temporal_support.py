import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("audit_ocean_state_sant_temporal_support.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_temporal_support", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_provider_metadata_receipt_binds_to_custodied_sources():
    payload = json.loads((ROOT / "research/ocean-state-sant-temporal-support-audit-2018.json").read_text(encoding="utf-8"))
    family = json.loads(MODULE.FAMILY.read_text(encoding="utf-8"))
    urls = MODULE.source_urls(family)
    MODULE.validate(payload)
    assert payload["source_family"]["sha256"] == MODULE.sha256(MODULE.FAMILY)
    for month in payload["months"]:
        assert {name: item["source_url"] for name, item in month["fields"].items()} == urls[month["month"]]
        assert all(item["time_bounds_attribute"] is None for item in month["fields"].values())
    feb = payload["months"][0]
    assert feb["month"] == "201802"
    assert feb["fields"]["sohtcbtm"]["interval_write_seconds"] == 31 * 86400
    assert "2018-02-15" in feb["fields"]["sohtcbtm"]["time_units"]


def test_temporal_gate_rejects_claimed_bounds_or_unmatched_field_time():
    payload = json.loads((ROOT / "research/ocean-state-sant-temporal-support-audit-2018.json").read_text(encoding="utf-8"))
    with_bounds = copy.deepcopy(payload)
    with_bounds["months"][0]["heat_content_has_time_bounds_variable"] = True
    with pytest.raises(ValueError):
        MODULE.validate(with_bounds)
    unmatched = copy.deepcopy(payload)
    unmatched["months"][0]["fields"]["vozocrtx"]["time_units"] = "seconds since 2018-02-16 00:00:00 UTC"
    with pytest.raises(ValueError):
        MODULE.validate(unmatched)


def test_das_parser_extracts_time_operation_without_inventing_bounds():
    das = '''Attributes { sohtcbtm { String online_operation "ave(x)"; Float32 interval_operation 1200.0; Float32 interval_write 2678400.0; String offline_operation "ave(x)"; } time_counter { String units "seconds since 2018-02-15 00:00:00 UTC"; String calendar "gregorian"; } }'''
    parsed = MODULE.parse_das(das, "sohtcbtm")
    assert parsed["time_bounds_attribute"] is None
    assert parsed["interval_write_seconds"] == 2678400.0
    assert parsed["online_operation"] == "ave(x)"
