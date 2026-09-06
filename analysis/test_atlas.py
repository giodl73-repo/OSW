import csv
import pathlib
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

from validate_feature_geometry import validate_register

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "atlas" / "app.js"
HTML = ROOT / "atlas" / "index.html"
CSS = ROOT / "atlas" / "styles.css"
RESEARCH_HTML = ROOT / "research" / "index.html"
REFERENCES = ROOT / "REFERENCES.bib"

class AtlasTests(unittest.TestCase):
    def test_public_surface_files_exist(self):
        for path in (APP, HTML, CSS, RESEARCH_HTML, REFERENCES, ROOT / "REVIEW-GUIDE.md", ROOT / "PREVIEW-STATUS.md", ROOT / "research" / "styles.css", ROOT / "research" / "zone-catalog.csv", ROOT / "research" / "claims-ledger.csv", ROOT / "atlas" / "README.md", ROOT / "projections" / "index.html", ROOT / "projections" / "styles.css", ROOT / "figures" / "osw-fluid-geography.svg", ROOT / "figures" / "osw-fluid-geography-interactive.svg", ROOT / "figures" / "osw-fluid-geography-water-first.svg", ROOT / "figures" / "osw-fluid-geography-water-first-interactive.svg", *(ROOT / "figures" / f"osw-projection-{slug}.svg" for slug in ("spilhaus", "oceanic-goode", "pelagos")), ROOT / "atlas" / "data" / "oisst-2026-08-01.js", ROOT / "atlas" / "data" / "oisst-anomaly-2026-08-01.js", ROOT / "atlas" / "data" / "oisst-error-2026-08-01.js", *(ROOT / "atlas" / "data" / f"argo-temperature-anomaly-{pressure}dbar-2026-07.js" for pressure in (10, 300, 700, 1000))):
            self.assertTrue(path.is_file(), path)

    def test_zone_catalog_has_unique_numbered_records(self):
        source = APP.read_text(encoding="utf-8")
        ids = re.findall(r'id: "([a-z0-9-]+)"', source)
        numbers = [int(value) for value in re.findall(r'\bn: (\d+),', source)]
        self.assertEqual(36, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(list(range(1, 37)), numbers)

    def test_zone_records_declare_measurement_boundaries(self):
        source = APP.read_text(encoding="utf-8")
        for field in ("boundary", "depth", "evidence", "source"):
            self.assertEqual(36, len(re.findall(rf'\b{field}: "', source)), field)

    def test_html_has_accessibility_and_status_cues(self):
        source = HTML.read_text(encoding="utf-8")
        for token in ('aria-live="polite"', 'aria-label="Ocean geography lens"', "ATLAS 10 · DEPTH LADDER", "conceptual, overlapping geography"):
            self.assertIn(token, source)

    def test_readme_and_atlas_expose_clear_entry_routes(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        html = HTML.read_text(encoding="utf-8")
        for token in ("## Enter the Ocean States", "Ocean States of the World", "Explore 56 ocean states, 36 shaped features, and the Atlas 10 depth ladder", "Open the full annotated map", "Read the field guide", "Open the research note", "Check every source"):
            self.assertIn(token, readme)
        for target in ("../figures/osw-fluid-geography.svg", "../HEATMASS.md", "../research/", "README.md", "../SOURCE-REGISTER.md"):
            self.assertIn(f'href="{target}"', html)

    def test_osw_rebrand_preserves_versioned_observation_interfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertIn("`OSW` always expands", readme)
        self.assertIn("The Ocean States", readme)
        self.assertIn("backward compatibility", readme)
        for token in ("window.OCEANLINES_OISST", "window.OCEANLINES_ARGO_TEMPERATURE_ANOMALY", 'oceanlines.oisst.snapshot.v2'):
            self.assertIn(token, app)
        for token in ("window.OSW_RELATION_MATRIX", "window.OSW_RELATION_METHOD", "window.OSW_RELATION_SMOKE"):
            self.assertIn(token, app)

    def test_research_note_separates_claims_and_records_data_receipts(self):
        source = RESEARCH_HTML.read_text(encoding="utf-8")
        styles = (ROOT / "research" / "styles.css").read_text(encoding="utf-8")
        for token in ("What can be concluded now?", "Does not establish", "What exact bytes are displayed?", "Which papers carry the argument?", "England et al. (2017)", "Goldner, Herold &amp; Huber (2014)", "Roemmich &amp; Gilson (2009)", "10.25921/RE9P-PT57", "54fde8766119da6856fff827b64946626eae3f61959792f962f296efb5baacd3", "a6756b88ecfe5e3c0307b7566ba142e3f9ddb8ebaa8823a5d08f9d3a3a1529e2", "24ae585b4b591b19d7b360fe8df3f9620e28f9754e8aa3e21bcb0860bc864ba6", "5a19dc77aaccecfd7e6aec34e80e42e1cbd83642c3f08a94d98c7018f631bb5c", "does not replace external scientific peer review"):
            self.assertIn(token, source)
        for target in re.findall(r'(?:href|src)="(\.\.?/[^"#]+)"', source):
            self.assertTrue((RESEARCH_HTML.parent / target).resolve().exists(), target)
        for token in ("@media print", "@page { size: A4", "break-after: page", "break-before: page", "print-color-adjust"):
            self.assertIn(token, styles)

    def test_corrected_primary_source_attributions_are_preserved(self):
        source_register = (ROOT / "SOURCE-REGISTER.md").read_text(encoding="utf-8")
        for token in ("England et al. 2017", "Hodel et al. 2021", "Rosevear et al. 2025"):
            self.assertIn(token, source_register)
        for stale in ("Hutchinson et al. 2017", "Touzeau et al. 2021", "Jenkins 2025"):
            self.assertNotIn(stale, source_register)

    def test_bibliography_and_optional_review_handoff_are_complete(self):
        bibliography = REFERENCES.read_text(encoding="utf-8")
        review = (ROOT / "REVIEW-GUIDE.md").read_text(encoding="utf-8")
        entries = re.findall(r"^@article\{([^,]+),", bibliography, re.MULTILINE)
        dois = re.findall(r"^  doi\s+= \{([^}]+)\}", bibliography, re.MULTILINE)
        self.assertEqual(16, len(entries))
        self.assertEqual(16, len(set(entries)))
        self.assertEqual(16, len(dois))
        self.assertEqual(16, len(set(value.lower() for value in dois)))
        self.assertIn('href="../REFERENCES.bib" download', RESEARCH_HTML.read_text(encoding="utf-8"))
        for token in ("no expectation of endorsement", "not requesting public association", "Any one of these is enough"):
            self.assertIn(token, review)

    def test_machine_readable_research_exports_match_the_atlas_contract(self):
        with (ROOT / "research" / "zone-catalog.csv").open(encoding="utf-8", newline="") as source:
            zones = list(csv.DictReader(source))
        with (ROOT / "research" / "claims-ledger.csv").open(encoding="utf-8", newline="") as source:
            claims = list(csv.DictReader(source))
        app = APP.read_text(encoding="utf-8")
        app_pairs = re.findall(r'id: "([a-z0-9-]+)", n: \d+, name: "([^"]+)"', app)
        self.assertEqual(app_pairs, [(zone["id"], zone["name"]) for zone in zones])
        self.assertEqual([str(value) for value in range(1, 37)], [zone["number"] for zone in zones])
        self.assertTrue(all(zone["lens"] and zone["depth_class"] and zone["properties"] and zone["basis"] for zone in zones))
        self.assertTrue(all(zone["inferential_boundary"] and zone["primary_or_register_source"] for zone in zones))
        self.assertTrue(all("·" not in zone["evidence_class"] for zone in zones))
        self.assertEqual("O18", zones[0]["source_ids"])
        self.assertEqual(["C1", "C2", "C3", "C4"], [claim["claim_id"] for claim in claims])
        self.assertTrue(all(claim["does_not_establish"] and claim["references"] for claim in claims))
        self.assertIn("gateway-only causation", claims[-1]["does_not_establish"])

    def test_preview_status_distinguishes_private_branch_from_public_release(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        status = (ROOT / "PREVIEW-STATUS.md").read_text(encoding="utf-8")
        checklist = (ROOT / "PUBLICATION-CHECKLIST.md").read_text(encoding="utf-8")
        self.assertIn("released Atlas 07", readme)
        self.assertIn("publicly visible review branch", readme)
        self.assertIn("APPROVED REVIEW PREVIEW; NOT RELEASED", readme)
        for token in ("visible on the pushed", "have not replaced the released Atlas 07", "Still not present", "Decisions deliberately still open"):
            self.assertIn(token, status)
        self.assertIn("- [ ] Obtain owner visual approval", checklist)
        self.assertIn("- [ ] Decide whether to promote", checklist)
        self.assertIn("Atlas 09 RG Argo 700 dbar anomaly", status)
        self.assertIn("ef6662e", status)
        self.assertIn("owner visual review open", status.lower())
        self.assertIn("Atlas 10 RG Argo depth ladder", status)
        self.assertIn("2756f1e", status)

    def test_preview_has_progressive_disclosure_and_mobile_zone_directory(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        for token in ('id="map-insight"', 'class="ring-workbench"', 'class="advanced-diagnostics"', "Inspect the paired rings", "Open polar mirrors and the latitude continuity ladder", 'id="zone-directory-list"', "Open the full-size province map"):
            self.assertIn(token, html)
        for token in ("list.append(item)", "scrollIntoView"):
            self.assertIn(token, app)
        self.assertIn("OSW Atlas 10 Preview", html)
        self.assertIn("zoneMatches", app)
        self.assertIn(".atlas-shell.observed-mode .zone-panel", css)

    def test_observed_map_has_reference_labels_and_three_tick_legend(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ('id="map-reference-labels"', "PACIFIC", "ATLANTIC", "INDIAN", "EQUATOR", 'id="scale-mid"'):
            self.assertIn(token, html)
        for token in ('"0°C baseline"', '"0.35°C"', '"15°C"'):
            self.assertIn(token, app)

    def test_preview_replaces_false_precision_claim_and_separates_nearby_markers(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertNotIn("false precision", html.lower())
        self.assertIn("Limits</strong> stated beside every view", html)
        self.assertIn("geometry comparison, not physical equivalence", html)
        self.assertIn('id: "indonesian-throughflow"', app)
        self.assertIn("x: 80.5, y: 46.2", app)

    def test_observed_map_declares_projection_and_text_equivalent(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ("Equirectangular display", "antimeridian", "Non-color map summary", 'aria-describedby="map-a11y-summary projection-note"'):
            self.assertIn(token, html)
        for token in ("renderTextSummary", "warmer", "cooler", "latitudeBands"):
            self.assertIn(token, app)

    def test_conceptual_boundaries_are_explicitly_permeable(self):
        html = HTML.read_text(encoding="utf-8")
        figure = (ROOT / "figures" / "osw-fluid-geography.svg").read_text(encoding="utf-8")
        self.assertIn("schematic geographic indexes", html)
        self.assertIn("schematic, permeable, and moving rather than measured boundaries", figure)

    def test_conceptual_map_uses_pinned_natural_earth_geometry(self):
        html = HTML.read_text(encoding="utf-8")
        figure = (ROOT / "figures" / "osw-fluid-geography.svg").read_text(encoding="utf-8")
        interactive_figure = (ROOT / "figures" / "osw-province-atlas-interactive.svg").read_text(encoding="utf-8")
        builder = (ROOT / "analysis" / "build_province_cartogram.py").read_text(encoding="utf-8")
        self.assertIn("osw-province-atlas-interactive.svg", html)
        self.assertIn("ca96624a56bd078437bca8184e78163e5039ad19", figure)
        self.assertIn("9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9", builder)
        self.assertEqual(12, figure.count('class="callout"'))
        self.assertEqual(56, interactive_figure.count('class="province '))
        self.assertIn('data-code="ALSK"', interactive_figure)

    def test_province_ground_is_selectable_zoomable_and_shared_by_all_modes(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        for token in ('id="province-select"', 'id="province-reset"', 'id="map-viewport"', "56 APPROXIMATE OCEAN STATES", 'aria-live="polite"'):
            self.assertIn(token, html)
        for token in ("loadProvinceMap", "selectProvince", "applyMapZoom", "provinceFeatureMatches", 'url.searchParams.set("province"'):
            self.assertIn(token, app)
        for token in (".province-map-host.observed-overlay", ".feature-shape-host", ".map-viewport"):
            self.assertIn(token, css)

    def test_numbered_map_markers_are_replaced_by_selectable_feature_shapes(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        overlay = (ROOT / "figures" / "osw-atlas-feature-shapes.svg").read_text(encoding="utf-8")
        builder = (ROOT / "analysis" / "build_atlas_feature_overlay.py").read_text(encoding="utf-8")
        self.assertIn('id="feature-shape-host"', html)
        self.assertEqual(36, overlay.count('class="feature-shape"'))
        for token in ("loadFeatureShapes", "selectable feature shapes", "Shapes are schematic geographic indexes"):
            self.assertIn(token, app + overlay)
        for feature_id in ("indo-pacific-warm-pool", "gulf-stream", "antarctic-polar-front", "mid-atlantic-ridge", "sargasso-sea"):
            self.assertIn(f'data-id="{feature_id}"', overlay)
        self.assertNotIn('button.className = "marker"', app)
        self.assertIn("The first twelve geometries preserve", builder)

    def test_feature_shapes_use_character_rich_mechanism_grammar(self):
        figure_path = ROOT / "figures" / "osw-atlas-feature-shapes.svg"
        overlay = figure_path.read_text(encoding="utf-8")
        ET.parse(figure_path)
        for token in (
            'class="water-branch"', 'class="gyre-spine"',
            'class="front-companion"', 'class="gate-section"',
            'class="ridge-flank"', 'class="trench-teeth"',
            'class="oxygen-core"', 'class="sargasso-boundary"',
        ):
            self.assertIn(token, overlay)
        self.assertNotIn('<ellipse class="gyre"', overlay)
        self.assertGreaterEqual(overlay.count('class="hit"'), 17)
        self.assertEqual(36, overlay.count('tabindex="0" role="button"'))
        self.assertEqual(36, overlay.count('aria-label="Select '))

    def test_feature_shapes_subtract_the_exact_province_map_land(self):
        overlay_path = ROOT / "figures" / "osw-atlas-feature-shapes.svg"
        province_path = ROOT / "figures" / "osw-province-atlas-interactive.svg"
        overlay = overlay_path.read_text(encoding="utf-8")
        namespace = "{http://www.w3.org/2000/svg}"
        overlay_root = ET.parse(overlay_path).getroot()
        province_root = ET.parse(province_path).getroot()
        overlay_land = next(
            element.attrib["d"] for element in overlay_root.iter(f"{namespace}path")
            if element.attrib.get("fill") == "black" and element.attrib.get("fill-rule") == "evenodd"
        )
        province_land = next(
            element.attrib["d"] for element in province_root.iter(f"{namespace}path")
            if element.attrib.get("class") == "land-outline"
        )
        self.assertEqual(province_land, overlay_land)
        self.assertIn('id="feature-ocean-only"', overlay)
        self.assertIn('mask="url(#feature-ocean-only)"', overlay)

    def test_relational_atlas_uses_sampled_shape_overlap_not_centroids(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        for token in ('id="relation-panel"', 'id="relation-overlaps"', 'id="relation-near"', 'id="relation-export"'):
            self.assertIn(token, html)
        for token in ("rendered-overlap-1", "classifyRenderedOverlap", "sampledPairHit", "near-contact", "exportRelationMatrix", "2016"):
            self.assertIn(token, app)
        self.assertNotIn("zone.x / 100 * 1600", app)
        for token in (".feature-shape.relation-muted", ".province.related", ".province.near-contact"):
            self.assertIn(token, css)
        fixture = (ROOT / "atlas" / "data" / "relation-smoke-fixture.js").read_text(encoding="utf-8")
        for token in ("gulf-stream", "GFST", "kuroshio", "KURO", "drake-passage", "FKLD", "antarctic-circumpolar-current", "ANTA"):
            self.assertIn(token, fixture)
        self.assertIn("verifyRelationSmokeFixture", app)

    def test_heat_continents_have_coastlike_shapes_distinct_from_blobs(self):
        builder = (ROOT / "analysis" / "build_fluid_geography.py").read_text(encoding="utf-8")
        figure = (ROOT / "figures" / "osw-fluid-geography.svg").read_text(encoding="utf-8")
        self.assertIn('id="indo-pacific-heat-continent"', builder)
        self.assertIn('id="western-hemisphere-heat-continent"', builder)
        self.assertGreaterEqual(figure.count('class="heat-continent"'), 3)
        self.assertGreaterEqual(figure.count('class="heat-shelf"'), 3)
        self.assertIn('<ellipse cx="205" cy="285"', figure)
        self.assertNotIn('<ellipse cx="1345" cy="442"', figure)

    def test_water_first_view_changes_emphasis_not_fluid_geography(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        reference = (ROOT / "figures" / "osw-fluid-geography-interactive.svg").read_text(encoding="utf-8")
        water_first = (ROOT / "figures" / "osw-fluid-geography-water-first-interactive.svg").read_text(encoding="utf-8")
        self.assertIn('data-conceptual-view="water-first"', html)
        self.assertIn('url.searchParams.set("view", currentConceptualView)', app)
        self.assertIn("WATER-FIRST", water_first)
        self.assertIn("fill:url(#ocean); stroke:#9ab8b8; stroke-opacity:.24", water_first)
        self.assertIn("fill:#182d31; stroke:#799395", reference)
        for feature in ('id="indo-pacific-heat-continent"', '<ellipse cx="205" cy="285"', 'class="current"', 'class="gate"'):
            self.assertEqual(reference.count(feature), water_first.count(feature), feature)

    def test_three_conceptual_grounds_labels_zoom_and_evidence_are_explicit(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        for token in ('data-conceptual-view="reference"', 'data-conceptual-view="water-first"', 'data-conceptual-view="shape-first"', 'id="feature-zoom"', 'id="evidence-badge"', "Evidence type qualifies"):
            self.assertIn(token, html)
        for token in ("renderFeatureLabels", "featureMapName", "zoomToSelectedFeature", 'url.searchParams.set("feature"', "featureView"):
            self.assertIn(token, app)
        for token in (".province-map-host.shape-only", ".feature-label-leader", '.evidence-badge[data-evidence="modeled-mixed"]'):
            self.assertIn(token, css)

    def test_feature_overlay_declares_clearance_gate_exemptions_and_seams(self):
        overlay = (ROOT / "figures" / "osw-atlas-feature-shapes.svg").read_text(encoding="utf-8")
        builder = (ROOT / "analysis" / "build_atlas_feature_overlay.py").read_text(encoding="utf-8")
        self.assertIn('id="feature-ocean-gates"', overlay)
        self.assertIn('stroke-width="10"', overlay)
        self.assertIn('mask="url(#feature-ocean-gates)"', overlay)
        self.assertEqual(7, overlay.count('data-seam="antimeridian"'))
        self.assertEqual(7, overlay.count('class="seam-continuation"'))
        for feature_id in ("drake-passage", "indonesian-throughflow", "mediterranean-outflow-water", "red-sea-water"):
            self.assertIn(f'"{feature_id}"', builder)

    def test_feature_geometry_admission_register_is_complete_and_rejects_promotion(self):
        register = ROOT / "research" / "feature-geometry-register.csv"
        schema = ROOT / "research" / "feature-geometry-contract.schema.json"
        with register.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(36, len(rows))
        self.assertEqual([], validate_register(register))
        self.assertIn('"geometry_basis"', schema.read_text(encoding="utf-8"))
        rows[0]["feature_id"] = "unknown-feature"
        rows[1]["license_id"] = ""
        rows[2]["reviewer_status"] = "admitted"
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False) as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            candidate = pathlib.Path(handle.name)
        try:
            errors = validate_register(candidate)
        finally:
            candidate.unlink(missing_ok=True)
        self.assertTrue(any("unknown feature ID" in error for error in errors))
        self.assertTrue(any("missing license_id" in error for error in errors))
        self.assertTrue(any("illustrative geometry cannot be admitted" in error for error in errors))

    def test_projection_lab_compares_one_overlay_and_declares_pelagos_status(self):
        page = (ROOT / "projections" / "index.html").read_text(encoding="utf-8")
        builder = (ROOT / "analysis" / "build_projection_bakeoff.py").read_text(encoding="utf-8")
        source_register = (ROOT / "SOURCE-REGISTER.md").read_text(encoding="utf-8")
        figures = [(ROOT / "figures" / f"osw-projection-{slug}.svg").read_text(encoding="utf-8") for slug in ("spilhaus", "oceanic-goode", "equal-earth", "pelagos")]
        for token in ("Spilhaus", "Oceanic Goode", "Equal Earth", "PELAGOS", "HEATPLATES", "not a newly derived projection equation", "+proj=laea +lat_0=-20 +lon_0=-165 +R=1"):
            self.assertIn(token, page)
        for token in ("adams_ws2", "+proj=igh_o +lon_0=-160", "+proj=eqearth +lon_0=-165", "+proj=laea +lat_0=-20 +lon_0=-165", "EXPECTED_SOURCE_SHA256"):
            self.assertIn(token, builder)
        for token in ("P1", "P2", "P3", "P4", "new center-and-edge policy"):
            self.assertIn(token, source_register)
        for figure in figures:
            self.assertIn("9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9", figure)
            for feature in ('class="heatmass"', 'class="anomaly"', 'class="current"', 'class="acc"', 'class="buried"', 'class="gate"'):
                self.assertIn(feature, figure)
            self.assertGreaterEqual(figure.count('class="heatmass"'), 3)
            self.assertGreaterEqual(figure.count('class="shelf"'), 3)
            self.assertNotIn("stroke-width:45", figure)

    def test_state_projection_bakeoff_transforms_the_same_56_state_system(self):
        page = (ROOT / "projections" / "index.html").read_text(encoding="utf-8")
        builder = (ROOT / "analysis" / "build_projection_bakeoff.py").read_text(encoding="utf-8")
        source_register = (ROOT / "SOURCE-REGISTER.md").read_text(encoding="utf-8")
        mollweide = (ROOT / "figures" / "osw-state-projection-mollweide-oceanic.svg").read_text(encoding="utf-8")
        oblique = (ROOT / "figures" / "osw-state-projection-oblique-cea.svg").read_text(encoding="utf-8")
        for figure in (mollweide, oblique):
            self.assertEqual(56, figure.count('class="province '))
            for token in ('class="realm-boundaries"', 'class="realm-casing"', 'class="region-boundaries"', 'class="region-casing"', 'class="land"', "same white-land treatment", "not published Longhurst boundaries", "SCHEMATIC · PROVISIONAL", "22 contiguous schematic regions", "connected before land masking and projection interruption"):
                self.assertIn(token.lower(), figure.lower())
        for slug in ("mollweide-oceanic", "oblique-cea"):
            no_hairlines = (ROOT / "figures" / f"osw-state-projection-{slug}-no-hairlines.svg").read_text(encoding="utf-8")
            self.assertEqual(56, no_hairlines.count('class="province '))
            self.assertIn("stroke:#4e79a7", no_hairlines)
            self.assertIn("STATE HAIRLINES OFF", no_hairlines)
        for token in ("STATE PROJECTION BAKEOFF", "Oceanic Mollweide", "Oblique Ocean Strip", "Drake-to-Indonesia", "leading projection for the Ocean States view", "LEADING", 'data-state-lines="on"', 'data-state-lines="off"', "data-lines-off-src"):
            self.assertIn(token, page)
        for token in ("POLAR REALM · EQUAL-AREA TOP-DOWN", "Arctic–Atlantic Polar", "North Pacific Polar", "Antarctic Polar", 'id="north-polar-clip"', 'id="south-polar-clip"', "48°N–90°N", "45°S–90°S", "+proj=laea +lat_0=90", "+proj=laea +lat_0=-90"):
            self.assertIn(token, mollweide)
        for token in ("REALM", "SCHEMATIC REGION", "STATE BORDER", "WHITE LAND = GEOGRAPHIC ANCHOR"):
            self.assertIn(token, mollweide)
        self.assertIn('width="1200" height="1360"', mollweide)
        for token in ("+proj=imoll_o +lon_0=-160", "+proj=ocea +lat_1=-56 +lon_1=-68 +lat_2=-3 +lon_2=123", "oceanic_mollweide_pieces"):
            self.assertIn(token, builder)
        for token in ("P6", "P7", "documented zone limits", "two-point axis"):
            self.assertIn(token, source_register)
        history = (ROOT / "HISTORY.md").read_text(encoding="utf-8")
        self.assertIn("Oceanic Mollweide wins the state map", history)
        self.assertIn("The third seminal moment", history)
        self.assertIn("Complete surface identity", history)
        self.assertIn("Coast-owned form", history)
        self.assertIn("An ocean-state world map", history)
        self.assertIn("PELAGOS retains its separate role", history)

    def test_observational_fields_run_through_one_ocean_state_projection(self):
        page = (ROOT / "projections" / "index.html").read_text(encoding="utf-8")
        builder = (ROOT / "analysis" / "build_state_data_views.py").read_text(encoding="utf-8")
        slugs = ("sst", "sst-anomaly", "sst-error", "argo-10", "argo-300", "argo-700", "argo-1000")
        figures = {
            slug: (ROOT / "figures" / f"osw-state-data-{slug}.svg").read_text(encoding="utf-8")
            for slug in slugs
        }
        self.assertEqual(7, len(figures))
        for slug, figure in figures.items():
            self.assertIn(f'data-view="{slug}"', figure)
            self.assertIn('data-source-grid="direct"', figure)
            self.assertIn('data-state-count="56"', figure)
            for token in ("DATA PRIMARY · STATES REFERENCE", "DIRECT GRID PROJECTION", "NO STATE AGGREGATION", "POLAR MIRRORS · SAME FIELD", "+proj=imoll_o +lon_0=-160", "provisional osw-regions-v0.1"):
                self.assertIn(token.lower(), figure.lower())
            self.assertIn('class="data-field"', figure)
            self.assertIn('class="state-lines"', figure)
            self.assertIn('class="region-lines"', figure)
            self.assertIn('class="realm-lines"', figure)
        self.assertIn("1971–2000", figures["sst-anomaly"])
        self.assertIn("not forecast error", figures["sst-error"].lower())
        for slug in ("argo-10", "argo-300", "argo-700", "argo-1000"):
            self.assertIn("64.5°S", figures[slug])
            self.assertIn("outside coverage", figures[slug])
        for token in ("EXPERIMENT 05 · DATA THROUGH THE STATES", "Now make the map carry evidence.", 'id="state-data-image"', 'data-state-data="sst"', 'data-state-data="argo-1000"', "No value is averaged by state"):
            self.assertIn(token, page)
        for token in ("TEMPERATURE_PALETTE", "ANOMALY_PALETTE", "ERROR_PALETTE", "grouped_main_field", "grouped_polar_field", "EXPECTED_SOURCE_SHA256"):
            self.assertIn(token, builder)

    def test_heatplates_prioritize_shape_without_implying_cross_panel_area(self):
        page = (ROOT / "projections" / "index.html").read_text(encoding="utf-8")
        figure_path = ROOT / "figures" / "osw-heatplates.svg"
        equal_earth_path = ROOT / "figures" / "osw-projection-equal-earth.svg"
        self.assertTrue(figure_path.is_file())
        self.assertTrue(equal_earth_path.is_file())
        figure = figure_path.read_text(encoding="utf-8")
        # Six panels; the dateline-crossing Indo-Pacific footprint is emitted as
        # two clipped paths, so region-path count is intentionally greater.
        self.assertGreaterEqual(figure.count('class="plate-region'), 6)
        for token in ("HEATPLATES", "PANEL-SPECIFIC ZOOM", "DO NOT COMPARE FOOTPRINT AREA ACROSS PANELS", "not observed thresholds"):
            self.assertIn(token.lower(), (figure + page).lower())
        for title in ("INDO-PACIFIC WARM POOL", "WESTERN WARM POOL", "NORTHEAST PACIFIC BLOB", "EL NIÑO TONGUE", "ATLANTIC WATER / ARCTIC", "CIRCUMPOLAR DEEP WATER"):
            self.assertIn(title, figure)

    def test_province_atlas_exposes_all_56_without_claiming_a_projection(self):
        page = (ROOT / "projections" / "index.html").read_text(encoding="utf-8")
        figure_path = ROOT / "figures" / "osw-province-atlas.svg"
        lakes_path = ROOT / "figures" / "osw-province-atlas-lakes.svg"
        coastal_states_path = ROOT / "figures" / "osw-province-atlas-coastal-states.svg"
        builder = (ROOT / "analysis" / "build_province_cartogram.py").read_text(encoding="utf-8")
        catalog_path = ROOT / "research" / "longhurst-province-reference.csv"
        region_catalog_path = ROOT / "research" / "osw-region-reference.csv"
        self.assertTrue(figure_path.is_file())
        self.assertTrue(lakes_path.is_file())
        self.assertTrue(coastal_states_path.is_file())
        self.assertTrue(catalog_path.is_file())
        self.assertTrue(region_catalog_path.is_file())
        figure = figure_path.read_text(encoding="utf-8")
        lakes = lakes_path.read_text(encoding="utf-8")
        coastal_states = coastal_states_path.read_text(encoding="utf-8")
        self.assertEqual(56, figure.count('class="province '))
        self.assertEqual(56, lakes.count('class="province '))
        self.assertEqual(56, coastal_states.count('class="province '))
        for token in ("PROVINCE ATLAS", "REFERENCE CARTOGRAM · NOT A PROJECTION", "CLASSIC SURFACE PROVINCES", "Static provinces are mean ecological references"):
            self.assertIn(token, figure + page)
        for code in ("BPLR", "WARM", "PEQD", "OCAL", "CCAL", "ISSG", "GFST", "SANT", "APLR"):
            self.assertIn(code, figure)
        self.assertIn("does not reproduce the CC-BY-NC-SA Marine Regions boundary dataset", figure)
        self.assertIn("Expected 56 provinces", builder)
        for token in ("Natural Earth 1:110m", "horizontally compressed", "EXPECTED_SOURCE_SHA256", 'class="coastline"'):
            self.assertIn(token, figure + builder + page)
        with catalog_path.open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(56, len(rows))
        self.assertEqual(56, len({row["code"] for row in rows}))
        self.assertTrue(all(row["edition"] == "classic 56-province reference" for row in rows))
        self.assertIn("Open the complete 56-row province directory", page)
        for token in ("CONTINENTS AS LAKES", 'mask id="continent-cutouts"', "ONE FILL", "Real coastlines cut the edge pieces"):
            self.assertIn(token, lakes)
        self.assertIn("osw-province-atlas-lakes.svg", page)
        for token in ("COAST-OWNED STATES", 'mask id="ocean-only"', "ALSK inherits Alaska", "nearest-seed internal borders"):
            self.assertIn(token, coastal_states + page)
        for token in ("11 ORGANIZATIONAL REALMS · 22 CONTIGUOUS SCHEMATIC REGIONS · 56 CLASSIC PROVINCE IDENTITIES", 'class="realm-boundary-casing"', 'class="realm-boundaries"', 'class="region-boundary-casing"', 'class="region-boundaries"', 'class="region-labels"', 'class="land-context"', 'pattern id="land-hatch"', "REALM BORDER", "SCHEMATIC-REGION BORDER", "OCEAN-STATE BORDER", "ARCTIC–ATLANTIC POLAR 3", "EASTERN PACIFIC COASTAL 4", "NORTH ATLANTIC WESTERLIES 4", "INDIAN TRADES 2", "SOUTHERN WESTERLIES 2"):
            self.assertIn(token, coastal_states)
        regions = re.findall(r'data-region="([^"]+)"', coastal_states)
        self.assertEqual(56, len(regions))
        self.assertEqual(22, len(set(regions)))
        for basin in ("pacific", "atlantic", "indian", "southern", "arctic"):
            self.assertIn(f"basin-{basin}", coastal_states)
        self.assertIn("osw-province-atlas-coastal-states.svg", page)
        with region_catalog_path.open(encoding="utf-8", newline="") as source:
            region_rows = list(csv.DictReader(source))
        self.assertEqual(22, len(region_rows))
        self.assertEqual(22, len({row["code"] for row in region_rows}))
        self.assertEqual(22, len({row["color"] for row in region_rows}))
        member_codes = [code for row in region_rows for code in row["member_state_codes"].split("|")]
        self.assertEqual(56, len(member_codes))
        self.assertEqual(56, len(set(member_codes)))
        self.assertTrue(all(row["label_anchor"] in row["member_state_codes"].split("|") for row in region_rows))
        self.assertTrue(all(row["classification_status"] == "provisional OSW organizational construct" for row in region_rows))
        self.assertTrue(all(row["topology_definition"] == "connected before land masking and projection interruption" for row in region_rows))
        self.assertIn("osw-region-reference.csv", page)

    def test_province_atlas_breakthrough_is_preserved_in_project_history(self):
        history = (ROOT / "HISTORY.md").read_text(encoding="utf-8")
        plan = (ROOT / "plans" / "province-atlas-shape-system.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for token in ("The ocean becomes a place", "Equal voice", "True footprint", "495ec4b", "identity can be simplified; geometry must declare its truth"):
            self.assertIn(token, history)
        for token in ("One ocean. 56 provinces. Two truths.", "varied puzzle cartogram", "8–12%", "legally compatible"):
            self.assertIn(token, plan)
        self.assertIn("Read the project history", readme)

    def test_observed_layer_is_explicitly_surface_only(self):
        html = HTML.read_text(encoding="utf-8")
        data = (ROOT / "atlas" / "data" / "oisst-2026-08-01.js").read_text(encoding="utf-8")
        self.assertIn("Observed SST", html)
        self.assertIn("OBSERVATIONAL · SURFACE", html)
        self.assertIn("not full-depth heat content", data)

    def test_anomaly_mode_declares_reference_period(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertIn('data-mode="anomaly"', html)
        self.assertIn("1971–2000", app)

    def test_error_mode_is_time_matched_and_bounded(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertIn('data-mode="error"', html)
        self.assertIn("TIME-MATCHED ERROR", app)
        self.assertIn("not forecast error", (ROOT / "atlas" / "data" / "oisst-error-2026-08-01.js").read_text(encoding="utf-8"))

    def test_depth_mode_is_explicitly_anomaly_not_heat_content(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        data = (ROOT / "atlas" / "data" / "argo-temperature-anomaly-700dbar-2026-07.js").read_text(encoding="utf-8")
        self.assertIn('data-mode="argo700"', html)
        self.assertIn("ARGO ANALYSIS · ${data.pressure_dbar.toFixed(0)} DBAR ANOMALY", app)
        self.assertIn("64.5°S–79.5°N", app)
        self.assertIn("not absolute temperature", data)
        self.assertIn("Antarctic shelf", data)

    def test_depth_probe_samples_each_product_on_its_own_grid(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertIn("samples each product on its own nearest display cell", html)
        self.assertIn("OCEANLINES_ARGO_TEMPERATURE_ANOMALY", app)
        self.assertIn("Products are sampled on their own grids", app)

    def test_argo_depth_ladder_is_accessible_and_bookmarkable(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ('id="argo-depths"', 'aria-label="Argo pressure level"', 'data-pressure="10"', 'data-pressure="300"', 'data-pressure="700"', 'data-pressure="1000"'):
            self.assertIn(token, html)
        for token in ("argoLayers", "setArgoPressure", 'searchParams.set("pressure"', "outside source domain", "Argo anomaly profile"):
            self.assertIn(token, app)

    def test_legacy_studies_remain_linked_beneath_geography_lenses(self):
        source = HTML.read_text(encoding="utf-8")
        for target in ("../HEATMASS.md", "../OCEANREALMS.md", "../OCEANBELTS.md"):
            self.assertIn(f'href="{target}"', source)

    def test_ocean_geography_filters_are_overlapping_accessible_and_bookmarkable(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ("ALL FEATURES", "WATERS", "FLOWS", "EDGES", "FLOOR", "LIFE", "EVENTS", 'id="filter-status"', 'aria-live="polite"', "not observed boundaries"):
            self.assertIn(token, html + app)
        for token in ("zoneMatches", "applyGeographyFilters", 'searchParams.set("lens"', 'shape.toggleAttribute("hidden", !show)', "shape.tabIndex = show ? 0 : -1"):
            self.assertIn(token, app)

    def test_coordinate_probe_has_pointer_keyboard_and_text_paths(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ('id="coordinate-probe"', 'id="probe-lat"', 'id="probe-lon"', 'id="probe-result"', 'aria-live="polite"'):
            self.assertIn(token, html)
        for token in ("probeCellFromCoordinates", "inspectCoordinates", 'addEventListener("click"', 'addEventListener("submit"', "Nearest active display cell"):
            self.assertIn(token, app)

    def test_coordinate_probe_is_bookmarkable_and_reports_all_fields(self):
        source = APP.read_text(encoding="utf-8")
        for token in ('searchParams.set("mode"', 'searchParams.set("lat"', 'searchParams.set("lon"', 'searchParams.delete("mode"', "OCEANLINES_OISST_ANOMALY", "OCEANLINES_OISST_ERROR", "OCEANLINES_ARGO_TEMPERATURE_ANOMALY", "none is heat content or transport"):
            self.assertIn(token, source)

    def test_polar_rings_have_visual_text_and_keyboard_paths(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ('id="ring-form"', 'id="ring-lat"', 'id="north-ring"', 'id="south-ring"', 'id="ring-summary"', 'id="ring-body"'):
            self.assertIn(token, html)
        for token in ("pairedRingRows", "longestCyclicRun", "ringStatistics", "geometryData = window.OCEANLINES_OISST", "renderRingComparison", 'searchParams.set("ring"', "not a current, barrier strength, heat-content, or transport measurement"):
            self.assertIn(token, app)

    def test_polar_ring_claim_is_geometry_not_transport(self):
        html = HTML.read_text(encoding="utf-8")
        for token in ("Land-or-missing gaps expose analyzed-water continuity", "do not measure currents or heat transport", "Analyzed-water coverage", "Longest arc"):
            self.assertIn(token, html)

    def test_latitude_ladder_has_chart_and_complete_text_table(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ('id="continuity-chart"', 'id="continuity-summary"', 'id="continuity-method"', 'id="continuity-body"', "Open the complete 45-pair scan"):
            self.assertIn(token, html)
        for token in ("latitudeLadder", "renderLatitudeLadder", "magnitude <= 88", "coverage >= 95", "longestDegrees >= 300", "Product-mask topology only; not a circulation boundary"):
            self.assertIn(token, app)

    def test_latitude_ladder_uses_redundant_line_patterns(self):
        html = HTML.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("Northern rows · solid", html)
        self.assertIn("Southern rows · dashed", html)
        self.assertIn("border-top-style: dashed", css)

    def test_polar_mirrors_declare_projection_and_orientation(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for token in ('id="north-polar"', 'id="south-polar"', 'id="polar-method"', 'id="polar-summary"', "radial azimuthal-equidistant", "intentionally mirrors the southern cap"):
            self.assertIn(token, html)
        for token in ("renderPolarMirror", "renderPolarMirrors", "const capLatitude = 40", "Math.atan2(dx, -dy)", 'hemisphere === "north"', "intentional comparison mirror"):
            self.assertIn(token, app)

    def test_polar_mirrors_have_text_and_non_color_selected_ring(self):
        html = HTML.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertIn("Beige means land or missing", html)
        self.assertIn("amber circle is the selected ring", html)
        self.assertIn("context.setLineDash([9, 6])", app)
        self.assertIn("not bathymetry, sea ice, circulation, or heat transport", app)

    def test_local_links_resolve(self):
        source = HTML.read_text(encoding="utf-8")
        for target in re.findall(r'(?:href|src)="(\.\.?/[^"#]+)"', source):
            self.assertTrue((HTML.parent / target).resolve().exists(), target)

if __name__ == "__main__":
    unittest.main()
