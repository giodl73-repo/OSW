"""Check Atlantic EUC reach scope, visual atlas navigation and ordering exclusion."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.locator('#route-atlas-select').select_option('current:atlantic-equatorial-undercurrent')
        page.locator('#route-atlas-preview').get_by_role('link',name='Full route card, measurements and sources').click()
        page.wait_for_function('location.hash === "#atlantic-euc-reach-reference-path-candidate"')
        card=page.locator('#atlantic-euc-reach-reference-path-candidate')
        assert card.locator('.route-map').is_visible()
        text=card.inner_text()
        for expected in ['4,500','4,300','4,600','subsurface','Excludes western North Brazil','Not full']:
            assert expected in text,expected
        assert page.locator('#reference-route-rows tr').count()==37
        assert page.locator('#reference-route-rows a[href="#atlantic-euc-reach-reference-path-candidate"]').count()==0
        card.locator('.route-map').screenshot(path='figures/atlantic-euc-reach-reference-path-review.png')
        card.get_by_role('link',name='Back to global current map').click()
        assert page.url.endswith('#route-atlas')
        snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
        row=next(r for r in snapshot['entries'] if r['id']=='current:atlantic-equatorial-undercurrent')
        assert row['capabilities']['reference_route']==1
        assert row['capabilities']['scope_notes']==1
        assert row['capabilities']['scoped_width']==0
        assert row['latest_observation_date'] is None
        assert not errors,errors
        browser.close()
    print('OK: Atlantic EUC subsurface reach map, partial extent, 37-row comparison exclusion, global return and unresolved dimensions/dates')

if __name__=='__main__':main()
