"""Smoke-test the motion atlas data join in a local Chromium browser."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        pass


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, executable_path=str(CHROME))
            try:
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/almanac/", wait_until="networkidle")
                assert "70 current-level records" in page.locator("#taxonomy-counts").inner_text()
                assert page.locator("#current-rows tr").count() == 100
                assert page.locator("#illustrated-span-rows tr").count() == 24
                assert "≈ 8,475 km" in page.locator("#illustrated-span-rows tr").first.inner_text()
                assert page.locator('#nasa-kuroshio a[href="https://svs.gsfc.nasa.gov/5425#media_group_376521"]').count() == 1
                assert page.locator('#nasa-kuroshio a[href="https://svs.gsfc.nasa.gov/5425#media_group_376522"]').count() == 1
                assert page.locator('#nasa-kuroshio a[href="https://svs.gsfc.nasa.gov/5425#media_group_376523"]').count() == 1
                assert "8 map-arrow crop regions" in page.locator("#nasa-gulf-stream").inner_text()
                assert page.locator("#nasa-gulf-stream details").first.locator("a").count() == 8
                assert "4 map-arrow crop regions" in page.locator("#nasa-agulhas").inner_text()
                assert "10 source-linked movie files" in page.locator("#nasa-gulf-stream").inner_text()
                assert page.locator("#nasa-gulf-stream details").last.locator("a").count() == 10
                assert "2 source-linked movie files" in page.locator("#nasa-upwelling").inner_text()
                assert "136 named eddy source records · context only" in page.locator("#nasa-ocean-eddies").inner_text()
                assert "97 named eddy source records · context only" in page.locator("#nasa-gulf-of-mexico-loop-eddies").inner_text()
                assert "8 named eddy source records · context only" in page.locator("#nasa-agulhas-rings").inner_text()
                assert page.locator('#nasa-agulhas-rings a[href="#eddy-geography-astrid-2000"]').count() == 1
                page.locator("#current-length-status").select_option("derived_lower_bound")
                assert page.locator("#current-rows tr").count() == 7
                assert page.locator("#current-gulf-stream").count() == 0
                page.locator("#current-length-status").select_option("published_estimate")
                assert page.locator("#current-rows tr").count() == 11
                assert "≈ 1,700 km" in page.locator("#current-alaska-coastal-gulf").inner_text()
                assert "Samalga" in page.locator("#current-alaska-coastal-gulf").inner_text()
                assert "≈ 2,500 km" in page.locator("#current-gulf-stream").inner_text()
                assert "≈ 1,200 km" in page.locator("#current-florida").inner_text()
                assert "≈ 6,000 km" in page.locator("#current-peru-humboldt").inner_text()
                assert "≈ 14,000 km" in page.locator("#current-pacific-equatorial-undercurrent").inner_text()
                page.locator("#current-length-status").select_option("all")
                page.locator("#current-nasa-status").select_option("nasa_named_or_described")
                assert page.locator("#current-rows tr").count() == 7
                page.locator("#current-nasa-status").select_option("independent_context")
                assert page.locator("#current-rows tr").count() == 3
                assert page.locator("#current-agulhas-return").count() == 1
                assert page.locator("#current-mindanao-current").count() == 1
                page.locator("#current-nasa-status").select_option("all")
                agulhas_return = page.locator("#current-agulhas-return")
                assert "≥ 1,400 km · unranked" in page.locator("#current-agulhas").inner_text()
                assert page.locator('#current-agulhas a[href="https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.837906/full"]').count() == 1
                assert "≥ 3,000 km · unranked" in agulhas_return.inner_text()
                assert "Inferred lower bound" in agulhas_return.inner_text()
                assert agulhas_return.locator('a[href="#current-agulhas"]').count() == 1
                assert agulhas_return.locator('a[href="#current-south-indian"]').count() == 1
                assert agulhas_return.locator('a[href="https://www.cfoo.co.za/seaatlas/papers/agulhas_return_current.pdf"]').count() == 1
                assert agulhas_return.locator('a[href="#nasa-agulhas-retroflection"]', has_text="NASA described turn").count() == 1
                kuroshio_extension = page.locator("#current-kuroshio-extension")
                assert kuroshio_extension.locator('a[href="#nasa-kuroshio-eastward-turn"]', has_text="NASA described turn").count() == 1
                assert kuroshio_extension.locator('a[href="https://www.whoi.edu/science/PO/POOL/projects.html"]').count() == 1
                assert "~1,000 km sampled reach" in page.locator("#current-east-greenland-coastal").inner_text()
                assert "≥ 2,100 km · unranked" in page.locator("#current-east-greenland").inner_text()
                assert page.locator('#current-east-greenland-coastal a[href="#current-east-greenland"]').count() == 1
                assert page.locator('#current-east-australian a[href="https://svs.gsfc.nasa.gov/14745"]', has_text="NASA film").count() == 1
                assert page.locator('#current-indonesian-throughflow a[href="https://svs.gsfc.nasa.gov/5425"]', has_text="NASA film").count() == 1
                assert page.locator('#current-indonesian-throughflow a[href="#nasa-indonesian-throughflow"]', has_text="NASA object record").count() == 1
                assert page.locator('#current-mindanao-current a[href="#nasa-indonesian-throughflow"]', has_text="NASA named receiving flow").count() == 1
                for current_id in ("new-guinea-coastal-undercurrent", "new-ireland-coastal-undercurrent", "solomon-island-coastal-undercurrent"):
                    assert "subsurface core" in page.locator(f"#current-{current_id}").inner_text()
                assert "southeastward in boreal winter" in page.locator("#current-new-guinea-coastal-current").inner_text()
                assert "140°W" in page.locator("#current-pacific-north-subsurface-countercurrent").inner_text()
                assert "140°W" in page.locator("#current-pacific-south-subsurface-countercurrent").inner_text()
                assert page.locator('#current-hiri-current a[href="#current-east-australian"]').count() == 1
                assert page.locator("#current-east-adriatic").count() == 1
                assert page.locator("#current-black-sea-rim").count() == 1
                assert "deep flow" in page.locator("#current-deep-western-boundary").inner_text()
                assert "subsurface core" in page.locator("#current-mediterranean-undercurrent").inner_text()
                for current_id, parent_id in (("atlantic-north-equatorial-countercurrent", "north-equatorial-countercurrent"), ("pacific-north-equatorial-countercurrent", "north-equatorial-countercurrent"), ("atlantic-south-equatorial-countercurrent", "south-equatorial-countercurrent"), ("pacific-south-equatorial-countercurrent", "south-equatorial-countercurrent"), ("indian-south-equatorial-countercurrent", "south-equatorial-countercurrent")):
                    row = page.locator(f"#current-{current_id}")
                    assert "unranked" in row.inner_text()
                    assert row.locator(f'a[href="#current-{parent_id}"]').count() == 1
                assert "≥ 1,800 km · unranked" in page.locator("#current-east-australian").inner_text()
                assert page.locator('#current-east-australian a[href="#current-tasman-front"]').count() == 1
                assert page.locator('#current-tasman-front a[href="#current-east-australian"]').count() == 1
                assert page.locator('#current-tasman-front a[href="https://doi.org/10.1002/2017JC013097"]').count() == 1
                assert page.locator('#current-tasman-front a[href*="Oke_etal.pdf"]').count() == 1
                assert page.locator('#current-agulhas a[href*="bg.copernicus.org/articles/18/5967/2021/"]').count() == 1
                assert "1,000 km source-specific scope" in page.locator("#current-agulhas").inner_text()
                assert "Inferred lower bound" in page.locator("#current-east-australian").inner_text()
                assert "~2,000 km sampled reach" in page.locator("#current-gulf-stream").inner_text()
                assert "≈ 2,500 km" in page.locator("#current-gulf-stream").inner_text()
                assert page.locator('#current-gulf-stream a[href="https://incois.gov.in/Tutor/regoc/pdffiles/colour/single/14P-Atlantic.pdf"]').count() == 1
                assert "Florida Current" in page.locator("#current-gulf-stream-system").inner_text()
                assert page.locator('#current-gulf-stream-system a[href="#current-florida"]').count() == 1
                assert page.locator('#current-gulf-stream-system a[href="#current-gulf-stream"]').count() == 1
                assert page.locator('#current-gulf-stream-system a[href="#current-north-atlantic"]').count() == 1
                assert page.locator('#nasa-gulf-stream a[href="#current-gulf-stream-system"]', has_text="Source-name system").count() == 1
                assert "Florida Straits" in page.locator("#nasa-gulf-stream").inner_text()
                hypothesis = page.locator("#current-greenland-middle-atlantic-shelf-hypothesis")
                assert "≈ 5,000 km · hypothesis · unranked" in hypothesis.inner_text()
                assert hypothesis.locator('a[href="#current-labrador"]', has_text="Related").count() == 1
                indian_euc = page.locator("#current-indian-equatorial-undercurrent")
                assert "subsurface core" in indian_euc.inner_text()
                assert "90°E, 2°S–2°N · ~13.5 Sv eastward" in indian_euc.inner_text()
                assert indian_euc.locator('a[href="#current-equatorial-undercurrent"]').count() == 1
                assert indian_euc.locator('a', has_text="NASA region (depth unverified)").count() == 1
                pacific_neuc = page.locator("#current-pacific-north-equatorial-undercurrent")
                assert "130°E, 8.5°N–17.5°N · ~5.1 Sv eastward" in pacific_neuc.inner_text()
                atlantic_seuc = page.locator("#current-atlantic-south-equatorial-undercurrent")
                assert "35°W, 4°S–2.5°S · ~2.8 Sv eastward" in atlantic_seuc.inner_text()
                norwegian_coastal = page.locator("#current-norwegian-coastal")
                assert "1–5 nmi off Store Torungen" in norwegian_coastal.inner_text()
                assert "convention-dependent" in norwegian_coastal.inner_text()
                assert norwegian_coastal.locator('a[href="#current-norwegian"]', has_text="Name overlap").count() == 1
                assert page.locator("#current-antarctic-coastal").count() == 1
                for current_id, transport in (("azores", "13.9 Sv eastward"), ("azores-countercurrent", "5.5 Sv westward")):
                    row = page.locator(f"#current-{current_id}")
                    assert "unranked" in row.inner_text()
                    assert "~110 km across" in row.inner_text()
                    assert transport in row.inner_text()
                    assert row.locator('a[href="https://doi.org/10.1029/2011JC007129"]').count() >= 1
                portugal = page.locator("#current-portugal")
                assert "unranked" in portugal.inner_text()
                assert "13.5–14.8°W" in portugal.inner_text()
                assert "1.8 ± 0.4 Sv southward" in portugal.inner_text()
                assert portugal.locator('a[href="https://doi.org/10.1002/jgrc.20227"]').count() >= 1
                canary = page.locator("#current-canary")
                assert "unranked" in canary.inner_text()
                assert "18.5–22.25°W" in canary.inner_text()
                assert "thermocline 6.2 ± 0.6 Sv; intermediate 2 ± 0.8 Sv southward" in canary.inner_text()
                assert canary.locator('a[href="https://doi.org/10.1002/jgrc.20227"]').count() == 1
                assert page.locator("#source-current-rows tr").count() == 52
                page.locator("#source-current-filter").select_option("candidate_needs_review")
                assert page.locator("#source-current-rows tr").count() == 7
                assert "historical current hypothesis" in page.locator("#mr-current-5398").inner_text()
                assert page.locator('#mr-current-5398 a[href="https://spo.nmfs.noaa.gov/sites/default/files/pdf-content/1975/733/ingham.pdf"]').count() == 1
                page.locator("#source-current-filter").select_option("all")
                assert page.locator("#mr-current-2364").count() == 1
                assert "Atlantic Equatorial Undercurrent" in page.locator("#mr-current-30077").inner_text()
                assert "5,500 km" in page.locator("#current-australian-west-south-boundary-flow").inner_text()
                assert page.locator('#current-australian-west-south-boundary-flow a[href="#current-zeehan"]').count() == 1
                assert page.locator("#eddy-rows tr").count() == 96
                assert page.locator("#eddy-geography-rows tr").count() == 35
                assert "136 source records" in page.locator("#all-eddy-count").inner_text()
                assert page.locator('#eddy-geography-meddy-ulla-1997 a[href="#current-mediterranean-undercurrent"]').count() == 1
                assert "1,000 m depth" in page.locator("#eddy-geography-meddy-ulla-1997").inner_text()
                assert "different era" in page.locator("#eddy-geography-meddy-ulla-1997").inner_text()
                assert "depth unverified" in page.locator("#eddy-geography-meddies-family").inner_text()
                page.locator("#all-eddy-search").fill("Feldman")
                assert page.locator('#all-eddy-results a[href="#eddy-loop-81-primary"]').count() == 1
                page.locator("#all-eddy-search").fill("Astrid")
                assert page.locator('#all-eddy-results a[href="#eddy-geography-astrid-2000"]').count() == 1
                page.locator("#all-eddy-search").fill("")
                assert page.locator('#eddy-geography-rows a[href="#nasa-ocean-eddies"]').count() == 35
                assert page.locator('#eddy-geography-cyprus-eddy-region a[href*="state=MEDI"]').count() == 1
                assert page.locator('#eddy-geography-shikmona-eddy-region a[href*="state=MEDI"]').count() == 1
                assert "occasional weekly or monthly anticyclonic reversals" in page.locator("#eddy-geography-latakia-eddy-region").inner_text()
                for eddy_id, box_text in (("mindanao-eddy-region", "126–130°E, 2–8°N"), ("halmahera-eddy-region", "128.5–135°E, 0–7°N")):
                    row = page.locator(f"#eddy-geography-{eddy_id}")
                    assert box_text in row.inner_text()
                    assert row.locator('a[href*="state=SUND"]').count() == 1
                    assert row.locator('a[href="https://doi.org/10.1029/2025JC022648"]').count() == 1
                    assert row.locator('a[href="#current-pacific-north-equatorial-countercurrent"]').count() == 1
                new_guinea = page.locator("#eddy-geography-new-guinea-eddy-region")
                assert "depth unverified" in new_guinea.inner_text()
                assert new_guinea.locator('a[href="#current-new-guinea-coastal-undercurrent"]').count() == 1
                assert new_guinea.locator('a[href="https://www2.jpgu.org/meeting/2017/PDF2017/A-OS22_O_e.pdf"]').count() == 1
                assert new_guinea.locator('a[href="https://doi.org/10.1029/2018JC014842"]').count() == 1
                assert "5 reported activity periods in 2010" in page.locator("#eddy-geography-cuba-anticyclones-family").inner_text()
                assert page.locator('#eddy-geography-cuba-anticyclones-family a[href="#nasa-gulf-of-mexico-loop-eddies"]').count() == 1
                assert page.locator('#eddy-loop-55-primary a[href="https://repository.library.noaa.gov/view/noaa/28993"]').count() == 1
                assert page.locator('#eddy-geography-persian-gulf-peddies-family a[href="#nasa-persian-gulf-saline-overflow"]').count() == 1
                assert "before inferred crop dates" in page.locator("#eddy-geography-persian-gulf-peddies-family").inner_text()
                assert "no sea-surface-height signature" in page.locator("#eddy-geography-persian-gulf-peddies-family").inner_text()
                assert page.locator('#eddy-geography-agulhas-rings-family a[href="#nasa-agulhas-rings"]').count() == 1
                assert "140 shed rings; 74 long-lived Walvis-crossing tracks" in page.locator("#eddy-geography-agulhas-rings-family").inner_text()
                assert page.locator('#eddy-geography-astrid-2000 a[href="#nasa-agulhas-rings"]').count() == 1
                assert "reported center" in page.locator("#eddy-geography-astrid-2000").inner_text()
                assert "~120 km radius" in page.locator("#eddy-geography-astrid-2000").inner_text()
                assert "different era" in page.locator("#eddy-geography-laura-1999").inner_text()
                assert "reported center" in page.locator("#eddy-geography-ana-2004").inner_text()
                assert "reported event point" in page.locator("#eddy-geography-eliza-2007").inner_text()
                assert "AS2" in page.locator("#eddy-geography-jeannette-2012").inner_text()
                assert "147078" in page.locator("#eddy-geography-lilian-2006").inner_text()
                assert "Agulhas Eddy W" in page.locator("#eddy-geography-agulhas-eddy-w-2000").inner_text()
                assert "22 February 2000" in page.locator("#eddy-geography-agulhas-eddy-w-2000").inner_text()
                assert "first detection; date not reported at 39.5°S, 14.6°E" in page.locator("#eddy-geography-lilian-2006").inner_text()
                assert ">5,500 km source-reported ring travel" in page.locator("#eddy-geography-lilian-2006").inner_text()
                assert "2015-12-27 at 21°S, 35°W" in page.locator("#eddy-geography-jeannette-2012").inner_text()
                assert page.locator('#eddy-geography-jeannette-2012 a[href*="level2_C_5.mp4"]').count() == 1
                assert "different era" in page.locator("#eddy-geography-jeannette-2012").inner_text()
                assert "Recurring regional name" in page.locator("#eddy-geography-batumi-eddy-region").inner_text()
                assert "No suitable OSW state" in page.locator("#eddy-geography-batumi-eddy-region").inner_text()
                assert "Individual · 1998" in page.locator("#eddy-geography-haida-1998").inner_text()
                assert page.locator('#eddy-geography-haida-1998 a[href="#eddy-geography-haida-eddy-region"]', has_text="Family").count() == 1
                assert page.locator('#eddy-geography-haida-1998 a[href*="svs.gsfc.nasa.gov/vis/"]').count() == 1
                assert "different era" in page.locator("#eddy-geography-haida-1998").inner_text()
                assert "CTD cast 47, 1,005 dbar" in page.locator("#eddy-geography-kenai-2007").inner_text()
                assert "54.783°N, 155.735°W · sample site" in page.locator("#eddy-geography-kenai-2007").inner_text()
                assert "6 source-detected in 1992–2008" in page.locator("#eddy-geography-kenai-eddy-region").inner_text()
                assert "Observed through 2008-01-23" in page.locator("#eddy-geography-kenai-2007").inner_text()
                assert "Dissipated early December 2007" in page.locator("#eddy-geography-sitka-2007").inner_text()
                assert "different era" in page.locator("#eddy-geography-kenai-2007").inner_text()
                assert "Secondary eddy" in page.locator("#eddy-loop-77-secondary").inner_text()
                assert "NASA model years overlap; identity unverified" in page.locator("#eddy-loop-77-primary").inner_text()
                assert "linked event began in NASA model years" in page.locator("#eddy-loop-77-secondary").inner_text()
                assert page.locator('#eddy-loop-77-primary a[href="#nasa-gulf-of-mexico-loop-eddies"]').count() == 1
                assert page.locator('#eddy-loop-77-primary a[href*="perpetual_ocean2_EQUIREC_071_final_beauty_level2_A_3.mp4"]').count() == 0
                assert "Published center near 26°N, 89°W" in page.locator("#eddy-loop-77-primary").inner_text()
                assert "Source-labeled map · 2023-12-21" in page.locator("#eddy-loop-77-primary").inner_text()
                assert page.locator('#eddy-loop-77-primary a[href*="UGOS_annualMtng2024_ProgramOverview_v2.pdf"]').count() == 1
                assert page.locator('#eddy-loop-77-primary a[href*="level2_B_3.mp4#t=237.93"]').count() == 1
                assert page.locator('#eddy-loop-77-primary a[href$="perpetual_ocean2_EQUIREC_071_final_beauty_level2_B_3.mp4"]').count() == 1
                assert page.locator("#nasa-rows tr").count() == 22
                assert page.locator('#nasa-objects a[href="https://x.com/latestincosmos/status/2104524519209935159"]').count() == 1
                assert "cropped repost" in page.locator("#nasa-objects").inner_text()
                assert page.locator('a[href="../research/nasa-perpetual-ocean-object-coverage-audit.json"]').count() == 1
                for example_id in ("gulf-stream", "kuroshio", "agulhas", "east-australian"):
                    assert page.locator(f'#nasa-western-boundary-currents a[href="#nasa-{example_id}"]', has_text="Example:").count() == 1
                assert page.locator('#nasa-indonesian-throughflow a[href="#current-indonesian-throughflow"]', has_text="Current ledger").count() == 1
                assert page.locator('#nasa-indonesian-throughflow a[href="../atlas/?feature=indonesian-throughflow&lens=flows"]', has_text="Atlas feature").count() == 1
                assert page.locator("#nasa-evidence-count").inner_text() == "39"
                assert "eddy class" in page.locator("#nasa-ocean-eddies").inner_text()
                assert page.locator('#nasa-ocean-eddies a[href="https://svs.gsfc.nasa.gov/3827#media_group_351519"]').count() == 1
                assert page.locator('#nasa-ocean-eddies a[href="https://svs.gsfc.nasa.gov/10841#media_group_350677"]').count() == 1
                assert page.locator('#nasa-ocean-eddies a', has_text="Subtype:").count() == 5
                assert page.locator('#nasa-agulhas-rings a[href="#nasa-ocean-eddies"]', has_text="Class:").count() == 1
                assert "REDS locator" in page.locator("#nasa-red-sea-saline-overflow").inner_text()
                assert "ARAB locator" in page.locator("#nasa-persian-gulf-saline-overflow").inner_text()
                assert page.locator('#nasa-kuroshio-eastward-turn a[href*="Perp_Oceans_Final_2.webm#t=95,103"]').count() == 2
                assert "large meanders can persist many months" in page.locator("#nasa-kuroshio-meanders").inner_text()
                assert page.locator('#nasa-western-boundary-currents a[href*="Perp_Oceans_Final_2.webm#t=55,65"]').count() == 2
                assert page.locator('#nasa-agulhas-rings a[href*="OceanFlows_AgulhasCurrent_3840x1080.mp4"]').count() == 2
                assert page.locator('#nasa-agulhas-rings a[href="#nasa-agulhas"]', has_text="Parent").count() == 1
                assert page.locator('#nasa-agulhas-rings a[href="#current-agulhas"]', has_text="Parent current").count() == 1
                for object_id in ("agulhas-rings", "gulf-stream", "gulf-stream-deep-return"):
                    assert page.locator(f'#nasa-{object_id} a[href="#nasa-global-overturning"]', has_text="System:").count() == 1
                assert page.locator('#nasa-agulhas-retroflection a[href="#current-agulhas-return"]', has_text="Independently named").count() == 1
                assert page.locator('#nasa-kuroshio-eastward-turn a[href="#current-kuroshio-extension"]', has_text="Independently named").count() == 1
                assert page.locator('#nasa-north-atlantic-sinking a[href="#nasa-global-overturning"]', has_text="Parent").count() == 1
                assert "ring class" in page.locator("#nasa-agulhas-rings").inner_text()
                page.locator("#nasa-search").fill("vertical_process")
                assert page.locator("#nasa-rows tr").count() == 2
                page.locator("#nasa-search").fill("")
                page.locator("#nasa-search").fill("Agulhas Rings")
                page.locator('#nasa-agulhas-rings a[href="#nasa-agulhas"]').click()
                assert page.locator("#nasa-search").input_value() == ""
                assert page.locator("#nasa-agulhas").is_visible()
                assert page.locator('#nasa-agulhas-retroflection a[href="https://svs.gsfc.nasa.gov/10841#media_group_350681"]').count() == 1
                assert page.locator('#nasa-western-boundary-rings a[href*="clean_noDate_1080p30.mp4"]', has_text="Source release overview").count() == 1
                assert "No bounded state footprint" in page.locator('#nasa-western-boundary-rings').inner_text()
                assert page.locator('#nasa-gulf-stream-deep-return a[href*="beauty_600m_and_below_1080p30.mp4"]').count() == 2
                cold_core_claim = page.locator('#nasa-gulf-stream-cold-cores a', has_text="NASA wording: mostly anticyclonic (scope disputed)")
                assert cold_core_claim.count() == 1
                assert "no individual eddy is classified" in cold_core_claim.get_attribute("title")
                assert page.locator('#nasa-gulf-stream-cold-cores a[href="https://doi.org/10.1126/science.212.4499.1091"]', has_text="Independent ring study").count() == 1
                assert page.locator('#nasa-western-boundary-currents a[href*="temperature_1080p30.mp4#t=150"]').count() == 1
                assert page.locator('#nasa-gulf-stream a[href*="state=GFST"]', has_text="mapped arrow").count() == 1
                assert page.locator('#nasa-kuroshio a[href*="state=KURO"]', has_text="atlas line").count() == 1
                assert "up to 2.5 m/s" in page.locator('#nasa-gulf-stream td').nth(4).inner_text()
                assert ">200× Amazon River water flow" in page.locator('#nasa-kuroshio td').nth(4).inner_text()
                assert page.locator('#nasa-kuroshio td').nth(4).locator('a[href*="script_37940_00.html"]').count() == 1
                for current_id in ("gulf-stream", "kuroshio"):
                    assert ">4 mph surface speed (2011 story)" in page.locator(f'#nasa-{current_id} td').nth(4).inner_text()
                    assert page.locator(f'#nasa-{current_id} td').nth(4).locator('a[href="https://svs.gsfc.nasa.gov/10841"]').count() == 1
                assert page.locator('#nasa-gulf-stream td').nth(5).locator('a[href*="svs.gsfc.nasa.gov"]').count() == 10
                assert page.locator('#nasa-gulf-stream td').nth(5).locator('a[href*="#media_group_351521"]').count() == 1
                assert "cues 49–54" in page.locator('#nasa-gulf-stream td').nth(5).inner_text()
                assert "7 releases · 55 movie files" in page.locator("#nasa-media-count").inner_text()
                assert page.locator("#nasa-media-releases details").count() == 7
                assert page.locator("#nasa-media-releases .source-review-note cite").count() == 7
                western_release = page.locator("#nasa-media-releases details").nth(2)
                assert "NASA's Scientific Visualization Studio (2025)" in western_release.locator("cite").text_content()
                assert western_release.locator(".nasa-release-objects li").count() == 14
                assert western_release.locator('.nasa-release-objects a[href="#nasa-indonesian-throughflow"]').count() == 1
                assert western_release.locator('.nasa-release-objects a[href="https://svs.gsfc.nasa.gov/5425#media_group_376523"]').count() > 0
                assert "10.5281/zenodo.16782525" in page.locator("#nasa-media-releases details").nth(3).locator("cite").text_content()
                page.locator("#nasa-media-releases details").last.locator("summary").click()
                assert "No named or individually described motion object" in page.locator("#nasa-media-releases details").last.inner_text()
                assert page.locator("#nasa-media-releases details").last.locator('a[href*="south_1080.mp4"]').count() == 1
                assert page.locator("#state-select option").count() == 57
                assert page.locator('a[href="../research/ocean-current-state-relation-matrix.json"]').count() == 1
                assert page.locator("#motion-markers a").count() == 184
                assert page.locator("#operational-eddy-polygons a[href^='object.html?id=navo-freddies']").count() == 4
                page.locator('#operational-eddy-polygons a[href$="C26001"]').click(trial=True)
                assert page.locator('#motion-markers a[href="#eddy-loop-77-primary"]').count() == 1
                page.locator('#eddy-loop-77-primary a[href="#motion-map-section"]').click()
                assert page.locator('#motion-markers a[data-record="loop-77-primary"].selected').count() == 1
                assert page.locator('#motion-markers a[href="#current-tasman-front"]').count() == 2
                assert page.locator('#motion-markers a[href="#current-agulhas-return"]').count() == 3
                page.locator("#state-select").select_option("SSTC")
                assert "Agulhas Return Current" in page.locator("#state-result").inner_text()
                class_details = page.locator("#state-result details", has_text="NASA classes or systems with indexed examples")
                assert class_details.count() == 1
                class_details.locator("summary").click()
                assert class_details.locator('a[href="#nasa-ocean-eddies"]').count() == 1
                assert class_details.locator('a[href="#nasa-agulhas-rings"]').count() == 2
                page.locator("#state-select").select_option("GFST")
                class_details = page.locator("#state-result details", has_text="NASA classes or systems with indexed examples")
                assert class_details.count() == 1
                class_details.locator("summary").click()
                assert class_details.locator('a[href="#nasa-global-overturning"]').count() == 1
                assert class_details.locator('a[href="#nasa-gulf-stream-deep-return"]').count() == 1
                page.locator("#state-select").select_option("TASM")
                assert "Tasman Front" in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("AUSE")
                assert "EDITORIAL NAMED CONTINUATION SKETCH CROSSING" in page.locator("#state-result").inner_text()
                assert page.locator('#state-result a[href="#current-tasman-front"]').count() == 1
                page.locator("#state-select").select_option("PSAE")
                assert "Haida-1998" in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("ALSK")
                assert "Kenai Eddy (2007)" in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("SARC")
                assert "East Greenland Coastal Current" in page.locator("#state-result").inner_text()
                assert page.locator('#state-result a[href*="north_1080.mp4"]', has_text="North polar perspective").count() == 1
                page.locator("#state-select").select_option("SANT")
                assert page.locator('#state-result a[href*="south_1080.mp4"]', has_text="South polar perspective").count() == 1
                page.locator("#state-select").select_option("CAMR")
                assert page.locator('#state-result a[href*="north_1080.mp4"]').count() == 0
                assert page.locator('#state-result a[href*="south_1080.mp4"]').count() == 0
                assert "96 Horizon Loop eddy names · shared Gulf source-region gateway" in page.locator("#state-result").inner_text()
                assert page.locator('#state-result a[href="#eddy-loop-77-primary"]').count() == 2
                published_center_details = page.locator("#state-result details", has_text="published Loop eddy center point")
                assert published_center_details.count() == 1
                published_center_details.locator("summary").click()
                assert "Berek" in published_center_details.inner_text()
                assert "no footprint or NASA identity claim" in published_center_details.inner_text()
                page.locator("#state-select").select_option("BRAZ")
                endpoint_details = page.locator("#state-result details", has_text="source-reported named-eddy point")
                assert endpoint_details.count() == 1
                endpoint_details.locator("summary").click()
                assert "Jeannette" in endpoint_details.inner_text()
                assert "track endpoint" in endpoint_details.inner_text()
                page.locator("#state-select").select_option("SSTC")
                first_detection_details = page.locator("#state-result details", has_text="source-reported named-eddy point")
                assert first_detection_details.count() == 1
                first_detection_details.locator("summary").click()
                assert "Lilian" in first_detection_details.inner_text()
                assert "first detection point" in first_detection_details.inner_text()
                page.locator("#state-select").select_option("BENG")
                assert page.locator('#state-result a[href="#eddy-geography-agulhas-eddy-w-2000"]').count() == 1
                assert "Agulhas Eddy W" in page.locator("#state-result").inner_text()
                for current_id, state_code in (("west-spitsbergen", "BPLR"), ("jutland", "NECS"), ("norwegian-coastal", "NECS")):
                    assert page.locator(f"#current-{current_id}").count() == 1
                    assert page.locator(f'#motion-markers a[href="#current-{current_id}"]').count() == 1
                    page.locator("#state-select").select_option(state_code)
                    assert current_id.replace("-", " ") in page.locator("#state-result").inner_text().lower()
                page.locator("#state-select").select_option("SANT")
                assert "Antarctic Coastal Current" in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("MEDI")
                for current_name in ("Algerian Current", "Balearic Current", "Western Adriatic Current", "Ligurian Current"):
                    assert current_name in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("NWCS")
                assert "Baffin Current" in page.locator("#state-result").inner_text()
                assert "Gaspé Current" in page.locator("#state-result").inner_text()
                assert "Greenland–Middle Atlantic shelf-current hypothesis" in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("CNRY")
                assert "Mauritanian Current" in page.locator("#state-result").inner_text()
                for state_code, current_name in (("PNEC", "Pacific Equatorial Undercurrent"), ("WTRA", "Atlantic Equatorial Undercurrent"), ("MONS", "Indian Ocean Equatorial Undercurrent")):
                    page.locator("#state-select").select_option(state_code)
                    assert current_name in page.locator("#state-result").inner_text()
                for state_code, current_name in (("CHIN", "Pacific North Equatorial Undercurrent"), ("WTRA", "Atlantic South Equatorial Undercurrent"), ("MONS", "Indian Ocean South Equatorial Undercurrent")):
                    page.locator("#state-select").select_option(state_code)
                    assert current_name in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("NAST E")
                assert "Azores Countercurrent" in page.locator("#state-result").inner_text()
                assert "Portugal Current" in page.locator("#state-result").inner_text()
                assert "Canary Current" in page.locator("#state-result").inner_text()
                page.locator("#state-select").select_option("KURO")
                assert page.locator('#state-result a[href="#nasa-kuroshio"]', has_text="Kuroshio").count() >= 1
                assert "nasa-identified current" in page.locator("#state-result").inner_text().lower()
                assert "schematic line crossing" in page.locator("#state-result").inner_text().lower()
                assert page.locator("#state-result .state-groups > div").filter(has_text="schematic line crossing").locator('a[href="#nasa-kuroshio"]').count() == 1
                page.locator("#state-select").select_option("AUSE")
                assert "editorial line crossing" in page.locator("#state-result").inner_text().lower()
                assert page.locator("#state-result .state-groups > div").filter(has_text="editorial line crossing").locator('a[href="#nasa-east-australian"]').count() == 1
                page.locator("#state-select").select_option("NAST W")
                assert "width-sensitive map contact" in page.locator("#state-result").inner_text().lower()
                assert page.locator("#state-result .state-groups > div").filter(has_text="width-sensitive map contact").locator('a[href="#nasa-gulf-stream"]').count() == 1
                assert page.locator("#nasa-western-boundary-rings").count() == 1
                assert page.locator('#motion-markers a[href="#nasa-western-boundary-rings"]').count() == 0
                assert page.locator('#motion-markers a[href="#nasa-agulhas-rings"]').count() == 1
                page.locator("#nasa-search").fill("Gulf")
                page.locator('#motion-markers a[href="#nasa-agulhas-rings"]').click()
                assert page.locator("#nasa-search").input_value() == ""
                assert page.locator("#nasa-agulhas-rings").is_visible()
                assert "> 2,000 km · unranked" in page.locator("#current-leeuwin").inner_text()
                assert page.locator('#motion-markers a[href="#current-leeuwin"]').count() == 1
                assert page.locator("#gulf-stream-fronts path").count() == 2
                assert page.locator("#gulf-stream-fronts").is_visible()
                assert page.locator("#geostrophic-streamline path").count() == 1
                assert "≈2,277 km" in page.locator("#geostrophic-reach-length").inner_text()
                page.locator("#show-geostrophic-streamline").uncheck()
                assert not page.locator("#geostrophic-streamline").is_visible()
                page.locator("#show-geostrophic-streamline").check()
                assert page.locator("#geostrophic-streamline").is_visible()
                assert page.locator("#operational-eddy-polygons path").count() == 4
                page.locator("#show-operational-eddy-polygons").uncheck()
                assert not page.locator("#operational-eddy-polygons").is_visible()
                page.locator("#show-operational-eddy-polygons").check()
                assert page.locator("#operational-eddy-polygons").is_visible()
                assert "≈5,088 km" in page.locator("#north-front-length").inner_text()
                assert "≈3,444 km" in page.locator("#south-front-length").inner_text()
                page.locator("#show-gulf-stream-fronts").uncheck()
                assert not page.locator("#gulf-stream-fronts").is_visible()
                page.locator("#show-gulf-stream-fronts").check()
                assert page.locator("#gulf-stream-fronts").is_visible()
                page.locator("#state-select").select_option("MEDI")
                assert "2011-12-02 to 2011-12-19 published local observation" in page.locator("#state-result .state-source-observation").inner_text()
                assert "Northern Current" in page.locator("#state-result .state-source-observation").inner_text()
                assert page.locator('#state-result .state-source-observation a[href="https://os.copernicus.org/articles/14/689/2018/"]').count() == 1
                page.locator("#state-select").select_option("NAST E")
                local_sections = page.locator("#state-result .state-source-observation")
                assert local_sections.count() == 4
                section_text = "\n".join(local_sections.all_inner_texts())
                for name in ("Canary Current", "Portugal Current", "Azores Current", "Azores Countercurrent"):
                    assert name in section_text
                assert "exact occupation dates" in section_text
                page.locator("#state-select").select_option("CNRY")
                assert page.locator("#state-result .state-source-observation").count() == 1
                assert "Canary Current" in page.locator("#state-result .state-source-observation").inner_text()
                page.locator("#state-select").select_option("NECS")
                assert page.locator("#state-result .state-source-observation").count() == 0
                page.locator("#state-select").select_option("GFST")
                assert "partial surface geostrophic streamline" in page.locator("#state-result .state-diagnosed-current-path").inner_text()
                assert "≈1,317 km" in page.locator("#state-result .state-diagnosed-current-path").inner_text()
                assert "1 dated NAVO operational eddy polygon" in page.locator("#state-result").inner_text()
                page.locator("#state-result .operational-eddy-details summary").click()
                assert "W26001" in page.locator("#state-result .operational-eddy-details").inner_text()
                assert "Gulf Stream" in page.locator("#state-result").inner_text()
                assert "3 of 100 named currents have atlas evidence here" in page.locator("#state-result").inner_text()
                assert "2026-09-28 analyzed surface front" in page.locator("#state-result").inner_text()
                assert "north wall (line segment intersection, ≈" in page.locator("#state-result").inner_text()
                assert "km of analyzed front in this atlas state" in page.locator("#state-result").inner_text()
                assert page.locator('#state-result a[href="object.html?id=current%3Agulf-stream-system"]').count() == 2
                assert "source arrow 57, 58" in page.locator("#state-result").inner_text()
                assert "source arrow 57, 58" in page.locator("#state-result .state-groups > div").filter(has_text="NASA-identified current · mapped arrow crossing").inner_text()
                assert "nasa-identified current" in page.locator("#state-result").inner_text().lower()
                assert "cartographic current arrows crossing" in page.locator("#state-result").inner_text().lower()
                assert page.locator("#state-result .state-movie-list a").count() == 8
                assert page.locator('#state-result .state-movie-list a[href*="#t="]').count() == 4
                assert all(href.endswith("#t=118.2") for href in page.locator('#state-result .state-movie-list a[href*="#t="]').evaluate_all("links => links.map(link => link.href)"))
                assert all("svs.gsfc.nasa.gov" in href for href in page.locator("#state-result .state-movie-list a").evaluate_all("links => links.map(link => link.href)"))
                assert "unknown" in page.locator("#state-result").inner_text()
                assert page.locator("#state-result details").count() - page.locator("#state-result .state-reference-routes details").count() == 8
                reference_join=json.loads((ROOT/'research/ocean-current-reference-route-state-join.json').read_text(encoding='utf-8'))
                expected_routes=reference_join['states']['GFST']['route_candidates']
                assert page.locator('#state-result .state-reference-routes li[data-candidate-id]').count()==len(expected_routes)
                for candidate in expected_routes:
                    item=page.locator(f'#state-result .state-reference-routes li[data-candidate-id="{candidate["candidate_id"]}"]')
                    assert item.locator('a').first.get_attribute('href')==candidate['route_url']
                assert 'not observed current passage' in page.locator('#state-result .state-reference-routes').inner_text()
                assert "unresolved" in page.locator("#state-result .nasa-unresolved-details summary").inner_text().lower()
                assert "2023-06-01" in page.locator("#state-result").inner_text()
                assert page.locator('#state-result .state-eddy-details a[href*="svs.gsfc.nasa.gov"][href*="#t="]').count() > 0
                assert page.locator('#state-result .state-eddy-details a', has_text="NASA crop").count() > 0
                page.locator("#show-state-eddies").check()
                assert page.locator("#detected-eddy-markers circle").count() > 0
                daily_contours = page.locator("#state-result details", has_text="Fully contained contours:")
                daily_contours.locator("summary").click()
                daily_contours.locator("button").first.click()
                assert page.locator("#selected-eddy-track path").count() == 1
                assert "seven-day file" in page.locator("#selected-track-summary").inner_text()
                assert page.locator('#selected-track-summary a[href*="#t=118.2"]').count() == 1
                weekly_visits = page.locator("#state-result details", has_text="NOAA weekly center visits")
                assert "weekly center visits" in weekly_visits.locator("summary").inner_text().lower()
                weekly_visits.locator("summary").click()
                weekly_visits.locator("button").first.click()
                assert page.locator("#selected-eddy-track path").count() == 1
                assert page.locator("#state-result details", has_text="Fully contained weekly contours").count() == 1
                assert page.locator("#state-result details", has_text="Weekly contours intersecting this state").count() == 1
                for date in ("2022-06-01", "2021-06-01"):
                    page.locator("#eddy-date-select").select_option(date)
                    assert date in page.locator("#state-result h4").all_inner_texts()[-1]
                    assert page.locator("#state-result details").count() - page.locator("#state-result .state-reference-routes details").count() == 8
                    assert page.locator("#detected-eddy-markers circle").count() > 0
                    assert page.locator("#selected-eddy-track path").count() == 0
                    weekly_visits = page.locator("#state-result details", has_text="NOAA weekly center visits")
                    assert date in weekly_visits.locator("summary").inner_text()
                    weekly_visits.locator("summary").click()
                    weekly_visits.locator("button").first.click()
                    assert page.locator("#selected-eddy-track path").count() == 1
                    assert "seven-day file" in page.locator("#selected-track-summary").inner_text()
                    assert page.locator('#state-result .state-movie-list a[href*="#t="]').count() == 0
                page.locator("#eddy-date-select").select_option("2023-06-01")
                assert page.locator("#state-result details").count() - page.locator("#state-result .state-reference-routes details").count() == 8
                assert page.locator("#eddy-date-select option").count() == 12
                for date in ("2023-12-01", "2021-03-01"):
                    page.locator("#eddy-date-select").select_option(date)
                    page.wait_for_function("date => [...document.querySelectorAll('#state-result h4')].some(node => node.textContent.includes(date))", arg=date)
                    assert page.locator("#state-result details").count() - page.locator("#state-result .state-reference-routes details").count() == 5
                    assert "June sample dates only" in page.locator("#selected-track-summary").inner_text()
                    assert page.locator("#detected-eddy-markers circle").count() > 0
                    assert page.locator("#selected-eddy-track path").count() == 0
                page.locator("#eddy-date-select").select_option("2023-06-01")
                page.wait_for_function("() => [...document.querySelectorAll('#state-result h4')].some(node => node.textContent.includes('2023-06-01'))")
                page.locator("#state-select").select_option("SUND")
                assert "2026-09-28 analyzed surface front" not in page.locator("#state-result").inner_text()
                gate_group = page.locator("#state-result .state-groups > div").filter(has_text="OSW schematic gate crossing")
                assert gate_group.locator('a[href="#nasa-indonesian-throughflow"]').count() == 1
                page.locator("#current-search").fill("Kuroshio")
                assert page.locator("#current-rows tr").count() == 2
                assert page.locator("#current-rows a", has_text="NASA region video").count() == 2
                object_page = browser.new_page()
                object_page.on("pageerror", lambda error: errors.append(str(error)))
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:acc", wait_until="networkidle")
                assert object_page.locator("#object-title").inner_text() == "Antarctic Circumpolar Current"
                assert object_page.get_by_role("combobox", name="Find an object").count() == 1
                assert object_page.get_by_role("button", name="Open object").count() == 1
                assert "25,000 km" in object_page.locator("#measurements").inner_text()
                assert "Rank 1 within the 11 published estimates" in object_page.locator("#measurements").inner_text()
                assert "Drawn map-arrow span: approximately 8,475 km" in object_page.locator("#measurements").inner_text()
                assert "linked claim records" in object_page.locator("#claim-audit").inner_text()
                assert "Individual claim review is pending" in object_page.locator("#claim-audit").inner_text()
                assert object_page.locator('#claim-audit a[href="release/v0.1.0/claims.csv"]').count() == 1
                assert object_page.locator("#observation-section").is_hidden()
                assert "56 unresolved relations" in object_page.locator("#relations").inner_text() or "unresolved relations" in object_page.locator("#relations").inner_text()
                assert object_page.locator("#identity a", has_text="Open almanac entry").get_attribute("href") == "index.html#current-acc"
                assert object_page.locator("#identity a", has_text="OSW source ledger").count() == 0
                slope_page = browser.new_page()
                slope_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:antarctic-slope", wait_until="networkidle")
                assert "21,000 km" in slope_page.locator("#measurements").inner_text()
                assert "Rank 2 within the 11 published estimates" in slope_page.locator("#measurements").inner_text()
                assert "Antarctic Peninsula" in slope_page.locator("#identity").inner_text()
                assert slope_page.locator("#classification-section").is_visible()
                assert slope_page.locator("#classifications dt").all_text_contents() == ["Fresh Shelf", "Dense Shelf", "Warm Shelf"]
                classification_text = slope_page.locator("#classifications").inner_text()
                assert "no observed regime or OSW state assignment is admitted" in classification_text
                assert "gamma_n" in classification_text and "0.5" in classification_text
                assert slope_page.locator('#classifications a[href="https://doi.org/10.1029/2018RG000624"]').count() == 1
                assert slope_page.locator('#relations a[href="object.html?id=current%3Aantarctic-coastal"]').count() == 1
                assert "geographic crop navigation only" in slope_page.locator("#media").inner_text()
                slope_page.close()
                ku = browser.new_page()
                ku.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:kuroshio", wait_until="networkidle")
                observed = ku.locator("#published-current-observations")
                assert "2018-01 to 2020-05" in observed.inner_text()
                assert "upper 50 m excluded" in observed.inner_text() and "malfunctioned" in observed.inner_text()
                assert observed.locator('a[href="object.html?id=state%3ACHIN"]').count() == 1
                assert "Instrument positions (longitude, latitude): 122.7, 18; 123, 18; 123.3, 18" in observed.inner_text()
                ku.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=state:CHIN", wait_until="networkidle")
                assert "2018-01 to 2020-05" in ku.locator("#published-current-observations").inner_text()
                assert ku.locator('#published-current-observations a[href="object.html?id=current%3Akuroshio"]').count() == 1
                ku.close()
                coastal_page = browser.new_page()
                coastal_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:alaska-coastal-gulf", wait_until="networkidle")
                assert "1989-05-10 to 1989-07-15" in coastal_page.locator("#published-current-observations").inner_text()
                assert "Shelikof Sea Valley" in coastal_page.locator("#published-current-observations").inner_text()
                assert "not an observed-geometry intersection" in coastal_page.locator("#published-current-observations").inner_text()
                coastal_page.close()
                object_page.locator("#object-search").fill("eddy:horizon:loop-81-primary")
                object_page.locator("#object-search").press("Enter")
                object_page.wait_for_url("**/almanac/object.html?id=eddy%3Ahorizon%3Aloop-81-primary")
                object_page.wait_for_function("document.querySelector('#object-title')?.textContent === 'Feldman'")
                assert object_page.locator("#object-title").inner_text() == "Feldman"
                assert "regional context only" in object_page.locator("#media").inner_text()
                assert "56 assessments across 56 OSW states; 1 has source-specific location evidence" in object_page.locator("#named-eddy-state-assessments").inner_text()
                assert "Verified whole-eddy containment or intersection: 0" in object_page.locator("#named-eddy-state-assessments").inner_text()
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=eddy:published:kraken-2013", wait_until="networkidle")
                assert object_page.locator("#footprint-section").is_visible()
                assert object_page.locator("#footprints svg path").count() == 1
                assert "robust across tested calibrations" in object_page.locator("#footprints").inner_text()
                assert "calibration sensitive candidate" in object_page.locator("#footprints").inner_text()
                assert "Containment unresolved" in object_page.locator("#footprints").inner_text()
                assert object_page.locator('#footprints a[href="object.html?id=state%3ACARB"]').count() == 1
                assert "2013-05-29 to 2013-12-15" in object_page.locator("#published-eddy-observations").inner_text()
                assert "state containment remains unresolved" in object_page.locator("#published-eddy-observations").inner_text()
                assert object_page.locator('#published-eddy-observations a[href="https://www.nature.com/articles/s41598-018-29582-5"]').count() == 1
                object_page.locator("#named-eddy-state-assessments summary").click()
                assert "figure derived red curve candidate" in object_page.locator("#named-eddy-state-assessments").inner_text()
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=state:CAMR", wait_until="networkidle")
                assert "state:CAMR" in object_page.locator("#identity").inner_text()
                assert object_page.locator("#identity a", has_text="Open almanac entry").get_attribute("href") == "index.html?state=CAMR"
                assert object_page.locator("#relations a[href*='object.html?id=current%3A']").count() > 0
                assert "point to exact OSW ledger rows" in object_page.locator("#claim-audit").inner_text()
                assert object_page.locator("#observation-rows tr").count() == 12
                assert "136 assessments across 136 named eddy records" in object_page.locator("#named-eddy-state-assessments").inner_text()
                assert object_page.locator('#named-eddy-state-assessments a[href*="named_eddy_state_assessments.csv"]').count() == 1
                assert object_page.get_by_role("table", name="NOAA daily eddy contour relations for this OSW state").count() == 1
                assert "2023-06-01" in object_page.locator("#observation-rows").inner_text()
                object_page.set_viewport_size({"width": 375, "height": 800})
                assert object_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:agulhas", wait_until="networkidle")
                assert object_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                assert "No comparable published-estimate rank" in object_page.locator("#measurements").inner_text()
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:leeuwin", wait_until="networkidle")
                assert "Source locator: PDF page 108" in object_page.locator("#measurements").inner_text()
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:northern-mediterranean", wait_until="networkidle")
                assert "2011-12-02 to 2011-12-19" in object_page.locator("#published-current-observations").inner_text()
                assert "whole-current path" in object_page.locator("#published-current-observations").inner_text()
                assert object_page.locator('#published-current-observations a[href="https://os.copernicus.org/articles/14/689/2018/"]').count() == 1
                assert "source reported local current presence" in object_page.locator("#relations").inner_text().lower() or "published local study" in object_page.locator("#relations").inner_text().lower()
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=state:MEDI", wait_until="networkidle")
                assert "Northern Current" in object_page.locator("#published-current-observations").inner_text()
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=state:NADR", wait_until="networkidle")
                assert "C26001" in object_page.locator("#operational-eddy-observations").inner_text()
                assert "C26002" in object_page.locator("#operational-eddy-observations").inner_text()
                assert object_page.locator("#operational-eddy-observations a", has_text="NAVO FREDDIES").count() == 2
                object_page.locator('#operational-eddy-observations a[href="object.html?id=navo-freddies%3A2026-09-25%3AC26001"]').click()
                object_page.wait_for_url("**/almanac/object.html?id=navo-freddies%3A2026-09-25%3AC26001")
                object_page.locator("#detection-detail svg").wait_for()
                assert "NAVO C26001" in object_page.locator("#object-title").inner_text()
                assert "not a match to this polygon" in object_page.locator("#detection-detail").inner_text()
                assert "Exact datum" in object_page.locator("#detection-detail").inner_text()
                assert "contained in approximate state" in object_page.locator("#detection-detail").inner_text()
                assert object_page.locator('#detection-detail a[href="object.html?id=state%3ANADR"]').count() == 1
                assert object_page.locator('#operational-eddy-observations a[href="object.html?id=state%3ANADR"]').count() == 1
                assert object_page.locator("#detection-detail svg path").count() == 2
                assert object_page.locator("#identity").inner_text().count("vertices") == 1
                object_page.locator("#detection-detail details").first.locator("summary").click()
                assert "not individually reviewed" in object_page.locator("#detection-detail details").first.inner_text()
                with object_page.expect_download() as detection_download:
                    object_page.locator("#detection-detail a[download]").click()
                packet = json.loads(Path(detection_download.value.path()).read_text(encoding="utf-8"))
                assert packet["entity"]["id"] == "navo-freddies:2026-09-25:C26001"
                assert packet["geometries"][0]["geometry"]["type"] == "Polygon"
                assert packet["state_observations"][0]["state_id"] == "state:NADR"
                assert packet["claims"][0]["subject_id"] == packet["entity"]["id"]
                assert packet["regional_movie_context"]["tiles"] and packet["regional_movie_context"]["claims"]
                packet_source_ids = {row["id"] for row in packet["sources"]}
                assert all(row["source_id"] in packet_source_ids for row in packet["regional_movie_context"]["tiles"])
                assert packet["geometries"][0]["source_snapshot_id"] in packet_source_ids
                assert any(row["rights_status"].startswith("pending") for row in packet["sources"])
                object_page.set_viewport_size({"width": 390, "height": 844})
                assert object_page.locator("#detection-detail").evaluate("node => node.getBoundingClientRect().right <= innerWidth")
                object_page.set_viewport_size({"width": 1280, "height": 900})
                object_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/object.html?id=current:gulf-stream-system", wait_until="networkidle")
                assert "2,277.3 km" in object_page.locator("#diagnosed-current-observations").inner_text()
                assert "37.125°N speed below threshold after 620 km" in object_page.locator("#diagnosed-current-observations").inner_text()
                assert "dated geostrophic streamline reach" in object_page.locator("#measurements").inner_text()
                assert "2026-09-28 north wall: 306 reported points, ≈5,088 km" in object_page.locator("#identity").inner_text()
                assert "2026-09-28 south wall: 204 reported points, ≈3,444 km" in object_page.locator("#identity").inner_text()
                assert "A dated analyzed surface front intersects" in object_page.locator("#relations").inner_text()
                assert "current passage unresolved" in object_page.locator("#relations").inner_text()
                object_page.close()
                movie_page = browser.new_page()
                movie_page.on("pageerror", lambda error: errors.append(str(error)))
                movie_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/movies.html", wait_until="networkidle")
                assert movie_page.locator("#movie-count").inner_text() == "70 of 70 crops"
                assert movie_page.locator("#movie-rows tr").count() == 70
                assert movie_page.get_by_role("combobox", name="OSW state").count() == 1
                assert movie_page.locator("#movie-state option").count() == 57
                movie_page.locator("#movie-state").select_option("state:BERS")
                assert 0 < movie_page.locator("#movie-rows tr").count() < 70
                assert movie_page.locator("#movie-level2_H_1").count() == 1
                movie_page.locator("#movie-level2_H_1 details").first.locator("summary").click()
                assert movie_page.locator('#movie-level2_H_1 a[href="object.html?id=state%3ABERS"]').count() == 1
                movie_page.locator("#movie-state").select_option("all")
                movie_page.locator("#movie-query").fill("level2_H_1")
                assert movie_page.locator("#movie-rows tr").count() == 1
                movie_page.locator("#movie-query").fill("")
                movie_page.locator("#movie-zoom").select_option("0")
                assert 0 < movie_page.locator("#movie-rows tr").count() < 70
                movie_page.set_viewport_size({"width": 375, "height": 800})
                assert movie_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                movie_page.close()
                route_catalog=json.loads((ROOT/'research/ocean-current-reference-path-candidates.json').read_text(encoding='utf-8'))
                route_counts=route_catalog['counts']
                routes_page = browser.new_page()
                routes_page.on("pageerror", lambda error: errors.append(str(error)))
                routes_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/reference-routes.html", wait_until="networkidle")
                width_inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
                width_count=width_inventory['counts']['measurements']
                routes_page.wait_for_function("count=>document.querySelector('#width-status').textContent.startsWith(count+' scoped')",arg=width_count)
                assert routes_page.locator('#width-rows tr').count() == width_count
                assert routes_page.locator('#width-decision-rows tr').count() == 100
                assert '25–40 km reported seasonal span' in routes_page.locator('#width-seasonal-northern-mediterranean').inner_text()
                assert 'not absolute annual extrema' in routes_page.locator('#width-seasonal-northern-mediterranean').inner_text()
                assert '25 km' in routes_page.locator('#width-northern-mediterranean-winter-width').inner_text()
                assert '40 km' in routes_page.locator('#width-northern-mediterranean-summer-width').inner_text()
                balearic_width = routes_page.locator('#width-decision-balearic')
                routes_page.get_by_text('Width coverage for all 100 names', exact=True).click()
                assert 'upwelled-water region' in balearic_width.inner_text()
                assert balearic_width.locator('a[href*="18176.pdf"]').count() == 1
                assert f"{width_inventory['counts']['currents_with_sources_reviewed_no_numeric_width']} reviewed without a comparable numeric current width" in routes_page.locator('#width-status').inner_text()
                antilles_width = routes_page.locator('#width-decision-antilles')
                assert 'transport integration domain' in antilles_width.inner_text()
                assert antilles_width.locator('a[href*="noaa_20909_DS1.pdf"]').count() == 1
                seasons_page = browser.new_page()
                seasons_page.on("pageerror", lambda error: errors.append(str(error)))
                seasons_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/seasons.html", wait_until="networkidle")
                assert seasons_page.locator('#season-current option').count() == 100
                assert 'about 25 km' in seasons_page.locator('#season-value').inner_text()
                assert 'Seasonal length: unknown' in seasons_page.locator('#season-length').inner_text()
                seasons_page.locator('#season-play').click()
                seasons_page.wait_for_function("document.querySelector('#season-value').textContent.includes('about 40 km')")
                seasons_page.locator('#season-play').click()
                assert 'not absolute annual extrema' in seasons_page.locator('#season-range').inner_text()
                assert seasons_page.locator('#season-map').evaluate("el => el.complete && el.naturalWidth > 0")
                seasons_page.locator('#season-current').select_option('somali')
                assert 'southward' in seasons_page.locator('#season-value').inner_text()
                assert '1,500 km' in seasons_page.locator('#season-length').inner_text()
                assert 'somali-winter' in seasons_page.locator('#season-map').get_attribute('src')
                assert 'different source-defined spatial scopes' in seasons_page.locator('#season-range').inner_text()
                seasons_page.locator('#season-play').click()
                seasons_page.wait_for_function("document.querySelector('#season-value').textContent.includes('northward')")
                seasons_page.locator('#season-play').click()
                assert '600 km' in seasons_page.locator('#season-length').inner_text()
                assert 'somali-summer-southern' in seasons_page.locator('#season-map').get_attribute('src')
                assert 'not the full summer Somali Current system' in seasons_page.locator('#season-map-note').inner_text()
                assert 'Width: unknown' in seasons_page.locator('#season-definition').inner_text()
                seasons_page.locator('#season-current').select_option('azores')
                assert 'about 110 km' in seasons_page.locator('#season-value').inner_text()
                assert '26 Oct' in seasons_page.locator('#season-phase').inner_text()
                assert '0–150 km' in seasons_page.locator('#season-definition').inner_text()
                assert 'meridional section' in seasons_page.locator('#season-definition').inner_text()
                assert 'caption says fall 2010' in seasons_page.locator('#season-definition').inner_text()
                assert seasons_page.locator('#season-play').is_disabled()
                assert 'single dated section' in seasons_page.locator('#season-range').inner_text()
                seasons_page.locator('#season-current').select_option('mediterranean-undercurrent')
                assert seasons_page.locator('#season-phase option').count() == 2
                assert 'about 30 km' in seasons_page.locator('#season-value').inner_text()
                assert 'one-sided' in seasons_page.locator('#season-value').inner_text()
                assert 'not width uncertainty' in seasons_page.locator('#season-definition').inner_text()
                assert seasons_page.locator('#season-play').is_disabled()
                assert 'not seasonal phases' in seasons_page.locator('#season-range').inner_text()
                seasons_page.locator('#season-phase').select_option('1')
                assert 'about 10 km' in seasons_page.locator('#season-value').inner_text()
                assert 'May 1993' in seasons_page.locator('#season-phase').inner_text()
                assert seasons_page.locator('#season-play').is_disabled()
                seasons_page.locator('#season-current').select_option('davidson')
                assert 'about 64 km' in seasons_page.locator('#season-value').inner_text()
                assert '1978 regional summary' in seasons_page.locator('#season-phase').inner_text()
                assert 'California and Oregon' in seasons_page.locator('#season-definition').inner_text()
                assert 'not a present-day width measurement' in seasons_page.locator('#season-definition').inner_text()
                assert 'April-September width' in seasons_page.locator('#season-range').inner_text()
                assert seasons_page.locator('#season-play').is_disabled()
                assert seasons_page.locator('#season-phase option').count() == 1
                assert '1,300 km' in seasons_page.locator('#season-length').inner_text()
                assert 'not applied uniformly' in seasons_page.locator('#season-definition').inner_text()
                assert 'davidson-winter' in seasons_page.locator('#season-map').get_attribute('src')
                assert seasons_page.locator('#season-map').evaluate('el => el.complete && el.naturalWidth > 0')
                seasons_page.locator('#season-current').select_option('balearic')
                assert 'not available' in seasons_page.locator('#season-value').inner_text()
                assert seasons_page.locator('#season-play').is_disabled()
                assert 'balearic-reference-path' in seasons_page.locator('#season-map').get_attribute('src')
                assert 'Static route context' in seasons_page.locator('#season-map-note').inner_text()
                seasons_page.locator('#season-current').select_option('portugal')
                assert seasons_page.locator('#season-play').is_disabled()
                assert 'Static reference route source' in seasons_page.locator('#season-source').inner_text()
                assert 'Seasonal length: unknown' in seasons_page.locator('#season-length').inner_text()
                assert 'Portugal Coastal Countercurrent' in seasons_page.locator('#season-map-note').inner_text()
                seasons_page.locator('#season-current').select_option('gaspe')
                assert '10–20 km reported typical regional range' in seasons_page.locator('#season-value').inner_text()
                assert 'No midpoint' in seasons_page.locator('#season-range').inner_text()
                assert seasons_page.locator('#season-bar').locator('..').is_hidden()
                assert seasons_page.locator('#season-play').is_disabled()
                assert 'gaspe-reference-path' in seasons_page.locator('#season-map').get_attribute('src')
                assert 'Static route context' in seasons_page.locator('#season-map-note').inner_text()
                seasons_page.set_viewport_size({'width':320,'height':900})
                assert seasons_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                seasons_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/seasons.html?current=somali", wait_until="networkidle")
                assert seasons_page.locator('#season-current').input_value() == 'somali'
                assert 'southward' in seasons_page.locator('#season-value').inner_text()
                dated_page = browser.new_page()
                dated_page.on("pageerror", lambda error: errors.append(str(error)))
                dated_page.goto(f"http://127.0.0.1:{server.server_port}/almanac/dated-current.html?series=2026", wait_until="networkidle")
                assert dated_page.locator('#dated-phase option').count() == 5
                assert 'truncated diagnostic' in dated_page.locator('#dated-value').inner_text()
                assert 'does not measure the current endpoint' in dated_page.locator('#dated-stop').inner_text()
                assert '5 intervening days' in dated_page.locator('#dated-gap').inner_text()
                assert dated_page.locator('#dated-map').evaluate("el => el.complete && el.naturalWidth > 0")
                first_map = dated_page.locator('#dated-map').get_attribute('src')
                dated_page.locator('#dated-play').click()
                dated_page.wait_for_function("document.querySelector('#dated-value').textContent.includes('2026-09-24')")
                dated_page.locator('#dated-play').click()
                assert 'gate-reaching diagnostic' in dated_page.locator('#dated-value').inner_text()
                assert '5 intervening days' in dated_page.locator('#dated-gap').inner_text()
                assert dated_page.locator('#dated-map').get_attribute('src') != first_map
                assert dated_page.locator('#dated-state-list a').count() > 0
                assert 'index.html?state=' in dated_page.locator('#dated-state-list a').first.get_attribute('href')
                dated_page.locator('#dated-phase').select_option('4')
                assert '2026-09-27' in dated_page.locator('#dated-value').inner_text()
                assert 'unknown' in dated_page.locator('#dated-width-range').inner_text()
                dated_page.set_viewport_size({'width':320,'height':900})
                assert dated_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                dated_page.locator('#dated-series').select_option('2025')
                dated_page.wait_for_function("document.querySelector('#dated-phase').options.length === 12")
                assert '2025-01-15' in dated_page.locator('#dated-value').inner_text()
                assert 'RADS 4.7.0' in dated_page.locator('#dated-version').inner_text()
                assert 'Processing version changes' in dated_page.locator('#dated-version').inner_text()
                dated_page.locator('#dated-phase').select_option('7')
                assert 'RADS 4.7.1' in dated_page.locator('#dated-version').inner_text()
                assert 'gate-reaching diagnostic' in dated_page.locator('#dated-value').inner_text()
                dated_page.locator('#dated-phase').select_option('11')
                assert 'distance cap' in dated_page.locator('#dated-stop').inner_text()
                assert 'circulate near its seed' in dated_page.locator('#dated-stop').inner_text()
                assert '0 of 9' in dated_page.locator('#dated-sensitivity').inner_text()
                assert 'No successful gate-reaching span' in dated_page.locator('#dated-sensitivity').inner_text()
                assert '4,000 km' in dated_page.locator('#dated-value').inner_text()
                assert dated_page.locator('#dated-scenario-rows tr').count() == 9
                dated_page.locator('#dated-phase').select_option('6')
                assert '9 of 9' in dated_page.locator('#dated-sensitivity').inner_text()
                assert 'about 70 km' in dated_page.locator('#dated-width').inner_text()
                assert 'meridional half-peak eastward-velocity span' in dated_page.locator('#dated-width').inner_text()
                assert 'resolution review required' in dated_page.locator('#dated-width').inner_text()
                assert '50–80 km' in dated_page.locator('#dated-width-range').inner_text()
                assert 'not statistical uncertainty' in dated_page.locator('#dated-width-range').inner_text()
                assert '70–150 km across 12 daily samples' in dated_page.locator('#dated-width-samples').inner_text()
                assert 'not annual extrema' in dated_page.locator('#dated-width-samples').inner_text()

                assert '3,480–3,690 km' in dated_page.locator('#dated-sensitivity').inner_text()
                assert 'not a confidence interval' in dated_page.locator('#dated-sensitivity').inner_text()
                dated_page.locator('details summary').click()

                assert dated_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                assert 'timeline-2025.json' in dated_page.locator('#dated-download').get_attribute('href')
                dated_page.close()
                seasons_page.close()
                assert f"{route_counts['route_candidates']} route candidates for {route_counts['currents_with_route_candidates']} of 89 currents; {route_counts['currents_without_route_candidates']} currents await routes" in routes_page.locator("#route-status").inner_text()
                assert routes_page.locator("#reference-route-rows tr").count() == sum(row["comparison_group"] == "osw_approximate_reference_routes" for row in route_catalog["candidates"])
                davidson = routes_page.locator('#davidson-winter-reference-path-candidate')
                assert '1,300 km' in davidson.inner_text() and '1,200–1,400 km' in davidson.inner_text()
                assert 'bookkeeping gates' in davidson.inner_text()
                assert '1978' in davidson.inner_text()
                assert davidson.locator('a[href*="level2_A_2.mp4"]').count() == 1
                tsushima = routes_page.locator('#tsushima-coastal-reference-path-candidate')
                assert '1,300 km' in tsushima.inner_text() and '1,100–1,300 km' in tsushima.inner_text()
                assert 'Japanese coastal-branch' in tsushima.inner_text()
                assert 'uninterrupted flow' in tsushima.inner_text()
                assert tsushima.locator('a[href*="2016JC011891"]').count() >= 1
                assert tsushima.locator('a[href*="level2_F_2.mp4"]').count() == 1
                balearic = routes_page.locator('#balearic-reference-path-candidate')
                assert '400 km' in balearic.inner_text() and '300–400 km' in balearic.inner_text()
                assert 'upstream mainland Northern Current' in balearic.inner_text()
                assert balearic.locator('a[href*="18176.pdf"]').count() >= 1
                assert balearic.locator('a[href*="level2_C_2.mp4"]').count() == 1
                norwegian_coastal = routes_page.locator('#norwegian-coastal-reference-path-candidate')
                assert '2,100 km' in norwegian_coastal.inner_text() and '2,000–2,200 km' in norwegian_coastal.inner_text()
                assert 'fjord circuits' in norwegian_coastal.inner_text() and 'No whole connected-system length' in norwegian_coastal.inner_text()
                assert norwegian_coastal.locator('a[href*="gmd.copernicus.org/articles/19/2785/2026"]').count() >= 1
                assert norwegian_coastal.locator('a[href*="level2_D_1.mp4"]').count() == 1
                azores_route = routes_page.locator('#azores-reference-path-candidate')
                assert '3,600 km' in azores_route.inner_text() and '3,300–3,700 km' in azores_route.inner_text()
                assert 'Azores Countercurrent' in azores_route.inner_text() and 'Gibraltar/Mediterranean inflow' in azores_route.inner_text()
                assert azores_route.locator('a[href*="842251"]').count() >= 1
                assert azores_route.locator('a[href*="level2_C_2.mp4"]').count() == 1
                wsc = routes_page.locator('#west-spitsbergen-reference-path-candidate')
                assert '800 km' in wsc.inner_text() and '600–900 km' in wsc.inner_text()
                assert 'shelf/fjord intrusions' in wsc.inner_text() and 'pre-branching gate' in wsc.inner_text()
                assert wsc.locator('a[href*="2017JC013553"]').count() >= 1
                assert wsc.locator('a[href*="level2_C_1.mp4"]').count() == 1
                for branch in ['svalbard-branch', 'yermak-branch', 'yermak-pass-branch']:
                    proposal = routes_page.locator(f'#inventory-addition-{branch}')
                    assert 'named Atlantic-water current branch' in proposal.inner_text()
                    assert 'no whole-current length or rank admitted' in proposal.inner_text()
                    assert proposal.locator('a[href*="2018JC014299"]').count() == 1
                portugal = routes_page.locator('#portugal-reference-path-candidate')
                assert '1,400 km' in portugal.inner_text() and '1,100–1,800 km' in portugal.inner_text()
                assert 'Portugal Coastal Countercurrent' in portugal.inner_text()
                assert 'not uniquely locate' in portugal.inner_text()
                assert portugal.locator('a[href*="010038152.pdf"]').count() >= 1
                assert portugal.locator('a[href*="level2_C_2.mp4"]').count() == 1
                canary = routes_page.locator('#canary-reference-path-candidate')
                assert '1,700 km' in canary.inner_text() and '1,500–1,800 km' in canary.inner_text()
                assert 'Cape Blanc' in canary.inner_text() and 'Lanzarote Passage recirculation' in canary.inner_text()
                assert canary.locator('a[href*="os.copernicus.org/articles/14/971/2018"]').count() >= 1
                assert canary.locator('a[href*="level2_C_3.mp4"]').count() == 1
                cipu = routes_page.locator('#inventory-addition-canary-intermediate-poleward-undercurrent')
                assert 'intermediate-layer poleward undercurrent' in cipu.inner_text()
                assert 'no whole-current length or rank admitted' in cipu.inner_text()
                assert cipu.locator('a[href*="2022JC019487"]').count() >= 1
                gaspe = routes_page.locator('#gaspe-reference-path-candidate')
                assert '500 km' in gaspe.inner_text() and '400–500 km' in gaspe.inner_text()
                assert 'Magdalen' in gaspe.inner_text()
                assert gaspe.locator('a[href*="Theau_Leclercq_fevrier2022.pdf"]').count() >= 1
                assert gaspe.locator('a[href*="level2_B_1.mp4"]').count() == 1
                assert "4,700 km" in routes_page.locator("#reference-route-rows tr").first.inner_text()
                jutland = routes_page.locator('#jutland-reference-path-candidate')
                assert '400 km' in jutland.inner_text() and '400–500 km' in jutland.inner_text()
                assert 'No North/South Jutland branch lengths or aliases admitted' in jutland.inner_text()
                assert 'sea-level seasonality is not a current-length measurement' in jutland.inner_text()
                assert jutland.locator('a[href*="level2_C_1.mp4"]').count() == 1
                np = routes_page.locator('#north-pacific-reference-path-candidate')
                assert '3,900–5,000 km' in np.inner_text() and 'NOAA glossary regional extent' in np.inner_text()
                assert 'different western origin near 170 degrees W' in np.inner_text()
                assert np.locator('a[href*="level2_H_2.mp4"]').count() == 1
                ke = routes_page.locator('#kuroshio-extension-reference-path-candidate')
                assert '1,400 km' in ke.inner_text() and '1,100–1,600 km' in ke.inner_text()
                assert 'not a universal termination rule' in ke.inner_text()
                assert ke.locator('a[href*="level2_G_2.mp4"]').count() == 1
                nac = routes_page.locator('#north-atlantic-reference-path-candidate')
                assert '3,300 km' in nac.inner_text() and '3,100–3,500 km' in nac.inner_text()
                assert 'entire branching Gulf Stream System' in nac.inner_text()
                assert nac.locator('a[href*="level2_C_2.mp4"]').count() == 1
                alaska = routes_page.locator('#alaska-reference-path-candidate')
                assert '1,400 km' in alaska.inner_text() and '700–1,700 km' in alaska.inner_text()
                assert 'distinct nearshore Alaska Coastal Current' in alaska.inner_text()
                assert 'northern/northwestern Alaskan Stream' in alaska.inner_text()
                assert alaska.locator('a[href*="level2_A_1.mp4"]').count() == 1
                assert "400 km" in routes_page.locator("#reference-route-rows tr").last.inner_text()
                leeuwin = routes_page.locator('#leeuwin-reference-path-candidate')
                assert "2,900 km" in leeuwin.inner_text() and "2,400–3,000 km" in leeuwin.inner_text()
                assert "Not the full 5,500 km boundary-flow system" in leeuwin.inner_text()
                for route_id, envelope in [('south-australian', '700–1,100 km'), ('zeehan', '500–900 km')]:
                    card = routes_page.locator(f'#{route_id}-reference-path-candidate')
                    assert "800 km" in card.inner_text() and envelope in card.inner_text()
                    assert 'winter' in card.inner_text().lower()
                zeehan_order = routes_page.locator('#comparison-zeehan-reference-path-candidate')
                assert "Positions 23–36" in zeehan_order.inner_text()
                zeehan_order.locator('summary').click()
                assert zeehan_order.locator('a', has_text='South Australian Current').is_visible()
                assert 'Positions 1–3 within retained envelopes' in routes_page.locator('#reference-route-rows tr').first.locator('td').nth(3).inner_text()
                agulhas = routes_page.locator('#agulhas-reference-path-candidate')
                assert "1,800–2,200 km" in agulhas.inner_text()
                assert "stops before the eastward Agulhas Return Current" in agulhas.inner_text()
                dwbc = routes_page.locator('#deep-western-boundary-reach-reference-path-candidate')
                assert "4,100 km" in dwbc.inner_text() and "3,900–4,200 km" in dwbc.inner_text()
                assert dwbc.locator('.warning').count() == 1
                assert "Deep Western Boundary Current" not in routes_page.locator('#reference-route-rows').inner_text()
                greenland = routes_page.locator("#comparison-east-greenland-reference-path-candidate")
                assert "2,700 km" in greenland.inner_text()
                assert "59 degrees N" in greenland.inner_text()
                assert "Excludes a distinct East Greenland Coastal Current axis" in greenland.inner_text()
                brazil = routes_page.locator("#comparison-brazil-reference-path-candidate")
                assert "3,200 km" in brazil.inner_text() and "2,600–4,200 km" in brazil.inner_text()
                benguela = routes_page.locator("#comparison-benguela-reference-path-candidate")
                assert "2,500 km" in benguela.inner_text() and "shelf-edge" in benguela.inner_text()
                assert routes_page.locator('#brazil-reference-path-candidate a[href="https://os.copernicus.org/articles/14/417/2018/"]').count() == 1
                assert routes_page.locator('#benguela-reference-path-candidate a[href*="1520-0485_2000_030_2589"]').count() == 1
                assert routes_page.locator('#comparison-agulhas-return-reach-reference-path-candidate').count() == 0
                assert 'WGS84 geodesics' in routes_page.locator('#measurement-rules-title + p').inner_text()
                assert routes_page.locator('a[href="../plans/ocean-current-measurement-protocol-v1.md"]').count() == 1
                wac = routes_page.locator('#western-adriatic-reference-path-candidate')
                assert '700 km' in wac.inner_text() and '700–800 km' in wac.inner_text()
                assert 'deep dense-water pathways' in wac.inner_text()
                assert 'not observed named-flow termination bounds' in wac.inner_text()
                assert 'not a simultaneous drifter trajectory' in wac.inner_text().lower()
                assert wac.locator('a[href*="level2_C_2.mp4"]').count() == 1
                assert wac.locator('a[href*="os-9-713-2013.pdf"]').count() == 1
                guinea = routes_page.locator('#guinea-reference-path-candidate')
                assert '1,200 km' in guinea.inner_text() and '1,000–1,200 km' in guinea.inner_text()
                assert 'not the full Guinea Current extent' in guinea.inner_text()
                assert 'not observed endpoint bounds' in guinea.inner_text()
                assert guinea.locator('a[href*="level2_C_3.mp4"]').count() == 1
                for addition_id in ['guinea-countercurrent', 'guinea-undercurrent']:
                    addition = routes_page.locator(f'#inventory-addition-{addition_id}')
                    assert addition.locator('a[href*="fmars.2020.607216"]').count() == 1
                    assert routes_page.locator(f'#decision-{addition_id}').count() == 0
                hiri = routes_page.locator('#hiri-reference-path-candidate')
                assert '1,900 km' in hiri.inner_text() and '1,900–2,500 km' in hiri.inner_text()
                assert 'Narrower literature uses Hiri only south of PNG' in hiri.inner_text()
                assert 'not equivalent-depth observations' in hiri.inner_text()
                for addition_id in ['gulf-of-papua', 'north-queensland', 'great-barrier-reef-undercurrent']:
                    addition = routes_page.locator(f'#inventory-addition-{addition_id}')
                    assert addition.locator('a[href*="2013JC009678"]').count() == 1
                    assert routes_page.locator(f'#decision-{addition_id}').count() == 0
                oyashio = routes_page.locator('#oyashio-reference-path-candidate')
                assert '1,000 km' in oyashio.inner_text() and '700–1,200 km' in oyashio.inner_text()
                assert 'temperature-defined intrusion index is not a velocity axis' in oyashio.inner_text()
                assert 'not an annual-mean endpoint' in oyashio.inner_text()
                assert 'offshore return branch into Subarctic Current' in oyashio.inner_text()
                nbc = routes_page.locator('#north-brazil-reference-path-candidate')
                assert '2,200 km' in nbc.inner_text() and '1,800–2,500 km' in nbc.inner_text()
                assert 'upstream North Brazil Undercurrent' in nbc.inner_text()
                assert 'outside this finite scenario set' in nbc.inner_text()
                guiana_plan = routes_page.locator('#decision-guiana')
                assert 'Resolve Guiana/Guyana naming' in guiana_plan.inner_text()
                assert 'Clarify naming' in guiana_plan.inner_text() or 'naming' in guiana_plan.inner_text().lower()
                caribbean = routes_page.locator('#caribbean-reference-path-candidate')
                assert '2,800 km' in caribbean.inner_text() and '2,500–2,800 km' in caribbean.inner_text()
                assert 'Excludes the northward Yucatan Current' in caribbean.inner_text()
                assert caribbean.locator('a[href*="level2_B_3.mp4"]').count() == 1
                mindanao = routes_page.locator('#mindanao-reference-path-candidate')
                assert '1,000 km' in mindanao.inner_text() and '800–1,200 km' in mindanao.inner_text()
                assert 'Near-surface gate convention only' in mindanao.inner_text()
                assert 'not the full seasonal velocity axis' in mindanao.inner_text()
                baffin = routes_page.locator('#baffin-reach-reference-path-candidate')
                assert '1,200 km' in baffin.inner_text() and '1,100–1,300 km' in baffin.inner_text()
                assert 'they are not whole-current endpoints' in baffin.inner_text()
                assert baffin.locator('.warning').count() == 1
                assert routes_page.locator('#comparison-baffin-reach-reference-path-candidate').count() == 0
                irminger = routes_page.locator('#irminger-reference-path-candidate')
                assert '1,200 km' in irminger.inner_text() and '700–1,400 km' in irminger.inner_text()
                assert 'North Icelandic Irminger continuation' in irminger.inner_text()
                for card in [baffin, irminger]:
                    assert card.locator('a[href*="level2_B_1.mp4"]').count() == 1
                niic = routes_page.locator('#inventory-addition-north-icelandic-irminger')
                assert 'not all waters follow one continuous upstream parcel route' in niic.inner_text()
                assert routes_page.locator('#decision-north-icelandic-irminger').count() == 0
                labrador = routes_page.locator('#labrador-reference-path-candidate')
                assert '2,100 km' in labrador.inner_text() and '1,800–2,400 km' in labrador.inner_text()
                assert 'inshore Avalon branch' in labrador.inner_text()
                assert labrador.locator('a[href*="level2_B_2.mp4"]').count() == 1
                west_greenland = routes_page.locator('#west-greenland-reference-path-candidate')
                assert '1,100 km' in west_greenland.inner_text() and '900–1,300 km' in west_greenland.inner_text()
                assert 'separate inshore West Greenland Coastal Current' in west_greenland.inner_text()
                assert west_greenland.locator('a[href*="level2_B_1.mp4"]').count() == 1
                coastal_addition = routes_page.locator('#inventory-addition-west-greenland-coastal')
                assert 'coastal shelf current' in coastal_addition.inner_text()
                assert 'no whole-current length or rank admitted' in coastal_addition.inner_text()
                proposal_count = len(json.loads((ROOT / 'research/ocean-current-inventory-expansion-candidates.json').read_text(encoding='utf-8'))['entries'])
                assert f'{proposal_count} proposed inventory additions' in routes_page.locator('#inventory-addition-status').inner_text()
                for current_id in ['tsugaru-warm', 'soya-warm', 'east-korea-warm', 'north-korea-cold']:
                    addition = routes_page.locator(f'#inventory-addition-{current_id}')
                    assert 'no whole-current length or rank admitted' in addition.inner_text()
                    assert addition.locator('a').count() >= 1
                winter = routes_page.locator('#somali-winter-reference-path-candidate')
                assert '1,500 km' in winter.inner_text() and '1,100–1,800 km' in winter.inner_text()
                assert 'Northeast winter monsoon' in winter.inner_text()
                summer = routes_page.locator('#somali-summer-southern-reference-path-candidate')
                assert '600 km' in summer.inner_text() and '500–700 km' in summer.inner_text()
                assert 'not the full summer Somali Current system' in summer.inner_text()
                for card in [winter, summer]:
                    assert card.locator('a[href*="level2_D_4.mp4"]').count() == 1
                addition = routes_page.locator('#inventory-addition-mozambique')
                assert 'intermittent coastal current regime' in addition.inner_text()
                assert 'not a persistent whole-current length' in addition.inner_text()
                assert addition.locator('a[href*="2008JC004846"]').count() == 1
                assert routes_page.locator('#decision-mozambique').count() == 0
                assert 'undefined' not in routes_page.locator('#route-cards').inner_text()
                northern = routes_page.locator('#northern-mediterranean-reference-path-candidate')
                assert '700 km' in northern.inner_text() and '600–800 km' in northern.inner_text()
                assert 'not the two-week December 2011 Toulon survey' in northern.inner_text()
                assert northern.locator('a[href="https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2021JC017589"]').count() == 1
                algerian = routes_page.locator('#algerian-reference-path-candidate')
                assert '900 km' in algerian.inner_text() and '600–900 km' in algerian.inner_text()
                assert 'detached Algerian eddies' in algerian.inner_text()
                for card in [northern, algerian]:
                    assert card.locator('a[href*="level2_C_2.mp4"]').count() == 1
                assert routes_page.locator("#route-queue-rows tr").count() == 89
                routes_page.locator("#route-coverage").select_option("unbuilt")
                assert routes_page.locator("#route-queue-rows tr").count() == route_counts["currents_without_route_candidates"]
                routes_page.locator("#route-coverage").select_option("candidate")
                assert routes_page.locator("#route-queue-rows tr").count() == route_counts["currents_with_route_candidates"]
                routes_page.locator('#route-coverage').select_option('all')
                assert routes_page.locator('#strategy-rows tr').count() == 10
                routes_page.locator('#route-strategy').select_option('split_basin_family')
                assert routes_page.locator('#route-queue-rows tr').count() == 8
                family = routes_page.locator('#decision-equatorial-undercurrent')
                assert 'Split basin families' in family.inner_text()
                family.locator('summary').click()
                assert family.locator('a[href="object.html?id=current%3Apacific-equatorial-undercurrent"]').is_visible()
                assert 'Basin-member records have not yet been added' in routes_page.locator('#decision-north-equatorial').inner_text()
                assert 'does not mean the flows are absent' in routes_page.locator('#decision-south-equatorial').inner_text()
                routes_page.locator('#route-coverage').select_option('candidate')
                assert routes_page.locator('#route-queue-rows tr').count() == 0
                assert '0 of 89' in routes_page.locator('#queue-count').inner_text()
                routes_page.locator('#route-coverage').select_option('all')
                routes_page.locator('#route-strategy').select_option('continuity_hypothesis')
                assert routes_page.locator('#route-queue-rows tr').count() == 1
                assert 'hypothetical status' in routes_page.locator('#route-queue-rows').inner_text()
                routes_page.locator('#route-strategy').select_option('seasonal_routes')
                assert routes_page.locator('#route-queue-rows tr').count() == 14
                routes_page.locator('#route-strategy').select_option('all')
                routes_page.locator('#route-query').fill('Bab el Mandeb')
                assert routes_page.locator('#route-queue-rows tr').count() == 1
                assert 'Red Sea' in routes_page.locator('#route-queue-rows').inner_text()
                routes_page.locator('#route-query').fill('')
                assert routes_page.locator('#route-queue-rows tr').count() == 89
                assert routes_page.locator('#agulhas-return-reach-reference-path-candidate .warning').count() == 1
                assert routes_page.locator('#east-australian-reference-path-candidate a[href*="level2_F_5.mp4"]').count() == 1
                assert routes_page.locator('#agulhas-return-extent-reference-path-candidate a[href*="level1_B_3.mp4"]').count() == 1
                for image in routes_page.locator(".route-map").all():
                    assert image.evaluate("el => el.complete && el.naturalWidth > 0")
                routes_page.set_viewport_size({"width": 320, "height": 900})
                assert routes_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                if screenshot := os.environ.get("OSW_REFERENCE_ROUTES_SCREENSHOT"):
                    routes_page.locator('#agulhas-return-extent-reference-path-candidate').screenshot(path=screenshot)
                routes_page.close()
                if screenshot := os.environ.get("OSW_MOTION_SCREENSHOT"):
                    page.screenshot(path=screenshot, full_page=True)
                assert not errors, errors
                print("OK: browser rendered currents, eddies, NASA objects, all 56 states, and map links")
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
