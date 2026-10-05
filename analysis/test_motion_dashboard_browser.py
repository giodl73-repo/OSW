"""Check dashboard coverage, filtering and content-based update indicators."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = json.loads((ROOT / 'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page = browser.new_page(viewport={'width':1440,'height':1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        url = 'http://127.0.0.1:8788/almanac/dashboard.html'
        page.goto(url,wait_until='networkidle')
        assert page.locator('#dashboard-schematic').is_visible()
        assert page.locator('.beck-station').count() == 100
        assert '100 / 100 current stations in view' in page.locator('#dashboard-station-count').inner_text()
        page.locator('#dashboard-search').fill('Portugal Current')
        page.locator('#dashboard-covered').check()
        page.locator('#dashboard-region').select_option('atlantic')
        assert page.locator('.beck-station').count() == 1
        page.locator('#dashboard-show-all').click()
        assert page.locator('.beck-station').count() == 100
        assert page.locator('#dashboard-region').input_value() == 'world'
        assert not page.locator('#dashboard-covered').is_checked()
        assert page.locator('.beck-station .beck-name').count() == 100
        station=page.locator('.beck-station').first
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '0'
        station.locator('circle').hover()
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '1'
        page.mouse.move(0,0)
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '0'
        station.focus()
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '1'
        stations=page.locator('.beck-station').evaluate_all('(els)=>els.map(e=>({n:Number(e.dataset.stationNumber),x:Number(e.dataset.worldX),y:Number(e.dataset.worldY)}))')
        assert sorted(s['n'] for s in stations) == list(range(1,101))
        assert all(74<=s['x']<=1526 and 104<=s['y']<=816 for s in stations)
        assert all(((a['x']-b['x'])**2+(a['y']-b['y'])**2)**.5>=30 for i,a in enumerate(stations) for b in stations[i+1:])
        assert page.locator('.beck-eddy-gateway').count() > 10
        assert page.locator('.beck-connection').count() == 5
        page.locator('.beck-connection').first.focus()
        page.keyboard.press('Enter')
        assert 'Read the source' in page.locator('#dashboard-schematic-detail').inner_text()
        assert page.locator('.schematic-station').count() == 100
        assert page.locator('.schematic-station text').count() == 100
        page.locator('.schematic-station').first.focus()
        page.keyboard.press('Enter')
        assert page.locator('#dashboard-schematic-detail').is_visible()
        page.locator('#dashboard-map-view').click()
        assert page.locator('#dashboard-atlas').is_visible()
        assert page.locator('#dashboard-grid').is_hidden()
        assert page.locator('.atlas-marker').count() > 100
        page.locator('#dashboard-search').fill('Portugal Current')
        assert page.locator('.atlas-route.lit').count() == 1
        page.locator('.atlas-marker').first.focus()
        page.keyboard.press('Enter')
        assert 'Portugal Current' in page.locator('#dashboard-map-detail').inner_text()
        page.locator('#dashboard-search').fill('')
        page.locator('#dashboard-schematic-view').click()
        page.locator('#dashboard-search').fill('Antilles Current')
        page.locator('#dashboard-metric').select_option('scope_notes')
        assert page.locator('.beck-station.lit').count() == 1
        page.locator('.beck-station').first.focus()
        page.keyboard.press('Enter')
        assert 'Modern observations' in page.locator('#dashboard-schematic-detail').inner_text()
        page.locator('#dashboard-search').fill('')
        page.locator('#dashboard-metric').select_option('reference_route')
        page.locator('#dashboard-map-view').click()
        page.locator('#dashboard-type').select_option('named_eddy')
        page.locator('#dashboard-region').select_option('gulf')
        gateway=page.locator('.atlas-marker').filter(has=page.locator('.marker-label')).first
        gateway.locator('.marker-core').click()
        assert 'regional gateway' in page.locator('#dashboard-map-detail').inner_text()
        assert page.locator('#dashboard-map-detail h4').count() >= 96
        page.locator('#dashboard-region').select_option('world')
        page.locator('#dashboard-type').select_option('all')
        page.locator('#dashboard-atlas').screenshot(path=str(ROOT / 'figures/motion-dashboard-atlas-review.png'))
        page.locator('#dashboard-card-view').click()
        assert page.locator('.motion-card').count() == 240
        assert page.locator('.motion-card.updated').count() == 0
        gulf=page.locator('[data-id="current:gulf-stream-system"]')
        gulf.locator('summary').click()
        assert '2026-09-28' in gulf.inner_text()
        coastal=page.locator('[data-id="current:norwegian-coastal"]')
        coastal.locator('summary').click()
        assert '2024-12-15' in coastal.inner_text()
        assert 'not individually reviewed' in coastal.inner_text()
        for metric in ['reference_route','reported_length','scoped_width','geometry','time_samples','source_connectivity','scope_notes','dated_diagnostics','flow_network','passage_transport']:
            page.locator('#dashboard-metric').select_option(metric)
            expected=sum(r['capabilities'][metric]>0 for r in data['entries'])
            assert page.locator('.motion-card.lit').count() == expected
            page.locator('#dashboard-covered').check()
            assert page.locator('.motion-card').count() == expected
            page.locator('#dashboard-covered').uncheck()
        page.locator('#dashboard-type').select_option('named_eddy')
        assert page.locator('.motion-card').count() == 136
        page.locator('#dashboard-type').select_option('all')
        page.locator('#dashboard-search').fill('Portugal Current')
        assert page.locator('.motion-card').count() == 1
        assert 'reference-routes.html#portugal' in page.locator('.record-links a').first.get_attribute('href')
        page.locator('#dashboard-search').fill('')
        page.locator('#dashboard-grid').screenshot(path=str(ROOT / 'figures/motion-dashboard-cards-review.png'))
        changed=json.loads(json.dumps(data))
        changed['entries'][0]['fingerprint']='test-new-record-content'
        changed['entries'][0]['section_fingerprints']['sources']='test-source-change'
        page.route('**/research/ocean-motion-dashboard.json',lambda route:route.fulfill(json=changed))
        page.locator('#dashboard-refresh').click()
        page.wait_for_function("document.querySelectorAll('.motion-card.updated').length === 1")
        assert '1 changed since marked seen' in page.locator('#dashboard-status').inner_text()
        assert 'Sources changed' in page.locator('.motion-card.updated .change-reason').inner_text()
        page.locator('#dashboard-changed').check()
        assert page.locator('.motion-card').count() == 1
        page.reload(wait_until='networkidle')
        assert page.locator('.motion-card.updated').count() == 1
        assert page.locator('.atlas-marker.updated').count() > 0
        page.locator('#dashboard-card-view').click()
        page.locator('#dashboard-seen').click()
        assert page.locator('.motion-card.updated').count() == 0
        page.locator('#dashboard-refresh').click()
        page.wait_for_function("!document.getElementById('dashboard-refresh').disabled")
        assert page.locator('.motion-card.updated').count() == 0
        page.unroute('**/research/ocean-motion-dashboard.json')
        page.route('**/research/ocean-motion-dashboard.json',lambda route:route.fulfill(status=503,body='unavailable'))
        page.locator('#dashboard-refresh').click()
        page.wait_for_function("document.getElementById('dashboard-status').textContent.includes('previously loaded')")
        assert page.locator('.motion-card').count() == 240
        page.emulate_media(reduced_motion='reduce')
        page.set_viewport_size({'width':320,'height':900})
        page.locator('#dashboard-map-view').click()
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.screenshot(path=str(ROOT / 'figures/motion-dashboard-mobile-review.png'),full_page=False)
        assert not errors,errors
        browser.close()
    print('OK: atlas routes, keyboard selection, shared eddy gateway, 240 records, coverage lights, updates, outage retention and mobile layout')


if __name__ == '__main__': main()
