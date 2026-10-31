"""Cloud-only route/card/query navigation and actual desktop/mobile captures."""
import functools
import hashlib
import http.server
import json
import os
import threading
from urllib.parse import quote

import pacific_secc_publication_admission_v1 as admission
from eicc_reference_browser_values_v3 import same


def browser_review(root, output):
    from check_south_java_model_layer_cloud_v1 import cloud_environment
    cloud_environment(dict(os.environ))  # Before browser/server startup.
    if os.environ.get('OSW_PACIFIC_SECC_DELIVERY_V1') != '1':
        raise ValueError('Exact Pacific delivery browser phase required')
    from playwright.sync_api import sync_playwright, expect
    q = admission.query
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    errors, originals, missing, screenshots, checked = [], [], [], [], []
    def write(name, value):
        (output / name).write_bytes((json.dumps(value, indent=2) + '\n').encode())
    def capture(locator, name):
        path = output / name; locator.screenshot(path=str(path))
        screenshots.append({'path': name, 'bytes': path.stat().st_size,
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    def wait_atlas(page):
        page.wait_for_function('(id)=>window.oswAtlasSnapshot?.working_reference_routes?.candidates.some(r=>r.id===id)', arg=q.ROUTE)
        expect(page.locator('#route-atlas-select')).to_have_value(q.TARGET)
        expect(page.locator('#route-atlas-status')).to_contain_text('Pacific South Equatorial Countercurrent')
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--renderer-process-limit=1'])
            page = browser.new_page(viewport={'width': 1100, 'height': 950}); page.set_default_timeout(180000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda req: originals.append(req.url) if req.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
            page.on('response', lambda response: missing.append({'url': response.url, 'status': response.status})
                    if response.url.startswith(base) and response.status >= 400 and not response.url.endswith('/favicon.ico') else None)
            page.goto(base + '/almanac/dashboard.html'); page.wait_for_function('window.oswDashboardSelection')
            page.locator('#dashboard-card-view').click()
            page.locator('#dashboard-search').fill('Pacific South Equatorial Countercurrent')
            card = page.locator('article[data-id="' + q.TARGET + '"]'); expect(card).to_be_visible()
            card.locator('details').evaluate('(el)=>el.open=true')
            link = card.get_by_role('link', name='Route', exact=True); link.focus(); link.press('Enter')
            wait_atlas(page)
            actual = page.evaluate('(id)=>window.oswAtlasSnapshot.working_reference_routes.candidates.filter(r=>r.id===id)', q.ROUTE)
            if len(actual) != 1 or actual[0]['figure'] != q.FIGURE or actual[0]['rank_eligible'] is not False:
                raise ValueError('Direct dashboard link selected the wrong atlas route or figure')
            capture(page.locator('#route-atlas'), 'pacific-secc-global-atlas.png')
            checked.append('dashboard-keyboard-route-link-selects-current-and-regional-reference')
            page.locator('#route-atlas-card-link').click()
            route_card = page.locator('section.route-card[id="' + q.ROUTE + '"]'); expect(route_card).to_be_visible()
            expect(route_card).to_contain_text('Studied reach only')
            expect(route_card).not_to_contain_text('both source-coordinate conventions')
            image = route_card.locator('img.route-map')
            image.scroll_into_view_if_needed()
            page.wait_for_function('(id)=>{const el=document.getElementById(id)?.querySelector("img.route-map");return el?.complete&&el.naturalWidth>0}', arg=q.ROUTE)
            expect(image).to_have_attribute('src', '../' + q.FIGURE)
            expect(route_card.get_by_role('link', name='Open route map at full size')).to_have_attribute('href', '../' + q.FIGURE)
            capture(route_card, 'pacific-secc-route-card.png')
            checked.append('real-route-card-image-full-size-link-and-regional-scope')
            page.goto(base + '/' + q.PAGE)
            page.get_by_role('link', name='Open the reference record and query map').click()
            page.wait_for_function('(id)=>window.oswLastQueryResult?.rows?.[0]?.id===id', arg=q.ROUTE)
            query_result = page.evaluate('window.oswLastQueryResult')
            if query_result['total'] != 1 or len(query_result['map_scene']['features']) != 1:
                raise ValueError('Support page query link did not select one mapped route')
            expect(page.locator('#query-map-features .query-map-mark')).to_have_count(1)
            expect(page.locator('#query-detail')).to_contain_text('Pacific SECC')
            capture(page.locator('#query-map-section'), 'pacific-secc-query-map.png')
            checked.append('support-page-link-inspects-exact-route-and-query-map')
            source_request = {'document': admission.FILE, 'pointer': '', 'limit': 500}
            page.goto(base + '/almanac/query.html?source-q=' + quote(json.dumps(source_request)))
            page.wait_for_function('window.oswSourceQueryResult')
            source_result = page.evaluate('window.oswSourceQueryResult')
            reconstructed = {row['source_key']: row['record'] for row in source_result['rows']}
            if not same(reconstructed, json.loads((root / admission.FILE).read_bytes())):
                raise ValueError('Actual source-query UI did not reconstruct the complete publication admission')
            checked.append('complete-publication-and-audited-parent-source-query-ui')
            page.goto(base + '/' + q.PAGE)
            page.get_by_role('link', name='Explore this current in the global atlas').click()
            wait_atlas(page)
            checked.append('support-page-atlas-link-restores-current-and-route')
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 950})
                page.goto(base + '/' + q.PAGE)
                expect(page.get_by_role('heading', name='Pacific South Equatorial Countercurrent', exact=True)).to_be_visible()
                expect(page.locator('main')).not_to_contain_text('awaiting native/WASM')
                page.wait_for_function('Array.from(document.images).every(el=>el.complete&&el.naturalWidth>0)')
                if page.evaluate('document.documentElement.scrollWidth>window.innerWidth'):
                    raise ValueError('Support page horizontal overflow at ' + str(width))
                capture(page.locator('main'), 'pacific-secc-support-' + str(width) + 'px.png')
            checked.append('reviewed-map-and-scope-reflow-at-320-and-390px')
            if errors or originals or missing:
                raise ValueError('Browser errors, original downloads or missing assets: ' + repr((errors, originals, missing)))
            browser.close()
    except Exception as error:
        if 'page' in locals():
            try: page.screenshot(path=str(output / 'browser-failure.png'), timeout=15000)
            except Exception: pass
        write('browser-failure.json', {'status': 'FAIL', 'error': str(error)[:2000], 'checks_completed': checked,
              'page_errors': errors, 'original_downloads': originals, 'missing_assets': missing,
              'url': page.url if 'page' in locals() else None})
        raise
    finally:
        server.shutdown(); server.server_close()
    return {'status': 'PASS', 'browser_verified': True, 'visual_review_complete': False,
            'checks': checked, 'screenshots': screenshots, 'page_errors': errors,
            'original_downloads': originals, 'missing_assets': missing}
