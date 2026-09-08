import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "build_ocean_column_viewer.py"
DATA = ROOT / "column" / "data.js"


def load_builder():
    spec = importlib.util.spec_from_file_location("column_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_payload(path=DATA):
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.OSW_COLUMN_DATA = (.*);\n", text, flags=re.DOTALL)
    assert match
    return json.loads(match.group(1))


def test_column_viewer_data_contract():
    payload = load_payload()
    assert payload["schema"] == "osw-ocean-column-viewer-data-v1"
    assert payload["claim_stage"] == "reference geography and conceptual teaching overlays"
    assert len(payload["provinces"]) == 56
    assert len({item["code"] for item in payload["provinces"]}) == 56
    assert len(payload["column_address"]["bands"]) == 5
    assert [item["bottom_m"] for item in payload["teaching_columns"]] == [90, 4800, 8000]
    assert "not local bathymetry" in payload["boundary"]


def test_column_viewer_build_is_deterministic(tmp_path):
    builder = load_builder()
    output = tmp_path / "data.js"
    builder.build(output)
    assert output.read_bytes() == DATA.read_bytes()


def test_column_viewer_accessible_interaction_contract():
    html = (ROOT / "column" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "column" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "column" / "styles.css").read_text(encoding="utf-8")
    for token in ('id="province-select"', 'id="band-controls"', 'id="overlay-controls"', 'aria-live="polite"', 'role="img"', "Evidence boundary", "does not establish that the combination contains wet volume"):
        assert token in html
    for token in ("history.replaceState", 'event.key === "Enter"', "aria-pressed", "updateReadout", "not a detected physical regime", "occupancy at this depth is unverified", "overlaySentence"):
        assert token in app
    assert '.focus()' not in app
    assert "overflow-x:hidden" in html
    assert ".masthead{flex-wrap:wrap}" in html
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css
