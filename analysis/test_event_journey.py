import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVENT = ROOT / "event"


def run_node(source: str) -> str:
    return subprocess.run(
        ["node", "-e", source], cwd=ROOT, check=True, capture_output=True,
        text=True, encoding="utf-8"
    ).stdout.strip()


def test_event_journey_has_five_progressively_enhanced_scenes() -> None:
    html = (EVENT / "index.html").read_text(encoding="utf-8")
    app = (EVENT / "app.js").read_text(encoding="utf-8")
    assert 'role="tab"' not in html
    assert 'role="tabpanel"' not in html
    assert html.count("data-scene-panel=") == 5
    assert 'tablist.setAttribute("role", "tablist")' in app
    assert 'tab.setAttribute("role", "tab")' in app
    assert 'panel.setAttribute("role", "tabpanel")' in app
    assert 'aria-live="polite"' in html
    assert "What this does not establish" in html
    assert "No substitute value" in app
    assert "if (!response.ok) throw new Error" in app
    assert ").catch(function (error)" in app
    assert "Trace the sources" in html
    assert "prefers-reduced-motion" in (EVENT / "styles.css").read_text(encoding="utf-8")


def test_event_journey_local_links_resolve() -> None:
    html = (EVENT / "index.html").read_text(encoding="utf-8")
    for target in re.findall(r'(?:href|src)="([^"]+)"', html):
        if target.startswith(("http://", "https://", "#")) or not target:
            continue
        path = (EVENT / target.split("#", 1)[0].split("?", 1)[0]).resolve()
        assert path.exists(), target


def test_scene_manifest_reads_exact_committed_values() -> None:
    script = r"""
const fs=require('fs'), api=require('./event/scenes.js');
const out={};
for(const scene of api.SCENES){
  const payloads={};
  for(const source of scene.sources) payloads[source[0]]=JSON.parse(fs.readFileSync(source[1].replace('../',''),'utf8'));
  out[scene.id]=api.model(scene,payloads);
}
process.stdout.write(JSON.stringify(out));
"""
    views = json.loads(run_node(script))
    assert list(views) == ["event", "surface", "boundary", "column", "motion"]
    assert [item["value"] for item in views["event"]["stats"]] == ["21 days", "49439.2 km²"]
    assert [item["value"] for item in views["surface"]["stats"]] == ["-0.13 °C", "+0.16 °C"]
    assert views["boundary"]["stats"][0]["value"] == "+112.61 W m⁻²"
    assert [item["value"] for item in views["column"]["stats"]] == ["+236.03 W m⁻²", "47.7 %"]
    assert [item["value"] for item in views["motion"]["stats"]] == ["+171.21 W m⁻²", "72.5 %", "-47.79 W m⁻²"]
    assert all(view["limitation"] and view["finding"] and view["time"] for view in views.values())


def test_scene_contract_rejects_missing_fields_and_wrong_schemas() -> None:
    result = run_node(r"""
const api=require('./event/scenes.js');
const scene=api.sceneById('motion');
const broken={d14:{schema:scene.sources[0][2],bridge_evaluation:{},boundary:'bounded'}};
try { api.model(scene,broken); process.stdout.write('unsafe'); }
catch(error) { process.stdout.write(error.message); }
""")
    assert result.startswith("Missing selector:")

    result = run_node(r"""
const api=require('./event/scenes.js');
const scene=api.sceneById('motion');
try { api.validate(scene,{d14:{schema:'invented'}}); process.stdout.write('unsafe'); }
catch(error) { process.stdout.write(error.message); }
""")
    assert result.startswith("Unexpected schema")


def test_invalid_scene_falls_back_to_event_and_app_replaces_url() -> None:
    assert run_node("const a=require('./event/scenes.js');process.stdout.write(a.sceneById('invented').id)") == "event"
    app = (EVENT / "app.js").read_text(encoding="utf-8")
    assert "requestedSceneIsValid" in app
    assert "replace: !requestedSceneIsValid" in app


def test_headline_numbers_are_not_copied_into_interface_sources() -> None:
    product_source = (EVENT / "index.html").read_text(encoding="utf-8") + (EVENT / "app.js").read_text(encoding="utf-8") + (EVENT / "scenes.js").read_text(encoding="utf-8")
    for value in ("112.61", "236.03", "171.21", "72.5", "-47.79", "49439.2"):
        assert value not in product_source


def test_readme_exposes_three_primary_entrances() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "| Explore the ocean | Follow heat | Inspect evidence |" in readme
    assert "[Follow one warm event →](event/)" in readme


def test_atlas_exposes_event_journey_in_one_action() -> None:
    atlas = (ROOT / "atlas" / "index.html").read_text(encoding="utf-8")
    assert '<a href="../event/">Follow heat</a>' in atlas
    workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    assert "node --check event/scenes.js" in workflow
    assert "node --check event/app.js" in workflow
