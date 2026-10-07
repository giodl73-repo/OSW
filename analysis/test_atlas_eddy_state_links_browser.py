"""Verify dated eddy relations and locator evidence stay distinct in atlas cards."""
import json
import os
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    snapshot=read('research/ocean-motion-dashboard.json')
    eddies=[r for r in snapshot['entries'] if r['type']!='named_current']
    provider=read('almanac/release/v0.1.0/operational_eddy_state_observations.json')
    assessments=read('almanac/release/v0.1.0/named_eddy_state_assessments.json')
    for row in eddies:
        records=row['state_evidence']
        if row['type']=='operational_eddy_detection':
            expected=[r for r in provider if r['operational_eddy_id']==row['id']]
            assert {(r['state_code'],r['observation_date']) for r in records}=={(r['state_id'].removeprefix('state:'),r['observation_date']) for r in expected}
            assert all(r['kind']=='dated_provider_polygon' for r in records)
        for assessment in assessments:
            if assessment['eddy_id']==row['id'] and assessment['physical_relation']!='unknown_no_dated_eddy_footprint':
                assert any(r['source_record_id']==assessment['id'] for r in records)
        assert all(r['source_record_id'] not in {a['id'] for a in assessments if a['eddy_id']==row['id'] and a['physical_relation']=='unknown_no_dated_eddy_footprint'} for r in records)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        total=0
        for row in eddies:
            page.locator('#route-atlas-eddy-select').select_option(row['id'])
            card_map=page.locator('.route-atlas-eddy-map')
            assert card_map.count()==1
            assert row['label'] in card_map.get_attribute('aria-label')
            assert card_map.get_attribute('viewBox')==page.locator('#route-atlas-map').get_attribute('viewBox')
            feature=next((f for f in row['map_features'] if f['geometry']['type']=='Polygon'),row['map_features'][0])
            if feature['geometry']['type']=='Polygon':
                assert card_map.locator('.route-atlas-eddy-footprint').count()==1
                assert card_map.locator('circle').count()==0
                assert 'Historical snapshot' in card_map.get_attribute('aria-label')
                assert 'closeup-ground.svg' in card_map.locator('image').get_attribute('href')
                assert 'closeup-ground.svg' in page.locator('#route-atlas-map > image').get_attribute('href')
                assert card_map.evaluate('svg=>{const v=svg.viewBox.baseVal;const g=svg.querySelector("path").getBBox();return g.x>=v.x&&g.y>=v.y&&g.x+g.width<=v.x+v.width&&g.y+g.height<=v.y+v.height;}')
            else:
                assert card_map.locator('circle').count()==1
                assert card_map.locator('.route-atlas-eddy-footprint').count()==0
                expected='no individual center' if feature['role']=='shared_regional_gateway' else 'footprint'
                assert expected in card_map.get_attribute('aria-label')
                x,y,width,height=map(float,card_map.get_attribute('viewBox').split())
                lon,lat=feature['geometry']['coordinates']
                assert x<=60+(lon+180)/360*1480<=x+width
                assert y<=90+(90-lat)/180*740<=y+height
            panel=page.locator('.route-atlas-eddy-state-links')
            items=panel.locator('li')
            assert items.count()==len(row['state_evidence'])
            for index,record in enumerate(row['state_evidence']):
                item=items.nth(index)
                assert item.get_attribute('data-evidence-kind')==record['kind']
                assert item.locator('a').first.get_attribute('href')==f'index.html?state={quote(record["state_code"])}#state-title'
                assert record['label'] in item.inner_text()
                assert (record['observation_date'] or 'exact observation date unresolved') in item.inner_text()
                assert item.get_by_role('link',name='Evidence receipt').get_attribute('href')=='../'+record['source_file']
            assert 'does not establish whole-eddy containment' in panel.inner_text()
            total+=items.count()
        # Polygon cards survive shared links and retain their own extent during main-map zoom.
        page.locator('#route-atlas-eddy-select').select_option('eddy:published:kraken-2013')
        saved=page.url;box=page.locator('.route-atlas-eddy-map').get_attribute('viewBox')
        page.locator('#route-atlas-in').click()
        assert page.locator('.route-atlas-eddy-map').get_attribute('viewBox')==box,(box,page.locator('.route-atlas-eddy-map').get_attribute('viewBox'),page.url)
        page.goto(saved,wait_until='networkidle')
        # Shared atlas frames are explicitly encoded to six decimal places.
        restored=page.locator('.route-atlas-eddy-map').get_attribute('viewBox')
        assert all(abs(a-b)<.000002 for a,b in zip(map(float,box.split()),map(float,restored.split()))),(box,restored)
        page.locator('.route-atlas-eddy-map').screenshot(path='figures/eddy-atlas-card-review.png')
        page.evaluate('''()=>{const key="osw-motion-dashboard-seen-v2",baseline=JSON.parse(localStorage.getItem(key));baseline["eddy:published:kraken-2013"].fingerprint="older-fixture";localStorage.setItem(key,JSON.stringify(baseline));}''')
        page.reload(wait_until='networkidle')
        expect(page.locator('.route-atlas-eddy-map.updated')).to_have_count(1,timeout=90000)
        assert 'Updated since your saved baseline' in page.locator('#route-atlas-preview').inner_text()
        point=next(r for r in eddies if r['map_features'][0]['geometry']['type']=='Point')
        page.locator('#route-atlas-eddy-select').select_option(point['id'])
        assert page.locator('.route-atlas-eddy-map.updated').count()==0
        page.mouse.move(0,0)
        name=page.locator('.route-atlas-eddy-map text')
        assert name.evaluate('node=>getComputedStyle(node).opacity')=='0'
        page.locator('.route-atlas-eddy-map g').focus()
        assert name.evaluate('node=>getComputedStyle(node).opacity')=='1'
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-world').click()
        assert page.locator('.route-atlas-eddy-map').count()==0
        assert not errors,errors
        browser.close()
    print(f'OK: {len(eddies)} mapped eddy cards, {total} scoped state links, polygon/locator distinction, share/zoom/reset, hover/focus names and mobile reflow')


if __name__=='__main__':main()
