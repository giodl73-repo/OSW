"""Regional summer route and mean-profile widths retain incompatible scopes."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    read=lambda path:json.loads(Path(path).read_text(encoding='utf-8'))
    catalog=read('research/ocean-current-reference-path-candidates.json')
    ident='atlantic-necc-western-summer-reference-path-candidate'
    candidate=read('research/'+ident+'.json')
    assert candidate['candidate_comparison_group']=='osw_studied_reach_routes'
    assert ident not in catalog['reference_route_length_order']
    assert candidate['source_season_convention']['months_by_label']=={'summer':[7,8,9]}
    row=next(r for r in read('research/ocean-motion-dashboard.json')['entries'] if r['id']=='current:atlantic-north-equatorial-countercurrent')
    assert row['capabilities']['scoped_width']==2 and row['capabilities']['reference_route']==1
    assert row['latest_observation_date'] is None
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aatlantic-north-equatorial-countercurrent#route-atlas',wait_until='networkidle')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['1,100 km','1,100–1,200','Studied reach only','all latitude gates and bends are editorial','not the selected route width','summer: Jul, Aug, Sep']:
            assert text.lower() in preview.inner_text().lower(),text
        assert preview.locator('.route-atlas-state-links li').count()==2
        assert '18/81' in preview.locator('.route-atlas-state-links').inner_text()
        page.locator('#route-atlas').screenshot(path='figures/atlantic-necc-western-summer-review.png')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=atlantic-north-equatorial-countercurrent',wait_until='networkidle')
        assert page.locator('#season-phase option').count()==2
        assert page.locator('#season-play').is_disabled()
        for index,width in enumerate([860,920]):
            page.locator('#season-phase').select_option(str(index))
            assert str(width)+' km' in page.locator('#season-value').inner_text()
            assert 'Mean velocity section' in page.locator('#season-title').inner_text()
            assert 'not an average of instantaneous widths' in page.locator('#season-definition').inner_text()
            assert 'January 1993-December 2017' in page.locator('#season-value').inner_text()
            assert 'No annual minimum/maximum' in page.locator('#season-length').inner_text()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors
        browser.close()
    print('OK: western summer studied reach, JAS convention, mean-profile section widths, no annual playback/rank/date transfer and mobile')


if __name__=='__main__':
    main()
