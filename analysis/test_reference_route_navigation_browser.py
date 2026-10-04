"""Verify direct navigation to asynchronously rendered route-map cards."""
import json,os,time
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for ident in ['agulhas-reference-path-candidate', 'south-atlantic-reach-reference-path-candidate']:
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#' + ident, wait_until='networkidle')
            page.wait_for_function('(id) => Math.abs(document.getElementById(id)?.getBoundingClientRect().top - 16) < 3', arg=ident)
            card = page.locator('#' + ident)
            assert card.locator('.route-map').is_visible()
            assert card.locator('.route-map').evaluate('(image) => image.complete && image.naturalWidth > 0')
            assert page.evaluate('document.activeElement.id') == ident
        page.locator('a[href="#comparison-title"]').click()
        page.locator('#comparison-agulhas-reference-path-candidate > td:first-child a').click()
        page.wait_for_function('Math.abs(document.getElementById("agulhas-reference-path-candidate").getBoundingClientRect().top - 16) < 3')
        page.go_back(wait_until='networkidle')
        assert page.url.endswith('#comparison-title')
        proposals=json.loads(Path('research/ocean-current-inventory-expansion-candidates.json').read_text(encoding='utf-8'))['entries']
        # Both data loads can finish in either order. Test cold direct links and
        # restored fragment navigation for every proposed identity.
        for row in proposals:
            ident='inventory-addition-'+row['proposed_id']
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#'+ident,wait_until='networkidle')
            page.wait_for_function('(id)=>{const top=document.getElementById(id)?.getBoundingClientRect().top;return document.activeElement.id===id && (Math.abs(top-16)<3 || (Math.abs(scrollY-(document.documentElement.scrollHeight-innerHeight))<3 && top>=0 && top<innerHeight-60));}',arg=ident)
            card=page.locator('#'+ident)
            assert row['name'] in card.locator('h3').inner_text()
            card.get_by_role('link',name='Back to current atlas',exact=True).click()
            page.wait_for_function('document.activeElement.id==="route-atlas"')
            page.go_back(wait_until='networkidle')
            page.wait_for_function('(id)=>document.activeElement.id===id',arg=ident)
        for delayed_file in ['ocean-current-inventory-expansion-candidates.json','ocean-current-reference-path-candidates.json']:
            def delayed(route):
                response=route.fetch();time.sleep(.25);route.fulfill(response=response)
            pattern='**/'+delayed_file
            page.route(pattern,delayed)
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#inventory-addition-mozambique',wait_until='networkidle')
            page.wait_for_function('document.activeElement.id==="inventory-addition-mozambique" && Math.abs(document.getElementById("inventory-addition-mozambique").getBoundingClientRect().top-16)<3')
            page.unroute(pattern,delayed)
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aaleutian#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:aleutian"')
        page.locator('.route-atlas-scope-reviews a[href="#inventory-addition-aleutian-north-slope"]').focus()
        page.keyboard.press('Enter')
        page.wait_for_function('document.activeElement.id==="inventory-addition-aleutian-north-slope"')
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#inventory-addition-aleutian-north-slope').get_by_role('link',name='Link to this proposed current',exact=True).click()
        assert page.evaluate('document.activeElement.id')=='inventory-addition-aleutian-north-slope'
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#inventory-addition-aleutian-north-slope').screenshot(path='figures/proposal-navigation-focus-review.png')
        assert not errors, errors
        browser.close()
    print(f'OK: two mapped route links, all {len(proposals)} proposed-card deep links/Back/focus, Aleutian keyboard relation, repeated link and mobile reflow')


if __name__ == '__main__':
    main()
