"""Cloud-only review of EICC navigation, complete records, maps and phone layout."""
import functools
import hashlib
import http.server
import json
import os
import threading

import check_south_java_model_layer_cloud_v1 as environment
import eicc_reference_delivery_v1 as delivery
import eicc_reference_query_v1 as context


def browser_review(root, output):
    environment.cloud_environment(dict(os.environ))  # Before any browser/server starts.
    from playwright.sync_api import sync_playwright, expect

    def read(path): return json.loads((root / path).read_bytes())
    def write(path, value): path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    errors, originals, images, checked = [], [], [], []
    contract = context.build_contract()
    def snapshot(locator, name):
        path = output / name; locator.screenshot(path=str(path))
        images.append({'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--renderer-process-limit=1'])
            page = browser.new_page(viewport={'width': 1100, 'height': 950}); page.set_default_timeout(180000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda req: originals.append(req.url) if req.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
            page.goto(base + '/almanac/dashboard.html'); page.wait_for_function('window.oswDashboardSelection')
            page.locator('#dashboard-card-view').click(); page.locator('#dashboard-search').fill('East India Coastal')
            card = page.locator('article[data-id="current:east-india-coastal"]'); expect(card).to_be_visible()
            card.locator('details').evaluate('(el)=>el.open=true')
            link = card.get_by_role('link', name='Query regional source-reference routes'); link.focus(); link.press('Enter')
            page.wait_for_function('window.oswLastQueryResult?.collection === "reference_routes"')
            result = page.evaluate('window.oswLastQueryResult')
            if result['total'] != 2 or len(result['map_scene']['features']) != 2:
                raise ValueError('Dashboard route link did not retrieve both EICC references')
            checked.append('dashboard-keyboard-navigation-to-two-references')
            for row in contract['collections'][context.ROUTES]:
                page.goto(base + '/almanac/' + context.PAGE.split('/')[-1])
                route_card = page.locator('article[id="' + row['id'] + '"]')
                link = route_card.get_by_role('link', name='Open this reference and its query map')
                link.focus(); link.press('Enter')
                page.wait_for_function('window.oswLastQueryResult?.total === 1')
                expect(page.locator('#query-detail')).to_contain_text(row['label'])
                result = page.evaluate('window.oswLastQueryResult')
                if (context.encoded(result['rows']) != context.encoded([row])
                        or len(result['map_scene']['features']) != 1
                        or result['map_scene']['features'][0]['entity_id'] != row['id']):
                    raise ValueError('Direct card link selected the wrong reference or map')
                expect(page.locator('#query-map-features .query-map-mark')).to_have_count(1)
                if float(page.locator('#query-map').get_attribute('viewBox').split()[2]) >= 360:
                    raise ValueError('Direct reference link did not fit the map')
                expect(page.locator('#query-map-time')).to_contain_text('not observed current axes')
                snapshot(page.locator('#query-map-section'), row['id'] + '-query-map.png')
            checked.append('both-static-card-links-select-inspect-and-fit-one-route')
            for name in [context.POINTS, context.SCALES]:
                page.goto(base + '/almanac/' + context.query_url(name)); page.wait_for_function('window.oswLastQueryResult')
                result = page.evaluate('window.oswLastQueryResult')
                expected = sorted(contract['collections'][name], key=lambda row: row['id'])
                if context.encoded(result['rows']) != context.encoded(expected) or result['map_scene'] is not None:
                    raise ValueError('Complete typed diagnostic rows or geography scope differs')
                expect(page.locator('#query-map-section')).to_be_hidden()
                if name == context.POINTS:
                    expect(page.locator('#query-rows')).to_contain_text('outlet')
                else:
                    expect(page.locator('#query-rows')).to_contain_text('not')
            checked.append('all-thirteen-typed-source-records-exact-and-unmapped')
            source_rows = [contract['collections'][name][-1] for name in context.OWNER_FIELDS]
            page.goto(base + '/almanac/' + source_rows[0]['source_query_url'])
            page.wait_for_function('window.oswSourceQueryResult')
            requests = [(path, '', read(path)) for path in sorted(delivery.DOCUMENTS)]
            from check_eicc_reference_delivery_v1 import resolve
            requests += [(row['source_file'], row['source_pointer'], resolve(read(row['source_file']), row['source_pointer']))
                         for row in source_rows]
            for path, pointer, original in requests:
                page.locator('#source-query-json').evaluate('(el)=>el.closest("details").open=true')
                page.locator('#source-query-json').fill(json.dumps({'document': path, 'pointer': pointer, 'limit': 500}))
                page.evaluate('window.oswSourceQueryResult=null'); page.locator('#source-query-run-json').click()
                page.wait_for_function('window.oswSourceQueryResult')
                result = page.evaluate('window.oswSourceQueryResult')
                reconstructed = {row['source_key']: row['record'] for row in result['rows']}
                if (result.get('ok') is not True or context.encoded(reconstructed) != context.encoded(original)
                        or result['source_sha256'] != hashlib.sha256((root / path).read_bytes()).hexdigest()):
                    raise ValueError('Browser source lookup differs: ' + path + pointer)
            checked.append('eight-complete-source-documents-and-three-exact-source-pointers')
            page.goto(base + '/' + context.PAGE)
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 950})
                expect(page.get_by_role('heading', name='East India Coastal Current: regional references and source support')).to_be_visible()
                expect(page.locator('article.point')).to_have_count(7)
                expect(page.locator('table.scales tbody tr')).to_have_count(6)
                expect(page.get_by_role('link', name='Open this reference and its query map')).to_have_count(2)
                if not page.locator('img').evaluate_all('(images)=>images.length===2&&images.every(el=>el.complete&&el.naturalWidth>0)'):
                    raise ValueError('Evidence map or source chart did not load')
                if page.evaluate('document.documentElement.scrollWidth>window.innerWidth'):
                    raise ValueError('Evidence page horizontal overflow')
                snapshot(page.locator('main'), 'eicc-reference-support-' + str(width) + 'px.png')
            checked.append('two-source-figures-and-all-records-reflow-at-320-and-390px')
            if errors or originals: raise ValueError('Browser errors or original downloads: ' + repr((errors, originals)))
            browser.close()
    except Exception as error:
        if 'page' in locals():
            try: page.screenshot(path=str(output / 'browser-failure.png'), timeout=15000)
            except Exception: pass
        write(output / 'browser-failure.json', {'status': 'FAIL', 'checks_completed': checked,
              'url': page.url if 'page' in locals() else None, 'errors': errors,
              'original_downloads': originals, 'error': str(error)[:1800]})
        raise
    finally: server.shutdown(); server.server_close()
    return {'checks': checked, 'screenshots': images, 'page_errors': errors, 'original_downloads': originals,
            'browser_verified': True, 'visual_review_complete': False}
