"""Dashboard evidence lights and direct, shareable mapped record cards."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8788/almanac/dashboard.html'

def main():
    data=json.loads((ROOT/'research/ocean-motion-dashboard.json').read_bytes())
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE);expect(page.locator('.beck-station')).to_have_count(100)
        for metric,owner in [('dated_diagnostics','current:loop'),('flow_network','current:indonesian-throughflow'),('passage_transport','current:indonesian-throughflow')]:
            page.locator('#dashboard-metric').select_option(metric)
            expect(page.locator('.beck-station.lit')).to_have_count(1)
            assert page.locator('.beck-station.lit').get_attribute('data-current-id')==owner
        page.locator('#dashboard-metric').select_option('flow_network')
        page.locator('.beck-station.lit').focus();page.keyboard.press('Enter')
        link=page.locator('#dashboard-schematic-detail a').filter(has_text='Open passage network card')
        target=link.evaluate('(a)=>a.href');link.click()
        expect(page.locator('#query-detail')).to_contain_text('All twelve named nodes',timeout=60000)
        expect(page.locator('#query-detail svg [role="button"]')).to_have_count(12)
        assert 'inspect=' in page.url
        shared=page.locator('#query-share').get_attribute('href')
        page.reload();expect(page.locator('#query-detail')).to_contain_text('All twelve named nodes',timeout=60000)
        assert page.url==shared
        page.locator('#query-run').click();expect(page.locator('#query-detail')).to_be_hidden()
        assert 'inspect=' not in page.url
        page.goto(BASE);expect(page.locator('.beck-station')).to_have_count(100)
        page.locator('#dashboard-metric').select_option('dated_diagnostics')
        page.locator('.beck-station.lit').focus();page.keyboard.press('Enter')
        page.locator('#dashboard-schematic-detail a').filter(has_text='Open mapped Loop Current card').click()
        expect(page.locator('#query-detail')).to_contain_text('Unranked method diagnostics (10)',timeout=60000)
        assert page.evaluate('window.oswLastQueryResult.map_scene.features.filter(f=>f.frame_id).length')==7
        page.goto(BASE);expect(page.locator('.beck-station')).to_have_count(100)
        page.locator('#dashboard-card-view').click();page.locator('#dashboard-metric').select_option('flow_network')
        page.locator('#dashboard-covered').check()
        expect(page.locator('.motion-card')).to_have_count(1)
        assert 'inspect=flow-network%3Aindonesian-throughflow' in page.locator('.motion-card h3 a').get_attribute('href')
        page.locator('.motion-card summary').click()
        expect(page.locator('.motion-card')).to_contain_text('Observed passage transport: 3')
        page.locator('#dashboard-grid').screenshot(path=str(ROOT/'figures/dashboard-network-coverage-review.png'))
        changed=json.loads(json.dumps(data));owner=next(r for r in changed['entries'] if r['id']=='current:indonesian-throughflow')
        owner['fingerprint']='test-network-update';owner['section_fingerprints']['measurements']='test-passage-update'
        page.route('**/research/ocean-motion-dashboard.json',lambda route:route.fulfill(json=changed))
        page.locator('#dashboard-refresh').click()
        expect(page.locator('.motion-card.updated')).to_have_count(1)
        expect(page.locator('.change-reason')).to_contain_text('Measurements changed')
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.unroute('**/research/ocean-motion-dashboard.json')
        page.goto(target.replace('inspect=flow-network%3Aindonesian-throughflow','inspect=unknown'))
        expect(page.locator('#query-status')).to_contain_text('Selected record is not in this result page',timeout=60000)
        expect(page.locator('#query-detail')).to_be_hidden()
        assert page.evaluate('window.oswLastQueryResult.total')==1
        expect(page.locator('#query-rows tr')).to_have_count(1)
        assert not errors;browser.close()
    print('PASS: three scoped coverage lights, direct network/Loop map cards, share/reload, selection clearing, isolated updates and mobile access')

if __name__=='__main__':main()
