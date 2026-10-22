"""The admitted slope branch reaches the same data through native, WASM and atlas UI."""
import json
import os
import argparse
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
import nwasc_working_admission as n
import hansen_asar_widths as asar
from test_current_research_evidence_browser import BASE, native


def check_admitted_card_navigation(page):
    """Initial hashes, in-page links and history must reveal admitted cards."""
    for current, width in [('norwegian-atlantic-slope', 1280),
                           ('southern-east-madagascar', 320)]:
        page.set_viewport_size({'width': width, 'height': 900})
        card_id = 'inventory-addition-' + current
        page.goto(BASE + '/almanac/reference-routes.html#' + card_id)
        card = page.locator('#' + card_id)
        expect(card).to_have_class('current-admission-card', timeout=120000)
        expect(card).to_be_focused(timeout=120000)
        page.wait_for_function('id => Math.abs(document.getElementById(id).getBoundingClientRect().top) < 100', arg=card_id)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        card.get_by_role('link', name='Back to current atlas', exact=True).focus()
        page.keyboard.press('Enter')
        expect(page.locator('#route-atlas')).to_be_focused()
        # A real hashchange returns keyboard focus, not just native anchor scroll.
        page.evaluate('(id) => { location.hash = id; }', card_id)
        expect(card).to_be_focused()
        page.wait_for_function('id => Math.abs(document.getElementById(id).getBoundingClientRect().top) < 100', arg=card_id)
        # A same-hash self-link still restores focus and position.
        page.evaluate('window.scrollTo(0, 0)')
        card.get_by_role('link', name='Link to this current', exact=True).evaluate('(e) => e.click()')
        expect(card).to_be_focused()
        page.wait_for_function('id => Math.abs(document.getElementById(id).getBoundingClientRect().top) < 100', arg=card_id)
        page.go_back()
        expect(page.locator('#route-atlas')).to_be_focused()
        print('PASS accepted-card deep link, hashchange, self-link and history', current, width, flush=True)
    for selector, name in [('.inventory-addition-card', 'Link to this proposed current'),
                           ('.route-card', None)]:
        target = page.locator(selector).first
        target_id = target.get_attribute('id')
        page.evaluate('(id) => { location.hash = id; }', target_id)
        expect(target).to_be_focused()
        if name:
            target.get_by_role('link', name=name, exact=True).evaluate('(e) => e.click()')
            expect(target).to_be_focused()
    expect(page.locator('.nwasc-admitted-dimensions img')).to_have_attribute(
        'alt', 'Norwegian Atlantic Slope Current: broad historical reported extent and six separately scoped width records. No whole-current width or annual range.')


def navigation_main():
    """Focused UI check; the unchanged numerical engine has a separate receipt."""
    out = n.ROOT / '.pytest_cache/nwasc-card-navigation'
    out.mkdir(exist_ok=True)
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        check_admitted_card_navigation(page)
        assert not errors, errors
        browser.close()
    receipt = {'status': 'PASS', 'accepted_current_cards': 2, 'viewport_widths': [1280, 320],
               'direct_hash_focus_scroll': True, 'hashchange_self_link_history': True,
               'pending_and_route_card_navigation': True, 'width_count_alt_text': 6, 'page_errors': errors}
    (out / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt), flush=True)


