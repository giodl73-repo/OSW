"""Saved samples retain exact geometry, date, scope and lifecycle in the atlas."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    sets={year:json.loads(Path(path).read_text()) for year,path in [('2025','research/ocean-current-dated-timeline-2025.json'),('2026','research/ocean-current-dated-timeline.json')]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Agulf-stream-system#route-atlas',wait_until='networkidle')
        host=page.locator('.atlas-timeline');host.locator('summary').click()
        page.locator('.atlas-timeline-date').wait_for(state='visible')
        page.wait_for_function("!document.querySelector('.atlas-timeline-date').disabled")
        for year,data in sets.items():
            if year!='2025':host.locator('.atlas-timeline-series').select_option(year)
            page.wait_for_function("!document.querySelector('.atlas-timeline-date').disabled")
            assert host.locator('.atlas-timeline-date option').count()==len(data['frames'])
            initial=page.locator('#route-atlas-map').get_attribute('viewBox')
            for index,frame in enumerate(data['frames']):
                host.locator('.atlas-timeline-date').select_option(str(index))
                assert frame['date'] in host.locator('.atlas-timeline-status').inner_text()
                assert frame['date'] in page.locator('#route-atlas-status').inner_text()
                assert page.locator('#route-atlas-dated-lines path:visible').count()==0
                assert frame['source_algorithm'] in host.inner_text()
                intersections=host.locator('.atlas-timeline-states li[data-state-code]')
                assert intersections.count()==len(frame['state_relations'])
                for relation in frame['state_relations']:
                    row=host.locator(f'.atlas-timeline-states li[data-state-code="{relation["state_code"]}"]')
                    assert row.get_attribute('data-predicate')==relation['predicate']
                    assert f'{int(relation["intersection_length_km"]+0.5):,}' in row.inner_text()
                    assert 'diagnostic-date='+frame['date'] in row.locator('a').get_attribute('href')
                assert frame['stop_reason'].replace('_',' ') in host.inner_text()
                assert data['sampling_note'] in host.inner_text()
                assert data['limitations'] in host.inner_text()
                assert host.locator(f'a[href="{frame["source_url"]}"]').count()==1
                assert page.locator('#route-atlas-map').get_attribute('viewBox')==initial
                actual=page.locator('#route-atlas-features > .atlas-timeline-line').get_attribute('d')
                # Browser and Python float-to-string formatting differ; compare projected coordinates numerically.
                import re
                assert len(re.findall(r'[ML]',actual))==len(frame['coordinates_lon_lat'])
                points=[tuple(map(float,x.split(','))) for x in re.split('[ML]',actual) if x.strip()]
                for (x,y),(lon,lat) in zip(points,frame['coordinates_lon_lat']):
                    assert abs(x-(60+(lon+180)/360*1480))<1e-9 and abs(y-(90+(90-lat)/180*740))<1e-9
                assert page.locator('.route-atlas-dated-content').is_hidden()
            shared=page.locator('[data-atlas-share]').get_attribute('href')
            fresh=browser.new_page();fresh.goto(shared,wait_until='networkidle')
            fresh.wait_for_function("document.querySelector('.atlas-timeline-date') && !document.querySelector('.atlas-timeline-date').disabled")
            assert data['frames'][-1]['date'] in fresh.locator('.atlas-timeline-status').inner_text();fresh.close()
        host.locator('.atlas-timeline-date').select_option('0')
        host.get_by_role('button',name='Play samples',exact=True).click()
        page.wait_for_function("document.querySelector('.atlas-timeline-date').value==='1'",timeout=5000)
        page.locator('[data-geometry-id="geometry:0150"][aria-pressed]').click()
        assert host.get_by_role('button',name='Play samples',exact=True).count()==1
        assert page.locator('#route-atlas-features > .atlas-timeline-line').count()==0
        assert page.locator('.route-atlas-dated-content').is_visible()
        assert page.locator('#route-atlas-dated-lines path:visible').count()==3
        host.locator('.atlas-timeline-date').select_option('0')
        host.get_by_role('button',name='Play samples',exact=True).click()
        host.locator('summary').click()
        page.wait_for_function("document.querySelector('.atlas-timeline button').textContent==='Play samples'")
        host.locator('summary').click()
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas').screenshot(path='figures/atlas-timeline-review.png')
        page.locator('#route-atlas-world').click()
        assert page.locator('.atlas-timeline').count()==0
        assert page.locator('#route-atlas-features > .atlas-timeline-line').count()==0
        assert 'atlas-date' not in page.url and 'atlas-series' not in page.url
        page.locator('#route-atlas-select').select_option('current:gulf-stream')
        assert page.locator('.atlas-timeline').count()==0
        detail=browser.new_page();detail.goto('http://127.0.0.1:8788/almanac/dated-current.html?series=2025&date=2025-08-15',wait_until='networkidle')
        assert '2025-08-15' in detail.locator('#dated-value').inner_text();detail.close()
        assert not errors,errors
        browser.close()
    print('OK: all 17 exact saved geometries, dates, gaps, sources, stable map scale, fresh share restoration, playback stop, mobile and identity boundary')


if __name__=='__main__':
    main()
