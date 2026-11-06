"""Browser observation v2: await real worker rendering and capture unclipped sidebar parts."""
import functools
import hashlib
import http.server
import json
import os
import threading
from urllib.parse import quote
import azores_2009_section_projection_v1 as p

CAPTURE_GEOMETRY = """el => {
  const r=el.getBoundingClientRect(), clips=[];
  for(let parent=el.parentElement;parent && !['BODY','HTML'].includes(parent.tagName);parent=parent.parentElement){
    const s=getComputedStyle(parent), p=parent.getBoundingClientRect();
    if(/auto|scroll|hidden|clip/.test(s.overflowY) && (r.top<p.top-2||r.bottom>p.bottom+2))clips.push('vertical');
    if(/auto|scroll|hidden|clip/.test(s.overflowX) && (r.left<p.left-2||r.right>p.right+2))clips.push('horizontal');
  }
  return {width:r.width,height:r.height,clipped_axes:clips};
}"""


def verify_capture_geometry(geometry):
    if (geometry['width'] <= 0 or geometry['height'] <= 0
            or geometry['clipped_axes']):
        raise ValueError('Capture target is clipped; capture an actual visible sidebar part')


def browser_review(root, output):
    from check_south_java_model_layer_cloud_v1 import cloud_environment
    cloud_environment(dict(os.environ))
    if os.environ.get('OSW_AZORES_SECTION_BROWSER_RESUME_V1') != '1':
        raise ValueError('Exact cloud section delivery required before browser startup')
    from playwright.sync_api import sync_playwright, expect
    bindings = json.loads((root / p.BINDINGS).read_bytes())['records']
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    errors, missing, originals, screenshots, checks = [], [], [], [], []
    def capture(locator, name):
        path = output / name
        locator.scroll_into_view_if_needed()
        geometry=locator.evaluate(CAPTURE_GEOMETRY)
        verify_capture_geometry(geometry)
        locator.screenshot(path=str(path))
        screenshots.append({'path': name, 'bytes': path.stat().st_size,
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'geometry': geometry})
    def ready(page, locator):
        locator.wait_for(state='visible', timeout=180000)
        expect(locator).to_be_visible()
        expect(locator).to_contain_text('source date conflict remains unresolved')
        expect(locator).to_contain_text('Width uncertainty and annual ranges remain unknown')
        image = locator.locator('img')
        image.wait_for()
        page.wait_for_function('(img)=>img.complete&&img.naturalWidth>0', arg=image.element_handle())
        expect(locator.get_by_role('link', name='Open section diagram at full size')).to_have_attribute('href', '../' + p.FIGURE)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--renderer-process-limit=1'])
            page = browser.new_page(viewport={'width': 1100, 'height': 950})
            page.set_default_timeout(180000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda req: originals.append(req.url)
                    if req.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
            page.on('response', lambda response: missing.append({'url': response.url, 'status': response.status})
                    if response.url.startswith(base) and response.status >= 400 and not response.url.endswith('/favicon.ico') else None)
            for row in bindings:
                current, identity = row['current_id'], row['id']
                page.goto(base + '/almanac/reference-routes.html?atlas-layout=map&atlas-feature=' + quote('current:' + current) + '#route-atlas')
                page.wait_for_function('window.oswAtlasSnapshot?.azores_2009_section_scene?.records.length===2')
                expect(page.locator('#route-atlas-select')).to_have_value('current:' + current)
                card = page.locator('.azores-section-review')
                ready(page, card)
                expect(card.get_by_role('heading', name=row['name'] + ' / selected record', exact=True)).to_be_visible()
                capture(card.locator('figure'), 'azores-' + current + '-atlas-figure.png')
                capture(card.locator('section[data-width-id="' + identity + '"]'), 'azores-' + current + '-atlas-selected-record.png')
                selected = card.locator('section[data-width-id="' + identity + '"]')
                selected.get_by_role('link', name='Inspect width record', exact=True).click()
                page.wait_for_function('window.oswSeasonSnapshot?.azores_2009_section_scene?.records.length===2')
                width = page.locator('#regional-width-range .azores-section-review')
                ready(page, width)
                expect(page.locator('#season-play')).to_be_disabled()
                if page.url.split('phase=')[-1].split('&')[0] != identity:
                    raise ValueError('Current card did not navigate to the selected dated width')
                capture(width, 'azores-' + current + '-width.png')
                selected = width.locator('section[data-width-id="' + identity + '"]')
                selected.get_by_role('link', name='Inspect exact source record').click()
                page.wait_for_function('window.oswSourceQueryResult?.ok')
                response = page.evaluate('window.oswSourceQueryResult')
                reconstructed = {r['source_key']: r['record'] for r in response['rows']}
                if reconstructed != row:
                    raise ValueError('Actual indexed source-row navigation differs from exact width record')
                individual = {'collection': 'widths', 'filters': [{'field': 'id', 'op': 'eq', 'value': identity}], 'limit': 1}
                page.goto(base + '/almanac/query.html?q=' + quote(json.dumps(individual)))
                page.wait_for_function('window.oswLastQueryResult?.ok')
                individual_result = page.evaluate('window.oswLastQueryResult')
                if individual_result['total'] != 1 or individual_result['rows'] != [row]:
                    raise ValueError('Individual width query changed the selected original row')
                individual_chart = page.locator('#query-chart-panels .azores-section-review')
                ready(page, individual_chart)
                expect(individual_chart.get_by_role('heading', name=row['name'] + ' / selected record', exact=True)).to_be_visible()
                checks.append(current + ': atlas, dated-width navigation, disabled seasonal playback, exact indexed source row')
            query = {'collection': 'widths', 'filters': [{'field': 'source_url', 'op': 'eq', 'value': bindings[0]['source_url']}],
                     'sort': {'field': 'id', 'direction': 'desc'}, 'limit': 1, 'offset': 1}
            page.goto(base + '/almanac/query.html?q=' + quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.ok')
            response = page.evaluate('window.oswLastQueryResult')
            if response['total'] != 2 or len(response['rows']) != 1:
                raise ValueError('Actual paginated mixed-width query differs')
            chart = page.locator('#query-chart-panels .azores-section-review')
            ready(page, chart)
            expect(chart.locator('section[data-width-id]')).to_have_count(2)
            chart.locator('section[data-width-id="' + response['rows'][0]['id'] + '"]').get_by_role('button', name='Inspect width record').click()
            expect(page.locator('#query-detail')).to_contain_text(response['rows'][0]['id'])
            capture(chart, 'azores-query-comparison.png')
            checks.append('paginated mixed query retains both source sections and inspects the exact selected row')
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 950})
                for row in bindings:
                    current = row['current_id']
                    page.goto(base + '/almanac/seasons.html?current=' + current + '&phase=' + row['id'])
                    card = page.locator('#regional-width-range .azores-section-review')
                    ready(page, card)
                    expect(page.locator('#season-play')).to_be_disabled()
                    if page.evaluate('document.documentElement.scrollWidth>window.innerWidth'):
                        raise ValueError('Section width page horizontal overflow at ' + str(width))
                    capture(card, 'azores-' + current + '-width-' + str(width) + 'px.png')
                    if width == 320:
                        page.goto(base + '/almanac/reference-routes.html?atlas-layout=map&atlas-feature=' + quote('current:' + current) + '#route-atlas')
                        page.wait_for_function('window.oswAtlasSnapshot?.azores_2009_section_scene?.records.length===2')
                        atlas_card = page.locator('.azores-section-review')
                        ready(page, atlas_card)
                        if page.evaluate('document.documentElement.scrollWidth>window.innerWidth'):
                            raise ValueError('Selected atlas width evidence overflows320px')
                        capture(atlas_card.locator('figure'), 'azores-' + current + '-atlas-figure-320px.png')
                        capture(atlas_card.locator('section[data-width-id="' + row['id'] + '"]'), 'azores-' + current + '-atlas-selected-record-320px.png')
                    checks.append(current + ': dated section at ' + str(width) + 'px without horizontal overflow')
            browser.close()
        if errors or missing or originals:
            raise ValueError('Browser errors, missing assets or original-science downloads: ' + str([errors, missing, originals])[:3000])
        return {'status': 'PASS', 'checks': checks, 'screenshots': screenshots,
                'page_errors': errors, 'missing_assets': missing, 'original_science_downloads': originals,
                'real_browser_executed': True, 'visual_review_complete': False}
    finally:
        server.shutdown()
        server.server_close()
