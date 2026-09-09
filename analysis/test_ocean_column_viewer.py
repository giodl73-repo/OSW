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
    assert "one grid cell" in payload["boundary"]
    assert "not a province mean" in payload["boundary"]
    assert sum(item["seed_measurement"]["cell_state"] == "wet" for item in payload["provinces"]) == 53
    assert payload["provenance"]["seed_source_release"] == "GEBCO_2026"
    assert all("tid_code" in item["seed_measurement"] for item in payload["provinces"])


def test_column_viewer_build_is_deterministic(tmp_path):
    builder = load_builder()
    output = tmp_path / "data.js"
    builder.build(output)
    assert output.read_bytes() == DATA.read_bytes()


def test_column_viewer_accessible_interaction_contract():
    html = (ROOT / "column" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "column" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "column" / "styles.css").read_text(encoding="utf-8")
    for token in ('id="province-select"', 'id="band-controls"', 'id="overlay-controls"', 'id="seed-status"', 'id="neighborhood-canvas"', 'id="footprint-canvas"', 'id="footprint-depth-profile"', 'id="footprint-profile-label"', 'id="footprint-map-label"', 'id="footprint-map-legend"', 'id="footprint-passport"', 'data-neighborhood-mode="depth"', 'data-neighborhood-mode="source"', 'data-footprint-profile="volume"', 'data-footprint-profile="seafloor"', 'data-footprint-map="family"', 'data-footprint-map="area"', 'data-footprint-map="volume"', 'data-footprint-map="depth"', 'data-footprint-map="floor"', 'aria-live="polite"', 'role="img"', "Evidence boundary", "not a province mean", 'src="neighborhoods.js"', 'src="province-footprints.js"', 'src="province-fingerprints.js"'):
        assert token in html
    for token in ("OSW_PROVINCE_FINGERPRINTS", "history.replaceState", 'event.key === "Enter"', "aria-pressed", "updateReadout", "renderNeighborhood", "renderFootprint", "renderPassport", "ranksFor", "rankColor", "floor_character", "substantial_seafloor_band_count", "volume_rank_advantage_over_area", "wet_area_fraction_by_seafloor_band", "water_volume_fraction_by_depth_band", "sampled_water_volume_km3", "not a detected physical regime", "does not reach this band", "bathymetry-truncated part", "not province-wide", "not the province", "overlaySentence"):
        assert token in app
    assert '.focus()' not in app
    assert "overflow-x:hidden" in html
    assert ".masthead{flex-wrap:wrap}" in html
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css
