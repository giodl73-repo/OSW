"""Actual cloud browser checks for five unlocated identities and family navigation."""
import functools
import hashlib
import http.server
import json
import os
import re
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY, verify_capture_geometry
import equatorial_basin_identity_runtime_v2 as runtime


OBJECT_READY = 'id => window.oswObjectView?.ok === true && window.oswObjectView.id === id'


def object_ready(page, owner):
    page.wait_for_function(OBJECT_READY, arg=owner, timeout=180000)
    return page.locator('#identity .equatorial-basin-identity-context')


def object_page(page, base, owner):
    page.goto(base + '/almanac/object.html?id=' + quote(owner))
    return object_ready(page, owner)


def browser_review(root, output):
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('OSW_EQUATORIAL_BASIN_IDENTITY_DELIVERY_V2') != '1'):
        raise ValueError('Exact scoped cloud browser required before payload access')
    from playwright.sync_api import sync_playwright, expect
    query = runtime.query
    contract = runtime.contract()
    scenes = runtime.scenes()
    original = json.loads(json.loads((output / 'parent-dashboard.json').read_bytes())['snapshot_json'])
    baseline = {r['id']: {'fingerprint': r['fingerprint'], 'sections': r['section_fingerprints']} for r in original['entries']}
    expected_dashboard = runtime.dashboard_document(original)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    errors, missing, originals, captures, checks = [], [], [], [], []

    def capture(locator, name):
        locator.scroll_into_view_if_needed()
        geometry = locator.evaluate(CAPTURE_GEOMETRY)
        if geometry['clipped_axes']:
            (output / (name + '.geometry.json')).write_text(json.dumps(geometry, indent=2) + '\n')
        verify_capture_geometry(geometry)
        path = output / (name + '.png')
        locator.screenshot(path=str(path))
        captures.append({'path': path.name, 'bytes': path.stat().st_size,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'geometry': geometry})

    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):
            raise ValueError('Page-level horizontal overflow')

    def panel_matches(panel, scene):
        expect(panel.locator('li[data-entity-id]')).to_have_count(len(scene['members']))
        expect(panel).to_contain_text(scene['dimension_status'])
        expect(panel).to_contain_text('do not establish physical connections')
        for member in scene['members']:
            item = panel.locator('li[data-entity-id="' + member['entity_id'] + '"]')
            expect(item.get_by_role('link', name=member['label'], exact=True)).to_have_attribute('href', member['object_url'])
            expect(item.get_by_role('link', name=member['family_label'], exact=True)).to_have_attribute('href', member['family_url'])
        expect(panel.locator('svg,canvas,img')).to_have_count(0)

    def query_page(page, request):
        page.goto(base + '/almanac/query.html?q=' + quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok')
        return page.evaluate('window.oswLastQueryResult')

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--renderer-process-limit=1'])
            page = browser.new_page(viewport={'width': 1100, 'height': 1100})
            page.set_default_timeout(180000)
            page.add_init_script('if(location.pathname.endsWith("/dashboard.html"))localStorage.setItem("osw-motion-dashboard-seen-v2",' + json.dumps(json.dumps(baseline)) + ');')
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('response', lambda r: missing.append({'url': r.url, 'status': r.status})
                    if r.url.startswith(base) and r.status >= 400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request', lambda r: originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
            for width in [1100, 320]:
                try:
                    page.set_viewport_size({'width': width, 'height': 1100})
                    suffix = '-' + str(width) + 'px'
                    memberships = contract['additions']['current_basin_memberships']
                    result = query_page(page, {'collection': 'current_basin_memberships', 'limit': 1, 'offset': 2})
                    expected = sorted(memberships, key=lambda r: r['id'])
                    if result['total'] != 5 or result['rows'] != expected[2:3]:
                        raise ValueError('Paginated membership query differs')
                    panel = page.locator('#query-chart-panels .equatorial-basin-identity-context')
                    panel_matches(panel, runtime.membership_scene(expected))
                    capture(panel.locator('h3'), 'basin-query-heading' + suffix)
                    for member in memberships:
                        capture(panel.locator('li[data-entity-id="' + member['entity_id'] + '"]'), 'basin-query-' + member['current_id'] + suffix)
                    no_overflow(page)
                    for family in sorted(contract['prior_family_records']):
                        result=query_page(page,{'collection':'objects','taxonomy':{'root_id':family,'relation':'children','include_root':False},'limit':100})
                        expected_ids=sorted(r['entity_id'] for r in memberships if r['family_entity_id']==family)
                        if sorted(r['id'] for r in result['rows'])!=expected_ids or result.get('taxonomy_scope')!=query.TAXONOMY_SCOPE:raise ValueError('General family query differs')
                        if result['map_scene']['features']!=[]:raise ValueError('General family query invented map placement')
                    selected = memberships[0]
                    result = query_page(page, {'collection': 'current_basin_memberships', 'filters': [
                        {'field': 'entity_id', 'op': 'eq', 'value': selected['entity_id']}], 'limit': 100})
                    if result['rows'] != [selected] or result['map_scene'] is not None:
                        raise ValueError('Filtered membership selection gained other records or geometry')
                    panel = page.locator('#query-chart-panels .equatorial-basin-identity-context')
                    panel_matches(panel, runtime.membership_scene([selected]))
                    capture(panel, 'basin-query-filtered' + suffix)
                    panel.get_by_role('button', name='Inspect membership record').click()
                    expect(page.locator('#query-detail')).to_contain_text(selected['id'])
                    capture(page.locator('#query-detail'), 'basin-membership-inspect' + suffix)
                    source_request = {'document': query.FILE, 'pointer': '/additions/current_basin_memberships', 'limit': 100}
                    page.goto(base + '/almanac/query.html?source-q=' + quote(json.dumps(source_request)))
                    page.wait_for_function('window.oswSourceQueryResult?.ok')
                    source = page.evaluate('window.oswSourceQueryResult')
                    if source['source_sha256'] != query.sha(query.FILE) or [r['record'] for r in source['rows']] != memberships:
                        raise ValueError('Membership source pointer differs')
                    no_overflow(page)

                    for owner, scene in scenes.items():
                        slug = owner.removeprefix('current:')
                        panel = object_page(page, base, owner)
                        panel_matches(panel, scene)
                        if owner in contract['expected_entity_ids']:
                            expect(panel.locator('a[aria-current="page"]')).to_have_count(1)
                        capture(panel, 'basin-object-' + slug + suffix)
                        no_overflow(page)
                    #Follow an actual family link and then a member link, rather than only checking hrefs.
                    panel = object_page(page, base, selected['entity_id'])
                    panel.locator('li').first.get_by_role('link', name=scenes[selected['entity_id']]['members'][0]['family_label'], exact=True).click()
                    page.wait_for_url('**/object.html?id=current%3Anorth-equatorial')
                    panel = object_ready(page, 'current:north-equatorial')
                    expect(panel.locator('li[data-entity-id]')).to_have_count(2)
                    panel.locator('li[data-entity-id="' + selected['entity_id'] + '"] a').first.click()
                    page.wait_for_url('**/object.html?id=' + quote(selected['entity_id'], safe=''))
                    panel_matches(object_ready(page, selected['entity_id']), scenes[selected['entity_id']])

                    page.goto(base + '/almanac/reference-routes.html?atlas-feature=' + quote(selected['entity_id']) + '#route-atlas')
                    page.wait_for_function('document.querySelectorAll("#route-atlas-select option").length===112')
                    for owner in contract['expected_entity_ids']:
                        slug = owner.removeprefix('current:')
                        page.locator('#route-atlas-select').select_option(owner)
                        panel = page.locator('#route-atlas-preview .equatorial-basin-identity-context')
                        panel_matches(panel, scenes[owner])
                        expect(page.locator('#route-atlas-status')).to_contain_text('no source-supported map placement')
                        expect(page.locator('#route-atlas-features [data-current-id="' + owner + '"]')).to_have_count(0)
                        #Atlas preview has a bounded scroll container; capture each complete member separately.
                        capture(panel.locator('h3'), 'basin-atlas-' + slug + '-heading' + suffix)
                        capture(panel.locator('li[data-entity-id="' + owner + '"]'), 'basin-atlas-' + slug + suffix)
                    status = page.locator('#inventory-addition-status')
                    expect(status).not_to_contain_text('unavailable')
                    for owner in contract['expected_entity_ids']:
                        expect(page.locator('#inventory-addition-' + owner.removeprefix('current:'))).to_have_class('current-admission-card')
                    no_overflow(page)

                    page.goto(base + '/almanac/seasons.html?current=' + quote(selected['current_id']))
                    page.wait_for_function('window.oswSeasonSnapshot?.ok')
                    for owner in contract['expected_entity_ids']:
                        slug = owner.removeprefix('current:')
                        page.locator('#season-current').select_option(slug)
                        panel = page.locator('#season-basin-identities .equatorial-basin-identity-context')
                        panel_matches(panel, scenes[owner])
                        expect(page.locator('#season-play')).to_be_disabled()
                        expect(page.locator('#season-phase')).to_be_disabled()
                        plan = page.evaluate('window.oswSeasonPlan')
                        if plan != runtime.empty_plan(slug):
                            raise ValueError('New identity seasonal plan differs')
                        capture(panel, 'basin-seasons-' + slug + suffix)
                    no_overflow(page)

                    page.goto(base + '/almanac/dashboard.html')
                    page.wait_for_function('window.oswDashboardSnapshot?.ok || document.querySelector("#dashboard-status").textContent.includes("Update check failed")')
                    actual = page.evaluate('window.oswDashboardSnapshot?.snapshot')
                    if actual != expected_dashboard:
                        raise ValueError('Complete browser dashboard differs from independent projection')
                    page.locator('#dashboard-card-view').click()
                    page.locator('#dashboard-type').select_option('named_current')
                    page.locator('#dashboard-metric').select_option('scoped_width')
                    page.locator('#dashboard-changed').check()
                    for owner in contract['expected_entity_ids']:
                        label = next(r['label'] for r in contract['additions']['entities'] if r['id'] == owner)
                        page.locator('#dashboard-search').fill(label)
                        card = page.locator('#dashboard-grid article[data-id="' + owner + '"]')
                        expect(card).to_have_count(1)
                        expect(card).to_have_class(re.compile(r'\bupdated\b'))
                        expect(card).not_to_have_class(re.compile(r'\blit\b'))
                        capture(card, 'basin-dashboard-' + owner.removeprefix('current:') + suffix)
                    no_overflow(page)
                    checks.append({'width': width, 'all_five_members': True, 'both_family_records': True,
                                   'navigation_followed': True, 'source_pointer_verified': True,
                                   'no_fabricated_map_positions': True, 'seasonal_playback_disabled': True,
                                   'complete_dashboard_verified': True, 'no_horizontal_overflow': True})
                except Exception as error:
                    failure = {'status': 'FAIL', 'width': width, 'url': page.url, 'error': str(error),
                               'page_errors': errors, 'missing_assets': missing, 'completed_captures': captures}
                    try:
                        failure['status_text'] = page.locator('body').inner_text()[:4000]
                        page.screenshot(path=str(output / ('basin-failure-' + str(width) + 'px.png')))
                    except Exception:
                        pass
                    (output / 'browser-observation-failure.json').write_text(json.dumps(failure, indent=2) + '\n')
                    raise
            browser.close()
        if errors or missing or originals:
            raise ValueError('Page errors, missing assets or original downloads: ' + json.dumps([errors, missing, originals]))
        return {'status': 'PASS', 'checks': checks, 'captures': captures, 'actual_screenshots': len(captures),
                'page_errors': errors, 'missing_assets': missing, 'original_downloads': originals,
                'visual_review_complete': False, 'installed': False}
    finally:
        server.shutdown()
        server.server_close()
