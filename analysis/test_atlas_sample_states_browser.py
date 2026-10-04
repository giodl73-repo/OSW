"""Every pinned dated relation has state-to-map and map-to-state navigation."""
import json
import os
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright


def main():
    sets={year:json.loads(Path(path).read_text(encoding='utf-8')) for year,path in [('2025','research/ocean-current-dated-timeline-2025.json'),('2026','research/ocean-current-dated-timeline.json')]}
    states=json.loads(Path('research/ocean-current-reference-route-state-join.json').read_text(encoding='utf-8'))['states']
    expected={code:[(year,frame,relation) for year,data in sets.items() for frame in data['frames'] for relation in frame['state_relations'] if relation['state_code']==code] for code in states}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/index.html?state=GFST&diagnostic-series=2025&diagnostic-date=2025-03-15#state-title',wait_until='networkidle')
        section=page.locator('.state-dated-samples')
        page.wait_for_function("document.querySelector('.state-dated-samples ul')")
        assert section.get_attribute('open') is not None
        assert section.locator('.requested-diagnostic-sample').get_attribute('data-sample-date')=='2025-03-15'
        checked=0
        for code,relations in expected.items():
            page.locator('#state-select').select_option(code)
            page.wait_for_function("document.querySelector('.state-dated-samples ul')")
            assert section.locator('li[data-sample-date]').count()==len(relations)
            for year,frame,relation in relations:
                row=section.locator(f'li[data-sample-date="{frame["date"]}"]')
                assert row.get_attribute('data-predicate')==relation['predicate']
                assert f'{int(relation["intersection_length_km"]+0.5):,}' in row.inner_text()
                assert frame['source_algorithm'] in row.inner_text()
                href=row.locator('a').get_attribute('href')
                assert 'atlas-date='+frame['date'] in href and 'atlas-series='+year in href
                checked+=1
            if not relations:
                section.locator('summary').click()
                assert 'current absence is not established' in section.inner_text()
        assert checked==36
        page.locator('#state-select').select_option('NAST W')
        page.wait_for_function("document.querySelector('.state-dated-samples ul')")
        if section.get_attribute('open') is None:section.locator('summary').click()
        section.locator('li[data-sample-date="2025-03-15"] a').click()
        page.wait_for_function("document.querySelector('.atlas-timeline-date') && !document.querySelector('.atlas-timeline-date').disabled")
        assert '2025-03-15' in page.locator('.atlas-timeline-status').inner_text()
        page.locator('.atlas-timeline-states li[data-state-code="NAST W"] a').click()
        page.wait_for_function("document.querySelector('.state-dated-samples ul')")
        assert page.locator('#state-select').input_value()=='NAST W'
        assert page.locator('.requested-diagnostic-sample').get_attribute('data-sample-date')=='2025-03-15'
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('.state-dated-samples').screenshot(path='figures/atlas-sample-state-links-review.png')
        # Optional dated evidence failure must leave other state inventories available.
        failed=browser.new_page()
        failed.route('**/ocean-current-dated-timeline*.json',lambda route:route.fulfill(status=503,body='Unavailable'))
        failed.goto('http://127.0.0.1:8788/almanac/index.html?state=GFST#state-title',wait_until='networkidle')
        failed.wait_for_function("document.querySelector('.state-dated-samples ul')")
        failed.locator('.state-dated-samples summary').click()
        assert 'Some diagnostic sample sets are unavailable' in failed.locator('.state-dated-samples').inner_text()
        assert failed.locator('#state-select option').count()>50
        failed.close()
        assert not errors,errors
        browser.close()
    print('OK: all 56 states / 36 dated diagnostic intersections, exact predicates/dates, state-atlas-state round trip, mobile and optional source failure')


if __name__=='__main__':
    main()
