from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_atlas_evidence_filter_is_explicit_and_url_addressable() -> None:
    html = (ROOT / "atlas/index.html").read_text(encoding="utf-8")
    app = (ROOT / "atlas/app.js").read_text(encoding="utf-8")
    assert 'id="filter-evidence"' in html
    assert 'href="../research/ocean-object-evidence-receipts.json"' in html
    for token in ("conceptual", "observed", "derived", "model-screen", "sensitivity", "unresolved"):
        assert f'value="{token}"' in html
    assert 'function evidenceToken(zone)' in app
    assert '["evidence", "#filter-evidence"]' in app


def test_event_and_exchange_keep_receipts_and_evidence_in_reading_order() -> None:
    event = (ROOT / "event/index.html").read_text(encoding="utf-8")
    exchange = (ROOT / "exchange/index.html").read_text(encoding="utf-8")
    assert 'id="scene-evidence"' in event
    assert 'id="receipt-link"' in event
    assert 'Current evidence' in exchange
    assert 'Download the complete receipt' in exchange
