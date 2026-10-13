"""Northern Tsuchiya reach cannot lend length, depth or width to NEUC."""
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    candidate=json.loads(Path('research/pacific-nscc-reach-reference-path-candidate.json').read_text(encoding='utf-8'))
    catalog=json.loads(Path('research/ocean-current-reference-path-candidates.json').read_text(encoding='utf-8'))
    snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    proposals=json.loads(Path('research/ocean-current-inventory-expansion-candidates.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()==proposals['current_ledger_sha256']
    rows={r['id']:r for r in snapshot['entries']}
    nscc=rows['current:pacific-north-subsurface-countercurrent']
    neuc=rows['current:pacific-north-equatorial-undercurrent']
    assert candidate['candidate_comparison_group']=='osw_studied_reach_routes'
    assert 'pacific-nscc-reach-reference-path-candidate' not in catalog['reference_route_length_order']
    assert nscc['latest_observation_date'] is None
    widths=json.loads(Path('research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))['measurements']
    for row in [nscc,neuc]:
        owner=row['id'].removeprefix('current:')
        assert row['capabilities']['scoped_width']==sum(w['current_id']==owner for w in widths)
        assert row['capabilities']['reference_route']==sum(r['current_id']==owner for r in catalog['candidates'])
    neuc_routes=[r for r in catalog['candidates'] if r['current_id']==neuc['id'].removeprefix('current:')]
    assert neuc_routes and all(r['id']!='pacific-nscc-reach-reference-path-candidate' for r in neuc_routes)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1000})
        page.emulate_media(reduced_motion='reduce')
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Apacific-north-subsurface-countercurrent#route-atlas',wait_until='networkidle')
        page.wait_for_function('(count)=>document.querySelectorAll(".route-card").length===count',arg=len(catalog['candidates']))
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['5,000 km','4,900–5,100','Studied reach only','220 m','130 m','not width']:
            assert text in preview.inner_text(),text
        assert preview.locator('.route-atlas-state-links li').count()==len(candidate['nominal_atlas_state_crossings'])
        page.locator('#route-atlas').screenshot(path='figures/pacific-nscc-reach-reference-path-review.png')
        page.locator('#route-atlas-select').select_option(neuc['id'])
        assert preview.locator('.route-map').is_visible()
        assert 'length is not transferred' in preview.inner_text()
        assert 'Studied reach only' in preview.inner_text()
        page.set_viewport_size({'width':320,'height':800})
        for row in [nscc,neuc]:
            page.locator('#route-atlas-select').select_option(row['id'])
            assert row['scope_notes'][0]['summary'] in preview.inner_text()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-world').click()
        assert preview.is_hidden()
        assert not errors,errors
        browser.close()
    print('OK: Tsuchiya studied reach visual/local depths/mobile; independent NEUC component routes; no borrowed length, width, date or rank; canonical ledger unchanged')


if __name__=='__main__':
    main()
