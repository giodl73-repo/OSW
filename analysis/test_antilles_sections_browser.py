"""Pinned observed sections are reachable without promoting current width."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    root=Path(__file__).resolve().parents[1]
    snapshot=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    current=next(r for r in snapshot['entries'] if r['id']=='current:antilles')
    assert current['capabilities']['scoped_width']==0
    assert current['capabilities']['reference_route']==0
    assert current['series'][0]['frames']==2
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1100});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aantilles#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:antilles"')
        page.locator('#route-atlas-preview a[href="antilles-sections.html"]').click()
        page.wait_for_function('document.querySelector("#section-select").disabled===false')
        assert page.locator('#section-samples tr').count()==23
        assert 'boundary unresolved' in page.locator('#section-status').inner_text()
        assert page.locator('.section-chart').evaluate('(img)=>img.complete && img.naturalWidth>0')
        page.locator('#section-select').select_option('abaco_repeat')
        assert page.locator('#section-samples tr').count()==27
        assert 'About 37 km sampled-peak-to-offshore-half-peak span' in page.locator('#section-status').inner_text()
        assert 'Full width and annual ranges unknown' in page.locator('#section-status').inner_text()
        assert page.url.endswith('?section=abaco_repeat')
        page.reload(wait_until='networkidle')
        assert page.locator('#section-select').input_value()=='abaco_repeat'
        x,y,w,h=map(float,page.locator('#section-stations').get_attribute('viewBox').split())
        for circle in page.locator('#section-station-layer circle').all():
            assert x<=float(circle.get_attribute('cx'))<=x+w
            assert y<=float(circle.get_attribute('cy'))<=y+h
        station=page.locator('.sample-station').first
        assert station.locator('.station-name').evaluate('(el)=>getComputedStyle(el).opacity')=='0'
        station.focus()
        assert station.locator('.station-name').evaluate('(el)=>getComputedStyle(el).opacity')=='1'
        assert '2005-05' in station.get_attribute('aria-label')
        page.screenshot(path=str(root/'figures/antilles-sections-page-review.png'),full_page=True)
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#section-select').select_option('abaco_first')
        assert page.locator('#section-samples tr').count()==23
        assert '37 km' not in page.locator('#section-status').inner_text()
        page.get_by_role('link',name='Return to Antilles on the atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:antilles"')
        assert not errors,errors
        browser.close()
    print('OK: atlas -> observed sections -> restored repeat -> atlas; 23/27 cast tables, map support, focus labels, source chart and mobile reflow; no width/route admission')

if __name__=='__main__':main()
