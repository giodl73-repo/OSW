"""Exercise the standalone screened atlas in local Chromium."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

from build_ocean_motion_screened_site import OUTPUT


CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        pass


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(OUTPUT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, executable_path=str(CHROME))
            try:
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="networkidle")
                assert page.get_by_role("main").count() == 1
                assert page.get_by_role("searchbox", name="Search name, basin, or ID").count() == 1
                assert page.get_by_role("searchbox", name="Find a current or evidence class").count() == 1
                assert page.get_by_role("combobox", name="Choose an OSW state").count() == 1
                assert page.get_by_role("table", name="Named-current length evidence inventory").count() == 1
                assert page.get_by_role("group", name="OSW 56-state equirectangular map with approximate editorial locator links for selected ocean motion records").count() == 1
                page.locator(".skip").focus()
                page.keyboard.press("Enter")
                assert page.evaluate("document.activeElement?.id === 'main'")
                assert "100 named currents · 40 named eddies" in page.locator("#coverage").inner_text()
                assert page.locator("#object-rows tr").count() == 218
                assert page.locator("#length-rows tr").count() == 11
                assert page.locator("#length-inventory-rows tr").count() == 100
                assert page.locator("#length-inventory-rows tr").filter(has_text="Published estimate").count() == 11
                assert page.locator("#length-inventory-rows tr").filter(has_text="OSW geographic floor").count() == 7
                assert page.locator("#length-inventory-rows tr").filter(has_text="Geographic span sensitivity:").count() == 7
                assert page.locator("#length-inventory-rows tr").filter(has_text="Possible position 6–7 of 7 geographic spans").count() == 2
                assert page.locator("#length-inventory-rows tr").filter(has_text="No numeric length admitted").count() == 71
                assert page.locator("#length-inventory-rows tr").filter(has_text="No whole-current number admitted").count() == 80
                for current_name in ("Caribbean Current", "South Atlantic Current", "South Indian Current"):
                    assert page.locator("#length-inventory-rows tr").filter(has_text=current_name).count() == 1
                page.locator("#length-search").fill("California Current")
                assert page.locator("#length-inventory-rows tr").count() == 1
                assert "regional system extent" in page.locator("#length-inventory-rows tr").inner_text()
                page.locator("#length-search").fill("")
                assert page.locator("#length-rows tr .warning").count() == 5
                assert page.locator("#length-rows tr").filter(has_text="California Current").locator(".warning").count() == 1
                assert "not a measured current-core axis" in page.locator("#length-rows tr").filter(has_text="California Current").inner_text()
                assert "not a traced whole-current axis" in page.locator("#length-rows tr").filter(has_text="Kuroshio Current").inner_text()
                assert page.locator("#length-rows tr").filter(has_text="California Current").locator('a[href^="https://meetings.pices.int/"]').count() == 1
                assert page.locator("#length-rows tr").filter(has_text="Kuroshio Current").locator('a[href^="https://tos.org/"]').count() == 1
                for name, value in (("Gulf Stream", "2,500"), ("Florida Current", "1,200")):
                    row = page.locator("#length-rows tr").filter(has=page.get_by_role("link", name=name, exact=True))
                    assert row.count() == 1 and value in row.inner_text()
                    assert row.locator('a[href^="https://incois.gov.in/"]').count() == 1
                assert page.locator("#length-rows tr").filter(has_text="Scientific claim review: pending.").count() == 11
                malvinas = page.locator("#length-rows tr").filter(has_text="Falkland (Malvinas) Current")
                assert malvinas.count() == 1 and "2,000" in malvinas.inner_text()
                assert malvinas.locator("td").first.inner_text() == "9"
                assert "conference abstract" in malvinas.inner_text()
                assert malvinas.locator('a[href="https://meetingorganizer.copernicus.org/EGU2009/EGU2009-12242.pdf"]').count() == 1
                assert page.locator("#movie-rows tr").count() == 70
                assert page.locator("#state-select option").count() == 57
                assert page.locator("#markers a").count() == 150
                assert page.request.get(f"http://127.0.0.1:{server.server_port}/osw-province-atlas-interactive.svg").ok
                if os.environ.get("OSW_MAP_SCREENSHOT"):
                    page.locator("#map").screenshot(path=os.environ["OSW_MAP_SCREENSHOT"])
                page.locator("#markers a").first.focus()
                assert page.evaluate("document.activeElement?.closest('#markers') !== null")
                page.locator("#search").fill("California Current")
                assert 0 < page.locator("#object-rows tr").count() < 218
                page.locator('#object-rows a[href="?id=current%3Acalifornia#record"]').click()
                assert page.locator("#record-title").inner_text() == "California Current"
                assert page.evaluate("document.activeElement?.id === 'record-title'")
                assert "Opened California Current" in page.locator("#selection-status").inner_text()
                assert "≈3,000 km" in page.locator("#record-body").inner_text()
                packet_link = page.get_by_role("link", name="Download this record and its evidence (JSON review copy)")
                assert packet_link.count() == 1
                packet_response = page.request.get(f"http://127.0.0.1:{server.server_port}/" + packet_link.get_attribute("href"))
                assert packet_response.ok and packet_response.json()["entity"]["id"] == "current:california"
                assert "source-set rank" in page.locator("#record-body").inner_text()
                assert "not a measured current-core axis" in page.locator("#record-body .warning").inner_text()
                assert "id=current%3Acalifornia" in page.url
                page.locator("#state-select").select_option("state:MEDI")
                assert "state=state%3AMEDI" in page.url
                assert "named-eddy/state assessments" in page.locator("#state-body").inner_text()
                assert "Opened Mediterranean Sea state passport" in page.locator("#state-status").inner_text()
                overview = page.get_by_role("table", name="State evidence overview")
                assert overview.get_by_role("row", name="Source-reported local current presence").locator("td").first.inner_text() == "1"
                assert "not physical absence" in page.locator(".state-evidence-overview").inner_text()
                state_packet = page.get_by_role("link", name="Download this state's records and evidence (JSON review copy)")
                assert state_packet.count() == 1
                state_response = page.request.get(f"http://127.0.0.1:{server.server_port}/" + state_packet.get_attribute("href"))
                assert state_response.ok and state_response.json()["entity"]["id"] == "state:MEDI"
                assert page.locator("#state-body summary").filter(has_text="Source-reported local presence:").count() == 1
                page.locator("#state-body summary").filter(has_text="Source-reported local presence:").click()
                assert "Off Toulon" in page.locator("#state-body").inner_text()
                assert page.locator('#state-body a[href="https://os.copernicus.org/articles/14/689/2018/"]').count() >= 1
                local_group = page.locator("#state-body > details").filter(has=page.locator('summary', has_text="Source-reported local presence:"))
                local_group.locator(".state-relation-evidence summary").first.click()
                assert "Source locator:" in local_group.inner_text()
                assert "Method:" in local_group.inner_text()
                assert "Scientific claim review: not individually reviewed" in local_group.inner_text()
                assert page.locator("#state-body summary").filter(has_text="Schematic or cartographic crossings:").count() == 1
                assert page.locator("#state-body summary").filter(has_text="Editorial locator candidates:").count() == 1
                assert page.locator("#state-body summary").filter(has_text="Unresolved physical crossings:").count() == 1
                assert page.locator("#state-body summary").filter(has_text="Named eddies with unresolved state intersection:").count() == 1
                assert "NASA regional crop display overlaps" in page.locator("#state-body").inner_text()
                page.set_viewport_size({"width": 390, "height": 780})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
                for zoom, width in (("200%", 390), ("400%", 1280)):
                    page.set_viewport_size({"width": width, "height": 780})
                    page.evaluate("zoom => { document.body.style.zoom = zoom; }", zoom)
                    metrics = page.evaluate("({scrollWidth: document.documentElement.scrollWidth, innerWidth})")
                    assert metrics["scrollWidth"] <= metrics["innerWidth"] + 1, (zoom, metrics)
                page.evaluate("document.body.style.zoom = ''")
                page.locator("#movie-search").fill("Kraken")
                assert page.locator("#movie-rows tr").count() == 10
                page.locator("#movie-rows details").first.locator("summary").click()
                assert "event identity not established" in page.locator("#movie-rows").inner_text()
                page.locator("#movie-search").fill("level0_A_1")
                assert page.locator("#movie-rows tr").count() == 1
                assert not errors, errors
                deep = browser.new_page()
                deep.goto(f"http://127.0.0.1:{server.server_port}/?id=current%3Akuroshio", wait_until="networkidle")
                assert deep.locator("#record-title").inner_text() == "Kuroshio Current"
                assert "2018-01 to 2020-05" in deep.locator("#record-body").inner_text()
                assert "malfunctioned" in deep.locator("#record-body").inner_text()
                assert deep.locator('a[href="?state=state%3ACHIN#states"]').count() == 1
                assert deep.get_by_role("link", name="Source license: CC BY 4.0").get_attribute("href") == "https://creativecommons.org/licenses/by/4.0/"
                ku_packet_link = deep.get_by_role("link", name="Download this record and its evidence (JSON review copy)")
                ku_packet = deep.request.get(f"http://127.0.0.1:{server.server_port}/" + ku_packet_link.get_attribute("href")).json()
                ku_observation = ku_packet["records"]["named_current_source_observations"][0]
                assert ku_observation["observation_time_precision"] == "month" and ku_observation["state_id"] == "state:CHIN"
                assert len(ku_observation["reported_observation_points_lon_lat"]) == 3
                assert any(claim["id"] == ku_observation["claim_id"] and claim["observation_support"]["reported_observation_points_lon_lat"] == ku_observation["reported_observation_points_lon_lat"] for claim in ku_packet["claims"])
                chin = browser.new_page()
                chin.goto(f"http://127.0.0.1:{server.server_port}/?state=state%3ACHIN#states", wait_until="networkidle")
                chin.get_by_text("Source-reported local presence: 1", exact=True).click()
                assert "2018-01 to 2020-05" in chin.locator("#state-body").inner_text()
                assert chin.locator('#state-body a[href="?id=current%3Akuroshio#record"]').count() >= 1
                chin.close()
                assert "not a traced whole-current axis" in deep.locator("#record-body .warning").inner_text()
                assert deep.locator("#length-rows tr").count() == 11
                slope = browser.new_page()
                slope.goto(f"http://127.0.0.1:{server.server_port}/?id=current%3Aantarctic-slope#record", wait_until="networkidle")
                assert slope.locator("#record-title").inner_text() == "Antarctic Slope Current"
                slope_row = slope.locator("#length-rows tr").filter(has_text="Antarctic Slope Current")
                assert slope_row.locator("td").first.inner_text() == "2" and "21,000" in slope_row.inner_text()
                assert "Antarctic Peninsula" in slope.locator("#record-body").inner_text()
                assert slope.locator(".classification-card dt").all_text_contents() == ["Fresh Shelf", "Dense Shelf", "Warm Shelf"]
                assert "no observed regime or OSW state assignment is admitted" in slope.locator(".classification-card").inner_text()
                packet_link = slope.get_by_role("link", name="Download this record and its evidence (JSON review copy)")
                packet_response = slope.request.get(f"http://127.0.0.1:{server.server_port}/" + packet_link.get_attribute("href"))
                assert packet_response.ok
                vocabulary = packet_response.json()["records"]["classification_vocabularies"][0]
                assert vocabulary["assignments"] == [] and len(vocabulary["terms"]) == 3
                assert any(claim["id"] == vocabulary["claim_id"] and claim["vocabulary_definition"]["terms"] == vocabulary["terms"] for claim in packet_response.json()["claims"])
                assert "source distinguished current" in slope.locator("#record-body").inner_text().lower()
                slope.close()
                coastal = browser.new_page()
                coastal.goto(f"http://127.0.0.1:{server.server_port}/?id=current%3Aalaska-coastal-gulf#record", wait_until="networkidle")
                assert coastal.locator("#record-title").inner_text() == "Alaska Coastal Current (Gulf of Alaska)"
                coastal_row = coastal.locator("#length-rows tr").filter(has_text="Alaska Coastal Current (Gulf of Alaska)")
                assert coastal_row.count() == 1 and "1,700" in coastal_row.inner_text()
                assert coastal_row.locator("td").first.inner_text() == "10"
                assert "Seward" in coastal_row.inner_text() and "Samalga" in coastal_row.inner_text()
                assert "Scientific claim review: pending." in coastal_row.inner_text()
                coastal_body = coastal.locator("#record-body").inner_text()
                assert "Published local current observations" in coastal_body
                assert "1989-05-10 to 1989-07-15" in coastal_body and "Shelikof Sea Valley" in coastal_body
                assert "not an observed-geometry intersection" in coastal_body
                assert coastal.get_by_role("link", name="Read cited publication copy (PDF)").get_attribute("href") == "https://workspace.aoos.org/files/2656915/Stabeno_etal_2016_Longterm_Obs_ACC.pdf"
                packet_link = coastal.get_by_role("link", name="Download this record and its evidence (JSON review copy)")
                packet_response = coastal.request.get(f"http://127.0.0.1:{server.server_port}/" + packet_link.get_attribute("href"))
                assert packet_response.ok
                assert "current:alaska-coastal-gulf" in packet_response.text()
                assert "shelikof-sea-valley-1989-alaska-coastal" in packet_response.text()
                coastal.goto(f"http://127.0.0.1:{server.server_port}/?state=state%3AALSK#states", wait_until="networkidle")
                coastal.locator("#state-body summary").filter(has_text="Source-reported local presence:").click()
                state_text = coastal.locator("#state-body").inner_text()
                assert "Shelikof Sea Valley" in state_text and "1989-05-10 to 1989-07-15" in state_text
                coastal.close()
                for slug, name, article in (
                    ("kraken-2013", "Kraken", "nature.com/articles/s41598-018-29582-5"),
                    ("thor-2020", "Thor", "frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1049645"),
                    ("ursa-2021", "Ursa", "frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1049645"),
                    ("cameron-2009-observed", "Cameron", "agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012JC007890"),
                    ("darwin-2009-observed", "Darwin", "agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012JC007890"),
                ):
                    ring = browser.new_page()
                    ring.goto(f"http://127.0.0.1:{server.server_port}/?id=eddy%3Apublished%3A{slug}#record", wait_until="networkidle")
                    assert ring.locator("#record-title").inner_text() == name
                    assert "observation window" in ring.locator("#record-body").inner_text()
                    assert ("Whole-eddy state containment remains unresolved" if slug == "kraken-2013" else
                            "state containment and intersection remain unresolved") in ring.locator("#record-body").inner_text()
                    assert ring.locator(f'#record-body a[href*="{article}"]').count() >= 1
                    assert ring.get_by_role("link", name="Download this record and its evidence (JSON review copy)").count() == 1
                    if slug == "kraken-2013":
                        footprint = ring.locator(".footprint-candidate")
                        assert footprint.count() == 1 and footprint.locator("svg path").count() == 1
                        assert "2013-05-29" in footprint.inner_text()
                        assert "outside the declared movie years" in footprint.inner_text()
                        assert "2021–2023" in footprint.inner_text()
                        assert footprint.get_by_role("link", name="Open NASA crop level2_B_3", exact=True).count() == 1
                        footprint.get_by_text("10 overlapping NASA crops", exact=True).click()
                        assert footprint.get_by_role("link", name="Open NASA crop level2_B_3", exact=True).count() == 2
                        assert footprint.get_by_role("link", name="Open NASA crop level2_B_3", exact=True).first.get_attribute("href").startswith("https://")
                        assert "robust across tested calibrations" in footprint.inner_text()
                        assert "calibration sensitive candidate" in footprint.inner_text()
                        assert "Containment unresolved" in footprint.inner_text()
                        packet_link = ring.get_by_role("link", name="Download this record and its evidence (JSON review copy)")
                        packet = ring.request.get(f"http://127.0.0.1:{server.server_port}/" + packet_link.get_attribute("href")).json()
                        candidate = packet["records"]["named_eddy_footprint_candidates"][0]
                        contexts = packet["records"]["footprint_movie_context"]
                        assert len(contexts) == 10
                        assert [row["tile_id"] for row in contexts if row["recommended"]] == ["level2_B_3"]
                        assert all(row["event_identity_status"] == "not_established" for row in contexts)
                        assert all(any(claim["id"] == row["claim_id"] and claim["support_claim_id"] == candidate["claim_id"] for claim in packet["claims"]) for row in contexts)
                        geometry = next(row for row in packet["records"]["geometries"] if row["id"] == candidate["geometry_id"])
                        assert len(geometry["geometry"]["coordinates"][0]) == 457
                        assert any(claim["id"] == candidate["claim_id"] and claim["footprint_support"]["geometry_sha256"] == geometry["geometry_sha256"] for claim in packet["claims"])
                        ring.set_viewport_size({"width": 320, "height": 800})
                        assert ring.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                        footprint.screenshot(path=str(Path(os.environ["TEMP"]) / "osw-kraken-footprint-card.png"))
                        assert "Dated figure location" in ring.locator("#record-body").inner_text()
                        assert "whole-ring containment remains unresolved" in ring.locator("#record-body").inner_text().lower()
                        assert ring.locator('#record-body a[href*="state%3ACAMR"]').count() >= 1
                        assert ring.locator('#record-body a[href*="state%3ACARB"]').count() >= 1
                        assert "axis-sensitive intersection candidate" in ring.locator("#record-body").inner_text()
                        audit_link = ring.locator('#record-body a[href="data/source-ledgers/kraken-2013-figure2-state-audit.json"]')
                        assert audit_link.count() == 2
                        assert ring.request.get(f"http://127.0.0.1:{server.server_port}/" + audit_link.first.get_attribute("href")).ok
                    if slug == "thor-2020":
                        assert "2020-01-27 · separation confirmed by date" in ring.locator("#record-body").inner_text()
                        assert "2020-03-23 · deformed and nearly split" in ring.locator("#record-body").inner_text()
                    if slug == "ursa-2021":
                        assert "2021-03-08 · temporary detachment" in ring.locator("#record-body").inner_text()
                        assert "2021-04-26 · final detachment reported" in ring.locator("#record-body").inner_text()
                    if slug in {"cameron-2009-observed", "darwin-2009-observed"}:
                        assert "Name origin: Horizon Marine attribution" in ring.locator("#record-body").inner_text()
                    if slug == "cameron-2009-observed":
                        assert "Dated observed center point" in ring.locator("#record-body").inner_text()
                        assert "The point does not establish whole-ring containment" in ring.locator("#record-body").inner_text()
                        assert ring.locator('#record-body a[href*="state%3ACAMR"]').count() >= 1
                    if slug == "darwin-2009-observed":
                        assert "Dated observed center point" not in ring.locator("#record-body").inner_text()
                        assert "near its center on August 5" in ring.locator("#record-body").inner_text()
                    ring.close()
                state_deep = browser.new_page()
                state_deep.goto(f"http://127.0.0.1:{server.server_port}/?state=state%3AMEDI#states", wait_until="networkidle")
                assert state_deep.locator("#state-select").input_value() == "state:MEDI"
                assert "named-eddy/state assessments" in state_deep.locator("#state-body").inner_text()
                state_deep.locator("#state-select").select_option("state:CAMR")
                assert state_deep.locator("#state-body .footprint-candidate").count() == 1
                assert "2013-05-29" in state_deep.locator("#state-body .footprint-candidate").inner_text()
                overview = state_deep.get_by_role("table", name="State evidence overview")
                assert overview.get_by_role("row", name="Dated named-eddy evidence").locator("td").first.inner_text() == "2"
                assert overview.get_by_role("row", name="Dated figure-footprint candidates").locator("td").first.inner_text() == "1"
                state_deep.set_viewport_size({"width": 320, "height": 900})
                assert overview.evaluate("el => el.scrollWidth <= el.clientWidth")
                if os.environ.get("OSW_STATE_SCREENSHOT"):
                    state_deep.locator(".state-evidence-overview").screenshot(path=os.environ["OSW_STATE_SCREENSHOT"])
                packet_link = state_deep.get_by_role("link", name="Download this state's records and evidence (JSON review copy)")
                state_packet = state_deep.request.get(f"http://127.0.0.1:{server.server_port}/" + packet_link.get_attribute("href")).json()
                assert state_packet["records"]["named_eddy_footprint_candidates"] and state_packet["records"]["geometries"]
                state_deep.locator("#state-body summary").filter(has_text="Inspect named-eddy locator candidates").click()
                assert "Cameron" in state_deep.locator("#state-body").inner_text()
                assert "reported center 2009-01-20; point only" in state_deep.locator("#state-body").inner_text()
                assert not errors, errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print("OK: screened atlas search, map, ranks, state passport, movies, and deep links")


if __name__ == "__main__":
    main()
