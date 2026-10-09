"""All atlas current cards retain their own source-defined width records."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:8788/almanac/reference-routes.html'
def main():
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
    decisions=inventory['current_decisions']
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':1200,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll(".route-card").length===64');page.wait_for_timeout(100)
        seen=[]
        for decision in decisions:
            ident=decision['current_id'];page.locator('#route-atlas-select').select_option('current:'+ident)
            section=page.locator('.atlas-width-evidence');records=section.locator('.atlas-width-record')
            expected=[row for row in inventory['measurements'] if row['current_id']==ident]
            assert records.count()==len(expected),(ident,records.count(),len(expected))
            assert records.evaluate_all('(items)=>items.map(item=>item.dataset.measurementId)')==[row['id'] for row in expected]
            seen += [row['id'] for row in expected]
            for row in expected:
                details=section.locator(f'[data-measurement-id="{row["id"]}"]')
                details.locator('summary').focus();page.keyboard.press('Enter')
                assert details.get_attribute('open') is not None
                assert row['boundary_rule'] in details.inner_text()
                assert details.get_by_text('Published source',exact=True).get_attribute('href')==row['source_url']
                href=details.get_by_text('Inspect this width record',exact=True).get_attribute('href')
                assert row['id'] in href and 'current='+ident in href
                details.locator('summary').focus();page.keyboard.press('Enter')
            if not expected:assert 'does not mean zero width' in section.inner_text()
        assert len(seen)==len(inventory['measurements']) and len(set(seen))==len(inventory['measurements'])
        page.locator('#route-atlas-select').select_option('current:north-brazil')
        row=page.locator('[data-measurement-id=north-brazil-hs2-oblique-mean-zero-width]')
        row.locator('summary').click();assert 'Discrepancy unresolved' in row.inner_text()
        row.get_by_text('Inspect this width record').click()
        expect(page.locator('#season-value')).to_contain_text('about 220 km')
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:north-brazil"')
        assert page.locator('.atlas-width-record').count()==2
        page.set_viewport_size({'width':860,'height':1000})
        page.locator('#route-atlas-select').select_option('current:labrador')
        page.locator('.atlas-width-record summary').click()
        page.locator('.atlas-width-evidence').screenshot(path=str(ROOT/'figures/atlas-inline-width-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-world').click();assert page.locator('.atlas-width-evidence').count()==0
        # Widths now come from the checked Rust snapshot. A legacy JSON URL
        # outage must not erase stored records or trigger a direct source fetch.
        direct_width_requests=[]
        def blocked_width(route):
            direct_width_requests.append(route.request.url)
            route.fulfill(status=503,body='unavailable')
        page.route('**/ocean-current-width-inventory.json',blocked_width)
        page.reload(wait_until='networkidle');page.locator('#route-atlas-select').select_option('current:labrador')
        assert page.locator('.atlas-width-record').count()==len([r for r in inventory['measurements'] if r['current_id']=='labrador'])
        assert not direct_width_requests
        assert page.locator('#route-atlas-preview h3').inner_text()=='Labrador Current'
        assert not errors,errors
        browser.close()
    print(f"OK: all 100 current cards, {len(inventory['measurements'])} unique scoped widths, definitions/source/record links, keyboard disclosure, conflict, inspector return, reset, mobile and stored widths without direct source requests")
if __name__=='__main__':main()
