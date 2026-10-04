import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_vertical_source_audit_rejects_all_direct_joins_and_preserves_bridge_contract():
    audit = json.loads((ROOT / "research/ocean-state-sant-vertical-process-source-audit-2026-09-12.json").read_text(encoding="utf-8"))
    assert audit["result"] == "no_directly_joinable_2018_native_vertical_process_source_identified"
    assert any(candidate["decision"] == "bridge_candidate_only_not_joinable" for candidate in audit["candidates"])
    assert any("native vertical velocity" in item for item in audit["join_contract"]["required"])