def main():
    doc, _ = n.verify_inputs()
    out = n.ROOT / '.pytest_cache/nwasc-admission-browser'
    out.mkdir(exist_ok=True)
    errors, originals = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width': 1360, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.lower().endswith(('.pdf', '.nc', '.zip', '.xml')) else None)
        queries = [
            {'collection': 'entities', 'filters': [{'field': 'type', 'op': 'eq', 'value': 'named_current'}], 'limit': 1},
            {'collection': 'current_identity_admissions', 'filters': [{'field': 'entity_id', 'op': 'eq', 'value': n.ENTITY}], 'limit': 1},
            {'collection': 'widths', 'filters': [{'field': 'current_id', 'op': 'eq', 'value': n.ID}], 'limit': 10},
            {'collection': 'length_assessments', 'filters': [{'field': 'rank_eligible', 'op': 'eq', 'value': True}], 'sort': {'field': 'published_length_km', 'direction': 'desc'}, 'limit': 100},
            {'collection': 'current_measurement_admissions', 'filters': [{'field': 'entity_id', 'op': 'eq', 'value': n.ENTITY}], 'limit': 1},
            {'collection': 'objects', 'filters': [{'field': 'id', 'op': 'eq', 'value': n.ENTITY}], 'limit': 1},
        ]
        for i, q in enumerate(queries):
            page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(q)))
            page.wait_for_function('window.oswLastQueryResult', timeout=120000)
            result = page.evaluate('oswLastQueryResult')
            assert result == native(q)
            assert result['total'] == [102, 1, 8, 13, 1, 1][i]
            if i == 1:
                assert result['rows'] == [doc['identity_entry']]
            if i == 2:
                assert result['rows'] == sorted(doc['width_records'] + [r for r in asar.verify_inputs()[0]['width_records'] if r['current_id']==n.ID], key=lambda r: r['id'])
            if i == 3:
                values = {r['entity_id']: (r['published_length_km'], r['published_rank']) for r in result['rows']}
                assert values[n.ENTITY] == (3500, 6)
                assert values['current:southern-east-madagascar'] == (650, 13)
            if i == 4:
                assert result['rows'] == [doc]
            if i == 5:
                assert result['map_scene']['mapped_objects'] == 1 and result['map_scene']['unmapped_objects'] == 0
                assert result['rows'][0]['map_features'][0]['role'] == 'editorial_reference_route'
            assert page.locator('#query-export').is_enabled()
            page.set_viewport_size({'width': 320, 'height': 1000})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            print('PASS native/WASM', q['collection'], result['total'], flush=True)
        page.goto(BASE + '/almanac/index.html#working-current-catalogue')
        page.wait_for_function('window.oswCurrentIdentityAdmissions', timeout=120000)
        section = page.locator('#working-current-catalogue')
        expect(section).to_contain_text('102 accepted named currents')
        accepted = section.get_by_role('link', name='Norwegian Atlantic Slope Current', exact=True)
        accepted.focus()
        page.keyboard.press('Enter')
        expect(page.locator('#object-title')).to_have_text(doc['entity']['label'], timeout=120000)
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Anorwegian-atlantic-slope#route-atlas')
        page.wait_for_function('window.oswAtlasSnapshot', timeout=120000)
        expect(page.locator('#route-atlas-preview > h3')).to_have_text(doc['entity']['label'], timeout=120000)
        links = page.locator('.route-atlas-evidence-links')
        links.locator('summary').focus()
        page.keyboard.press('Enter')
        figure = links.get_by_role('link', name='Compare separately scoped reported dimensions', exact=True)
        expect(figure).to_have_attribute('href', '../' + n.FIGURE)
        assert links.get_by_role('link', name='Query all admitted local width records', exact=True).count() == 1
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        links.screenshot(path=str(out / 'atlas-links-mobile.png'))
        card = page.locator('#inventory-addition-' + n.ID)
        expect(card).to_have_class('current-admission-card')
        expect(card.locator('.nwasc-admitted-dimensions')).to_contain_text('3,500 km')
        expect(card.locator('.nwasc-admitted-dimensions')).to_contain_text('Six local width records')
        assert page.locator('.inventory-addition-card').count() == 27
        expect(page.locator('#inventory-addition-southern-east-madagascar')).to_contain_text('working reported-length rank 13')
        # Every source served by the atlas retains its own file address and bytes.
        for path in [n.FILE, n.CATALOGUE, n.EXPORT]:
            source = page.evaluate('(path)=>window.oswAtlasSnapshot.sources_json[path]', path)
            assert source.encode('utf-8') == (n.ROOT / path).read_bytes()
        figure.focus()
        page.keyboard.press('Enter')
        expect(page.locator('svg')).to_have_attribute('role', 'img')
        expect(page.locator('#desc')).to_contain_text('not six independent new observations')
        page.set_viewport_size({'width': 1100, 'height': 800})
        page.screenshot(path=str(out / 'figure.png'))
        page.goto(BASE + '/almanac/seasons.html?current=' + n.ID)
        page.wait_for_function('window.oswSeasonSnapshot', timeout=120000)
        expect(page.locator('#season-current')).to_have_value(n.ID)
        expect(page.locator('#season-play')).to_be_disabled()
        plan = page.evaluate('window.oswSeasonSnapshot.phase_plans["norwegian-atlantic-slope"]')
        assert not plan['can_play'] and plan['eligible_indices'] == []
        assert {p['width_id'] for p in plan['phases']} == {r['id'] for r in doc['width_records'] + [w for w in asar.verify_inputs()[0]['width_records'] if w['current_id']==n.ID]}
        assert all(p['playback_step_eligible'] is False and p['frame_id'] is None for p in plan['phases'])
        expect(page.locator('#season-range')).to_contain_text('not a seasonal sequence')
        check_admitted_card_navigation(page)
        assert not errors and not originals, (errors, originals)
        browser.close()
    receipt = {'status': 'PASS', 'native_actual_wasm_queries': 6, 'current_identities': 102,
               'ranked_lengths': 13, 'admitted_local_widths': 8, 'current_rank': 6, 'madagascar_rank': 13,
               'accepted_index_and_object_navigation': True, 'atlas_sources_exact': True,
               'proposal_links_resolve_accepted_identity': True, 'mobile_320px': True,
               'keyboard_scalar_figure': True, 'seasonal_animation_disabled': True, 'automatic_original_requests': 0,
               'accepted_card_direct_hash_focus_scroll': ['norwegian-atlantic-slope', 'southern-east-madagascar'],
               'accepted_card_hashchange_self_link_history': True}
    (out / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--navigation-only', action='store_true')
    args = parser.parse_args()
    navigation_main() if args.navigation_only else main()
