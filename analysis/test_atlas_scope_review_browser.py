"""Scope reviews stay visible without inheriting routes from similar names."""
import json,hashlib,os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    reviewed=[r for r in snapshot['entries'] if r.get('scope_notes')]
    proposals=json.loads(Path('research/ocean-current-inventory-expansion-candidates.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()==proposals['current_ledger_sha256']
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':320,'height':800});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll("#route-atlas-select option").length===101')
        for row in reviewed:
            page.locator('#route-atlas-select').select_option(row['id'])
            review=page.locator('.route-atlas-scope-reviews')
            assert review.is_visible()
            for note in row['scope_notes']:
                assert note['summary'] in review.inner_text()
                assert review.locator(f'a[href="../{note["audit_file"]}"]').count()==1
                assert review.locator(f'a[href="{note["source_url"]}"]').count()>=1
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-select').select_option('current:persian-gulf-saline-overflow')
        assert page.locator('.route-atlas-local-dimensions tbody tr').count()==6
        assert '30–35' in page.locator('.route-atlas-local-dimensions').inner_text()
        assert 'R17: 230' in page.locator('.route-atlas-local-dimensions').inner_text()
        assert 'not annual extrema' in page.locator('.route-atlas-scope-reviews').inner_text()
        assert page.locator('#route-atlas-preview .route-map').count()==0
        page.reload(wait_until='networkidle')
        assert page.locator('.route-atlas-local-dimensions tbody tr').count()==6
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('.route-atlas-local-dimensions').screenshot(path='figures/persian-gulf-core-scope-card-review.png')
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#route-atlas-select').select_option('current:red-sea-saline-overflow')
        reach=page.locator('.route-atlas-reported-reach')
        assert 'About 130 km' in reach.inner_text()
        assert 'not a fixed depth interval' in reach.inner_text()
        assert 'not a whole-current length' in reach.inner_text()
        assert reach.locator('.route-atlas-outflow-branches li').count()==3
        assert page.locator('#route-atlas-preview .route-map').count()==0
        reach.locator('summary').click()
        assert 'about 115 km long' in reach.inner_text() and 'about 120 km long' in reach.inner_text()
        assert 'not current width estimates' in reach.inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.reload(wait_until='networkidle')
        assert page.locator('.route-atlas-outflow-branches li').count()==3
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('.route-atlas-reported-reach').screenshot(path='figures/red-sea-reported-reach-card-review.png')
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#route-atlas-select').select_option('current:norwegian')
        assert page.locator('#route-atlas-preview .route-map').count()==0
        page.locator('.route-atlas-scope-reviews a[data-atlas-current="current:norwegian-coastal"]').click()
        assert page.locator('#route-atlas-select').input_value()=='current:norwegian-coastal'
        page.locator('#route-atlas-select').select_option('current:spitsbergen-atlantic')
        assert page.locator('#route-atlas-preview .route-map').count()==0
        page.locator('.route-atlas-scope-reviews a[data-atlas-current="current:west-spitsbergen"]').click()
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        page.locator('#route-atlas-select').select_option('current:guiana')
        assert page.locator('#route-atlas-preview .route-map').count()==0
        assert 'ring motion remain separate' in page.locator('.route-atlas-scope-reviews').inner_text()
        page.locator('.route-atlas-scope-reviews a[data-atlas-current="current:north-brazil"]').click()
        assert page.locator('#route-atlas-select').input_value()=='current:north-brazil'
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        for ident in ['norwegian-atlantic','norwegian-atlantic-slope','norwegian-atlantic-front']:
            card=page.locator('#inventory-addition-'+ident)
            assert 'no whole-current length or rank admitted' in card.inner_text()
            assert card.locator('a[href="https://os.copernicus.org/articles/22/17/2026/"]').count()==1
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('#route-atlas-select').select_option('current:norwegian')
        page.locator('#route-atlas').screenshot(path='figures/norwegian-naming-scope-review.png')
        assert not errors,errors
        browser.close()
    print(f'OK: {len(reviewed)} atlas source-scope reviews, Norwegian/Spitsbergen related navigation, three proposed identities, no borrowed routes and mobile reflow')


if __name__=='__main__':main()
